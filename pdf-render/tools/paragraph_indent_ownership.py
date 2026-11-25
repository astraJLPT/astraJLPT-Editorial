"""Let exact canonical one-em paragraph spaces own their indent once."""
import html
from model import Projection, digest


def prepare(value, binding):
    if digest(value) != binding['content_sha256']:
        raise ValueError('Stale paragraph indent binding')
    offsets = binding['offsets']
    if not offsets or len(offsets) != len(set(offsets)):
        raise ValueError('Paragraph indent offsets must be nonempty and unique')
    original = Projection(value)
    raw = value['html'] if isinstance(value, dict) else html.escape(value)
    projection = Projection({'html': raw})
    if original.text != projection.text:
        raise ValueError('Paragraph indent preparation changed projection')
    edits = []
    for offset in offsets:
        if (type(offset) is not int or not 0 <= offset < len(projection.text) - 1
                or projection.text[offset] != '　'
                or (offset != 0 and projection.text[offset - 1] != '\n')
                or projection.text[offset + 1].isspace()
                or projection.overlaps_ruby(offset, offset + 1)):
            raise ValueError('Indent must select one fullwidth space at a paragraph start')
        start, end = projection.raw_span(offset, offset + 1)
        if raw[start:end] != '　':
            raise ValueError('Canonical indent must be one literal fullwidth space')
        edits.append((start, end))
    for start, end in sorted(edits, reverse=True):
        raw = raw[:start] + '<span data-canonical-paragraph-indent="one-em">　</span>' + raw[end:]
    result = {'html': raw}
    if isinstance(value, str):
        from plain_rich_breaks import prepare as preserve_breaks
        result = preserve_breaks(result)
    after = Projection(result)
    if original.text != after.text or original.ruby != after.ruby:
        raise ValueError('Paragraph indent ownership changed canonical text or ruby')
    return result
