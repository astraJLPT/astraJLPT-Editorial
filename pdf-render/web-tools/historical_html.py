"""Shared Old written-paper consumers, bound to the native source contracts."""
import hashlib
import html
import json
import re
from functools import lru_cache
from pathlib import Path
from bs4 import BeautifulSoup
from model import Projection,digest
from presentation import source_binding
from semantic_html import add_style,add_class,pt,gap
from presentation_slice import slice_inline


def definition_label(soup,node,m):
    """Match the native fixed label box and JFM parenthesis cells exactly.

    Generic mixed-script glue is not the authored spacing of a note label.
    Full-width parenthesis glyphs occupy half-em native cells; leaving their
    browser advances at one em crowds the following term for two-digit labels.
    """
    text=node.get_text();match=re.fullmatch(r'([（(])注([0-9０-９]*)([）)])',text)
    if not match:raise ValueError('Invalid atomic Old definition label')
    cfg=m['style'].get('historical_typography',{})
    before=cfg.get('note_after_chu_em',.22);after=cfg.get('note_after_digit_em',.12)
    if any(type(v) not in (int,float) or not 0<=v<=.5 for v in (before,after)):
        raise ValueError('Invalid Old definition label spacing')
    node.clear();add_class(node,'old-note-label')
    add_style(node,white_space='nowrap',overflow_wrap='normal',word_break='keep-all',text_indent='0',
              **{'--old-note-em':pt(m['style']['note_pt'])})
    for n,token in enumerate(match.groups()):
        if n==1:
            node.append('注')
            if token:
                digits=soup.new_tag('span');digits.string=token
                if token.isascii():add_class(digits,'tex-latin')
                add_style(digits,margin_left=f'calc(var(--old-note-em) * {before})',margin_right=f'calc(var(--old-note-em) * {after})')
                node.append(digits)
        else:
            part=soup.new_tag('span');part.string=token
            if token in '（）':
                add_class(part,'old-note-parenthesis')
                add_style(part,display='inline-block',width='calc(var(--old-note-em) * .5)',text_indent='0')
                if n==0:
                    part.clear();glyph=soup.new_tag('span');glyph.string=token
                    add_style(glyph,display='inline-block',transform='translateX(calc(var(--old-note-em) * .5 - 1em))')
                    part.append(glyph)
            else:add_class(part,'tex-latin ascii-parenthesis')
            node.append(part)
    if node.get_text()!=text:raise ValueError('Old definition label changed characters')


def enabled(m):
    return m.get('exam',{}).get('generation')=='historical-1991-2009'


def state(m):
    if not enabled(m):return None
    if '_web_old' in m:return m['_web_old']
    from historical_numbering import collect as numbering
    from historical_layout import collect,collect_stems
    from historical_target_rows import collect as targets
    from historical_example_rows import collect as examples,collect_options
    from historical_context_keep import collect as keeps
    from historical_complex import collect_graphs
    from historical_spatial import collect as spatial
    from historical_groups import collect as groups
    labels,options,breaks=collect(m)
    result=dict(numbering=numbering(m),labels=labels,options=options,stems=collect_stems(m),targets=targets(m),examples=examples(m),example_options=collect_options(m),keeps=keeps(m),graphs=collect_graphs(m),spatial=spatial(m),groups=groups(m))
    from historical_page_relationships import collect as page_relationships
    from historical_answer_lists import collect as answer_lists
    from historical_label_answers import collect as label_answers
    from historical_dialogue_questions import collect as dialogue_questions
    from historical_figure_question import collect as side_figures
    from historical_example_frame import collect as example_frames
    result.update(page_relationships=page_relationships(m),answer_lists=answer_lists(m),label_answers=label_answers(m),
                  dialogue_questions=dialogue_questions(m),side_figures=side_figures(m),example_frames=example_frames(m))
    m['_web_old']=result
    return result


def prepare_field(value,m,target):
    old=state(m)
    if old and target in old['spatial']:
        from historical_spatial import prepare
        binding,original,slot=old['spatial'][target]
        value=prepare(value,binding,original,slot)
    if old and '/' not in target:
        item=next((i for s in m['document']['sections'] for i in s['items'] if i['id']==target),None)
        meta=m['layout']['items'].get(target,{})
        if item:
            original=item.get('stem',item.get('content'))
            if meta.get('historical_stem_prose') and 'data-historical-text-role' not in str(value):
                from historical_prose import prepare
                spec=meta['historical_stem_prose'];value=prepare(value,{**spec,'content_sha256':spec['stem_sha256']},m['unit'],original)
            if meta.get('historical_inline_atoms') and 'data-historical-answer-slot' not in str(value):
                from historical_inline_atoms import prepare
                value=prepare(value,meta['historical_inline_atoms'],m['unit'],original)
            if meta.get('historical_inline_dialogue_question') and 'data-historical-dialogue-blank' in str(value):
                from historical_dialogue_questions import prepare
                value=prepare(value,meta['historical_inline_dialogue_question'],original)
    return value


