"""Explicit same-old-level inference, subordinate to exact-unit UARS evidence."""
import re
from collections import Counter
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
from model import ROOT,Projection,digest,read,file_hash
from historical_era import entry,presentation
from reference_approvals import approved_reference

PROFILE=ROOT/'pdf-render/config/historical-numbering-profiles.json'


def bound_context_nodes(value,binding):
    """Resolve audited underline associations without rewriting canonical prose.

    Retyped witnesses can omit reference furniture or preserve local circled
    labels. Every selected underline and any removed label are bound explicitly;
    unscored underlines remain untouched, including targets of omitted items.
    """
    if digest(value)!=binding['content_sha256']:
        raise ValueError('Inferred reference field changed')
    soup=BeautifulSoup(value['html'],'html.parser')
    if binding.get('mode')!='bound_underlines':
        nodes=soup.select('u[data-reference-label],span[data-reference-parenthesized="true"]')
        if len(nodes)!=len(binding['references']):raise ValueError('Inferred reference count changed')
        for node,r in zip(nodes,binding['references']):
            if node['data-reference-label']!=r['source_label']:raise ValueError('Inferred reference order changed')
        return soup,nodes
    underlines=soup.select('u');indices=[r['underline_index']for r in binding['references']]
    if len(indices)!=len(set(indices)) or indices!=sorted(indices):
        raise ValueError('Duplicate or reordered inferred underline')
    unused=binding['unscored_underlines']
    if sorted(indices+[r['index']for r in unused])!=list(range(len(underlines))):
        raise ValueError('Every source underline needs an explicit disposition')
    for r in unused:
        if Projection({'html':underlines[r['index']].decode_contents()}).text!=r['text']:
            raise ValueError('Unscored source underline changed')
    nodes=[]
    for r in binding['references']:
        node=underlines[r['underline_index']]
        text=Projection({'html':node.decode_contents()}).text
        if text!=r['underline_text']:raise ValueError('Inferred underline text changed')
        suffix=r.get('stem_suffix','');punctuation=r.get('underline_suffix','')
        if punctuation not in ('','。') or (punctuation and not text.endswith(punctuation)):
            raise ValueError('Invalid bound underline punctuation')
        target=text[:-len(punctuation)]if punctuation else text
        if suffix:
            if not isinstance(node.next_sibling,str) or not node.next_sibling.startswith(suffix):
                raise ValueError('Source target continuation changed')
            target+=suffix
        if target!=r['target_text']:raise ValueError('Inferred target differs from its scored stem')
        prefix=r.get('source_prefix');gap=r.get('source_prefix_gap','')
        if not isinstance(gap,str) or not re.fullmatch(r'[ \u3000\t]{0,8}',gap) or (gap and not prefix):
            raise ValueError('Invalid inferred reference prefix gap')
        if prefix and (not isinstance(prefix,str) or not re.fullmatch('[①-⑳]',prefix)
                       or not isinstance(node.previous_sibling,str) or not node.previous_sibling.endswith(prefix+gap)):
            raise ValueError('Inferred reference prefix changed')
        nodes.append(node)
    return soup,nodes


