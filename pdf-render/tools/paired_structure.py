"""Exact A/B labels and external citations over preserved canonical HTML."""
from bs4 import BeautifulSoup, NavigableString, Tag
from model import Projection, digest


def prepare(value, binding, source_value=None):
    source = value if source_value is None else source_value
    if digest(source) != binding['content_sha256'] or not isinstance(value, dict):
        raise ValueError('Stale or unsupported paired structure binding')
    if Projection(value).text != Projection(source).text or Projection(value).ruby != Projection(source).ruby:
        raise ValueError('Paired preparation changed source text or ruby')
    soup = BeautifulSoup(value['html'], 'html.parser')
    nodes = [n for n in soup.children if not isinstance(n, NavigableString) or n.strip()]
    labels = [n for n in nodes if isinstance(n, Tag) and n.name in ['p', 'b', 'strong']
              and Projection({'html': str(n)}).text.strip() in ['A', 'B']]
    if binding.get('inline_prefix'):
        if labels or len(binding['labels']) != 1 or not nodes or not isinstance(nodes[0], Tag) or nodes[0].name != 'p':
            raise ValueError('Inline paired prefix requires one leading paragraph and one label')
        first = nodes[0].contents[0] if nodes[0].contents else None
        label = binding['labels'][0]
        if not isinstance(first, NavigableString) or not str(first).startswith(label + ' '):
            raise ValueError('Inline paired prefix must match the exact first text run')
        marker = soup.new_tag('span')
        marker.string = label
        first.replace_with(marker, NavigableString(str(first)[1:]))
        labels = [marker]
    if [Projection({'html': str(n)}).text.strip() for n in labels] != binding['labels']:
        raise ValueError('Paired labels differ from the exact authored sequence')
    for n, label in zip(labels, binding['labels']):
        n['data-paired-label'] = label
    for citation in binding.get('outside_citations', []):
        matches = [n for n in nodes if isinstance(n, Tag) and n.name in ['p', 'div']
                   and Projection({'html': str(n)}).text.strip() == citation]
        if len(matches) != 1 or matches[0].find(['table', 'section', 'p', 'div']):
            raise ValueError('External paired citation needs one exact complete inline block')
        n = matches[0]
        previous = n.find_previous_sibling()
        if previous is None or previous.name != 'div' or 'border:' not in previous.get('style', ''):
            raise ValueError('External citation must immediately follow its existing passage frame')
        n['data-paired-outside-citation'] = 'true'
    result = {'html': str(soup)}
    if Projection(result).text != Projection(value).text or Projection(result).ruby != Projection(value).ruby:
        raise ValueError('Paired structure changed protected text or ruby')
    return result
