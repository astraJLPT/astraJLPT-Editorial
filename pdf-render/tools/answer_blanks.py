"""Presentation-only empty answer brackets, with role and neighbour controls."""
import html
import re
from model import Projection

EMPTY = re.compile(r'[（(][ \u3000\t]+[）)]')
COMPACT = re.compile(r'\(\)|（）')
QUESTION_EMPTY = re.compile(r'[（(][ \u3000\t]+[）)]|\(\)|（）')
ROLES = {'body', 'heading', 'example'}
KEYS = {'inner_width_em', 'side_space_em', 'punctuation_side_space_em', 'digit_side_space_em'}
DEFAULT = {'inner_width_em': 2.8, 'side_space_em': .45,
           'punctuation_side_space_em': 0, 'digit_side_space_em': .45}
PUNCTUATION = set('。、，．,.！？!?：:；;」』）)]】〉》「『（([【〈《')


def validate(settings):
    if set(settings) - KEYS:raise ValueError('Unknown answer bracket setting')
    for key, value in settings.items():
        limit = 5 if key == 'inner_width_em' else 2
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= limit:
            raise ValueError('Invalid answer bracket dimension')
    return {**DEFAULT, **settings}


def prepare(value, role, settings, *, compact_question=False, historical_underline_samples=False):
    if role not in ROLES:raise ValueError('Unknown answer bracket role')
    dimensions = validate(settings)
    raw = value['html'] if isinstance(value, dict) else html.escape(value).replace('\n', '<br/>')
    if 'data-answer-blank' in raw:return value, []
    p = Projection({'html': raw}); edits = []; records = []; padding = set()
    # Exact Old inline-atom bindings own their width. Other blanks in the same
    # field still receive the ordinary role; Modern takes the unchanged path.
    protected = [m.span() for m in re.finditer(
        r'<span(?=[^>]*data-historical-answer-slot="parenthesized_answer_slot")[^>]*>[^<>]*</span>',raw)] if historical_underline_samples else []
    for match in (QUESTION_EMPTY if compact_question else EMPTY).finditer(p.text):
        a, b = match.span()
        if COMPACT.fullmatch(match[0]) and (re.search(r'[A-Za-z0-9_./:@]$',p.text[:a]) or re.match(r'[A-Za-z0-9_/:]',p.text[b:])):
            continue  # Function/URL syntax is not an inferred Japanese answer slot.
        if any(r['start'] < b and r['end'] > a for r in p.ruby):
            raise ValueError('An empty bracket cannot replace a ruby base')
        start, end = p.mapping[a][0], p.mapping[b-1][1]
        if any(x<=start and end<=y for x,y in protected):continue
        if historical_underline_samples and role=='heading' and re.fullmatch(
                r'[（(]<span data-double-underline="true">[ \u3000\t]+</span>[）)]',raw[start:end]):
            # An explicitly authored historical instruction demonstrates the
            # tested double rule; its parenthetical is not an answer slot.
            continue
        if '<' in raw[start:end]:raise ValueError('Empty bracket crosses unsupported markup')
        left = p.text[:a].rstrip(' \u3000\t')[-1:]
        right = p.text[b:].lstrip(' \u3000\t')[:1]
        def side(neighbour):
            if not neighbour or neighbour in '\r\n':return 0
            if neighbour in PUNCTUATION:return dimensions['punctuation_side_space_em']
            if re.fullmatch(r'[0-9０-９]', neighbour):return dimensions['digit_side_space_em']
            return dimensions['side_space_em']
        # Own adjacent ASCII layout spaces across inline markup too. Preserve
        # their exact projection inside zero-width presentation wrappers.
        for step, pos in [(-1, a-1), (1, b)]:
            while 0 <= pos < len(p.text) and p.text[pos] == ' ':
                if p.mapping[pos]:padding.add(tuple(p.mapping[pos][:2]))
                pos += step
        inner, before, after = dimensions['inner_width_em'], side(left), side(right)
        compact = COMPACT.fullmatch(match[0]) is not None
        kind = ' data-blank-kind="compact-question"' if compact else ''
        span = (f'<span data-answer-blank="{role}"{kind} data-blank-inner="{inner}" '
                f'data-blank-left="{before}" data-blank-right="{after}">{raw[start:end]}</span>')
        edits.append((start, end, span))
        records.append({'kind': 'answer_blank', 'role': role, 'projection_start': a,
                        'original': match[0], 'left_neighbour': left, 'right_neighbour': right,
                        'inner_width_em': inner, 'left_space_em': before, 'right_space_em': after,
                        'glyph_policy': 'native surrounding Japanese face and size'})
        if compact:records[-1]['basis']='Empty matched parentheses in a scored question stem; inferred answer-slot geometry, canonical text unchanged'
    if not edits:return value, []
    edits.extend((a,b,'<span data-blank-padding="ascii">'+raw[a:b]+'</span>')for a,b in padding)
    edits.sort()
    if any(a[1] > b[0] for a, b in zip(edits, edits[1:])):
        raise ValueError('Adjacent empty brackets need an explicit bounded decision')
    for a, b, replacement in reversed(edits):raw = raw[:a] + replacement + raw[b:]
    result = {'html': raw}
    # Plain values already render runs of newlines as one paragraph boundary.
    # Compare against the unannotated HTML projection, preserving that existing
    # normalization and every visible character; never mutate the source value.
    if Projection(result).text != p.text:raise ValueError('Bracket presentation changed protected text')
    return result, records
