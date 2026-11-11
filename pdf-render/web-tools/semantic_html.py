"""Consume the same authored semantic layout as the TeX renderer.

No question IDs or exam text are layout selectors. Source validators and balanced
inline slicing come from pdf-render; unsupported new bindings fail the web build
instead of quietly reverting to an ordinary paragraph.
"""
import hashlib
import math
import re
from pathlib import Path
from bs4 import BeautifulSoup, Tag
from model import Projection, digest
from richtex import RichTeX
import dialogue
import structured_documents
from example_layout import prepare as prepare_example
from presentation_slice import slice_inline
from notice_layout import html_lines, notice_nodes, meaningful
from paired_passages import parameters as paired_parameters
from table_roles import alignment as table_alignment
from tex_html import prepare_bound_inline, render_inline, source_html


def reject_unknown(spec, allowed, role):
    missing = set(spec) - set(allowed.split())
    if missing:
        raise ValueError(f'HTML adapter needs {role} support for: {", ".join(sorted(missing))}')


def projection_binding(value, binding, role):
    if hashlib.sha256(Projection(value).text.encode()).hexdigest() != binding['projection_sha256']:
        raise ValueError('Stale ' + role + ' projection')


def converter():
    return RichTeX(Path(__file__).resolve().parents[1] / 'work/assets')


def pt(value):
    return f'calc(var(--point) * {value})'


def gap(value):
    return f'calc(var(--point) * {value} * var(--block-preset) * var(--block-adjust))'


def add_style(node, **properties):
    existing=node.get('style','').rstrip()
    node['style'] = existing + (';' if existing and not existing.endswith(';') else '') + ''.join(k.replace('_', '-') + ':' + str(v) + ';' for k, v in properties.items())


def add_class(node, name):
    node['class'] = [*node.get('class', []), name]


def render_dialogue(value, m, binding, target, *, scene_lines=(), named_colon=False):
    # The PDF's validator owns the source hash, speaker identity, turn order and
    # authored continuation rules. It does not write a PDF or alter the model.
    reject_unknown(binding, 'projection_sha256 turns state basis speaker_align split_before continuation_lines evidence single_speaker', 'dialogue')
    conv=converter();conv.word_space_em=m['style'].get('word_space_em',0)
    from historical_html import enabled
    conv.source_target_markers=enabled(m)
    conv.historical_embedded_query=m['style'].get('historical_typography',{}).get('embedded_query')
    conv.historical_citation_metrics=m['style'].get('historical_typography',{}).get('citation')
    dialogue.render(conv, value, binding, scene_lines=scene_lines, named_colon=named_colon)
    prepared = prepare_bound_inline(value, m, 'question', target)
    raw_lines = dialogue.lines(prepared, binding.get('split_before'),preserve_underlined_blanks=enabled(m),preserve_historical_word_gaps=enabled(m))
    turns = {row['line']: row for row in binding['turns']}
    continuations = {row['line']: row['turn_line'] for row in binding.get('continuation_lines', [])}
    result = []
    for index, raw in enumerate(raw_lines):
        if index in continuations:
            continue
        if index not in turns:
            result.append(f'<div class="dialogue-scene" data-source-line="{index}">{render_inline({"html": raw}, m, "question")}</div>')
            continue
        text = Projection({'html': raw}).text
        qa = re.match(r'^\s*([QAＱＡ][:：])', text)
        at = qa.end() if qa and turns[index]['speaker'] == qa[1] else (re.match(r'^\s*'+re.escape(turns[index]['speaker']),text).end() if named_colon else min(i for i, c in enumerate(text) if c in '「｢'))
        speaker = slice_inline(raw, 0, at)
        utterance = slice_inline(raw, at, len(text))
        # LuaTeX-ja's opening quote has half an em of leading sidebearing.
        # Its ink extends left of the half-width cell, unlike a browser's full
        # Japanese character box. Keep that source glyph and align its cell.
        if text[at] == '「':
            utterance = '<span class="dialogue-quote">' + slice_inline(raw, at, at + 1) + '</span>' + (slice_inline(raw, at + 1, len(text)) if at + 1 < len(text) else '')
        if continuations.get(index + 1) == index:
            utterance += raw_lines[index + 1]
        from label_separators import prepare as prepare_labels
        speaker_value,_=prepare_labels({'html':speaker.strip()},presentation=False,source_context={'html':raw})
        result.append(f'<div class="dialogue-turn" data-source-line="{index}">'
                      f'<div class="dialogue-speaker">{render_inline(speaker_value, m, "option")}</div>'
                      f'<div class="dialogue-utterance">{render_inline({"html": utterance}, m, "question")}</div></div>')
    align = binding.get('speaker_align', 'center')
    return f'<div class="dialogue" data-speaker-align="{align}">{"".join(result)}</div>'


