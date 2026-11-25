"""Source-bound vector replacements; original encoded figures remain canonical."""
import base64
import hashlib
from bs4 import BeautifulSoup
from model import digest
from presentation import source_binding

FLOW_TOPOLOGY={1:('BDCA','ABCD'),2:('CBD>A','A>CBD'),3:('BDCA','A>CBD'),4:('CBD>A','ABCD')}
SET_TOPOLOGY={1:('語彙','使用語彙','理解語彙'),2:('語彙','理解語彙','使用語彙'),
              3:('語彙','使用語彙 overlaps 理解語彙'),4:('語彙','理解語彙 disjoint 使用語彙')}


def collect(model):
    result={}
    for section in model['document']['sections']:
        for item in section['items']:
            binding=model['layout']['items'][item['id']].get('historical_native_diagrams')
            if not binding:continue
            if model.get('exam',{}).get('generation')!='historical-1991-2009':raise ValueError('Old diagrams outside Old era')
            slot=binding['slot'];value=item.get(slot)
            if slot not in {'content','options'}or digest(value)!=binding['field_sha256']:raise ValueError('Stale native diagram field')
            source_binding(model['unit'],binding['evidence'])
            values=value if slot=='options'else[value]
            if len(values)!=len(binding['panels']):raise ValueError('Native panel count differs from field')
            for index,(v,p)in enumerate(zip(values,binding['panels']),1):
                images=BeautifulSoup(v['html'],'html.parser').find_all('img')if isinstance(v,dict)else[]
                if len(images)!=1:raise ValueError('Each native panel needs one exact preserved image')
                key=hashlib.sha256(base64.b64decode(images[0]['src'].split(',',1)[1])).hexdigest()
                if key!=p['image_sha256']or key in result:raise ValueError('Stale or duplicate diagram selector')
                kind=p['kind'];choice=p['choice']
                if kind=='flow_choice':expected=list(FLOW_TOPOLOGY[index])
                elif kind=='sets_choice':expected=list(SET_TOPOLOGY[index])
                elif kind=='flow_passage':expected=['ABCD','left_outline_arrow','boxed_ABCD','図2-1']
                else:raise ValueError('Unknown native Old diagram')
                if p['topology']!=expected or choice!=(index if slot=='options'else None):raise ValueError('Diagram topology/choice order differs from source contract')
                result[key]={**p,'owner':item['id'],'evidence':binding['evidence']}
    return result


def flow_tex(panel):
    passage=panel['kind']=='flow_passage';choice=panel['choice']
    lines=[r'\begin{tikzpicture}[x=1pt,y=1pt,baseline=0pt,line width=.5pt,',
           r'cell/.style={ellipse,draw,minimum width=19pt,minimum height=14pt,inner sep=0pt,font=\rmfamily\fontsize{10}{11}\selectfont},',
           r'link/.style={-{Stealth[length=4pt,width=3pt]},line width=.65pt}]']
    lines.append(r'\path[use as bounding box](0,0)rectangle(180,'+('108'if passage else'106')+');')
    lines.append(r'\draw(0,0)rectangle(180,'+('108'if passage else'94')+');')
    if not passage:lines.append(r'\node[anchor=south west,inner sep=0pt,font=\rmfamily\fontsize{11}{12}\selectfont]at(0,98){'+str(choice)+'};')
    def chain(x,letters,prefix,ys=(81,57,33,9)):
        for c,y in zip(letters,ys):lines.append(r'\node[cell]('+prefix+c+')at('+str(x)+','+str(y)+'){'+c+'};')
        for a,b in zip(letters,letters[1:]):lines.append(r'\draw[link]('+prefix+a+'.south)--('+prefix+b+'.north);')
    def fan(x,branch,prefix):
        lines.append(r'\node[cell]('+prefix+'A)at('+str(x)+','+('70'if branch else'17')+'){A};')
        for c,dx in zip('CBD',[-25,0,25]):
            lines.append(r'\node[cell]('+prefix+c+')at('+str(x+dx)+','+('17'if branch else'70')+'){'+c+'};')
            start,end=(prefix+'A.south',prefix+c+'.north')if branch else(prefix+c+'.south',prefix+'A.north')
            lines.append(r'\draw[link]('+start+')--('+end+');')
    if passage:
        lines.append(r'\node[font=\InstructionJapanese\fontsize{10}{12}\selectfont]at(90,99){図2-1};')
        chain(30,'ABCD','p',ys=(79,56,33,10))
        lines.append(r'\draw(137,7)rectangle(179,82);')
        for c,y in zip('ABCD',[72,53,34,15]):lines.append(r'\node[font=\rmfamily\fontsize{10}{11}\selectfont]at(158,'+str(y)+'){'+c+'};')
        lines.append(r'\draw(72,39)--(85,48)--(85,43)--(113,43)--(113,35)--(85,35)--(85,30)--cycle;')
    else:
        left,right=FLOW_TOPOLOGY[choice]
        if left=='BDCA':chain(45,left,'l')
        else:fan(45,False,'l')
        if right=='ABCD':chain(135,right,'r')
        else:fan(135,True,'r')
    lines.append(r'\end{tikzpicture}')
    return '\n'.join(lines)


def sets_tex(panel):
    c=panel['choice'];lines=[r'\begin{tikzpicture}[x=1pt,y=1pt,baseline=0pt,line width=.45pt,every node/.style={font=\InstructionJapanese\fontsize{10}{12}\selectfont,inner sep=0pt}]',
        r'\path[use as bounding box](0,0)rectangle(160,170);',
        r'\node[anchor=south west,font=\rmfamily\fontsize{11}{12}\selectfont]at(0,158){'+str(c)+'};',
        r'\draw(80,75)ellipse[x radius=75,y radius=70];',
        r'\node at(80,133){'+(r'\ruby{語彙}{ごい}'if c==1 else'語彙')+'};']
    if c in (1,2):
        middle,inner=SET_TOPOLOGY[c][1:]
        lines += [r'\draw(80,74)ellipse[x radius=51,y radius=47];',r'\draw(80,74)ellipse[x radius=28,y radius=24];',
                  r'\node at(80,108){'+middle+'};',r'\node at(80,74){'+inner+'};']
    elif c==3:
        lines += [r'\draw(56,75)ellipse[x radius=44,y radius=44];',r'\draw(104,75)ellipse[x radius=44,y radius=44];',
                  r'\node at(37,75){使用語彙};',r'\node at(123,75){理解語彙};']
    else:
        lines += [r'\draw(52,75)ellipse[x radius=34,y radius=33];',r'\draw(112,52)ellipse[x radius=21,y radius=21];',
                  r'\node at(52,75){理解語彙};',r'\node[font=\InstructionJapanese\fontsize{8}{10}\selectfont]at(112,52){使用語彙};']
    lines.append(r'\end{tikzpicture}');return '\n'.join(lines)


def render(conv,key,style):
    binding=getattr(conv,'historical_native_diagrams',{}).get(key)
    if binding is None:return None
    if not getattr(conv,'source_target_markers',False)or style is None or style['role']!='illustration':raise ValueError('Native diagram requires an Old illustration role')
    tex=sets_tex(binding)if binding['kind']=='sets_choice'else flow_tex(binding)
    conv.features.append({'kind':'historical_native_diagram','source_image_sha256':key,**binding,'native_vectors':True,'canonical_image_preserved':True})
    return r'\par\addvspace{8pt}\noindent\resizebox{'+str(style['width_fraction'])+r'\linewidth}{!}{'+tex+r'}\par\addvspace{8pt}'
