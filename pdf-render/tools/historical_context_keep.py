"""Keep a source-observed context/question group only when it fits a page."""
from model import digest
from presentation import source_binding

def collect(model):
    starts={};ends=set()
    for section in model['document']['sections']:
        items=section['items']
        for index,item in enumerate(items):
            binding=model['layout']['items'][item['id']].get('historical_context_keep')
            if not binding:continue
            if model.get('exam',{}).get('generation')!='historical-1991-2009' or 'content'not in item:
                raise ValueError('Historical context keep requires an Old passage')
            following=[]
            for q in items[index+1:]:
                if 'stem'not in q:break
                following.append(q)
            query=binding.get('query_for')
            if query is not None:
                from model import Projection
                import re
                if (index==0 or set(query)!={'id','content_sha256'}
                        or items[index-1]['id']!=query['id'] or 'content'not in items[index-1]
                        or digest(items[index-1]['content'])!=query['content_sha256']
                        or not model['layout']['items'][query['id']].get('historical_reading_dialogue')
                        or not re.match(r'^[（(][1-9][）)]',Projection(item['content']).text.strip())):
                    raise ValueError('Stale or invalid attached dialogue query')
                count=len(binding['questions'])
                if not 1<=count<=4 or count>len(following):raise ValueError('Invalid query answer group')
                attached=[]
                for q in following:
                    answer=model['layout']['items'][q['id']].get('historical_label_answer',{})
                    if answer.get('context_id')!=query['id']:break
                    attached.append(q)
                if count!=len(attached):raise ValueError('Attached query must retain every consecutive kana answer')
                following=following[:count]
                for q in following:
                    answer=model['layout']['items'][q['id']].get('historical_label_answer',{})
                    if answer.get('context_id')!=query['id'] or answer.get('context_sha256')!=query['content_sha256']:
                        raise ValueError('Attached query must bind the preceding dialogue kana answers')
                if any(answer['label']not in Projection(item['content']).text for answer in
                       [model['layout']['items'][q['id']]['historical_label_answer']for q in following]):
                    raise ValueError('Attached query omits an answer label')
            if not following or [q['id']for q in following]!=binding['questions'] or digest(item['content'])!=binding['content_sha256'] or digest(following)!=binding['questions_sha256']:
                raise ValueError('Stale historical context-group association')
            meta=model['layout']['items'][item['id']]
            graph=meta.get('historical_graph_after')
            if 'historical_page_break_after'in meta or graph and graph.get('placement','after_questions')!='source_order':
                raise ValueError('Historical keep conflicts with a source page or figure boundary')
            source_binding(model['unit'],binding['evidence'])
            starts[item['id']]=binding;ends.add(following[-1]['id'])
    return starts,ends


def measured_reservation(style,source_targets,binding):
    """A measured context group owns its reservation instead of eight text lines."""
    policy=style.get('reading_context_reservation','standard')
    if policy not in ['standard','measured_groups']or(policy!='standard'and not source_targets):
        raise ValueError('Invalid Old reading context reservation policy')
    return policy=='measured_groups'and bool(binding)
