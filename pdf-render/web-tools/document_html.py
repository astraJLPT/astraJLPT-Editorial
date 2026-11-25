"""Bound document lines, metadata columns and rule families for the shared reader."""
import re
from bs4 import BeautifulSoup
from model import Projection,digest
from presentation_slice import slice_inline
from notice_layout import html_lines
from semantic_html import add_style,add_class,pt,gap,reject_unknown


def bound_lines(raw,before=None):
    # Mixing HTML and XML spellings of void br tags confuses html.parser when
    # fragments are concatenated. Consistent void tags keep the full last line.
    raw=re.sub(r'<br\s*/?>','<br/>',raw)
    soup=BeautifulSoup(raw,'html.parser')
    for space in soup.select('.tex-word-space'):
        # The upstream splitter preserves authored gap atoms, whereas ordinary
        # whitespace-only spans are discarded. Keep already resolved web glue.
        space['data-authored-word-gap']='preserved'
    chunks=html_lines(str(soup))
    if not before:return chunks
    hits=[(i,Projection({'html':chunk}).text) for i,chunk in enumerate(chunks) if before in Projection({'html':chunk}).text]
    if len(hits)!=1 or hits[0][1].count(before)!=1:raise ValueError('Bound line break must select one exact inline span')
    i,text=hits[0];at=text.index(before)
    if not at:raise ValueError('Bound line break already begins a line')
    chunks[i:i+1]=[slice_inline(chunks[i],0,at),slice_inline(chunks[i],at,len(text))]
    return chunks


def select_line(soup,text,occurrences=1,occurrence=0,space_equivalent=False):
    tags=['p','div','center','h3','h4']
    normalize=lambda v:v.replace('\u3000',' ') if space_equivalent else v
    from section_layout import flow_lines
    # Some source rectangles begin with a bare recipient before their first p.
    if any(not getattr(n,'name',None) and str(n).strip() for n in soup.contents):
        children=flow_lines(list(soup.contents));soup.clear()
        for child in children:soup.append(child)
    def semantic(n):
        clone=BeautifulSoup(str(n),'html.parser')
        for visual in clone.select('.visual-only,.annotation-label'):visual.decompose()
        return normalize(Projection({'html':str(clone)}).text.strip())
    matches=[n for n in soup.find_all(tags) if not n.find(tags+['table']) and semantic(n)==text]
    if not matches and '\n' in text:
        expected=text.splitlines()
        for first in list(soup.find_all(tags)):
            sequence=[first,*first.find_next_siblings(limit=len(expected)-1)]
            if len(sequence)==len(expected) and [Projection({'html':str(n)}).text.strip() for n in sequence]==expected:
                region=BeautifulSoup('','html.parser').new_tag('div');first.insert_before(region)
                for n in sequence:region.append(n.extract())
                matches.append(region)
    if len(matches)!=occurrences:
        for node in list(soup.find_all(tags)):
            if node.find(tags+['table']) or not node.find('br'):continue
            chunks=html_lines(node.decode_contents())
            if not any(normalize(Projection({'html':c}).text.strip())==text for c in chunks):continue
            for chunk in chunks:
                p=BeautifulSoup('','html.parser').new_tag('p');p.append(BeautifulSoup(chunk,'html.parser'));node.insert_before(p)
            node.decompose()
        matches=[n for n in soup.find_all(tags) if not n.find(tags+['table']) and semantic(n)==text]
    if not matches:
        # A source line may own a mixed inline lead and a nested paragraph.
        # Select only the deepest exact complete container; never a substring.
        candidates=[n for n in soup.find_all(tags) if not n.find('table') and semantic(n)==text]
        matches=[n for n in candidates if not any(other is not n and n in other.parents for other in candidates)]
    if len(matches)!=occurrences or not 0<=occurrence<len(matches):raise ValueError('Exact document line not found: '+text)
    return matches[occurrence]


def rule_style(node,rule,edge='bottom'):
    from document_rules import rule_tex
    rule_tex(rule)
    add_style(node,**{'border_'+edge:f'{pt(rule["width_pt"])} {rule["pattern"]} color-mix(in srgb,currentColor {(1-rule["gray"])*100}%,var(--paper))'})