def structured_html(value, m, binding, original=None):
    reject_unknown(binding, 'genre content_sha256 evidence groups split_before', 'structured document')
    conv=converter();conv.word_space_em=m['style'].get('word_space_em',0)
    structured_documents.render(conv, value if original is None else original, binding)
    lines = structured_documents.lines(value, binding.get('split_before'))
    out = []; cursor = 0
    for group in binding['groups']:
        reject_unknown(group, 'role lines before_pt after_pt align indent_em join rows label_width_em marker instruction_inset_em rule_after rule_after_gap_pt', 'document group')
        role = group['role']; count = len(group['lines']); fragments = lines[cursor:cursor + count]; cursor += count
        if role == 'prefix':
            out.extend('<p>' + fragment + '</p>' for fragment in fragments)
            continue
        if role == 'metadata':
            from document_html import metadata_html,rule_style
            region=BeautifulSoup('<div class="document-group document-metadata" data-document-group="metadata"></div>','html.parser').div
            region.append(BeautifulSoup(metadata_html(fragments,group['rows'],group.get('label_width_em',5)),'html.parser'))
            add_style(region,margin_top=gap(group.get('before_pt',0)),margin_bottom=gap(group.get('after_pt',0)))
            if 'rule_after' in group:
                rule_style(region,group['rule_after']);add_style(region,padding_bottom=gap(group.get('after_pt',0)),margin_bottom=gap(group.get('rule_after_gap_pt',8)))
            out.append(str(region));continue
        if role == 'instruction':
            raw=fragments[0];text=Projection({'html':raw}).text;at=text.index(group['marker'])
            out.append('<div class="document-group document-instruction" data-document-group="instruction" style="'+f'margin-top:{gap(group.get("before_pt",0))};margin-bottom:{gap(group.get("after_pt",0))};margin-left:calc(var(--nominal-em) * {group.get("instruction_inset_em",0)})'+'"><span>'+slice_inline(raw,at,at+1)+'</span><span>'+slice_inline(raw,at+1,len(text))+'</span></div>');continue
        if binding['genre']=='email' and role in ('body','greeting','closing'):
            from email_family import prepare_padding
            fragments=[source_html(prepare_padding({'html':raw})[0]) for raw in fragments]
        align = group.get('align', {'title': 'center', 'sender': 'right', 'date': 'right', 'closing': 'right'}.get(role, 'left'))
        indent = group.get('indent_em', 0 if binding['genre'] == 'email' or role != 'body' else 1)
        separator = '<br>' if group.get('join', 'hard') == 'hard' else ' '
        css = f'text-align:{align};text-indent:calc(var(--nominal-em) * {indent});margin-top:{gap(group.get("before_pt", 0))};margin-bottom:{gap(group.get("after_pt", 0))}'
        out.append(f'<p class="document-group" data-document-group="{role}" style="{css}">{separator.join(fragments)}</p>')
    return {'html': ''.join(out)}


def prepare_semantic_value(value, m, meta, target, original=None):
    if meta.get('structured_document'):
        value = structured_html(value, m, meta['structured_document'],original)
    if meta.get('example_layout'):
        value = prepare_example(value, meta['example_layout'])
    if meta.get('historical_reading_dialogue'):
        return value
    # Plain fields promoted to rich content by frozen ruby still have real
    # newline paragraph boundaries. CSS whitespace collapse must not erase them.
    raw = source_html(value)
    if not BeautifulSoup(raw,'html.parser').find(['p','div','table','section','h3','h4']):
        raw=raw.replace('\n','<br>')
    from section_layout import flow_lines
    return {'html': ''.join(str(n) for n in flow_lines(list(BeautifulSoup(raw,'html.parser').contents)))}


