"""Exact native range groups with local optical treatment, never normalization.

The caller binds the whole source field by digest. Each token also declares its
exact occurrence count, and must be a clock, weekday or count range. Ruby nodes
are indivisible. The stored and projected Unicode strings remain unchanged.
"""
import re
from bs4 import NavigableString, Tag
from model import Projection


def validate(text, style):
    clock = r'[0-9]{1,2}[:：][0-9]{2}'
    japanese_clock = r'[0-9]{1,2}時(?:半)?'
    valid = any(re.fullmatch(pattern, text) for pattern in [
        clock + r'[~～〜]' + clock,
        japanese_clock + r'~(?:' + japanese_clock + r')?',
        r'[月火水木金土日]~[月火水木金土日]',
        r'[0-9]{1,2}人~[0-9]{1,2}人',
    ])
    if not valid or style not in ['optical_ascii_wave', 'compact_clock']:
        raise ValueError('Range token must be an exact clock, weekday or count range')
    if (style == 'optical_ascii_wave' and text.count('~') != 1
            or style == 'compact_clock' and not re.fullmatch(clock + r'[～〜]' + clock, text)):
        raise ValueError('Range optical role does not match its retained characters')


def prepare(soup, records):
    seen = set()
    for record in records:
        text, style, count = (record[k] for k in ['text', 'style', 'occurrences'])
        validate(text, style)
        if text in seen or type(count) is not int or not 1 <= count <= 20:
            raise ValueError('Duplicate range token or invalid occurrence count')
        seen.add(text)
        matches = []
        for parent in [soup, *soup.find_all(True)]:
            if parent.name in ['ruby', 'rt', 'rp'] or parent.find_parent(['ruby', 'rt', 'rp']):
                continue
            if parent.has_attr('data-range-token') or parent.find_parent(attrs={'data-range-token': True}):
                continue
            atoms = []
            for child in parent.children:
                if isinstance(child, NavigableString):
                    atoms.extend((c, NavigableString(c)) for c in str(child))
                elif isinstance(child, Tag) and child.name == 'ruby':
                    atoms.append((Projection({'html': str(child)}).text, child))
                else:
                    atoms.append(('\0', child))
            joined = ''.join(a for a, n in atoms)
            offsets = [0]
            for a, n in atoms:
                offsets.append(offsets[-1] + len(a))
            spans = []
            for match in re.finditer(re.escape(text), joined):
                if match.start() not in offsets or match.end() not in offsets:
                    raise ValueError('Range token would split a ruby base')
                spans.append((offsets.index(match.start()), offsets.index(match.end())))
            if spans:
                matches.append((parent, atoms, spans))
        if sum(len(spans) for parent, atoms, spans in matches) != count:
            raise ValueError('Range token occurrence count changed: ' + text)
        for parent, atoms, spans in matches:
            starts = {start: end for start, end in spans}
            parent.clear()
            target, end = parent, -1
            for index, (a, node) in enumerate(atoms):
                if index == end:
                    target = parent
                if index in starts:
                    target = soup.new_tag('span')
                    target['data-range-token'] = style
                    target['data-range-text'] = text
                    parent.append(target)
                    end = starts[index]
                target.append(node)


def render(converter, node, context):
    text = Projection({'html': str(node)}).text
    style = node['data-range-token']
    validate(text, style)
    if text != node['data-range-text']:
        raise ValueError('Range token text changed before native emission')
    saved = getattr(converter, 'keep_spaced_words', False)
    converter.keep_spaced_words = False
    try:
        body = ''.join(converter.node(child, context) for child in node.children)
    finally:
        converter.keep_spaced_words = saved
    if style == 'optical_ascii_wave':
        glyph = r'\textasciitilde{}'
        if body.count(glyph) != 1:
            raise ValueError('ASCII range glyph failed to reach native emission')
        # The same native U+007E glyph is widened and lowered. No replacement
        # font, alias, ActualText substitution or canonical edit is involved.
        body = body.replace(glyph, r'\hspace{.06em}\raisebox{-.22em}{\scalebox{2.1}[1]{\textasciitilde{}}}\hspace{.06em}')
    elif style == 'compact_clock':
        body = body.replace('：', r'\makebox[.35em][c]{：}')
    converter.features.append({'kind': 'native_range_token', 'text': text,
                              'style': style, 'codepoints_preserved': True})
    return r'\mbox{' + body + '}'
