"""Bound scene and omission paragraph roles; characters and ruby stay exact."""
import copy,html,re
from bs4 import BeautifulSoup, NavigableString
from model import Projection

DEFAULTS = {'scene': {'indent_em': .5}, 'omission': {'indent_em': 1}}
ATTRIBUTION = re.compile(r'[（(].+(?:による|より)[。.]?[）)]')


def omission_pair(soup, text, after_text):
    if not re.fullmatch(r'[（(](?:中略|前略|後略)[）)]',text):
        raise ValueError('Inline omission requires an existing complete omission marker')
    blocks=[n for n in soup.find_all('p') if Projection({'html':str(n)}).text.strip()==text]
    if len(blocks)!=1:raise ValueError('Inline omission requires one complete paragraph')
    block=blocks[0];previous=block.previous_sibling
    while isinstance(previous,NavigableString) and not previous.strip():previous=previous.previous_sibling
    if previous is None or getattr(previous,'name',None)!='p' or block.attrs or previous.attrs:
        raise ValueError('Inline omission requires adjacent plain paragraphs')
    if block.find(['p','div','br','table','section']) or previous.find(['p','div','br','table','section']):
        raise ValueError('Inline omission cannot merge structural blocks')
    if not after_text or Projection({'html':str(previous)}).text.strip()!=after_text:
        raise ValueError('Inline omission has a stale preceding paragraph')
    return block,previous


def join_inline_omissions(soup):
    """Move only a source-bound omission into its exact preceding paragraph."""
    for node in list(soup.select('span[data-inline-omission-after]')):
        text=Projection({'html':str(node)}).text;after_text=node['data-inline-omission-after']
        if node.get('data-paragraph-role')!='omission':raise ValueError('Invalid inline omission role')
        block,previous=omission_pair(soup,text,after_text)
        if list(block.children)!=[node]:raise ValueError('Inline omission has unexpected surrounding markup')
        before=Projection({'html':str(soup)})
        pattern=re.escape(after_text)+r'\n+'+re.escape(text)
        if len(re.findall(pattern,before.text))!=1:raise ValueError('Ambiguous inline omission boundary')
        expected=re.sub(pattern,lambda m:after_text+text,before.text,count=1)
        previous.append(node.extract());block.decompose()
        current=Projection({'html':str(soup)})
        ruby=lambda p:[(r['base'],r['reading']) for r in p.ruby]
        if current.text!=expected or ruby(before)!=ruby(current):raise ValueError('Inline omission changed protected content')


