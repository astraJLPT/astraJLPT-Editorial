"""Slice already-presented inline HTML without losing zero-text furniture.

The upstream canonical slicer intentionally drops empty tags. Web presentation
also has empty spans with real geometry (blank interiors, instruction gaps).
This adapter retains them at their projected boundary; ruby remains atomic.
"""
import html
from bs4 import BeautifulSoup, NavigableString
from model import Projection


def slice_inline(raw,start,end):
    projection=Projection({'html':raw})
    if not 0<=start<end<=len(projection.text):raise ValueError('Invalid presented inline span')
    if any(r['start']<p<r['end'] for r in projection.ruby for p in (start,end)):
        raise ValueError('Presented span splits ruby')
    cursor=0
    def visit(node):
        nonlocal cursor
        if isinstance(node,NavigableString):
            a=cursor;cursor+=len(str(node))
            return html.escape(str(node)[max(start-a,0):max(min(end-a,len(str(node))),0)]) if a<end and cursor>start else ''
        if node.name=='ruby':
            a=cursor;cursor+=len(Projection({'html':str(node)}).text)
            return str(node) if start<=a and cursor<=end else ''
        if node.name in ('br','p','div','table','rt','rp'):raise ValueError('Expected one presented inline fragment')
        if not node.contents:return str(node) if start<=cursor<end else ''
        children=''.join(visit(child) for child in node.children)
        if not children:return ''
        clone=BeautifulSoup(str(node),'html.parser').find();clone.clear()
        for child in list(BeautifulSoup(children,'html.parser').contents):clone.append(child)
        return str(clone)
    result=''.join(visit(node) for node in BeautifulSoup(raw,'html.parser').contents)
    # HTML parsers normalize pure ASCII whitespace; protected letters, ruby
    # and presentation markers must remain exact within the selected span.
    if Projection({'html':result}).text!=projection.text[start:end]:raise ValueError('Presented inline slice changed text')
    return result
