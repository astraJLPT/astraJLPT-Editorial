"""Authored native memo roles inside rich stems or other content fields."""
import re
from bs4 import BeautifulSoup, Tag, NavigableString
from model import Projection,digest
from notice_layout import html_lines
from example_layout import slice_inline


def fold_geometry(binding):
    """Bound native-table geometry; omitted dimensions retain the old frame."""
    if 'fold_size_pdf_pt' not in binding:
        return None
    fold=binding['fold_size_pdf_pt']
    if (binding.get('layout')not in {'native_table','paragraph_lines'} or not isinstance(fold,dict)
            or set(fold)!={'width','height'}):
        raise ValueError('Embedded fold dimensions require one native table or paragraph memo')
    for key,lo,hi in [('width',12,33),('height',12,24)]:
        value=fold[key]
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not lo<=value<=hi:
            raise ValueError('Invalid embedded fold dimension: '+key)
    return fold


def native_list_parts(node,binding):
    """Select the whole existing caption and unordered list, never flatten them."""
    children=[n for n in node.children if not isinstance(n,NavigableString)or n.strip()]
    if (node.name not in ['div','section'] or len(children)!=2
            or any(not isinstance(n,Tag) for n in children)
            or children[0].name!='p' or children[1].name not in ['ul','p']
            or children[0].find(['p','div','section','table','ul','ol','br'])
            or Projection({'html':str(children[0])}).text.strip('\n')!=binding['title']):
        raise ValueError('Native list memo requires one complete title paragraph and list')
    if children[1].name=='p':
        paragraph=children[1]
        if paragraph.find(['p','div','section','table','ul','ol']) or any(n.find('br') for n in paragraph.find_all('ruby')):
            raise ValueError('Memo paragraph list must contain only simple marked lines')
        lines=html_lines(paragraph.decode_contents())
        plain=[Projection({'html':line}).text for line in lines]
        if (not 1<=len(lines)<=12 or len(paragraph.find_all('br'))!=len(lines)-1
                or any(not s.startswith('・') or not s[1:].strip() for s in plain)
                or Projection({'html':str(paragraph)}).text.strip('\n').split('\n')!=plain):
            raise ValueError('Memo paragraph list requires every complete explicit bullet line')
        listing=BeautifulSoup('<ul></ul>','html.parser').ul
        for raw,text in zip(lines,plain):
            row=BeautifulSoup('<li></li>','html.parser').li
            row['data-literal-list-marker']='・'
            body=BeautifulSoup(slice_inline(raw,1,len(text)),'html.parser')
            for child in list(body.children):row.append(child)
            listing.append(row)
        return children[0],list(listing.find_all('li',recursive=False))
    rows=[n for n in children[1].children if not isinstance(n,NavigableString)or n.strip()]
    if (not 1<=len(rows)<=12 or any(not isinstance(n,Tag)or n.name!='li' for n in rows)
            or any(n.find(['p','div','section','table','ul','ol','br']) for n in rows)
            or any(not Projection({'html':str(n)}).text.strip() for n in rows)):
        raise ValueError('Native list memo requires complete simple nonempty list items')
    return children[0],rows


