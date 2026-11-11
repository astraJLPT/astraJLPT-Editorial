"""Native vertical reading and exact bound horizontal frame geometry."""
import re
from bs4 import BeautifulSoup
from model import digest,Projection
from semantic_html import add_style,add_class,pt,gap,wrap_tail,reject_unknown


def vertical(soup,source,meta,style):
    header=meta.get('vertical_header')
    if header:
        if digest(source)!=header['content_sha256'] or not isinstance(source,str) or not source.startswith(header['prefix']):raise ValueError('Stale vertical header')
        label,title=header['prefix'].strip().split('\n')
        from document_html import select_line
        lead=select_line(soup,label);following=select_line(soup,title)
        add_class(lead,'passage-label');add_class(following,'passage-label');add_class(lead,'paired-label')
        add_style(lead,display='inline-block',margin_right='.6em');add_style(following,display='inline-block')
    elif meta.get('vertical_paired_label'):
        from paired_passages import parameters
        spec=meta['vertical_paired_label']
        label=spec['label'];first=next((n for n in soup.contents if getattr(n,'name',None) or str(n).strip()),None)
        original=BeautifulSoup(source['html'],'html.parser').find('p')if isinstance(source,dict)else None
        if digest(source)!=spec['content_sha256'] or label not in ['A','B'] or original is None or original.get_text()!=label or original.find(True) or first is None or first.name!='p' or first.get_text()!=label:raise ValueError('Invalid native vertical paired label')
        add_class(first,'passage-label');add_class(first,'paired-label');cfg=parameters(style.get('paired_passages'))
        add_style(first,font_family='PairedLabel',margin_top=gap(cfg['first_label_before_pt']if label=='A'else cfg['next_label_before_pt']))
    elif not soup.select_one('.passage-label'):
        from document_html import select_line
        label=Projection(source).text.split('\n')[0].strip()
        if not re.fullmatch(r'[（(][0-9０-９]+[）)]',label):raise ValueError('Vertical body requires its horizontal source label')
        add_class(select_line(soup,label),'passage-label')
    frame=wrap_tail(soup,'vertical-frame')
    # Native TeX unwraps the copied source containers inside vertical passages.
    for wrapper in list(frame.find_all(['center','div'])):wrapper.unwrap()
    for br in frame.select('[data-vertical-soft-break]'):
        if br.get('data-vertical-soft-break')!='true':raise ValueError('Invalid vertical line marker')
        add_class(br,'source-joined-break')
    size=style.get('vertical_body_pt',style['body_pt']);padding=style.get('vertical_frame_padding_em',.25)
    if meta.get('vertical_frame'):
        spec=meta['vertical_frame']
        if digest(source)!=spec['content_sha256'] or not .25<=spec['padding_em']<=2:raise ValueError('Stale or invalid vertical frame')
        padding=spec['padding_em']
    # CSS already centres the physical frame with auto horizontal margins.
    # Keep the native print-layout offset in the PDF path; applying it to the
    # independently laid-out browser frame shifts it away from that centre.
    add_style(frame,font_size=f'calc(var(--glyph-point) * {size})',height=f'calc(var(--glyph-point) * {size*style["vertical_extent_em"]})',line_height=f'calc(var(--glyph-point) * {size*style.get("vertical_column_pitch_em",1.8)} * var(--line-preset) * var(--line-adjust))',padding=pt(size*padding),border=f'{pt(.4)} solid currentColor',margin='auto',position='relative')
    frame['style']+='--nominal-em:'+pt(size)+';'
    for p in frame.find_all('p',recursive=False):
        # TeX's vertical vbox reserves one glyph at its outer columns, with
        # baseline pitch only between columns. CSS line boxes include half
        # leading on both edges; remove that surplus without moving the ink.
        add_style(p,text_indent=f'calc(var(--glyph-point) * {size})',margin='0',
                  margin_left='calc((1em - 1lh) / 2)',margin_right='calc((1em - 1lh) / 2)')
    outer=soup.new_tag('div',attrs={'class':'vertical-scroll','tabindex':'0','role':'region','aria-label':'Vertical passage'})
    frame.wrap(outer);add_style(outer,margin_top=gap(style.get('paragraph_skip_pt',0)),margin_bottom=gap(style.get('vertical_after_pt',0)))


def pins(soup,frame,spec):
    from notice_pins import decorate
    decorate('',spec)
    add_style(frame,position='relative')
    for corner in ('top-left','top-right','bottom-left','bottom-right'):
        node=soup.new_tag('i',attrs={'class':'frame-pin '+corner,'aria-hidden':'true'})
        node['style']='--pin-size:'+pt(spec['radius_pdf_pt']*2*72.27/72)+';--pin-inset:'+pt(spec['inset_pt'])+';--pin-gray:'+str((1-spec['fill_gray'])*100)+'%;'
        frame.append(node)


def horizontal(soup,source,spec):
    from horizontal_frames import apply
    apply(r'\begin{NoticeFrame}\end{NoticeFrame}',source,spec)
    frames=soup.select('.notice-frame,.document-section')
    if len(frames)!=1:raise ValueError('Horizontal geometry needs exactly one frame')
    for side in ('left','right','top','bottom'):add_style(frames[0],**{'padding_'+side:pt(spec[side+'_pt'])})
    if spec.get('pins'):pins(soup,frames[0],spec['pins'])
