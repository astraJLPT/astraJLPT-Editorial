"""Historical choice arrangements using the reader's real radio/label cells."""
import re
from bs4 import BeautifulSoup
from model import Projection
from semantic_html import add_style, pt, gap
from historical_flow_html import em


def special_grid(soup,m,q,s):
    article=soup.article;grid=article.select_one('.options-grid');kind=s['kind']
    if kind not in ('shared_header_table','chronology'):return False
    article['data-native-cols']='1';grid['style']+='--option-columns:1;'
    add_style(grid,grid_template_columns='1fr',gap='0',width=f'{s.get("width_fraction",1)*100}%')
    if kind=='shared_header_table':
        headers=None
        for option in grid.select('.option'):
            text=option.select_one('.option-text');table=text.table
            if table is None:raise ValueError('Historical shared table lost its canonical cells')
            rows=table.find_all('tr');head=rows[0].find_all(['th','td'],recursive=False);cells=rows[1].find_all(['th','td'],recursive=False)
            current=[c.decode_contents() for c in head]
            if headers is not None and current!=headers:raise ValueError('Shared option table headers differ')
            headers=current;literal=soup.new_tag('span',attrs={'class':'source-literal sr-only'});literal.append(table.extract());text.clear();text.append(literal)
            visual=soup.new_tag('span',attrs={'class':'old-table-values visual-only','aria-hidden':'true'})
            for cell in cells:
                node=soup.new_tag('span');node.append(BeautifulSoup(cell.decode_contents(),'html.parser'));visual.append(node)
            text.append(visual);add_style(text,margin='0');add_style(visual,display='grid',grid_template_columns='1fr 1fr')
            for cell in visual.find_all(recursive=False):add_style(cell,padding=pt(s.get('row_sep_pt',7)),border_left=f'{pt(.4)} '+s.get('table_inner_separator','solid')+' currentColor',text_align=s.get('table_cell_alignment','left'))
            add_style(option,grid_template_columns=em(1.6)+' minmax(0,1fr)',padding='0',border=f'{pt(.4)} solid currentColor',border_top='0')
            add_style(option.select_one('.option-number'),text_align='center')
            add_style(option.select_one('.option-feedback'),position='absolute',right='0',top='0')
        header=soup.new_tag('div',attrs={'class':'old-option-header visual-only','aria-hidden':'true'})
        add_style(header,display='grid',grid_template_columns=em(1.6)+' 1fr 1fr')
        header.append(soup.new_tag('span'))
        for raw in headers:
            cell=soup.new_tag('span');cell.append(BeautifulSoup(raw,'html.parser'));add_style(cell,padding=pt(s.get('row_sep_pt',7)),border=f'{pt(.4)} solid currentColor',text_align='center')
            if s.get('header_tracking_em'):add_style(cell,letter_spacing=em(s['header_tracking_em']))
            header.append(cell)
        grid.insert(0,header);add_style(grid,margin_top=gap(s.get('before_pt',8)))
    else:
        for index,option in enumerate(grid.select('.option')):
            text=option.select_one('.option-text');raw=text.decode_contents();plain=Projection({'html':raw}).text
            match=re.fullmatch(r'([a-d]) − ([a-d]) − a − ([a-d])',plain)
            if not match:raise ValueError('Historical chronology lost its bound order')
            text.clear();literal=soup.new_tag('span',attrs={'class':'source-literal sr-only'});literal.append(BeautifulSoup(raw,'html.parser'));text.append(literal)
            visual=soup.new_tag('span',attrs={'class':'visual-only','aria-hidden':'true'});add_style(visual,display='grid',grid_template_columns='repeat(7,2em)',text_align='center')
            for j,value in enumerate([match[1],'−',match[2],'−','a','−',match[3]]):
                cell=soup.new_tag('span');cell.string=value
                if j==4:add_style(cell,border_left=f'{pt(.4)} solid currentColor',border_right=f'{pt(.4)} solid currentColor',border_top=f'{pt(.4)} solid currentColor' if index==0 else '0',border_bottom=f'{pt(.4)} solid currentColor' if index==3 else '0')
                visual.append(cell)
            text.append(visual)
        add_style(grid,width='max-content',max_width='100%')
    return True


