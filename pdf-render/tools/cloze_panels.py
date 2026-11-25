"""Bind existing label/introduction/frame triples without changing their text."""
from bs4 import BeautifulSoup, NavigableString, Tag
from model import Projection, digest


def prepare(value, binding, original=None):
    source = value if original is None else original
    if digest(source) != binding['content_sha256'] or not isinstance(value, dict):
        raise ValueError('Stale cloze panel binding')
    soup = BeautifulSoup(value['html'], 'html.parser')
    nodes = [n for n in soup.children if not isinstance(n, NavigableString) or n.strip()]
    labels = [r['label'] for r in binding['panels']]
    if not labels or len(labels) != len(set(labels)):
        raise ValueError('Cloze panel labels must be unique')
    used = set()
    for row in binding['panels']:
        matches = [k for k, n in enumerate(nodes) if isinstance(n, Tag) and n.name == 'p'
                   and Projection({'html': str(n)}).text.strip() == row['label']]
        if len(matches) != 1:
            raise ValueError('Cloze panel needs one exact label paragraph')
        k = matches[0]
        if k + 2 >= len(nodes) or used.intersection([k, k+1, k+2]):
            raise ValueError('Cloze panel has missing or overlapping nodes')
        label, intro, frame = nodes[k:k+3]
        if (not isinstance(intro, Tag) or intro.name != 'p'
                or Projection({'html': str(intro)}).text.strip() != row['introduction']
                or not isinstance(frame, Tag) or frame.name != 'div'
                or 'border:' not in frame.get('style', '') or frame.find(['div', 'section'])):
            raise ValueError('Cloze panel requires its exact adjacent introduction and frame')
        wrapper = soup.new_tag('div')
        wrapper['data-cloze-panel'] = 'true'
        label.insert_before(wrapper)
        for node in [label, intro, frame]:
            wrapper.append(node.extract())
        used.update([k, k+1, k+2])
    result = {'html': str(soup)}
    if Projection(result).text != Projection(value).text or Projection(result).ruby != Projection(value).ruby:
        raise ValueError('Cloze panel ownership changed text or ruby')
    return result


def render(conv, node, context):
    children = [n for n in node.children if isinstance(n, Tag)]
    if node['data-cloze-panel'] != 'true' or len(children) != 3:
        raise ValueError('Invalid prepared cloze panel')
    label, intro, frame = children
    label_tex = ''.join(conv.node(n, context) for n in label.children)
    header = r'\PassageLabel{' + label_tex + '}' + conv.node(intro, context)
    body = conv.node(frame, context).replace('NoticeFrame', 'ClozeFrame')
    conv.features.append({'kind': 'cloze_panel_header_ownership',
        'label': Projection({'html': str(label)}).text.strip(),
        'introduction': Projection({'html': str(intro)}).text.strip()})
    return r'\KeepClozePanel{' + header + '}{' + body + '}'
