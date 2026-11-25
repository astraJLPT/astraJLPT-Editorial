"""Exact native lines for a reviewed email whose line lengths are tested."""
from bs4 import Tag
from model import Projection
from notice_layout import html_lines
from example_layout import slice_inline


def validate(binding):
    required = {'lines', 'body_pt', 'baseline_pt'}
    if (not required <= set(binding) or binding.get('role') != 'email'
            or binding.get('layout') != 'explicit_email_lines'
            or binding.get('container_tag') != 'div' or binding.get('presentation') != 'typed_box'
            or set(binding) & {'title', 'rows', 'paragraphs'}):
        raise ValueError('Explicit email requires a complete typed line binding')
    lines = binding['lines']
    if (not isinstance(lines, list) or not 2 <= len(lines) <= 20
            or any(not isinstance(s, str) or not s.strip() or '\n' in s for s in lines)):
        raise ValueError('Explicit email requires nonempty complete authored lines')
    for name, lo, hi in [('body_pt', 7, 14), ('baseline_pt', 8, 24), ('padding_pt', 8, 30), ('width_fraction', .5, 1)]:
        value = binding.get(name, 8 if name == 'padding_pt' else 1)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not lo <= value <= hi:
            raise ValueError('Invalid explicit email geometry: '+name)
    if binding['baseline_pt'] < binding['body_pt'] + 2:
        raise ValueError('Explicit email needs adequate line pitch')
    metadata = binding.get('metadata_columns')
    if metadata:
        if set(metadata) != {'label_width_em', 'rows'} or not 1 <= metadata['label_width_em'] <= 6:
            raise ValueError('Invalid explicit email metadata columns')
        seen = set()
        for row in metadata['rows']:
            if (set(row) != {'line', 'label', 'separator', 'value'} or type(row['line']) is not int
                    or not 0 <= row['line'] < len(lines) or row['line'] in seen
                    or row['separator'] not in {':', '：'}
                    or lines[row['line']] != row['label'] + row['separator'] + row['value']):
                raise ValueError('Email metadata must bind one complete unchanged line')
            seen.add(row['line'])


def parts(node, binding):
    validate(binding)
    if (not isinstance(node, Tag) or node.name != 'div'
            or any(n.name not in {'div', 'br', 'span', 'u', 'b', 'strong', 'i', 'em', 'ruby', 'rt', 'rp'} for n in node.find_all())
            or len(node.find_all('br')) != len(binding['lines']) - 1
            or any(n.find(['br', 'div', 'p']) for n in node.find_all('ruby'))):
        raise ValueError('Explicit email accepts simple complete rich lines only')
    before = Projection({'html': str(node)})
    if before.text != binding['text'] or before.text.strip('\n').split('\n') != binding['lines']:
        raise ValueError('Explicit email text or authored line boundaries changed')
    lines = html_lines(node.decode_contents())
    if [Projection({'html': line}).text.strip('\n') for line in lines] != binding['lines']:
        raise ValueError('Explicit email line splitting lost or changed content')
    ruby = [(r['base'], r['reading']) for r in before.ruby]
    if ruby != [(r['base'], r['reading']) for line in lines for r in Projection({'html': line}).ruby]:
        raise ValueError('Explicit email line splitting changed ruby')
    return lines


def render(conv, node, binding):
    lines = parts(node, binding)
    width = binding.get('width_fraction', 1); padding = binding.get('padding_pt', 8)
    metadata = binding.get('metadata_columns', {})
    rows = {r['line']: r for r in metadata.get('rows', [])}
    rendered = []
    for index, line in enumerate(lines):
        if index in rows:
            row = rows[index]; split = len(row['label']); end = split + len(row['separator'])
            pieces = [slice_inline(line, a, b) for a, b in [(0, split), (split, end), (end, len(binding['lines'][index]))]]
            label, colon, value = [conv.value({'html': part}, 'option') for part in pieces]
            tex = (r'\makebox['+str(metadata['label_width_em'])+r'em][l]{'+label+'}'
                   +r'\makebox[1em][c]{'+colon+'}'+value)
        else:
            tex = conv.value({'html': line}, 'option')
        rendered.append(r'\noindent\mbox{'+tex+r'}\par')
    body = ''.join(rendered)
    frame = (r'\begin{NoticeFrame}[nobreak=true,skipabove=0pt,skipbelow=0pt,linewidth=.5pt,'
        +'innerleftmargin='+str(padding)+'pt,innerrightmargin='+str(padding)+'pt,'
        +'innertopmargin='+str(padding)+'pt,innerbottommargin='+str(padding)+'pt]'
        +r'{\PreserveDocumentDigitstrue\setlength\parindent{0pt}\setlength\parskip{0pt}'
        +r'\fontsize{'+str(binding['body_pt'])+'}{'+str(binding['baseline_pt'])+r'}\selectfont '+body+r'}\end{NoticeFrame}')
    conv.features.append({'kind': 'embedded_document', 'role': 'email', 'layout': 'explicit_email_lines',
        'presentation': 'typed_box', 'line_count': len(lines), 'lines': binding['lines'],
        'body_pt': binding['body_pt'], 'baseline_pt': binding['baseline_pt'], 'canonical_changed': False})
    if rows:conv.features.append({'kind':'embedded_email_metadata_columns','columns':metadata,'canonical_changed':False})
    return r'\par\addvspace{8pt}\noindent\begin{minipage}{'+str(width)+r'\linewidth}'+frame+r'\end{minipage}\par\vspace{7pt}'
