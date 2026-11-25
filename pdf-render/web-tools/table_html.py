"""Finite source-bound table presentations, using native cells and ruby."""
import re
from bs4 import BeautifulSoup
from model import Projection,digest
from presentation_slice import slice_inline
from notice_layout import html_lines
from document_html import bound_lines
from semantic_html import add_style,add_class,pt,gap


def new(name='span',raw='',cls=None):
    n=BeautifulSoup('','html.parser').new_tag(name,attrs={'class':cls} if cls else {})
    if raw:n.append(BeautifulSoup(raw,'html.parser'))
    return n


def money(raw,width):
    text=Projection({'html':raw}).text;match=re.fullmatch(r'\s*([0-9]+(?:,[0-9]{3})*)\s*円\s*',text)
    if not match or '<ruby' in raw or not 1<=width<=8:raise ValueError('Money cell needs its exact plain amount')
    out=new(cls='money-value');amount=new(raw=slice_inline(raw,match.start(1),match.end(1)))
    add_style(amount,display='inline-block',width=f'calc(var(--nominal-em) * {width})',text_align='right')
    out.append(amount);out.append(new(raw=slice_inline(raw,match.end(1),len(text))))
    return out


def option_money(markup,options,spec,index):
    from option_columns import render
    from semantic_html import converter
    render(converter(),options,spec)
    soup=BeautifulSoup(markup,'html.parser');raw=str(soup);text=Projection({'html':raw}).text
    match=re.fullmatch(r'([0-9]+(?:,[0-9]{3})*)(円から)(、?)([0-9]+(?:,[0-9]{3})*)(円引いたものを支払う。)',text)
    if not match:raise ValueError('Money option lost its bound structure')
    out=new(cls='money-option')
    for i in range(1,6):
        n=new(raw=slice_inline(raw,match.start(i),match.end(i)) if match.end(i)>match.start(i) else '')
        if i in (1,4):add_style(n,display='inline-block',text_align='right',width=f'calc(var(--nominal-em) * {spec["amount_widths_em"][0 if i==1 else 1]})')
        if i==3:add_style(n,display='inline-block',width='1em')
        out.append(n)
    return str(out)


def cell_roles(cell,spec):
    if 'vertical_align' in spec:add_style(cell,vertical_align=spec['vertical_align'])
    if spec.get('aligned_money'):
        node=money(cell.decode_contents(),spec.get('amount_width_em',3));cell.clear();cell.append(node)
    if spec.get('aligned_duration'):
        raw=cell.decode_contents();text=Projection({'html':raw}).text.strip();match=re.fullmatch(r'(?:(\d+)(分))?(\d+)(秒)',text)
        if not match or cell.find('ruby'):raise ValueError('Duration cell requires exact plain time')
        line=new(cls='duration-value');cell.clear();cell.append(line)
        for i,width in [(1,.7),(2,1),(3,1.2),(4,1)]:
            n=new(raw=slice_inline(raw,match.start(i),match.end(i)) if match[i] else '')
            add_style(n,display='inline-block',width=f'{width}em',text_align='right' if i in (1,3) else 'center');line.append(n)
    if 'body_pt' in spec:add_style(cell,font_size=f'calc(var(--glyph-point) * {spec["body_pt"]})',line_height=pt(spec['baseline_pt']))
    if 'ruby_intergap_em' in spec:cell['style']+='--ruby-intergap:'+str(spec['ruby_intergap_em'])+'em;'
    if 'line_indents_em' in spec:
        chunks=bound_lines(cell.decode_contents(),spec.get('break_before'));indents=spec['line_indents_em']
        hangs=spec.get('line_hanging_em',[0]*len(chunks));families=spec.get('line_font_families',['body']*len(chunks));before=spec.get('line_before_pt',[0]*len(chunks))
        if any(len(x)!=len(chunks) for x in [indents,hangs,families,before]):raise ValueError('Cell line roles changed count')
        cell.clear()
        for index,(raw,indent,hang,family,space) in enumerate(zip(chunks,indents,hangs,families,before)):
            if spec.get('normalize_line_starts'):
                text=Projection({'html':raw}).text;at=len(text)-len(text.lstrip(' \u3000\t'))
                if at:raw='<span class="source-literal sr-only">'+slice_inline(raw,0,at)+'</span>'+slice_inline(raw,at,len(text))
            n=new('div',raw)
            column=spec.get('line_label_column')
            if column and index in [column['start_line'],*column['continuation_lines']]:
                width=column['width_em'];indent=0;hang=width
                if index==column['start_line']:
                    text=Projection({'html':raw}).text;at=len(text)-len(text.lstrip());end=at+len(column['label'])
                    if text[at:end]!=column['label']:raise ValueError('Cell label column changed')
                    label=new(raw=slice_inline(raw,0,end));add_style(label,display='inline-block',width=f'calc(var(--nominal-em) * {width})')
                    n.clear();n.append(label);n.append(new(raw=slice_inline(raw,end,len(text))))
                else:
                    spacer=new();add_style(spacer,display='inline-block',width=f'calc(var(--nominal-em) * {width})');spacer['aria-hidden']='true';n.insert(0,spacer)
            add_style(n,padding_left=f'calc(var(--nominal-em) * {indent+hang})',text_indent=f'calc(var(--nominal-em) * {-hang})',margin_top=gap(space),font_family={'body':'Body','notice_body':'Body','heading':'Heading'}[family]);cell.append(n)
    if 'document_bullet' in spec:
        from notice_html import line_style
        line_style(BeautifulSoup('','html.parser'),cell,{'document_bullet':spec['document_bullet']})


