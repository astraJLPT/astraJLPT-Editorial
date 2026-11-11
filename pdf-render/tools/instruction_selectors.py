"""Bound four-choice administrative selectors; never general dot replacement."""
import re
from bs4 import BeautifulSoup,NavigableString

SPACE=r'[ \u3000\t\r\n]*'
SEQUENCE=SPACE.join([r'[1１]',r'[·•・]',r'[2２]',r'[·•・]',r'[3３]',r'[·•・]',r'[4４]'])
PATTERN=re.compile(SEQUENCE+r'(?:'+SPACE+r'から)?')
FULLWIDTH=str.maketrans('1234','１２３４')
ASCII=str.maketrans('１２３４','1234')

def prepare(soup):
    found=[]
    # Inline capture wrappers can split a selector into several text nodes.
    # Recompute after each atom so offsets never refer to replaced nodes. Ruby
    # and already prepared atoms are hard boundaries, not searchable text.
    while True:
        text='';nodes=[]
        for node in soup.find_all(string=True):
            if any(p.name in ('ruby','rt','rp','script','style') or p.has_attr('data-choice-selector') for p in node.parents):
                text+='\uffff';continue
            start=len(text);text+=str(node);nodes.append((start,len(text),node))
        match=PATTERN.search(text)
        if not match:break
        selected=[(a,b,n) for a,b,n in nodes if a<match.end() and b>match.start()]
        atom=soup.new_tag('span',attrs={'data-choice-selector':'four'});atom.string=match[0]
        for j,(a,b,node) in enumerate(selected):
            raw=str(node);left=max(0,match.start()-a);right=min(b-a,match.end()-a)
            parts=[NavigableString(raw[:left])]
            if j==0:parts.append(atom)
            parts.append(NavigableString(raw[right:]));node.replace_with(*parts)
        found.append(match[0])
    return found

def parts(text):
    if not PATTERN.fullmatch(text):raise ValueError('Invalid prepared instruction selector')
    digits=re.findall(r'[1-4１-４]',text)
    return digits,re.search(SPACE+r'から$',text)

def resolve(model):
    """Scoped UARS-backed role; inherited paper fonts/choice roles stay intact."""
    from era_registry import for_unit
    if for_unit(model['unit']).GENERATION=='historical-1991-2009' or model['unit'][:2] not in ('N4','N5'):return
    style=model['style'];horizontal=style.get('heading_horizontal_scale',1)
    style['font_roles']['instruction_selector']={
        'path':'fonts_official/A-OTF-GothicMB101Pr6N-Bold.otf',
        'sha256':'cf33366000ee2314947c0fae2d25798c71c24fe584c7fa0be615d667642965ea',
        'features':[],'horizontal_scale':1,'scale':1,'bold_same_face':True,
        'selection_status':'Modern GothicMB101 Bold substitute for approved FutoGoB101-Bold selector glyphs; exact legacy font identity not claimed'}
    # UARS N4 has nominal full-em cells; the N5 witnesses range .9296–.9993
    # em after justification. Use .96 em at the shared un-justified boundary.
    advance=1.0 if model['unit'].startswith('N4') else .96
    style['instruction_selector']={'role':'instruction_selector','cell_em':advance/horizontal,
        'digit_horizontal_scale':1,'suffix_gap_em':0,'display_digits':'fullwidth',
        'basis':'2018 official N4V p3; N5V p3,p5 and N5G p6; separator and digit advance calibrated independently from ink'}

def tex(conv,node):
    text=node.get_text();digits,suffix=parts(text)
    if node.find():raise ValueError('Selector must remain an exact text atom')
    cfg=getattr(conv,'selector_presentation',None)
    if cfg:
        def cell(char,digit=False):
            scale=cfg.get('digit_horizontal_scale',1) if digit else cfg.get('dot_horizontal_scale',1)
            glyph=char if char.isascii() else r'\ltjalchar"'+format(ord(char),'X')+r'\relax'
            return r'\makebox['+str(cfg['cell_em'])+r'em][c]{{\SelectorDigits\scalebox{'+str(scale)+r'}[1]{'+glyph+'}}}'
        trans=ASCII if cfg.get('display_digits')=='ascii' else FULLWIDTH
        body=cell('・').join(cell(d.translate(trans),True) for d in digits)
        if suffix:body+=r'\hspace{'+str(cfg['suffix_gap_em'])+r'em}から'
    else:
        gap=getattr(conv,'heading_choice_gap_em',0)
        sep=r'\hspace{'+str(gap/2)+r'em}・\hspace{'+str(gap/2)+'em}' if gap else '・'
        body=sep.join(conv.text(d) for d in digits)
        if suffix:body+=(conv.text(suffix[0][:-2]) if suffix[0]!='から' else r'\hspace{.3em}')+'から'
    conv.features.append({'kind':'instruction_selector','source':text,'display_dot':'・','policy':cfg or 'existing_level_role','canonical_changed':False})
    return r'\mbox{'+body+'}'
