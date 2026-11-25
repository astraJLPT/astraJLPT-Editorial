"""Exact paragraph metadata inside a source-bound native document frame."""
from bs4 import Tag
from model import Projection
from structured_documents import metadata


def collect(children, binding, line_styles):
    rows=binding['rows'];labels=[r['label'] for r in rows]
    if len(rows)<2 or len(labels)!=len(set(labels)):
        raise ValueError('Section metadata needs distinct exact labels')
    selected={}
    for row in rows:
        text=row['label']+row['separator']+row['value']
        hits=[(n,c) for n,c in enumerate(children) if Projection({'html':str(c)}).text.strip()==text]
        if len(hits)!=1:raise ValueError('Section metadata must select one complete exact paragraph')
        index,child=hits[0]
        if (not isinstance(child,Tag) or child.name!='p' or child.find(['p','div','br','table','section','img'])
                or index in selected or any(s['text']==text for s in line_styles)):
            raise ValueError('Section metadata has nested or conflicting paragraph roles')
        for key in ['before_pt','after_pt']:
            value=row.get(key,0)
            if isinstance(value,bool) or not isinstance(value,(int,float)) or not 0<=value<=40:
                raise ValueError('Invalid section metadata gap')
        selected[index]=row
    if list(selected)!=sorted(selected):
        raise ValueError('Section metadata rows must follow original document order')
    return selected


def render(conv, child, row, binding):
    body=metadata(conv,[child.decode_contents()],{'label_width_em':binding['label_width_em'],'rows':[row]})
    conv.features.append({'kind':'section_document_metadata','label':row['label'],
        'separator':row['separator'],'value':row['value'],'label_width_em':binding['label_width_em']})
    return (r'\par\addvspace{'+str(row.get('before_pt',0))+'pt}'+body
        +r'\par\vspace{'+str(row.get('after_pt',0))+'pt}')
