"""Modern prose uses shared role sizes; only registered designs may differ.

Reference-scan approval is evidence permission, not a blanket size exception.
"""
import json
from pathlib import Path
from model import digest

POLICY=Path(__file__).resolve().parents[1]/'config/typography_policy.json'

def passage_type(style, task, section=None):
    section=section or {}
    family=section.get('typography_family')
    if family=='memo':return style['memo_typography']['body_pt'],style['memo_typography']['baseline_pt']
    if family=='body':return style['body_pt'],style['baseline_pt']
    task_style=style.get('task_overrides',{}).get(task,{})
    return tuple(task_style.get('passage_'+k,task_style.get(k,style.get('passage_'+k,style[k]))) for k in ['body_pt','baseline_pt'])

def controls(node, path=''):
    if isinstance(node,list):
        for i,v in enumerate(node):yield from controls(v,path+'/'+str(i))
    elif isinstance(node,dict):
        for k,v in node.items():
            if k in ['font_pt','title_font_pt','body_pt']:yield path+'/'+k,v
            elif k=='line_sizes_pt':
                for i,size in enumerate(v):yield path+'/'+k+'/'+str(i),size
            elif k not in ['evidence','basis','source']:yield from controls(v,path+'/'+k)

def validate(staged, style):
    if staged['exam']['generation'] != 'modern-2010':raise ValueError('Modern typography policy requires modern generation')
    policy=json.loads(POLICY.read_text(encoding='utf-8'))
    unit=staged['unit']; notices=policy['notice_documents'].get(unit,{})
    items={i['id']:(staged['layout']['sections'][s['id']]['task'],i) for s in staged['sections'] for i in s['items']}
    for owner,record in notices.items():
        if owner not in items or digest(items[owner][1].get(record.get('field','content')))!=record['content_sha256']:
            raise ValueError('Stale notice typography exception: '+unit+'/'+owner)
    for group in ['section_styles','block_styles','table_styles']:
        for owner,node in style.get(group,{}).items():
            if owner in notices:continue
            task,item=items[owner]
            if group=='section_styles':
                if node.get('typography_family')=='notice':raise ValueError('Notice typography requires a registered notice: '+unit+'/'+owner)
                size,_=passage_type(style,task,node)
            else:size=style['table_body_pt'] if group=='table_styles' else passage_type(style,task)[0]
            for path,value in controls(node):
                if value!=size:raise ValueError(f'Unapproved prose size {unit}/{owner}{path}: {value} != shared {size}')
    for owner,node in style.get('embedded_documents',{}).items():
        if unit=='N3_07_2012' and owner=='reading-q033':
            protected=policy['protected_email']
            if (digest(items[owner][1]['stem'])!=protected['content_sha256'] or
                node.get('body_pt')!=7.75 or node.get('baseline_pt')!=13):
                raise ValueError('Protected Q33 email long-line treatment changed')
        elif any(True for _ in controls(node)):
            raise ValueError('Unapproved embedded-document size: '+unit+'/'+owner)
