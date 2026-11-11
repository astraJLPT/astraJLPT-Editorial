"""Explicit gap ownership at passage boundaries, independent of text leading."""
from model import digest
from presentation import source_binding


def resolve(model, item, task):
    style = model['style']
    result = {}
    if task == 'reading' and model['layout']['items'][item['id']].get('notes') and 'reading_notes_to_question_pt' in style:
        result = {'note_after_pt': 0, 'after_pt': 0,
                  'following_question_gap_pt': style['reading_notes_to_question_pt'],
                  'origin': 'reading_notes_to_question_pt'}
    binding = style.get('passage_boundaries', {}).get(item['id'])
    if binding:
        source_binding(model['unit'], binding['evidence'])
        if digest(item['content']) != binding['content_sha256']:
            raise ValueError('Stale passage boundary binding')
        result.update({k: v for k, v in binding.items() if k not in ['evidence', 'content_sha256']})
        result['origin'] = 'explicit_source_boundary'
    for key, value in result.items():
        if key == 'origin':continue
        if key=='questions_start':
            if task!='paired_reading'or value!='next_page':raise ValueError('Invalid paired question boundary')
            continue
        if key=='cloze_choices':
            if task!='cloze' or value not in ['next_page','flow']:raise ValueError('Invalid cloze question boundary')
            continue
        if key=='note_keep_with_previous':
            if not isinstance(value,bool) or not model['layout']['items'][item['id']].get('notes'):
                raise ValueError('Note attachment requires a boolean and authored notes')
            continue
        if key not in ['note_before_pt','note_after_pt','after_pt','following_question_gap_pt','intro_after_pt'] or isinstance(value,bool) or not isinstance(value,(int,float)) or not 0 <= value <= 60:
            raise ValueError('Invalid passage boundary: ' + key)
    return result


def question_groups(model):
    groups = model['style'].get('question_groups', [])
    starts, ends, covered = {}, set(), set()
    for group in groups:
        source_binding(model['unit'],group['evidence'])
        ids = group['items']
        if len(ids)<2 or len(ids)!=len(set(ids)) or covered.intersection(ids):raise ValueError('Overlapping question group')
        matches = []
        for section in model['document']['sections']:
            items = section['items']; positions=[n for n,i in enumerate(items)if i['id']in ids]
            if positions:
                if len(positions)!=len(ids) or positions!=list(range(positions[0],positions[0]+len(ids))):raise ValueError('Question group must be contiguous in one section')
                matches=[items[n] for n in positions]
        if [i['id']for i in matches]!=ids or any('stem'not in i for i in matches):raise ValueError('Question group identity changed')
        if group['content_sha256']!=digest(matches):raise ValueError('Question group content changed')
        gap=group['question_gap_pt']
        if isinstance(gap,bool)or not isinstance(gap,(int,float))or not 0<=gap<=24:raise ValueError('Invalid group question gap')
        starts[ids[0]]=group;ends.add(ids[-1]);covered.update(ids)
    return starts,ends,covered


def typography(model,item,task=None):
    binding=model['style'].get('passage_typography',{}).get(item['id'])
    if not binding:return {}
    source_binding(model['unit'],binding['evidence'])
    if digest(item['content'])!=binding['content_sha256'] or set(binding)-{'content_sha256','evidence','baseline_pt'}:
        raise ValueError('Stale or unknown passage typography')
    if task is None:
        task=next(model['tasks'][s['id']]for s in model['document']['sections']if any(i['id']==item['id']for i in s['items']))
    style=model['style'];local=style.get('task_overrides',{}).get(task,{})
    baseline=binding['baseline_pt'];size=local.get('passage_body_pt',local.get('body_pt',style.get('passage_body_pt',style['body_pt'])))
    if isinstance(baseline,bool)or not size*1.45<=baseline<=size*2.5:raise ValueError('Passage leading outside readable range')
    return {'baseline_pt':baseline}