def mark_introduction(soup, source, meta, style):
    binding = meta.get('introduction')
    if not binding:
        return
    reject_unknown(binding, 'projection_sha256 text role state basis evidence allow_inline_label following_prefix following_context', 'introduction')
    projection_binding(source, binding, 'introduction')
    # Native annotation preparation moves a validated marker into metadata.
    # Match the same introduction after that presentation-only transformation.
    binding=dict(binding)
    for note in soup.select('[data-note-label]'):
        term=Projection({'html':str(note)}).text
        literal=term+note['data-note-label']
        if literal in binding['text']:
            binding['text']=binding['text'].replace(literal,term,1)
    roots=meaningful(list(soup.contents))
    if len(roots)==1 and isinstance(roots[0],Tag) and roots[0].name=='div' and roots[0].find('section'):
        roots[0].unwrap()
        from section_layout import flow_lines
        children=flow_lines(list(soup.contents));soup.clear()
        for child in children:soup.append(child)
    for node in list(soup.find_all('p',recursive=False)):
        chunks=html_lines(node.decode_contents()) if node.find('br') else []
        if any(Projection({'html':c}).text.strip()==binding['text'] for c in chunks):
            for raw in chunks:
                part=soup.new_tag('p');part.append(BeautifulSoup(raw,'html.parser'))
                if re.fullmatch(r'[（(][0-9０-９]+[）)]',Projection({'html':raw}).text.strip()):add_class(part,'passage-label')
                node.insert_before(part)
            node.decompose()
    if binding.get('allow_inline_label'):
        for p in list(soup.find_all('p',recursive=False)):
            text=Projection({'html':str(p)}).text.strip()
            label=re.match(r'^[（(][0-9０-９]+[）)]\s*',text)
            if label and text[label.end():].startswith(binding['text']):
                raw=p.decode_contents();whole=Projection({'html':raw}).text;at=whole.index(binding['text'])
                lead=soup.new_tag('p',attrs={'class':'passage-label'});lead.append(BeautifulSoup(slice_inline(raw,0,at),'html.parser'))
                p.insert_before(lead);p.clear();p.append(BeautifulSoup(slice_inline(raw,at,len(whole)),'html.parser'))
    if binding.get('following_prefix'):
        continuation=binding['following_prefix']
        for anchor in meta.get('notes',{}).get('inline_anchors',[]):
            if anchor['marker'] in continuation:continuation=continuation.replace(anchor['marker'],'',1)
        compact=lambda text:re.sub(r'\s+','',text)
        hits=[p for p in soup.find_all('p',recursive=False) if Projection({'html':str(p)}).text.strip().startswith(binding['text'])]
        if len(hits)!=1:raise ValueError('Inline introduction must have one exact leading paragraph')
        node=hits[0];raw=node.decode_contents();text=Projection({'html':raw}).text;at=text.index(binding['text'])+len(binding['text'])
        if text[at:].strip():
            if not compact(text[at:]).startswith(compact(continuation)):raise ValueError('Inline introduction continuation changed')
            intro=soup.new_tag('p');intro.append(BeautifulSoup(slice_inline(raw,0,at),'html.parser'));node.insert_before(intro)
            node.clear();node.append(BeautifulSoup(slice_inline(raw,at,len(text)),'html.parser'))
        else:
            following=''.join(map(str,node.next_siblings))
            if not compact(Projection({'html':following}).text).startswith(compact(continuation)):raise ValueError('Inline introduction continuation changed')
    if binding.get('allow_inline_label'):
        for p in list(soup.find_all('p',recursive=False)):
            text=Projection({'html':str(p)}).text.strip()
            label=re.match(r'^[（(][0-9０-９]+[）)]\s*',text)
            if label and text[label.end():]==binding['text']:
                raw=p.decode_contents();whole=Projection({'html':raw}).text;at=whole.index(binding['text'])
                lead=soup.new_tag('p',attrs={'class':'passage-label'});lead.append(BeautifulSoup(slice_inline(raw,0,at),'html.parser'))
                p.insert_before(lead);p.clear();p.append(BeautifulSoup(slice_inline(raw,at,len(whole)),'html.parser'))
    selected = [p for p in soup.find_all(['p', 'h3', 'h4'], recursive=False)
                if Projection({'html': str(p)}).text.strip() == binding['text']]
    if len(selected) != 1:
        raise ValueError('Introduction must select one complete paragraph')
    add_class(selected[0], 'context-intro')
    key = 'document_intro_after_pt' if binding['role'] == 'document' else 'intro_after_pt'
    add_style(selected[0], margin_bottom=gap(style.get(key, 6)))


