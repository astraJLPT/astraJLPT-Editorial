"""Bound Latin and content-digit roles, separate from numbered furniture."""
import re
from functools import lru_cache
from pathlib import Path
from bs4 import BeautifulSoup
from fontTools.ttLib import TTFont
from numeral_roles import exceptions


def heading_digits(soup, m, nodes=None):
    """Apply the native instruction numeral role, including its width advance."""
    from font_geometry import role_metrics
    from historical_html import enabled
    from historical_typography import instruction_digit_presentation
    old = enabled(m)
    for node in soup.select('[data-instruction-digit]') if nodes is None else nodes:
        bounded = node['data-instruction-digit'] == 'selector'
        role, extra = instruction_digit_presentation(m['style'], bounded) if old else ('instruction_numeral' if m['style'].get('approved_administrative_numerals') else 'instruction_latin', 1)
        spec = m['style']['font_roles'][role]
        family = 'OldSelector' if role == 'historical_instruction_digit' else 'AdministrativeNumerals' if role=='instruction_numeral' else 'InstructionLatin'
        scale = spec.get('horizontal_scale', 1) * extra
        size = spec.get('scale', 1)
        text = node.get_text()
        display = text.translate(str.maketrans('０１２３４５６７８９','0123456789')) if (old and bounded) or role=='instruction_numeral' else text
        fullwidth = display in '１２３４'
        metric = role_metrics(m, role, display) if not fullwidth else None
        node.clear()
        node['data-font-role'] = role
        node['data-horizontal-scale'] = str(scale)
        # The label's quarter-em gap is independent of the numeral face/width.
        node['class'] = ['instruction-digit'] + (['heading-number'] if 'heading-number' in node.get('class', []) else [])
        line_height = '0' if node['data-instruction-digit'] == 'task' else '1'
        node['style'] = (f'font-family:{family};font-size:calc(var(--nominal-em) * {size});'
                         f'display:inline-block;width:{(.5 if fullwidth else metric["advance"]) * scale}em;'
                         f'text-indent:0;line-height:{line_height};vertical-align:baseline;')
        if node.has_attr('data-selector-last-gap'):node['style']+='margin-right:calc(var(--nominal-em) * .3);'
        glyph = soup.new_tag('span')
        glyph.string = display
        glyph['style'] = f'display:inline-block;transform:scaleX({scale});transform-origin:left;'
        if fullwidth:
            # HeadingChoiceNumber uses a half-em box around a Japanese glyph.
            glyph['style'] += 'font-family:Heading;width:.5em;text-align:center;'
            ink=soup.new_tag('span');ink.string=display
            ink['style']='font-size:calc(var(--nominal-em) * var(--glyph-scale));'
            glyph.clear();glyph.append(ink)
        if display != text:
            literal=soup.new_tag('span',attrs={'class':'source-literal sr-only'});literal.string=text;node.append(literal)
            glyph['class']=['visual-only'];glyph['aria-hidden']='true'
        node.append(glyph)


@lru_cache(maxsize=None)
def advances(path,index):
    with TTFont(path,fontNumber=index) as font:
        cmap=font.getBestCmap();em=font['head'].unitsPerEm
        return {c:font['hmtx'][cmap[ord(c)]][0]/em for c in '0123456789０１２３４５６７８９' if ord(c) in cmap}


def present(soup,m,context,target):
    if context=='heading':
        heading_digits(soup,m)
        return
    style=m['style'];roles=style['font_roles'];base=(target or '').split('/')[0]
    identifiers={s['text'] for binding in style.get('inline_presentations',{}).values() for s in binding.get('literal_identifiers',[])}
    for latin in soup.select('.tex-latin'):
        if latin.get_text() in identifiers:
            latin['class'].append('literal-identifier');latin['style']=latin.get('style','')+'font-family:ContactLatin,Body,serif;white-space:nowrap;'
    notice=base in style.get('block_styles',{})
    if not notice and base:
        notice=any(i['id']==base and i.get('type')=='notice' for s in m['document']['sections'] for i in s['items'])
    if notice and 'notice_latin' in roles:
        for latin in soup.select('.tex-latin:not(.literal-identifier)'):latin['style']=latin.get('style','')+'font-family:NoticeLatin,Body,serif;'
    default='option_content_numeral' if context=='option' or '/options/' in (target or '') else 'notice_numeral' if notice else 'body_numeral'
    if '_web_numeral_exceptions' not in m:m['_web_numeral_exceptions']=exceptions(m)
    slot=target if '/options/' in (target or '') else (target or '')+('/stem' if context=='question' else '/content')
    role=m['_web_numeral_exceptions'].get(slot,{}).get('role',default)
    if role not in roles:return
    spec=roles[role];family={'body_numeral':'BodyNumeral','option_content_numeral':'OptionNumeral','notice_numeral':'NoticeNumeral'}[role]
    path=Path(spec.get('path',style['fonts'].get(spec.get('source',''),'')))
    path=__import__('package_paths').resource(path)
    scale=spec.get('horizontal_scale',1);widths=advances(str(path),spec.get('font_index',0))
    features=','.join('"'+f+'"' for f in spec.get('features',[])) or 'normal'
    if scale!=1 and spec.get('features'):raise ValueError('Scaled content numerals need explicit feature advances')
    for node in list(soup.find_all(string=True)):
        if any(p.name in ('rt','rp') or p.has_attr('data-workbook-font') or set(p.get('class',[]))&{'source-literal','visual-only','content-digits','answer-slot','star-slot','cloze-slot','literal-identifier'} for p in node.parents):continue
        parts=re.split('([0-9０-９]+)',str(node))
        if len(parts)==1:continue
        result=[]
        for part in parts:
            if not part:continue
            if not re.fullmatch('[0-9０-９]+',part):result.append(part);continue
            outer=soup.new_tag('span',attrs={'class':'content-digits','data-font-role':role})
            inherited=any('tex-latin' in p.get('class',[]) for p in node.parents)
            outer['style']='font-family:'+family+';font-size:'+('1em' if inherited else 'calc(1em / var(--glyph-scale))')+';font-feature-settings:'+features+';'
            if scale!=1:
                outer['style']+='display:inline-block;width:'+str(sum(widths[c] for c in part)*scale)+'em;'
                inner=soup.new_tag('span');inner['style']='display:inline-block;transform-origin:left;transform:scaleX('+str(scale)+');';inner.string=part;outer.append(inner)
            else:outer.string=part
            result.append(outer)
        node.replace_with(*result)
