"""Old section measures, with explicit task and canonical-role boundaries."""
import re
from bs4 import BeautifulSoup
from model import Projection,digest
from presentation import source_binding

def page_inset(style,task,section_meta):
    value=style.get('task_overrides',{}).get(task,{}).get('page_body_bottom_inset_mm',0)
    if type(value)not in [int,float] or not 0<=value<=25:raise ValueError('Invalid Old task page inset')
    if value and task not in ['reading_test','orthography_test','vocabulary','paraphrase','usage','grammar','sentence_composition']:raise ValueError('Task page inset requires a question-list role')
    if value and section_meta.get('start_policy','new_page')!='new_page':raise ValueError('Task page measure cannot start inside a flowing page')
    return value

def geometry(style,inset):
    m=style['margins_mm']
    # Increase the footer distance by the same amount as the shortened body,
    # preserving its physical baseline and the running header position.
    return (r'\newgeometry{headsep=34pt,footskip='+str(round(style.get('footer_skip_pt',30)+inset*72.27/25.4,8))+'pt,left='+str(m['left'])+'mm,right='+str(m['right'])+'mm,top='+str(m['top'])+'mm,bottom='+str(m['bottom']+inset)+'mm}')

def phrase_line(model,section):
    meta=model['layout']['sections'][section['id']];binding=meta.get('historical_answer_line')
    if not binding:return None
    if not {'kind','section_sha256','evidence'}<=set(binding) or set(binding)-{'kind','section_sha256','evidence','question_widths'} or binding['kind']!='phrase' or meta['task']!='grammar':raise ValueError('Invalid phrase answer-line role')
    if digest(section)!=binding['section_sha256']:raise ValueError('Stale phrase answer-line section')
    source_binding(model['unit'],binding['evidence'])
    questions=section['items']
    if not questions or any('stem'not in q for q in questions):raise ValueError('Phrase answer-line section must contain scored questions only')
    for q in questions:
        text=Projection(q['stem']).text
        plain=len(re.findall(r'(?<![A-Za-z_])_+(?![A-Za-z_])|＿+',text))
        authored=0
        if isinstance(q['stem'],dict):
            soup=BeautifulSoup(q['stem']['html'],'html.parser')
            for node in soup.find_all('u'):
                if not re.fullmatch(r'[ \u3000\t]+',node.get_text()):continue
                if node.attrs or node.find() or node.find_parent(['ruby','rt','rp']):
                    raise ValueError('Phrase blank requires plain authored underline markup')
                authored+=1
        if plain+authored!=1 or '★'in text:raise ValueError('Each phrase question needs one unambiguous answer line')
    value=model['style'].get('historical_typography',{}).get('phrase_answer_line_width_em')
    if type(value)not in [int,float]or not 4<=value<=10:raise ValueError('Missing or invalid phrase answer-line width')
    widths=binding.get('question_widths',{})
    if not isinstance(widths,dict) or set(widths)-{q['id']for q in questions}:raise ValueError('Unknown phrase answer-line question')
    if any(type(v)not in [int,float]or not 4<=v<=10 for v in widths.values()):raise ValueError('Invalid source question answer-line width')
    result=dict(width_em=value,questions=[q['id']for q in questions],canonical_changed=False)
    if widths:result['question_widths']=dict(widths)
    return result