def wrap_tail(soup, cls):
    """Keep existing lead/label roles outside a document's physical frame."""
    nodes = meaningful(list(soup.contents)); start = 0
    introductions=[index for index,node in enumerate(nodes) if isinstance(node,Tag) and 'context-intro' in node.get('class',[])]
    if introductions:start=max(introductions)+1
    for index, node in enumerate(nodes):
        if index<start:continue
        if isinstance(node, Tag) and set(node.get('class', [])) & {'passage-label', 'context-intro'}:
            start = index + 1
        else:
            break
    if start == len(nodes):
        raise ValueError('Empty document frame')
    if len(nodes[start:])==1 and isinstance(nodes[start],Tag) and nodes[start].has_attr('data-native-frame'):
        frame=nodes[start];frame.name='div';frame['class']=[c for c in frame.get('class',[]) if c!='source-native-frame'];add_class(frame,cls)
        del frame['data-native-frame']
        return frame
    frame = soup.new_tag('div', attrs={'class': cls})
    nodes[start].insert_before(frame)
    for node in nodes[start:]:
        frame.append(node.extract())
    return frame


def paired_frames(soup, style, frame_style='box'):
    cfg = paired_parameters(style.get('paired_passages'))
    for marker in list(soup.select('[data-paired-label]')):
        if marker.name=='span':
            paragraph=marker.parent
            if paragraph.name!='p' or marker.previous_sibling:raise ValueError('Inline paired label lost its leading position')
            label=soup.new_tag('p');label.append(marker.extract());paragraph.insert_before(label)
    nodes = meaningful(list(soup.contents)); labels = []
    for i, node in enumerate(nodes):
        text = Projection({'html': str(node)}).text.strip().translate(str.maketrans('ＡＢ', 'AB'))
        displayed=node.select_one('[data-paired-label-display]') if isinstance(node,Tag) else None
        if displayed:text=displayed['data-paired-label-display']
        if re.fullmatch(r'A|B|\([AB]\)|（[AB]）', text):
            labels.append((i, next(c for c in text if c in 'AB')))
    if labels and [label for _, label in labels] not in [['A'], ['B'], ['A', 'B']]:
        raise ValueError('Ambiguous paired passage labels')
    for k, (start, label) in enumerate(labels or [(-1, 'A')]):
        stop = labels[k + 1][0] if k + 1 < len(labels) else len(nodes)
        if stop <= start + 1:
            raise ValueError('Empty paired passage')
        if start >= 0:
            add_class(nodes[start], 'paired-label')
            add_style(nodes[start], text_align=cfg['label_align'], margin_top=gap(cfg['first_label_before_pt' if label == 'A' else 'next_label_before_pt']), margin_bottom=gap(cfg['label_frame_gap_pt']))
        selected=nodes[start+1:stop]
        citations=[n for n in selected if isinstance(n,Tag) and n.has_attr('data-paired-outside-citation')]
        selected=[n for n in selected if n not in citations]
        if len(selected)==1 and isinstance(selected[0],Tag) and selected[0].has_attr('data-native-frame'):
            original_frame=selected[0]
            if original_frame['data-native-frame']=='rules':frame_style='horizontal_rules'
            selected=list(original_frame.contents)
            original_frame.unwrap()
        frame = soup.new_tag('div', attrs={'class': 'paired-frame', 'data-frame-style': frame_style})
        add_style(frame, padding=f'{pt(cfg["frame_padding_pt"])} {pt(cfg["frame_side_padding_pt"])}', border_width=pt(cfg['rule_pt']))
        selected[0].insert_before(frame)
        for node in selected:
            frame.append(node.extract())
        for citation in citations:add_style(citation,text_align='right',margin_top=gap(4),text_indent='0')
        if frame.find('p', recursive=False):
            add_style(frame.find('p', recursive=False), text_indent=f'calc(var(--nominal-em) * {cfg["first_paragraph_indent_em"]})')


