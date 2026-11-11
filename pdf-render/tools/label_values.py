"""Exact label/value associations with native closing-label alignment.

This consumes complete, consecutive paragraph nodes selected by their accepted
text. It does not infer a list from bracket-shaped punctuation elsewhere.
"""
import re
from bs4 import BeautifulSoup, NavigableString, Tag
from model import Projection


def collect(children, binding):
    from notice_layout import html_lines
    entries = binding['entries']
    labels = [e['label'] for e in entries]
    if not entries or len(labels) != len(set(labels)):
        raise ValueError('Label/value entries must be nonempty and unique')
    if any(not re.fullmatch(r'【[^【】\s]{1,12}】', label) for label in labels):
        raise ValueError('Label/value anchor must be one closing-bracket label')
    for key, high in [('before_pt', 60), ('after_pt', 60), ('indent_em', 4), ('gap_em', 2)]:
        value = binding.get(key, 0)
        if type(value) not in [int, float] or not 0 <= value <= high:
            raise ValueError('Invalid label/value spacing: '+key)
    flat = []
    for index, child in enumerate(children):
        if not isinstance(child, Tag) or child.name not in ['p', 'div'] or child.find(['table', 'section']):
            flat.append((index, None, None))
            continue
        for raw in html_lines(child.decode_contents()):
            flat.append((index, raw, Projection({'html': raw}).text.strip()))
    expected = []
    for entry in entries:
        values = entry['value_lines']
        if not values or any(not isinstance(v, str) or not v.strip() for v in values):
            raise ValueError('Label/value needs exact nonempty value lines')
        expected.extend([entry['label'] + values[0], *values[1:]])
    matches = [n for n in range(len(flat)-len(expected)+1)
               if [r[2] for r in flat[n:n+len(expected)]] == expected]
    if len(matches) != 1:
        raise ValueError('Label/value list must match one complete consecutive sequence')
    first = matches[0]
    selected = flat[first:first+len(expected)]
    indexes = sorted(set(r[0] for r in selected))
    if indexes != list(range(indexes[0], indexes[-1]+1)) or any(
            r[0] in indexes for r in flat[:first]+flat[first+len(expected):]):
        raise ValueError('Label/value list must consume complete adjacent paragraphs')
    result, cursor = [], 0
    for entry in entries:
        pieces = selected[cursor:cursor+len(entry['value_lines'])]
        cursor += len(pieces)
        soup = BeautifulSoup(pieces[0][1], 'html.parser')
        node = next((n for n in soup.descendants if isinstance(n, NavigableString) and n.strip()), None)
        if node is None or node.parent.name in ['ruby', 'rt', 'rp'] or not str(node).startswith(entry['label']):
            raise ValueError('Label must be one existing leading plain-text run')
        node.replace_with(str(node)[len(entry['label']):])
        raw = '<br/>'.join([str(soup), *[p[1] for p in pieces[1:]]])
        old = Projection({'html': '<br/>'.join(p[1] for p in pieces)})
        new = Projection({'html': entry['label'] + raw})
        signature = lambda p: [(r['base'], r['reading']) for r in p.ruby]
        if ''.join(old.text.split()) != ''.join(new.text.split()) or signature(old) != signature(new):
            raise ValueError('Label/value selection changed text or ruby')
        result.append((entry['label'], raw))
    return indexes, result


def render(conv, pairs, binding, context):
    measure = ''.join(r'\MeasureLabelValue{' + conv.text(label) + '}' for label, _ in pairs)
    rows = ''.join(r'\LabelValueRow{' + conv.text(label) + '}{'
                   + conv.value({'html': raw}, context) + '}' for label, raw in pairs)
    conv.features.append({'kind': 'closing_bracket_label_values', 'labels': [p[0] for p in pairs],
                          'value_lines': [e['value_lines'] for e in binding['entries']]})
    return (r'\par\addvspace{' + str(binding.get('before_pt', 0)) + r'pt}\begingroup'
            + r'\parskip=0pt\parindent=0pt\rightskip=0pt plus 1fil\relax'
            + r'\advance\leftskip by ' + str(binding.get('indent_em', 0)) + r'em\relax'
            + r'\LabelValueWidth=0pt\LabelValueGap=' + str(binding.get('gap_em', .5)) + r'em\relax'
            + measure + rows + r'\par\endgroup\vspace{' + str(binding.get('after_pt', 0)) + 'pt}')
