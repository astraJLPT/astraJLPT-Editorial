"""Conservative definition candidates shared by staging and bound rendering.

An inline reference is never a definition. A colon anchors automatic discovery;
an immediately preceding, sequential definition may use whitespace instead.
Separator-free tails require explicit author review and a bound notes range.
"""
import re

LABEL=re.compile(r'^[ \u3000]*[（(][ \u3000]*注[ \u3000]*([0-9０-９]*)[ \u3000]*[)）][ \u3000]*(.*)$')


def definition(line,allow_space=False,allow_label_colon=False):
    match=LABEL.fullmatch(line.rstrip('\r\n'))
    if not match:return None
    label,body=match.groups()
    # A reviewed definition can retain a redundant colon after its label.
    # Automatic discovery remains conservative; only a bound tail opts in.
    if allow_label_colon and body.startswith((':','：')):body=body[1:].lstrip(' \u3000')
    split=re.fullmatch(r'([^:：\n]+?)\s*[:：]\s*(\S.*)',body)
    separator='colon'
    if split is None and allow_space:
        split=re.fullmatch(r'(\S+)[ \u3000]+(\S.*)',body);separator='space'
    if split is None:return None
    term,meaning=split.groups()
    if not term.strip()or not meaning.strip():return None
    return {'label':label,'term':term.strip(),'definition':meaning.strip(),'separator':separator}


def cluster_start(text):
    lines=text.splitlines(keepends=True);offsets=[];offset=0
    for line in lines:offsets.append(offset);offset+=len(line)
    anchored=[n for n,line in enumerate(lines)if definition(line)]
    if not anchored:return None
    first=anchored[0]
    # Only contiguous earlier definitions with sequential numeric labels join.
    following=definition(lines[first])
    while first:
        prior=definition(lines[first-1],True)
        if not prior or not prior['label']or not following['label']:break
        if int(prior['label'])+1!=int(following['label']):break
        first-=1;following=prior
    return offsets[first]


def terms_in_confirmed_cluster(text):
    # Only called after an explicit, projection-bound definition tail is selected.
    # Some audited tails serialize several complete definitions on one line.
    pieces=re.split(r'(?=[（(][ \u3000]*注[ \u3000]*[0-9０-９]*[ \u3000]*[)）])',text)
    result={}
    for piece in pieces:
        for line in piece.splitlines():
            row=definition(line,True,True)
            if row:
                if row['label'] in result:raise ValueError('Duplicate bound note definition')
                result[row['label']]=row['term']
    return result


def separate_lines(value):
    """Split a reviewed merged definition tail, retaining all exact inline content."""
    import html
    from model import Projection
    from semantic_lines import split_before
    raw=value['html']if isinstance(value,dict)else html.escape(value).replace('\n','<br/>')
    from notice_layout import html_lines
    fragments=html_lines(raw)
    labels=re.findall(r'[（(][ \u3000]*注[ \u3000]*[0-9０-９]*[ \u3000]*[)）]',Projection(value).text)
    if len(labels)!=len(set(labels)):raise ValueError('Ambiguous merged definition labels')
    terms=terms_in_confirmed_cluster(Projection(value).text)
    if len(labels)!=len(terms):raise ValueError('Merged note tail contains a non-definition')
    return {'html':'<br/>'.join(split_before(fragments,labels))}


def presentation(value, separate=False):
    """Prepare only definition-role colons in an already bound note tail.

    Explicit line splitting is validated by separate_lines. Within each line,
    only a leading definition's first separator is styled. Colons later in
    its explanation (times, URLs, ratios, code, etc.) remain literal. Offsets
    refer to this prepared tail, never to a rewritten editorial field.
    """
    import html
    from model import Projection
    source = separate_lines(value) if separate else value
    raw = source['html'] if isinstance(source, dict) else html.escape(source).replace('\n', '<br/>')
    projection = Projection({'html': raw})
    edits, records = [], []
    offset = 0
    for line in projection.text.splitlines(keepends=True):
        match = LABEL.fullmatch(line.rstrip('\r\n'))
        if match:
            body = match[2]
            body_start = offset + match.start(2)
            # A redundant separator after the label is an explicitly supported
            # bound-tail convention. It does not authorize rewriting the rest.
            label_colon = body_start if body.startswith((':', '：')) else None
            skip = len(body) - len(body.lstrip(':： \u3000')) if label_colon is not None else 0
            rest = body[skip:]
            sep = re.search(r'[:：]', rest)
            colon = None
            literal = False
            if sep and rest[:sep.start()].strip() and rest[sep.end():].strip():
                pos = sep.start()
                literal = (pos > 0 and pos+1 < len(rest)
                           and rest[pos-1].isdigit() and rest[pos+1].isdigit()) or rest[pos+1:pos+3] == '//'
                if not literal:
                    colon = body_start + skip + pos
            row = definition(line, True, True)
            if literal:
                space = re.fullmatch(r'(\S+)[ \u3000]+(\S.*)', rest)
                row = dict(label=match[1],term=space[1],definition=space[2],separator='space') if space else None
            if row:
                records.append(dict(label=row['label'],term=row['term'],definition=row['definition'],
                                    start=offset+match.start(),end=offset+len(line.rstrip('\r\n')),
                                    colon=colon,label_colon=label_colon))
                for point in (label_colon, colon):
                    if point is None: continue
                    if projection.overlaps_ruby(point, point+1):
                        raise ValueError('Definition separator overlaps ruby')
                    a,b = projection.raw_span(point, point+1)
                    edits.append((a,b,'<span data-note-definition-colon="true">：</span>'))
        offset += len(line)
    for a,b,replacement in reversed(edits):
        raw = raw[:a]+replacement+raw[b:]
    result = {'html':raw}
    final = Projection(result)
    points = {p for row in records for p in (row['colon'],row['label_colon']) if p is not None}
    expected = ''.join('：' if n in points else c for n,c in enumerate(projection.text))
    if final.text != expected or final.ruby != projection.ruby:
        raise ValueError('Note presentation changed unrelated text or ruby')
    from label_separators import prepare as label_separators
    result,_=label_separators(result)
    return result, records
