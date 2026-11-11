"""Presentation-only separation between complete instruction sentences."""
import re
from bs4 import NavigableString


def prepare(soup):
    nodes = [n for n in soup.descendants if isinstance(n, NavigableString)
             and not any(p.name in {'rt', 'rp'} for p in n.parents)]
    offsets = []
    position = 0
    for index, node in enumerate(nodes):
        raw = str(node)
        tail = ''.join(str(n) for n in nodes[index + 1:])
        matches = [m.end() for m in re.finditer('。', raw)
                   if re.match(r'[一-龯ぁ-ゖァ-ヶ1１]', (raw[m.end():] + tail)[:1])]
        if matches:
            pieces = []
            start = 0
            for end in matches:
                pieces.append(NavigableString(raw[start:end]))
                marker = soup.new_tag('span')
                marker['data-instruction-boundary'] = 'sentence'
                pieces.append(marker)
                offsets.append(position + end)
                start = end
            pieces.append(NavigableString(raw[start:]))
            node.replace_with(*pieces)
        position += len(raw)
    return offsets
