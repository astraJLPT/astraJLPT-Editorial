"""Narrow one additional verified punctuation mask; retain all other guards."""
from candidate_policy import *
import candidate_policy as v1

def review_eligibility(r,field,projection):
    key='N4_07_2024-PD-025'
    if key not in r['uncertain']:return v1.review_eligibility(r,field,projection)
    c=cases(r['unit'])[key];sentence='最近いいやり方を見つけました。'
    assert r['unit']=='N4_07_2024' and r['owner']=='reading-b005'
    assert c['editorial_reading']==sentence and c['principal']['reading']=='最近、いいやり方を見つけました。'
    assert c['categories']==['punctuation'] and c['disposition']=='retained_variant' and not c['linked_case_ids']
    assert projection.text.count(sentence)==1
    start=projection.text.index(sentence);end=start+len(sentence)
    if r['a']<end and r['b']>start:return v1.review_eligibility(r,field,projection)
    risk,adjustments=v1.review_eligibility({**r,'uncertain':[x for x in r['uncertain'] if x!=key]},field,projection)
    adjustments.append(dict(case=key,decision='outside_verified_punctuation_sentence',risk_span=[start,end],
        field_sha256=json_hash(field['value']),reason='The sole disputed comma follows 最近 in the early sentence describing discovery of the bus-trip method. This occurrence is outside that complete sentence; the comma cannot affect its lexical reading or the later driver dialogue. The sentence remains masked and source text is unchanged.'))
    return risk,adjustments
