"""Data-only native TeX line/bar/pie artwork for historical listening documents."""
import json
import math
import re
from jsonschema import Draft202012Validator,ValidationError
from historical_listening import bound_file
from historical_listening_contract import obj,array,S,REF

NUMBER={'type':'number'}
POINT={'type':'array','items':NUMBER,'minItems':2,'maxItems':2}
STYLE={'enum':['solid','dashed','dash_dot','dash_dot_dot','dotted']}
FILL={'enum':['black','white','gray','darkgray']}
COLORS={'black':'black','white':'white','gray':'black!35','darkgray':'black!65'}


def schema():
    line=obj(dict(kind={'const':'line'},points=array(POINT,2),style=STYLE,width=NUMBER))
    dot=obj(dict(kind={'const':'dot'},point=POINT,radius=NUMBER))
    label=obj(dict(kind={'const':'label'},point=POINT,text=S,size=NUMBER,anchor={'enum':['center','west','east','north','south','north west']}))
    image=obj(dict(kind={'const':'image'},point=POINT,width=NUMBER,height=NUMBER,asset=REF))
    rect=obj(dict(kind={'const':'rect'},point=POINT,width=NUMBER,height=NUMBER,fill=FILL,line_width=NUMBER))
    polygon=obj(dict(kind={'const':'polygon'},points=array(POINT,3),fill=FILL,line_width=NUMBER))
    sector=obj(dict(kind={'const':'sector'},point=POINT,radius=NUMBER,start_angle=NUMBER,end_angle=NUMBER,
                    fill={'enum':['black','white','gray','darkgray']},line_width=NUMBER))
    return obj(dict(contract={'const':'historical-listening-artwork-1.0'},
        canvas=obj(dict(width=NUMBER,height=NUMBER)),
        coordinate_note=S,source_crop=REF,
        elements=array({'oneOf':[line,dot,label,image,rect,sector,polygon]},1)))


def load(ref):
    path=bound_file(ref,'preprocess/assets');value=json.loads(path.read_text('utf-8-sig'))
    try:Draft202012Validator(schema()).validate(value)
    except ValidationError as exc:raise ValueError('Invalid listening artwork: '+exc.message)from exc
    w=value['canvas']['width'];h=value['canvas']['height']
    if not(0<w<=10000 and 0<h<=10000):raise ValueError('Invalid artwork bounds')
    bound_file(value['source_crop'],'preprocess/assets')
    for element in value['elements']:
        for point in element.get('points',[element.get('point')]):
            if point is not None and (not all(math.isfinite(v)for v in point)or not(0<=point[0]<=w and 0<=point[1]<=h)):
                raise ValueError('Artwork point outside canvas')
        for key in ('width','height','size','radius','line_width'):
            if key in element and not(0<element[key]<=10000):raise ValueError('Invalid artwork size')
        if element['kind']=='image':bound_file(element['asset'],'preprocess/assets')
        if element['kind']=='sector':
            a,b=element['start_angle'],element['end_angle'];x,y=element['point'];r=element['radius']
            if not (math.isfinite(a) and math.isfinite(b) and 0<b-a<=360):
                raise ValueError('Invalid artwork sector angles')
            if not (r<=x<=w-r and r<=y<=h-r):raise ValueError('Artwork sector outside canvas')
    return value


def dependencies(ref):
    value=load(ref)
    return [value['source_crop'],*[e['asset']for e in value['elements']if e['kind']=='image']]


def render(ref,width_mm,text):
    value=load(ref);w=value['canvas']['width'];h=value['canvas']['height'];scale=width_mm/w
    def pt(point):return '('+','.join(str(v)for v in point)+')'
    def size(number):return f'{number*scale:.6f}mm'
    patterns={'solid':'solid','dashed':'dash pattern=on 9pt off 3pt',
              'dash_dot':'dash pattern=on 6pt off 2pt on 1pt off 2pt',
              'dash_dot_dot':'dash pattern=on 6pt off 2pt on 1pt off 2pt on 1pt off 2pt','dotted':'densely dotted'}
    lines=[r'\begin{tikzpicture}[x='+size(1)+',y=-'+size(1)+']',
           rf'\path[use as bounding box](0,0) rectangle ({w},{h});']
    for e in value['elements']:
        kind=e['kind']
        if kind=='line':lines.append(r'\draw[line width='+size(e['width'])+','+patterns[e['style']]+',line cap=round,line join=round] '+' -- '.join(pt(p)for p in e['points'])+';')
        elif kind=='dot':lines.append(r'\fill '+pt(e['point'])+' circle[radius='+size(e['radius'])+'];')
        elif kind=='label':
            fs=e['size']*scale*72/25.4
            label_text=text(e['text'])
            # A curly apostrophe in an abbreviated Latin year must not acquire
            # the full Japanese punctuation cell or inter-script glue.
            if re.fullmatch(r'’\d{2}',e['text']):
                label_text=r'\textquoteright{}'+e['text'][1:]
            lines.append(r'\node[anchor='+e['anchor']+r',inner sep=0pt,font={\sffamily\fontsize{'+f'{fs:.4f}'+'}{'+f'{fs*1.15:.4f}'+r'}\selectfont}] at '+pt(e['point'])+' {'+label_text+'};')
        elif kind=='image':
            image=bound_file(e['asset'],'preprocess/assets')
            lines.append(r'\node[anchor=north west,inner sep=0pt] at '+pt(e['point'])+r' {\includegraphics[width='+size(e['width'])+',height='+size(e['height'])+']{'+image.as_posix()+'}};')
        elif kind=='rect':lines.append(r'\draw[fill='+COLORS[e['fill']]+',line width='+size(e['line_width'])+'] '+pt(e['point'])+' rectangle '+pt([e['point'][0]+e['width'],e['point'][1]+e['height']])+';')
        elif kind=='polygon':lines.append(r'\draw[fill='+COLORS[e['fill']]+',line width='+size(e['line_width'])+'] '+' -- '.join(pt(p)for p in e['points'])+' -- cycle;')
        elif kind=='sector':
            # Explicit Cartesian cubic arcs avoid TikZ polar-unit ambiguity with
            # a negative y basis. Angles increase clockwise in the source view.
            x,y=e['point'];r=e['radius'];a=math.radians(e['start_angle']);end=math.radians(e['end_angle'])
            start=[x+r*math.cos(a),y+r*math.sin(a)]
            path=pt([x,y])+' -- '+pt(start)
            while a<end-1e-12:
                b=min(a+math.pi/2,end);k=4/3*math.tan((b-a)/4)
                c1=[x+r*(math.cos(a)-k*math.sin(a)),y+r*(math.sin(a)+k*math.cos(a))]
                c2=[x+r*(math.cos(b)+k*math.sin(b)),y+r*(math.sin(b)-k*math.cos(b))]
                dest=[x+r*math.cos(b),y+r*math.sin(b)]
                path+=' .. controls '+pt(c1)+' and '+pt(c2)+' .. '+pt(dest);a=b
            fill=COLORS[e['fill']]
            lines.append(r'\draw[fill='+fill+',line width='+size(e['line_width'])+'] '+path+' -- cycle;')
    return '\n'.join(lines+[r'\end{tikzpicture}'])
