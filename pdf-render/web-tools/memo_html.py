"""HTML adapter for the native, exactly bound embedded document roles."""
from bs4 import BeautifulSoup
from model import Projection
from semantic_html import add_class,add_style,pt,gap
from embedded_documents import prepare as prepare_native, native_list_parts
from notice_layout import html_lines
from presentation_slice import slice_inline

def prepare(value,m,q):
    binding=m['style'].get('embedded_documents',{}).get(q['id'])
    if not binding:return value
    from presentation import source_binding
    source_binding(m['unit'],binding['evidence'])
    return prepare_native(value,binding,q['stem'])

def folded_corner(soup,node,width=33,height=21,rule=.45):
    """FoldedMemo's interrupted outline and multi-segment flap, in PDF bp."""
    add_class(node,'native-folded-memo')
    add_style(node,position='relative',padding_bottom=f'max({pt(height*22/21+4)},var(--memo-bottom-padding,0px))')
    svg=BeautifulSoup('<svg class="memo-fold visual-only" aria-hidden="true" focusable="false" viewBox="0 0 33 22" preserveAspectRatio="none"><path d="M0 0H34V23H0Z" fill="var(--paper)" stroke="none"/><path d="M0 22L33 1M0 22L9 0L22 3L33 1" fill="none" stroke="currentColor" vector-effect="non-scaling-stroke"/></svg>','html.parser').svg
    add_style(svg,position='absolute',right=pt(-rule),bottom=pt(-rule),width=pt(width*72.27/72),height=pt(height*22/21*72.27/72),overflow='visible',pointer_events='none',stroke_width=pt(rule))
    node.append(svg)

