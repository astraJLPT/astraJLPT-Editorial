"""Resolve the selected rule family for explicitly authored email documents."""
from model import merge_defaults


def prepare_padding(value):
    """Present exact paragraph-leading U+3000 as padding, keeping canonical text."""
    import html
    from model import Projection
    original=Projection(value)
    offsets=[n for n,ch in enumerate(original.text) if ch=='\u3000' and
             (n==0 or original.text[n-1]=='\n') and n+1<len(original.text) and not original.text[n+1].isspace()]
    if not offsets:return value,[]
    raw=value['html'] if isinstance(value,dict) else html.escape(value)
    projected=Projection({'html':raw});assert projected.text==original.text
    spans=[]
    for offset in offsets:
        if projected.overlaps_ruby(offset,offset+1):raise ValueError('Email padding overlaps ruby')
        start,end=projected.raw_span(offset,offset+1)
        if raw[start:end]!='\u3000':raise ValueError('Email padding must be a literal paragraph-leading space')
        spans.append((start,end))
    for start,end in reversed(spans):
        raw=raw[:start]+'<span data-email-paragraph-padding="zero">\u3000</span>'+raw[end:]
    result={'html':raw}
    if isinstance(value,str):
        from plain_rich_breaks import prepare
        result=prepare(result)
    after=Projection(result)
    if after.text!=original.text or after.ruby!=original.ruby:raise ValueError('Email padding changed text or ruby')
    return result,offsets


def headers(model):
    style = model['style']
    family = style.get('email_family', {})
    result = {key: merge_defaults(family, value)
              for key, value in style.get('email_headers', {}).items()}
    for section in model['document']['sections']:
        for item in section['items']:
            key = item['id']
            binding = model['layout']['items'][key].get('structured_document')
            if (key in result or not binding or binding['genre'] != 'email'
                    or style.get('content_frames', {}).get(key) != 'horizontal_rules'):
                continue
            if not family.get('rule_set'):
                raise ValueError('Structured email needs its selected shared rule family')
            # Reuse the explicit genre's exact content and source binding. The
            # normal email path still checks both before emitting any rules.
            result[key] = merge_defaults(family, {
                'content_sha256': binding['content_sha256'],
                'evidence': binding['evidence']})
    return result
