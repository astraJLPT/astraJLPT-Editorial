"""Explicit Old dialogue blanks whose question labels occur inside the speech."""
import re
from bs4 import BeautifulSoup
from model import Projection,digest
from dialogue import candidates,lines
from presentation import source_binding


def collect(model):
    result={}
    for section in model['document']['sections']:
        for item in section['items']:
            meta=model['layout']['items'][item['id']]
            b=meta.get('historical_inline_dialogue_question')
            if b is None:continue
            if (model.get('exam',{}).get('generation')!='historical-1991-2009'
                    or model['layout']['sections'][section['id']]['task']!='grammar'
                    or 'stem'not in item or not isinstance(item['stem'],dict)
                    or digest(item['stem'])!=b['stem_sha256']
                    or digest(item['options'])!=b['options_sha256']
                    or len(item['options'])!=4
                    or not re.fullmatch(r'(?:[1-9]|10)',b['label'])
                    or meta.get('printed_label',{}).get('value')!=b['label']
                    or any(k in meta for k in ['historical_question_label','historical_label_answer','historical_target_row','historical_answer_list'])):
                raise ValueError('Stale or conflicting inline dialogue question')
            marks=BeautifulSoup(item['stem']['html'],'html.parser').select('u[data-historical-dialogue-blank]')
            if (len(marks)!=1 or marks[0].get('data-historical-dialogue-blank')!=b['label']
                    or marks[0].find(True) or marks[0].get_text()!='\u3000'+b['label']+'\u3000'):
                raise ValueError('Inline dialogue requires exactly one literal underlined number')
            dialogue=meta.get('dialogue',{})
            found=candidates(item['stem']);raw=lines(item['stem'])
            if dialogue.get('single_speaker')is True and len(raw)==1 and '「'in raw[0]:
                found=[dict(line=0,speaker=Projection({'html':raw[0].split('「',1)[0]}).text.strip())]
            if not dialogue or found!=dialogue.get('turns')or len(found)!=len(raw):
                raise ValueError('Inline dialogue requires all exact speaker turns')
            options=meta.get('historical_options',{})
            if options.get('kind')!='grid' or options.get('columns')not in [2,4]:
                raise ValueError('Inline dialogue requires its source option grid')
            source_binding(model['unit'],b['evidence']);result[item['id']]=b
    return result


def prepare(value,binding,source_value):
    if digest(source_value)!=binding['stem_sha256']or not isinstance(value,dict):
        raise ValueError('Stale inline dialogue presentation')
    soup=BeautifulSoup(value['html'],'html.parser');marks=soup.select('u[data-historical-dialogue-blank]')
    if len(marks)!=1 or marks[0]['data-historical-dialogue-blank']!=binding['label']:
        raise ValueError('Missing exact inline dialogue marker')
    del marks[0]['data-historical-dialogue-blank']
    result={'html':str(soup)}
    if (Projection(result).text,Projection(result).ruby)!=(Projection(value).text,Projection(value).ruby):
        raise ValueError('Inline dialogue preparation changed text/ruby')
    return result


def render(conv,item,binding,stem_tex,options_tex,gap):
    if not getattr(conv,'source_target_markers',False):raise ValueError('Inline dialogue outside Old')
    if stem_tex.count(r'\DialogueSetup{')!=1 or r'\DialogueTurn{'not in stem_tex:
        raise ValueError('Missing inline dialogue consumer')
    conv.features.append(dict(kind='historical_inline_dialogue_question',target=item['id'],label=binding['label'],outer_label=False,stem_sha256=binding['stem_sha256'],canonical_changed=False))
    return (r'{\par\addvspace{'+str(gap)+r'pt}\noindent\begin{minipage}{\linewidth}'
            r'\setlength\parindent{0pt}\hypertarget{'+item['id']+r'}{}\label{'+item['id']+r'}'
            r'\HistoricalReadingDialogue{0}{'+stem_tex+r'}\par\nobreak '
            +options_tex+r'\end{minipage}\par}')
