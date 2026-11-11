"""Current v3 written field semantics; never infer era or task from owner prefix/year."""
from ruby_core import Projection,KANJI_RE
import re
MODERN='modern-2010';HIST='historical-1991-2009'
APPROX={'1級':'N1','2級':'N2','3級':'N4','4級':'N5'}
TASKS={'reading_test','orthography_test','vocabulary','paraphrase','usage','grammar','sentence_composition','cloze','reading','paired_reading','information_retrieval'}
def proficiency(generation,original):
    if generation==HIST and original in APPROX:return APPROX[original]
    if generation==MODERN and original in ('N1','N2','N3','N4','N5'):return original
    raise ValueError('Unknown era or original level')
def iter_current(doc):
    era=doc['exam']['generation'];level=doc['exam']['historical_level'];prof=proficiency(era,level)
    for si,s in enumerate(doc['sections']):
        if s['part'] not in ('vocab','grammar','reading'):raise ValueError('Written document contains unsupported part')
        task=doc['layout']['sections'][s['id']].get('task','unknown')
        common=dict(era=era,original_level=level,level=prof,unit=doc['unit'],section=s['id'],part=s['part'],task=task)
        yield dict(common,owner=s['id'],slot='heading',role='heading',pointer=f'/sections/{si}/heading',value=s['heading'])
        for ii,i in enumerate(s['items']):
            root=f'/sections/{si}/items/{ii}';k=i.get('type','stem')
            for slot in ('stem','content'):
                if slot in i:yield dict(common,owner=i['id'],slot=slot,role=k,pointer=root+'/'+slot,value=i[slot])
            for oi,v in enumerate(i.get('options',[])):
                yield dict(common,owner=i['id'],slot=f'options/{oi}',role='example' if k=='example' else 'option',pointer=f'{root}/options/{oi}',value=v)
def protect(field,proj,start,end):
    task=field['task'];role=field['role']
    if task not in TASKS:return 'unclassified_v3_task'
    if role=='example':return 'worked_example_not_independent'
    if task=='sentence_composition' and role in ('passage','table','notice') and re.search(r'[（(]\s*(?:こたえかた|答え方|解答例)\s*[）)]',proj.text):
        return 'embedded_worked_answer_example'
    # Deliberately malformed orthography can be a distractor even when not an explicit spelling question.
    if role=='option' and task in {'reading_test','orthography_test','vocabulary','paraphrase','usage'}:return 'tested_or_intentionally_variant_choice'
    if proj.is_underlined(start,end):return 'marked_question_target'
    if task in {'reading_test','orthography_test'} and role=='stem':
        if not any(x and x[3] for x in proj.mapping):return 'undelimited_tested_target'
    if task in {'usage','paraphrase'} and role=='stem' and not any(x and x[3] for x in proj.mapping):
        return 'unmarked_lexical_prompt'
    return None
def provisional_slots(document,case_rows,principal_rows):
    # Only written item identities passed by caller. Key-only uncertainty cannot be propagated into unrelated fields.
    ids={v['id'] for s in document['sections'] for v in [s]+s['items']};out={}
    for x in (*case_rows,*principal_rows):
        if x.get('item_id') not in ids or x.get('status')=='resolved':continue
        slot=(x.get('field') or '').removesuffix('/html').strip('/')
        out.setdefault(x['item_id'],[]).append((slot,x.get('case_id') or x.get('difference_id')))
    return out
def masked(field,blocks):
    hits=[v for slot,v in blocks.get(field['owner'],[]) if not slot or slot==field['slot'] or field['slot'].startswith(slot+'/')]
    return list(filter(None,hits))

