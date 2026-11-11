"""Source-bound notice typography, decoration and native content regions."""
import copy,hashlib,math,re
from pathlib import Path
from bs4 import BeautifulSoup,Tag
from model import digest,Projection
from presentation_slice import slice_inline
from notice_layout import meaningful,notice_nodes,html_lines,split_notice_pages,split_nested_contact,panel_heading
from semantic_html import add_style,add_class,pt,gap,reject_unknown
from document_html import select_line,rule_style,bound_lines


def artifact(m,spec):
    root=Path(__file__).resolve().parents[2]/'pdf-render/schema'/m['unit'][:2]
    path=(root/spec['path']).resolve()
    if not path.is_relative_to(root.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest()!=spec['sha256']:raise ValueError('Missing or stale notice artwork')
    if spec['role']!='decorative' or not 0<spec['width_fraction']<.6:raise ValueError('Unsupported notice artwork')
    return path,'assets/illustrations/'+spec['sha256'][:20]+path.suffix.lower()


def fragment(soup,raw,cls=''):
    node=soup.new_tag('span',attrs={'class':cls} if cls else {})
    if raw:node.append(BeautifulSoup(raw,'html.parser'))
    return node


def ribbon(node,spec,size,padding):
    edge=spec['edge']
    if edge not in ('left','right'):raise ValueError('Invalid attached ribbon edge')
    add_class(node,'attached-ribbon');node['data-edge']=edge
    over=spec.get('inner_overhang_pt',size*1.4)
    node['style']+=f'--ribbon-rule:{pt(spec["thickness_pt"])};--ribbon-gray:{(1-spec["gray"])*100}%;--ribbon-gap:{pt(spec["gap_pt"])};--ribbon-overhang:{pt(over)};--ribbon-outset:{pt(padding)};'


def line_style(soup,node,s):
    reject_unknown(s,'text font_family before_pt after_pt align font_pt baseline_pt hanging_prefix bold label_column first_indent_em hanging_em indent_em break_before split_lines line_indents_em angular_delimiters period_spacing document_bullet box width_fraction marker boxed_label indent_like_prefix line_breaks_before inline_list box_padding_pt box_indent_em offset_x_pt label label_width_em label_font_family numeric_padding_em time_columns time_columns_align time_column_sep_pt time_letterspace time_label_gap_em','notice line')
    for token in s.get('line_breaks_before',[]):
        raw='<br/>'.join(bound_lines(node.decode_contents(),token));node.clear();node.append(BeautifulSoup(raw,'html.parser'))
    if s.get('inline_list'):
        raw=node.decode_contents();text=Projection({'html':raw}).text;markers=s['inline_list']['markers']
        positions=[text.index(t) if text.count(t)==1 else -1 for t in markers]
        if not positions or positions!=sorted(set(positions)) or text[:positions[0]].strip():raise ValueError('Inline list lost its ordered markers')
        node.clear()
        for index,(a,b) in enumerate(zip(positions,positions[1:]+[len(text)])):
            part=fragment(soup,slice_inline(raw,a,b));add_style(part,display='inline-block',white_space='nowrap',margin_right='calc(var(--nominal-em) * .8)' if index<len(positions)-1 else '0');node.append(part)
    add_style(node,margin_top=gap(s.get('before_pt',0)),margin_bottom=gap(s.get('after_pt',0)),text_align=s.get('align','left'))
    if 'offset_x_pt' in s:add_style(node,margin_left=pt(s['offset_x_pt']),margin_right=pt(-s['offset_x_pt']))
    if 'font_family' in s:add_style(node,font_family={'body':'Body','notice_body':'Body','heading':'NoticeHeading','notice_heading':'NoticeHeading','notice_label':'NoticeLabel'}[s['font_family']])
    if s.get('bold'):add_style(node,font_family='BodyBold,Body,serif')
    if 'font_pt' in s:add_style(node,font_size=f'calc(var(--glyph-point) * {s["font_pt"]})')
    if 'baseline_pt' in s:add_style(node,line_height=f'calc(var(--point) * {s["baseline_pt"]} * var(--line-preset) * var(--line-adjust))')
    indent=s.get('indent_em',0);hang=s.get('hanging_em',1 if s.get('hanging_prefix') or s.get('document_bullet') else 0)
    add_style(node,padding_left=f'calc(var(--nominal-em) * {indent+hang})',text_indent=f'calc(var(--nominal-em) * {s.get("first_indent_em",-hang)})')
    if s.get('label_width_em'):
        raw=node.decode_contents();text=Projection({'html':raw}).text;a=len(text)-len(text.lstrip());end=a+len(s['label'])
        if text[a:end]!=s['label']:raise ValueError('Stale notice distributed label')
        label=fragment(soup,'');body=fragment(soup,slice_inline(raw,end,len(text)))
        for char in s['label']:
            part=soup.new_tag('span');part.string=char;label.append(part)
        add_style(label,display='inline-flex',justify_content='space-between',width=f'calc(var(--nominal-em) * {s["label_width_em"]-.7})',margin_right='calc(var(--nominal-em) * .7)',font_family='NoticeLabel' if s.get('label_font_family')=='notice_label' else 'Body')
        if 'numeric_padding_em' in s:
            padding=s['numeric_padding_em']
            if not 0<=padding<=.4:raise ValueError('Invalid notice numeric padding')
            for text_node in list(body.find_all(string=True)):
                if text_node.parent.name in ('rt','rp'):continue
                parts=[]
                for token in re.split(r'([0-9]+)',str(text_node)):
                    if token.isascii() and token.isdigit():
                        number=soup.new_tag('span');number.string=token;add_style(number,margin_inline=f'calc(var(--nominal-em) * {padding})');parts.append(number)
                    elif token:parts.append(token)
                text_node.replace_with(*parts)
        node.clear();node.append(label);node.append(body)
    if s.get('time_columns'):
        text=Projection({'html':node.decode_contents()}).text
        pairs=re.findall(r'([①②③④⑤⑥])\s*([0-9]{1,2}:[0-9]{2}～[0-9]{1,2}:[0-9]{2})',text)
        if [a for a,b in pairs]!=['①','④','②','⑤','③','⑥'] or re.sub(r'\s','',text)!=''.join(a+b for a,b in pairs):raise ValueError('Time columns require six unchanged pairs')
        node.clear();add_style(node,display='grid',grid_template_columns='repeat(2,minmax(0,1fr))',column_gap=pt(2*s.get('time_column_sep_pt',5)),row_gap=pt(2),text_indent='0')
        for label,value in pairs:
            cell=soup.new_tag('span');a=soup.new_tag('span');a.string=label;v=soup.new_tag('span');v.string=value
            add_style(a,margin_right=f'calc(var(--nominal-em) * {s.get("time_label_gap_em",.3)})');add_style(v,letter_spacing=f'{s.get("time_letterspace",0)/100}em')
            cell.extend([a,v]);add_style(cell,white_space='nowrap',text_align=s.get('time_columns_align','left'));node.append(cell)
    if s.get('label_column'):
        spec=s['label_column'];raw=node.decode_contents();text=Projection({'html':raw}).text;a=len(text)-len(text.lstrip());b=a+len(spec['label'])
        if text[a:b]!=spec['label']:raise ValueError('Stale notice label column')
        lead=fragment(soup,slice_inline(raw,a,b));body=fragment(soup,slice_inline(raw,b,len(text)))
        node.clear();node.append(lead);node.append(body);add_class(node,'notice-label-row')
        add_style(node,grid_template_columns=f'calc(var(--nominal-em) * {spec["width_em"]}) minmax(0,1fr)',text_indent='0')
        add_style(lead,text_align=spec.get('align','left'),padding_right=f'calc(var(--nominal-em) * {spec.get("gap_em",.5)})')
    if s.get('split_lines') or s.get('break_before'):
        chunks=bound_lines(node.decode_contents(),s.get('break_before'));indents=s.get('line_indents_em',[0]*len(chunks))
        if len(chunks)!=len(indents):raise ValueError('Notice line indent count changed')
        node.clear()
        for raw,inset in zip(chunks,indents):
            p=soup.new_tag('div');p.append(BeautifulSoup(raw,'html.parser'));add_style(p,padding_left=f'calc(var(--nominal-em) * {inset})');node.append(p)
    if s.get('box'):
        add_style(node,border=f'{pt(.45)} solid currentColor',padding=f'{pt(s.get("box_padding_pt",3))} {pt(8)}',width=f'{s.get("width_fraction",1)*100}%',box_sizing='border-box',margin_left=f'calc(var(--nominal-em) * {s["box_indent_em"]})' if 'box_indent_em' in s else 'auto',margin_right='auto')
    if s.get('angular_delimiters'):
        # Keep the exact canonical glyphs while exposing their TeX display form.
        for node_text in list(node.find_all(string=True)):
            if node_text.parent.name in ('rt','rp'):continue
            pieces=re.split('([〈〉])',str(node_text))
            if len(pieces)>1:
                out=[]
                for token in pieces:
                    if token not in ('〈','〉'):out.append(token);continue
                    atom=soup.new_tag('span');hidden=soup.new_tag('span',attrs={'class':'source-literal sr-only'});hidden.string=token;atom.append(hidden)
                    visual=soup.new_tag('span',attrs={'class':'visual-only','aria-hidden':'true'});visual.string='<' if token=='〈' else '>';atom.append(visual);out.append(atom)
                node_text.replace_with(*out)
    if s.get('period_spacing'):
        for latin in node.select('.tex-latin'):add_style(latin,letter_spacing='.03em')
    if s.get('boxed_label') or s.get('marker') or s.get('document_bullet'):
        raw=node.decode_contents();text=Projection({'html':raw}).text;a=len(text)-len(text.lstrip());token=s.get('boxed_label',s.get('marker',{}).get('character','●'))
        if not text[a:].startswith(token):raise ValueError('Stale bound label/marker')
        label=fragment(soup,slice_inline(raw,a,a+len(token)))
        if s.get('boxed_label'):add_style(label,border=f'{pt(.4)} solid currentColor',padding=pt(1))
        elif s.get('marker'):
            if s['marker']!={'character':'▶','kind':'notched_arrowhead'}:raise ValueError('Unsupported notched marker')
            add_class(label,'notice-notched-marker')
        else:
            from document_bullets import DEFAULTS
            dims=DEFAULTS[s['document_bullet']]
            add_style(label,display='inline-block',font_size=f'{dims["scale"]}em',vertical_align=f'{dims["raise_em"]}em',margin_right=f'{dims["gap_em"]/dims["scale"]}em')
            add_style(node,padding_left=f'calc(var(--nominal-em) * {s.get("indent_em",0)+dims["scale"]+dims["gap_em"]})',text_indent=f'calc(var(--nominal-em) * {-dims["scale"]-dims["gap_em"]})')
        node.clear();node.append(label)
        if a+len(token)<len(text):node.append(BeautifulSoup(slice_inline(raw,a+len(token),len(text)),'html.parser'))
    if s.get('indent_like_prefix'):
        body=fragment(soup,node.decode_contents());node.clear()
        measure=soup.new_tag('span',attrs={'class':'visual-only indent-measure','aria-hidden':'true'});measure.string=s['indent_like_prefix']
        node.append(measure);node.append(body);add_style(node,display='grid',grid_template_columns='max-content minmax(0,1fr)',text_indent='0')


def present(soup,source,style,m):
    if digest(source)!=style['content_sha256']:raise ValueError('Stale notice content binding')
    reject_unknown(style,'content_sha256 body_pt baseline_pt word_space_em paragraph_skip_pt frame_padding_pt title contact asset indent_hierarchy body_width_fraction intro_word_space_em table_word_space_em wave_separators intro_align emphasis_terms flow_lines content_selector line_styles intro_line_count intro_bold frame_top_pt frame_bottom_pt inset_panels frame_rule list_indent_em latin_role ruby_intergap_em intro_break_before collapse_paragraph_boundaries page_frame page_segments segments_same_page page_flow colon_fields table_row_breaks list_continuations','notice')
    if 'table_row_breaks' in style:
        tables=soup.find_all('table');boundaries=style['table_row_breaks']
        if len(tables)!=1:raise ValueError('Table continuation needs one table')
        rows=tables[0].find_all('tr')
        if boundaries!=sorted(set(boundaries)) or not all(type(n)is int and 0<n<len(rows) for n in boundaries):raise ValueError('Invalid table continuation rows')
        for index,row in enumerate(rows):
            for cell in row.find_all(['td','th'],recursive=False):
                if any(index<n<index+int(cell.get('rowspan',1)) for n in boundaries):raise ValueError('Table continuation splits a spanning cell')
        # Native continuation changes only physical pagination. Keep one table.
        tables[0]['data-source-page-break-rows']=','.join(map(str,boundaries))
    if style.get('page_segments'):
        # Retain the explicitly partitioned documents, omit only physical page breaks.
        parts=split_notice_pages({'html':str(soup)},style);soup.clear()
        for value,segment in parts:
            child=copy.deepcopy(style)
            for k in ('page_segments','segments_same_page','content_selector'):child.pop(k,None)
            child.update(segment);child.pop('start_text');child['content_sha256']=digest(value)
            inner=BeautifulSoup(value['html'],'html.parser');present(inner,value,child,m)
            region=soup.new_tag('div',attrs={'class':'notice-segment notice-frame'});region.append(inner)
            frame_geometry(region,child,m)
            if soup.contents:add_style(region,margin_top=gap(6 if style.get('segments_same_page') else 2*style['baseline_pt']))
            soup.append(region)
        return
    title=style['title'];contact=style['contact']
    reject_unknown(title,'selector node_count line_sizes_pt before_pt after_pt leading_ratio structured_lines line_font_families line_alignments line_before_pt attached_bar line_slants shape arch_rise_pt arch_sweep_degrees box_width_fraction box_padding_pt box_radius_pt break_before plain_prefix','notice title')
    reject_unknown(contact,'selector flow before_pt align marker break_before office_after_pt segments baseline_pt raise_pt rule_before_pt telephone phone_dash_scale email_phone_separator_width_em','notice contact')
    nodes=meaningful(notice_nodes({'html':str(soup)},style))
    if len(nodes)==1 and isinstance(nodes[0],Tag) and nodes[0].name=='section':nodes=meaningful(list(nodes[0].contents))
    if title['selector'] not in ('leading_nodes','leading_region','none'):raise ValueError('Unsupported title selector')
    native=meaningful(notice_nodes(source,style))
    if len(native)==1 and isinstance(native[0],Tag) and native[0].name=='section':native=meaningful(list(native[0].contents))
    if title['selector']=='none':title_raw=''
    elif title['selector']=='leading_nodes':title_raw=''.join(map(str,native[:title['node_count']]))
    elif isinstance(native[0],Tag) and native[0].name in ('center','p','h1','h2','h3'):title_raw=native[0].decode_contents()
    else:
        selected=[]
        while native and not (isinstance(native[0],Tag) and native[0].name in ('p','div','table')):selected.append(native.pop(0))
        title_raw=''.join(map(str,selected))
    expected=title.get('plain_prefix',Projection({'html':title_raw}).text.strip())
    wanted=''.join(expected.split());taken=[];count=0;accum=''
    while wanted and accum!=wanted:
        if not nodes:raise ValueError('Missing bound notice title')
        node=nodes.pop(0);raw=node.decode_contents() if isinstance(node,Tag) else str(node);text=Projection({'html':raw}).text
        compact=''.join(text.split());remaining=wanted[len(accum):]
        if remaining.startswith(compact):taken.append(raw);accum+=compact;count+=1
        elif compact.startswith(remaining):
            chars=0;end=0
            for end,ch in enumerate(text,1):
                if not ch.isspace():chars+=1
                if chars==len(remaining):break
            taken.append(slice_inline(raw,0,end));rest=soup.new_tag('p');rest.append(BeautifulSoup(slice_inline(raw,end,len(text)),'html.parser'));nodes.insert(0,rest);accum=wanted;count+=1
        else:raise ValueError('Notice title source selection changed')
    raws=bound_lines('<br>'.join(taken),title.get('break_before'))
    if len(raws)!=len(title['line_sizes_pt']):raise ValueError('Notice title line count changed')
    tail=[]
    if contact['selector']=='last_paragraph':tail=[nodes.pop()]
    elif contact['selector']=='marker_suffix':
        hits=[i for i,n in enumerate(nodes) if Projection({'html':str(n)}).text.strip()==contact['marker']]
        if len(hits)!=1:raise ValueError('Notice contact marker must select one complete node')
        tail=nodes[hits[0]:];nodes=nodes[:hits[0]]
    elif contact['selector']=='last_panel_suffix':nodes,tail=split_nested_contact(nodes,contact['marker'])
    elif contact['selector']!='none':raise ValueError('Unsupported contact selector')
    soup.clear();heading=None
    if count:
        heading=soup.new_tag('div',attrs={'class':'notice-title-lines'})
        add_style(heading,margin_top=gap(title.get('before_pt',0)),margin_bottom=gap(title.get('after_pt',0)))
        families=title.get('line_font_families',['heading']*len(raws));aligns=title.get('line_alignments',['center']*len(raws));slants=title.get('line_slants',[0]*len(raws));gaps=title.get('line_before_pt',[0]*len(raws))
        if not all(len(v)==len(raws) for v in [families,aligns,slants,gaps]):raise ValueError('Notice title roles changed line count')
        for i,(raw,size,family,align,slant,before) in enumerate(zip(raws,title['line_sizes_pt'],families,aligns,slants,gaps)):
            line=soup.new_tag('div',attrs={'class':'notice-title-line'});line.append(BeautifulSoup(raw,'html.parser'))
            # TeX's baseline pitch uses nominal points, independently of the
            # glyph scale applied by the bound Japanese font.
            add_style(line,font_size=f'calc(var(--glyph-point) * {size})',line_height=f'calc(var(--point) * {size*title.get("leading_ratio",1.3):g} * var(--line-preset) * var(--line-adjust))',font_family={'body':'Body','heading':'NoticeHeading','notice_heading':'NoticeHeading'}[family],text_align=align,margin_top=gap(before))
            if slant:add_style(line,transform=f'skewX({-math.degrees(math.atan(slant))}deg)')
            if title.get('attached_bar',{}).get('line_index')==i:ribbon(line,title['attached_bar'],size,style['frame_padding_pt'])
            heading.append(line)
        if title.get('shape')=='arch':
            text=expected.strip()
            if len(raws)!=1 or '<ruby' in raws[0] or not 3<=len(text)<=30:raise ValueError('Invalid arched title')
            line=heading.find('div');line.clear();add_style(line,padding_top=pt(title['arch_rise_pt']))
            for i,ch in enumerate(text):
                t=2*i/(len(text)-1)-1;glyph=soup.new_tag('span');glyph.string=ch
                angle=t*title['arch_sweep_degrees']/2
                width=(f'calc(var(--point) * {title["line_sizes_pt"][0]*style.get("word_space_em",0)})' if ch.isspace() else f'{math.cos(math.radians(angle))+.88*abs(math.sin(math.radians(angle))):.6f}em')
                add_style(glyph,display='inline-block',width=width,white_space='pre',transform=f'translateY(calc(var(--point) * {-title["arch_rise_pt"]*(1-t*t)})) rotate({angle}deg)');line.append(glyph)
        elif title.get('shape') in ('box','opposite_round_box'):
            add_style(heading,border=f'{pt(.45)} solid currentColor',width=f'{title.get("box_width_fraction",.8)*100}%',padding=pt(title.get('box_padding_pt',2)),margin_left='auto',margin_right='auto')
            if title['shape']=='opposite_round_box':add_style(heading,border_radius=f'{pt(title.get("box_radius_pt",6))} 0')
        elif title.get('shape'):raise ValueError('Unsupported title shape')
        soup.append(heading)
    body=soup.new_tag('div',attrs={'class':'notice-body'})
    for node in nodes:body.append(node)
    soup.append(body)
    for continuation in style.get('list_continuations',[]):
        hits=[n for n in body.find_all('li') if Projection({'html':str(n)}).text.strip()==continuation['text']]
        if len(hits)!=1:raise ValueError('List continuation needs one exact list item')
        node=hits[0];chunks=bound_lines(node.decode_contents());prefix=continuation['prefix']
        if len(chunks)!=2 or not Projection({'html':chunks[0]}).text.startswith(prefix):raise ValueError('List continuation lost its two lines or prefix')
        node.clear();node.append(BeautifulSoup(chunks[0],'html.parser'))
        row=soup.new_tag('div');measure=fragment(soup,slice_inline(chunks[0],0,len(prefix)),'visual-only');measure['aria-hidden']='true';add_style(measure,visibility='hidden')
        row.append(measure);row.append(BeautifulSoup(chunks[1],'html.parser'));node.append(row)
    if style.get('intro_align'):
        first=body.find(['p','center'],recursive=False)
        if not first:raise ValueError('Missing notice introduction')
        add_style(first,text_align=style['intro_align'])
    if style.get('indent_hierarchy'):
        for node in body.find_all(['p','div'],recursive=False):
            text=Projection({'html':str(node)}).text.strip();inset=0 if re.match(r'^[A-Z][.．]',text) else .8 if text.startswith(('【','<','〈','①','②','③','④')) else 1.8
            add_style(node,padding_left=f'calc(var(--nominal-em) * {inset})')
    for binding in style.get('line_styles',[]):
        # Native notice line bindings select whole top-level nodes. A repeated
        # panel title is a different scope and must not make this ambiguous.
        direct=[n for n in body.find_all(recursive=False) if Projection({'html':str(n)}).text.strip()==binding['text']]
        line_style(soup,direct[0] if len(direct)==1 else select_line(body,binding['text']),binding)
    for emphasis in style.get('emphasis_terms',[]):
        text=emphasis['text'];candidates=[n for n in body.find_all(['p','div','h3','h4']) if not n.find(['p','div','h3','h4','table']) and Projection({'html':str(n)}).text.count(text)==1]
        if len(candidates)!=1:raise ValueError('Emphasis needs one exact body term')
        node=candidates[0];raw=node.decode_contents();plain=Projection({'html':raw}).text;at=plain.index(text);end=at+len(text)
        token=fragment(soup,slice_inline(raw,at,end));add_style(token,font_family='BodyBold,Body,serif',font_size=f'calc(var(--glyph-point) * {emphasis["font_pt"]})',margin_left=f'{emphasis.get("before_em",0)}em',margin_right=f'{emphasis.get("after_em",0)}em')
        node.clear()
        if at:node.append(BeautifulSoup(slice_inline(raw,0,at),'html.parser'))
        node.append(token)
        if end<len(plain):node.append(BeautifulSoup(slice_inline(raw,end,len(plain)),'html.parser'))
    if style.get('inset_panels'):
        panels=style['inset_panels']
        # These explicit source gaps must not collapse across panel siblings
        # or through the body into the preceding title's after-space.
        add_class(body,'notice-inset-flow')
        selector=panels.get('selector','table_divs')
        selected=body.select(':scope > [data-notice-inset-panel]') if selector=='flow_ranges' else [n for n in body.find_all('div',recursive=False) if n.find('table')] if selector=='table_divs' else [
                  n for n in body.find_all('div',recursive=False) if n.has_attr('data-native-frame') or selector=='titled_divs']
        if len(selected)!=len(panels['titles']):raise ValueError('Inset panel count differs from source')
        for panel_index,(panel,title_text) in enumerate(zip(selected,panels['titles'])):
            if panel_heading(panel)!=title_text:raise ValueError('Inset panel ordered title differs from source')
            if selector=='titled_divs':
                from section_layout import flow_lines
                children=flow_lines(list(panel.children));panel.clear()
                for child in children:panel.append(child)
            add_style(panel,border=f'{pt(.45)} solid currentColor',border_radius=pt(panels['radius_pt']),padding=pt(panels['padding_pt']),margin_top=gap(panels.get('gap_pt',4)),margin_bottom=gap(panels.get('gap_pt',4)))
            if 'title_font_pt' in panels:
                title_node=next((n for n in panel.children if isinstance(n,Tag)),None)
                if title_node is None or Projection({'html':str(title_node)}).text.strip().splitlines()[0]!=title_text:raise ValueError('Inset title must start with its exact bound heading')
                size=panels['title_font_pt']
                add_style(title_node,font_size=f'calc(var(--glyph-point) * {size})',line_height=f'calc(var(--point) * {size*1.5:g} * var(--line-preset) * var(--line-adjust))',text_align=panels.get('title_align','center'),margin_bottom=gap(4))
                if 'title_rule_pt' in panels:add_style(title_node,border_bottom=f'{pt(panels["title_rule_pt"])} solid currentColor')
            for binding in panels.get('line_styles',[[] for _ in selected])[panel_index]:
                line_style(soup,select_line(panel,binding['text']),binding)
    if style.get('colon_fields'):
        fields=style['colon_fields'];region=soup.new_tag('div',attrs={'class':'notice-colon-fields'})
        add_style(region,width=f'{fields.get("width_fraction",.94)*100}%',margin=f'{gap(fields.get("before_pt",12))} auto {gap(fields.get("after_pt",12))}')
        for i,row in enumerate(fields['rows']):
            node=select_line(body,row['text']);raw=node.decode_contents();text=Projection({'html':raw}).text;match=re.fullmatch(r'\s*(.+?)([:：])\s*(\S.*?)\s*',text,re.S)
            if not match or match[1]!=row['label']:raise ValueError('Stale colon field')
            if i==0:node.insert_before(region)
            grid=soup.new_tag('div',attrs={'class':'document-metadata-row'});add_style(grid,grid_template_columns=f'calc(var(--nominal-em) * {fields.get("label_width_em",3)}) .6em minmax(0,1fr)')
            for j in [1,2,3]:grid.append(fragment(soup,slice_inline(raw,match.start(j),match.end(j))))
            if row.get('range_display'):
                if match[3]!='18:00~20:00' or row['range_display']!='18:00～20:00':raise ValueError('Unsupported range display')
                cell=grid.find_all('span',recursive=False)[-1];add_class(cell,'source-range-display')
                for child in list(cell.contents):
                    hidden=soup.new_tag('span',attrs={'class':'source-literal sr-only'});hidden.append(child.extract());cell.append(hidden)
                show=soup.new_tag('span',attrs={'class':'visual-only','aria-hidden':'true'});show.string=row['range_display'];cell.append(show)
            region.append(grid);node.decompose()
    contact_node=None
    if tail:
        contact_node=soup.new_tag('div',attrs={'class':'notice-contact'})
        add_style(contact_node,margin_top=gap(contact.get('before_pt',0)),text_align=contact.get('align','right'))
        raw=''.join(map(str,tail));lines=bound_lines(raw,contact.get('break_before'))
        if contact['flow']=='postal_two_lines':
            if not Projection({'html':lines[-1]}).text.startswith('〒'):raise ValueError('Postal contact lacks address')
            lines=[' '.join(lines[:-1]),lines[-1]]
        elif contact['flow']=='join_last_two_lines':
            if len(lines)<3 or not Projection({'html':lines[-2]}).text.strip().startswith('電話') or not Projection({'html':lines[-1]}).text.strip().startswith('ホームページ'):raise ValueError('Joined contact needs terminal phone and website lines')
            lines=lines[:-2]+[lines[-2]+'<span class="notice-contact-gap"> </span>'+lines[-1]]
        elif contact['flow']!='preserve':raise ValueError('Unsupported contact flow')
        for raw in lines:
            p=soup.new_tag('p');p.append(BeautifulSoup(raw,'html.parser'));contact_node.append(p)
        if contact.get('baseline_pt'):add_style(contact_node,line_height=f'calc(var(--point) * {contact["baseline_pt"]} * var(--line-preset) * var(--line-adjust))')
        if contact.get('rule_before_pt'):add_style(contact_node,border_top=f'{pt(contact["rule_before_pt"])} solid currentColor',padding_top=pt(5))
        if contact.get('telephone'):
            phone=contact['telephone'];candidates=[n for n in contact_node.find_all(string=True) if phone in str(n)]
            if len(candidates)!=1 or str(candidates[0]).count(phone)!=1:raise ValueError('Exact telephone presentation changed')
            text=str(candidates[0]);a=text.index(phone);parts=[text[:a]]
            for index,piece in enumerate(phone.split('-')):
                if index:
                    dash=fragment(soup,'-');scale=contact['phone_dash_scale'];add_style(dash,display='inline-block',transform=f'scaleX({scale})',transform_origin='left',margin_right=f'{(scale-1)*.33}em');parts.append(dash)
                parts.append(piece)
            parts.append(text[a+len(phone):]);candidates[0].replace_with(*parts)
        if 'email_phone_separator_width_em' in contact:
            candidates=[n for n in contact_node.find_all(string=True) if '/' in str(n)]
            if len(candidates)!=1 or str(candidates[0]).count('/')!=1:raise ValueError('Contact separator changed')
            before,after=str(candidates[0]).split('/');separator=fragment(soup,'/');add_style(separator,display='inline-block',width=f'calc(var(--nominal-em) * {contact["email_phone_separator_width_em"]})',text_align='center');candidates[0].replace_with(before,separator,after)
        if 'office_after_pt' in contact:
            rows=contact_node.find_all('p',recursive=False)
            if len(rows)!=2:raise ValueError('Office clearance requires two contact rows')
            add_style(rows[0],margin_bottom=gap(contact['office_after_pt']))
        if contact.get('segments'):
            # Each segment has a bound source span; use inline cells with the
            # source PDF's measured advances, allowing a narrow screen to wrap.
            for spec in contact['segments']:
                candidates=[p for p in contact_node.find_all('p') if Projection({'html':str(p)}).text.count(spec['text'])==1]
                if len(candidates)!=1:raise ValueError('Contact segment missing')
                p=candidates[0];raw=p.decode_contents();text=Projection({'html':raw}).text;a=text.index(spec['text']);b=a+len(spec['text']);p.clear()
                if a:p.append(BeautifulSoup(slice_inline(raw,0,a),'html.parser'))
                span=fragment(soup,slice_inline(raw,a,b));add_style(span,display='inline-block',margin_left=f'{spec.get("gap_before_em",0)}em',white_space='nowrap');p.append(span)
                if 'width_bp' in spec:add_style(span,width=pt(spec['width_bp']*72.27/72))
                for latin in span.select('.tex-latin'):add_style(latin,letter_spacing=f'{spec.get("ascii_letterspace",0)/100}em')
                if b<len(text):p.append(BeautifulSoup(slice_inline(raw,b,len(text)),'html.parser'))
        soup.append(contact_node)
    if style.get('wave_separators'):
        tables=body.find_all('table')
        if len(tables)!=1:raise ValueError('Wave bands require one table')
        table=tables[0];target=table.parent if table.parent.name=='div' else table
        for where in ('before','after'):
            rule=soup.new_tag('div',attrs={'class':'notice-wave','aria-hidden':'true'});getattr(target,'insert_'+where)(rule)
        body.append(soup.new_tag('div',attrs={'class':'notice-wave','aria-hidden':'true'}))
    if style.get('asset'):
        spec=style['asset'];_,path=artifact(m,spec);image=soup.new_tag('img',src='../'+path,alt='',attrs={'class':'notice-art','aria-hidden':'true'})
        add_style(image,width=f'{spec["width_fraction"]*100}%',height='auto',object_fit='contain')
        placement=spec['placement']
        if placement=='contact_left':
            if contact_node is None:raise ValueError('Contact artwork needs a contact')
            wrap=soup.new_tag('div',attrs={'class':'notice-art-row'});contact_node.wrap(wrap);wrap.insert(0,image);add_style(contact_node,flex='1',min_width='0')
            add_style(image,margin_left=pt(spec.get('left_inset_pt',0)))
            if contact.get('raise_pt'):add_style(contact_node,transform=f'translateY({pt(-contact["raise_pt"])})')
        elif placement=='intro_right':
            selected=list(body.find_all(recursive=False))[:style.get('intro_line_count',1)]
            if not selected:raise ValueError('Intro artwork needs text')
            wrap=soup.new_tag('div',attrs={'class':'notice-art-row'});selected[0].insert_before(wrap);text=soup.new_tag('div');add_style(text,flex='1',min_width='0')
            for n in selected:text.append(n.extract())
            if style.get('intro_bold'):add_style(text,font_family='Heading')
            if style.get('intro_break_before'):
                chunks=bound_lines(text.decode_contents(),style['intro_break_before']);text.clear();text.append(BeautifulSoup('<br>'.join(chunks),'html.parser'))
            text['style']+='--word-space-em:'+str(style.get('intro_word_space_em',style.get('word_space_em',0)))+';';wrap.append(text);wrap.append(image);add_style(image,margin_top=pt(-spec.get('raise_pt',0)))
        elif placement in ('title_left','title_right'):
            if heading is None:raise ValueError('Title artwork needs title')
            add_style(heading,position='relative');add_style(image,position='absolute',top=pt(spec.get('raise_pt',0)),**{placement.split('_')[1]:pt(spec.get('left_inset_pt' if placement=='title_left' else 'right_inset_pt',0))});heading.append(image)
        elif placement=='table_right':
            table=body.find_all('table')[spec['table_index']];wrap=soup.new_tag('div',attrs={'class':'notice-art-row'});table.wrap(wrap)
            table['data-art-width']=str(spec['table_width_fraction']);wrap.append(image)
        else:raise ValueError('Unsupported artwork placement')
    if style.get('body_width_fraction',1)!=1:
        outer=soup.new_tag('div',attrs={'class':'notice-inner'});nodes=list(soup.contents)
        for n in nodes:outer.append(n.extract())
        add_style(outer,width=f'{style["body_width_fraction"]*100}%',margin='auto');soup.append(outer)
    # RichTeX normalizes consecutive NoticeLine tokens to one Para. Preserve
    # the semantic paragraph gap instead of a full blank line per captured br.
    for br in list(soup.find_all('br')):
        if br.parent is None or br.find_parent('table'):continue
        rest=[];node=br.next_sibling
        while node is not None and (getattr(node,'name',None)=='br' or not getattr(node,'name',None) and not str(node).strip()):
            rest.append(node);node=node.next_sibling
        if not any(getattr(n,'name',None)=='br' for n in rest):continue
        br.name='span';add_class(br,'notice-paragraph-break')
        for n in rest:n.extract()


def frame_geometry(frame,style,m):
    """Retain source width, rule and padding while omitting physical page whitespace."""
    from table_html import rule_css
    add_style(frame,border=rule_css(style.get('frame_rule',{'style':'single','width_pt':.45})),
              padding=pt(style.get('frame_padding_pt',12)),
              padding_top=pt(style.get('frame_top_pt',style.get('frame_padding_pt',12))),
              padding_bottom=pt(style.get('frame_bottom_pt',style.get('frame_padding_pt',12))))
    for edge in {'left','right','top','bottom'}-set(style.get('frame_rule',{}).get('edges',['left','right','top','bottom'])):
        add_style(frame,**{'border_'+edge:'0'})
    if style.get('page_frame'):
        from registered_notice import render
        render('',style) # Validate the same bounded A4 dimensions as the TeX emitter.
        f=style['page_frame'];left=m['style']['margins_mm']['left']*72/25.4
        add_style(frame,width=pt(f['width_bp']*72.27/72),max_width='none',box_sizing='border-box',
                  margin_left=pt((f['x_bp']-left)*72.27/72),border_width=pt(f['rule_bp']*72.27/72))
        frame['data-page-frame-policy']='source-width-and-rule; continuous-height'
    if 'ruby_intergap_em' in style:frame['style']+='--ruby-intergap:calc(var(--nominal-em) * '+str(style['ruby_intergap_em'])+');'
    if style.get('latin_role'):
        if style['latin_role']!='document':raise ValueError('Unsupported notice Latin role')
        add_class(frame,'document-latin')
