"""Additional source-bound flow roles in the shared HTML reader."""
import json
import re
from bs4 import BeautifulSoup
from model import Projection, digest
from semantic_html import add_style, add_class, pt, gap
from presentation_slice import slice_inline


def em(value):
    return f'calc(var(--nominal-em) * {value})'


def inline_atoms(soup, m):
    from tex_html import visual_atom
    from historical_inline_atoms import kana_profiles
    cfg=m['style']['historical_typography']
    for node in soup.select('[data-historical-answer-slot]'):
        role=node['data-historical-answer-slot'];text=node.get_text();box=node.select_one('[data-native-inline-box="label"]')
        if role=='dialogue_phrase_answer_line':
            width=float(node['data-historical-slot-width'])
            visual_atom(soup,node,'old-bound-answer-line','')
            add_style(node,display='inline-block',width=em(width),border_bottom=f'{pt(.4)} solid currentColor',height='0.9em',vertical_align='baseline')
            continue
        if role=='compact_reference_range':
            add_style(node,white_space='nowrap',letter_spacing='-.08em',margin_right=em(.2))
            continue
        middle=text[1:-1].strip();width=float(node.get('data-historical-slot-width',cfg.get('slot_inner_width_em',2.4)))
        outer=cfg.get('slot_outer_gap_em',.18);side=.45
        if role=='kana_answer_slot':
            width=kana_profiles()[node['data-historical-kana-width']]['inner_width_em'];outer=0
        if role=='boxed_parenthesized_answer_slot':
            if not node.has_attr('data-historical-slot-width'):
                add_style(node,white_space='nowrap');continue
            outer=0
        if role=='bracket_answer_slot':side=1;outer=0
        if role=='corner_answer_slot':side=.5
        visual_atom(soup,node,'old-bound-answer-slot','')
        visual=node.select_one('.visual-only');add_style(visual,display='inline-flex',align_items='baseline',white_space='nowrap')
        left=soup.new_tag('span');left.string=text[0];add_style(left,display='inline-block',width=em(side),text_align='right')
        inner=soup.new_tag('span');add_style(inner,display='inline-block',width=em(width),text_align='center')
        if box:inner.append(BeautifulSoup(str(box),'html.parser'))
        else:inner.string=middle
        if role=='kana_answer_slot':add_style(inner,font_family='Heading' if node['data-historical-kana-font']=='gothic' else 'Body')
        right=soup.new_tag('span');right.string=text[-1];add_style(right,display='inline-block',width=em(side),text_align='left')
        for part in (left,inner,right):visual.append(part)
        add_style(node,display='inline-block',text_indent='0',margin_left=em(outer),margin_right=em(float(node.get('data-historical-slot-after',outer))))