def block_value(m,item):
    old=state(m);value=item['content']
    if not old:return value
    meta=m['layout']['items'][item['id']];prose=meta.get('historical_prose')
    if meta.get('historical_example_target_row',{}).get('source_shape')=='merged_prompt_target_embedded_choices':
        # Keep the embedded canonical choices once in the source projection;
        # the native example places the target beside its visible option grid.
        soup=BeautifulSoup(value['html'],'html.parser');prompt=soup.p;br=prompt.br
        if br is None or soup.ol is None:raise ValueError('Merged example lost its bound source structure')
        target=soup.new_tag('p')
        for node in list(br.next_siblings):target.append(node.extract())
        br.decompose();prompt.insert_after(target);soup.ol['class']=['source-literal','sr-only']
        value={'html':str(soup)}
    if meta.get('historical_components'):
        from historical_nodes import prepare
        value=prepare(value,meta['historical_components'],m['unit'])
    if meta.get('historical_graph_after') and meta['historical_graph_after'].get('placement','after_questions')=='after_questions':
        from historical_complex import detach_graph
        value,figure=detach_graph(value,meta['historical_graph_after'])
        old.setdefault('figure_hashes',{})[item['id']]=digest(figure)
        if prose:
            from historical_prose import split_deferred_figure
            prose,figure=split_deferred_figure(item['content'],figure,prose,m['unit'])
        old.setdefault('figures',{})[item['id']]=figure
    if prose:
        from historical_prose import prepare
        value=prepare(value,prose,m['unit'],item['content'])
    inferred=old['numbering']
    if inferred and item['id'] in inferred['contexts']:
        from historical_numbering import context_value
        value=context_value(value,inferred['contexts'][item['id']])
    if meta.get('historical_inline_label'):
        from historical_inline_labels import validate,prepare_body_paragraphs
        validate(m,item,meta['historical_inline_label'])
        value,_=prepare_body_paragraphs(value,meta['historical_inline_label']['text'])
    if meta.get('historical_document_frame',{}).get('paragraphs'):
        from historical_document_frame import prepare
        value=prepare(value,meta['historical_document_frame'],m['unit'],item['content'])
    return value


def question_label(m,q,label):
    old=state(m)
    if not old:return str(label),'boxed'
    inferred=(old['numbering'] or {}).get('questions',{}).get(q['id'],{})
    number=inferred.get('display_number',str(label));kind=old['labels'].get(q['id'],inferred.get('kind','boxed'))
    if kind=='boxed':return number,kind
    from historical_layout import question_label as native
    display,_=native(kind,number,m['style'])
    return display,kind


def remove_inferred_prefix(value,m,q):
    old=state(m)
    record=(old['numbering'] or {}).get('questions',{}).get(q['id']) if old else None
    if record:
        from historical_numbering import stem_value
        return stem_value(value,record)
    return value


def leading_content(m,q):
    binding=m['layout']['items'][q['id']].get('printed_label',{}).get('leading_content')
    if not binding:return False
    text=Projection(q['stem']).text
    if not enabled(m) or digest(q['stem'])!=binding['stem_sha256'] or not text.startswith(binding['text']) or not re.match(r'^[0-9]+\s+\S',binding['text']):raise ValueError('Invalid historical leading content')
    source_binding(m['unit'],binding['evidence'])
    return True


@lru_cache(maxsize=None)
def reference_font(path,index,text):
    """Native ink dimensions and x-height, not browser line-box estimates."""
    from fontTools.ttLib import TTFont
    from fontTools.pens.boundsPen import BoundsPen
    with TTFont(path,fontNumber=index) as font:
        cmap=font.getBestCmap();glyphs=font.getGlyphSet();em=font['head'].unitsPerEm
        boxes=[];advance=0
        for char in text:
            if ord(char) not in cmap:raise ValueError('Reference label glyph absent from bound font')
            name=cmap[ord(char)];pen=BoundsPen(glyphs);glyphs[name].draw(pen)
            if pen.bounds:boxes.append(pen.bounds)
            advance+=font['hmtx'][name][0]
        xheight=getattr(font.get('OS/2'),'sxHeight',0)
        if not xheight:
            pen=BoundsPen(glyphs);glyphs[cmap[ord('x')]].draw(pen);xheight=pen.bounds[3]
        return dict(ascent=max((b[3] for b in boxes),default=0)/em,descent=max((max(0,-b[1]) for b in boxes),default=0)/em,width=advance/em,xheight=xheight/em)


def reference_metrics(m,role,text):
    style=m['style'];spec=style['font_roles'].get(role,{'source':role})
    path=Path(spec.get('path',style['fonts'].get(spec.get('source',''),'')))
    path=__import__('package_paths').resource(path)
    return reference_font(str(path),spec.get('font_index',0),text)


