"""Separate an exact terminal introduction from its stored instruction field."""
import html
from bs4 import BeautifulSoup,Tag
from model import Projection,digest
from section_layout import flow_lines


def split(value,binding,source_value=None):
    source=value if source_value is None else source_value
    if digest(source)!=binding['content_sha256']:
        raise ValueError('Stale heading introduction binding')
    text=binding['text']
    if not text or '\n' in text or binding['role'] not in ['passage','document']:
        raise ValueError('Invalid heading introduction role')
    original,current=Projection(source),Projection(value)
    compact=lambda p:''.join(p.text.split())
    ruby=lambda p:[(r['base'],r['reading']) for r in p.ruby]
    if compact(original)!=compact(current) or ruby(original)!=ruby(current):
        raise ValueError('Prior heading preparation changed text or ruby')
    inline=binding.get('inline_terminal',False)
    if type(inline)is not bool:raise ValueError('Inline terminal introduction requires a boolean opt-in')
    if original.text.count(text)!=1 or not original.text.rstrip().endswith(text):
        raise ValueError('Heading introduction must be one unique terminal passage')
    if not inline and original.text.rstrip().splitlines()[-1].strip()!=text:
        raise ValueError('Heading introduction must be one complete terminal paragraph')
    raw=html.escape(value).replace('\n','<br/>') if isinstance(value,str) else value['html']
    nodes=[n for n in flow_lines(list(BeautifulSoup(raw,'html.parser').children))
           if Projection({'html':str(n)}).text.strip()]
    if any(not isinstance(n,Tag) or n.name!='p' or n.find(['p','div','table','section','br']) for n in nodes):
        raise ValueError('Heading introduction requires simple complete paragraphs')
    if inline:
        if len(nodes)!=1:raise ValueError('Inline terminal introduction requires one flattened paragraph')
        raw=nodes[0].decode_contents();p=Projection({'html':raw});start=p.text.find(text)
        original_start=original.text.find(text)
        for plain,offset in [(original.text,original_start),(p.text,start)]:
            if offset<=0 or not plain[offset-1].isspace() or not plain[:offset].rstrip().endswith('。'):
                raise ValueError('Inline introduction requires whitespace after a complete instruction sentence')
        if p.text.count(text)!=1 or not p.text.rstrip().endswith(text):
            raise ValueError('Prepared heading lost its terminal introduction')
        from example_layout import slice_inline
        heading={'html':slice_inline(raw,0,start)}
        intro={'html':slice_inline(raw,start,start+len(text))}
    else:
        if len(nodes)<2 or Projection({'html':str(nodes[-1])}).text.strip()!=text:
            raise ValueError('Prepared heading lost its terminal introduction boundary')
        heading={'html':'<br/>'.join(n.decode_contents() for n in nodes[:-1])}
        intro={'html':nodes[-1].decode_contents()}
    left,right=Projection(heading),Projection(intro)
    if not left.text.strip() or compact(left)+compact(right)!=compact(original) or ruby(left)+ruby(right)!=ruby(original):
        raise ValueError('Heading introduction split changed protected content')
    return heading,intro