def prepare(value,binding,source_value=None):
    fold_geometry(binding)
    source=value if source_value is None else source_value
    if digest(source)!=binding['content_sha256'] or not isinstance(value,dict):raise ValueError('Stale embedded document field')
    if Projection(source).text!=Projection(value).text or Projection(source).ruby!=Projection(value).ruby:
        raise ValueError('Prior embedded document presentation changed content/ruby')
    if 'flow_lines' in binding and (binding['flow_lines'] is not True or binding.get('layout')!='paragraph_lines'):
        raise ValueError('Explicit line flow requires a typed paragraph memo')
    soup=BeautifulSoup(value['html'],'html.parser')
    if binding.get('layout')=='paragraph_lines':
        paragraphs=binding['paragraphs']
        if (binding['container_tag']!='p' or binding.get('presentation')not in {'typed_box','handwritten_memo'}
                or not 2<=len(paragraphs)<=12 or paragraphs[0]!=binding['title']
                or binding['text']!='\n'.join(paragraphs)):
            raise ValueError('Invalid typed paragraph memo binding')
        if binding.get('flow_lines'):
            from section_layout import flow_lines
            if not soup.find('br',recursive=False):raise ValueError('Flat memo requires existing root line breaks')
            raw_nodes=[n for n in soup.children if not isinstance(n,NavigableString) or n.strip()]
            if any(isinstance(a,Tag) and a.name=='br' and isinstance(b,Tag) and b.name=='br'
                    for a,b in zip(raw_nodes,raw_nodes[1:])):
                raise ValueError('Flat memo flow must not discard an explicit empty line')
            prepared={'html':''.join(map(str,flow_lines(list(soup.children))))}
            original,current=Projection(value),Projection(prepared)
            if original.text.rstrip('\n')!=current.text.rstrip('\n') or original.ruby!=current.ruby:
                raise ValueError('Flat memo flow changed text, line boundaries or ruby')
            soup=BeautifulSoup(prepared['html'],'html.parser')
        roots=[n for n in soup.children if not isinstance(n,NavigableString)or n.strip()]
        matches=[]
        for start in range(1,len(roots)-len(paragraphs)+1):
            selected=roots[start:start+len(paragraphs)]
            if (all(isinstance(n,Tag) and n.name=='p' and not n.find(['p','div','section','table']) for n in selected)
                    and [Projection({'html':str(n)}).text.strip('\n') for n in selected]==paragraphs):
                matches.append(selected)
        if len(matches)!=1:raise ValueError('Typed memo requires one exact contiguous paragraph group after its question')
        selected=matches[0];group=soup.new_tag('div');group['data-embedded-document']='memo'
        selected[0].insert_before(group)
        for n in selected:group.append(n.extract())
        result={'html':str(soup)}
        original,current=Projection(value),Projection(result)
        same_text=(original.text.rstrip('\n')==current.text.rstrip('\n')) if binding.get('flow_lines') else original.text==current.text
        if not same_text or original.ruby!=current.ruby:
            raise ValueError('Typed memo grouping changed content/ruby')
        return result
    found=[n for n in soup.find_all(binding['container_tag'])if Projection({'html':str(n)}).text==binding['text']]
    if binding.get('layout')=='explicit_email_lines':
        from embedded_email_lines import parts,validate
        validate(binding)
        # A simple outer frame may wrap an identical line container. Select the
        # outermost complete match; independent duplicate documents still fail.
        found=[n for n in found if not any(p in found for p in n.parents)]
        if len(found)!=1:raise ValueError('Explicit email requires one complete outer container')
        parts(found[0],binding)
        found[0]['data-embedded-document']='email'
        result={'html':str(soup)}
        if Projection(value).text!=Projection(result).text or Projection(value).ruby!=Projection(result).ruby:
            raise ValueError('Explicit email tagging changed content/ruby')
        return result
    if len(found)!=1:raise ValueError('Embedded document must select one exact complete container')
    if binding.get('layout')=='native_list':native_list_parts(found[0],binding)
    found[0]['data-embedded-document']='memo'
    result={'html':str(soup)}
    if Projection(value).text!=Projection(result).text or Projection(value).ruby!=Projection(result).ruby:
        raise ValueError('Embedded memo tagging changed content/ruby')
    return result