def email_frame(soup, source, style, target, m=None):
    from email_family import headers
    spec = (headers(m) if m else style.get('email_headers', {})).get(target, {})
    reject_unknown(spec, 'content_sha256 evidence paragraph_skip_pt rule_set metadata last_header_line metadata_to_rule_pt rule_to_body_pt spaced_paragraphs first_line_indent_em', 'email header')
    if spec and digest(source) != spec['content_sha256']:
        raise ValueError('Stale email header binding')
    frame = wrap_tail(soup, 'email-frame')
    rules = spec.get('rule_set', {})
    reject_unknown(rules, 'top bottom inner internal terminal_internal_as_bottom before_pt after_pt top_gap_pt bottom_gap_pt', 'email rules')
    for edge in ('top', 'bottom'):
        rule = rules.get(edge, {'width_pt': 2, 'pattern': 'solid'})
        add_style(frame, **{'border_' + edge + '_width': pt(rule['width_pt']), 'border_' + edge + '_style': rule['pattern']})
    add_style(frame, padding_top=pt(rules.get('top_gap_pt', 10)), padding_bottom=pt(rules.get('bottom_gap_pt', 12)),
              margin_top=gap(rules.get('before_pt', 11)), margin_bottom=gap(rules.get('after_pt', 0)))
    for p in frame.find_all('p', recursive=False):
        if not p.has_attr('data-document-group'):
            add_style(p, margin_bottom=gap(spec.get('paragraph_skip_pt', 0)),text_indent=f'calc(var(--nominal-em) * {spec.get("first_line_indent_em",0)})')
    from document_html import email_details
    email_details(frame,source,spec)


def prepare_table_values(value,style,target):
    """Consume exact cell word groups before typography adds presentation spans."""
    soup=BeautifulSoup(source_html(value),'html.parser')
    from inline_layout import prepare_inline
    for index,table in enumerate(soup.find_all('table')):
        spec=style.get('table_styles',{}).get(target,{}).get(str(index),{})
        occupied={}
        for r,row in enumerate([n for n in table.find_all('tr') if n.find_parent('table') is table]):
            col=0
            for cell in row.find_all(['td','th'],recursive=False):
                while occupied.get((r,col)):col+=1
                for entry in spec.get('cell_styles',[]):
                    if (entry['row'],entry['column'])!=(r,col):continue
                    groups=list(entry.get('keep_words',[]))
                    if entry.get('keep_time_ranges'):
                        times=re.findall(r'[0-9０-９]{1,2}[:：][0-9０-９]{2}[～〜\-][0-9０-９]{1,2}[:：][0-9０-９]{2}',Projection({'html':str(cell)}).text)
                        if not times:raise ValueError('Time-range role has no source range')
                        groups.extend(times)
                    if not groups:continue
                    raw={'html':cell.decode_contents()}
                    prepared=prepare_inline(raw,{'content_sha256':digest(raw),'groups':groups})
                    cell.clear();cell.append(BeautifulSoup(prepared['html'],'html.parser'))
                for y in range(r,r+int(cell.get('rowspan',1))):
                    for x in range(col,col+int(cell.get('colspan',1))):occupied[y,x]=True
                col+=int(cell.get('colspan',1))
    return {'html':str(soup)}


