"""Explicit document-list roles. Never infer bullets from a circle alone."""
import re
from bs4 import BeautifulSoup, NavigableString, Tag

DEFAULTS = {
    'item': {'scale': .55, 'raise_em': .12, 'gap_em': .30},
    'heading': {'scale': .75, 'raise_em': .06, 'gap_em': .20},
}


def regions(soup):
    """Complete explicit lines inside plain flow, paragraphs and table cells."""
    containers=[soup]+soup.find_all(['p','div','td','th','li','center','section'])
    block={'p','div','table','tr','td','th','ul','ol','li','section','center','h1','h2','h3','h4'}
    for parent in containers:
        pending=[]
        for node in list(parent.children)+[None]:
            boundary=(node is None or isinstance(node,Tag)and
                      (node.name in block or node.name=='br' or node.has_attr('data-authored-plain-break')))
            if boundary:
                if pending:
                    yield pending
                    pending=[]
            else:
                pending.append(node)


def candidates(value):
    """Discover candidates for human authorship; this never activates a role."""
    from model import Projection
    import html
    raw=value['html']if isinstance(value,dict)else html.escape(value).replace('\n','<br>')
    soup=BeautifulSoup(raw,'html.parser')
    return [text for nodes in regions(soup)
            if (text:=Projection({'html':''.join(map(str,nodes))}).text.strip()).startswith('●')]


def prepare(soup, entries):
    """Select exact authored complete lines, including lines inside rich cells."""
    from model import Projection
    before=Projection({'html':str(soup)})
    if not entries or len({e['text']for e in entries})!=len(entries):
        raise ValueError('Document bullet lines require unique complete text')
    available=list(regions(soup))
    for entry in entries:
        if (set(entry)!={'text','role'} or entry['role']not in DEFAULTS
                or not entry['text'].startswith('●') or entry['text'].count('●')!=1):
            raise ValueError('Document bullet line requires one existing leading circle and a role')
        matches=[nodes for nodes in available
                 if Projection({'html':''.join(map(str,nodes))}).text.strip()==entry['text']]
        if len(matches)!=1:
            raise ValueError('Document bullet must select one complete explicit line')
        nodes=matches[0]
        if any(isinstance(n,Tag)and n.find(['table','p','div','ul','ol','br'])for n in nodes):
            raise ValueError('Document bullet cannot absorb nested blocks or another list')
        span=soup.new_tag('span');span['data-document-bullet']=entry['role']
        nodes[0].insert_before(span)
        for node in nodes:span.append(node.extract())
    after=Projection({'html':str(soup)})
    if before.text!=after.text or before.ruby!=after.ruby:
        raise ValueError('Document bullet roles changed text or ruby')


def present(conv, plain, body, role, context):
    if context not in ['notice', 'notice_cell'] or role not in DEFAULTS:
        raise ValueError('Document bullet requires a bound notice role')
    if not plain.startswith('●') or plain.count('●') != 1 or body.count('●') != 1:
        raise ValueError('Document bullet must select one existing leading circle')
    values = getattr(conv, 'document_bullets', DEFAULTS)[role]
    bounds = {'scale': (.3, 1), 'raise_em': (0, .3), 'gap_em': (0, .8)}
    if set(values) != set(bounds) or any(isinstance(values[k], bool) or not isinstance(values[k], (int, float)) or not a <= values[k] <= b for k, (a, b) in bounds.items()):
        raise ValueError('Invalid document bullet dimensions')
    # The marker owns this one separator, including an existing fullwidth gap.
    # Its fixed gutter is also the continuation indent. Keep it with its text.
    width = round(values['scale'] + values['gap_em'], 4)
    marker = (r'\makebox[' + str(width) + r'em][l]{\raisebox{' + str(values['raise_em']) + r'em}{\scalebox{'
              + str(values['scale']) + r'}{●}}}\nobreak{}')
    body = re.sub(r'●(?:[ \u3000\t]|\\hskip [0-9.]+em\\relax )*', lambda _: marker, body, count=1)
    conv.features.append({'kind': 'document_bullet', 'role': role, 'context': context, 'text': plain,
                          'effective': values, 'gutter_em': width, 'canonical_glyph': '●'})
    return body, width