def collect(model):
    b=model['layout'].get('historical_numbering')
    if not b:return None
    if model.get('exam',{}).get('generation')!='historical-1991-2009':raise ValueError('Old numbering outside its era')
    owner=entry(model['unit'])
    if approved_reference(owner) is not None:raise ValueError('Exact-unit UARS takes precedence over inferred numbering')
    profile=read(PROFILE)
    if b['profile_sha256']!=file_hash(PROFILE) or b['old_level']!=owner['historical_level'] or b['status']!='same_level_inference':raise ValueError('Stale or mismatched same-level numbering profile')
    control=profile['levels'][b['old_level']]
    for c in control['controls']:
        if entry(c['unit'])['historical_level']!=owner['historical_level']:raise ValueError('Cross-level numbering inference')
        if presentation(c['unit'],c['evidence']) is None:raise ValueError('A numbering control must have approved UARS')
    items={i['id']:i for s in model['document']['sections'] for i in s['items']}
    if set(b['questions'])!={iid for iid,i in items.items() if 'stem'in i}:raise ValueError('Inferred numbering must account for every scored item')
    policy=b.get('reset_policy','legacy_section')
    boxed=b['old_level']in ['3級','4級']
    if policy not in ['legacy_section','group_local','booklet_continuous']:
        raise ValueError('Unknown inferred numbering policy')
    if policy!='legacy_section' and (policy=='booklet_continuous')!=boxed:
        raise ValueError('Numbering policy belongs to a different Old level')
    if profile.get('revision',0)>=3 and policy=='legacy_section':
        raise ValueError('Legacy section numbering must be reconciled with group-local controls')
    context_of={};local_numbers={}
    for iid,r in b['contexts'].items():
        if iid not in items or 'content'not in items[iid]:raise ValueError('Unknown inferred target context')
        bound_context_nodes(items[iid]['content'],r)
        for n,ref in enumerate(r['references'],1):
            qid=ref['question_id']
            if qid in context_of or qid not in b['questions']:raise ValueError('Duplicate or unknown target association')
            context_of[qid]=iid;local_numbers[qid]=str(n)
            q=b['questions'][qid]
            if [ref['source_label'],ref['display_number']]!=[q['source_label'],q['display_number']]:
                raise ValueError('Incoherent inferred target/question reference')
            if r.get('mode')=='bound_underlines' and Projection(items[qid]['stem']).text!=ref['target_text']:
                raise ValueError('Inferred underline belongs to a different question')
    for section in model['document']['sections']:
        qs=[i for i in section['items'] if 'stem'in i]
        for n,q in enumerate(qs,1):
            r=b['questions'][q['id']];original=model['layout']['items'][q['id']]['printed_label']['value']
            if r['source_label']!=original or r['stem_sha256']!=digest(q['stem']) or r['options_sha256']!=digest(q['options']):raise ValueError('Stale inferred question or options')
            if r['kind'] not in ['parenthesized','question','bracketed_question','bracketed_query','boxed']:raise ValueError('Unknown inferred label role')
            if r.get('section')!=section['id'] or r.get('context')!=context_of.get(q['id']):
                raise ValueError('Inferred question section/context changed')
            if policy=='booklet_continuous':
                position=re.fullmatch(r'(?:vocab|reading)-q([0-9]+)',q['id'])
                if (not position or r['kind']!='boxed' or r['display_number']!=str(int(position[1]))
                    or r.get('source_prefix')):
                    raise ValueError('Boxed numbering must preserve the audited booklet positions and omissions')
            elif model['tasks'][section['id']]!='reading':
                expected=local_numbers.get(q['id'],str(n))if policy=='group_local'else str(n)
                if r['kind']!='parenthesized' or r['display_number']!=expected:
                    raise ValueError('Scored numbering must reset at its explicit target group or ordinary section')
            elif r['kind']=='boxed' or not r.get('source_prefix'):
                raise ValueError('Reading label requires its exact local prefix')
            if r.get('source_prefix'):
                text=Projection(q['stem']).text
                if not text.startswith(r['source_prefix']):raise ValueError('Local question prefix changed')
                label=r['source_prefix'].strip()
                expected='【問い】' if r['kind']=='bracketed_query' else '【問'+r['display_number']+'】' if r['kind']=='bracketed_question' else '問'+r['display_number']
                if label!=expected:raise ValueError('Inferred label differs from admitted local question structure')
        range_binding=b['ranges'].get(section['id'])
        if range_binding:
            validate_range(section,model['tasks'][section['id']],range_binding,b,model['layout']['items'])
    if set(b['ranges'])-{s['id']for s in model['document']['sections']}:
        raise ValueError('Unknown inferred instruction-range section')
    return b


def validate_range(section,task,binding,numbering,item_metadata):
    """Bind heading references to actual emitted questions, not reprint ordinals."""
    if section.get('part')!='vocab' or task not in ('vocabulary','usage','paraphrase'):
        raise ValueError('Invalid inferred instruction range family')
    questions=[q for q in section['items']if 'stem'in q]
    if len(questions)<2:raise ValueError('Instruction range requires multiple questions')
    source=[item_metadata[q['id']]['printed_label']['value']for q in [questions[0],questions[-1]]]
    displayed=[numbering['questions'][q['id']]['display_number']for q in questions]
    expected=[displayed[0],displayed[-1]]
    if (digest(section['heading'])!=binding['heading_sha256'] or binding['source_labels']!=source
        or binding['display_labels']!=expected
        or [int(n)for n in displayed]!=list(range(int(expected[0]),int(expected[1])+1))):
        raise ValueError('Stale inferred instruction range')
    style='boxed'if numbering['old_level']in ['3級','4級']else'parenthesized'
    if binding.get('number_style','parenthesized')!=style:
        raise ValueError('Instruction range has a different level numbering role')
    labels=binding.get('heading_labels',source)
    if not isinstance(labels,list) or len(labels)!=2:raise ValueError('Invalid heading reference labels')
    normalized=[]
    for label in labels:
        if not isinstance(label,str):raise ValueError('Invalid heading reference label')
        if re.fullmatch('[①-⑳]',label):normalized.append(str(ord(label)-0x2460+1))
        elif re.fullmatch('[1-9][0-9]*',label):normalized.append(label)
        else:raise ValueError('Unsupported heading reference label')
    if normalized not in [source,expected,['1',str(len(questions))]]:
        raise ValueError('Heading range does not identify its question group')
    token=lambda x:r'(?<![0-9])(?:[（(\[]?'+re.escape(x)+r'[）)\]]?)(?![0-9])'
    if len(re.findall(token(labels[0])+r'\s*から\s*'+token(labels[1]),Projection(section['heading']).text))!=1:
        raise ValueError('Heading range must occur exactly once in canonical prose')