def prose_role(soup,node,m):
    role=node['data-historical-text-role'];style=m['style'];cfg=style['historical_typography']
    if role=='numbered_introduction':
        raw=node.decode_contents();text=Projection({'html':raw}).text;match=re.match(r'^[（(][0-9０-９]+[）)]',text)
        if not match:raise ValueError('Numbered introduction lost its source label')
        node.clear();label=soup.new_tag('span');label.append(BeautifulSoup(slice_inline(raw,0,match.end()),'html.parser'))
        add_style(label,display='inline-block',width=em(style.get('inline_passage_label_width_em',2.5)),text_indent='0',white_space='nowrap')
        node.append(label);node.append(BeautifulSoup(slice_inline(raw,match.end(),len(text)),'html.parser'))
        add_style(node,text_indent='0',margin_bottom=gap(cfg.get('introduction_after_pt',8)))
    elif role=='source_annotation':
        inset=float(node.get('data-historical-inset',0));add_style(node,font_size=f'calc(var(--glyph-point) * {style["note_pt"]*.75})',line_height=pt(style['note_baseline_pt']*.75),padding_left=em(inset+1),text_indent=em(-1),margin_top=gap(4))
    elif role=='document_headline':
        add_style(node,font_family='Heading',font_size='1.18em',line_height='1.18lh',text_indent='0',margin_left=em(1),margin_bottom=gap(16))
    elif role=='question_instruction':
        add_style(node,text_indent='0',margin_top=gap(2*style['baseline_pt']),margin_bottom=gap(8))
    elif role=='embedded_query':
        cfg=cfg['embedded_query'];raw=node.decode_contents();text=Projection({'html':raw}).text;end=len('【しつもん】')
        label=soup.new_tag('span');label.append(BeautifulSoup(slice_inline(raw,0,end),'html.parser'));add_style(label,display='inline-block',width=em(cfg['width_em']),text_indent='0')
        if cfg.get('label_font_role')=='task_label':add_style(label,font_family='TaskLabelJapanese')
        node.clear();node.append(label);node.append(BeautifulSoup(slice_inline(raw,end,len(text)),'html.parser'))
        add_style(node,display='block',padding_left=em(cfg['left_inset_em']+cfg['width_em']-cfg['continuation_pullback_em']),text_indent=em(cfg['continuation_pullback_em']-cfg['width_em']),margin_top=gap(cfg['before_pt']))
    elif role=='labeled_paragraph':
        label=node.select_one('[data-historical-margin-label="true"]')
        if label is None:raise ValueError('Missing bound paragraph margin label')
        add_style(node,position='relative',margin_left=em(3),text_indent=em(1),margin_bottom=gap(7))
        add_style(label,position='absolute',left=em(-3),top='0',bottom='0',writing_mode='vertical-rl',font_family='Heading',font_size=pt(10),text_indent='0',display='flex',justify_content='center')
        bracket=soup.new_tag('span',attrs={'class':'old-paragraph-bracket visual-only','aria-hidden':'true'});add_style(bracket,position='absolute',left=em(-.8),top='0',bottom='0',width=em(.4),border_left=f'{pt(.5)} solid currentColor',border_top=f'{pt(.5)} solid currentColor',border_bottom=f'{pt(.5)} solid currentColor');node.append(bracket)
    else:raise ValueError('Unknown Old prose role: '+role)