def present(soup,m,q):
    binding=m['style'].get('embedded_documents',{}).get(q['id'])
    if not binding:return
    nodes=soup.select('[data-embedded-document]')
    if len(nodes)!=1:raise ValueError('Embedded document lost its single validated region')
    node=nodes[0];layout=binding.get('layout','rows');role=binding['role']
    handwritten=role=='memo' and binding.get('presentation')!='typed_box'
    task=next(m['tasks'][s['id']] for s in m['document']['sections'] if any(i['id']==q['id'] for i in s['items']))
    task_style={**m['style'],**m['style'].get('task_overrides',{}).get(task,{})}
    width=binding.get('width_fraction',1 if role=='email' else {'native_table':.92,'native_list':.8,'paragraph_lines':.65}.get(layout,.75))
    padding=binding.get('padding_pt',8 if role=='email' else 10 if layout=='paragraph_lines' else 14)
    # The whole table (and its caption) remains inside the fold. Lists/rows and
    # paragraph memos keep the native external caption instead.
    region=soup.new_tag('div',attrs={'class':'embedded-document','data-document-role':role,'data-document-layout':layout})
    node.insert_before(region)
    frame=soup.new_tag('div',attrs={'class':'embedded-document-frame'})
    title=None
    if layout=='native_table':
        container=node.find_parent(class_='table-scroll')
        if container:
            region.extract();container.insert_before(region);frame.append(container.extract())
        else:frame.append(node.extract())
        table=frame.find('table');scroll=table.find_parent(class_='table-scroll')
        spec=m['style'].get('table_styles',{}).get(q['id'],{}).get('0',{})
        caption=table.find('caption',recursive=False)
        if caption:
            caption.extract();caption.name='div';add_class(caption,'embedded-table-caption')
            add_style(caption,text_align='center',margin_bottom=gap(6))
            (scroll or table).insert_before(caption)
        add_style(scroll or table,margin_top=gap(spec.get('before_pt',6)),margin_bottom=gap(spec.get('after_pt',6)))
    elif layout=='native_list':
        # The original container was validated before font/space markup.
        title=node.find('p',recursive=False);title.extract()
        for child in list(node.contents):frame.append(child.extract())
        node.decompose()
        for listing in frame.find_all('ul'):
            add_style(listing,margin='0',padding_left='1em',list_style_position='outside')
    elif layout=='paragraph_lines':
        title=node.find('p',recursive=False);title.extract()
        for child in list(node.contents):frame.append(child.extract())
        node.decompose()
    elif layout=='rows':
        lines=html_lines(node.decode_contents());title=soup.new_tag('div')
        title.append(BeautifulSoup(lines[0],'html.parser'))
        body=Projection({'html':lines[1]}).text;cursor=0
        table=soup.new_tag('div',attrs={'class':'embedded-memo-rows'})
        for row in binding['rows']:
            text=row['label']+row['separator']+row['value'];start=body.find(text,cursor)
            if start<cursor or body[cursor:start].strip():raise ValueError('Memo row order changed')
            end=start+len(text);label_end=start+len(row['label']);value_start=label_end+len(row['separator'])
            for col,(a,b) in enumerate([(start,label_end),(label_end,value_start),(value_start,end)]):
                cell=soup.new_tag('span');raw=slice_inline(lines[1],a,b)
                if col==1:
                    # The bound row separator is a label colon even when the
                    # flat source line contains multiple label/value pairs.
                    if row['separator'].strip() not in (':','：'):raise ValueError('Invalid memo row separator')
                    literal=soup.new_tag('span',attrs={'class':'source-literal sr-only'});literal.append(BeautifulSoup(raw,'html.parser'));cell.append(literal)
                    visible=soup.new_tag('span',attrs={'class':'visual-only','aria-hidden':'true','data-memo-label-colon':'true'});visible.string='：';add_style(visible,margin_left='.12em',margin_right='.12em');cell.append(visible)
                else:cell.append(BeautifulSoup(raw,'html.parser'))
                table.append(cell)
            cursor=end
        if body[cursor:].strip():raise ValueError('Unconsumed memo row text')
        add_style(table,column_gap=pt(6),row_gap=pt(10),padding=f'{pt(5)} {pt(3)}')
        frame.append(table);node.decompose()
    elif layout=='explicit_email_lines':
        for child in list(node.contents):frame.append(child.extract())
        node.decompose()
    else:raise ValueError('Unknown embedded document layout')
    if title:
        add_class(title,'embedded-document-caption');add_style(title,text_indent='0',margin='0',text_align='center' if handwritten else 'left',margin_bottom=gap(binding.get('title_after_pt',5 if layout in ('rows','native_list') else 10 if binding.get('presentation')=='handwritten_memo' else 4)))
        region.append(title)
    region.append(frame)
    for old in frame.select('.source-native-frame'):
        old['class']=[c for c in old.get('class',[]) if c!='source-native-frame']
        add_style(old,border='0',padding='0',margin='0')
    # Every native embedded-document body enables PreserveDocumentDigits.
    # Remove the content-numeral width/scale wrapper inside that exact region;
    # ordinary question/options and external captions keep their own roles.
    from document_font_html import preserve_document_digits, memo_font
    preserve_document_digits(soup,frame)
    add_style(region,width=f'{width*100}%',margin_left='auto' if handwritten else '0',margin_right='auto' if handwritten else '0',margin_top=gap(10 if layout=='rows' else 8),margin_bottom=gap(7),text_indent='0',max_width='100%')
    add_style(frame,border=f'{pt(.5 if role=="email" else .6 if binding.get("presentation")=="typed_box" else .45)} solid currentColor',padding=pt(padding),text_indent='0',**{'--memo-bottom-padding':pt(padding)})
    if handwritten:
        typo=m['style'].get('memo_typography',{})
        body_pt=typo.get('body_pt',m['style']['body_pt'])
        baseline=typo.get('baseline_pt',task_style['baseline_pt']) if layout=='paragraph_lines' else task_style['baseline_pt']
        add_style(frame,line_height=pt(baseline))
        memo_font(soup,frame,m['style'],body_pt)
        fold=binding.get('fold_size_pdf_pt',{'width':33,'height':21})
        folded_corner(soup,frame,fold['width'],fold['height'])
    elif role=='email':
        add_style(frame,font_size=f'calc(var(--glyph-point) * {binding["body_pt"]})',line_height=pt(binding['baseline_pt']),white_space='nowrap',overflow_x='auto')
    paragraphs=frame.find_all('p')
    for p in paragraphs:add_style(p,text_indent='0',margin_top='0',margin_bottom=gap(3 if layout=='paragraph_lines' and p is not paragraphs[-1] else 0))