def style_table(table, spec, style, context='body'):
    reject_unknown(spec, 'column_weights column_alignments row_sep_pt column_sep_pt rules cell_styles body_pt baseline_pt header_align header_gray before_pt after_pt width_fraction align top_gap_pt vertical_align rule_style stub_align circled_bullet_gap_em column_groups group_gap_fraction diagonal_header cell_flow vertical_cells left_inset_pt row_separations discount_pt date_cells panel_padding_pt panel_title_pt panel_radius_pt panel_gap_pt panel_lines caption_style approved_duration', 'table')
    add_class(table, 'source-table')
    # TeX enumerates semantic rows; captured br tags between rows have no
    # content role. Browsers otherwise foster-parent them above the table.
    for br in list(table.select(':scope > br,thead > br,tbody > br,tfoot > br,tr > br')):br.decompose()
    if context != 'example' and (context != 'notice' or 'baseline_pt' in spec):
        add_style(table, font_size=f'calc(var(--glyph-point) * {spec.get("body_pt", style["table_body_pt"])})',
                  line_height=pt(spec.get('baseline_pt', style['table_baseline_pt'])))
    else:
        add_style(table, font_size='inherit', line_height='inherit')
    rules = spec.get('rules', {})
    reject_unknown(rules, 'default horizontal vertical double_gap_pt', 'table rules')
    if rules or spec.get('rule_style'):
        # Bound cell edges implement the complete native rule system. A
        # captured HTML border attribute would add a second outer frame.
        table.attrs.pop('border',None)
        add_style(table,border='0')
    rule = rules.get('default', {'width_pt': .58, 'style': 'single'})
    if rule['style'] not in ('single','none','double','dashed'):
        raise ValueError('Unsupported HTML table rule')
    rows = [n for n in table.find_all('tr') if n.find_parent('table') is table]; occupied = {}; grid = []; ncols = 0
    for r, row in enumerate(rows):
        col = 0
        for cell in row.find_all(['td', 'th'], recursive=False):
            while occupied.get((r, col)):
                col += 1
            text = Projection({'html': str(cell)}).text.strip()
            bound = [entry for entry in spec.get('cell_styles', []) if entry['row'] == r and entry['column'] == col]
            if len(bound) > 1:
                raise ValueError('Duplicate table cell binding')
            if bound:
                reject_unknown(bound[0], 'row column align text background_gray keep_words keep_time_ranges vertical_align aligned_money amount_width_em aligned_duration line_indents_em break_before line_hanging_em line_font_families line_before_pt body_pt baseline_pt ruby_intergap_em normalize_line_starts line_label_column document_bullet', 'table cell')
                if 'text' in bound[0] and text != bound[0]['text']:
                    raise ValueError('Stale table cell binding')
                if bound[0].get('keep_words') and not cell.select('[data-bounded-word]'):raise ValueError('Unconsumed table word grouping')
            alignments = spec.get('column_alignments', [])
            alignment, _ = table_alignment(cell, text, r, col, spec, alignments[col] if col < len(alignments) else 'left', bound[0] if bound else None)
            add_style(cell, text_align=alignment)
            add_style(cell, padding=f'{pt(spec.get("row_sep_pt", 4))} {pt(spec.get("column_sep_pt", 3))}', border_width=pt(rule.get('width_pt',.58) if rule['style']=='single' else 0))
            gray=bound[0].get('background_gray') if bound else None
            if gray is None and r==0:gray=spec.get('header_gray')
            if gray is not None:
                if not 0<=gray<=1:raise ValueError('Invalid table gray')
                add_style(cell,background=f'color-mix(in srgb,currentColor {(1-gray)*100:.6f}%,var(--paper))')
            grid.append((r, col, cell))
            if bound:
                from table_html import cell_roles
                cell_roles(cell,bound[0])
            for y in range(r, r + int(cell.get('rowspan', 1))):
                for x in range(col, col + int(cell.get('colspan', 1))):
                    occupied[y, x] = True
            col += int(cell.get('colspan', 1))
            ncols = max(ncols, col)
    if any(not any((r, c) == (entry['row'], entry['column']) for r, c, _ in grid) for entry in spec.get('cell_styles', [])):
        raise ValueError('Unused table cell binding')
    if context != 'example':
        # RichTeX uses sqrt(content length), capped at 12, for unbound columns.
        # Reuse that rule instead of allowing a browser's auto table algorithm
        # to squeeze the label column into short vertical fragments.
        weights = [1.0] * ncols
        for _, col, cell in grid:
            if int(cell.get('colspan', 1)) == 1:
                width = max((len(line) for line in Projection({'html': str(cell)}).text.strip().splitlines()), default=1)
                weights[col] = max(weights[col], min(12, math.sqrt(max(1, width))))
        weights = spec.get('column_weights', weights)
        if len(weights) != ncols or any(w <= 0 for w in weights):
            raise ValueError('Table column weights mismatch')
        if 'column_alignments' in spec and len(spec['column_alignments']) != ncols:
            raise ValueError('Table column alignments mismatch')
        # Replace captured presentational columns with the resolved source
        # weights. Keeping both creates phantom empty columns in HTML tables.
        for captured in list(table.find_all(['colgroup','col'],recursive=False)):
            captured.decompose()
        cg = BeautifulSoup('', 'html.parser').new_tag('colgroup'); total = sum(weights)
        for weight in weights:
            col = BeautifulSoup('', 'html.parser').new_tag('col')
            add_style(col,width=f'{weight/total*100:.6f}%')
            cg.append(col)
        if 'column_weights' in spec and not spec.get('column_groups') and spec.get('cell_flow') not in ('contact_list','notice_panels'):
            table['data-column-weights']=','.join(map(str,weights))
        # Intrinsic minimum widths still matter on small screens. The wrapper
        # scrolls if those minima exceed the available width; cells never need
        # a per-paper minimum width or font-size exception.
        table.insert(0, cg); add_style(table, table_layout='fixed' if 'column_weights' in spec and not spec.get('column_groups') else 'auto')
    if 'width_fraction'in spec:add_style(table,width=f'{spec["width_fraction"]*100}%')
    if spec.get('align')=='center':add_style(table,margin_left='auto',margin_right='auto')
    elif spec.get('align')=='right':add_style(table,margin_left='auto')
    from table_html import extra
    extra(table,spec,grid,ncols)


