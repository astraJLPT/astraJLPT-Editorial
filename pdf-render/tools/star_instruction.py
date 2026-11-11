"""Recognize only the administrative instruction, never a four-slot exercise."""
import re
from model import Projection
from example_layout import slice_inline


def prepare(raw):
    p=Projection({'html':raw})
    m=re.match(r'^2[.．]\s*([_＿]*\s*★\s*[_＿]*)\s*に入る番号を解答用紙にマーク',p.text)
    if not m:return raw,False
    a,b=m.span(1)
    # The selected range consists solely of the one marker and display strokes.
    if re.sub(r'[_＿\s★]','',p.text[a:b]) or p.text[a:b].count('★')!=1:
        raise ValueError('Invalid administrative STAR marker')
    before=slice_inline(raw,0,a)if a else''
    after=slice_inline(raw,b,len(p.text))if b<len(p.text)else''
    result=before+'<span data-star-instruction-symbol="true">★</span>'+after
    q=Projection({'html':result})
    if q.text!=p.text[:a]+'★'+p.text[b:]:raise ValueError('Administrative STAR changed words')
    if [(r['base'],r['reading'])for r in p.ruby]!=[(r['base'],r['reading'])for r in q.ruby]:
        raise ValueError('Administrative STAR changed ruby')
    return result,True
