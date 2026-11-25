"""Explicit document semantics select defaults across native frame representations."""
import copy
from model import digest, merge_defaults

DEFAULTS = {
 'student_composition': {'frame_rule_pt': .6},
 'magazine_column': {'frame_rule_pt': 1.05},
 'memo': {'font_role':'memo','ruby_intergap_em':0,'ruby_base_height_em':.8,'frame_style':'folded_corner'},
 'email': {'first_line_indent_em':0},
}


def resolve(item, metadata, task, style, section_style):
    section_style=copy.deepcopy(section_style)
    if section_style and 'typography_family' in section_style:
        family=section_style['typography_family']
        if family not in ['body','notice','memo']:raise ValueError('Unknown section typography family')
        if 'body_pt' in section_style or 'baseline_pt' in section_style:
            raise ValueError('A shared section family cannot compete with local type size')
        if family=='memo':
            typography=style['memo_typography']
        else:
            prefix='notice_' if family=='notice' else ''
            typography={k:style[prefix+k] for k in ['body_pt','baseline_pt']}
        section_style.update(typography)
    binding=metadata.get('document_role')
    if not binding:return None,section_style
    role=binding['role']
    if role not in DEFAULTS or digest(item['content'])!=binding['content_sha256'] or not binding['basis']:
        raise ValueError('Stale or unsupported document role')
    if role=='email':
        indent=style.get('email_family',{}).get('first_line_indent_em',0)
        if isinstance(indent,bool) or not 0<=indent<=2:raise ValueError('Invalid email family indent')
        if task not in ['reading','cloze','paired_reading']:raise ValueError('Email role requires a prose task')
        if section_style:
            section_style['paragraph_indent_em']=indent
            section_style.pop('first_paragraph_indent_em',None)
        return {'role':role,'parameters':{'first_line_indent_em':indent},'basis':binding['basis']},section_style
    params=style.get('document_roles',DEFAULTS)[role]
    if role in ['student_composition','magazine_column']:
        if task!='cloze' or set(params)!={'frame_rule_pt'} or not .3<=params['frame_rule_pt']<=2:raise ValueError('Invalid cloze document role')
    elif set(params)!={'font_role','ruby_intergap_em','ruby_base_height_em','frame_style'} or params['font_role']!='memo' or params['frame_style']!='folded_corner':
        raise ValueError('Invalid memo document role')
    result=copy.deepcopy(section_style)
    if result:
        derived={k:v for k,v in params.items() if k!='frame_rule_pt'}
        if 'frame_rule_pt' in params and result['frame_style']=='box':derived['frame_rule']={'style':'single','width_pt':params['frame_rule_pt']}
        result=merge_defaults(derived,result)
        if role=='memo':result['frame_style']=params['frame_style']
    elif role=='memo':
        raise ValueError('Memo role requires an explicitly selected document section')
    return {'role':role,'parameters':params,'basis':binding['basis']},result


def wrap(tex, role):
    if not role:return tex
    if role['role']=='email':return tex
    if 'frame_rule_pt' in role['parameters']:
        if not any(x in tex for x in [r'\begin{ClozeFrame}',r'\ObservedSection{']):raise ValueError('Document frame role did not reach a native frame')
        return r'{\renewcommand\ClozeFrameRule{'+str(role['parameters']['frame_rule_pt'])+'pt}'+tex+'}'
    if r'\MemoJapanese' not in tex:raise ValueError('Memo role did not reach its font consumer')
    return tex
