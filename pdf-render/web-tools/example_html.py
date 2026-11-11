"""Shared, unscored worked-example furniture from the bound TeX style."""
import re
from bs4 import BeautifulSoup
from model import Projection
from presentation_slice import slice_inline
from semantic_html import add_style, add_class, pt, gap


def native_answer_rows(soup,meta):
    """Expose exactly the AnswerLine/InlineAnswerLine forms accepted by TeX.

    Captured paragraphs, line breaks and combined bubble cells are storage
    variants of the same unscored row. Never infer an answer or add a label.
    """
    circles='①②③④❶❷❸❹●'
    answer_name=r'[（(](?:解答用紙|かいとうようし)[）)]'
    example_name=r'[（(](?:例|れい)[）)]'
    for p in list(soup.find_all('p')):
        if p.find_parent('table') or p.find(['div','p','table']):continue
        raw=p.decode_contents().replace('<br/>','\n').replace('<br>','\n')
        text=Projection({'html':raw}).text
        combined=re.fullmatch(r'\s*('+answer_name+r')\s*('+example_name+r')\s*(['+circles+r'\s]+)\s*',text)
        separate=re.fullmatch(r'\s*('+example_name+r')\s*(['+circles+r'\s]+)\s*',text)
        inline=re.fullmatch(r'\s*([（(]解答用紙の例[：:])\s*(['+circles+r'\s]+)([）)])\s*',text)
        prev=p.find_previous_sibling()
        if separate and (not prev or not re.fullmatch(r'\s*'+answer_name+r'\s*',Projection({'html':str(prev)}).text)):separate=None
        match=combined or separate or inline
        if not match:continue
        if len(re.findall('['+circles+']',text))!=4:raise ValueError('Answer demonstration needs four source bubbles')
        if inline and not meta.get('example_layout',{}).get('inline_answer_frame'):
            add_class(p,'inline-answer-demo');continue
        wrap=soup.new_tag('div',attrs={'class':'table-scroll','role':'region','aria-label':'Worked answer example','tabindex':'0'})
        table=soup.new_tag('table');wrap.append(table);row=soup.new_tag('tr');table.append(row)
        if combined or inline:
            caption=soup.new_tag('caption');caption.append(BeautifulSoup(slice_inline(raw,match.start(1),match.end(1)),'html.parser'));table.insert(0,caption)
        if combined or separate:
            k=2 if combined else 1
            cell=soup.new_tag('td');cell.append(BeautifulSoup(slice_inline(raw,match.start(k),match.end(k)),'html.parser'));row.append(cell)
        else:
            table['data-answer-label']='false';add_class(wrap,'example-inline-answer-line')
            tail=soup.new_tag('span');tail.append(BeautifulSoup(slice_inline(raw,match.start(3),match.end(3)),'html.parser'));wrap.append(tail)
        k=3 if combined else 2
        cell=soup.new_tag('td');cell.append(BeautifulSoup(slice_inline(raw,match.start(k),match.end(k)),'html.parser'));row.append(cell)
        p.replace_with(wrap)
    # A legacy cell containing all four marks gets the same four native cells
    # and colsep as a five-cell source table, without double word-space glue.
    for table in soup.find_all('table'):
        rows=table.find_all('tr')
        if len(rows)!=1:continue
        for cell in list(rows[0].find_all(['td','th'],recursive=False)):
            raw=cell.decode_contents();text=Projection({'html':raw}).text
            marks=list(re.finditer('['+circles+']',text))
            if len(marks)==4 and not re.sub('['+circles+r'\s]','',text):
                for j,mark in enumerate(marks):
                    c=soup.new_tag('td');c.append(BeautifulSoup(slice_inline(raw,0 if j==0 else mark.start(),marks[j+1].start() if j<3 else len(text)),'html.parser'));cell.insert_before(c)
                cell.decompose()
        for cell in rows[0].find_all(['td','th'],recursive=False):
            text=Projection({'html':str(cell)}).text
            if len(re.findall('['+circles+']',text))!=1 or re.sub('['+circles+r'\s]','',text):continue
            add_class(cell,'answer-bubble-cell')
            for space in cell.select('.tex-word-space'):space['class']='source-literal sr-only'
            for node in list(cell.find_all(string=True)):
                if node.strip() or node.find_parent(class_='source-literal'):continue
                hidden=soup.new_tag('span',attrs={'class':'source-literal sr-only'});node.wrap(hidden)


