"""Native breadcrumb separators and literal contact/identifier glyph routes."""
import re
from bs4 import NavigableString
from model import Projection


def prepare(soup,binding):
    soup.smooth()
    for text in binding.get('breadcrumbs',[]):
        projection=Projection({'html':str(soup)}).text
        if projection.count(text)!=1 or '>' not in text:raise ValueError('Breadcrumb requires one exact navigation line')
        # Reparse only the selected base characters. Separator nodes have no
        # Japanese/ruby children and remain searchable literal ASCII >.
        start=projection.index(text);end=start+len(text);offset=0;found=0
        for n in list(soup.descendants):
            if not isinstance(n,NavigableString) or n.find_parent(['rt','rp']):continue
            # Use the projection map rather than DOM whitespace offsets below.
            if '>' not in str(n):continue
            candidates=[]
            p=Projection({'html':str(soup)})
            for match in re.finditer('>',p.text[start:end]):candidates.append(start+match.start())
            break
        else:candidates=[]
        # A base projection span gives the exact raw escaped glyph boundary.
        from bs4 import BeautifulSoup
        raw=str(soup);p=Projection({'html':raw})
        for index in sorted(candidates,reverse=True):
            lo,hi=p.raw_span(index,index+1)
            raw=raw[:lo]+'<span data-breadcrumb-separator="true">&gt;</span>'+raw[hi:];found+=1
        if found!=text.count('>'):raise ValueError('Breadcrumb separator count changed')
        soup.clear()
        for n in list(BeautifulSoup(raw,'html.parser').children):soup.append(n)
    for spec in binding.get('literal_identifiers',[]):
        text=spec['text'];count=spec['occurrences']
        if not re.fullmatch(r'[0-9A-Za-z①-⑳-]+',text) or '-'not in text:raise ValueError('Invalid literal identifier')
        pattern=r'(?<![A-Za-z0-9])'+re.escape(text)+r'(?![A-Za-z0-9])'
        if len(re.findall(pattern,Projection({'html':str(soup)}).text))!=count:raise ValueError('Literal identifier count changed: '+text)
        # Glyph routing happens when text is emitted, preserving the original
        # inline tree for structured metadata and email consumers.