def rule_css(rule,gap_width=1.2):
    kind=rule.get('style','single');width=rule.get('width_pt',.4)
    if kind=='none':return '0 none currentColor'
    if kind=='double':width=2*width+rule.get('double_gap_pt',gap_width)
    return f'{pt(width)} '+{'single':'solid','double':'double','dashed':'dashed'}[kind]+' currentColor'


def extra(table,spec,grid,ncols):
    rows=[n for n in table.find_all('tr') if n.find_parent('table') is table];nrows=len(rows);rules=spec.get('rules');style=spec.get('rule_style','grid')
    group_starts={r for r,c,cell in grid if cell.get('scope')=='rowgroup'}
    if spec.get('caption_style'):
        caption=table.find('caption',recursive=False);bound=spec['caption_style']
        if caption is None or Projection({'html':str(caption)}).text.strip()!=bound['text']:raise ValueError('Native table caption changed')
        add_style(caption,text_align=bound['align'],font_size=f'calc(var(--glyph-point) * {bound["font_pt"]})',line_height=pt(bound['baseline_pt']),padding_top=gap(bound.get('before_pt',0)),padding_bottom=gap(bound.get('after_pt',6)),font_family='Heading' if bound.get('font_family')=='heading' else 'Body')
        if bound.get('boxed'):
            box=new(raw=caption.decode_contents());add_style(box,display='inline-block',border=f'{pt(.5)} solid currentColor',padding=pt(6));caption.clear();caption.append(box)
    if style not in ('grid','row_groups','bands_with_stub','outer_box'):raise ValueError('Unsupported table rules')
    if rules:
        from rules import table_settings
        table_settings(rules,nrows,ncols)
    for r,c,cell in grid:
        rs=int(cell.get('rowspan',1));cs=int(cell.get('colspan',1))
        if rules:
            for edge,axis,index in [('top','horizontal',r),('bottom','horizontal',r+rs),('left','vertical',c),('right','vertical',c+cs)]:
                rule=next((x for x in rules.get(axis,[]) if x['boundary']==index),rules.get('default',{'style':'single','width_pt':.4}))
                add_style(cell,**{'border_'+edge:rule_css(rule,rules.get('double_gap_pt',1.2))})
        elif style!='grid':
            for edge in ('top','bottom','left','right'):
                show=(edge=='top' and r==0) or (edge=='bottom' and r+rs==nrows)
                if style=='bands_with_stub':show=edge in ('top','bottom') or (edge=='right' and c+cs==1) or (edge=='left' and c==1)
                if style=='outer_box':show=show or edge=='left' and c==0 or edge=='right' and c+cs==ncols
                if style=='row_groups':show=show or edge=='top' and r in group_starts
                add_style(cell,**{'border_'+edge:rule_css({'style':'single' if show else 'none','width_pt':.58})})
        if spec.get('vertical_align'):add_style(cell,vertical_align=spec['vertical_align'])
        if c==0 and spec.get('stub_align'):add_style(cell,text_align=spec['stub_align'])
        for sep in spec.get('row_separations',[]):
            if sep['row']==r:add_style(cell,padding_top=pt(sep['above_pt']),padding_bottom=pt(sep['below_pt']))
        if spec.get('circled_bullet_gap_em'):
            for textnode in list(cell.find_all(string=True)):
                if textnode.parent.name in ('rt','rp'):continue
                pieces=re.split('([①②③④⑤⑥])',str(textnode));out=[]
                for token in pieces:
                    if re.fullmatch('[①②③④⑤⑥]',token):
                        span=new(raw=token);add_style(span,margin_right=f'{spec["circled_bullet_gap_em"]}em');out.append(span)
                    else:out.append(token)
                if len(pieces)>1:textnode.replace_with(*out)
        vertical=[v for v in spec.get('vertical_cells',[]) if (v['row'],v['column'])==(r,c)]
        if vertical:
            if len(vertical)!=1 or Projection({'html':str(cell)}).text.strip()!=vertical[0]['text'] or cell.find('ruby'):raise ValueError('Stale vertical table label')
            box=new('span',cell.decode_contents(),'vertical-cell-label');cell.clear();cell.append(box)
        date=[v for v in spec.get('date_cells',[]) if (v['row'],v['column'])==(r,c)]
        if date:
            if len(date)!=1 or Projection({'html':str(cell)}).text.strip()!=date[0]['text']:raise ValueError('Stale date cell')
            chunks=html_lines(cell.decode_contents());cell.clear()
            for raw in chunks:
                text=Projection({'html':raw}).text;match=re.fullmatch(r'(\d{1,2})(日)([（(])([月火水木金土日])([）)])',text)
                if not match:raise ValueError('Unknown date anchor structure')
                line=new('div',cls='anchored-date')
                for i in range(1,6):line.append(new(raw=slice_inline(raw,match.start(i),match.end(i))))
                cell.append(line)
        if spec.get('cell_flow')=='sale_prices' and c>0:
            chunks=bound_lines(cell.decode_contents());raw=''.join(chunks);text=Projection({'html':raw}).text
            if len(cell.find_all(['s','del']))!=1 or text.count('⇒')!=1:raise ValueError('Unknown sale-price structure')
            at=text.index('⇒');old=[];cursor=0
            for chunk in chunks:
                length=len(Projection({'html':chunk}).text)
                if cursor>=at:break
                old.append(slice_inline(chunk,0,min(length,at-cursor)))
                cursor+=length
            cell.clear()
            for line in old:cell.append(new('div',line))
            lower=new('div',slice_inline(raw,at,len(text)));add_style(lower,font_size=f'calc(var(--glyph-point) * {spec["discount_pt"]})',line_height='1.4');cell.append(lower)
        if spec.get('diagonal_header') and (r,c)==(0,0):
            chunks=html_lines(cell.decode_contents())
            if len(chunks)!=2 or cs<2:raise ValueError('Diagonal header requires two spanning labels')
            cell.clear();add_class(cell,'diagonal-header');cell.append(new('div',chunks[0]));cell.append(new('div',chunks[1]))
            for node in cell.select('[style]'):
                node['style']=';'.join(p for p in node['style'].split(';') if not p.strip().startswith('float:'))
    for k in ('vertical_cells','date_cells'):
        if any(not any((e['row'],e['column'])==(r,c) for r,c,_ in grid) for e in spec.get(k,[])):raise ValueError('Unused '+k+' binding')
    if spec.get('cell_flow')=='contact_list':
        if ncols!=2 or any(int(cell.get('rowspan',1))!=1 or int(cell.get('colspan',1))!=1 for _,_,cell in grid):raise ValueError('Invalid contact table')
        add_class(table,'contact-list')
        # Source contact rows flow label + one em + value as a paragraph,
        # including full-width continuation lines, rather than two columns.
        values=[(grid[r*2][2].decode_contents(),grid[r*2+1][2].decode_contents()) for r in range(nrows)]
        table.clear()
        for r,(label,value) in enumerate(values):
            row=new('tr');cell=new('td');row.append(cell);table.append(row)
            lead=new('strong',label);cell.append(lead);cell.append(new('span',' ','notice-contact-gap'));cell.append(BeautifulSoup(value,'html.parser'))
            add_style(cell,text_align='left',border='0',padding=f'{pt(3 if r==0 else 0)} {pt(8)} {pt(3 if r==nrows-1 else 0)}')
        add_style(table,border=f'{pt(.45)} solid currentColor',border_collapse='separate',border_spacing='0',table_layout='auto')
    elif spec.get('cell_flow')=='notice_panels':
        if ncols!=2 or any(int(cell.get('rowspan',1))!=1 or int(cell.get('colspan',1))!=1 for _,_,cell in grid):raise ValueError('Invalid notice panels')
        from section_layout import flow_lines
        from document_html import select_line
        from inline_layout import prepare_inline
        add_class(table,'notice-panels');table['style']+='--panel-gap:'+pt(spec.get('panel_gap_pt',10))+';'
        for r,c,cell in grid:
            add_style(cell,padding='0',border='0')
            nodes=[n for n in flow_lines(list(cell.children)) if Projection({'html':str(n)}).text.strip()]
            if not nodes or nodes[0].name!='center' or nodes[-1].name!='div':raise ValueError('Panel title/contact changed')
            cell.clear();panel=new('div',cls='notice-panel')
            for n in nodes:panel.append(n)
            cell.append(panel);add_style(panel,border_radius=pt(spec.get('panel_radius_pt',12)),padding=pt(spec.get('panel_padding_pt',9)))
            add_style(nodes[0],text_align='center',font_size=f'calc(var(--glyph-point) * {spec.get("panel_title_pt",13)})',margin_bottom=gap(6))
            add_style(nodes[-1],text_align='right',margin_top='auto',padding_top=gap(5))
            for binding in spec.get('panel_lines',[]):
                if (binding['row'],binding['column'])!=(r,c):continue
                node=select_line(panel,binding['text'],space_equivalent=True);raw=node.decode_contents()
                if binding.get('keep_words'):
                    # Typography spans may divide a word; source projection is
                    # still exact and balanced inline slicing keeps ruby whole.
                    for word in binding['keep_words']:
                        text=Projection({'html':raw}).text
                        if text.count(word)!=1:raise ValueError('Panel word binding changed')
                        at=text.index(word);end=at+len(word)
                        raw=(slice_inline(raw,0,at) if at else '')+'<span data-bounded-word="true">'+slice_inline(raw,at,end)+'</span>'+(slice_inline(raw,end,len(text)) if end<len(text) else '')
                if binding.get('continuation_before'):
                    chunks=bound_lines(raw,binding['continuation_before']);raw=chunks[0]+'<br><span style="display:inline-block;width:6.35em" aria-hidden="true"></span>'+chunks[1]
                node.clear();node.append(BeautifulSoup(raw,'html.parser'))
            for node in panel.find_all('p',recursive=False):
                text=Projection({'html':str(node)}).text.strip();label='【見学できる人の数】'
                add_style(node,padding_left='1em',text_indent='-1em')
                if text.startswith(label):
                    raw=node.decode_contents();plain=Projection({'html':raw}).text;at=plain.index(label)+len(label)
                    node.clear();node.append(BeautifulSoup(slice_inline(raw,0,at),'html.parser'))
                    continuation=new('div',slice_inline(raw,at,len(plain)));add_style(continuation,text_indent='0');node.append(continuation)
                elif not text.startswith('【'):add_style(node,text_indent='0')
    elif spec.get('cell_flow')=='transit_routes':
        from diagram_html import transit_table
        transit_table(table,spec,grid,ncols)
    elif spec.get('cell_flow') not in (None,'sale_prices'):raise ValueError('Unsupported table cell flow')
    if spec.get('column_groups'):
        groups=spec['column_groups'];gap_fraction=spec.get('group_gap_fraction',.04)
        if [c for group in groups for c in group]!=list(range(ncols)) or any(int(cell.get('rowspan',1))!=1 or int(cell.get('colspan',1))!=1 for _,_,cell in grid):raise ValueError('Invalid parallel table groups')
        add_class(table,'parallel-grids')
        # Empty spacer cells retain the canonical row order while exposing the
        # same two side-by-side grids. They carry no content or answer binding.
        cols=table.select('colgroup col');weights=spec.get('column_weights',[1]*ncols);part=(1-gap_fraction*(len(groups)-1))/len(groups)
        for group in groups:
            total=sum(weights[c] for c in group)
            for c in group:add_style(cols[c],width=f'{part*weights[c]/total*100}%')
        for group in groups[:-1]:
            boundary=group[-1]
            spacer=new('col');add_style(spacer,width=f'{gap_fraction*100}%');cols[boundary].insert_after(spacer)
            for r,c,cell in grid:
                if c==boundary:
                    blank=new('td',cls='table-group-gap');blank['aria-hidden']='true';cell.insert_after(blank)
