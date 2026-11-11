"""Promote an exact adjacent paragraph to its existing table's native caption."""
from bs4 import BeautifulSoup, Tag, NavigableString
from model import Projection, digest


def prepare(value, binding, original=None):
    if digest(original if original is not None else value) != binding['content_sha256']:
        raise ValueError('Stale table-caption ownership')
    if not isinstance(value, dict) or set(value) != {'html'}:
        raise ValueError('Table-caption ownership requires HTML')
    soup = BeautifulSoup(value['html'], 'html.parser')
    tables = soup.find_all('table')
    seen = set()
    for row in binding['captions']:
        index = row['table_index']
        if isinstance(index, bool) or not isinstance(index, int) or index in seen or not 0 <= index < len(tables):
            raise ValueError('Unknown or duplicate table-caption index')
        seen.add(index)
        table = tables[index]
        previous = table.previous_sibling
        while isinstance(previous, NavigableString) and not previous.strip():
            previous = previous.previous_sibling
        if (not isinstance(previous, Tag) or previous.name != 'p'
                or Projection({'html': str(previous)}).text.strip() != row['text']
                or table.find('caption', recursive=False)):
            raise ValueError('Table caption must name its exact adjacent complete paragraph')
        previous.name = 'caption'
        table.insert(0, previous.extract())
    result = {'html': str(soup)}
    a, b = Projection(value), Projection(result)
    if a.text != b.text or a.ruby != b.ruby:
        raise ValueError('Table-caption ownership changed text or ruby')
    return result