def reference_label(soup,n,m):
    """Mirror UnderlinedReference's baseline drop and exact label roles.

    A zero-advance inline label shares the first target baseline. Its transform
    supplies the source drop without making the whole underline unbreakable.
    Only source-requested clearance contributes depth to the surrounding line.
    """
    text=n['data-reference-label'];cfg=m['style']['historical_typography']
    label=soup.new_tag('span',attrs={'class':'old-reference-label visual-only','aria-hidden':'true'})
    if n.get('data-reference-parenthesized')=='true':
        if not text.isdigit() or n.get('data-reference-position','before') not in ('before','after'):raise ValueError('Invalid Old parenthetical reference')
        label.string='（'+text+'）';add_style(label,**{'--old-label-em':'var(--nominal-em)'})
        compact_label(label,m,'parenthesized')
        if n.get('data-reference-position')=='after':n.append(label)
        else:n.insert(0,label)
        return
    if n.name!='u':raise ValueError('Unconsumed historical reference label role')
    boxed=n.get('data-reference-boxed')=='true'
    compact=not boxed and bool(re.fullmatch(r'（[1-9][0-9]*）',text)) and not n.has_attr('data-reference-clearance')
    size=cfg.get('target_reference_pt',5.5) if compact else 7.5
    ex=reference_metrics(m,'body_latin','x')['xheight']
    underline=(m['style'].get('underline_drop_ex',.45)+m['style'].get('underline_thickness_ex',.1))*ex
    drop_ex=cfg.get('target_reference_drop_ex',1.5) if compact else m['style'].get('reference_drop_ex',2)
    add_style(n,text_underline_offset=f'calc(var(--nominal-em) * {m["style"].get("underline_drop_ex",.45)*ex})',text_decoration_thickness=f'calc(var(--nominal-em) * {m["style"].get("underline_thickness_ex",.1)*ex})')
    if boxed:
        if not re.fullmatch(r'[1-9][0-9]*',text):raise ValueError('Old boxed reference requires a positive number')
        font=reference_metrics(m,'boxed_numeral',text);pad=.7;rule=.35
        fixed=cfg.get('inline_box_one_em' if len(text)==1 else 'inline_box_two_em',0)
        width=(fixed if fixed else font['width'])*size+2*(pad+rule)
        height=(font['ascent']+font['descent'])*size+2*(pad+rule);depth=font['descent']*size+pad+rule
        # SVG text uses the same bound local label font. Its frame follows ink
        # bounds, avoiding a browser's unrelated line-height padding.
        svg=BeautifulSoup(f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" aria-hidden="true"><rect x="{rule/2}" y="{rule/2}" width="{width-rule}" height="{height-rule}" fill="none" stroke="currentColor" stroke-width="{rule}"/><text x="{width/2}" y="{font["ascent"]*size+pad+rule}" text-anchor="middle" font-family="Label" font-size="{size}" fill="currentColor">{text}</text></svg>','html.parser').svg
        add_style(svg,width=pt(width),height=pt(height),vertical_align=pt(-depth),overflow='visible');label.append(svg)
        ink_height=pt(font['ascent']*size+pad+rule);clearance=1.5
        label['data-reference-font-role']='boxed_numeral'
    else:
        label.string=text;clearance=float(n.get('data-reference-clearance',0))
        if compact:
            add_style(label,font_size=f'calc(var(--glyph-point) * {size})',**{'--old-label-em':pt(size)})
            compact_label(label,m,'parenthesized')
            japanese=reference_metrics(m,'body','（）')['ascent']*size
            latin=reference_metrics(m,'body_latin',text[1:-1])['ascent']*size
            ink_height=f'max(calc(var(--glyph-point) * {japanese}),{pt(latin)})'
            label['data-reference-font-role']='compact_target'
        else:
            role='body_latin' if text.isascii() else 'body';family='BodyLatin' if text.isascii() else 'Body'
            point='--point' if text.isascii() else '--glyph-point'
            add_style(label,font_family=family,font_size=f'calc(var({point}) * {size})')
            ink_height=f'calc(var({point}) * {reference_metrics(m,role,text)["ascent"]*size})'
            label['data-reference-font-role']=role
    drop=f'max(calc(var(--nominal-em) * {drop_ex*ex}),calc({ink_height} + var(--nominal-em) * {underline} + var(--point) * .6))'
    label['data-reference-size-pt']=str(size)
    add_style(label,display='inline-block',width='0',height='0',line_height='0',white_space='nowrap',vertical_align='baseline',text_indent='0',text_decoration='none',transform=f'translateY({drop})')
    n.insert(0,label)
    if clearance:
        reserve=soup.new_tag('span',attrs={'class':'old-reference-clearance visual-only','aria-hidden':'true'})
        depth=f'calc({drop} + var(--point) * {clearance})'
        add_style(reserve,display='inline-block',width='0',height=depth,vertical_align=f'calc(-1 * {depth})');n.insert(1,reserve)


def present_inline(soup,m):
    if not enabled(m):return
    cfg=m['style'].get('historical_typography',{})
    for n in soup.select('[data-historical-word-gap]'):
        add_class(n,'authored-word-gap')
    for n in soup.select('[data-historical-sentence-blank]'):
        s=json.loads(n['data-historical-sentence-blank'])
        add_style(n,display='inline-block',box_sizing='content-box',width=f'calc(var(--nominal-em) * {s["width_em"]})',height=f'calc(var(--nominal-em) * {s["height_em"]+.08})',border=f'{pt(.4)} solid currentColor',padding='0',font_size='0',vertical_align='calc(var(--nominal-em) * -.08 - var(--point) * .4)')
    for n in soup.select('[data-historical-spatial-paragraph]'):
        s=json.loads(n['data-historical-spatial-paragraph'])
        add_style(n,padding_left=f'calc(var(--nominal-em) * {s.get("inset_em",0)})',text_indent=f'calc(var(--nominal-em) * {s.get("first_line_indent_em",0)-s.get("first_line_outdent_em",0)})',margin_top=gap(s.get('before_pt',0)),margin_bottom=gap(s.get('after_pt',0)),text_align=s.get('align','left'))
        if s.get('font')=='instruction':add_style(n,font_family='Heading')
    for n in soup.select('[data-reference-label]'):reference_label(soup,n,m)
    for n in soup.select('[data-double-underline]'):add_style(n,text_decoration_line='underline',text_decoration_style='double')
    for n in soup.select('[data-extra-underline]'):
        ex=reference_metrics(m,'body_latin','x')['xheight']
        offset=(m['style'].get('underline_drop_ex',.45)+m['style'].get('underline_thickness_ex',.1)+.12)*ex
        add_style(n,text_decoration_line='underline',text_underline_offset=f'calc(var(--nominal-em) * {offset})')
    for n in soup.select('[data-historical-inline-body]'):add_style(n,padding_left='calc(var(--nominal-em) * 1)',text_indent='0')
    for n in soup.select('[data-historical-text-role]'):
        role=n['data-historical-text-role']
        if role=='citation':
            add_style(n,text_align='right',text_indent='0',margin_top=gap(4),margin_bottom=gap(8))
            metrics=cfg.get('citation_metrics',{})
            size=float(n.get('data-historical-font-pt',metrics.get('font_pt',m['style'].get('passage_body_pt',m['style']['body_pt']))))
            leading=float(n.get('data-historical-baseline-pt',metrics.get('baseline_pt',m['style'].get('passage_baseline_pt',m['style']['baseline_pt']))))
            add_style(n,font_size=f'calc(var(--glyph-point) * {size})',line_height=pt(leading))
        elif role=='note':
            raw=n.decode_contents();text=Projection({'html':raw}).text
            if not text.strip() and not n.find('img'):
                # A bound notes block may already have been transferred by the
                # shared note consumer; its empty anchor owns no second text.
                n.decompose();continue
            match=re.match(r'^([（(]注[0-9０-９]*[）)])(.*?[:：])(.*)$',text,re.S)
            if not match:raise ValueError('Old definition lost its exact label/term: '+repr(text[:180]))
            label_width=pt(m['style']['note_pt']*3.6)
            n.clear();add_class(n,'old-note-definition');add_style(n,display='grid',grid_template_columns=f'{label_width} max-content minmax(0,1fr)',font_size=f'calc(var(--glyph-point) * {m["style"]["note_pt"]})',line_height=pt(m['style']['note_baseline_pt']),text_indent='0',margin='0')
            for a,z in [match.span(k) for k in (1,2,3)]:
                part=soup.new_tag('span')
                if z>a:part.append(BeautifulSoup(slice_inline(raw,a,z),'html.parser'))
                n.append(part)
            definition_label(soup,n.contents[0],m)
            add_style(n.contents[1],min_width='0')
            add_style(n.contents[2],min_width='0')
            add_style(n.contents[1],padding_right='.2em')
            arrangement=n.get('data-historical-definition-arrangement')
            if arrangement=='description_next_line':
                add_style(n,grid_template_columns=f'{label_width} minmax(0,1fr)')
                add_style(n.contents[2],grid_column='2',grid_row='2')
            elif arrangement=='continuation_at_term':add_style(n,grid_template_columns=f'{label_width} auto minmax(0,1fr)')
        else:
            from historical_flow_html import prose_role
            prose_role(soup,n,m)
    from historical_flow_html import inline_atoms
    inline_atoms(soup,m)


def reading_dialogue(value,m,binding,source):
    from historical_reading_dialogue import prepare
    from semantic_html import render_dialogue
    prepared=prepare(value,binding,m['unit'],source)
    structure=dict(projection_sha256=hashlib.sha256(Projection(prepared).text.encode()).hexdigest(),turns=binding['turns'],state='observed',speaker_align='left')
    soup=BeautifulSoup(render_dialogue(prepared,m,structure,None,scene_lines=binding.get('scene_lines',()),named_colon=binding.get('turn_separator')=='colon'),'html.parser');region=soup.select_one('.dialogue')
    if binding.get('opening_label'):
        add_style(region,margin_left='calc(var(--nominal-em) * 2.5)',position='relative')
        label=soup.new_tag('span',attrs={'class':'old-dialogue-opening'});label.string=binding['opening_label']
        add_style(label,position='absolute',left='calc(var(--nominal-em) * -2.5)',top='0');region.insert(0,label)
    return str(soup)


def heading(soup,m,target):
    old=state(m)
    binding=(old['numbering'] or {}).get('ranges',{}).get(target) if old else None
    if not binding:return
    from tex_html import visual_atom
    for source,display in zip(binding.get('heading_labels',binding['source_labels']),binding['display_labels']):
        if source==display:continue
        nodes=[n for n in soup.select('.tex-latin') if n.get_text()==source and not n.find_parent(class_='heading-label')]
        if not nodes:
            hits=[n for n in soup.find_all(string=True)if source in str(n) and not any(set(p.get('class',[]))&{'heading-label','source-literal','visual-only'}for p in n.parents)]
            if len(hits)==1:
                text=str(hits[0]);before,after=text.split(source,1);node=soup.new_tag('span');node.string=source
                hits[0].replace_with(before,node,after);nodes=[node]
        if len(nodes)!=1:raise ValueError('Old heading range lost its bound label')
        if binding.get('number_style')=='boxed':
            visual_atom(soup,nodes[0],'cloze-slot old-heading-range',display)
            if m['style']['historical_typography'].get('inline_number_box_role')=='main_question':
                box=m['style']['question_box'];add_style(nodes[0],width=pt(box['width_pt']),height=pt(box['height_pt']),border_width=pt(box['rule_pt']),font_size=pt(m['style']['question_label_pt']))
        else:visual_atom(soup,nodes[0],'old-heading-range','（'+display+'）')


def figure(m,qid):
    old=state(m)
    if not old or qid not in old['graphs'][1]:return ''
    bid=old['graphs'][1][qid]
    if bid not in old.get('figures',{}):
        item=next(i for s in m['document']['sections'] for i in s['items'] if i['id']==bid)
        block_value(m,item)
    value=old['figures'][bid];soup=BeautifulSoup(value['html'],'html.parser')
    table=soup.select_one('table[data-native-chart="historical-2009-pies"]')
    if table is None:
        from tex_html import render_inline
        from semantic_html import present_tables
        soup=BeautifulSoup(render_inline(value,m),'html.parser')
        present_tables(soup,m['style'],bid)
        return '<div class="old-deferred-figure" data-source-context="'+bid+'" data-source-sha256="'+old['figure_hashes'][bid]+'">'+str(soup)+'</div>'
    from richtex import RichTeX
    from historical_figures import pies
    from pathlib import Path
    conv=RichTeX(Path(__file__).resolve().parents[1]/'work/assets');conv.source_target_markers=True
    pies(table,conv)
    import math
    cm=72.27/2.54;parts=['<div class="old-pie-title">グラフ</div><div class="old-pies">']
    pattern='old-pie-dots-'+m['unit']+'-'+qid
    for index,row in enumerate(table.find_all('tr')[1:]):
        cells=row.find_all(['th','td']);label=cells[0].get_text();values=[c.get_text() for c in cells[1:]]
        svg=[f'<svg viewBox="-2.15 -2.05 4.3 4.1" style="width:{pt(4.3*cm)};height:auto;max-width:100%;overflow:visible" aria-hidden="true"><defs><pattern id="{pattern}-{index}" width=".07" height=".07" patternUnits="userSpaceOnUse"><rect width=".07" height=".07" fill="var(--paper)"/><circle cx=".035" cy=".035" r=".008" fill="currentColor"/></pattern></defs>']
        start=90
        point=lambda angle,radius:(radius*math.cos(math.radians(angle)),-radius*math.sin(math.radians(angle)))
        for n,text in enumerate(values):
            amount=float(text[:-1]);end=start-amount*3.6;x,y=point(start,1.5);ex,ey=point(end,1.5)
            fill=['currentColor',f'url(#{pattern}-{index})','var(--paper)'][n]
            svg.append(f'<path d="M 0 0 L {x:.6f} {y:.6f} A 1.5 1.5 0 {int(amount>50)} 1 {ex:.6f} {ey:.6f} Z" fill="{fill}" stroke="currentColor" stroke-width="{.35/cm}"/>')
            mid=(start+end)/2;small=amount<10;radius=1.88 if small else .9 if abs(math.cos(math.radians(mid)))>.9 else 1.07
            lx,ly=point(mid,radius)
            if small:
                ax,ay=point(mid,1.4);bx,by=point(mid,1.66);svg.append(f'<path d="M {ax} {ay} L {bx} {by}" fill="none" stroke="currentColor" stroke-width="{.35/cm}"/>')
            color='var(--paper)' if n==0 and not small else 'currentColor'
            svg.append(f'<text x="{lx}" y="{ly}" text-anchor="middle" dominant-baseline="middle" fill="{color}" font-family="Body" font-size="{9.5/cm}"'+(' stroke="var(--paper)" stroke-width=".042" paint-order="stroke"' if n==1 else '')+'>'+text+'</text>')
            start=end
        svg.append('</svg>');parts.append('<div class="old-pie"><div>'+label+'</div>'+''.join(svg)+'</div>')
    parts.append('</div><div class="old-pie-legend">')
    for index,label in enumerate([c.get_text() for c in table.find_all('tr')[0].find_all('th')][1:]):
        parts.append(f'<span><i class="pie-fill-{index}"></i>{label}</span>')
    parts.append('</div>')
    return '<div class="old-deferred-figure" data-source-context="'+bid+'" data-source-sha256="'+digest(value)+'"><div class="source-literal sr-only">'+str(table)+'</div><div class="visual-only" aria-hidden="true">'+''.join(parts)+'</div></div>'


def present_block(soup,m,item):
    old=state(m)
    if not old:return
    meta=m['layout']['items'][item['id']]
    if meta.get('historical_inline_label') and not soup.select_one('.old-dialogue-opening'):
        p=soup.find('p');tail='';line=BeautifulSoup(p.decode_contents(),'html.parser');br=line.find('br',recursive=False)
        if br:
            following=list(br.next_siblings);tail=str(br)+''.join(map(str,following))
            for node in [br,*following]:node.extract()
        raw=str(line);text=Projection({'html':raw}).text;label=meta['historical_inline_label']['text'];a=text.index(label);z=a+len(label)
        p.clear();lead=soup.new_tag('span');lead.append(BeautifulSoup(slice_inline(raw,0,z),'html.parser'));add_style(lead,display='inline-block',width=f'calc(var(--nominal-em) * {m["style"].get("inline_passage_label_width_em",2.5)})',text_indent='0',white_space='nowrap');p.append(lead)
        if z<len(text):p.append(BeautifulSoup(slice_inline(raw,z,len(text)),'html.parser'))
        if tail:p.append(BeautifulSoup(tail,'html.parser'))
        add_style(p,padding_left='calc(var(--nominal-em) * 1)',text_indent='calc(var(--nominal-em) * -1)')
    if item.get('type')=='example':present_example(soup,m,item)
    from historical_flow_html import components
    components(soup,m,item)


def present_example(soup,m,item):
    old=state(m);cfg=m['style']['examples'];bid=item['id'];meta=m['layout']['items'][bid]
    # Mirror HistoricalExampleExplanation's semantic position: prose after
    # choices and before the answer-sheet demonstration owns the first indent.
    choices_seen=False;explanation_seen=False
    typo=m['style'].get('historical_typography',{})
    for node in soup.find_all(recursive=False):
        classes=set(node.get('class',[]))
        if classes & {'source-literal','example-option-bindings'}:continue
        text=Projection({'html':str(node)}).text.strip()
        if classes & {'example-answer-line','inline-answer-demo'} or re.match(r'^[（(](?:解答用紙|かいとうようし)',text):break
        if classes & {'example-options','example-native-options','example-source-options'} or re.match(r'^[1-4]\s+',text):
            choices_seen=True;continue
        if choices_seen and node.name=='p' and text:
            add_class(node,'example-explanation')
            add_style(node,text_indent='1em',margin_left=f'calc(var(--nominal-em) * {typo.get("example_explanation_inset_em",0)})')
            if not explanation_seen:add_style(node,margin_top=gap(typo.get('example_explanation_before_pt',10)))
            if typo.get('example_explanation_tracking_em'):add_style(node,letter_spacing=f'{typo["example_explanation_tracking_em"]}em')
            explanation_seen=True
    opts=soup.select_one('.example-options,.example-source-options,.example-native-options')
    target=old['examples'].get(bid);grid=old['example_options'].get(bid)
    if target:
        if opts is None:raise ValueError('Old target example lost choices')
        paragraphs=soup.find_all('p',recursive=False);p=paragraphs[target['target_part']]
        if Projection({'html':str(p)}).text.strip()!=target['target_text']:raise ValueError('Old example target moved')
        row=soup.new_tag('div',attrs={'class':'old-example-target'});p.insert_before(row);row.append(p.extract());row.append(opts.extract())
        add_style(row,display='grid',grid_template_columns=f'calc(var(--nominal-em) * {target["target_width_em"]}) minmax(0,1fr)',margin_left=f'calc(var(--nominal-em) * {target["left_indent_em"]})',align_items='start')
        opts['data-native-cols']=str(target['columns']);opts['style']+=f'--example-columns:{target["columns"]};'
        add_style(p,margin='0',text_indent='0');add_style(opts,grid_template_columns='repeat(var(--example-columns),minmax(0,1fr))',margin='0')
    elif grid:
        if opts is None:raise ValueError('Old example lost its bound option grid')
        from historical_example_rows import resolve_options_geometry
        s=resolve_options_geometry(grid,cfg)
        opts['data-native-cols']=str(s['columns']);opts['style']+=f'--example-columns:{s["columns"]};'
        add_style(opts,grid_template_columns='repeat(var(--example-columns),minmax(0,1fr))',margin_left=f'calc(var(--nominal-em) * {s.get("left_indent_em",0)})',width=f'calc({s.get("width_fraction",1)*100}% - var(--nominal-em) * {s.get("left_indent_em",0)})')
    if meta.get('historical_picture_example'):
        from historical_picture_example import validate
        s=meta['historical_picture_example'];validate(item,s,m['unit'])
        if opts is None:raise ValueError('Old picture example lost its options')
        p=soup.find_all('p',recursive=False)
        if s.get('kind')=='prose':
            g=s['prose_geometry']
            add_style(p[0],float='left',width=f'calc(var(--nominal-em) * {g["body_inset_em"]+g["first_line_indent_em"]})')
            add_style(p[1],padding_left=f'calc(var(--nominal-em) * {g["body_inset_em"]})',text_indent=f'calc(var(--nominal-em) * {g["first_line_indent_em"]})')
            add_style(p[2],margin_left=f'calc(var(--nominal-em) * {g.get("query_left_inset_em",1)})')
        else:
            from historical_picture_example import parts
            from semantic_html import render_dialogue
            _,dialogue,turns,_=parts(item['content'])
            structure=dict(projection_sha256=hashlib.sha256(Projection(dialogue).text.encode()).hexdigest(),turns=turns,state='observed',speaker_align='left')
            rendered=BeautifulSoup(render_dialogue(dialogue,m,structure,None),'html.parser')
            frame=soup.new_tag('div',attrs={'class':'old-picture-dialogue'});p[1].insert_before(frame)
            for node in p[1:4]:node.decompose()
            frame.append(rendered);add_style(frame,margin_left=f'calc(var(--nominal-em) * {s.get("dialogue_indent_em",5)})')
            add_style(p[0],position='absolute',width=f'calc(var(--nominal-em) * {s.get("example_label_width_em",5)})',text_indent='0')
            add_style(p[4],padding_left='calc(var(--nominal-em) * 7)',text_indent='calc(var(--nominal-em) * -7)')
        panel_grid(opts,s['image_grid'],example=True)


def panel_grid(grid,s,example=False):
    grid['data-image-panels']='true'
    indent='0' if example else 'var(--option-indent-em)'
    add_style(grid,width=f'calc((100% - var(--nominal-em) * {indent}) * {s.get("panel_grid_width_fraction",1)})',margin_left=f'calc(var(--nominal-em) * ({indent} + {s.get("panel_left_indent_em",0)}))',margin_top=gap(s.get('panel_before_pt',8)))
    for option in grid.find_all('span',recursive=False) if example else grid.select('.option'):
        add_style(option,display='flex',flex_direction='column',align_items='start')
        if not example:add_style(option.select_one('.option-text'),width='100%',margin='0')
        label=option.select_one('.example-choice-number' if example else '.option-number')
        add_style(label,margin_left=f'calc(var(--nominal-em) * {s.get("panel_label_inset_em",0)})',margin_bottom=pt(s.get('panel_label_gap_pt',3)))
        for image in option.select('.source-image'):add_style(image,width=f'{s.get("panel_width_fraction",1)*100}%',height='auto',margin='0')


def present_question(markup,m,q,task,kind):
    old=state(m)
    if not old:return markup
    soup=BeautifulSoup(markup,'html.parser');article=soup.article;grid=article.select_one('.options-grid');stem=article.select_one('.q-stem');label=article.select_one('.question-no')
    # A historical override is optional. The native dispatcher uses the same
    # task-based standard option grid when no explicit arrangement is bound.
    s=old['options'].get(q['id'],{'kind':'grid','columns':int(article['data-native-cols']),'source_numbered':False})
    add_class(article,'old-question');article['data-label-kind']=kind
    if kind!='boxed':
        p=m['style'].get('historical_typography',{});width=p.get('parenthesized_indent_em',2.8) if kind=='parenthesized' else 8 if kind=='bracketed_shitsumon_numbered' else 7 if kind=='bracketed_shitsumon' else 4.6 if kind.startswith('bracketed') else 2.8
        label_size=p.get('parenthesized_size_pt',m['style']['body_pt']) if kind=='parenthesized' and q['id'] not in old['targets'] else m['style']['body_pt']
        add_style(label,border='0',width='auto',height='auto',display='block',white_space='nowrap',font_family='Body',font_size=f'calc(var(--glyph-point) * {label_size})',top='0',line_height='inherit',padding='0',background='none',**{'--old-label-em':f'calc(var(--point) * {label_size})'})
        geometry=p.get({'query':'query_label','bracketed_query':'bracketed_query_label','bracketed_question':'bracketed_numbered_query_label','bracketed_shitsumon':'shitsumon_label','bracketed_shitsumon_numbered':'shitsumon_label'}.get(kind,''))
        if geometry:
            width=geometry['left_inset_em']+geometry['width_em']+(1 if kind=='bracketed_shitsumon_numbered' else 0)
            add_style(label,left=f'calc(var(--nominal-em) * {geometry["left_inset_em"]})',font_family='Body' if geometry['font']=='body' else 'OldQuestion')
            if kind in ('query','bracketed_query','bracketed_question'):
                add_style(article,**{'--option-indent-em':m['style'].get('option_indent_em',2.1)+geometry['left_inset_em']})
        add_style(stem,**{'--question-indent-em':width})
        pullback=p.get('question_continuation_pullback_em',1 if kind in ('bracketed_shitsumon','bracketed_shitsumon_numbered') else None)
        if pullback is not None:add_style(stem,**{'--question-continuation-indent-em':width-pullback})
        compact_label(label,m,kind)
    if q['id'] in old['stems']:add_style(article.select_one('.question-content'),font_family='Heading')
    add_style(grid,width='calc(100% - var(--nominal-em) * var(--option-indent-em))')
    from historical_options_html import special_grid,enhance,question_flow
    special=special_grid(soup,m,q,s)
    if special:pass
    elif s['kind']=='grid':
        columns=s['columns'];article['data-native-cols']=str(columns);grid['style']+=f'--option-columns:{columns};'
        if s.get('column_widths'):
            values=s['column_widths']
            if len(values)!=columns or not all(v>0 for v in values):raise ValueError('Invalid Old column widths')
            grid['data-column-weights']=','.join(map(str,values));add_style(grid,grid_template_columns=' '.join(f'{v*100}%' for v in values),column_gap=f'{(1-sum(values))/(columns-1)*100}%')
        if s.get('image_panels'):
            article['data-image-panels']='true';panel_grid(grid,s)
    elif s['kind']=='combination':
        article['data-native-cols']='1';grid['style']+='--option-columns:1;';add_style(grid,width=f'calc((100% - var(--nominal-em) * var(--option-indent-em)) * {s["width_fraction"]})')
        keys=s['keys'];syntax=s.get('cell_syntax','key_colon_value')
        from historical_combination import parse
        rows=parse(q['options'],keys,syntax)
        from tex_html import render_inline
        for node,row in zip(grid.select('.option-text'),rows):
            node.clear();add_style(node,display='grid',grid_template_columns=f'repeat({s.get("cell_columns",len(keys))},minmax(0,1fr))')
            for match in row:
                cell=soup.new_tag('span');cell.append(BeautifulSoup(render_inline(match['whole'],m,'option'),'html.parser'));node.append(cell)
    else:raise ValueError('Old options need a consumer: '+s['kind'])
    from historical_metrics import parameters as component_metrics
    metrics=component_metrics(m['style'],task)
    if not s.get('image_panels') and not special:
        for option in grid.select('.option'):
            label_width=1.5 if s['kind']=='combination' else s.get('label_width_em',metrics['option_label_width_em'])
            add_style(option,grid_template_columns=f'calc(var(--nominal-em) * {label_width}) minmax(0,1fr) 1em')
            add_style(option.select_one('.option-text'),margin_left='0')
    local=m['style'].get('task_overrides',{}).get(task,{})
    baseline=local.get('option_baseline_pt',m['style']['option_baseline_pt']);body=local.get('body_pt',m['style']['body_pt'])
    if not s.get('image_panels') and not special:add_style(grid,margin_top=gap(baseline*.3-body*.2))
    if q['id'] in old['targets']:
        from historical_target_rows import parameters
        t=old['targets'][q['id']];dims={**parameters(m['style'],task),**{k:v for k,v in t.items() if k=='target_width_em'}}
        row=soup.new_tag('div',attrs={'class':'old-target-row'});stem.insert_before(row);row.append(stem.extract());row.append(grid.extract())
        add_style(row,display='grid',grid_template_columns=f'calc(var(--nominal-em) * {dims["target_width_em"]}) minmax(0,1fr)',margin_left=f'calc(var(--nominal-em) * {dims["left_indent_em"]})',align_items='start')
        add_style(stem,margin='0',**{'--question-indent-em':dims['label_width_em'],'--question-continuation-indent-em':dims['label_width_em']})
        add_style(grid,margin='0',padding='0',width='100%',row_gap=gap(dims['choice_row_gap_pt']));add_style(article,padding_top=gap(dims['row_gap_pt']),margin_top='0',margin_bottom=gap(metrics['target_group_after_pt']) if q['id'] in old['groups'][1] else '0')
        article['data-source-context']=t['context_id']
    enhance(soup,m,q,s)
    question_flow(soup,m,q,old)
    return str(soup)


def compact_label(node,m,kind):
    p=m['style']['historical_typography'];text=node.get_text();soup=BeautifulSoup('','html.parser')
    if kind=='parenthesized':
        match=re.fullmatch('（([0-9]+)）',text)
        if not match:raise ValueError('Old compact label changed')
        node.clear()
        for index,token in enumerate(['（',match[1],'）']):
            part=soup.new_tag('span');part.string=token;add_style(part,display='inline-block',text_indent='0')
            if index!=1:
                side=f'calc(var(--old-label-em) * {p["parenthesis_side_em"]})'
                add_style(part,width=side,text_align='left')
                if index==0:
                    # CSS right alignment falls back to the start when this
                    # full-em glyph overflows its narrow source makebox.
                    # Position the glyph explicitly at the box's right edge.
                    part.clear();glyph=soup.new_tag('span');glyph.string=token
                    add_style(glyph,display='inline-block',transform=f'translateX(calc({side} - 1em))')
                    part.append(glyph)
            else:
                add_style(part,font_family='BodyLatin,Body,serif',font_size='var(--old-label-em)')
                if len(token)>1:
                    width=reference_metrics(m,'body_latin',token)['width']*p['two_digit_width']
                    part.clear();digits=soup.new_tag('span');digits.string=token
                    add_style(part,width=f'calc(var(--old-label-em) * {width})')
                    add_style(digits,display='inline-block',transform=f'scaleX({p["two_digit_width"]})',transform_origin='left');part.append(digits)
            node.append(part)
    elif kind in ('question','bracketed_question','bracketed_query'):
        add_style(node,font_family='OldQuestion,Body,serif')
        node.clear()
        for part in re.split(r'([0-9]+)',text):
            if not part:continue
            if part.isdigit():
                digit=soup.new_tag('span');digit.string=part;dims=p['reading_digit'];add_style(digit,display='inline-block',font_family='OldDigit,Body,serif',font_size='var(--old-label-em)',transform=f'scale({dims["width"]},{dims["height"]})',transform_origin='left bottom',margin_left=f'calc(var(--nominal-em) * {p["question_digit_gap_em"]})');node.append(digit)
            else:node.append(part)


def block_geometry(m,item,task):
    old=state(m)
    if not old:return ''
    from historical_metrics import parameters
    p=parameters(m['style'],task);values={}
    if item['id'] in old['groups'][0]:values.update(block_before_pt=p['target_group_before_pt'],passage_after_pt=p['target_prose_after_pt'])
    if item['id'] in old['example_options']:
        from historical_example_rows import after_gap
        values['passage_after_pt']=after_gap(m['style']['examples'],old['example_options'][item['id']],m['style']['examples'].get('after_pt',10))[0]
    return ''.join('--'+k.replace('_','-')+':'+str(v)+';' for k,v in values.items())