def metadata_html(fragments,rows,width=5):
    soup=BeautifulSoup('','html.parser');out=[];texts=[Projection({'html':raw}).text for raw in fragments];covered=[[] for _ in fragments];previous=(-1,-1)
    for row in rows:
        sep=row.get('separator',row.get('colon'));text=row['label']+sep+row['value']
        hits=[(i,m.start(),m.end()) for i,t in enumerate(texts) for m in re.finditer(re.escape(text),t)]
        if len(hits)!=1:raise ValueError('Metadata row must select one exact source span')
        i,a,b=hits[0]
        if (i,a)<=previous:raise ValueError('Metadata rows changed order')
        previous=(i,a);covered[i].append((a,b));l=a+len(row['label']);v=l+len(sep)
        node=soup.new_tag('div',attrs={'class':'document-metadata-row'})
        add_style(node,grid_template_columns=f'calc(var(--nominal-em) * {width}) .8em minmax(0,1fr)')
        for x,y in [(a,l),(l,v),(v,b)]:
            part=soup.new_tag('span');part.append(BeautifulSoup(slice_inline(fragments[i],x,y),'html.parser'));node.append(part)
        out.append(str(node))
    for text,ranges in zip(texts,covered):
        if ''.join(c for n,c in enumerate(text) if not any(a<=n<b for a,b in ranges)).strip():raise ValueError('Metadata would omit content')
    return ''.join(out)


def present_lines(soup,source,spec):
    if digest(source)!=spec['content_sha256']:raise ValueError('Stale document line binding')
    for row in spec['lines']:
        reject_unknown(row,'text role occurrence occurrences align indent_em before_pt after_pt','document line')
        node=select_line(soup,row['text'],row.get('occurrences',1),row.get('occurrence',0))
        role=row['role'];align=row.get('align',{'title':'center','sender':'right','date':'right','closing':'right'}.get(role,'left'))
        add_class(node,'document-line-'+role)
        add_style(node,text_align=align,text_indent=f'calc(var(--nominal-em) * {row.get("indent_em",1 if role=="body" else 0)})',margin_top=gap(row.get('before_pt',0)),margin_bottom=gap(row.get('after_pt',0)))


def present_fields(soup,source,binding):
    if digest(source)!=binding['content_sha256']:raise ValueError('Stale document field binding')
    for row in binding['rows']:
        node=select_line(soup,row['text']);raw=node.decode_contents();text=Projection({'html':raw}).text;cursor=0;parts=[];columns=[]
        for j,field in enumerate(row['fields']):
            phrase=field['label']+field['separator']+field['value'];at=text.find(phrase,cursor)
            if at<0 or text[cursor:at].strip():raise ValueError('Document fields changed content/order')
            a=at+len(field['label']);b=a+len(field['separator']);end=at+len(phrase)
            for x,y in [(at,a),(a,b),(b,end)]:parts.append(slice_inline(raw,x,y) if y>x else '')
            columns += [f'calc(var(--nominal-em) * {binding["label_width_em"]})',f'calc(var(--nominal-em) * {binding.get("separator_width_em",0)})',f'calc(var(--nominal-em) * {field["value_width_em"]})' if j<len(row['fields'])-1 else 'minmax(0,1fr)']
            cursor=end
        if text[cursor:].strip():raise ValueError('Document fields omit content')
        node.clear();add_class(node,'document-metadata-row');add_style(node,grid_template_columns=' '.join(columns),text_indent='0')
        for part in parts:
            span=soup.new_tag('span');span.append(BeautifulSoup(part,'html.parser'));node.append(span)