def components(soup,m,item):
    meta=m['layout']['items'][item['id']]
    if meta.get('historical_target_dialogue'):
        from historical_groups import target_dialogue_turns
        turns=target_dialogue_turns(item,meta['historical_target_dialogue'],m['unit'])
        paragraphs=soup.find_all('p',recursive=False)
        if len(paragraphs)!=len(turns):raise ValueError('Bound target dialogue lost paragraphs')
        kana=Projection(item['content']).text.startswith('とい')
        for p in paragraphs:add_style(p,padding_left=em(3 if kana else 2),text_indent=em(1),margin='0')
    for node in soup.select('[data-historical-frame-paragraph]'):
        spec=json.loads(node['data-historical-frame-paragraph']);add_style(node,margin_top=gap(spec.get('before_pt',0)),margin_bottom=gap(spec.get('after_pt',0)),text_indent='0')
        if spec['role']=='title':add_style(node,text_align='center')
        if spec['role']=='list':add_style(node,padding_left=em(spec['hanging_em']),text_indent=em(-spec['hanging_em']))
    for node in soup.select('[data-historical-framed-document="single"],[data-historical-labeled-frame]'):
        add_style(node,border=f'{pt(.5)} '+('dashed' if node.get('data-historical-border-style')=='dashed' else 'solid')+' currentColor',padding=em(.6),margin_top=gap(7),margin_bottom=gap(7),position='relative')
        if node.has_attr('data-historical-frame-width'):
            add_style(node,width=f'{float(node["data-historical-frame-width"])*100}%',margin_left=em(float(node['data-historical-frame-inset'])))
        if node.has_attr('data-historical-labeled-frame'):
            label=soup.new_tag('span',attrs={'data-native-frame-label':node['data-historical-labeled-frame']});label.string=node['data-historical-labeled-frame']
        else:
            label=node.find_previous_sibling()
            if label is None or label.name!='p' or Projection({'html':str(label)}).text.strip() not in list('ABCD'):label=None
        if label is not None:
            row=soup.new_tag('div',attrs={'class':'old-labeled-frame'});node.insert_before(row)
            row.append(label.extract());row.append(node.extract())
            add_style(row,display='grid',grid_template_columns=em(1.6)+' minmax(0,1fr)',align_items='start',margin_top=gap(8),margin_bottom=gap(7))
            add_style(label,text_indent='0',margin='0',padding_top=pt(6),white_space='nowrap')
            add_style(node,margin='0')
            if node.get('data-historical-frame-role')=='alternative':
                add_style(node,border_width=pt(.4),padding=f'{pt(3)} {pt(8)}')
                for p in node.find_all('p',recursive=False):add_style(p,text_indent='0')
    for node in soup.select('[data-historical-order-flow="vertical"]'):
        add_style(node,text_align='center',margin='0')
        for p in node.find_all('p',recursive=False):add_style(p,text_indent='0',margin='0',line_height='1.25')
        frame=node.find_previous_sibling()
        if (frame is not None and frame.get('data-historical-frame-role')=='passage'
                and node.get('data-historical-compact-sequence')=='true'):
            first=node.find('p',recursive=False)
            if first is None or Projection({'html':str(first)}).text.strip()!='⬇':raise ValueError('Connected sequence lost its first arrow')
            # Preserve the arrow once for assistive/copy text. Its visible ink
            # is attached to the frame border, independent of following gaps.
            first['class']=[*first.get('class',[]),'source-literal','sr-only']
            svg=BeautifulSoup('<svg class="old-connected-arrow visual-only" aria-hidden="true" focusable="false" viewBox="0 0 8 10"><path d="M2 0H6V5.8H8L4 10L0 5.8H2Z" fill="currentColor"/></svg>','html.parser').svg
            add_style(frame,margin_bottom=pt(13),border_width=pt(.9),padding=f'{pt(6)} {pt(8)}')
            add_style(svg,position='absolute',top='100%',left='50%',transform='translateX(-50%)',width=pt(8),height=pt(10),overflow='visible')
            frame.append(svg)
            add_class(node,'old-connected-sequence')
            add_style(node,margin_top='0',margin_bottom=gap(6))
    for node in soup.select('[data-historical-continuation-slot]'):
        add_style(node,margin_top=gap(7),margin_bottom=gap(7))
        blank=node.select_one('[data-historical-framed-blank]')
        if blank:add_style(blank,border=f'{pt(.5)} solid currentColor',min_height=em(float(node.get('data-historical-slot-bottom',2))),display='grid',place_items='center',text_indent='0')
    for node in soup.select('[data-historical-bracket-label]'):
        add_style(node,position='relative',margin_left=em(2),padding_left=em(.5),border_left=f'{pt(.5)} solid currentColor')
        label=soup.new_tag('span',attrs={'class':'visual-only','aria-hidden':'true'});label.string=node['data-historical-bracket-label'];add_style(label,position='absolute',left=em(-2),top='0');node.insert(0,label)
    for node in soup.select('[data-historical-table-chart]'):
        add_style(node,display='grid',grid_template_columns='minmax(0,1fr) minmax(0,1fr)',column_gap='2%',align_items='start')
        for child in node.find_all(recursive=False):add_style(child,min_width='0')
    for node in soup.select('[data-historical-figure-pair]'):
        add_style(node,width=f'{float(node["data-historical-figure-width"])*100}%',margin_left='auto',margin_right='auto',border='0')
        for cell in node.select('td,th'):add_style(cell,border='0',text_align='center')
    for node in soup.select('[data-historical-note-group]'):
        width=float(node['data-historical-note-image-width']);ps=node.find_all('p',recursive=False)
        figure=ps[-1];figure.extract();left=soup.new_tag('div')
        for p in list(node.contents):left.append(p.extract())
        node.append(left);node.append(figure)
        add_style(node,display='grid',grid_template_columns=f'{float(node.get("data-historical-note-left-width",.98-width))*100}% {width*100}%',gap='2%',align_items='center')
        for im in figure.select('.source-image'):add_style(im,width='100%')
    for node in soup.select('[data-historical-illustrated-notes]'):
        children=node.find_all('p',recursive=False)
        if len(children)==2:add_style(node,display='grid',grid_template_columns='1fr 1fr',gap='2%')
        for im in node.select('.source-image'):add_style(im,width=f'{float(node.get("data-historical-note-image-fraction",.5))*100}%',margin_left='auto',margin_right='auto')
    for node in soup.select('[data-historical-glossary-triplet]'):
        notes=node.find_all('p',recursive=False)
        if len(notes)!=3:raise ValueError('Compact glossary lost its three notes')
        figure=next((im for im in notes[1].select('.source-image')
                     if not any('source-literal' in p.get('class',[]) for p in im.parents)),None)
        if figure is None:raise ValueError('Compact glossary lost its original illustration')
        add_class(node,'old-glossary-triplet')
        add_style(node,font_size=f'calc(var(--glyph-point) * {m["style"]["note_pt"]})',line_height=pt(m['style']['note_baseline_pt']))
        # Retain DOM/source order 3,4,5; the grid places 3 and 5 at left.
        add_style(notes[0],grid_column='1',grid_row='1')
        add_style(notes[2],grid_column='1',grid_row='2')
        add_style(notes[1],grid_column='2',grid_row='1 / span 2',display='grid',grid_template_columns='minmax(max-content,34%) minmax(0,42%)',column_gap='2%',align_items='start')
        prefix=soup.new_tag('span',attrs={'class':'old-glossary-caption'})
        figure.extract()
        for child in list(notes[1].contents):prefix.append(child.extract())
        notes[1].append(prefix);notes[1].append(figure)
        add_style(prefix,display='block',text_indent='0',padding_top='1.8em',white_space='nowrap',text_align='left')
        add_style(figure,width='100%',margin='0')
    for node in soup.select('[data-historical-after-label-illustration]'):
        p=node.p;add_style(p,display='flex',gap=em(float(node['data-historical-note-label-width'])),align_items='start')
        for im in p.select('.source-image'):add_style(im,width=f'{float(node["data-historical-note-image-width"])*100}%',margin='0')
    wrapped=meta.get('historical_wrapped_illustration')
    if wrapped:
        from historical_wrapped_illustration import detach
        detach(item['content'],wrapped,m['unit'])
        image=soup.select_one('[data-source-sha256="'+wrapped['image_sha256']+'"]')
        panel=image.find_parent('p');image.extract();panel.decompose()
        add_style(image,float='right',width=f'{wrapped["width_fraction"]*100}%',margin_left=em(wrapped['gap_em']),margin_top='0',margin_bottom='0')
        soup.insert(0,image)
    frame=meta.get('historical_document_frame')
    if frame:document_frame(soup,m,item,frame)
    example=meta.get('historical_example_frame')
    if example:
        node=soup.select_one('[data-historical-framed-document="single"]');label=node.find_previous_sibling();query=node.find_next_sibling()
        row=soup.new_tag('div',attrs={'class':'old-framed-example'});label.insert_before(row);row.append(label.extract());row.append(node.extract())
        add_style(row,display='grid',grid_template_columns=em(example['label_width_em'])+' minmax(0,1fr)',align_items='start')
        add_style(label,text_indent='0',margin='0');add_style(node,margin='0',border=f'{pt(example["rule_pt"])} solid currentColor',padding=f'{pt(example["padding_y_pt"])} {pt(example["padding_x_pt"])}')
        add_style(query,margin_left=em(example['question_indent_em']))


