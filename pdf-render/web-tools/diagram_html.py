"""Native HTML diagrams from the renderer's exact semantic structures."""
import math
from bs4 import BeautifulSoup
from model import Projection
from semantic_html import add_style,pt,gap
from tex_html import render_inline


def decision_value(value,source,binding):
    from decision_trees import prepare
    return prepare(value,binding,source)


def present_decision(soup,m,binding):
    from decision_trees import validate
    original=soup.select_one('[data-native-decision-tree]')
    if original is None:raise ValueError('Missing native decision list')
    # Validate the unpresented source separately; typography spans must never
    # replace the exact authored list hash as the source authority.
    item=next(i for s in m['document']['sections'] for i in s['items'] if m['layout']['items'][i['id']].get('decision_tree')==binding)
    canonical=BeautifulSoup(item['content']['html'],'html.parser')
    from model import digest
    roots=[n for n in canonical.find_all('ul') if digest({'html':str(n)})==binding['list_sha256']]
    if len(roots)!=1:raise ValueError('Decision list hash is ambiguous')
    levels,outcomes=validate(roots[0],binding)
    inset=binding['inset_fraction'];heights=binding['level_heights_pt'];pitch=binding['level_gap_pt']
    starts=[sum(heights[:j])+pitch*j for j in range(len(levels))]
    terminal=starts[-1]+heights[-1]+binding['outcome_gap_pt']+binding['outcome_height_pt']/2
    leaves=[.13+inset*j for j in range(len(levels))]+[1-inset/2-.12]
    region=soup.new_tag('div',attrs={'class':'native-decision-diagram visual-only','aria-hidden':'true'})
    # Keep the source-width chart readable when the surrounding prose reflows.
    # Round the minimum down to whole TeX points to allow CSS border rounding.
    style=m['style'];frame=style.get('block_styles',{}).get(item['id'],{})
    margins=style['margins_mm']
    native_width=(210-margins['left']-margins['right'])*72.27/25.4
    native_width-=2*(frame.get('frame_padding_pt',8)+frame.get('frame_rule',{}).get('width_pt',.45))
    add_style(region,position='relative',min_width=pt(math.floor(native_width)),height=pt(terminal+binding['outcome_height_pt']/2),margin_top=gap(binding['before_pt']),margin_bottom=gap(binding['after_pt']),font_size=f'calc(var(--glyph-point) * {binding["body_pt"]})',line_height=pt(binding['baseline_pt']))
    def node(cls,raw,**css):
        element=soup.new_tag('div',attrs={'class':cls})
        if raw:element.append(BeautifulSoup(render_inline({'html':raw},m,'body'),'html.parser'))
        add_style(element,position='absolute',box_sizing='border-box',**css);region.append(element);return element
    for j,(level,y,height) in enumerate(zip(levels,starts,heights)):
        left=inset*j;width=1-left;middle=y+height/2+(5 if level['prompt'] else 0)
        node('decision-level','',left=f'{left*100}%',top=pt(y),width=f'{width*100}%',height=pt(height),border=f'{pt(.45)} solid currentColor')
        if level['prompt']:node('decision-prompt',''.join(map(str,level['prompt'])),left=f'{(left+width/2)*100}%',top=pt(y+9),width=f'calc({width*100}% - {pt(12)})',transform='translate(-50%,-50%)',text_align='center')
        for c,label in enumerate(level['labels']):
            node('decision-label',''.join(map(str,label)),left=f'{(left+width*(.25+.5*c))*100}%',top=pt(middle),width=f'calc({width*50}% - {pt(12)})',transform='translate(-50%,-50%)',text_align='left')
            last=c==0 or j==len(levels)-1;x=leaves[j if c==0 else -1] if last else left+width*.6
            bottom=terminal-binding['outcome_height_pt']/2 if last else starts[j+1]
            line=node('decision-connector','',left=f'{x*100}%',top=pt(y+height),height=pt(bottom-y-height),border_left=f'{pt(.5)} '+('solid' if c==0 else 'dashed')+' currentColor')
            node('decision-branch','ab'[c],left=f'{x*100}%',top=pt(y+height+6),transform='translate(-100%,-50%)',padding_right=pt(2))
    for index,(x,label) in enumerate(zip(leaves,outcomes)):
        leaf=node('decision-outcome',''.join(map(str,label)),left=f'{x*100}%',top=pt(terminal),min_height=pt(binding['outcome_height_pt']),padding=pt(3),border=f'{pt(.45)} solid currentColor',transform='translate(-50%,-50%)',display='flex',align_items='center',text_align='center',white_space='nowrap')
        leaf['data-outcome-index']=str(index)
    original['class']=[*original.get('class',[]),'source-literal','sr-only']
    scroll=soup.new_tag('div',attrs={'class':'decision-scroll','tabindex':'0','role':'region','aria-label':'Decision diagram'})
    add_style(scroll,overflow_x='auto',max_width='100%')
    scroll.append(region);original.insert_after(scroll)


