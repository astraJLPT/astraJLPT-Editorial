"""Final candidate eligibility adds an exact administrative-prefix exclusion."""
from candidate_policy_v2 import *
import candidate_policy_v2 as v2
import re

def administrative_prefix(r,projection):
    marker=re.match(r'^\s*問\s*[0-9０-９]+',projection.text)
    return bool(marker and r['a']<marker.end() and r['b']>marker.start())

def review_eligibility(r,field,projection):
    guard,adjustments=v2.review_eligibility(r,field,projection)
    if not guard and administrative_prefix(r,projection):
        return 'administrative_question_number',adjustments
    return guard,adjustments
