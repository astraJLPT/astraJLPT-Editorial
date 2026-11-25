"""D19's source-positioned duration labels, shared ink and advance constants."""
import re
from bs4 import BeautifulSoup
from model import Projection
from workbook_typography import macro

FONT_ID = 'gothicbbb_pr6_medium'
INK_SCALE = .775
FIRST_ADVANCE = .4993
LAST_ADVANCE = .7493
SINGLE_ADVANCE = 1.0007
FONT_PT = 14
INK_OFFSET = .1125


def tex(conv, raw):
    soup = BeautifulSoup(raw, 'html.parser')
    text = Projection({'html': raw}).text.strip()
    match = re.fullmatch(r'([0-9]{1,2})分', text)
    if not match:
        raise ValueError('D19 duration must retain its numeric label and 分')
    digits = match[1]
    name = macro(FONT_ID)
    ruby = soup.find('ruby')
    suffix = str(ruby) if ruby else '分'
    if Projection({'html': suffix}).text != '分':
        raise ValueError('Unexpected duration ruby')
    cells = []
    for index, char in enumerate(digits):
        advance = SINGLE_ADVANCE if len(digits) == 1 else FIRST_ADVANCE if index == 0 else LAST_ADVANCE
        glyph = format(ord(char) + 0xFEE0, 'X')
        cells.append(r'\makebox[' + str(advance) + r'em][l]{\hspace{' + str(INK_OFFSET) + r'em}\scalebox{'
                     + str(INK_SCALE) + r'}[1]{\ltjalchar"' + glyph + r'\relax}}')
    previous = getattr(conv, 'numeric_role', None)
    conv.numeric_role = None
    try:
        tail = ''.join(conv.node(n, 'cell') for n in BeautifulSoup(suffix, 'html.parser').children)
    finally:
        conv.numeric_role = previous
    conv.features.append({'kind':'approved_duration_composition','text':text,'ink_scale':INK_SCALE,
                          'digit_advances_em':[SINGLE_ADVANCE] if len(digits)==1 else [FIRST_ADVANCE,LAST_ADVANCE]})
    # The source measurements are glyph-origin advances. Carry the common
    # digit ink offset into the unit origin rather than shortening the final gap.
    return '{\\' + name + 'Latin\\' + name + 'Japanese\\fontsize{14}{20}\\selectfont\\ltjsetparameter{xkanjiskip=0pt}' + ''.join(cells) + r'\hspace{'+str(INK_OFFSET)+'em}'+tail + '}'


def html(duration):
    soup = BeautifulSoup(str(duration), 'html.parser')
    text = Projection({'html': str(duration)}).text.strip()
    match = re.fullmatch(r'([0-9]{1,2})分', text)
    if not match:
        raise ValueError('D19 HTML duration label changed')
    digits = match[1]
    ruby = duration.find('ruby')
    suffix = str(ruby) if ruby else '分'
    duration.clear()
    duration['data-font-role'] = 'workbook_' + FONT_ID
    duration['data-duration-ink-scale'] = str(INK_SCALE)
    duration['style'] = duration.get('style','') + ';font-family:' + macro(FONT_ID) + ';font-size:calc(var(--point) * 14);white-space:nowrap;'
    literal = soup.new_tag('span', attrs={'class':'source-literal sr-only'})
    literal.string = digits
    duration.append(literal)
    for index, char in enumerate(digits):
        advance = SINGLE_ADVANCE if len(digits)==1 else FIRST_ADVANCE if index==0 else LAST_ADVANCE
        cell = soup.new_tag('span', attrs={'class':'visual-only','aria-hidden':'true','data-advance-em':str(advance)})
        cell['style'] = f'display:inline-block;width:{advance}em;text-indent:0;line-height:1;'
        ink = soup.new_tag('span')
        ink.string = chr(ord(char)+0xFEE0)
        ink['style'] = f'display:inline-block;margin-left:{INK_OFFSET}em;transform:scaleX({INK_SCALE});transform-origin:left;'
        cell.append(ink)
        duration.append(cell)
    unit=soup.new_tag('span',attrs={'class':'duration-unit','style':f'margin-left:{INK_OFFSET}em;'})
    for node in list(BeautifulSoup(suffix, 'html.parser').contents):unit.append(node)
    duration.append(unit)