def enhance(soup,m,q,s):
    from tex_html import render_inline
    article=soup.article;grid=article.select_one('.options-grid')
    image_only=all(isinstance(v,dict) and len(BeautifulSoup(v['html'],'html.parser').find_all('img'))==1 and not Projection(v).text.strip() for v in q['options'])
    if image_only and s['kind']=='grid':
        # These source-bound columns contain scalable artwork, not text whose
        # intrinsic SVG width should force the text-fitting fallback to one.
        article['data-image-panels']='true';grid['data-image-panels']='true'
        if not s.get('source_numbered'):
            for option in grid.select('.option'):
                add_style(option,align_items='start')
                add_style(option.select_one('.option-number'),align_self='start')
    if s.get('source_numbered'):
        for option in grid.select('.option'):
            label=option.select_one('.option-number');label['class'].append('sr-only')
            add_style(option,display='block');add_style(option.select_one('.option-text'),display='block',margin='0')
            for im in option.select('.source-image'):add_style(im,width=f'{s.get("panel_width_fraction",1)*100}%',margin='0')
    if s.get('contiguous_strip'):
        from PIL import Image
        import io,base64
        sizes=[Image.open(io.BytesIO(base64.b64decode(BeautifulSoup(v['html'],'html.parser').img['src'].split(',',1)[1]))).size for v in q['options']]
        if len({h for w,h in sizes})!=1:raise ValueError('Contiguous strip height changed')
        add_style(grid,grid_template_columns=' '.join(f'{w}fr' for w,h in sizes),gap='0',width='100%',margin='0');grid['data-column-weights']=','.join(str(w/sum(w for w,h in sizes)) for w,h in sizes)
        for option in grid.select('.option'):add_style(option,padding='0',border='0')
    for index,text in enumerate(grid.select('.option-text'),1):
        if str(index) in s.get('text_horizontal_scales',{}):
            scale=s['text_horizontal_scales'][str(index)];wrapper=soup.new_tag('span')
            for child in list(text.contents):wrapper.append(child.extract())
            text.append(wrapper);add_style(wrapper,display='inline-block',transform=f'scaleX({scale})',transform_origin='left',width=f'{100/scale}%')
        if s.get('paired_fragments') or s.get('aligned_pairs'):
            raw=render_inline(q['options'][index-1],m,'option');value=Projection(q['options'][index-1]).text;at=value.index('　')
            from presentation_slice import slice_inline
            text.clear()
            for start,end in [(0,at),(at,len(value))]:
                segment=slice_inline(raw,start,end)
                if s.get('aligned_pairs'):
                    from label_separators import prepare as label_separators
                    prepared,_=label_separators({'html':segment},presentation=False);segment=prepared['html']
                cell=soup.new_tag('span');cell.append(BeautifulSoup(segment,'html.parser'));text.append(cell)
            if s.get('aligned_pairs'):add_style(text,display='grid',grid_template_columns=em(s['aligned_pairs']['first_column_width_em'])+' 1fr')
            else:add_style(text,display='inline-flex',column_gap=em(s['paired_fragments']['gap_em']))
        if s.get('sequence_arrow_indent_em'):
            for node in text.find_all(string=True):
                if str(node).strip()=='↓':
                    arrow=soup.new_tag('span');arrow.string=str(node);add_style(arrow,display='inline-block',margin_left=em(s['sequence_arrow_indent_em']));node.replace_with(arrow)
    if s.get('row_gap_pt') is not None:add_style(grid,row_gap=gap(s['row_gap_pt']))
    sides=[side for side in ('prefix','suffix') if 'braced_'+side in s]
    if sides:
        from historical_layout import braced_stem
        braced_stem(q,s)
        stem=article.select_one('.question-content');wrapper=soup.new_tag('div',attrs={'class':'old-braced-choices'})
        grid.insert_before(wrapper);wrapper.append(grid.extract());add_style(wrapper,display='flex',align_items='center',max_width='100%',overflow_x='auto')
        # Shared phrases reserve their source-bound widths. Do not squeeze the
        # choices to one glyph between them on narrow screens. Keep wrapping
        # within the available measure, down to ten nominal glyph widths
        # including labels; beyond that the existing wrapper can scroll.
        add_style(grid,width='max-content' if 'suffix' in sides else 'auto',min_width=em(10),max_width='100%',flex='1 1 auto',margin='0')
        for side in sides:
            spec=s['braced_'+side];paragraphs=stem.find_all('p');matches=[p for p in paragraphs if Projection({'html':p.decode_contents()}).text.strip()==spec['text']]
            if len(matches)!=1:raise ValueError('Bound shared answer phrase moved')
            phrase=matches[0];copy=BeautifulSoup(str(phrase),'html.parser').p;phrase['class']=[*phrase.get('class',[]),'sr-only']
            copy['class']=['visual-only'];copy['aria-hidden']='true';add_style(copy,flex=f'0 0 {em(spec[side+"_width_em"])}',margin='0',text_indent='0')
            brace=BeautifulSoup('<svg viewBox="0 0 16 100" preserveAspectRatio="none" class="visual-only" aria-hidden="true"><path d="M 15 0 C 2 0 9 42 1 50 C 9 58 2 100 15 100" fill="none" stroke="currentColor" stroke-width="1"/></svg>','html.parser').svg
            add_style(brace,width=em(1),align_self='stretch',flex_shrink='0',min_height=em(6))
            if side=='prefix':wrapper.insert(0,brace);wrapper.insert(0,copy);add_style(wrapper,margin_left=em(spec.get('indent_em',0)))
            else:add_style(brace,transform='scaleX(-1)');wrapper.append(brace);wrapper.append(copy)


