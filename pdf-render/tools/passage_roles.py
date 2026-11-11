"""Bound passage introductions and restored links to existing note definitions."""
import hashlib
import html
import re
from bs4 import BeautifulSoup, NavigableString, Tag
from model import Projection
from section_layout import flow_lines


def paragraph_breaks_tex(conv, value, tex, binding):
    """Restore exact, source-reviewed paragraph starts without editing content."""
    projection = Projection(value)
    if hashlib.sha256(projection.text.encode()).hexdigest() != binding['projection_sha256']:
        raise ValueError('Stale paragraph-break projection')
    for start in binding['starts']:
        offset, prefix = start['offset'], start['prefix']
        if offset <= 0 or not prefix or '\n' in prefix or projection.text[offset:offset + len(prefix)] != prefix:
            raise ValueError('Stale paragraph start')
        if any(r['start'] < offset < r['end'] for r in projection.ruby):
            raise ValueError('Paragraph start splits ruby')
        # A reviewed prefix is a text locator, not a replacement for its inline
        # content. Keep the complete ruby that now belongs to that exact span.
        end = offset + len(prefix)
        for ruby in projection.ruby:
            if ruby['start'] < end < ruby['end']:
                end = ruby['end']
        fragment_value = projection.text[offset:end]
        if isinstance(value, dict):
            from notice_layout import html_lines
            from example_layout import slice_inline
            cursor = 0
            for raw in html_lines(value['html']):
                line = Projection({'html': raw}).text
                at = projection.text.find(line, cursor)
                if at < cursor or projection.text[cursor:at].strip():
                    raise ValueError('Paragraph prefix line changed projection')
                cursor = at + len(line)
                if at <= offset < cursor:
                    if end > cursor:
                        raise ValueError('Paragraph prefix crosses a structural boundary')
                    fragment_value = {'html': slice_inline(raw, offset-at, end-at)}
                    break
            else:
                raise ValueError('Paragraph prefix has no exact inline line')
        feature_count = len(conv.features)
        try:
            fragment = conv.value(fragment_value, 'body')
        finally:
            # This is a lookup probe; the full passage already owns its ruby
            # and other semantic feature records.
            del conv.features[feature_count:]
        if tex.count(fragment) != 1:
            raise ValueError('Paragraph prefix must select one rendered span')
        tex = tex.replace(fragment, r'\Para\indent ' + fragment, 1)
    conv.features.append({'kind': 'restored_paragraph_breaks', 'starts': binding['starts'], 'state': binding['state']})
    return tex


def introduction_tex(conv, value, tex, binding, notes=None):
    p=Projection(value)
    if hashlib.sha256(p.text.encode()).hexdigest()!=binding['projection_sha256']:
        raise ValueError('Stale introduction projection')
    text=binding['text']
    if p.text.count(text)!=1 or '\n'in text:raise ValueError('Introduction must be one exact complete paragraph')
    start=p.text.index(text);end=start+len(text)
    prefix=p.text[:start].split('\n')[-1]
    inline_label=binding.get('allow_inline_label',False) and re.fullmatch(r'[（(][0-9０-９]{1,2}[）)]\s*',prefix)
    suffix=p.text[end:].split('\n')[0]
    inline_body=binding.get('following_prefix')
    if inline_body and (not text.endswith('。') or not suffix.lstrip().startswith(inline_body) or p.text.count(inline_body)!=1):raise ValueError('Changed bound inline introduction boundary')
    if (prefix.strip() and not inline_label)or (suffix.strip() and not inline_body):raise ValueError('Introduction is not a complete line')
    if any(r['start']<start<r['end']or r['start']<end<r['end']for r in p.ruby):raise ValueError('Introduction splits ruby')
    rs,re_=p.mapping[start][0],p.mapping[end-1][1]
    for r in p.ruby:
        if r['start']==start:rs=p.raw.rfind('<ruby',0,rs+1)
        if r['end']==end:re_=p.raw.find('</ruby>',re_)+7
    content=p.raw[rs:re_]
    if Projection({'html':content}if isinstance(value,dict)else content).text!=text:raise ValueError('Introduction crosses markup boundary')
    if not isinstance(value,dict):content=html.escape(content)
    feature_count=len(conv.features)
    # Match the actual passage preparation, including N5 punctuation glue and
    # intact ruby word groups. Option context deliberately omits that glue.
    fragment_value={'html':content}
    if notes:
        _,definitions=conv.split_notes(value,notes)
        fragment_value=conv.note_markers(fragment_value,definitions)
    fragment=conv.value(fragment_value,'body')
    del conv.features[feature_count:]
    if tex.count(fragment)!=1:raise ValueError('Introduction must match exactly one rendered span')
    macro={'document':r'\DocumentIntroduction{','passage':r'\PassageIntroduction{'}[binding['role']]
    conv.features.append({'kind':'passage_introduction','text':text,'role':binding['role'],'state':binding['state']})
    # Plain email lines use EmailLine rather than Para. Explicit boundaries
    # keep an introduction outside the documentary frame in either encoding.
    return tex.replace(fragment,r'\Para '+macro+fragment+'}'+r'\Para ',1)


