"""Exact literal combination cells with intact ruby only inside their values."""
import re
from model import Projection
from example_layout import slice_inline


def parse(values,keys,syntax='key_colon_value'):
    pattern={'key_colon_value':r'([A-Za-zア-エ])([：:])([^\s：:]+)',
             'circled_key_space_value':r'([①②③④])( )([^\s]+)',
             'key_fullwidth_value':r'([A-Za-zア-エ①-⑳])(\u3000)([^\s]+)',
             'key_dash_value':r'([A-Za-zア-エ])(－)([①-⑳])'}.get(syntax)
    if pattern is None:raise ValueError('Unknown combination cell syntax')
    separator=r'\u3000{1,2}(?=['+re.escape(''.join(keys))+r']\u3000)' if syntax=='key_fullwidth_value' else '\u3000'
    result=[]
    for value in values:
        projection=Projection(value);text=projection.text;spans=[];start=0
        for split in re.finditer(separator,text):
            spans.append((start,split.start()));start=split.end()
        spans.append((start,len(text)))
        matches=[re.fullmatch(pattern,text[a:b]) for a,b in spans]
        if len(matches)!=len(keys) or not all(matches) or [m[1] for m in matches]!=keys:
            raise ValueError('Combination keys/value cells differ from binding')
        value_spans=[(a+m.start(3),a+m.end(3)) for (a,b),m in zip(spans,matches)]
        if any(not any(a<=r['start']<r['end']<=b for a,b in value_spans) for r in projection.ruby):
            raise ValueError('Combination ruby must stay inside one literal value')
        def fragment(a,b):
            return text[a:b] if isinstance(value,str) else {'html':slice_inline(value['html'],a,b)}
        row=[]
        for (a,b),m in zip(spans,matches):
            row.append(dict(key=m[1],separator=m[2],value=fragment(a+m.start(3),a+m.end(3)),whole=fragment(a,b)))
        result.append(row)
    return result