def transit_table(table,spec,grid,ncols):
    from table_html import new
    from document_html import bound_lines
    from presentation_slice import slice_inline
    if ncols!=5 or len(grid)%6:raise ValueError('Transit routes require five-cell rows and spanning headers')
    weights=spec.get('column_weights',[22,17,24,17,20])
    table['class']=[*table.get('class',[]),'transit-routes']
    for r,c,cell in grid:
        row=cell.parent
        if r%2==0:
            if c!=0 or cell.name!='th' or int(cell.get('colspan',1))!=5:raise ValueError('Transit heading must span five columns')
            add_style(row,display='block',border_top=f'{pt(.65)} dashed currentColor',padding_top=pt(9),margin_top=pt(10) if r else '0',margin_bottom=pt(5))
            add_style(cell,display='block',border='0',padding='0',text_align='left',background='none')
        else:
            # Intrinsic track minima keep ruby station names and durations
            # inside their cells on narrow readers; the existing wrapper can
            # pan the diagram instead of letting labels cross connectors.
            add_style(row,display='grid',grid_template_columns=' '.join(f'minmax(max-content,{w}fr)' for w in weights),align_items='center')
            add_style(cell,display='block',padding=pt(4),text_align='center',box_sizing='border-box',border='0')
            if c in (0,2,4):
                if '→' in Projection({'html':str(cell)}).text:raise ValueError('Transit station contains a connector')
                # Centre one normal-flow text box. Making ruby, bare text and
                # <br> siblings into flex items destroys the station's lines.
                label=new('span',cls='transit-station-label')
                for child in list(cell.contents):label.append(child.extract())
                cell.append(label);add_style(label,white_space='nowrap')
                add_style(cell,min_height=pt(67),border=f'{pt(.45)} solid currentColor',background='color-mix(in srgb,currentColor 18%,var(--paper))',display='flex',align_items='center',justify_content='center')
            else:
                raw=cell.decode_contents();chunks=bound_lines(raw)
                if len(chunks)!=2:raise ValueError('Transit leg must have two lines')
                upper,lower=[Projection({'html':x}).text for x in chunks]
                if not upper.lstrip().startswith('→') or not lower.rstrip().endswith('→') or upper.count('→')+lower.count('→')!=2:raise ValueError('Transit endpoints changed')
                a=upper.index('→');z=lower.rindex('→')
                cell.clear();cell.append(new(raw=slice_inline(chunks[0],0,a+1),cls='source-literal sr-only'))
                mode=new('div',slice_inline(chunks[0],a+1,len(upper)));duration=new('div',slice_inline(chunks[1],0,z))
                if spec.get('approved_duration')=='D19':
                    from workbook_duration import html as duration_html
                    duration_html(duration)
                add_style(mode,margin_bottom=pt(14));add_style(duration,margin_top=pt(14));cell.append(mode)
                connector=new('div');add_style(connector,border_top=f'{pt(3.5)} solid color-mix(in srgb,currentColor 55%,var(--paper))');cell.append(connector);cell.append(duration)
                cell.append(new(raw=slice_inline(chunks[1],z,len(lower)),cls='source-literal sr-only'))
    for cols in table.find_all('colgroup'):cols.decompose()
    add_style(table,display='block',width='100%',min_width='max-content')
