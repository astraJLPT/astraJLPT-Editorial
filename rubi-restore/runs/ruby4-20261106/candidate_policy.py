"""Eligibility for a contextual-review queue, never automatic reading approval."""
from common import *
from functools import lru_cache
from ruby_core import Projection,json_hash,KANJI_RE
from ruby2_scope import protect

# These are ordinary geographic names in the documented lexical resource;
# personal labels such as 林 are intentionally absent. Each use still needs
# its own contextual verdict, just as a common noun does.
PLACE_READINGS={('日本','にほん'),('東京','とうきょう'),('京都','きょうと'),('大阪','おおさか')}

@lru_cache(201)
def cases(unit):
    folder=ROOT/'preprocess'/unit[:2]/unit;out={}
    for prefix in ('principal_differences','unresolved_cases'):
        p=folder/f'{prefix}_{unit}.jsonl'
        if p.exists():
            for line in p.read_text('utf-8-sig').splitlines():
                if not line.strip():continue
                r=json.loads(line);out[r.get('case_id') or r.get('difference_id')]=r
    return out

def uncertainty(r,field,projection):
    remaining=[];explanations=[]
    for key in r['uncertain']:
        c=cases(r['unit'])[key]
        if c.get('disposition')=='supported_repair':
            # The source recovery has been settled. Linked unresolved cases are
            # separate records in the same mask and are processed normally.
            explanations.append(dict(case=key,decision='settled_editorial_repair',disposition=c['disposition']))
        elif key=='N2_12_2015-PD-012':
            title='「アサーション入門―自分も相手も大切にする自己表現法」'
            assert c['editorial_reading']==title and c['principal']['reading']==title.replace('「','『').replace('」','』')
            assert projection.text.count(title)==1 and r['owner']=='reading-b005'
            start=projection.text.index(title);end=start+len(title)
            if r['a']<end and r['b']>start:remaining.append(key)
            else:explanations.append(dict(case=key,decision='outside_exact_title_variant',risk_span=[start,end],
                field_sha256=json_hash(field['value']),reason='The difference is the attribution title quotation marks. This occurrence lies wholly outside that title and its lexical reading cannot depend on those brackets.'))
        else:remaining.append(key)
    return remaining,explanations

def review_eligibility(r,field,projection):
    assert json_hash(field['value'])==r['hash'] and projection.text[r['a']:r['b']]==r['base']
    risk=protect(field,projection,r['a'],r['b'])
    if risk:return 'protected:'+risk,[]
    if r['role'] in ('heading','example'):return 'administrative_or_worked_template',[]
    if projection.overlaps_ruby(r['a'],r['b']):return 'canonical_ruby',[]
    try:projection.raw_span(r['a'],r['b'])
    except ValueError:return 'cross_node_span',[]
    remaining,adjustments=uncertainty(r,field,projection)
    if remaining:return 'unresolved_field:'+','.join(remaining),adjustments
    if r['guard'] and not (r['guard']=='unverified_place_name' and (r['base'],r['rd']) in PLACE_READINGS):
        return 'reading_guard:'+r['guard'],adjustments
    names=r['features']['dictionary_names']
    if (names[3] or names[4] or names[5]) and (r['base'],r['rd']) not in PLACE_READINGS:
        return 'unverified_proper_name',adjustments
    if r['duplicate']:
        adjustments.append(dict(decision='substantive_occurrence_review_only',
            reason='A cross-item/context duplicate remains excluded from statistical fitting/evaluation. This authored occurrence is eligible only for full contextual deployment review; worked examples/headings and direct source mappings remain separate.'))
    if r['alignment']!='dictionary_exact' or names[1]!=1:
        adjustments.append(dict(decision='contextual_disambiguation_required',alignment=r['alignment'],dictionary_reading_count=names[1],
            reason='Candidate generation is not acceptance. Inspect the whole lexical expression, sentence, alternatives and task before accepting this polyphonic or kana-aligned span.'))
    if not r['rd'] or not KANJI_RE.search(r['base']):return 'invalid_candidate',adjustments
    return None,adjustments