def email_details(frame,source,spec):
    for item in spec.get('spaced_paragraphs',[]):
        prefix=item['starts_with']
        hits=[n for n in frame.find_all(['p','div']) if not n.find(['p','div']) and Projection({'html':str(n)}).text.lstrip().startswith(prefix)]
        if not hits and '\n' in prefix:
            # Plain source line breaks can be separate native flow paragraphs.
            start,following=prefix.split('\n',1)
            hits=[n for n in frame.find_all(['p','div']) if not n.find(['p','div']) and Projection({'html':str(n)}).text.strip()==start and n.find_next_sibling() and Projection({'html':str(n.find_next_sibling())}).text.lstrip().startswith(following)]
        # Full bound paragraphs win over prefixes shared by another paragraph.
        exact=[n for n in hits if Projection({'html':str(n)}).text.strip()==prefix]
        if len(exact)==1:hits=exact
        if len(hits)!=1:raise ValueError('Ambiguous email paragraph boundary: '+prefix)
        add_style(hits[0],margin_top=gap(item['before_pt']))
    if spec.get('last_header_line'):
        last=select_line(frame,spec['last_header_line']);bar=BeautifulSoup('<div class="email-inner-rule" aria-hidden="true"></div>','html.parser').div
        existing=last.find_next_sibling()
        if existing and existing.name=='hr':existing.decompose()
        rule_style(bar,spec['rule_set'].get('inner',spec['rule_set']['top']))
        add_style(bar,margin_top=gap(spec.get('metadata_to_rule_pt',10)),margin_bottom=gap(spec.get('rule_to_body_pt',8)));last.insert_after(bar)
    if spec.get('metadata'):
        meta=spec['metadata'];rows=meta['rows'];selected=[select_line(frame,r['label']+r['colon']+r['value']) for r in rows]
        markup=metadata_html([n.decode_contents() for n in selected],rows,meta.get('label_width_em',3))
        region=BeautifulSoup('<div class="email-metadata">'+markup+'</div>','html.parser').div;selected[0].insert_before(region)
        for node in selected:node.decompose()
    for edge in ('top','bottom'):
        if edge in spec.get('rule_set',{}):rule_style(frame,spec['rule_set'][edge],edge)
    internal=spec.get('rule_set',{}).get('internal',[]);bars=frame.find_all('hr')
    if len(internal)!=len(bars):
        if internal or bars:raise ValueError('Email internal rule count changed')
    for bar,rule in zip(bars,internal):
        add_style(bar,border='0',margin_top=gap(8),margin_bottom=gap(8));rule_style(bar,rule)
    if spec.get('rule_set',{}).get('terminal_internal_as_bottom'):
        if not bars or internal[-1]!=spec['rule_set']['bottom'] or Projection({'html':''.join(map(str,bars[-1].next_siblings))}).text.strip():raise ValueError('Email terminal rule changed')
        bars[-1].decompose()


def paragraph_breaks(soup,source,binding):
    from semantic_html import projection_binding
    projection_binding(source,binding,'paragraph break')
    original=Projection(source)
    for row in binding['starts']:
        at=row['offset'];prefix=row['prefix']
        if at<=0 or original.text[at:at+len(prefix)]!=prefix or original.overlaps_ruby(at,at):raise ValueError('Stale paragraph start')
        containers=[n for n in soup.find_all(['p','div','section']) if prefix in Projection({'html':str(n)}).text]
        for container in [n for n in containers if not any(other is not n and n in other.parents for other in containers)]:
            if container.name!='p':
                from section_layout import flow_lines
                children=flow_lines(list(container.contents));container.clear()
                for child in children:container.append(child)
        candidates=[n for n in soup.find_all(['p','div']) if not n.find(['p','div','table','section']) and prefix in Projection({'html':str(n)}).text]
        if len(candidates)!=1:raise ValueError('Paragraph start needs one exact rendered span')
        node=candidates[0];raw=node.decode_contents();text=Projection({'html':raw}).text;at=text.index(prefix)
        if text.count(prefix)!=1:raise ValueError('Ambiguous paragraph prefix')
        if at:
            lead=soup.new_tag('p');lead.append(BeautifulSoup(slice_inline(raw,0,at),'html.parser'));node.insert_before(lead)
            node.clear();node.append(BeautifulSoup(slice_inline(raw,at,len(text)),'html.parser'))
        add_style(node,text_indent='var(--nominal-em)')
