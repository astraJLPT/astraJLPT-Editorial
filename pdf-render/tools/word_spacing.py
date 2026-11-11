"""Bounded presentation of single Japanese word spaces, never canonical edits."""
import html
import re
from bs4 import BeautifulSoup, NavigableString, Tag
from model import Projection

POLICIES={'preserve','continuous_japanese'}
JAPANESE=re.compile(r'[ぁ-んァ-ヶー一-龥々〆ヵヶ]')
DIGIT=re.compile(r'[0-9０-９]')


def continuous_japanese(value, protected_lines=()):
    raw=value['html'] if isinstance(value,dict) else html.escape(value).replace('\n','<br/>')
    soup=BeautifulSoup(raw,'html.parser');atoms=[];removed=[]
    def visit(node):
        if isinstance(node,NavigableString):
            atoms.extend((node,n,c)for n,c in enumerate(str(node)));return
        if not isinstance(node,Tag):return
        if node.name in ['rt','rp']:return
        if node.name in ['table','h1','h2','h3','h4'] or 'passage-author' in node.get('class',[]) or (node.name in ['p','div'] and Projection({'html':str(node)}).text.strip() in protected_lines):
            atoms.append((None,0,'\n'));return
        boundary=node.name in ['p','div','section','br','li','blockquote']
        if boundary:atoms.append((None,0,'\n'))
        for child in node.children:visit(child)
        if boundary:atoms.append((None,0,'\n'))
    for node in soup.children:visit(node)
    edits={}
    for n,(node,index,c) in enumerate(atoms):
        if c!=' ' or n==0 or n==len(atoms)-1:continue
        a,b=atoms[n-1][2],atoms[n+1][2]
        # Never collapse runs, paragraph indentation, fullwidth alignment,
        # Latin words, phone groups, or two numeric columns.
        ja,jb=bool(JAPANESE.fullmatch(a)),bool(JAPANESE.fullmatch(b))
        if not ((ja and (jb or DIGIT.fullmatch(b))) or (jb and (DIGIT.fullmatch(a) or a in '、。？！）」』】')) or (ja and b in '「『（【')):continue
        edits.setdefault(id(node),(node,set()))[1].add(index)
        removed.append({'left':a,'right':b,'node_offset':index})
    for node,indexes in edits.values():node.replace_with(''.join(c for n,c in enumerate(str(node))if n not in indexes))
    result={'html':str(soup)}
    before,after=Projection(value),Projection(result)
    assert ''.join(before.text.split())==''.join(after.text.split())
    assert [(r['base'],r['reading'])for r in before.ruby]==[(r['base'],r['reading'])for r in after.ruby]
    return result,removed