def bind_printed_options(soup,item,m):
    """Keep distinct editorial option/ruby bindings behind one printed choice.

    An example may store the same choice both in its printed body and in its
    option fields, with distinct frozen ruby IDs. An inert template retains the
    latter fields, and each is bound to its already visible printed choice.
    """
    from tex_html import render_inline
    compact=lambda v:re.sub(r'\s+','',Projection(v).text)
    candidates=soup.select('.example-native-options > span')
    list_candidates=soup.select('.example-source-options > li')
    if not candidates and list_candidates:candidates=list_candidates
    if not candidates:
        for n,option in enumerate(item['options'],1):
            # A worked solution repeats/reorders choices. Bind the independent
            # original strip, whose complete order is exactly 1,2,3,4.
            strips=[t for t in soup.find_all('table') if len(t.find_all('tr'))==1 and [compact({'html':str(c)}) for c in t.find_all('td')]==[str(j)+compact(o) for j,o in enumerate(item['options'],1)]]
            if len(strips)>1:raise ValueError('Printed example has ambiguous independent option strips')
            hits=[strips[0].find_all('td')[n-1]] if strips else [p for p in soup.find_all(['p','td']) if compact({'html':str(p)})==str(n)+compact(option)]
            if len(hits)!=1:raise ValueError(m['unit']+':'+item['id']+' option '+str(n)+' needs one exact source paragraph')
            candidates.append(hits[0])
    if len(candidates)!=4:raise ValueError('Printed example options need four native choice anchors')
    template=soup.new_tag('template',attrs={'class':'example-option-bindings'})
    for n,(option,printed) in enumerate(zip(item['options'],candidates),1):
        expected_text=compact(option) if printed.name=='li' else str(n)+compact(option)
        if compact({'html':str(printed)})!=expected_text:raise ValueError('Example option differs from its printed anchor')
        expected={(r['base'],r['reading']) for r in Projection(option).ruby}
        actual={(r['base'],r['reading']) for r in Projection({'html':str(printed)}).ruby}
        if not expected<=actual:raise ValueError('Printed example option omits its bound ruby')
        anchor=item['id']+'-native-option-'+str(n);printed['id']=anchor
        source=soup.new_tag('span',attrs={'data-option-index':str(n),'data-printed-anchor':anchor})
        source.append(BeautifulSoup(render_inline(option,m,'example',item['id']+'/options/'+str(n-1)),'html.parser'));template.append(source)
    soup.append(template)


def source_options(soup,item,style,task):
    """Keep one ordered list and lift invalid block children out of paragraphs."""
    for paragraph in list(soup.find_all('p')):
        blocks=paragraph.find_all(['ol','ul','table','div'],recursive=False)
        if not blocks:continue
        current=soup.new_tag('p',attrs=dict(paragraph.attrs))
        for child in list(paragraph.contents):
            if child in blocks:
                if current.contents:paragraph.insert_before(current)
                paragraph.insert_before(child.extract());current=soup.new_tag('p',attrs=dict(paragraph.attrs))
            else:current.append(child.extract())
        if current.contents:paragraph.insert_before(current)
        paragraph.decompose()
    expected=[Projection(o).text.strip() for o in item.get('options',[])]
    matches=[]
    for listing in soup.find_all('ol'):
        if 'source-literal' in listing.get('class',[]) or listing.find_parent(class_='source-literal'):continue
        rows=listing.find_all('li',recursive=False)
        if expected and [Projection({'html':str(r)}).text.strip() for r in rows]==expected:
            if listing.has_attr('reversed') or listing.get('start','1')!='1':continue
            matches.append(listing)
    if len(matches)>1:raise ValueError('Ambiguous repeated source option lists')
    for listing in matches:
        add_class(listing,'example-source-options')
        columns=1 if task in ('usage','paraphrase') else 4
        add_style(listing,display='grid',grid_template_columns=f'repeat({columns},minmax(0,1fr))',
                  margin_left=f'calc(var(--nominal-em) * {style["examples"].get("ordinary_choice_indent_em",style["examples"].get("choice_indent_em",1.8))})')


