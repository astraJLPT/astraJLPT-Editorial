"""Shared HTML consumer for the PDF renderer's authored document sections."""
from bs4 import BeautifulSoup
from model import digest, Projection
from section_layout import prepare_sections
from semantic_html import reject_unknown, add_style, add_class, pt, gap


def prepare(value, source, spec):
    if digest(source) != spec['content_sha256']:
        raise ValueError('Stale semantic section binding')
    return prepare_sections(value, spec)


def present(soup, spec, style, *, native_glyph_scale=1):
    reject_unknown(spec, 'content_sha256 evidence selector section_count intro_text intro_line_count frame_style padding_pt paragraph_indent_em title_placement title_align title_after_pt before_pt after_pt line_styles last_paragraph_author author_before_pt author_after_pt author_latin_role frame_top_pt frame_bottom_pt frame_rule frame_rule_pt first_paragraph_indent_em lead_gap_pt following_question_gap_pt width_fraction font_role body_pt baseline_pt typography_family pins fold_size_pdf_pt ruby_intergap_em ruby_base_height_em ruby_size_ratio unbordered_composition_divs unwrap_existing_frame split_paragraph_lines flow_lines paragraph_break_before external_title number_box_labels label_value_list metadata_rows list_layout', 'semantic section')
    sections = soup.select('section.reading-passage')
    if len(sections) != spec['section_count']:
        raise ValueError('Semantic section count changed')
    for section in sections:
        section.name = 'div'
        add_class(section, 'document-section')
        frame = spec['frame_style']
        if frame not in ('box', 'cloze', 'folded_corner', 'pinned_corners'):
            raise ValueError('Unsupported semantic frame: ' + frame)
        add_class(section, 'section-' + frame)
        pad = spec.get('padding_pt', 12)
        rule = spec.get('frame_rule', {'style':'single','width_pt':spec.get('frame_rule_pt', style.get('cloze_frame_rule_pt',.6) if frame=='cloze' else .45)})
        reject_unknown(rule, 'style width_pt edges double_gap_pt', 'section frame rule')
        if rule['style'] not in ('single', 'none', 'double'):
            raise ValueError('Unsupported section frame rule')
        add_style(section, padding_left=pt(8 if frame=='cloze' else pad), padding_right=pt(8 if frame=='cloze' else pad),
                  padding_top=pt(spec.get('frame_top_pt',20 if frame=='cloze' else pad)),
                  padding_bottom=pt(spec.get('frame_bottom_pt',8 if frame=='cloze' else pad)),
                  margin_top=gap(spec.get('before_pt',0)), margin_bottom=gap(spec.get('after_pt',0)),
                  border_width=pt(rule.get('width_pt',.45)), border_style='solid' if rule['style']=='single' else rule['style'])
        if 'edges' in rule:
            for edge in ('top','bottom','left','right'):
                if edge not in rule['edges']: add_style(section, **{'border_'+edge+'_width':'0'})
        if frame=='cloze':add_class(section,'cloze-frame')
        if 'width_fraction' in spec:add_style(section, width=f'{spec["width_fraction"]*100}%', margin_left='auto', margin_right='auto')
        if 'body_pt' in spec:
            add_style(section,font_size=f'calc(var(--glyph-point) * {spec["body_pt"]})',line_height=f'max(1.5em,calc(var(--point) * {spec["baseline_pt"]} * var(--line-preset) * var(--line-adjust)))')
            section['style']+='--nominal-em:'+pt(spec['body_pt'])+';'
        if spec.get('font_role','body')!='body':
            roles={'memo':'Memo','letter':'Letter'}
            if spec['font_role'] not in roles:raise ValueError('Unsupported document font role')
            role=style['font_roles'][spec['font_role']];scale=role.get('scale',1)
            add_style(section,font_family=roles[spec['font_role']]+',Body,serif',
                      font_size=f'calc(var(--glyph-point) * {spec.get("body_pt",style["body_pt"])})',
                      font_feature_settings=','.join('"'+f+'"' for f in role.get('features',[])) or 'normal',
                      **{'--glyph-scale':scale,'--glyph-point':f'calc(var(--point) * {scale})'})
        for p in section.find_all('p',recursive=False):add_style(p,text_indent=f'calc(var(--nominal-em) * {spec.get("paragraph_indent_em",1)})')
        lines = spec.get('line_styles',[])
        for line in lines:
            reject_unknown(line,'text align font_pt baseline_pt before_pt after_pt font_family right_inset_em indent_em letter_space_em line_sizes_pt native_down_arrow rule_after_pt attached_bar slant label_column inset_frame','section line')
            from document_html import select_line
            node=select_line(section,line['text']);add_class(node,'section-styled-line')
            if line.get('label_column'):
                from notice_html import line_style
                line_style(soup,node,line)
                continue
            if line.get('inset_frame'):
                panel=line['inset_frame'];add_style(node,border=f'{pt(.45)} solid currentColor',border_radius=pt(panel['radius_pt']),padding=pt(panel['padding_pt']))
            add_style(node,text_align=line.get('align','left'),text_indent=pt(0),margin_top=gap(line.get('before_pt',0)),margin_bottom=gap(line.get('after_pt',0)))
            if 'font_pt'in line:add_style(node,font_size=f'calc(var(--glyph-point) * {line["font_pt"]})')
            if 'baseline_pt'in line:add_style(node,line_height=f'max(1.5em,calc(var(--point) * {line["baseline_pt"]} * var(--line-preset) * var(--line-adjust)))')
            if 'font_family'in line:
                add_style(node,font_family={'heading':'Heading','body':'Body','notice_heading':'NoticeHeading'}[line['font_family']])
                node['data-document-font-override']=line['font_family']
                if spec.get('font_role')=='memo' and line['font_family']=='heading':
                    # This native line selects the main \gtfamily, whose face
                    # is already bundled as NoticeHeading, not the separately
                    # bound instruction face. Restore the measured JA scale.
                    heading=style['font_roles']['notice_heading']
                    if heading.get('source')!='heading' and heading.get('path')!=style['fonts']['heading']:
                        raise ValueError('Memo heading needs the bound main sans face')
                    add_style(node,font_family='NoticeHeading',font_feature_settings='normal',
                              **{'--glyph-scale':native_glyph_scale,'--glyph-point':f'calc(var(--point) * {native_glyph_scale})'})
            if 'right_inset_em'in line:add_style(node,padding_right=f'calc(var(--nominal-em) * {line["right_inset_em"]})')
            if 'indent_em'in line:add_style(node,padding_left=f'calc(var(--nominal-em) * {line["indent_em"]})')
            if 'letter_space_em'in line:add_style(node,letter_spacing=f'calc(var(--nominal-em) * {line["letter_space_em"]})')
            if 'rule_after_pt'in line:add_style(node,border_bottom=f'{pt(line["rule_after_pt"])} solid currentColor')
            if line.get('attached_bar') and 'line_sizes_pt' not in line:
                from notice_html import ribbon
                ribbon(node,line['attached_bar'],line['font_pt'],pad)
            if line.get('slant'):
                import math
                add_style(node,transform=f'skewX({-math.degrees(math.atan(line["slant"]))}deg)')
            if 'line_sizes_pt'in line:
                from notice_layout import html_lines
                chunks=html_lines(node.decode_contents())
                if len(chunks)!=len(line['line_sizes_pt']):raise ValueError('Section line size count changed')
                node.clear()
                for index,(chunk,size) in enumerate(zip(chunks,line['line_sizes_pt'])):
                    part=soup.new_tag('div');part.append(BeautifulSoup(chunk,'html.parser'))
                    add_style(part,font_size=f'calc(var(--glyph-point) * {size})');node.append(part)
                    if line.get('attached_bar') and index==line['attached_bar'].get('line_index',0):
                        from notice_html import ribbon
                        ribbon(part,line['attached_bar'],size,pad)
                    if line.get('native_down_arrow',{}).get('line')==index:
                        arrow=line['native_down_arrow']
                        if Projection({'html':chunk}).text.strip()!='↓':raise ValueError('Native arrow needs its exact source glyph')
                        add_class(part,'native-arrow');part['style']+='--arrow-width:'+pt(arrow['width_pt'])+';--arrow-height:'+pt(arrow['height_pt'])+';'
                        part['style']+='--arrow-shaft:'+str(arrow['shaft_width_pt']/arrow['width_pt']*50)+'%;--arrow-head-start:'+str((1-arrow['head_height_pt']/arrow['height_pt'])*100)+'%;'
        if spec.get('metadata_rows'):
            from section_metadata import collect
            from notice_layout import meaningful
            from document_html import metadata_html
            children=meaningful(list(section.contents));binding=spec['metadata_rows']
            for index,row in collect(children,binding,spec.get('line_styles',[])).items():
                node=children[index];raw=node.decode_contents();node.name='div';node.clear()
                node.append(BeautifulSoup(metadata_html([raw],[row],binding['label_width_em']),'html.parser'))
                add_style(node,margin_top=gap(row.get('before_pt',0)),margin_bottom=gap(row.get('after_pt',0)))
        if spec.get('list_layout'):
            from section_lists import render
            from semantic_html import converter
            roots=section.find_all('ul',recursive=False)
            if len(roots)!=1:raise ValueError('Section list needs one root')
            binding=spec['list_layout'];render(converter(),roots[0],'body',binding)
            def lists(node,depth):
                level=binding['levels'][depth]
                add_style(node,padding_left=f'calc(var(--nominal-em) * {level["indent_em"]})',margin='0',list_style_type='"・"')
                for item in node.find_all('li',recursive=False):
                    add_style(item,margin_top=gap(level['item_before_pt']),padding_left='calc(var(--nominal-em) * .2)')
                    for child in item.find_all('ul',recursive=False):lists(child,depth+1)
            lists(roots[0],0)
        if spec.get('label_value_list'):
            from label_values import collect
            from notice_layout import meaningful
            children=meaningful(list(section.contents));indexes,pairs=collect(children,spec['label_value_list']);binding=spec['label_value_list']
            region=soup.new_tag('div',attrs={'class':'label-value-list'})
            add_style(region,margin_top=gap(binding.get('before_pt',0)),margin_bottom=gap(binding.get('after_pt',0)),margin_left=f'calc(var(--nominal-em) * {binding.get("indent_em",0)})',grid_template_columns='max-content minmax(0,1fr)',column_gap=f'{binding.get("gap_em",.5)}em')
            children[indexes[0]].insert_before(region)
            for label,raw in pairs:
                term=soup.new_tag('span');term.string=label;region.append(term)
                value=soup.new_tag('div');value.append(BeautifulSoup(raw,'html.parser'));region.append(value)
            for index in indexes:children[index].decompose()
        for node in section.select('.passage-author'):
            add_style(node,text_align='right',text_indent='0',margin_top=gap(spec.get('author_before_pt',0)),margin_bottom=gap(spec.get('author_after_pt',0)))
        first=section.find('p',recursive=False)
        if 'first_paragraph_indent_em'in spec:
            first=next((p for p in section.find_all('p',recursive=False) if 'section-styled-line' not in p.get('class',[])),None)
            if not first:raise ValueError('Missing first paragraph indent target')
            add_style(first,text_indent=f'calc(var(--nominal-em) * {spec["first_paragraph_indent_em"]})')
        title=section.find(['h3','h4'],recursive=False)
        if title and spec.get('title_placement')!='preserve':
            add_style(title,text_align=spec.get('title_align','center'),font_size='inherit',margin_top='0',margin_bottom=gap(spec.get('title_after_pt',8)))
            if spec.get('title_placement')=='before_frame':section.insert_before(title.extract())
        if first and spec.get('lead_gap_pt') and not lines:add_style(first,margin_bottom=gap(spec['lead_gap_pt']))
        if frame=='pinned_corners':
            from frame_html import pins
            pins(soup,section,spec['pins'])
        if frame=='folded_corner':
            from memo_html import folded_corner
            fold=spec.get('fold_size_pdf_pt',{'width':33,'height':21})
            add_style(section,**{'--memo-bottom-padding':pt(spec.get('frame_bottom_pt',pad))})
            folded_corner(soup,section,fold['width'],fold['height'],rule.get('width_pt',.45))
        if 'ruby_size_ratio'in spec:section['style']+='--ruby-size:'+str(spec['ruby_size_ratio'])+'em;'
        if spec.get('font_role')=='memo':
            from document_font_html import memo_font
            memo_font(soup,section,style,spec.get('body_pt',style['body_pt']))
