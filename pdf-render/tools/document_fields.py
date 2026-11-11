"""Native columns for exact existing colon or literal-bracket field rows."""
import copy
import re
from model import Projection, digest
from structured_documents import lines
from example_layout import slice_inline


def dimension(value, lower, upper, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not lower <= value <= upper:
        raise ValueError('Invalid document field '+name)
    return value


def render(conv, value, tex, binding, context='body'):
    if digest(value) != binding['content_sha256']:
        raise ValueError('Stale document fields')
    label_width = dimension(binding['label_width_em'], 1, 12, 'label width')
    separator_width = dimension(binding.get('separator_width_em', 0), 0, 2, 'separator width')
    available = lines(value)
    texts = [Projection({'html': x}).text.strip() for x in available]
    matcher = copy.copy(conv)
    matcher.features = []
    selected, edits = [], []
    for row in binding['rows']:
        text = row['text']
        if not text or texts.count(text) != 1 or '\n' in text:
            raise ValueError('Document field row must select one complete unique line')
        index = texts.index(text)
        if selected and index <= selected[-1]:
            raise ValueError('Document field rows overlap or change source order')
        selected.append(index)
        raw = available[index]
        projection = Projection({'html': raw})
        fields = row['fields']
        if not 1 <= len(fields) <= 2:
            raise ValueError('Document field row requires one or two fields')
        prefix, offset, cursor = [], 0, 0
        last_value = None
        for n, field in enumerate(fields):
            label, separator, content = field['label'], field['separator'], field['value']
            if not label.strip() or not content.strip() or separator.strip() not in ['', ':', '：']:
                raise ValueError('Invalid document field label, separator or value')
            phrase = label+separator+content
            at = projection.text.find(phrase, cursor)
            if at < 0 or projection.text[cursor:at].strip():
                raise ValueError('Document fields must exhaust their exact row in order')
            label_end = at+len(label)
            content_at = label_end+len(separator)
            end = content_at+len(content)
            label_raw = slice_inline(raw, at, label_end)
            separator_raw = slice_inline(raw, label_end, content_at)
            value_raw = slice_inline(raw, content_at, end)
            # The original rendered row already recorded these source glyphs.
            # Re-emission replaces that exact fragment; it is not new content.
            label_tex = matcher.value({'html': label_raw}, 'option')
            separator_tex = matcher.value({'html': separator_raw.strip()}, 'option') if separator.strip() else ''
            value_tex = matcher.value({'html': value_raw}, context)
            prefix.append(r'\makebox['+str(label_width)+r'em][l]{'+label_tex+'}')
            prefix.append(r'\makebox['+str(separator_width)+r'em][c]{'+separator_tex+'}')
            offset += label_width+separator_width
            if n < len(fields)-1:
                width = dimension(field.get('value_width_em'), 1, 20, 'nonterminal value width')
                prefix.append(r'\makebox['+str(width)+r'em][l]{'+value_tex+'}')
                offset += width
            else:
                if 'value_width_em' in field:
                    raise ValueError('Final document value must retain native wrapping')
                last_value = value_tex
            cursor = end
        if projection.text[cursor:].strip():
            raise ValueError('Document fields omit row content')
        native = matcher.value({'html': raw}, context)
        if not native or tex.count(native) != 1:
            raise ValueError('Document field row did not reach one native fragment')
        start = tex.index(native)
        if any(max(start, a) < min(start+len(native), b) for a,b,_ in edits):
            raise ValueError('Document field native fragments overlap')
        output = r'\DocumentFieldRow{'+str(offset)+'}{'+''.join(prefix)+'}{'+last_value+'}'
        edits.append((start, start+len(native), output))
    if not selected:
        raise ValueError('Document fields need explicit rows')
    for start, end, output in sorted(edits, reverse=True):
        tex = tex[:start]+output+tex[end:]
    conv.features.append({'kind': 'document_field_columns', 'rows': binding['rows'],
                          'label_width_em': label_width, 'separator_width_em': separator_width,
                          'canonical_changed': False, 'final_values_hang_at_value_column': True})
    return tex