def present_tables(soup, style, target, context='body', worked=False):
    bindings = style.get('table_styles', {}).get(target, {})
    tables = soup.find_all('table')
    if set(bindings) - {str(i) for i in range(len(tables))}:
        raise ValueError('Unused table layout binding: ' + target)
    for index, table in enumerate(tables):
        style_table(table, bindings.get(str(index), {}), style, context)
        if worked and len(table.find_all('tr')) == 2 and all(len(r.find_all('td', recursive=False)) == 6 for r in table.find_all('tr')):
            add_class(table, 'star-worked-table')
        wrap = soup.new_tag('div', attrs={'class': 'table-scroll', 'tabindex': '0', 'role': 'region', 'aria-label': 'Table'})
        table.wrap(wrap)
        spec=bindings.get(str(index),{})
        if 'before_pt'in spec or 'top_gap_pt'in spec:add_style(wrap,margin_top=gap(spec.get('before_pt',spec.get('top_gap_pt',0))))
        elif table.get('data-question-display-owner') and context=='body' and 'caption_style' not in spec:
            add_style(wrap,margin_top=gap(style['question_table_before_pt']))
        if 'after_pt'in spec:add_style(wrap,margin_bottom=gap(spec['after_pt']))
        if 'left_inset_pt'in spec:add_style(wrap,margin_left=pt(spec['left_inset_pt']),width='100%')
        if table.get('data-art-width'):add_style(wrap,width=f'{float(table["data-art-width"])*100}%')


