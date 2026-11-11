"""Source-bound transfers between existing contexts and scored questions."""
from question_tables import collect,detach
from tex_html import prepare_bound_inline,render_inline
from bs4 import BeautifulSoup


def tables(m):
    if '_web_question_tables' not in m:m['_web_question_tables']=collect(m)
    return m['_web_question_tables']


def fragment(m,record):
    source=next(i for s in m['document']['sections'] for i in s['items'] if i['id']==record['context_id'])
    prepared=prepare_bound_inline(source['content'],m,'body',source['id'],source['content'])
    return detach(prepared,record['binding'])


def question_table(m,qid):
    from semantic_html import present_tables,prepare_table_values
    record=tables(m)[1].get(qid)
    if record is None:return ''
    cid=record['context_id'];_,value=fragment(m,record)
    if 'question_table_before_pt' in m['style']:
        from question_displays import prepare
        value=prepare(value,qid,associated=True)
    value=prepare_table_values(value,m['style'],cid)
    soup=BeautifulSoup(render_inline(value,m,'body',font_target=cid),'html.parser')
    present_tables(soup,m['style'],cid)
    return f'<div class="question-context-table" data-source-context="{cid}" data-source-sha256="{record["binding"]["table_sha256"]}">{soup}</div>'