def prepare(value, paragraphs):
    raw = value['html'] if isinstance(value, dict) else html.escape(value).replace('\n', '<br/>')
    original = Projection({'html':raw})
    for spec in paragraphs:
        text, role = spec['text'], spec['role']
        if role not in {*DEFAULTS, 'citation', 'signature'} or '\n' in text or not text:
            raise ValueError('Unknown or non-inline paragraph role')
        if role=='citation' and not ATTRIBUTION.fullmatch(text):
            raise ValueError('Citation role requires one exact source attribution')
        if role=='signature':
            soup=BeautifulSoup(raw,'html.parser')
            ends=[n for n in soup.find_all(['p','div'])
                  if not n.find(['p','div','table','section'])
                  and Projection({'html':str(n)}).text.rstrip().endswith(text)]
            if len(text)>80 or len(ends)!=1:
                raise ValueError('Signature requires one exact terminal simple paragraph span')
        inline_after=spec.get('inline_after')
        if inline_after is not None:
            if role!='omission' or spec.get('break_before') or 'frame_placement' in spec:
                raise ValueError('Inline omission conflicts with another paragraph role')
            omission_pair(BeautifulSoup(raw,'html.parser'),text,inline_after)
        outside = spec.get('frame_placement') == 'outside'
        if 'frame_placement' in spec and (not outside or role != 'citation'):
            raise ValueError('Exterior frame placement requires a citation')
        if outside:
            soup = BeautifulSoup(raw, 'html.parser')
            blocks = [n for n in soup.find_all(['p','div'])
                      if Projection({'html':str(n)}).text.strip() == text
                      and not n.find(['p','div','table','section'])]
            if len(blocks) != 1:
                raise ValueError('Exterior citation requires one complete inline block')
        p = Projection({'html':raw})
        if p.text.count(text) != 1:
            raise ValueError('Paragraph role must match one exact phrase')
        start = p.text.index(text); end = start + len(text)
        if any(r['start'] < start < r['end'] or r['start'] < end < r['end'] for r in p.ruby):
            raise ValueError('Paragraph role splits ruby')
        lo, hi = p.mapping[start][0], p.mapping[end-1][1]
        for r in p.ruby:
            if r['start'] == start: lo = raw.rfind('<ruby', 0, lo+1)
            if r['end'] == end: hi = raw.find('</ruby>', hi)+7
        fragment = raw[lo:hi]
        if Projection({'html':fragment}).text != text:
            raise ValueError('Paragraph role crosses an unbalanced structural boundary')
        prefix = ' data-paragraph-break-before="true"' if spec.get('break_before',False) else ''
        placement = ' data-frame-placement="outside"' if outside else ''
        flow=' data-inline-omission-after="'+html.escape(inline_after,quote=True)+'"' if inline_after is not None else ''
        if 'preferred_break_after' in spec:
            token=spec['preferred_break_after']
            if role!='citation' or not token or text.count(token)!=1:raise ValueError('Citation boundary must be exact and unique')
            flow+=' data-citation-break-after="'+html.escape(token,quote=True)+'"'
        raw = raw[:lo] + '<span data-paragraph-role="'+role+'"'+prefix+placement+flow+'>'+fragment+'</span>' + raw[hi:]
    result = {'html':raw}; after = Projection(result)
    if original.text != after.text or original.ruby != after.ruby:
        raise ValueError('Paragraph role altered content or ruby')
    return result


def render(conv, node, context):
    role = node['data-paragraph-role']
    if role in ['citation','signature']:
        text=Projection({'html':str(node)}).text
        if role=='citation' and not ATTRIBUTION.fullmatch(text):
            raise ValueError('Invalid citation paragraph')
        body=''.join(conv.node(n,context)for n in node.children)
        if node.has_attr('data-citation-break-after'):
            from example_layout import slice_inline
            token=node['data-citation-break-after'];at=text.index(token)+len(token);raw=node.decode_contents()
            chunks=[conv.value({'html':slice_inline(raw,a,b)},context) for a,b in [(0,at),(at,len(text))]]
            # Each bibliographic part stays together when it fits. A part wider
            # than the available line retains normal Japanese wrapping.
            body=r'\allowbreak{}'.join(r'{\sbox0{'+part+r'}\ifdim\wd0<\linewidth\usebox0\else '+part+r'\fi}' for part in chunks)
            conv.features.append({'kind':'preferred_citation_boundary','after':token,'text':text})
        conv.features.append({'kind':'bound_paragraph_role','role':role,'text':text,
                              'parameters':{'align':'right','keep_with_previous':True}})
        result = r'\par\nobreak\DocumentLine{r}{0}{4}{0}{'+body+'}'
        if node.get('data-frame-placement') == 'outside':
            conv.features.append({'kind':'bound_exterior_citation','text':text})
            result = r'\ExteriorCitationStart{}'+result+r'\ExteriorCitationEnd{}'
        return result
    params = getattr(conv, 'paragraph_roles', DEFAULTS).get(role)
    if not params or set(params) != {'indent_em'} or isinstance(params['indent_em'], bool) or not 0 <= params['indent_em'] <= 2:
        raise ValueError('Invalid paragraph role defaults')
    body = ''.join(conv.node(n, context) for n in node.children)
    conv.features.append({'kind':'bound_paragraph_role','role':role,'text':Projection({'html':str(node)}).text,'parameters':params})
    if node.has_attr('data-inline-omission-after'):
        if role!='omission':raise ValueError('Invalid inline omission role')
        conv.features[-1]['flow']='inline_after_previous'
        return r'\hspace{'+str(params['indent_em'])+'em}'+body
    command = r'\SceneParagraph{' if role=='scene' else r'\RoleParagraph{'
    return (r'\par ' if node.get('data-paragraph-break-before')=='true' else '')+command+str(params['indent_em'])+'}{'+body+'}'