def has_printed_options(value, options):
    """Recognize all four exact source options, independent of vocabulary."""
    if isinstance(value,dict):
        soup=BeautifulSoup(value['html'],'html.parser')
        expected=[Projection(o).text.strip() for o in options]
        for listing in soup.find_all('ol'):
            if listing.find_parent(class_='source-literal') or 'source-literal' in listing.get('class',[]):continue
            if listing.has_attr('reversed') or listing.get('start','1')!='1':continue
            rows=listing.find_all('li',recursive=False)
            if (all(expected) and len(rows)==len(options) and all(r.get('value',str(n))==str(n) for n,r in enumerate(rows,1))
                    and [Projection({'html':str(r)}).text.strip() for r in rows]==expected):return True
    text = Projection(value).text
    pattern = r'\s*'.join(str(n) + r'\s*' + re.escape(Projection(option).text.strip()) for n, option in enumerate(options, 1))
    return bool(re.search(pattern, text))


def audit_layout(m):
    # These decisions are already consumed by the HTML or intentionally omitted
    # for a continuous page (pagination). A new semantic binding needs a consumer.
    allowed = 'writing_mode content_role suppression_basis printed_label dialogue example_variant example_layout introduction notes document_role structured_document document_lines document_fields soft_line_breaks vertical_flow vertical_header vertical_paired_label vertical_frame horizontal_frame option_money_columns paragraph_breaks paired_label_presentation paragraph_indent_ownership paired_structure shared_note_anchors keep_with_previous intake_candidate_exclusions table_captions cloze_panel_headers context_label question_table decision_tree'
    from historical_html import state as old_state
    if old_state(m):
        allowed+=' historical_options historical_target_row historical_prose historical_inline_label historical_graph_after historical_example_target_row historical_example_options historical_spatial historical_reading_dialogue historical_question_prose historical_question_label historical_picture_example historical_context_keep historical_inline_atoms historical_stem_prose historical_components historical_document_frame historical_wrapped_illustration historical_vertical_inset historical_vertical_letter historical_passage_start historical_question_boundary historical_page_break_after historical_answer_list historical_label_answer historical_inline_dialogue_question'
    from context_html import tables
    from image_html import artwork
    artwork(m)
    if old_state(m):allowed+=' historical_artwork historical_native_diagrams historical_target_dialogue historical_example_frame historical_figure_beside_question'
    tables(m)
    from intake_roles import candidates
    candidates(m) # Validates explicitly reviewed ordinary-body exclusions.
    for target, meta in m['layout']['items'].items():
        reject_unknown(meta, allowed, target)
        if meta.get('vertical_paired_label'):
            from presentation import source_binding
            source_binding(m['unit'],meta['vertical_paired_label']['evidence'])
        for binding in [meta.get('context_label'),meta.get('introduction')]:
            if not binding or not binding.get('following_context'):continue
            items=next(s['items'] for s in m['document']['sections'] if any(i['id']==target for i in s['items']))
            index=next(n for n,i in enumerate(items) if i['id']==target);current=items[index]
            following=binding['following_context']
            projection_binding(current['content'],binding,'separate context lead')
            if index+1>=len(items) or items[index+1]['id']!=following['id'] or digest(items[index+1].get('content'))!=following['content_sha256']:raise ValueError('Separated context lead lost its exact following content')
        if meta.get('keep_with_previous'):
            # Pagination has no geometric effect in the continuous reader.
            item=next(i for s in m['document']['sections'] for i in s['items'] if i['id']==target)
            projection_binding(item['content'],meta['keep_with_previous'],'paragraph keep')
        mode = meta.get('writing_mode', {})
        if isinstance(mode, dict) and mode.get('value', mode.get('mode', 'horizontal')) not in ('horizontal', 'horizontal-tb', 'unknown', 'vertical', 'vertical-rl'):
            raise ValueError('HTML adapter needs writing-mode support for ' + target)
    for section in m['document']['sections']:
        for item in section['items']:
            # Registered samples can retain an ordinary multiline stem in the
            # exact released model. Do not infer a different dialogue layout.
            if not old_state(m) and 'stem' in item and dialogue.candidates(item['stem']) and not m['layout']['items'][item['id']].get('dialogue') and m.get('public_output',{}).get('class')!='sample':
                raise ValueError('Dialogue needs an explicit source layout binding: ' + item['id'])
