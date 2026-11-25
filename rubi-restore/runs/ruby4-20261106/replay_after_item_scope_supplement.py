"""Replay the R8 supplemented queue with exact initial and final verdicts.

Final verdicts supersede initial judgments only at the identical binding.
No judgment is manufactured; newly reached IDs require both review stages.
The earlier replay, queue, code and ledgers remain immutable.
"""
from common import *
import argparse, gzip
from collections import Counter, defaultdict
from simulate_selection import identity, select, order
from replay_contextual_selection import replay, binding, verdict_binding


def checked_verdict(v):
    check(v['judgment_source']); check(v['packet'])
    for amendment in v.get('amendments', []):
        check(amendment['source'])
    assert v['decision'] in ('suitable', 'reject', 'needs_evidence')
    assert len(v['reason']) > 70 and v['expression'] and v['whole_reading']
    assert v['reading'] == v['proposed_reading']
    if v['decision'] == 'suitable':
        assert all(v[k] == 'yes' for k in ('reading_fit', 'attachment_fit', 'task_safe'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--wave', required=True, type=int)
    args = parser.parse_args()
    dest = f'selection/refill-{args.wave:03}'
    assert not (RUN/dest).exists(), 'Use a fresh immutable wave directory'
    freeze = load(RUN/'policy-freeze-v3.json')
    check(freeze['selection']['algorithm'])
    index = load(check(freeze['selection']['queue']))
    original = load(check(freeze['selection']['initial_proposals']))
    checkpoint = load(RUN/'checkpoint-initial-review.json')
    initial_paths = [check(checkpoint['ledger'])]
    initial_paths += sorted((RUN/'selection').glob('refill-*/review-ledger.json'))
    initial = {}
    for path in initial_paths:
        for v in load(path)['rows']:
            checked_verdict(v)
            assert v['proposal_id'] not in initial
            initial[v['proposal_id']] = v

    final_paths = sorted((RUN/'selection').glob('final-reread-*/review-ledger.json'))
    assert final_paths
    final = {}
    for path in final_paths:
        ledger = load(path)
        assert ledger['completed_packets'] == ledger['total_packets']
        for v in ledger['rows']:
            checked_verdict(v)
            assert v['stage'] == 'separate_final_contextual_reread'
            assert v['reviewer'] == 'executing_model' and not v['independent_evaluation']
            assert v['proposal_id'] not in final
            final[v['proposal_id']] = v
    # Bind the large completed reread to its separately sealed completion receipt.
    complete = load(RUN/'selection/final-reread-001/completion.json')
    check(complete['ledger']); check(complete['progress'])
    for path in sorted((RUN/'selection').glob('final-reread-*/completion.json')):
        receipt = load(path)
        check(receipt['ledger']); check(receipt['progress'])
    starts = {k:v for k,v in final.items() if v['review_origin'] == 'starting_719'}
    assert len(starts) == 719 and all(v['decision'] == 'suitable' for v in starts.values())
    verdicts = dict(initial)
    overrides = []
    for pid, v in final.items():
        if pid in starts:
            continue
        old = initial[pid]
        assert verdict_binding(old) == verdict_binding(v)
        if old['decision'] != v['decision']:
            overrides.append(dict(proposal_id=pid, initial_decision=old['decision'],
                final_decision=v['decision'], initial_judgment=old['judgment_source'],
                final_judgment=v['judgment_source'], binding=list(verdict_binding(v))))
        verdicts[pid] = v

    correction_paths = [RUN/'selection/corrections/score-reconciliation.json']
    correction_paths += sorted((RUN/'selection').glob('final-corrections-*/score-reconciliation.json'))
    correction_paths += sorted((RUN/'selection').glob('r8-corrections-*/score-reconciliation.json'))
    extras = defaultdict(list)
    for path in correction_paths:
        correction = load(path)
        check(correction['code']); check(correction['preparation'])
        assert correction['original_score_replay_exact']
        assert correction['policy'] in [ref(RUN/'policy-freeze.json'),ref(RUN/'policy-freeze-v2.json'),ref(RUN/'policy-freeze-v3.json')]
        for r in load(check(correction['ranked'])):
            assert r['proposal_id'] == identity(r)
            old = verdicts[r['supersedes_proposal_id']]
            assert old['decision'] == 'reject'
            assert (r['unit'], r['pointer'], r['hash']) == (old['unit'], old['pointer'], old['field_sha256'])
            extras[r['unit']].append(r)

    roster = {r['unit']:r for r in load(RUN/'paper-roster.json')}
    papers = {r['unit']:r for r in load(check(freeze['allocations']['papers']))}
    sections = defaultdict(list)
    for r in load(check(freeze['allocations']['sections'])):
        sections[r['unit']].append(r)
    selected, summaries, reproduced, seen = [], [], [], set()
    starting_seen = set()
    for item in index['files']:
        u = item['unit']; owner = roster[u]
        check(owner['editorial'])
        starting = load(check(owner['sidecar']))['annotations']
        for a in starting:
            pid = a['annotation_id']; v = starts[pid]
            assert pid not in starting_seen
            starting_seen.add(pid)
            assert verdict_binding(v) == (u, a['pointer'], a['field_sha256'], a['start'], a['end'], a['base'], a['reading'])
        if owner['public_class'] != 'restored':
            assert not starting and not extras[u]
            continue
        with gzip.open(check(item['file']), 'rt', encoding='utf8') as f:
            rows = [json.loads(line) for line in f]
        seen.update(identity(r) for r in rows)
        old, _, _ = select(rows, sections[u], papers[u], starting, True)
        reproduced += old
        for r in extras[u]:
            assert identity(r) not in seen
            seen.add(identity(r))
        rows += extras[u]
        kept, gaps, cap, skipped, rejected = replay(rows, sections[u], papers[u], starting, verdicts)
        for r in kept:
            pid = r['proposal_id']
            r['proposal_state'] = ('final_context_suitable_pending_delivery' if pid in final
                else 'initially_suitable_pending_final_reread' if pid in initial
                else 'requires_full_context_review')
        selected += kept
        summaries.append(dict(unit=u, level=papers[u]['level'], era=papers[u]['era'],
            allowance=papers[u]['additional_allowance'], new_groups=len(kept),
            additional_covered=sum(r['covered_kanji'] for r in kept), section_gaps=gaps,
            paper_remaining=cap, skipped=skipped, rejected_ids=rejected))
    assert starting_seen == starts.keys()
    assert reproduced == original, 'Frozen initial selection must replay exactly'
    assert verdicts.keys() <= seen
    by_id = {r['proposal_id']:r for r in selected}
    assert len(by_id) == len(selected)
    unknown = [r for r in selected if r['proposal_id'] not in initial]
    final_missing = [r for r in selected if r['proposal_id'] not in final]
    assert all(final[k]['decision'] == 'suitable' for k in by_id.keys() & final.keys())
    previous = {r['proposal_id']:r for r in load(RUN/'selection/refill-012/provisional-selection.json')}
    delta = dict(removed=sorted(previous.keys()-by_id.keys()), added=sorted(by_id.keys()-previous.keys()))
    save(dest+'/provisional-selection.json', selected)
    save(dest+'/proposals.json', unknown)
    save(dest+'/requires-final-reread.json', final_missing)
    save(dest+'/paper-replay.json', summaries)
    save(dest+'/changed-final-decisions.json', overrides)
    from context_packets import write_packets
    packets = write_packets(unknown, dest+'/context')
    status = ('pending_contextual_review' if unknown else 'pending_supplemental_final_reread'
        if final_missing else 'final_context_reconciled_pending_freeze')
    result = dict(status=status, code=ref(__file__),
        frozen_replay_algorithm=ref(RUN/'replay_contextual_selection.py'),
        frozen_policy=ref(RUN/'policy-freeze-v3.json'), queue=freeze['selection']['queue'],
        previous_v5_replay_proof=ref(RUN/'research/queue-v6-reconciliation.json'),
        correction_reconciliations=[ref(p) for p in correction_paths],
        baseline_replay_exact=True, baseline_replayed=len(reproduced), starting_retained=719,
        verdict_ledgers=[ref(p) for p in initial_paths], final_verdict_ledgers=[ref(p) for p in final_paths],
        initial_verdict_counts=Counter(v['decision'] for v in initial.values()),
        effective_verdict_counts=Counter(v['decision'] for v in verdicts.values()),
        separate_final_verdict_counts=Counter(v['decision'] for v in final.values()),
        changed_final_decisions=len(overrides), delta_from_candidate_v2=delta,
        provisional_groups=len(selected), provisional_covered_kanji=sum(r['covered_kanji'] for r in selected),
        unreviewed_groups=len(unknown), context_packets=len(packets),
        missing_final_verdicts=len(final_missing), final_reread_complete=not final_missing,
        suitable_not_selected=sorted(k for k,v in verdicts.items() if v['decision']=='suitable' and k not in by_id),
        rejections=sorted(k for k,v in verdicts.items() if v['decision']!='suitable'),
        outputs={k:ref(RUN/dest/f) for k,f in [('selection','provisional-selection.json'),
            ('new_proposals','proposals.json'),('final_reread_needed','requires-final-reread.json'),
            ('papers','paper-replay.json'),('contexts','context/index.json'),('overrides','changed-final-decisions.json')]})
    save(dest+'/replay.json', result)
    progress('selection', status, 'Review all newly reached IDs at both stages before freezing the exact selected set', ref(RUN/dest/'replay.json'))
    print(json.dumps({k:result[k] for k in ('baseline_replay_exact','initial_verdict_counts',
        'effective_verdict_counts','provisional_groups','provisional_covered_kanji',
        'unreviewed_groups','missing_final_verdicts','delta_from_candidate_v2')},ensure_ascii=False))


if __name__ == '__main__':
    main()