def email_metadata(conv, value, tex, spec):
    """Align exact existing label/colon/value lines; never rewrite their characters."""
    rows = spec['rows']; lines = [r['label']+r['colon']+r['value'] for r in rows]
    p = Projection(value)
    if not rows or any(p.text.splitlines().count(line) != 1 for line in lines):
        raise ValueError('Email metadata requires exact unique existing lines')
    if any(r['colon'] not in [':','：'] or not r['label'] or '\n' in r['value'] for r in rows):
        raise ValueError('Invalid metadata label or separator')
    offsets=[p.text.index(line) for line in lines]
    if offsets!=sorted(offsets) or any(p.text[a+len(line):b].strip() for a,b,line in zip(offsets,offsets[1:],lines)):
        raise ValueError('Email metadata rows must be consecutive')
    # Match each actual inline fragment so metadata containing frozen ruby does
    # not fall back to its plain projection. Paragraph furniture stays outside.
    fragments=lines;labels=[r['label'] for r in rows];values=[r['value'] for r in rows]
    if isinstance(value,dict):
        from notice_layout import html_lines
        from example_layout import slice_inline
        raw=value['html']
        if not BeautifulSoup(raw,'html.parser').find(['p','div','br','center']):raw=raw.replace('\n','<br/>')
        available=html_lines(raw);fragments=[];labels=[];values=[]
        for row,line in zip(rows,lines):
            hits=[x for x in available if Projection({'html':x}).text==line]
            if len(hits)!=1:raise ValueError('Email metadata requires one complete rich inline line')
            fragment=hits[0];label_end=len(row['label']);value_start=label_end+len(row['colon'])
            label=slice_inline(fragment,0,label_end)
            # Also validate the separator boundary against a whole ruby group.
            slice_inline(fragment,label_end,value_start)
            rendered_value={'html':slice_inline(fragment,value_start,len(line))} if row['value'] else ''
            fragments.append({'html':fragment});values.append(rendered_value)
            labels.append({'html':label} if BeautifulSoup(label,'html.parser').find() else row['label'])
    # Audited plain emails may serialize single or blank lines. Match only
    # their native paragraph separators, never intervening body text.
    # Exact matching and replacement revisit glyphs already emitted in tex.
    # Keep their temporary feature records out of the emitted-content ledger.
    matcher=copy.copy(conv);matcher.features=[]
    pattern=r'(?:\s*\\(?:Para|EmailLine)\s*)+'.join(re.escape(matcher.value(line,'email')) for line in fragments)
    matches=list(re.finditer(pattern,tex))
    if len(matches) != 1:
        raise ValueError('Email metadata does not match one contiguous rendered block')
    width=spec.get('label_width_em',3)
    if isinstance(width,bool) or not 2<=width<=5:raise ValueError('Invalid metadata label width')
    body=''.join(r'\EmailMetadataRow{'+str(width)+'}{'+(matcher.value(label,'option') if isinstance(label,dict) else r'\hfill '.join(matcher.text(c)for c in label))+'}{'+matcher.text(r['colon'])+'}{'+matcher.value(v,'option')+'}'for r,label,v in zip(rows,labels,values))
    conv.features.append({'kind':'email_metadata_alignment','rows':rows,'label_width_em':width})
    return re.sub(pattern,lambda _:r'{\parindent=0pt\parskip=0pt '+body+'}',tex,count=1)
