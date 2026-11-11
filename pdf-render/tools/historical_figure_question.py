"""One exact source illustration beside its immediately following reading item."""
import base64,hashlib,re
from bs4 import BeautifulSoup
from model import Projection,digest
from presentation import source_binding


def collect(model):
    contexts={};questions={}
    for section in model['document']['sections']:
        for index,item in enumerate(section['items']):
            m=model['layout']['items'][item['id']];b=m.get('historical_figure_beside_question')
            if b is None:continue
            if (model.get('exam',{}).get('generation')!='historical-1991-2009'
                    or model['layout']['sections'][section['id']]['task']!='reading'
                    or item.get('type')!='passage' or not isinstance(item.get('content'),dict)
                    or digest(item['content'])!=b['content_sha256']
                    or index+1>=len(section['items'])
                    or any(k in m for k in ['historical_graph','historical_wrapped_illustration','historical_context_keep','historical_reading_dialogue'])):
                raise ValueError('Invalid beside-question figure context')
            q=section['items'][index+1];qm=model['layout']['items'][q['id']]
            if (q['id']!=b['question_id'] or 'stem'not in q
                    or digest(q['stem'])!=b['stem_sha256']or digest(q['options'])!=b['options_sha256']
                    or qm.get('historical_options',{}).get('columns')!=1
                    or q['id']in questions):raise ValueError('Stale beside-question association')
            soup=BeautifulSoup(item['content']['html'],'html.parser');images=soup.find_all('img')
            if (len(images)!=1 or soup.find('table')or not re.fullmatch(r'（[1-9]）',Projection(item['content']).text.strip())
                    or hashlib.sha256(base64.b64decode(images[0]['src'].split(',',1)[1],validate=True)).hexdigest()!=b['image_sha256']):
                raise ValueError('Figure must contain its exact single image and source label')
            left,gap=b['left_width_fraction'],b['gap_fraction']
            if type(left)not in [int,float]or type(gap)not in [int,float]or not .2<=left<=.4 or not .02<=gap<=.08:
                raise ValueError('Invalid beside-question geometry')
            source_binding(model['unit'],b['evidence']);contexts[item['id']]=b;questions[q['id']]=item['id']
    return contexts,questions


def render(conv,context_id,binding,figure_tex,question_tex):
    left=binding['left_width_fraction'];gap=binding['gap_fraction'];right=round(1-left-gap,5)
    conv.features.append(dict(kind='historical_figure_beside_question',context=context_id,question=binding['question_id'],image_sha256=binding['image_sha256'],canonical_changed=False))
    return (r'\par\noindent\begin{minipage}{\linewidth}'
            r'\begin{minipage}[t]{'+str(left)+r'\linewidth}\vspace{0pt}'+figure_tex+r'\end{minipage}'
            r'\hspace{'+str(gap)+r'\linewidth}\begin{minipage}[t]{'+str(right)+r'\linewidth}\vspace{0pt}'
            +question_tex+r'\end{minipage}\end{minipage}\par')
