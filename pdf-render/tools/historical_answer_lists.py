"""Exact Old written prompts with explicitly bound answer-number placement.

Logical questions may share a verbatim stem; only an uninterrupted run bound
to the same emitting owner permits that repeated prompt to be emitted once.
"""
import re
from model import digest
from presentation import source_binding


def collect(model):
    bindings={qid:meta['historical_answer_list']for qid,meta in model['layout']['items'].items()if 'historical_answer_list'in meta}
    if not bindings:return {}
    if model.get('exam',{}).get('generation')!='historical-1991-2009':
        raise ValueError('Historical answer list outside Old JLPT')
    items={i['id']:i for s in model['document']['sections']for i in s['items']}
    previous={}
    for section in model['document']['sections']:
        for n,item in enumerate(section['items']):
            previous[item['id']]=section['items'][n-1]['id']if n else None
    for qid,b in bindings.items():
        q=items[qid];meta=model['layout']['items'][qid];grid=meta.get('historical_options',{})
        if ('stem'not in q or not q['stem'] or digest(q['stem'])!=b['stem_sha256']
            or digest(q['options'])!=b['options_sha256'] or len(q['options'])!=4):
            raise ValueError('Stale historical answer-list content')
        if (grid.get('kind')!='grid' or grid.get('columns')!=1 or grid.get('source_numbered')is not False
            or grid.get('options_sha256')!=b['options_sha256'] or 'historical_target_row'in meta or 'historical_question_label'in meta):
            raise ValueError('Historical answer list requires its explicit one-column choice grid')
        source_binding(model['unit'],b['evidence'])
        number_only=isinstance(q['stem'],str) and re.fullmatch(r'[1-9][0-9]{0,2}',q['stem'])
        if number_only and (q['stem']!=meta.get('printed_label',{}).get('value') or b.get('shared_prompt_owner') or b.get('answer_number_placement','beside_first_choice')!='beside_first_choice'):
            raise ValueError('Number-only answer list must exactly match its separate printed label')
        owner=b.get('shared_prompt_owner')
        placement=b.get('answer_number_placement','beside_first_choice')
        if placement not in {'beside_first_choice','prompt_right'} or (owner and placement!='beside_first_choice'):
            raise ValueError('Invalid historical answer-number placement')
        if 'prompt_after_pt'in b:
            value=b['prompt_after_pt']
            if(type(value)not in[int,float]or not 0<=value<=30 or owner or number_only or placement!='beside_first_choice'):
                raise ValueError('Source prompt spacing requires its emitting beside-choice prompt')
        if owner:
            if (owner not in bindings or 'shared_prompt_owner'in bindings[owner]
                or items[owner].get('stem')!=q['stem']
                or bindings[owner].get('answer_number_placement','beside_first_choice')!='beside_first_choice'):
                raise ValueError('Shared historical prompt requires its exact emitting owner')
            prior=previous[qid]
            while prior!=owner:
                if (prior not in bindings or bindings[prior].get('shared_prompt_owner')!=owner
                    or items[prior].get('stem')!=q['stem']):
                    raise ValueError('Shared historical prompt must form an uninterrupted run')
                prior=previous[prior]
            if bindings[owner]['evidence']['source_sha256']!=b['evidence']['source_sha256']:
                raise ValueError('Shared historical prompt witness mismatch')
    return bindings


def render(conv,item,binding,number,stem_tex,option_tex,gap):
    if not number.isdigit():raise ValueError('Historical answer-list number must be numeric')
    shared=binding.get('shared_prompt_owner')
    placement=binding.get('answer_number_placement','beside_first_choice')
    number_only=isinstance(item['stem'],str) and item['stem']==number and bool(re.fullmatch(r'[1-9][0-9]{0,2}',item['stem']))
    emit_prompt=not(shared or number_only)
    prompt=r'\noindent '+stem_tex+r'\par\addvspace{6pt}'if emit_prompt else ''
    conv.features.append(dict(kind='historical_answer_list',target=item['id'],stem_sha256=digest(item['stem']),
        options_sha256=digest(item['options']),shared_prompt_owner=shared,prompt_emitted=emit_prompt,number_only_stem=number_only,
        canonical_changed=False,answer_number_placement=placement))
    if 'prompt_after_pt'in binding:
        value=binding['prompt_after_pt']
        if(type(value)not in[int,float]or not 0<=value<=30 or not emit_prompt or placement!='beside_first_choice'):
            raise ValueError('Invalid source prompt spacing consumer')
        prompt=r'\noindent '+stem_tex+r'\par\nobreak\nointerlineskip\vspace{'+str(value)+r'pt}'
        conv.features[-1]['prompt_after_pt']=value
    if placement=='prompt_right':
        return (r'{\par\addvspace{'+str(gap)+r'pt}\noindent\begin{minipage}{\linewidth}\setlength\parindent{0pt}'
            +r'\hypertarget{'+item['id']+r'}{}\label{'+item['id']+'}'
            +r'\noindent '+stem_tex+r'\nobreak\hfill\QNumber{'+number+r'}\par\addvspace{6pt}'
            +r'\noindent\hspace*{\QuestionIndent}\begin{minipage}[t]{\dimexpr\linewidth-\QuestionIndent\relax}\vspace{0pt}'
            +option_tex+r'\end{minipage}\par\end{minipage}\par}')
    return (r'{\par\addvspace{'+str(gap)+r'pt}\noindent\begin{minipage}{\linewidth}\setlength\parindent{0pt}'
        +r'\hypertarget{'+item['id']+r'}{}\label{'+item['id']+'}'+prompt
        +r'\noindent\begin{minipage}[t]{\QuestionIndent}\vspace{0pt}\strut{}\QNumber{'+number+r'}\end{minipage}'
        +r'\begin{minipage}[t]{\dimexpr\linewidth-\QuestionIndent\relax}\vspace{0pt}'+option_tex
        +r'\end{minipage}\par\end{minipage}\par}')
