"""Data contract shared by the maintained schema and the component validator.

The inventory describes printed evidence, not an inferred modern exam format.
Script text and keys can only occur in the separately selected script component.
"""
import copy

OWNERS = ['N1_1996','N2_1996','N1_1999','N2_1999','N3_2007','N4_2007',
          'N3_2008','N4_2008','N3_2009','N4_12_2009']
CONTRACT = 'historical-listening-documents-1.0'


def obj(properties, required=None):
    return dict(type='object', properties=properties,
                required=list(properties) if required is None else required,
                additionalProperties=False)


def array(items, minimum=0, unique=False):
    return dict(type='array', items=items, minItems=minimum, uniqueItems=unique)


S = dict(type='string', minLength=1)
ID = dict(type='string', pattern=r'^[a-zA-Z0-9][a-zA-Z0-9_.:-]*$')
HASH = dict(type='string', pattern=r'^[a-f0-9]{64}$')
REF = obj(dict(path=S, sha256=HASH))
LOCATOR = obj(dict(source_id=ID, physical_pages=array(dict(type='integer',minimum=1),unique=True),
                   region=S, extraction_pointer=S), ['source_id','physical_pages','region'])
SOURCE = obj(dict(id=ID,path=S,sha256=HASH,
                  role=dict(enum=['question_layout','script_content','answer_key']),
                  authority=dict(enum=['uars_question_layout','published_script','transcript_copy','answer_key']),
                  evidence_note=S))
INVENTORY = obj(dict(id=ID,group=ID,number=dict(type='integer',minimum=1),
                     kind=dict(enum=['scored','example']),
                     printed_state=dict(enum=['printed','none','unrecovered']),
                     printed_options=array(S,unique=True), evidence=array(LOCATOR,1)))
COVERAGE = obj(dict(state=dict(enum=['complete_available','partial_available']),
                    known_total_scored=dict(type=['integer','null'],minimum=0),
                    available_scored_ids=array(ID,unique=True),reviewed_scored_ids=array(ID,unique=True),
                    known_missing_ids=array(ID,unique=True),unknown_extent=dict(type='boolean'),note=S))
GAP = obj(dict(id=ID,question_ids=array(ID,unique=True),description=S,
               severity=dict(enum=['informational','material','blocking']),
               source_attempts=array(LOCATOR),case_id=ID))


def block_schema(script):
    kinds = ['heading','instruction','question_label','text','figure','blank','editorial_note']
    if script:
        kinds += ['dialogue','answer']
    properties = dict(id=ID,kind=dict(enum=kinds),question_ids=array(ID,unique=True),
                      evidence=array(LOCATOR),content=dict(oneOf=[S,obj(dict(html=S))]),
                      asset=obj(dict(path=S,sha256=HASH,provenance=REF)),
                      width_mm=dict(type='number',exclusiveMinimum=0,maximum=175),
                      height_mm=dict(type='number',minimum=0,maximum=230),
                      style=dict(enum=['body','small','centered','bold','boxed']))
    block = obj(properties,['id','kind','question_ids','evidence'])
    block['allOf'] = [
        {'if':{'properties':{'kind':{'const':'figure'}}},'then':{'required':['asset','width_mm'],
            'not':{'required':['content']}},'else':{'not':{'required':['asset']}}},
        {'if':{'properties':{'kind':{'const':'blank'}}},'then':{'required':['height_mm'],
            'not':{'required':['content']}}},
        {'if':{'properties':{'kind':{'not':{'enum':['figure','blank']}}}},'then':{'required':['content']}}
    ]
    return block


def component_schema(script):
    page = obj(dict(id=ID,printed_folio=dict(type=['string','null']),
                    evidence=array(LOCATOR,1),blocks=array(block_schema(script),1)))
    return obj(dict(id=ID,kind={'const':'listening_script' if script else 'listening_questions'},
                    title=S,pages=array(page,1),coverage=COVERAGE,gaps=array(GAP)))


def schema():
    value = obj(dict(contract={'const':CONTRACT},sources=array(SOURCE,1),inventory=array(INVENTORY),
                     questions=component_schema(False),script=component_schema(True)))
    return {'$schema':'https://json-schema.org/draft/2020-12/schema',
            '$id':'https://local.jlpt/schema-v3/historical-1991-2009/listening-documents-1.0',
            'title':'Old JLPT separately selected listening document components', **copy.deepcopy(value)}
