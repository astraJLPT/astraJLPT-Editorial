"""Semantic cell alignment, shared by normal and spanning table cells.

Header identity comes from the canonical th element or an authored header row.
Body prose stays left aligned unless an explicit column/cell role says otherwise.
No alignment decision supplies a background fill.
"""


def alignment(cell, text, row, column, presentation, column_alignment,
              bound=None, header_default='center', mark_default='center'):
    if bound and 'align' in bound:
        return bound['align'], 'bound_cell'
    if row == 0 and 'header_align' in presentation:
        return presentation['header_align'], 'authored_header_row'
    if cell.name == 'th':
        return header_default, 'semantic_header'
    if text.strip() in ['○', '〇', '×']:
        return mark_default, 'availability_mark'
    return column_alignment, 'column_or_prose'
