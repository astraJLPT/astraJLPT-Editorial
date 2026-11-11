"""Replay the frozen queue using bound manual verdicts; never author judgments.

Unknown rows are provisionally reserved solely to prepare the next review wave.
This is not a delivery selection and does not satisfy the final-reread gate.
"""
from common import *
import argparse, gzip
from collections import Counter, defaultdict
from simulate_selection import identity, order, kcount, select


def binding(r):
    return (r['unit'], r['pointer'], r['hash'], r['a'], r['b'], r['base'], r['rd'])


def verdict_binding(v):
    return (v['unit'], v['pointer'], v['field_sha256'], v['start'], v['end'],
            v['base'], v['proposed_reading'])


def replay(rows, sections, paper, starting, verdicts):
    used = defaultdict(list)
    for a in starting:
        used[a['pointer']].append((a['start'], a['end']))
    remain = {r['section']: r['additional_allowance'] for r in sections}
    cap = paper['additional_allowance']
    selected, skipped, rejected = [], Counter(), []
    for r in sorted(rows, key=lambda r: order(r, True)):
        pid = identity(r)
        verdict = verdicts.get(pid)
        if verdict:
            assert binding(r) == verdict_binding(verdict), (pid, 'stale verdict')
        if r['starting_id']:
            continue
        if r['review_guard']:
            skipped[r['review_guard'].split(':')[0]] += 1
            continue
        if verdict and verdict['decision'] != 'suitable':
            skipped['contextual_' + verdict['decision']] += 1
            rejected.append(pid)
            continue
        cost = kcount(r['base'])
        assert cost > 0
        if any(a < r['b'] and b > r['a'] for a, b in used[r['pointer']]):
            skipped['overlap'] += 1
            continue
        if cost > remain[r['section']] or cost > cap:
            skipped['allowance'] += 1
            continue
        used[r['pointer']].append((r['a'], r['b']))
        remain[r['section']] -= cost
        cap -= cost
        selected.append({**r, 'proposal_id':pid, 'covered_kanji':cost,
            'proposal_state':'initially_suitable_pending_final_reread' if verdict else 'requires_full_context_review',
            'final_tie_inputs':list(order(r, True)[1:])})
    assert cap >= 0 and min(remain.values(), default=0) >= 0
    return selected, remain, cap, skipped, rejected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--wave', required=True, type=int)
    parser.add_argument('--with-corrections', action='store_true')
    args = parser.parse_args()
    dest = f'selection/refill-{args.wave:03}'
    assert not (RUN/dest).exists(), 'Use a fresh immutable wave directory'
    freeze = load(RUN/'policy-freeze.json')
    check(freeze['selection']['algorithm'])
    index = load(check(freeze['selection']['queue']))
    original = load(check(freeze['selection']['initial_proposals']))
    checkpoint = load(RUN/'checkpoint-initial-review.json')
    ledgers = [check(checkpoint['ledger'])]
    ledgers += sorted((RUN/'selection').glob('refill-*/review-ledger.json'))
    verdicts = {}
    for path in ledgers:
        ledger = load(path)
        for v in ledger['rows']:
            assert v['proposal_id'] not in verdicts, v['proposal_id']
            check(v['judgment_source']); check(v['packet'])
            for amendment in v.get('amendments', []):
                check(amendment['source'])
            assert v['decision'] in ('suitable', 'reject', 'needs_evidence')
            if v['decision'] == 'suitable':
                assert v['reading'] == v['proposed_reading']
                assert all(v[k] == 'yes' for k in ('reading_fit', 'attachment_fit', 'task_safe'))
            verdicts[v['proposal_id']] = v
    roster = {r['unit']: r for r in load(RUN/'paper-roster.json')}
    papers = {r['unit']: r for r in load(check(freeze['allocations']['papers']))}
    sections = defaultdict(list)
    for r in load(check(freeze['allocations']['sections'])):
        sections[r['unit']].append(r)
    extras=defaultdict(list);correction_receipt=None
    if args.with_corrections:
        correction_path=RUN/'selection/corrections/score-reconciliation.json'
        correction_receipt=ref(correction_path)
        correction=load(correction_path)
        check(correction['code']);check(correction['preparation'])
        for r in load(check(correction['ranked'])):
            assert r['proposal_id']==identity(r)
            old=verdicts[r['supersedes_proposal_id']]
            assert old['decision']=='reject'
            assert (r['unit'],r['pointer'],r['hash'])==(old['unit'],old['pointer'],old['field_sha256'])
            extras[r['unit']].append(r)
    selected, summaries, reproduced, seen, starting_count = [], [], [], set(), 0
    for item in index['files']:
        u = item['unit']; rr = roster[u]
        check(rr['editorial'])
        starting = load(check(rr['sidecar']))['annotations']
        starting_count += len(starting)
        if rr['public_class'] != 'restored':
            assert not starting
            continue
        with gzip.open(check(item['file']), 'rt', encoding='utf-8') as f:
            rows = [json.loads(line) for line in f]
        seen.update(identity(r) for r in rows)
        old, _, _ = select(rows, sections[u], papers[u], starting, True)
        reproduced += old
        for r in extras[u]:
            assert identity(r) not in seen, 'Corrected identity already exists in frozen queue'
            seen.add(identity(r))
        rows+=extras[u]
        kept, gaps, cap, skipped, rejected = replay(rows, sections[u], papers[u], starting, verdicts)
        selected += kept
        summaries.append(dict(unit=u, level=papers[u]['level'], era=papers[u]['era'],
            allowance=papers[u]['additional_allowance'], new_groups=len(kept),
            additional_covered=sum(r['covered_kanji'] for r in kept), section_gaps=gaps,
            paper_remaining=cap, skipped=skipped, rejected_ids=rejected))
    assert starting_count == 719
    assert reproduced == original, 'Frozen initial selection does not replay exactly'
    assert verdicts.keys() <= seen, 'A review ID is absent from frozen queue'
    by_id = {r['proposal_id']: r for r in selected}
    assert len(by_id) == len(selected)
    unknown = [r for r in selected if r['proposal_id'] not in verdicts]
    suitable = {k for k, v in verdicts.items() if v['decision'] == 'suitable'}
    save(dest+'/provisional-selection.json', selected)
    save(dest+'/proposals.json', unknown)
    save(dest+'/paper-replay.json', summaries)
    from context_packets import write_packets
    packets = write_packets(unknown, dest+'/context')
    result = dict(status='pending_contextual_review' if unknown else 'pending_corrections_and_final_reread',
        frozen_policy=ref(RUN/'policy-freeze.json'), queue=freeze['selection']['queue'],
        correction_reconciliation=correction_receipt,
        baseline_replay_exact=True, baseline_replayed=len(reproduced), starting_retained_pending_reread=starting_count,
        verdict_ledgers=[ref(p) for p in ledgers], verdict_counts=Counter(v['decision'] for v in verdicts.values()),
        provisional_groups=len(selected), provisional_covered_kanji=sum(r['covered_kanji'] for r in selected),
        unreviewed_groups=len(unknown), context_packets=len(packets),
        suitable_not_selected=sorted(suitable-by_id.keys()),
        rejections=sorted(k for k,v in verdicts.items() if v['decision']!='suitable'),
        outputs={k:ref(RUN/dest/f) for k,f in [('selection','provisional-selection.json'),('new_proposals','proposals.json'),('papers','paper-replay.json'),('contexts','context/index.json')]},
        final_reread_complete=False)
    save(dest+'/replay.json', result)
    progress('selection', result['status'], 'Read '+dest+'/context before judging replacement candidates', ref(RUN/dest/'replay.json'))
    print(json.dumps({k:result[k] for k in ('baseline_replay_exact','baseline_replayed','verdict_counts','provisional_groups','provisional_covered_kanji','unreviewed_groups','context_packets')},ensure_ascii=False))


if __name__ == '__main__':
    main()
