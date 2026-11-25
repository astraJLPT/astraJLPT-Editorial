"""Bind retired unresolved name decisions independently of tokenizer tags."""
from candidate_policy_v3 import *
import candidate_policy_v3 as v3
from functools import lru_cache

@lru_cache(None)
def retired_names():
    rs=[r for r in load(CONTEXT/'final-ledger.json') if r['disposition']=='retire unsafe reading']
    assert {(r['unit'],r['base']) for r in rs}=={('N4_07_2023','林'),('N4_07_2024','林')}
    return rs

def unresolved_name(r):
    for old in retired_names():
        if r['unit']==old['unit'] and r['pointer']==old['pointer']:
            assert r['hash']==old['field_sha256'],'Retired-name field changed; rebind explicitly'
            if r['a']<old['end'] and r['b']>old['start']:return old['annotation_id']
    return None

def review_eligibility(r,field,projection):
    guard,adjustments=v3.review_eligibility(r,field,projection)
    retired=unresolved_name(r)
    if retired:
        return 'unresolved_personal_name',adjustments+[dict(decision='preserve_retired_name_decision',superseded_id=retired,
            reason='The earlier full-context audit established a speaker name with no item-specific pronunciation evidence. A tokenizer common-noun tag cannot override that binding.')]
    return guard,adjustments
