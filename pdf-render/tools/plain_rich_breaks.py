"""Keep verified plain-source paragraphs after ruby turns the field into HTML."""
from bs4 import BeautifulSoup,NavigableString
from model import Projection

def prepare(value):
    if not isinstance(value,dict):return value
    before=Projection(value);soup=BeautifulSoup(value['html'],'html.parser')
    for node in list(soup.descendants):
        if not isinstance(node,NavigableString)or '\n'not in node:continue
        if node.parent.name in ['rt','rp']or node.parent.has_attr('data-authored-plain-break'):continue
        replacement=[]
        for i,part in enumerate(str(node).split('\n')):
            if i:
                br=soup.new_tag('span');br['data-authored-plain-break']='line';br.string='\n';replacement.append(br)
            if part:replacement.append(NavigableString(part))
        node.replace_with(*replacement)
    result={'html':str(soup)};after=Projection(result)
    if before.text!=after.text or before.ruby!=after.ruby:raise ValueError('Plain rich paragraph preservation changed text/ruby')
    return result
