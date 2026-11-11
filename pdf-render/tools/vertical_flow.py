"""Explicitly joined HTML line wraps inside an authored vertical body.

Marking br elements preserves the projection and ruby offsets used to split
horizontal notes. Only the vertical renderer consumes these exact markers.
"""
from bs4 import BeautifulSoup
from model import Projection,digest


def prepare(value,binding):
    if not isinstance(value,dict) or set(value)!={'html'}:
        raise ValueError('Vertical HTML flow requires one rich content field')
    if digest(value)!=binding['content_sha256']:
        raise ValueError('Stale vertical flow binding')
    indices=binding['join_br_indices']
    if not indices or any(type(n)is not int or n<0 for n in indices) or indices!=sorted(set(indices)):
        raise ValueError('Vertical line-wrap indices must be sorted unique integers')
    soup=BeautifulSoup(value['html'],'html.parser');breaks=soup.find_all('br')
    if any(n>=len(breaks)for n in indices):
        raise ValueError('Vertical line-wrap index outside the content')
    for n in indices:
        br=breaks[n]
        if br.attrs or br.contents or br.find_parent(['ruby','rt','rp','table']):
            raise ValueError('Vertical line-wrap join must select a plain body br')
        # Consecutive breaks are paragraph boundaries, not copied line wraps.
        if br.previous_sibling is None or br.next_sibling is None or getattr(br.previous_sibling,'name',None)=='br' or getattr(br.next_sibling,'name',None)=='br':
            raise ValueError('Vertical flow cannot consume a paragraph boundary')
        br['data-vertical-soft-break']='true'
    result={'html':str(soup)};old,new=Projection(value),Projection(result)
    if old.text!=new.text or old.ruby!=new.ruby:
        raise ValueError('Vertical flow changed canonical projection or ruby')
    return result