def question_flow(soup,m,q,old):
    article=soup.article;stem=article.select_one('.q-stem');content=article.select_one('.question-content');grid=article.select_one('.options-grid');label=article.select_one('.question-no')
    if q['id'] in old['label_answers']:
        from historical_label_answers import label_parts
        spec=old['label_answers'][q['id']];marker,instruction=label_parts(q,spec)
        marker=spec['label'] if spec.get('label_style')=='bare_kana' else marker
        content['class'].append('sr-only');label.string=marker
        add_style(label,position='static',border='0',height='auto',width=em(2.8),font_family='Body' if spec.get('kana_font')=='body' or spec.get('label_style')=='circled' else 'Heading')
        row=soup.new_tag('div',attrs={'class':'old-label-answer'});stem.insert_after(row);row.append(label.extract());row.append(grid.extract());add_style(row,display='grid',grid_template_columns=em(2.8)+' minmax(0,1fr)');add_style(grid,width='100%',margin='0')
        if instruction:
            from tex_html import render_inline
            lead=soup.new_tag('div',attrs={'class':'visual-only','aria-hidden':'true'});lead.append(BeautifulSoup(render_inline(instruction,m),'html.parser'));row.insert_before(lead)
        add_style(stem,margin='0',padding='0',min_height='0')
    elif q['id'] in old['answer_lists']:
        spec=old['answer_lists'][q['id']];number=m['layout']['items'][q['id']]['printed_label']['value']
        hide=spec.get('shared_prompt_owner') or q['stem']==number
        if hide:content['class'].append('sr-only')
        add_style(stem,padding='0',margin='0',display='block');add_style(content,padding='0',text_indent='0',margin_bottom=gap(spec.get('prompt_after_pt',6)) if not hide else '0')
        if spec.get('answer_number_placement')=='prompt_right':add_style(label,position='static',float='right')
        else:
            row=soup.new_tag('div',attrs={'class':'old-answer-list'});grid.insert_before(row);row.append(label.extract());row.append(grid.extract());add_style(row,display='grid',grid_template_columns='calc(var(--nominal-em) * var(--question-indent-em)) minmax(0,1fr)',align_items='start');add_style(label,position='static');add_style(grid,width='100%',margin='0')
    elif q['id'] in old['dialogue_questions']:
        # The source label is part of the final dialogue line, not a separate
        # boxed question before the first speaker.
        label['class'].append('sr-only');add_style(stem,padding='0');add_style(content,padding='0',text_indent='0')
