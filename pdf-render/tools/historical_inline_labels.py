"""Validate explicitly identified inline passage labels without editing prose."""
import re
from model import digest, Projection
from presentation import source_binding
from bs4 import BeautifulSoup, Tag


def validate(model, item, binding):
    if model.get('exam', {}).get('generation') != 'historical-1991-2009':
        raise ValueError('Historical inline label outside Old JLPT')
    if (digest(item['content']) != binding['content_sha256']
            or not re.fullmatch(r'[（(][1-9][0-9]?[）)]', binding['text'])
            or not Projection(item['content']).text.lstrip().startswith(binding['text'])):
        raise ValueError('Stale or invalid historical inline passage label')
    source_binding(model['unit'], binding['evidence'])


def prepare_body_paragraphs(value, label, numbered_introduction=False, spatial_paragraphs=()):
    """Continue the opening paragraph's inset without inheriting its label.

    Explicit paragraph/document roles own their own geometry. Only ordinary
    top-level prose following an ordinary inline-labelled opener is eligible.
    The wrapper is a rendering annotation, never a canonical text edit.
    """
    if not isinstance(value, dict) or 'html' not in value:
        return value, []
    soup = BeautifulSoup(value['html'], 'html.parser')
    roots = [n for n in soup.children if isinstance(n, Tag)]
    if (not roots or roots[0].name != 'p' or (roots[0].attrs and not(numbered_introduction and roots[0].attrs=={'data-historical-text-role':'numbered_introduction'}))
            or not Projection({'html': str(roots[0])}).text.lstrip().startswith(label)):
        return value, []
    # A composite introduction governs a frame/table/exercise; its later
    # paragraphs are not automatically ordinary continuing prose.
    marked = []
    for index, node in enumerate(roots[1:], 1):
        if node.name != 'p' or node.attrs:
            continue
        plain = Projection({'html': str(node)}).text.strip()
        if plain in spatial_paragraphs:
            continue
        if not plain or node.find(['p', 'div', 'table', 'ol', 'ul', 'br']):
            continue
        node['data-historical-inline-body'] = 'continued-paragraph'
        marked.append(dict(top_level_index=index, text=plain))
    if not marked:
        return value, []
    result = {'html': str(soup)}
    before, after = Projection(value), Projection(result)
    if before.text != after.text or before.ruby != after.ruby:
        raise ValueError('Historical inline paragraph inset changed content or ruby')
    return result, marked
