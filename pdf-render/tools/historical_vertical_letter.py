"""Source-bound ruled vertical letter; every glyph remains canonical live text."""
import re
from bs4 import BeautifulSoup,Tag
from model import Projection,digest
from presentation import source_binding


def parts(value,binding):
    if not isinstance(value,dict)or set(value)!={'html'}or digest(value)!=binding['content_sha256']:
        raise ValueError('Stale ruled vertical letter')
    soup=BeautifulSoup(value['html'],'html.parser');roots=[n for n in soup.contents if str(n).strip()]
    if (len(roots)!=2 or getattr(roots[0],'name',None)!='p' or roots[0].attrs or roots[0].find()
        or not re.fullmatch(r'（[1-9][0-9]*）',roots[0].get_text())
        or getattr(roots[1],'name',None)!='div' or roots[1].attrs!={'data-historical-vertical-letter':'ruled'}):
        raise ValueError('Ruled letter requires its separate label and explicit canonical wrapper')
    paragraphs=[n for n in roots[1].contents if str(n).strip()]
    roles=[n.get('data-letter-role')if isinstance(n,Tag)else None for n in paragraphs]
    if (len(roles)<4 or roles[-3:]!=['date','sender','recipient'] or any(r!='body'for r in roles[:-3])
        or any(n.name!='p' or set(n.attrs)!={'data-letter-role'}for n in paragraphs)):
        raise ValueError('Ruled letter must preserve body, date, signature and addressee order')
    columns=[]
    for p,role in zip(paragraphs,roles):
        if any(n.name not in {'ruby','rt','rp','br'}or n.attrs for n in p.find_all()):
            raise ValueError('Unsupported markup inside ruled letter')
        if role!='body'and p.find('br'):raise ValueError('Letter metadata must occupy one source column')
        fragments=re.split(r'<br\s*/?>',p.decode_contents())
        if any(not Projection({'html':x}).text.strip()for x in fragments):
            raise ValueError('Empty ruled-letter column')
        for j,html in enumerate(fragments):
            columns.append(dict(role=role,paragraph_start=j==0,content={'html':html}))
    if binding['columns']!=len(columns)or not 6<=len(columns)<=20:
        raise ValueError('Ruled-letter column count differs from its source binding')
    reconstructed=''.join(Projection(c['content']).text for c in columns)
    original=Projection({'html':str(roots[1])})
    if re.sub(r'\s+','',reconstructed)!=re.sub(r'\s+','',original.text):
        raise ValueError('Ruled-letter segmentation lost text')
    semantic_ruby=lambda rows:[{k:v for k,v in r.items()if k not in {'start','end'}}for r in rows]
    ruby=[r for c in columns for r in Projection(c['content']).ruby]
    if semantic_ruby(ruby)!=semantic_ruby(original.ruby):raise ValueError('Ruled-letter segmentation changed ruby')
    for key,lo,hi in [('body_pt',9,14),('extent_em',25,50),('column_pitch_em',1.8,3.5),('padding_em',.4,2),('word_space_em',0,1)]:
        v=binding[key]
        if type(v)not in [int,float]or not lo<=v<=hi:raise ValueError('Invalid ruled-letter geometry: '+key)
    return roots[0].get_text(),columns


def render(conv,value,binding,unit,target):
    if not getattr(conv,'source_target_markers',False):raise ValueError('Ruled letter outside Old written renderer')
    source_binding(unit,binding['evidence']);label,columns=parts(value,binding)
    size=binding['body_pt'];extent=binding['extent_em'];pitch=binding['column_pitch_em'];pad=binding['padding_em']
    width=len(columns)*pitch+2*pad;height=extent+2*pad
    saved_vertical=getattr(conv,'active_vertical_body',False);saved_space=conv.word_space_em
    conv.active_vertical_body=True;conv.word_space_em=binding['word_space_em']
    nodes=[]
    try:
        for j,c in enumerate(columns):
            # Existing ruby conversion uses native tate ruby on this branch.
            tex=conv.value(c['content'],'body')
            indent=1.5 if c['role']=='date'else 1 if c['role']=='body'and c['paragraph_start']else 0
            lead=r'\hfill 'if c['role']=='sender'else r'\hspace*{'+str(indent)+r'\zw}'
            tail=r'\hspace*{1\zw}'if c['role']=='sender'else ''
            fill='0pt'if c['role']=='sender'else'0pt plus 1fil'
            x=width-pad-(j+.5)*pitch
            nodes.append(r'\node[anchor=north,inner sep=0pt,outer sep=0pt]at('+str(x)+','+str(-pad)+r'){\hbox{\tate\vbox{\hsize='+str(extent)+r'\zw\leftskip=0pt\rightskip=0pt\parindent=0pt\parfillskip='+fill+r'\baselineskip='+str(pitch)+r'\zw\noindent '+lead+tex+tail+r'\par}}};')
    finally:conv.active_vertical_body=saved_vertical;conv.word_space_em=saved_space
    rules=[r'\draw[line width=.3pt]('+str(pad+j*pitch)+','+str(-pad)+')--('+str(pad+j*pitch)+','+str(-height+pad)+');'for j in range(1,len(columns))]
    conv.features.append(dict(kind='historical_ruled_vertical_letter',target=target,columns=len(columns),internal_rules=len(rules),roles=[c['role']for c in columns],content_sha256=binding['content_sha256'],ruby_count=len(Projection(value).ruby),canonical_changed=False))
    # One semantic letter is a single framed object. Pagination remains natural;
    # there are no page-number or question-count breaks in this mechanism.
    return (r'\par\noindent\begin{minipage}{\linewidth}\centering{\rmfamily\mcfamily\fontsize{'+str(size)+'}{'+str(size)+r'}\selectfont\begin{tikzpicture}[x=1em,y=1em]'
        +r'\path[use as bounding box](0,0)rectangle('+str(width)+','+str(-height)+');'
        +r'\draw[line width=.6pt](0,0)rectangle('+str(width)+','+str(-height)+');'
        +r'\begin{pgfinterruptboundingbox}\node[anchor=north east,inner sep=0pt,outer sep=0pt]at(-.5,0){'+conv.text(label)+r'};\end{pgfinterruptboundingbox}'
        +''.join(rules)+''.join(nodes)+r'\end{tikzpicture}}\par\end{minipage}\par\addvspace{8pt}')