def group_figures(markup,m):
    from historical_html import state
    old=state(m)
    if not old or not old['side_figures'][0]:return markup
    soup=BeautifulSoup(markup,'html.parser')
    for iid,spec in old['side_figures'][0].items():
        figure=soup.find(id=iid)
        if figure is None:continue
        question=soup.find(id=spec['question_id'])
        if question is None:raise ValueError('Bound figure question is absent from its section')
        row=soup.new_tag('div',attrs={'class':'source-figure-question','data-context':iid})
        figure.insert_before(row);row.append(figure.extract());row.append(question.extract())
        left=spec['left_width_fraction'];gap=spec['gap_fraction']
        add_style(row,display='grid',grid_template_columns=f'{left*100}% minmax(0,1fr)',column_gap=f'{gap*100}%',align_items='start')
        add_style(question,margin_top='0')
    return str(soup)


def document_frame(soup,m,item,spec):
    from presentation import source_binding
    if digest(item['content'])!=spec['content_sha256']:raise ValueError('Stale historical document frame')
    source_binding(m['unit'],spec['evidence'])
    frame=soup.select_one('.source-native-frame,[data-historical-framed-document="single"],.notice-frame')
    if frame is None and spec['kind']=='label_beside_box':
        p=soup.find('p');label=p.find('span',recursive=False)if p else None
        if label is None or Projection({'html':label.decode_contents()}).text!=spec['label']:raise ValueError('Labeled notice lost its exact source label')
        label.extract();frame=soup.new_tag('div',attrs={'class':'notice-frame'})
        for node in list(soup.contents):frame.append(node.extract())
        soup.append(label);soup.append(frame)
    if frame is None:raise ValueError('Bound Old frame has no source rectangle')
    add_style(frame,position='relative',border=f'{pt(spec["rule_pt"])} solid currentColor',padding=f'{pt(spec.get("top_padding_pt",spec["padding_pt"]))} {pt(spec["padding_pt"])} {pt(spec.get("bottom_padding_pt",spec["padding_pt"]))}',font_family='Heading' if spec['font_role']=='instruction' else 'Body')
    if 'width_fraction' in spec:add_style(frame,width=f'{spec["width_fraction"]*100}%',margin_left='auto',margin_right='auto')
    if 'before_pt' in spec:add_style(frame,margin_top=gap(spec['before_pt']))
    if spec['kind']=='label_beside_box':
        add_style(frame,display='inline-block',vertical_align='top')
        lead=frame.find_previous_sibling()
        if lead:add_style(lead,display='inline-block',width=em(spec['label_width_em']),vertical_align='top',text_indent='0')
        return
    width=spec.get('fold_width_pt',33);height=spec.get('fold_height_pt',21)
    fold=BeautifulSoup(f'<svg viewBox="0 0 {width} {height}" class="visual-only old-fold" aria-hidden="true"><path d="M 0 {height} Q {width*.75} {height*.6} {width} 0 L {width} {height} Z" fill="var(--paper)" stroke="currentColor" stroke-width="{spec["rule_pt"]}"/></svg>','html.parser').svg
    add_style(fold,position='absolute',right=pt(-spec['rule_pt']),bottom=pt(-spec['rule_pt']),width=pt(width),height=pt(height));frame.append(fold)
    if spec['kind']=='pinned_folded_corner':
        for x,y in [('left','top'),('right','top'),('left','bottom')]:
            pin=soup.new_tag('span',attrs={'class':'visual-only','aria-hidden':'true'});add_style(pin,position='absolute',width=pt(5),height=pt(5),border_radius='50%',background='currentColor',**{x:pt(5),y:pt(5)});frame.append(pin)


