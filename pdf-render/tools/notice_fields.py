"""Exact existing metadata rows, rendered as three native label/colon/value columns."""
import re
from bs4 import BeautifulSoup
from model import Projection
from example_layout import slice_inline

def prepare(nodes,binding):
    expected=[r['text']for r in binding['rows']];plain=[Projection({'html':str(n)}).text.strip()for n in nodes]
    starts=[j for j in range(len(nodes)-len(expected)+1)if plain[j:j+len(expected)]==expected]
    if len(starts)!=1:raise ValueError('Notice fields require one exact adjacent node sequence')
    j=starts[0];holder=BeautifulSoup('<div data-notice-fields="colon"></div>','html.parser').div
    for n in nodes[j:j+len(expected)]:holder.append(n)
    return nodes[:j]+[holder]+nodes[j+len(expected):]

def render(conv,node,binding):
    children=list(node.children);rows=[]
    if len(children)!=len(binding['rows']):raise ValueError('Notice field rows changed')
    for child,spec in zip(children,binding['rows']):
        raw=child.decode_contents();text=Projection({'html':raw}).text
        if text.strip()!=spec['text']:raise ValueError('Stale notice field row')
        match=re.fullmatch(r'\s*(.+?)([:：])\s*(\S.*?)\s*',text,re.S)
        if not match or match[1]!=spec['label']:raise ValueError('Notice label/colon association changed')
        value=slice_inline(raw,match.start(3),match.end(3));tex=conv.value({'html':value},'notice')
        if spec.get('range_display'):
            if match[3]!='18:00~20:00'or spec['range_display']!='18:00～20:00'or tex.count(r'\textasciitilde{}')!=1:raise ValueError('Unsupported bound range display')
            tex=r'\mbox{'+tex.replace(r'\textasciitilde{}',r'\hspace{.15em}～\hspace{.15em}')+'}'
            conv.features.append({'kind':'range_display_mapping','canonical':match[3],'display':spec['range_display'],'context':'bound_notice_metadata','canonical_changed':False})
        label=slice_inline(raw,match.start(1),match.end(1))
        rows.append(conv.value({'html':label},'notice')+' & '+conv.text(match[2])+' & '+tex+r' \\')
    width=binding.get('width_fraction',.94)
    if not .7<=width<=1:raise ValueError('Invalid metadata width')
    conv.features.append({'kind':'notice_colon_fields','labels':[r['label']for r in binding['rows']],'width_fraction':width})
    label_width=binding.get('label_width_em',3);before=binding.get('before_pt',12);after=binding.get('after_pt',12)
    if not 2<=label_width<=10 or not 0<=before<=20 or not 0<=after<=20:raise ValueError('Invalid metadata column geometry')
    return r'\par\addvspace{'+str(before)+r'pt}{\centering\begin{tblr}{width='+str(width)+r'\linewidth,colspec={Q[l,wd='+str(label_width)+r'em] Q[c,wd=.6em] X[l]},colsep=3pt,rowsep=2pt,cells={valign=t}}'+''.join(rows)+r'\end{tblr}\par}\vspace{'+str(after)+'pt}'
