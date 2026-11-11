"""Apply 53 manually bound short-item scopes; preserve all v5 safeguards."""
from candidate_policy_v5 import *
import candidate_policy_v5 as v5


@lru_cache(None)
def scope_rules():
    freeze = load(RUN/'research/residual-item-mask-scope-freeze.json')
    result = {}
    for receipt in freeze['manual_batches']:
        for rule in load(check(receipt)):
            k = (rule['unit'],rule['pointer'])
            assert k not in result and k not in v5.scope_rules()
            assert rule['decision'] in ('narrow_to_exact_risk_spans','preserve_full_field_risk')
            assert not rule['source_content_changed'] and not rule['uncertainties_resolved']
            check(rule['source_editorial'])
            for case in rule['cases']:
                source = check(case['case_source'])
                records = [json.loads(line) for line in source.read_text('utf-8-sig').splitlines() if line.strip()]
                hits = [r for r in records if (r.get('case_id') or r.get('difference_id')) == case['case_id']]
                assert len(hits) == 1 and json_hash(hits[0]) == case['case_record_sha256']
                assert hits[0] == case['record']
            assert set(rule['case_ids']) == {c['case_id'] for c in rule['cases']}
            result[k] = (rule,receipt)
    assert len(result) == freeze['field_count'] == 53
    return result


def review_eligibility(r,field,projection):
    entry = scope_rules().get((r['unit'],r['pointer']))
    if not entry:
        return v5.review_eligibility(r,field,projection)
    rule,receipt = entry
    assert r['hash'] == rule['field_sha256'] == json_hash(field['value'])
    assert field['owner'] == rule['owner']
    for span in rule['risk_spans']:
        assert 0 <= span['start'] < span['end'] <= len(projection.text)
        assert projection.text[span['start']:span['end']] == span['text']
    if rule['decision'] == 'preserve_full_field_risk':
        assert len(rule['risk_spans']) == 1
        assert rule['risk_spans'][0]['start'] == 0
        assert rule['risk_spans'][0]['end'] == len(projection.text)
    overlap = any(r['a'] < s['end'] and r['b'] > s['start'] for s in rule['risk_spans'])
    removed = sorted(set(r['uncertain']) & set(rule['case_ids'])) if not overlap else []
    if not removed:
        return v5.review_eligibility(r,field,projection)
    candidate = {**r,'uncertain':[k for k in r['uncertain'] if k not in removed]}
    guard,adjustments = v5.review_eligibility(candidate,field,projection)
    adjustments.append(dict(decision='outside_manually_bound_residual_item_risks',cases=removed,
        field_sha256=rule['field_sha256'],manual_scope_batch=receipt,
        risk_spans=[[s['start'],s['end']] for s in rule['risk_spans']],
        reason=rule['review_reason'],source_content_changed=False,
        reading_verdict='not_supplied_by_scope_rule'))
    return guard,adjustments
