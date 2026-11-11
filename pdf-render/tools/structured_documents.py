"""Authored document roles over unchanged complete lines and inline ruby.

The author supplies every group in original order. Metadata rows may recover
layout from a merged line, but must exhaust its exact label/colon/value text.
"""
import html,re
from bs4 import BeautifulSoup
from model import Projection,digest
from notice_layout import html_lines
from example_layout import slice_inline


def lines(value, split_prefixes=None):
    raw=value['html']if isinstance(value,dict)else html.escape(value).replace('\n','<br/>')
    soup=BeautifulSoup(raw,'html.parser')
    if soup.find(['table','img','section']):raise ValueError('Structured line document cannot discard a table, image or section')
    # Source-plain fields promoted by frozen ruby retain literal newline breaks.
    if not soup.find(['p','div','br','center']):raw=raw.replace('\n','<br/>')
    result=html_lines(raw)
    if split_prefixes:
        from semantic_lines import split_before
        result=split_before(result,split_prefixes)
    return result


def metadata(conv,fragments,spec):
    width=spec.get('label_width_em',5)
    if isinstance(width,bool)or not isinstance(width,(int,float))or not 1<=width<=12:raise ValueError('Invalid metadata label width')
    projections=[Projection({'html':x})for x in fragments];used=[[]for _ in fragments];rendered=[]
    previous=(-1,-1)
    for row in spec['rows']:
        text=row['label']+row['separator']+row['value']
        if row['separator'].strip()not in [':','：']or not row['label']or not row['value']:raise ValueError('Invalid metadata row')
        hits=[(j,m.start(),m.end())for j,p in enumerate(projections)for m in re.finditer(re.escape(text),p.text)]
        if len(hits)!=1:raise ValueError('Metadata row must select one exact source span')
        j,a,b=hits[0]
        if(j,a)<=previous or any(max(a,x)<min(b,y)for x,y in used[j]):raise ValueError('Metadata rows changed order or overlap')
        previous=(j,a);used[j].append((a,b));label_end=a+len(row['label']);value_start=label_end+len(row['separator'])
        label=slice_inline(fragments[j],a,label_end);value=slice_inline(fragments[j],value_start,b)
        rendered.append(r'\DocumentMetadataRow{'+str(width)+'}{'+conv.value({'html':label},'option')+'}{'+conv.text(row['separator'].strip())+'}{'+conv.value({'html':value},'body')+'}')
    for p,ranges in zip(projections,used):
        remainder=''.join(c for n,c in enumerate(p.text)if not any(a<=n<b for a,b in ranges))
        if remainder.strip():raise ValueError('Metadata rows would omit source text')
    return ''.join(rendered)


def render(conv,value,binding):
    if digest(value)!=binding['content_sha256']:raise ValueError('Stale structured document')
    raw=lines(value,binding.get('split_before'));texts=[Projection({'html':x}).text.strip()for x in raw]
    if [x for g in binding['groups']for x in g['lines']]!=texts:
        raise ValueError('Document groups must cover every exact line once and in order')
    if binding['genre']not in ['email','formal_letter','internal_notice','web_notice','public_notice']:raise ValueError('Unknown document genre')
    out=[];cursor=0
    for group in binding['groups']:
        count=len(group['lines']);fragments=raw[cursor:cursor+count];cursor+=count
        if not count:raise ValueError('Empty document group')
        role=group['role'];before=group.get('before_pt',0);after=group.get('after_pt',0)
        if any(isinstance(x,bool)or not isinstance(x,(int,float))or not 0<=x<=40 for x in [before,after]):raise ValueError('Invalid document gap')
        if 'instruction_inset_em' in group:
            inset=group['instruction_inset_em']
            if (role!='instruction' or isinstance(inset,bool)
                    or not isinstance(inset,(int,float)) or not 0<=inset<=14):
                raise ValueError('Instruction inset requires an instruction role and 0–14em')
        if role=='prefix':
            out.extend(conv.value({'html':x},'body')+r'\Para 'for x in fragments);continue
        if role=='metadata':body=metadata(conv,fragments,group)
        else:
            if role not in ['title','recipient','sender','date','signature','body','greeting','closing','contact','instruction','plain']:raise ValueError('Unknown document group role')
            values=[{'html':x}for x in fragments]
            if binding['genre']=='email' and role in ['body','greeting','closing']:
                from email_family import prepare_padding
                for index,value_part in enumerate(values):
                    values[index],offsets=prepare_padding(value_part)
                    if offsets:
                        conv.features.append({'kind':'structured_email_padding','role':role,
                            'source_line':cursor-count+index,'offsets':offsets,
                            'content_sha256':binding['content_sha256'],'canonical_changed':False})
            parts=[conv.value(part,'body')for part in values]
            if role=='instruction':
                marker=group['marker']
                if len(fragments)!=1 or not texts[cursor-1].startswith(marker)or len(marker)!=1:raise ValueError('Instruction needs its exact leading marker')
                text=Projection({'html':fragments[0]}).text;start=text.index(marker)
                if text[:start].strip():raise ValueError('Instruction marker has preceding content')
                content=slice_inline(fragments[0],start+1,len(text))
                body=r'\DocumentInstruction{'+conv.text(marker)+'}{'+conv.value({'html':content},'body')+'}'
                if 'instruction_inset_em' in group:
                    body=r'{\advance\leftskip by '+str(inset)+r'em\relax '+body+'}'
                    conv.features.append({'kind':'structured_instruction_inset','marker':marker,
                        'text':texts[cursor-1],'inset_em':inset,'continuation_hang_em':1.2})
            else:
                align=group.get('align',{'title':'center','sender':'right','date':'right','closing':'right'}.get(role,'left'))
                if align not in ['left','center','right']:raise ValueError('Unknown document alignment')
                default_indent=(getattr(conv,'email_first_line_indent_em',0) if binding['genre']=='email' else 1) if role=='body' else 0
                indent=group.get('indent_em',default_indent)
                if not isinstance(indent,(int,float))or isinstance(indent,bool)or not 0<=indent<=2:raise ValueError('Invalid document indent')
                join=group.get('join','hard')
                if join not in ['hard','soft']:raise ValueError('Unknown document line joining')
                body=(r'\par\noindent 'if join=='hard'else' ').join(parts)
                body=r'\DocumentLine{'+{'left':'l','center':'c','right':'r'}[align]+'}{'+str(indent)+'}{0}{0}{'+body+'}'
        ending=r'\par\vspace{'+str(after)+'pt}'
        if 'rule_after' in group:
            from document_rules import rule_tex
            gap=group.get('rule_after_gap_pt',8)
            if role!='metadata' or isinstance(gap,bool) or not isinstance(gap,(int,float)) or not 0<=gap<=40:
                raise ValueError('Structured metadata rule requires a valid following gap')
            ending+=rule_tex(group['rule_after'])+r'\nobreak\vspace{'+str(gap)+'pt}'
        elif 'rule_after_gap_pt' in group:
            raise ValueError('Structured rule gap requires its metadata rule')
        out.append(r'\par\addvspace{'+str(before)+'pt}'+body+ending)
    conv.features.append({'kind':'structured_document','genre':binding['genre'],'source_line_count':len(raw),
       'roles':[{'role':g['role'],'lines':len(g['lines'])}for g in binding['groups']],
       'content_sha256':binding['content_sha256'],'all_source_lines_once':True,'canonical_changed':False})
    return ''.join(out)
