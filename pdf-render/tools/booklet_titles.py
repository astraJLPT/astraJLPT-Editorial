"""Separate a source-bound genuine first title from its numbered instruction."""
import html,re
from bs4 import BeautifulSoup
from model import Projection,digest
from notice_layout import html_lines


def split(value,binding,source_value=None):
    source=value if source_value is None else source_value
    if digest(source)!=binding['content_sha256']:
        raise ValueError('Stale booklet title')
    text=binding['text']
    if not isinstance(text,str)or not text or '\n'in text:
        raise ValueError('Booklet title must name one exact complete line')
    raw=html.escape(value).replace('\n','<br/>')if isinstance(value,str)else value['html']
    lines=html_lines(raw)
    if len(lines)<2 or Projection({'html':lines[0]}).text.strip()!=text:
        raise ValueError('Booklet title must be the complete first line')
    if any(BeautifulSoup(x,'html.parser').find(['table','section','img'])for x in lines):
        raise ValueError('Booklet title requires simple instruction lines')
    if not re.match(r'^\s*(問題|もんだい)\s*[0-9０-９]{1,2}',Projection({'html':lines[1]}).text):
        raise ValueError('Booklet title must precede a numbered instruction')
    title={'html':lines[0]}
    heading={'html':'<br/>'.join(lines[1:])}
    original,current=Projection(source),Projection(value)
    left,right=Projection(title),Projection(heading)
    compact=lambda p:''.join(p.text.split())
    ruby=lambda p:[(r['base'],r['reading'])for r in p.ruby]
    if (compact(original)!=compact(current)or compact(left)+compact(right)!=compact(current)
            or ruby(original)!=ruby(current)or ruby(left)+ruby(right)!=ruby(current)):
        raise ValueError('Booklet title changed protected text or ruby')
    gap=binding.get('after_pt',12)
    if isinstance(gap,bool)or not isinstance(gap,(int,float))or not 0<=gap<=30:
        raise ValueError('Invalid booklet title gap')
    return title,heading