def render(conv,node,binding,defaults):
    fold=fold_geometry(binding)
    if binding.get('layout')=='explicit_email_lines':
        if node.get('data-embedded-document')!='email':raise ValueError('Explicit email node role changed')
        from embedded_email_lines import render as render_email
        return render_email(conv,node,binding)
    if node.get('data-embedded-document')!='memo' or binding['role']!='memo':raise ValueError('Unknown embedded document role')
    if binding.get('layout')=='paragraph_lines':
        children=[n for n in node.children if isinstance(n,Tag)]
        if (binding.get('presentation')not in {'typed_box','handwritten_memo'} or any(n.name!='p' for n in children)
                or [Projection({'html':str(n)}).text.strip('\n') for n in children]!=binding['paragraphs']):
            raise ValueError('Typed memo paragraph structure changed')
        width=binding.get('width_fraction',.65);padding=binding.get('padding_pt',10)
        if not .5<=width<=1 or not 8<=padding<=30:raise ValueError('Invalid typed memo geometry')
        title=conv.value({'html':children[0].decode_contents()},'option')
        body=r'\par\vspace{3pt}'.join(conv.value({'html':n.decode_contents()},'body') for n in children[1:])
        if binding['presentation']=='handwritten_memo':
            if defaults['font_role']!='memo' or defaults['frame_style']!='folded_corner':raise ValueError('Memo defaults not active')
            text=(r'{\PreserveDocumentDigitstrue\MemoLatin\MemoJapanese\setlength\parindent{0pt}\raggedright '
                  +r'\fontsize{'+str(conv.memo_typography['body_pt'])+'}{'+str(conv.memo_typography['baseline_pt'])+r'}\selectfont '
                  +r'\ltjsetruby{intergap='+str(defaults['ruby_intergap_em'])+',ybaseheight='+str(defaults['ruby_base_height_em'])+'}'
                  +body+r'\par}')
            frame=r'\FoldedMemo{'+str(padding)+'}{'+text+'}'
            if fold is not None:
                frame=(r'{\renewcommand\FoldCornerScaleX{'+str(fold['width']/33)
                       +r'}\renewcommand\FoldCornerScaleY{'+str(fold['height']/21)+'}'+frame+'}')
            conv.features.append({'kind':'embedded_document','role':'memo','layout':'paragraph_lines',
                'presentation':'handwritten_memo','row_count':len(children)-1,'text':binding['text'],
                'title_after_pt':binding.get('title_after_pt',10),'canonical_changed':False})
            return (r'\par\addvspace{8pt}{\centering '+title+r'\par\vspace{'+str(binding.get('title_after_pt',10))+r'pt}'
                    +r'\begin{minipage}{'+str(width)+r'\linewidth}'+frame+r'\end{minipage}\par}\vspace{7pt}')
        frame=(r'\begin{NoticeFrame}[nobreak=true,skipabove=0pt,skipbelow=0pt,linewidth=.6pt,'
            +'innerleftmargin='+str(padding)+'pt,innerrightmargin='+str(padding)+'pt,'
            +'innertopmargin='+str(padding)+'pt,innerbottommargin='+str(padding)+'pt]'
            +r'{\PreserveDocumentDigitstrue\setlength\parindent{0pt}\raggedright '+body+r'\par}\end{NoticeFrame}')
        conv.features.append({'kind':'embedded_document','role':'memo','layout':'paragraph_lines',
            'presentation':'typed_box','row_count':len(children)-1,'text':binding['text'],'canonical_changed':False})
        return (r'\par\addvspace{8pt}\noindent\begin{minipage}{'+str(width)+r'\linewidth}'
            +title+r'\par\vspace{4pt}'+frame+r'\end{minipage}\par\vspace{7pt}')
    if defaults['font_role']!='memo'or defaults['frame_style']!='folded_corner':raise ValueError('Memo defaults not active')
    if binding.get('layout')=='native_list':
        if Projection({'html':str(node)}).text!=binding['text']:
            raise ValueError('Embedded memo must retain its complete native list')
        caption,rows=native_list_parts(node,binding)
        width=binding.get('width_fraction',.8);padding=binding.get('padding_pt',14)
        if not .5<=width<=1 or not 8<=padding<=30:raise ValueError('Invalid memo geometry')
        title=conv.value({'html':caption.decode_contents()},'option')
        old_indent=getattr(conv,'notice_list_indent',None);conv.notice_list_indent=1
        try:body=''.join(conv.node(n,'notice') for n in rows)
        finally:conv.notice_list_indent=old_indent
        text=r'{\PreserveDocumentDigitstrue\MemoLatin\MemoJapanese\ltjsetruby{intergap='+str(defaults['ruby_intergap_em'])+',ybaseheight='+str(defaults['ruby_base_height_em'])+'}'+body+r'\par}'
        conv.features.append({'kind':'embedded_document','role':'memo','layout':'native_list',
            'title':binding['title'],'row_count':len(rows),'text':binding['text'],
            'parameters':defaults,'canonical_changed':False})
        return (r'\par\addvspace{8pt}{\centering '+title+r'\par\vspace{5pt}\begin{minipage}{'
            +str(width)+r'\linewidth}\FoldedMemo{'+str(padding)+'}{'+text+r'}\end{minipage}\par}\vspace{7pt}')
    if binding.get('layout')=='native_table':
        if Projection({'html':str(node)}).text!=binding['text']:
            raise ValueError('Embedded memo must retain its exact native table')
        source_table=node
        if node.name!='table':
            children=[n for n in node.children if not isinstance(n,NavigableString)or n.strip()]
            if (node.name not in ['div','section'] or len(children)!=1
                    or not isinstance(children[0],Tag) or children[0].name!='table'
                    or children[0].find('table')):
                raise ValueError('Contained memo requires exactly one native table and no other content')
            source_table=children[0]
        width=binding.get('width_fraction',.92);padding=binding.get('padding_pt',14)
        if not .5<=width<=1 or not 8<=padding<=30:raise ValueError('Invalid memo geometry')
        # Render the existing cells directly. No transcription, flattened rows,
        # or recursive dispatch through the embedded-document node hook.
        native=BeautifulSoup(str(source_table),'html.parser').table
        cap=native.find('caption',recursive=False);title=''
        if cap:
            title=r'{\centering '+conv.value({'html':cap.decode_contents()},'body')+r'\par}\vspace{6pt}'
            cap.extract()
        text=r'{\PreserveDocumentDigitstrue\MemoLatin\MemoJapanese\ltjsetruby{intergap='+str(defaults['ruby_intergap_em'])+',ybaseheight='+str(defaults['ruby_base_height_em'])+'}'+title+conv.table(native,'body')+'}'
        conv.features.append({'kind':'embedded_document','role':'memo','layout':'native_table',
            'row_count':len(native.find_all('tr')),'text':binding['text'],'parameters':defaults,'canonical_changed':False})
        frame=r'\FoldedMemo{'+str(padding)+'}{'+text+'}'
        if fold is not None:
            frame=(r'{\renewcommand\FoldCornerScaleX{'+str(fold['width']/33)
                   +r'}\renewcommand\FoldCornerScaleY{'+str(fold['height']/21)+'}'+frame+'}')
            conv.features.append({'kind':'embedded_native_table_fold','geometry':fold,
                                  'text':binding['text'],'canonical_changed':False})
        return r'\par\addvspace{8pt}{\centering\begin{minipage}{'+str(width)+r'\linewidth}'+frame+r'\end{minipage}\par}\vspace{7pt}'
    raw=node.decode_contents();lines=html_lines(raw);plain=Projection({'html':str(node)}).text
    if plain!=binding['text'] or len(lines)!=2 or Projection({'html':lines[0]}).text!=binding['title']:
        raise ValueError('Embedded memo title/row structure changed')
    body=Projection({'html':lines[1]}).text;cursor=0;rows=[]
    for row in binding['rows']:
        text=row['label']+row['separator']+row['value'];start=body.find(text,cursor)
        if start<cursor or body[cursor:start].strip() or body.count(text)!=1:raise ValueError('Memo row must preserve exact sequential source text')
        end=start+len(text);label_end=start+len(row['label']);value_start=label_end+len(row['separator'])
        if row['separator'].strip()not in [':','：']:raise ValueError('Memo separator must retain its colon')
        pieces=[slice_inline(lines[1],a,b)for a,b in [(start,label_end),(value_start,end)]]
        rendered=[conv.value({'html':p},'cell')for p in pieces]
        rows.append(rendered[0]+r' & \NoteDefinitionColon{} & '+rendered[1]+r' \\')
        cursor=end
    if body[cursor:].strip():raise ValueError('Memo rows would omit content')
    width=binding.get('width_fraction',.75);padding=binding.get('padding_pt',14)
    if not .5<=width<=1 or not 8<=padding<=30:raise ValueError('Invalid memo geometry')
    table=r'\begin{tblr}{colspec={l c l},colsep=3pt,rowsep=5pt}'+''.join(rows)+r'\end{tblr}'
    text=r'{\PreserveDocumentDigitstrue\MemoLatin\MemoJapanese\ltjsetruby{intergap='+str(defaults['ruby_intergap_em'])+',ybaseheight='+str(defaults['ruby_base_height_em'])+'}'+table+'}'
    title=conv.value({'html':lines[0]},'option')
    conv.features.append({'kind':'embedded_document','role':'memo','title':binding['title'],
        'row_count':len(rows),'text':plain,'parameters':defaults,'canonical_changed':False})
    return r'\par\addvspace{10pt}{\centering '+title+r'\par\vspace{5pt}\begin{minipage}{'+str(width)+r'\linewidth}\FoldedMemo{'+str(padding)+'}{'+text+r'}\end{minipage}\par}\vspace{7pt}'
