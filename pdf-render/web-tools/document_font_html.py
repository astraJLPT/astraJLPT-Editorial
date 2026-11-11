"""Native handwriting font scope, including document digits and font-size glue."""
import re
from semantic_html import add_class, add_style, pt


def preserve_document_digits(soup, region):
    """PreserveDocumentDigitstrue leaves each original digit in the local face."""
    for digits in region.select('.content-digits'):
        digits.replace_with(soup.new_string(digits.get_text()))


def memo_font(soup, region, style, body_pt):
    spec=style['font_roles']['memo'];scale=spec.get('scale',1)
    preserve_document_digits(soup,region)
    add_class(region,'native-memo-font')
    add_style(region,font_family='Memo,Body,serif',
              font_size=f'calc(var(--glyph-point) * {body_pt})',
              font_feature_settings=','.join('"'+f+'"' for f in spec.get('features',[])) or 'normal',
              **{'--glyph-scale':scale,'--glyph-point':f'calc(var(--point) * {scale})',
                 '--nominal-em':pt(body_pt*scale)})
    # Both MemoLatin and MemoJapanese use Scale. An explicit alternate face
    # (identifier, line override, numbered furniture) still owns its font.
    excluded={'literal-identifier','cloze-slot','answer-slot','star-slot',
              'paired-label','old-note-label','note-label','annotation-label'}
    def owns(node):
        for part in [node,*node.parents]:
            if part is region:return True
            if part.name in ('svg','path') or excluded.intersection(part.get('class',[])):return False
            if part.has_attr('data-document-font-override'):return False
            family=re.findall(r'(?:^|;)\s*font-family\s*:\s*([^;]+)',part.get('style',''))
            generic_latin='tex-latin' in part.get('class',[]) and family and family[-1].startswith(('BodyLatin','NoticeLatin'))
            if family and not generic_latin and not family[-1].startswith(('Memo','inherit')):return False
        return False
    # Native table cells and bold source markup remain in the selected Memo
    # family (the pinned handwriting face has no separate bold variant).
    # Explicit cell/line font overrides still terminate this inherited scope.
    for node in region.select('table,th,td,caption,b,strong'):
        if owns(node):add_style(node,font_family='inherit',font_weight='400')
    for atom in region.select('.tex-latin'):
        if owns(atom):add_style(atom,font_family='Memo,Body,serif',font_size='1em')
    # LuaTeX's FakeBold is a percentage of each glyph's em. Re-evaluate the
    # relative stroke on descendants so ruby and authored smaller lines use
    # their own font size rather than inheriting the body's computed pixels.
    stroke=spec.get('embolden',0)/100
    for node in [region,*region.find_all(True)]:
        if node.name in ('svg','path'):continue
        add_style(node,**{'-webkit-text-stroke-width':f'{stroke:g}em' if owns(node) else '0'})
    # xkanjiskip is resolved in the native 12pt preamble before MemoLatin is
    # selected; changing the document font must not enlarge this fixed glue.
    for atom in region.select('.mixed-before,.mixed-after'):
        if not owns(atom):continue
        for cls,side in [('mixed-before','left'),('mixed-after','right')]:
            if cls in atom.get('class',[]):add_style(atom,**{'margin_'+side:pt(12*style.get('mixed_script_gap_em',0))})
