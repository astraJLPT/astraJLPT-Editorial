"""Exact complete-line roles; body prose and canonical characters stay intact."""
import re,copy
from bs4 import BeautifulSoup,Tag
from model import Projection,digest


def render(conv,value,tex,spec,context='body',prepared_value=None):
    if digest(value)!=spec['content_sha256']:raise ValueError('Stale document line binding')
    text=Projection(value).text;edits=[];used=set()
    if prepared_value is not None:
        original,current=Projection(value),Projection(prepared_value)
        signature=lambda p:[(r['base'],r['reading'])for r in p.ruby]
        if ''.join(original.text.split())!=''.join(current.text.split())or signature(original)!=signature(current):raise ValueError('Prepared document line changed protected content')
        value=prepared_value
    if getattr(conv,'workbook_font_spans',None):
        from workbook_typography import prepare
        value=prepare(value,conv.workbook_font_spans)
    for row in spec['lines']:
        phrase=row['text'];occurrence=row.get('occurrence',0)
        if not phrase or '\n'in phrase or row['role']not in ['title','recipient','sender','date','signature','closing','body']:
            raise ValueError('Invalid document line role')
        count=sum(line.strip()==phrase for line in text.splitlines())
        if count!=row.get('occurrences',1) or not 0<=occurrence<count:
            raise ValueError('Document line must select an exact complete occurrence')
        matcher=copy.copy(conv);matcher.features=[]
        if isinstance(value,dict):
            from section_layout import flow_lines
            soup=BeautifulSoup(value['html'],'html.parser')
            nodes=flow_lines(list(soup.children))
            selected=[n for n in nodes if Projection({'html':str(n)}).text.strip()==phrase]
            if len(selected)!=count:
                selected=[n for n in soup.find_all(['p','div','center'])if not n.find(['p','div','center','table'])and Projection({'html':str(n)}).text.strip()==phrase]
            if len(selected)!=count:raise ValueError('Document line requires a whole structural node')
            fragments=[]
            for n in selected:
                native=matcher.node(n,context)
                native=re.sub(r'^(?:\s*\\(?:Para|EmailLine)\s*)+|(?:\s*\\(?:Para|EmailLine)\s*)+$','',native).strip()
                body=matcher.value({'html':n.decode_contents()},context)if isinstance(n,Tag)else native
                fragments.append((native,body))
            if len(set(fragments))!=1:raise ValueError('Repeated document line has distinct markup; use a narrower structural binding')
            native,display=fragments[0]
        else:native=display=matcher.value(phrase,context)
        pattern=re.compile(r'(^|\\(?:Para|EmailLine)\s*)('+re.escape(native)+r')(?=\s*(?:\\(?:Para|EmailLine)\b|\\begin\{ReadingNotes\}|$))')
        hits=list(pattern.finditer(tex))
        if len(hits)!=count:raise ValueError('Document line did not reach an exact native paragraph: '+phrase)
        hit=hits[occurrence];a,b=hit.span(2)
        if(a,b)in used:raise ValueError('Duplicate document line role')
        used.add((a,b));align=row.get('align',{'title':'center','recipient':'left','sender':'right','date':'right','signature':'left','closing':'right','body':'left'}[row['role']])
        if align not in ['left','center','right']:raise ValueError('Invalid document line alignment')
        indent=row.get('indent_em',1 if row['role']=='body'else 0)
        before=row.get('before_pt',0);after=row.get('after_pt',0)
        if any(isinstance(x,bool)or not isinstance(x,(int,float))or x<0 for x in [indent,before,after])or indent>2 or max(before,after)>40:
            raise ValueError('Invalid document line spacing')
        output=r'\DocumentLine{'+{'left':'l','center':'c','right':'r'}[align]+'}{'+str(indent)+'}{'+str(before)+'}{'+str(after)+'}{'+display+'}'
        edits.append((a,b,output));conv.features.append({'kind':'document_line_role','text':phrase,'occurrence':occurrence,'role':row['role'],'alignment':align})
    for a,b,out in sorted(edits,reverse=True):tex=tex[:a]+out+tex[b:]
    return tex