def present(soup, style, meta, task):
    ex=style['examples'];star=meta.get('example_variant')=='star_worked'
    native_answer_rows(soup,meta)
    for slot in list(soup.select('.star-slot')):
        paragraph=slot.find_parent('p')
        if paragraph and Projection({'html':str(paragraph)}).text.count('_')<3:
            slot.replace_with('★')
    # Four existing numbered choices may be stored as lines or one paragraph.
    # Their native order, labels, punctuation and ruby remain intact.
    for p in list(soup.find_all('p')):
        if p.find_parent('table') or p.find(['p','div','table']):continue
        raw=p.decode_contents().replace('<br/>','\n').replace('<br>','\n')
        text=Projection({'html':raw}).text
        matches=list(re.finditer(r'(?<!\S)([1-4])[)）]?\s+',text))
        if len(matches)!=4 or [m[1] for m in matches]!=list('1234'):continue
        start=matches[0].start();prefix=text[:start]
        if prefix.strip() and not prefix.endswith('\n'):continue
        explicit_lines='\n' in text[start:].rstrip()
        grid=soup.new_tag('div',attrs={'class':'example-native-options'})
        if explicit_lines:grid['data-source-columns']='1'
        for j,m in enumerate(matches):
            cell=soup.new_tag('span');cell.append(BeautifulSoup(slice_inline(raw,m.start(),matches[j+1].start() if j<3 else len(text)),'html.parser'));grid.append(cell)
        if prefix.strip():
            p.clear();p.append(BeautifulSoup(slice_inline(raw,0,start).rstrip(),'html.parser'));p.insert_after(grid)
        else:p.replace_with(grid)
    for grid in soup.select('.example-options,.example-native-options'):
        for cell in grid.find_all('span',recursive=False):
            number=cell.select_one('.tex-latin')
            if ex.get('choice_numeral_role')=='choice' and number and re.fullmatch('[1-4]',number.get_text()):
                original=number.select_one('.content-digits')
                width=re.search(r'(?:^|;)width:([^;]+)',original.get('style','')) if original else None
                value=number.get_text();number.clear();number['class']='example-choice-number'
                if width:number['style']='width:'+width[1]
                digit=soup.new_tag('span');digit.string=value;number.append(digit)
        add_style(grid,margin_left=f'calc(var(--nominal-em) * {ex.get("choice_indent_em",1.8) if star else ex.get("ordinary_choice_indent_em",ex.get("choice_indent_em",1.8))})')
        if task in ('usage','paraphrase'):add_style(grid,grid_template_columns='1fr')
        if grid.get('data-source-columns')=='1':add_style(grid,grid_template_columns='1fr',margin_left='0')
    for table in list(soup.find_all('table')):
        rows=table.find_all('tr');text=Projection({'html':str(table)}).text
        bubbles=re.findall('[①②③④❶❷❸❹●]',text)
        if len(rows)==1 and len(bubbles)==4:
            add_class(table,'example-answer-table')
            wrap=table.parent
            if 'table-scroll' not in wrap.get('class',[]):raise ValueError('Unwrapped example answer table')
            add_class(wrap,'example-answer-line')
            cap=table.find('caption')
            first_cell=rows[0].find(['td','th'],recursive=False)
            answer_label=r'\s*[（(](?:解答用紙|かいとうようし|解答|答え)[）)]\s*'
            if cap:cap.extract();cap.name='span';wrap.insert(0,cap)
            elif first_cell and re.fullmatch(answer_label,Projection({'html':str(first_cell)}).text):
                # The TeX emitter places a captured first-cell sheet label
                # outside the answer box, just like a separate caption.
                first_cell.extract();first_cell.name='span';first_cell.attrs={};wrap.insert(0,first_cell)
            else:
                prev=wrap.find_previous_sibling()
                if prev and re.fullmatch(answer_label,Projection({'html':str(prev)}).text):
                    prev.extract();prev.name='span';wrap.insert(0,prev)
            first_cell=rows[0].find(['td','th'],recursive=False)
            if first_cell and re.fullmatch(r'\s*[（(](?:例|れい)[）)]\s*',Projection({'html':str(first_cell)}).text):
                for border in list(first_cell.find_all('span')):
                    if 'border:' in border.get('style',''):border.unwrap()
                label=soup.new_tag('span',attrs={'class':'answer-example-label'})
                for child in list(first_cell.contents):label.append(child.extract())
                first_cell.append(label)
            add_style(wrap,margin_top=gap(ex.get('answer_before_pt',7)),margin_bottom=0,
                      padding_right=f'calc(var(--nominal-em) * {-2*ex.get("answer_offset_em",0)})')
            # TeX's Japanese font metric gives label parentheses half cells.
            # These are labels, not empty answer brackets or numeral bubbles.
            for node in list(wrap.find_all(string=True)):
                if not re.search('[（）]',str(node)):continue
                if any(p.name in ('rt','rp') or 'source-literal' in p.get('class',[]) for p in node.parents):continue
                out=[]
                for part in re.split('([（）])',str(node)):
                    if part in ('（','）'):
                        mark=soup.new_tag('span',attrs={'class':'answer-label-parenthesis'+(' open' if part=='（' else '')});mark.string=part;out.append(mark)
                    elif part:out.append(part)
                node.replace_with(*out)
        elif star and len(rows)>=2 and all(len(r.find_all(['td','th'],recursive=False))==6 for r in rows[:2]):
            add_class(table,'star-worked-table')
            wrap=table.parent;add_class(wrap,'star-worked-frame')
            following=wrap.find_next_sibling()
            while following and following.name=='p' and re.match(r'^[A-ZＡ-Ｚ]\s*[「｢]',Projection({'html':str(following)}).text.strip()):
                nxt=following.find_next_sibling();row=soup.new_tag('tr');cell=soup.new_tag('td',colspan='6')
                for child in list(following.contents):cell.append(child.extract())
                following.decompose();row.append(cell);table.append(row);following=nxt
            add_style(wrap,width=f'{ex.get("star_box_width_fraction",1)*100}%',
                      padding=pt(ex.get('star_box_padding_pt',15)),
                      margin_top=gap(ex.get('star_frame_before_pt',ex.get('star_solution_before_pt',20))),
                      margin_bottom=gap(ex.get('star_solution_after_pt',14)))
            if ex.get('star_box_align','left')=='center':add_style(wrap,margin_left='auto',margin_right='auto')
            add_style(table,line_height=f'calc(var(--point) * {ex.get("star_row_baseline_pt",20)} * var(--line-preset) * var(--line-adjust))')
    for line in soup.select('.example-answer-table,.inline-answer-demo'):
        for node in list(line.find_all(string=True)):
            if node.find_parent(class_='source-literal') or not re.search('[①②③④❶❷❸❹●]',str(node)):continue
            out=[]
            for part in re.split('([①②③④❶❷❸❹●])',str(node)):
                if not part:continue
                if part not in '①②③④❶❷❸❹●':out.append(part);continue
                filled=part in '❶❷❸❹●'
                atom=soup.new_tag('span',attrs={'class':'answer-bubble'+(' filled' if filled else '')})
                literal=soup.new_tag('span',attrs={'class':'source-literal sr-only'});literal.string=part;atom.append(literal)
                glyph=soup.new_tag('span',attrs={'class':'visual-only','aria-hidden':'true'})
                if filled:glyph.string='\u200b'
                else:
                    from font_geometry import role_metrics
                    number=str('①②③④'.index(part)+1)
                    metric=role_metrics({'style':style},'answer_bubble_numeral',number)
                    svg=soup.new_tag('svg',attrs={'viewBox':'0 0 1000 1000','width':'1em','height':'1em','class':'bubble-ink','focusable':'false'})
                    text=soup.new_tag('text',attrs={'x':'500','y':str(500+500*(metric['top']+metric['bottom'])),'text-anchor':'middle','font-size':'1000'})
                    text.string=number;svg.append(text);glyph.append(svg)
                atom.append(glyph);out.append(atom)
            node.replace_with(*out)
    return ';'.join('--example-'+k.replace('_','-')+':'+str(v) for k,v in ex.items() if isinstance(v,(int,float)))+f';--example-top-pt:{ex.get("ordinary_top_padding_pt",ex.get("ordinary_padding_pt",9)) if not star else ex.get("ordinary_padding_pt",9)};--word-space-em:{ex.get("word_space_em",0) if star else ex.get("ordinary_word_space_em",ex.get("word_space_em",0))}'