def detach_vertical_introduction(body, binding):
    """Take only the first complete paragraph after an existing vertical label.

    The caller validates the full original projection through introduction_tex;
    this narrower structural check prevents pulling later body text outside.
    """
    text = binding['text']
    if binding.get('following_prefix'):
        raise ValueError('Vertical introduction requires a separate complete paragraph')
    if isinstance(body, str):
        prefix = body[:len(body)-len(body.lstrip('\n'))]
        rest = body[len(prefix):]
        if not rest.startswith(text+'\n'):
            raise ValueError('Vertical introduction must lead the body')
        return text, rest[len(text)+1:]
    soup = BeautifulSoup(body['html'], 'html.parser')
    roots = [n for n in soup.children if Projection({'html': str(n)}).text.strip()]
    if (not roots or not isinstance(roots[0], Tag) or roots[0].name != 'p'
            or roots[0].find(['p','div','table','section','br'])
            or Projection({'html': str(roots[0])}).text.strip('\n') != text):
        raise ValueError('Vertical introduction must be the first complete paragraph')
    intro = {'html': roots[0].decode_contents()}
    roots[0].extract()
    return intro, {'html': str(soup)}


def keep_with_previous_tex(conv, value, tex, binding):
    """Keep exact, authored trailing paragraphs with preceding body text."""
    p = Projection(value)
    if hashlib.sha256(p.text.encode()).hexdigest() != binding['projection_sha256']:
        raise ValueError('Stale paragraph-keep projection')
    for text in binding['paragraphs']:
        if '\n' in text or p.text.count(text) != 1:
            raise ValueError('Paragraph keep must name one complete line')
        start = p.text.index(text); end = start + len(text)
        if not p.text[:start].strip() or p.text[:start].split('\n')[-1].strip() or p.text[end:].split('\n')[0].strip():
            raise ValueError('Paragraph keep requires a separate preceding paragraph')
        if any(r['start'] < start < r['end'] or r['start'] < end < r['end'] for r in p.ruby):
            raise ValueError('Paragraph keep splits ruby')
        rs, re_ = p.mapping[start][0], p.mapping[end - 1][1]
        for r in p.ruby:
            if r['start'] == start: rs = p.raw.rfind('<ruby', 0, rs + 1)
            if r['end'] == end: re_ = p.raw.find('</ruby>', re_) + 7
        raw = p.raw[rs:re_]
        if Projection({'html': raw} if isinstance(value, dict) else raw).text != text:
            raise ValueError('Paragraph keep crosses markup boundary')
        feature_count = len(conv.features)
        fragment = conv.value({'html': raw if isinstance(value, dict) else html.escape(raw)}, 'option')
        del conv.features[feature_count:]
        pattern = r'\\Para\s*' + re.escape(fragment)
        if len(re.findall(pattern, tex)) != 1:
            raise ValueError('Paragraph keep must select one rendered paragraph boundary')
        tex = re.sub(pattern, lambda _: r'\KeepWithPreviousParagraph{' + fragment + '}', tex, count=1)
    conv.features.append({'kind': 'bound_paragraph_keep', 'paragraphs': binding['paragraphs'], 'state': binding['state']})
    return tex


def restore_note_links(before, after, anchors):
    """Wrap exact spans; generated marker text comes only from an existing definition."""
    p=Projection(before);definitions=Projection(after).text;replacements=[]
    for a in anchors:
        start,end=a['term_start'],a['term_end'];term=a['term'];label=a['label']
        if not 0<=start<end<=len(p.text)or p.text[start:end]!=term:raise ValueError('Stale restored note term')
        if len(re.findall(re.escape(label)+r'\s*'+re.escape(a['definition_term'])+r'\s*[:：]',definitions))!=1:
            raise ValueError('Restored note link must name one existing definition')
        if any(r['start']<start<r['end']or r['start']<end<r['end']for r in p.ruby):raise ValueError('Restored note link splits ruby')
        if not p.mapping[start]or not p.mapping[end-1]:raise ValueError('Unmapped restored note term')
        rs,re_=p.mapping[start][0],p.mapping[end-1][1]
        for r in p.ruby:
            if r['start']==start:rs=p.raw.rfind('<ruby',0,rs+1)
            if r['end']==end:re_=p.raw.find('</ruby>',re_)+7
        raw=p.raw[rs:re_]
        if Projection({'html':raw} if isinstance(before,dict)else raw).text!=term:raise ValueError('Restored note link crosses markup boundary')
        if not isinstance(before,dict):raw=html.escape(raw)
        replacements.append((rs,re_,'<span data-note-label="'+html.escape(label,quote=True)+'">'+raw+'</span>'))
    replacements.sort()
    if any(a[1]>b[0]for a,b in zip(replacements,replacements[1:])):raise ValueError('Overlapping restored note links')
    if isinstance(before,dict):
        raw=p.raw
        for start,end,replacement in reversed(replacements):raw=raw[:start]+replacement+raw[end:]
    else:
        chunks=[];last=0
        for start,end,replacement in replacements:chunks.extend([html.escape(p.raw[last:start]),replacement]);last=end
        chunks.append(html.escape(p.raw[last:]));raw=''.join(chunks).replace('\n','<br/>')
    result={'html':raw}
    if Projection(result).text!=p.text:raise ValueError('Restored note link changed protected projection')
    return result
