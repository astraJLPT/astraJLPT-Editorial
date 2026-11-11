"""Exact display of an existing paired label, with canonical delimiters retained."""
import html
import re
from model import Projection, digest


def label_value(text):
    normalized = text.translate(str.maketrans('ＡＢ', 'AB'))
    match = re.fullmatch(r'(?:\(([AB])\)|（([AB])）)', normalized)
    return next(g for g in match.groups() if g) if match else None


def prepare(value, binding, source_value=None):
    source = value if source_value is None else source_value
    if digest(source) != binding['content_sha256']:
        raise ValueError('Stale paired label presentation')
    source_label, display = binding['source_label'], binding['display_label']
    if display not in ['A', 'B'] or label_value(source_label) != display:
        raise ValueError('Paired label display must preserve its A/B identity')
    original, current = Projection(source), Projection(value)
    if original.text != current.text or original.ruby != current.ruby:
        raise ValueError('Paired label preparation changed protected text or ruby')
    raw = (value['html'] if isinstance(value, dict) else
           html.escape(value).replace('\n', '<span data-authored-plain-break="line">\n</span>'))
    projection = Projection({'html': raw})
    first = projection.text.split('\n')[0]
    if first.strip() != source_label:
        raise ValueError('Paired label must be the complete first line')
    start = len(first) - len(first.lstrip())
    end = start + len(source_label)
    if projection.overlaps_ruby(start, end):
        raise ValueError('Paired label cannot contain ruby')
    a, b = projection.raw_span(start, end)
    if raw[a:b] != source_label:
        raise ValueError('Paired label cannot cross inline markup')
    raw = (raw[:a] + '<span data-paired-label-source="' + source_label +
           '" data-paired-label-display="' + display + '">' + source_label +
           '</span>' + raw[b:])
    result = {'html': raw}
    prepared = Projection(result)
    if prepared.text != current.text or prepared.ruby != current.ruby:
        raise ValueError('Paired label presentation changed protected content')
    return result