def vertical(soup,m,item,meta):
    """Use native semantic columns, with local scrolling and live ruby."""
    from tex_html import render_inline
    from presentation import source_binding
    spec=meta.get('historical_vertical_letter')
    if spec:
        from historical_vertical_letter import parts
        label,columns=parts(item['content'],spec);source_binding(m['unit'],spec['evidence'])
        soup.clear();lead=soup.new_tag('p');lead.string=label;add_class(lead,'passage-label');soup.append(lead)
        frame=soup.new_tag('div',attrs={'class':'old-ruled-letter'})
        size=spec['body_pt'];pitch=spec['column_pitch_em'];extent=spec['extent_em'];pad=spec['padding_em']
        add_style(frame,display='flex',flex_direction='row-reverse',width=em(len(columns)*pitch+2*pad),height=em(extent+2*pad),padding=em(pad),border=f'{pt(.6)} solid currentColor',font_size=f'calc(var(--glyph-point) * {size})',**{'--nominal-em':pt(size),'--word-space-em':spec['word_space_em']})
        for j,column in enumerate(columns):
            node=soup.new_tag('div',attrs={'data-letter-role':column['role']});node.append(BeautifulSoup(render_inline(column['content'],m),'html.parser'))
            indent=1.5 if column['role']=='date' else 1 if column['role']=='body' and column['paragraph_start'] else 0
            add_style(node,writing_mode='vertical-rl',width=em(pitch),flex_shrink='0',height='100%',line_height=em(pitch),text_indent=em(indent),white_space='nowrap',border_left=f'{pt(.3)} solid currentColor' if j<len(columns)-1 else '0')
            if column['role']=='sender':add_style(node,text_align='right',padding_bottom=em(1))
            frame.append(node)
        outer=soup.new_tag('div',attrs={'class':'vertical-scroll','tabindex':'0','role':'region','aria-label':'Ruled vertical letter'});outer.append(frame);soup.append(outer)
        return
    from frame_html import vertical as regular_vertical
    if meta.get('historical_vertical_inset'):
        spec=meta['historical_vertical_inset'];source_binding(m['unit'],spec['evidence'])
        from historical_complex import vertical_parts
        vertical_parts(item['content'],spec)
        label=soup.select_one('[data-outer-passage-label]');body=soup.select_one('[data-vertical-passage-body]');inset=soup.select_one('[data-vertical-inset-figure]');trailer=soup.select_one('[data-horizontal-passage-trailer]')
        add_class(label,'passage-label');g=spec['geometry'];size=m['style'].get('vertical_body_pt',m['style']['body_pt'])
        frame=soup.new_tag('div',attrs={'class':'vertical-frame old-vertical-inset'});body.insert_before(frame);frame.append(body.extract());frame.append(inset.extract())
        add_style(frame,position='relative',writing_mode='vertical-rl',height=em(g['extent_em']),font_size=f'calc(var(--glyph-point) * {size})',line_height=em(g['column_pitch_em']),padding=em(.25),border=f'{pt(.4)} solid currentColor',**{'--nominal-em':pt(size)})
        # The inset is a real flow exclusion occupying the bottom of the first
        # source-bound columns; the exterior citation/notes remain horizontal.
        add_style(body,display='contents')
        exclusion=soup.new_tag('span',attrs={'class':'visual-only vertical-inset-exclusion','aria-hidden':'true'})
        add_style(exclusion,float='right',width=em(g['column_pitch_em']*g['inset_columns']),height=em(g['inset_height_em']),shape_outside='inset(0) content-box',margin_top=em(g['extent_em']-g['inset_height_em']))
        body.insert(0,exclusion)
        add_style(inset,position='absolute',right=em(.25),bottom=em(.25),width=em((g['inset_columns']-.6)*g['column_pitch_em']),height=em(g['inset_height_em']),writing_mode='horizontal-tb',display='grid',place_items='end center')
        for image in inset.select('.source-image'):add_style(image,width='100%',height='auto',margin='0')
        outer=soup.new_tag('div',attrs={'class':'vertical-scroll','tabindex':'0','role':'region','aria-label':'Vertical passage with diagram'});frame.wrap(outer)
        for p in body.find_all('p',recursive=False):add_style(p,margin='0',text_indent=em(1))
        add_style(trailer,margin_top=gap(8),writing_mode='horizontal-tb')
        notes=trailer.find_all('p',recursive=False)
        if len(notes)>1:add_style(notes[1],margin_top=gap(spec.get('citation_to_notes_pt',0)))
        return
    else:local=m['style']
    regular_vertical(soup,item['content'],meta,local)
