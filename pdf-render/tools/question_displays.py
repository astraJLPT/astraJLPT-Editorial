"""Identify a following question table without changing canonical content.

The table component owns the one exterior gap. Options, inline glyphs, tables
inside cells and notices retain their own roles and spacing.
"""
from bs4 import BeautifulSoup, NavigableString


def prepare(value, target, associated=False):
    if isinstance(value, str):
        return value
    soup = BeautifulSoup(value['html'], 'html.parser')
    if soup.select('[data-question-display-owner]'):
        raise ValueError('Question display markers are renderer-owned')
    seen_prose = associated

    def visit(parent):
        nonlocal seen_prose
        for child in parent.children:
            if isinstance(child, NavigableString):
                if child.strip():
                    seen_prose = True
            elif child.has_attr('data-embedded-document'):
                # A memo/email owns its exterior separation and interior table
                # metrics. Do not turn an internal table into a second boundary.
                seen_prose = False
            elif child.name == 'table':
                if seen_prose:
                    child['data-question-display-owner'] = target
                # A second display does not itself establish a prose boundary.
                seen_prose = False
            elif child.name not in ['rt', 'rp', 'img']:
                visit(child)

    visit(soup)
    return {'html': str(soup)}