def ruby_after_deletions(before,after,deletions):
    """Require exact ruby groups after only explicitly checked label removal.

    Display-only removal shifts later projection offsets; it does not change
    canonical sidecar spans. Never permit a deletion inside a ruby base.
    """
    expected=[]
    for group in before.ruby:
        if any(a<group['end'] and b>group['start'] for a,b in deletions):return False
        shift=lambda position:sum(b-a for a,b in deletions if b<=position)
        expected.append({**group,'start':group['start']-shift(group['start']),
                         'end':group['end']-shift(group['end'])})
    return after.ruby==expected


def context_value(value,binding):
    before=Projection(value);soup,refs=bound_context_nodes(value,binding);removed=[]
    for node,r in zip(refs,binding['references']):
        prefix=r.get('source_prefix')
        if prefix:
            previous=node.previous_sibling;gap=r.get('source_prefix_gap','')
            previous.replace_with(previous[:-len(prefix+gap)]+gap);removed.append(prefix)
        if binding.get('number_style')=='boxed':
            node['data-reference-label']=r['display_number'];node['data-reference-boxed']='true'
        else:
            node['data-reference-label']=r['display_number'] if node.name=='span' else '（'+r['display_number']+'）'
            node.attrs.pop('data-reference-boxed',None)
    out={'html':str(soup)}
    after=Projection(out)
    operations=[(op,a,b,c,d)for op,a,b,c,d in SequenceMatcher(None,before.text,after.text,autojunk=False).get_opcodes()if op!='equal']
    edits=[(op,before.text[a:b],after.text[c:d])for op,a,b,c,d in operations]
    if (any(op!='delete'or new for op,old,new in edits)
        or Counter(''.join(old for op,old,new in edits))!=Counter(''.join(removed))
        or not ruby_after_deletions(before,after,[(a,b)for op,a,b,c,d in operations])):raise ValueError('Numbering inference changed target prose/ruby')
    return out


def stem_value(value,record):
    prefix=record.get('source_prefix')
    if not prefix:return value
    p=Projection(value)
    if not p.text.startswith(prefix):raise ValueError('Inferred question prefix no longer exact')
    if isinstance(value,str):return value[len(prefix):]
    if re.search(r'<(?:br|p|div|table)\b',value['html'],re.I) and value['html'].startswith(prefix):
        # A source erratum can follow the question on another line. Remove
        # only the exact leading label; preserve all later block boundaries.
        out={'html':value['html'][len(prefix):]};after=Projection(out)
        if after.text!=p.text[len(prefix):] or not ruby_after_deletions(p,after,[(0,len(prefix))]):
            raise ValueError('Question prefix removal changed source prose/ruby')
        return out
    from example_layout import slice_inline
    return {'html':slice_inline(value['html'],len(prefix),len(p.text))}


def heading_range_label(conv,label,*,boxed=True):
    """Apply a selected Old number role to a validated heading reference."""
    if not boxed:return r'\HistoricalCompactNumber{'+label+'}'
    if getattr(conv,'historical_inline_number_box_role',None)=='main_question' and re.fullmatch(r'[1-9][0-9]{0,2}',label):
        if not getattr(conv,'source_target_markers',False):raise ValueError('Historical heading number outside Old')
        conv.features.append(dict(kind='historical_inline_number_box',text=label,font_role='boxed_numeral',geometry_role='main_question',context='bound_heading_range',canonical_changed=False))
        return r'\leavevmode\hbox{\hspace{\ClozeClearance}\QNumber{'+label+r'}\hspace{\ClozeClearance}}'
    return r'\Cloze{'+label+'}'
