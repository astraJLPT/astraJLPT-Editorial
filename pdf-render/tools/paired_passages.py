"""Shared paired-passage geometry, independent of input container syntax."""
import re

DEFAULTS = {
    'first_label_before_pt': 10, 'next_label_before_pt': 16,
    'label_frame_gap_pt': 3, 'label_align': 'left',
    'frame_padding_pt': 12, 'frame_side_padding_pt': 8,
    'first_paragraph_indent_em': 1, 'rule_pt': .5,
    'new_page_before_labels': [],
}


def parameters(overrides=None):
    if overrides is None:
        overrides = {}
    if not isinstance(overrides, dict) or set(overrides) - set(DEFAULTS):
        raise ValueError('Unknown paired passage control')
    result = {**DEFAULTS, **overrides}
    if result['label_align'] not in ['left', 'center', 'right']:
        raise ValueError('Invalid paired label alignment')
    if result['new_page_before_labels']not in [[],['B']]:raise ValueError('Invalid paired page boundary')
    for key, upper in [('first_label_before_pt', 40), ('next_label_before_pt', 40),
                       ('label_frame_gap_pt', 20), ('frame_padding_pt', 30),
                       ('frame_side_padding_pt', 30), ('first_paragraph_indent_em', 2),
                       ('rule_pt', 2)]:
        value = result[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= upper:
            raise ValueError('Invalid paired passage dimension: ' + key)
    return result


def trim_paragraphs(tex):
    return re.sub(r'(?:\s*\\Para\s*)+$', '', re.sub(r'^(?:\s*\\Para\s*)+', '', tex)).strip()


def unwrap_frame(tex):
    """Consume one whole structural HTML box, never nested/document-specific boxes."""
    tex = trim_paragraphs(tex)
    for env in ['NoticeFrame', 'PairedFrame', 'RuleFrame']:
        begin, end = r'\begin{' + env + '}', r'\end{' + env + '}'
        if tex.startswith(begin) and tex.endswith(end):
            if tex.count(begin) != 1 or tex.count(end) != 1:
                raise ValueError('Nested paired passage frames require an explicit section binding')
            body = tex[len(begin):-len(end)]
            if body.startswith('['):
                raise ValueError('Custom paired frame options require an explicit section binding')
            return trim_paragraphs(body), env
    if any(r'\begin{' + env + '}' in tex for env in ['NoticeFrame', 'PairedFrame', 'RuleFrame']):
        raise ValueError('A paired passage must have one complete outer frame')
    return tex, None


def render(tex, frame_style='box', overrides=None):
    """A/B roles win over generic HTML border rendering; notes are handled by caller."""
    cfg = parameters(overrides)
    # Empty HTML wrappers and text newlines are equivalent paragraph boundaries.
    parts = [x.strip() for x in tex.split(r'\Para') if x.strip()]
    # Parenthesized A/B labels are semantic paired labels too. Keep the exact
    # characters and their ASCII glyph routing in the emitted label.
    def label_value(value):
        plain = value.replace(r'\AsciiParen{(}', '(').replace(r'\AsciiParen{)}', ')')
        plain = plain.translate(str.maketrans('ＡＢ', 'AB'))
        if plain in ['A', 'B']:
            return plain
        match = re.fullmatch(r'(?:\(([AB])\)|（([AB])）)', plain)
        return next(g for g in match.groups() if g) if match else None
    labels = [n for n, x in enumerate(parts) if label_value(x)]

    def frame(body):
        citation = ''
        start, end = r'\PairedCitationStart{}', r'\PairedCitationEnd{}'
        if start in body or end in body:
            body = trim_paragraphs(body)
            if body.count(start) != 1 or body.count(end) != 1 or not body.endswith(end):
                raise ValueError('External citation must be one complete authored passage tail')
            body, citation = body[:-len(end)].split(start)
        body, old_env = unwrap_frame(body)
        if not body:
            raise ValueError('Empty paired passage body')
        if not body.startswith((r'\DocumentLine{', r'\noindent 　')):
            body = r'\hspace*{' + str(cfg['first_paragraph_indent_em']) + 'em}' + body
        if frame_style == 'none':
            return body + (r'\par\addvspace{4pt}' + citation if citation else '')
        env = 'RuleFrame' if frame_style == 'horizontal_rules' or old_env == 'RuleFrame' else 'PairedFrame'
        opts = ','.join(key + '=' + str(value) + 'pt' for key, value in [
            ('linewidth', cfg['rule_pt']), ('innertopmargin', cfg['frame_padding_pt']),
            ('innerbottommargin', cfg['frame_padding_pt']), ('splittopskip', cfg['frame_padding_pt']),
            ('splitbottomskip', cfg['frame_padding_pt']), ('innerleftmargin', cfg['frame_side_padding_pt']),
            ('innerrightmargin', cfg['frame_side_padding_pt'])])
        return r'\begin{' + env + '}[' + opts + ']' + body + r'\end{' + env + '}' + (r'\par\addvspace{4pt}' + citation if citation else '')

    if not labels:
        return frame(tex), 'paired_context_frame'
    values = [label_value(parts[n]) for n in labels]
    if values not in [['A'], ['B'], ['A', 'B']]:
        raise ValueError('Ambiguous paired passage labels')
    out = parts[:labels[0]]
    for k, start in enumerate(labels):
        stop = labels[k + 1] if k + 1 < len(labels) else len(parts)
        # B keeps its continuation role when stored in a separate content item.
        gap = cfg['first_label_before_pt'] if values[k] == 'A' else cfg['next_label_before_pt']
        if values[k]in cfg['new_page_before_labels']:
            out.append(r'\clearpage');gap=0
        glue = r'\addvspace{' if values[k] == 'A' else r'\vspace{'
        out += [r'\par' + glue + str(gap) + r'pt}\PairedPassageLabel{' + parts[start] + '}',
                frame(r'\Para '.join(parts[start + 1:stop]))]
    align = {'left': 'l', 'center': 'c', 'right': 'r'}[cfg['label_align']]
    scope = r'{\renewcommand\PairedLabelAlignment{' + align + r'}\renewcommand\PairedLabelFrameGap{' + str(cfg['label_frame_gap_pt']) + 'pt}'
    return scope + r'\Para '.join(out) + '}', 'explicit_paired_labels_separate_frames'
