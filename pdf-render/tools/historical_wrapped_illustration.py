"""Exact source illustration beside the opening horizontal passage paragraph."""
from bs4 import BeautifulSoup,Tag
from model import Projection,digest
from presentation import source_binding
from historical_complex import image_hash

def detach(value,binding,unit):
    if not isinstance(value,dict)or digest(value)!=binding['content_sha256']:
        raise ValueError('Stale historical wrapped illustration')
    source_binding(unit,binding['evidence'])
    width,gap,lines=binding['width_fraction'],binding['gap_em'],binding['short_lines']
    if type(width)not in [int,float]or not .15<=width<=.3 or type(gap)not in [int,float]or not .3<=gap<=2 or type(lines)is not int or not 3<=lines<=8:
        raise ValueError('Invalid source illustration geometry')
    soup=BeautifulSoup(value['html'],'html.parser');roots=[n for n in soup.children if isinstance(n,Tag)]
    images=soup.find_all('img')
    if len(images)!=1 or image_hash(images[0])!=binding['image_sha256'] or roots[0].name!='p' or roots[0].find(['img','br']):
        raise ValueError('Wrapped illustration requires one exact image and opening prose paragraph')
    panel=images[0].parent
    if panel is not roots[-1]or panel.name!='p'or panel.get_text(strip=True)or 'source-illustration'not in panel.get('class',[]):
        raise ValueError('Wrapped illustration must be the canonical final illustration panel')
    image=images[0].extract();panel.decompose();out={'html':str(soup)}
    if Projection(value).text!=Projection(out).text or Projection(value).ruby!=Projection(out).ruby:
        raise ValueError('Wrapped illustration changed native text or ruby')
    return out,image

def wrap_tex(conv,tex,binding,image,item_id,anchor):
    if not getattr(conv,'source_target_markers',False):raise ValueError('Historical wrapping outside Old JLPT')
    body,separator,trailer=tex.partition(r'\Para ')
    if not separator or not body.startswith(r'\HistoricalInlinePassageLabel{')or r'\HistoricalCitation{'not in trailer:
        raise ValueError('Wrapped illustration needs one normalized opening paragraph and exterior citation')
    from historical_nodes import image_at_width
    graphic=image_at_width(conv,image,1)
    prefix=r'\par\addvspace{8pt}\noindent';suffix=r'\par\addvspace{8pt}'
    if not graphic.startswith(prefix)or not graphic.endswith(suffix):raise ValueError('Unexpected illustration renderer')
    graphic=graphic[len(prefix):-len(suffix)]
    conv.features.append(dict(kind='historical_wrapped_illustration',target=item_id,image_sha256=binding['image_sha256'],width_fraction=binding['width_fraction'],short_lines=binding['short_lines'],image_bytes_preserved=True,canonical_changed=False))
    if anchor.count(r'\label{'+item_id+'}')!=1:raise ValueError('Wrapped passage needs its exact interior anchor')
    return (r'\HistoricalWrappedIllustration{'+str(binding['width_fraction'])+'}{'+str(binding['gap_em'])+'}{'+str(binding['short_lines'])+'}{'+body+'}{'+graphic+'}{'+anchor+'}'+trailer)
