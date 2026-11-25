"""New queue from exactly frozen v5 queue scores and a bound eligibility supplement."""
from common import *
import gzip
from collections import Counter,defaultdict
from ruby_core import Projection
from ruby2_scope import iter_current
from rank_candidates import stream,key,frequencies
from candidate_policy_v6 import review_eligibility,scope_rules
from frequency_policy import make_lookup
from simulate_selection import select


def main():
    previous = load(RUN/'policy-freeze-v2.json')
    old_index = load(check(previous['selection']['queue']))
    for r in previous['eligibility']: check(r)
    check(previous['scorer']); check(previous['frequency']['policy'])
    scope = load(RUN/'research/residual-item-mask-scope-freeze.json')
    check(scope['policy']); check(scope['ranking_code'])
    from reading_resources import dictionary,tokenizer
    pairs,_,resource = frequencies()
    assert resource == previous['frequency']['resource']
    lookup = make_lookup(dictionary.Dictionary().create(),tokenizer,pairs)
    roster = {r['unit']:r for r in load(RUN/'paper-roster.json')}
    census = {r['unit']:r for r in load(RUN.parent/'ruby2-20261105/opportunity-census.json')['units']}
    papers = {r['unit']:r for r in load(check(previous['allocations']['papers']))}
    sections = defaultdict(list)
    for r in load(check(previous['allocations']['sections'])): sections[r['unit']].append(r)
    indices,changes,proposed,summaries,old_replay = [],[],[],[],[]
    all_counts = Counter(); guarded_changes = Counter(); checked_rows = 0
    for number,entry in enumerate(old_index['files'],1):
        u = entry['unit']; owner = roster[u]
        rows = list(stream(check(entry['file'])))
        if owner['public_class'] == 'restored':
            fields = {f['pointer']:f for f in iter_current(load(check(owner['editorial'])))}
            projections = {p:Projection(f['value']) for p,f in fields.items()}
            raw = {key(r):r for r in stream(check(census[u]))}
            assert len(raw) == len(rows)
            starting = load(check(owner['sidecar']))['annotations']
            before,_,_ = select(rows,sections[u],papers[u],starting,True)
            old_replay += before
            for r in rows:
                old_guard = r['review_guard']
                rawr = raw[key(r)]
                guard,adjustments = review_eligibility(rawr,fields[r['pointer']],projections[r['pointer']])
                if r['direct'] and not r['starting_id']: guard = 'direct_evidence_route'
                if (u,r['pointer']) not in scope_rules():
                    assert guard == old_guard,(u,key(r),guard,old_guard)
                if guard != old_guard:
                    assert old_guard and old_guard.startswith('unresolved_field:'),(u,key(r),old_guard,guard)
                    assert (u,r['pointer']) in scope_rules()
                    changes.append(dict(**{k:r[k] for k in ['unit','pointer','a','b','base','rd','rank_score']},
                        before=old_guard,after=guard,adjustments=adjustments))
                    guarded_changes[guard or 'review_eligible'] += 1
                    r.update(review_guard=guard,guard_adjustments=adjustments)
                    r['frequency'] = lookup(r,projections[r['pointer']]) if not guard else dict(state='not_evaluated')
                # Every other stored feature, score, analogy and prior-gloss value
                # is copied unchanged from the hash-checked v5 queue.
                checked_rows += 1
            kept,gaps,skipped = select(rows,sections[u],papers[u],starting,True)
            proposed += kept
            summaries.append(dict(unit=u,groups=len(kept),covered=sum(r['covered_kanji'] for r in kept),gaps=gaps,skipped=skipped))
        dest = RUN/'ranked-v6'/f'{u}.jsonl.gz'
        assert not dest.exists(),dest
        dest.parent.mkdir(exist_ok=True)
        with dest.open('wb') as st,gzip.GzipFile(filename='',fileobj=st,mode='wb',mtime=0,compresslevel=5) as z:
            for r in rows: z.write((json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n').encode())
        counts = Counter('starting' if r['starting_id'] else r['review_guard'] or 'review_eligible' for r in rows)
        all_counts.update(counts)
        indices.append(dict(unit=u,public_class=owner['public_class'],counts=counts,file=ref(dest)))
        if number%25 == 0: print('Scoped queue',number,flush=True)
    assert old_replay == load(check(previous['selection']['initial_proposals']))
    save('research/ranking-index-v6.json',dict(files=indices,counts=all_counts,previous_queue=previous['selection']['queue'],
        policy=ref(RUN/'candidate_policy_v6.py'),scope=ref(RUN/'research/residual-item-mask-scope-freeze.json'),
        unchanged_scorer=previous['scorer'],frequency=previous['frequency']))
    save('research/guard-changes-v6.json',changes)
    save('research/proposals-v6.json',proposed)
    save('research/simulation-v6.json',summaries)
    save('research/queue-v6-reconciliation.json',dict(code=ref(__file__),previous_policy=ref(RUN/'policy-freeze-v2.json'),
        previous_initial_replay_exact=True,previous_initial_groups=len(old_replay),
        restored_candidate_rows_checked=checked_rows,unchanged_stored_scores=True,
        unchanged_allowances=True,unchanged_frequency_and_order=True,changed_guards=len(changes),
        changed_guard_outcomes=guarded_changes,unaudited_proposals=len(proposed),
        unaudited_covered=sum(r['covered_kanji'] for r in proposed),
        outputs={k:ref(RUN/'research'/f) for k,f in [('queue','ranking-index-v6.json'),('changes','guard-changes-v6.json'),
            ('proposals','proposals-v6.json'),('simulation','simulation-v6.json')]}))
    print('Queue complete',len(proposed),'guard changes',len(changes),dict(guarded_changes),flush=True)


if __name__ == '__main__': main()
