"""HTML projection of the exact shared administrative selector atom."""
import re
from bs4 import NavigableString
from instruction_selectors import prepare,parts
from semantic_html import add_style

def present(soup,m):
    prepare(soup);cfg=m['style'].get('instruction_selector')
    for atom in soup.select('[data-choice-selector]'):
        text=atom.get_text();_,suffix=parts(text);previous=atom.previous_sibling
        atom['class']=['heading-selector','instruction-number-sequence']
        if m['style'].get('heading_selector_boundary') and isinstance(previous,NavigableString) and str(previous).endswith('。'):
            add_style(atom,margin_left='calc(var(--nominal-em) * var(--heading-word-space-em,0))')
        atom.clear()
        if cfg:
            # One source-text layer serves painting, selection and accessibility.
            # Keep the calibrated cell advances separate from authored spaces.
            visual=soup.new_tag('span',attrs={'class':'source-literal selector-source-calibrated','data-font-role':'instruction_selector'})
            add_style(visual,font_family='SelectorDigits',font_size='var(--nominal-em)',white_space='nowrap',text_indent='0')
            for token in re.split(r'([1-4１-４]|[·・]|[ \u3000]+)',text):
                if not token:continue
                if token.isspace():
                    space=soup.new_tag('span',attrs={'class':'selector-source-space'});space.string=token
                    add_style(space,display='inline-block',width='0',line_height='1',white_space='pre');visual.append(space)
                elif token=='から':
                    tail=soup.new_tag('span',attrs={'class':'selector-suffix'});tail.string=token
                    add_style(tail,font_family='Heading',font_size='calc(1em * var(--glyph-scale))',margin_left=f'{cfg["suffix_gap_em"]}em');visual.append(tail)
                else:
                    kind='digit' if token in '1234１２３４' else 'dot'
                    cell=soup.new_tag('span',attrs={'class':'selector-cell selector-'+kind});cell.string=token;visual.append(cell)
            for cell in visual.select('.selector-cell'):
                add_style(cell,display='inline-block',width=f'{cfg["cell_em"]}em',text_align='center',text_indent='0',line_height='1')
                glyph=soup.new_tag('span');glyph.string=cell.get_text();cell.clear();cell.append(glyph)
                scale=cfg.get('digit_horizontal_scale',1) if 'selector-digit' in cell['class'] else cfg.get('dot_horizontal_scale',1)
                add_style(glyph,display='inline-block',transform=f'scaleX({scale})',transform_origin='center')
                if 'selector-digit' in cell['class'] and cfg.get('display_digits')=='fullwidth':
                    # The sample font's fwid substitution is the same full-width
                    # glyph, without replacing the original copyable character.
                    add_style(glyph,font_feature_settings='"fwid"')
                cell['data-effective-ink-scale']=str(scale*m['style'].get('heading_horizontal_scale',1))
            atom.append(visual)
        else:
            # Other modern levels retain their accepted font and spacing.
            # The two source dot codepoints share only this selector role.
            for token in re.split(r'([1-4１-４]|[·・]|[ \u3000]+)',text):
                if not token:continue
                if token in '1234１２３４' and len(token)==1:
                    node=soup.new_tag('span',attrs={'class':'instruction-digit','data-instruction-digit':'selector' if suffix else 'instruction'});node.string=token;atom.append(node)
                elif token in ('·','・'):
                    if token=='·':
                        old=soup.new_tag('span',attrs={'class':'source-literal sr-only'});old.string=token;atom.append(old)
                        dot=soup.new_tag('span',attrs={'class':'heading-dot visual-only','aria-hidden':'true'});dot.string='・';atom.append(dot)
                    else:atom.append(NavigableString(token))
                elif token.isspace():
                    old=soup.new_tag('span',attrs={'class':'source-literal sr-only'});old.string=token;atom.append(old)
                else:
                    node=soup.new_tag('span',attrs={'class':'selector-suffix'});node.string=token
                    if suffix:add_style(node,margin_left='calc(var(--nominal-em) * .3)')
                    atom.append(node)
