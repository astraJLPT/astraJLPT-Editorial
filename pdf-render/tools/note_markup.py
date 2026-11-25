"""Move exact note labels beneath terms without consuming formatting boundaries.

This is a presentation transform. Coordinates come from exact definitions or
validated authored anchors, never fuzzy matching. Inline ancestors are split
at the term edges so an underline remains inside, rather than around, the
annotated term. Marker deletion is a separate operation.
"""
import html
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from model import Projection
from ruby_core import VOID

INLINE = {'a', 'span', 'u', 'b', 'strong', 'em', 'i', 's', 'del', 'font',
          'small', 'sup', 'sub'}


class _Stack(HTMLParser):
    def __init__(self, raw):
        super().__init__(convert_charrefs=False)
        self.stack = []
        self.feed(raw)

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.get_starttag_text()))

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in VOID: return
        if not self.stack or self.stack[-1][0] != tag:
            raise ValueError('Unbalanced markup at inline note boundary: ' + tag)
        self.stack.pop()


def _inline_stack(raw, offset):
    stack = _Stack(raw[:offset]).stack
    if any(tag in {'ruby', 'rt', 'rp'} for tag, _ in stack):
        raise ValueError('Inline note boundary splits ruby')
    start = len(stack)
    while start and stack[start-1][0] in INLINE:
        start -= 1
    return stack[start:]


def _open(stack):
    return ''.join(raw for tag, raw in stack)


def _close(stack):
    return ''.join('</'+tag+'>' for tag, raw in reversed(stack))


def annotate(value, anchors, *, preserve_reference_containers=False):
    """Wrap terms and remove only their labels, preserving text/ruby/underlines."""
    if not anchors: return value
    source = Projection(value)
    raw = value['html'] if isinstance(value, dict) else html.escape(value)
    projection = Projection({'html': raw})
    if projection.text != source.text:
        raise ValueError('Note preparation changed projection')
    initial_stack = _Stack(raw).stack
    edits = []
    removed = set()
    for anchor in anchors:
        start, end, ms, me = (anchor[k] for k in
                              ('term_start', 'term_end', 'marker_start', 'marker_end'))
        if projection.text[start:end] != anchor['term'] or projection.text[ms:me] != anchor['marker']:
            raise ValueError('Stale inline note markup anchor')
        if '\n' in anchor['term'] or projection.overlaps_ruby(ms, me):
            raise ValueError('Inline note spans a paragraph or ruby label')
        if any(r['start'] < p < r['end'] for r in projection.ruby for p in (start, end)):
            raise ValueError('Inline note boundary splits ruby')
        if not projection.mapping[start] or not projection.mapping[end-1]:
            raise ValueError('Unmapped inline note boundary')
        rs, rt = projection.mapping[start][0], projection.mapping[end-1][1]
        for ruby in projection.ruby:
            if ruby['start'] == start:
                rs = raw.rfind('<ruby', 0, rs+1)
            if ruby['end'] == end:
                rt = raw.find('</ruby>', rt) + 7
        if rs < 0 or rt < 7 and any(r['end'] == end for r in projection.ruby):
            raise ValueError('Missing complete ruby at inline note boundary')
        left, right = _inline_stack(raw, rs), _inline_stack(raw, rt)
        if preserve_reference_containers:
            # A reference belongs to its entire underline, not to every clone
            # made around a lexical note. Keep the common referenced ancestor
            # outside the inserted note span; nested formatting still splits.
            import re
            common = 0
            for a, b in zip(left, right):
                if a != b: break
                common += 1
            keep = 0
            for index, (tag, opening_tag) in enumerate(left[:common]):
                if tag == 'u':
                    node = BeautifulSoup(opening_tag + '</u>', 'html.parser').u
                    if re.fullmatch(r'[①-⑳]', node.get('data-reference-label', '')):
                        keep = index + 1
            if keep:
                left, right = left[keep:], right[keep:]
        opening = '<span data-note-label="'+html.escape(anchor['marker'], quote=True)+'">'
        replacement = (_close(left) + opening + _open(left) + raw[rs:rt]
                       + _close(right) + '</span>' + _open(right))
        edits.append((rs, rt, replacement))
        # A marker is literal text in one node. Do not remove the intervening
        # closing tags or source whitespace as the former raw slice did.
        ma, mb = projection.raw_span(ms, me)
        edits.append((ma, mb, ''))
        removed.update(range(ms, me))
    edits.sort()
    if any(a[1] > b[0] for a, b in zip(edits, edits[1:])):
        raise ValueError('Overlapping inline note markup anchors')
    for start, end, replacement in reversed(edits):
        raw = raw[:start] + replacement + raw[end:]
    # split_notes can leave an outer paragraph open at the end of a fragment;
    # preserve that original outer stack, but never introduce a mismatched tag.
    if _Stack(raw).stack != initial_stack:
        raise ValueError('Inline note changed outer markup structure')
    # Splitting a formatting ancestor at its own edge can leave an empty clone.
    # Remove only zero-content formatting nodes, never spans/anchors, blank
    # fields, source spaces, or any ruby node.
    soup = BeautifulSoup(raw, 'html.parser')
    for node in list(soup.find_all(['u', 'b', 'strong', 'i', 'em', 'font', 'small'])):
        if not node.contents:
            node.decompose()
    raw = str(soup)
    result = {'html': raw}
    after = Projection(result)
    expected = ''.join(c for n, c in enumerate(source.text) if n not in removed)
    if after.text != expected:
        raise ValueError('Inline note changed protected text')
    shift = lambda p: p - sum(n < p for n in removed)
    expected_ruby = [(shift(r['start']), shift(r['end']), r['base'], r['reading']) for r in source.ruby]
    actual_ruby = [(r['start'], r['end'], r['base'], r['reading']) for r in after.ruby]
    if expected_ruby != actual_ruby:
        raise ValueError('Inline note changed ruby association')
    expected_underlines = [bool(m and m[3]) for n, m in enumerate(source.mapping) if n not in removed]
    if expected_underlines != [bool(m and m[3]) for m in after.mapping]:
        raise ValueError('Inline note changed underline extent')
    if isinstance(value, str):
        from plain_rich_breaks import prepare
        result = prepare(result)
    return result
