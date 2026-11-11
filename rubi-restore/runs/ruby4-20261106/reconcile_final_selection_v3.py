"""Bind the final replay to manual verdicts and prepare inactive release overlays.

No acceptance reasons are generated here. This performs identity, provenance,
preservation and set-equality checks on already authored decisions.
"""
from common import *
import copy, csv
from collections import Counter, defaultdict
from simulate_selection import kcount
from replay_contextual_selection import binding, verdict_binding
from ruby2_validate import validate


def main():
    replay_path = RUN/'selection/refill-016/replay.json'
    replay = load(replay_path)
    assert replay['baseline_replay_exact'] and replay['final_reread_complete']
    assert replay['unreviewed_groups'] == replay['missing_final_verdicts'] == 0
    initial = {}
    for receipt in replay['verdict_ledgers']:
        for v in load(check(receipt))['rows']:
            assert v['proposal_id'] not in initial
            initial[v['proposal_id']] = v
    finals = {}
    for receipt in replay['final_verdict_ledgers']:
        for v in load(check(receipt))['rows']:
            assert v['proposal_id'] not in finals
            finals[v['proposal_id']] = v
    errata_path = RUN/'selection/final-v2/context-metadata-errata-001.json'
    errata = load(errata_path)
    check(errata['sealed_final_ledger']); check(errata['sealed_review_ledger'])
    for e in errata['entries']:
        assert e['field'] == 'reason'
        v = finals[e['proposal_id']]
        assert v['judgment_source'] == e['judgment_source']
        check(e['judgment_source'])
        assert v['reason'] == e['previous']
        v['reason'] = e['corrected']
        v.setdefault('metadata_errata', []).append(dict(source=ref(errata_path),
            field='reason',previous=e['previous'],corrected=e['corrected'],explanation=e['explanation']))
    original = load(check(load(RUN/'selection/final-reread-001/preparation.json')['outputs']['selection']))
    starting = [r for r in original if r['review_origin'] == 'starting_719']
    additions = load(check(replay['outputs']['selection']))
    rows = sorted(starting+additions, key=lambda r:(r['unit'],int(r['pointer'].split('/')[2]),r['pointer'],r['a'],r['b'],r['rd']))
    selected = {r['proposal_id']:r for r in rows}
    assert len(starting) == 719 and len(additions) == replay['provisional_groups']
    assert len(selected) == len(rows) == 719 + len(additions)
    assert selected.keys() <= finals.keys()
    selected_final_verdicts = {k:v for k,v in finals.items() if k in selected}
    assert selected.keys() == {k for k,v in selected_final_verdicts.items() if v['decision'] == 'suitable'}
    historical_suitable = {k:v for k,v in finals.items() if v['decision'] == 'suitable' and k not in selected}
    effective = {**initial, **finals}
    effective_rejections = {k:v for k,v in effective.items() if v['decision'] != 'suitable'}
    assert set(replay['rejections']) == effective_rejections.keys()
    assert not selected.keys() & effective_rejections.keys()
    supplemental_complete = load(RUN/'selection/final-reread-004/completion.json')
    check(supplemental_complete['ledger']);check(supplemental_complete['progress'])
    assert not any(r.get('direct') for r in rows), 'An exact-source route needs separate observed-placement verification'
    rejected = {k for k,v in finals.items() if v['decision'] != 'suitable'}
    assert 'rr4-ed202b215076f82fe65b' in rejected
    assert 'rr4-e07148e2589b837ec906' in selected
    assert not {'rr1-8f87ddfda90441bd6813','rr1-d43c8f25ab4664c5d956'} & selected.keys()

    source_index = {}
    sources = [RUN.parent/'ruby2-20261105'/name for name in (
        'development-printed-observations.json','final-printed-observations.json','legacy-witnesses/verified-final.json')]
    for path in sources:
        for v in load(path)['rows']:
            sid = v['sid']
            assert sid not in source_index
            source_index[sid] = dict(observation=v,observation_ledger=ref(path),
                use='Prior printing evidence at another occurrence, never exact-placement evidence for a selected inference')
    used_crops = {sid for r in rows for sid in r['pos_crops']+r['contra_crops']}
    assert used_crops <= source_index.keys(), sorted(used_crops-source_index.keys())
    save('selection/final-v3/final-source-reference-index.json', {k:source_index[k] for k in sorted(used_crops)})
    definitions = dict(
        placement=dict(high='Reserved for exact authorized same-occurrence printed evidence; no selected Pass4 inference is assigned this category.',
            medium='At least two distinct prior lineages print the same base/reading in the same task and field role, with more positive than negative lineages. Still analogical, not verified historical placement.',
            low='Model-ranked or weaker/conflicting analogy. The presence score is not a probability and does not establish historical printing.'),
        reading=dict(high='Executing-model full-context review finds the selected reading sound, with no unresolved alternative-reading flag.',
            medium='The selected reading is defensible but an explicit reading variant or other recorded uncertainty remains; see the per-occurrence reason.',
            low='Unresolved or unsuitable reading; not eligible for selection.'),
        attachment_and_task='All selected IDs have explicit yes judgments at their exact field/hash/span. These categorical judgments are not measured error probabilities.',
        layout='Contextual linguistic suitability does not certify PDF/browser layout; explicit layout_trial_required flags remain pending final rendered verification.',
        evaluation='Initial and final reviews were performed by the same executing agent; the final reread is an additional check, not an independent or blind evaluation.')
    save('selection/final-v3/confidence-definitions.json', definitions)
    detailed = []
    byunit = defaultdict(list)
    for r in rows:
        pid = r['proposal_id']; v = finals[pid]
        assert binding(r) == verdict_binding(v)
        assert v['reading'] == r['rd'] and all(v[k]=='yes' for k in ('reading_fit','attachment_fit','task_safe'))
        check(v['judgment_source']); check(v['packet'])
        for a in v.get('amendments',[]): check(a['source'])
        init = initial.get(pid)
        if init:
            assert init['decision'] == 'suitable' and binding(r) == verdict_binding(init)
        else:
            assert r.get('review_origin') == 'starting_719'
        placement = 'medium' if r['analogy_positive_lineages'] >= 2 and r['analogy_positive_lineages'] > r['analogy_negative_lineages'] else 'low'
        item = dict(annotation_id=pid,review_record_id='P4-FINAL:'+pid,release_id=RUBY_ID,
            disposition='retained_starting' if r.get('review_origin')=='starting_719' else 'accepted_addition',
            binding={k:r[k] for k in ('unit','section','owner','slot','pointer','hash','a','b','base','rd')},
            ranked_record=r,initial_context_verdict=init,final_context_verdict=v,
            prior_context_ledger=r.get('prior_context_ledger'),prior_context_key=r.get('prior_context_key'),
            placement=dict(support='analogical_prior_printing' if r['analogy_positive_lineages'] else 'model_only',
                confidence=placement,exact_occurrence_observed=False,score_is_calibrated_probability=False,
                positive_reference_ids=r['pos_crops'],negative_reference_ids=r['contra_crops'],
                source_reference_index=ref(RUN/'selection/final-v3/final-source-reference-index.json')),
            reading=dict(confidence='high' if v['uncertainty']=='none' else 'medium',
                contextual_fit=True,full_expression=v['expression'],whole_reading=v['whole_reading'],uncertainty=v['uncertainty']),
            attachment=dict(confidence='high',exact_span_reviewed=True),
            task=dict(confidence='high',protected_target_guard_passed=True,contextually_safe=True),
            selection_rule='Retained starting identity' if r.get('review_origin')=='starting_719' else 'Descending frozen score and exact-tie order; suitable whole span fits both section and paper allowances',
            allocation=dict(section=r['section'],covered_kanji=kcount(r['base']),replay=ref(replay_path)),
            policy=ref(RUN/'policy-freeze-v3.json'))
        detailed.append(item);byunit[r['unit']].append((r,item))
    save('selection/final-v3/final-selected.json', rows)
    save('selection/final-v3/final-context-ledger.json', detailed)
    save('selection/final-v3/final-rejected-reread.json', [finals[k] for k in sorted(rejected)])
    save('selection/final-v3/final-starting-reconciliation.json', [dict(annotation_id=r['proposal_id'],
        disposition='retained',binding=binding(r),final_review_record_id='P4-FINAL:'+r['proposal_id'],
        uncertainty=finals[r['proposal_id']]['uncertainty'],prior_sidecar=r['prior_sidecar']) for r in starting])

    save('selection/final-v3/final-historical-suitable-not-selected.json', [dict(
        proposal_id=k,final_verdict=historical_suitable[k],disposition='suitable_not_selected_under_supplemented_frozen_ranking_and_unchanged_caps',
        rejected_or_retired=False,replay=ref(replay_path)) for k in sorted(historical_suitable)])
    save('selection/final-v3/final-effective-rejections.json',[effective_rejections[k] for k in sorted(effective_rejections)])
    baseline = load(RUN/'baseline.json')
    prior_selection = load(check(baseline['ruby']['selection']))
    prior_root = ROOT/'rubi-restore/releases'/prior_selection['release_id']
    prior_owners = {r['unit']:r for r in prior_selection['owners']}
    candidates = []
    for owner in load(RUN/'paper-roster.json'):
        u=owner['unit'];check(owner['editorial']);check(owner['defaults'])
        old=load(check(owner['sidecar']));old_ann={a['annotation_id']:a for a in old['annotations']}
        assert owner['public_class']=='restored' or not byunit[u]
        ov=copy.deepcopy(old)
        ov.update(release_id=RUBY_ID,processing_status='pass4_context_reviewed_pending_delivery',
            frozen_origin=dict(release_id=prior_selection['release_id'],
                frozen_overlay=ref(prior_root/prior_owners[u]['frozen_overlay'])),annotations=[])
        for r,item in byunit[u]:
            pid=r['proposal_id']
            a=copy.deepcopy(old_ann[pid]) if pid in old_ann else dict(
                annotation_id=pid,section_id=r['section'],owner_id=r['owner'],field=r['slot'],
                pointer=r['pointer'],field_sha256=r['hash'],start=r['a'],end=r['b'],base=r['base'],reading=r['rd'],
                origin='project_rubi_restore',basis='inferred',decision='accepted',
                acceptance_route='pass4_ranked_allowance_and_full_context_review',rule='frozen_policy_with_exact_bound_contextual_verdicts',
                model_score=r['rank_score'],score_is_calibrated_probability=False)
            a.update(release_id=RUBY_ID,review_record_id=item['review_record_id'])
            if r.get('supersedes_proposal_id'):a['supersedes_proposal_id']=r['supersedes_proposal_id']
            ov['annotations'].append(a)
        path=RUN/'selection/final-v3/final-overlays'/f'{u}.json'
        save(path.relative_to(RUN),ov)
        candidates.append(dict(unit=u,accepted=len(ov['annotations']),editorial_freeze_sha256=owner['editorial']['sha256'],**ref(path)))
    candidate=RUN/'selection/final-v3/final-candidate-selection.json'
    save(candidate.relative_to(RUN),dict(release_id=RUBY_ID,per_owner=candidates))
    validation=validate(candidate)
    assert validation['inferred_groups']==len(rows) and validation['source_ruby_preserved']==12356
    save('selection/final-v3/final-candidate-validation.json',validation)
    counts=dict(selected=len(rows),starting_retained=719,starting_corrected=0,starting_retired=0,
        new_additions=len(additions),additional_covered_kanji=sum(kcount(r['base']) for r in additions),
        separate_final_verdicts=len(finals),selected_suitable_final_verdicts=len(selected),
        rejected_final_verdicts=len(rejected),suitable_not_selected=len(replay['suitable_not_selected']),
        historical_suitable_final_not_selected=len(historical_suitable),effective_rejections=len(effective_rejections),
        final_uncertainties=Counter(v['uncertainty'] for k,v in finals.items() if k in selected),
        placement_confidence=Counter(v['placement']['confidence'] for v in detailed),
        reading_confidence=Counter(v['reading']['confidence'] for v in detailed))
    save('selection/final-v3/final-reconciliation.json',dict(status='contextual_selection_reconciled_delivery_pending',
        code=ref(__file__),replay=ref(replay_path),counts=counts,
        selected_final_set_equality=True,unique_ids=True,exact_bindings=True,
        set_equality_scope='All selected IDs equal the suitable final-verdict projection on the selected set. Every selected ID has a final verdict; previously suitable but displaced IDs remain archived separately and are not mislabeled rejected.',
        eligibility_supplement=ref(RUN/'policy-freeze-v3.json'),supplemental_reread=ref(RUN/'selection/final-reread-004/completion.json'),
        r8_corrections=ref(RUN/'selection/r8-corrections-001/score-reconciliation.json'),
        item_corrections=ref(RUN/'selection/r8-corrections-002/score-reconciliation.json'),
        context_metadata_errata=ref(errata_path),
        initial_final_reviews_are_independent=False,active_pointers_changed=False,
        preserved_prior_retirements=['rr1-8f87ddfda90441bd6813','rr1-d43c8f25ab4664c5d956'],
        final_correction=dict(rejected_id='rr4-ed202b215076f82fe65b',new_id='rr4-e07148e2589b837ec906',
            lexical_evidence=ref(RUN/'selection/final-reread-001/lexical-corroboration-K11939.json'),
            rescore=ref(RUN/'selection/final-corrections-001/score-reconciliation.json')),
        outputs={k:ref(RUN/'selection/final-v3'/f) for k,f in [('selected','final-selected.json'),
            ('ledger','final-context-ledger.json'),('starting','final-starting-reconciliation.json'),
            ('rejected','final-rejected-reread.json'),('candidate','final-candidate-selection.json'),
            ('validation','final-candidate-validation.json'),('confidence','confidence-definitions.json'),
            ('source_references','final-source-reference-index.json'),('historical_suitable_not_selected','final-historical-suitable-not-selected.json'),('effective_rejections','final-effective-rejections.json')]}))
    progress('selection','contextual_selection_reconciled_delivery_pending',
        'Finish achieved coverage, residual-burden and fresh-source diagnostics; freeze release inputs and rebuild all201',
        ref(RUN/'selection/final-v3/final-reconciliation.json'))
    print(json.dumps(counts,ensure_ascii=False))


if __name__=='__main__':main()
