"""Strict SVG projection of the released renderer's finite vector vocabulary.

Coordinates and labels come from the validated native artwork emitters. This
does not inspect PDFs, execute TeX, interpret arbitrary TeX, or redraw data from
an image. Unknown commands/paths fail closed. Fonts remain the reader's shared
source-bound faces. Canonical source images are retained by image_html.
"""
import hashlib
import html
import math
import re
from functools import lru_cache
from pathlib import Path
from fontTools.ttLib import TTFont

NUM=r'-?(?:\d+(?:\.\d*)?|\.\d+)'
ROLES={'rmfamily':('Body','body'),'mcfamily':('Body','body'),'bfseries':('BodyBold','bold'),
       'InstructionJapanese':('Heading','instruction_japanese'),'InstructionLatin':('InstructionLatin','instruction_latin'),
       'HistoricalQuestionJapanese':('OldQuestion','historical_question_japanese'),'AsciiParen':('AsciiParen','ascii_parenthesis')}


def balanced(s,start,opening='{',closing='}'):
    if s[start]!=opening:raise ValueError('Missing vector delimiter '+s[start:start+30])
    depth=1;i=start+1
    while i<len(s):
        if s[i]=='\\':i+=2;continue
        if s[i]==opening:depth+=1
        if s[i]==closing:
            depth-=1
            if not depth:return s[start+1:i],i+1
        i+=1
    raise ValueError('Unclosed vector delimiter')


def options(s):
    parts=[];start=0;depth=0
    for i,ch in enumerate(s):
        if ch in '{[':depth+=1
        elif ch in '}]':depth-=1
        elif ch==',' and depth==0:parts.append(s[start:i].strip());start=i+1
    parts.append(s[start:].strip());out={}
    for p in parts:
        if not p:continue
        k,sep,v=p.partition('=');out[k.strip()]=v.strip() if sep else True
    return out


def number(s,default=0):
    if s is None:return default
    if isinstance(s,(int,float)):return float(s)
    return float(str(s).removesuffix('pt'))


def attrs(**values):
    return ' '.join(f'{k.replace("_","-")}="{html.escape(str(v),quote=True)}"'for k,v in values.items()if v is not None)


@lru_cache(maxsize=None)
def font_widths(path,index):
    with TTFont(path,fontNumber=index)as f:
        em=f['head'].unitsPerEm
        return {chr(c):f['hmtx'][g][0]/em for c,g in f.getBestCmap().items()}


class Vector:
    def __init__(self,source,model,prefix):
        self.source=source;self.model=model;self.prefix=prefix;self.parts=[];self.defs=[];self.named={};self.styles={};self.stack=[];self.bounds=None;self.yflip=1;self.default={};self.font={'size':10,'baseline':12,'family':'Body','role':'body','latin_family':'BodyLatin','latin_role':'body_latin'};self.images={};self.text=[]

    def select_font(self,font,command):
        if command in ['rmfamily','InstructionLatin','AsciiParen']:
            family,role=('BodyLatin','body_latin')if command=='rmfamily'else ROLES[command]
            if role not in self.model['style']['font_roles'] and role=='body_latin':family,role='Body','body'
            font.update(latin_family=family,latin_role=role)
        else:font['family'],font['role']=ROLES[command]

    def text_runs(self,text,font,dy):
        return [{'text':piece,'font':({**font,'family':font['latin_family'],'role':font['latin_role']}if piece.isascii()else dict(font)),'dy':dy}
                for piece in re.findall(r'[\x00-\x7f]+|[^\x00-\x7f]+',text)]

    def widths(self,font,text):
        style=self.model['style'];spec=style['font_roles'].get(font['role'],{'source':font['role']})
        path=Path(spec.get('path',style['fonts'].get(spec.get('source',''),'')))
        path=__import__('package_paths').resource(path)
        widths=font_widths(str(path),spec.get('font_index',0))
        return sum(widths.get(c,widths.get('?',.5))for c in text)*font['size']

    def parse_text(self,s,font=None,dy=0):
        font=dict(font or self.font);runs=[];i=0
        while i<len(s):
            if s[i]=='{':
                body,i=balanced(s,i);runs.extend(self.parse_text(body,font,dy));continue
            if s[i]!='\\':
                end=s.find('\\',i);end=len(s)if end<0 else end
                brace=s.find('{',i,end);end=brace if brace>=0 else end
                text=s[i:end];runs.extend(self.text_runs(text,font,dy));i=end;continue
            i+=1
            if i<len(s)and s[i]=='\\':runs.append({'break':True});i+=1;continue
            if s[i:i+1]in ['%','&','_','#','{','}']:
                runs.extend(self.text_runs(s[i],font,dy));i+=1;continue
            match=re.match(r'[A-Za-z]+',s[i:])
            if not match:raise ValueError('Unknown vector text escape: '+s[i:])
            command=match[0];i+=len(command)
            if command in ROLES:
                self.select_font(font,command)
            elif command in ['selectfont','relax']:pass
            elif command=='fontsize':
                size,i=balanced(s,i);baseline,i=balanced(s,i);font.update(size=float(size),baseline=float(baseline))
            elif command=='ruby':
                base,i=balanced(s,i);reading,i=balanced(s,i)
                runs.append({'text':base,'ruby':reading,'font':dict(font),'dy':dy})
            elif command=='textsuperscript':
                body,i=balanced(s,i);runs.extend(self.parse_text(body,{**font,'size':font['size']*.7},dy-font['size']*.5))
            elif command=='shortstack':
                if s[i:i+1]=='[':_,i=balanced(s,i,'[',']')
                body,i=balanced(s,i);runs.extend(self.parse_text(body,font,dy))
            elif command=='ltjalchar':
                match=re.match(r'\s*"([0-9A-Fa-f]+)\s*',s[i:])
                if not match:raise ValueError('Invalid vector Unicode literal')
                runs.append({'text':chr(int(match[1],16)),'font':dict(font),'dy':dy});i+=match.end()
            else:raise ValueError('Unsupported vector text macro: '+command)
        return runs

    def expand_options(self,raw):
        out=dict(self.default)
        for key,value in options(raw).items():
            if key in self.styles:out.update(options(self.styles[key]))
            else:out[key]=value
        return out

    def paint(self,opts,command):
        fill=opts.get('fill','black' if command=='fill' else 'none')
        stroke='black' if command=='draw' or opts.get('draw') else 'none'
        if 'white'in opts:fill='white'
        if 'black'in opts:fill='black'
        if 'pattern'in opts:fill='url(#'+self.pattern(opts['pattern'])+')'
        color=next((k for k in opts if re.fullmatch(r'black!\d+',k)),None)
        if color:stroke=f'rgb({255*(1-float(color[6:])/100):g} {255*(1-float(color[6:])/100):g} {255*(1-float(color[6:])/100):g})'
        result=dict(fill=fill,stroke=stroke,stroke_width=number(opts.get('line width'),.4))
        if 'line cap'in opts:result['stroke_linecap']=opts['line cap']
        if 'line join'in opts:result['stroke_linejoin']=opts['line join']
        if 'dash pattern'in opts:result['stroke_dasharray']=' '.join(re.findall(NUM+r'(?=pt)',opts['dash pattern']))
        if 'dashed'in opts:result['stroke_dasharray']='3 3'
        if 'dotted'in opts:result['stroke_dasharray']='.4 2'
        arrow=next((k for k in opts if k.startswith('-{')or k in ['->','<-','<->']),None)
        if arrow:
            match=re.search(r'length=('+NUM+r')pt,width=('+NUM+r')pt',arrow)
            length,width=map(float,match.groups())if match else(4,3)
            ident=self.prefix+'-arrow-'+str(len(self.defs))
            self.defs.append(f'<marker id="{ident}" markerWidth="{length}" markerHeight="{width}" refX="{length}" refY="{width/2}" orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M0 0 L{length} {width/2} L0 {width} Z" fill="black"/></marker>')
            if arrow.startswith('<'):result['marker_start']='url(#'+ident+')'
            if arrow!='<-':result['marker_end']='url(#'+ident+')'
        return attrs(**result)

    def pattern(self,name):
        ident=self.prefix+'-'+re.sub(r'\W+','-',name)
        if any('id="'+ident+'"'in d for d in self.defs):return ident
        size=4;body=''
        if name=='HistoricalIron':size=1.6;body='<path d="M0 0 V1.6" stroke="black" stroke-width=".3"/>'
        elif name=='HistoricalCopper':size=4;body='<path d="M0 0 H4 M0 0 V4" stroke="black" stroke-width=".3"/>'
        elif name=='dots':size=3;body='<circle cx="1" cy="1" r=".5" fill="black"/>'
        elif name=='horizontal lines':body='<path d="M0 0 H4" stroke="black" stroke-width=".4"/>'
        elif name in ['north east lines','north west lines']:
            body='<path d="'+('M-1 1 L1 -1 M0 4 L4 0 M3 5 L5 3'if name=='north east lines'else'M-1 3 L1 5 M0 0 L4 4 M3 -1 L5 1')+'" stroke="black" stroke-width=".4"/>'
        elif name=='crosshatch':body='<path d="M0 0 L4 4 M0 4 L4 0" stroke="black" stroke-width=".4"/>'
        else:raise ValueError('Unsupported native pattern: '+name)
        self.defs.append(f'<pattern id="{ident}" width="{size}" height="{size}" patternUnits="userSpaceOnUse">{body}</pattern>');return ident

    def coordinate(self,raw):
        if re.fullmatch(NUM+','+NUM,raw):return tuple(map(float,raw.split(',')))
        name,_,anchor=raw.partition('.')
        if name not in self.named:raise ValueError('Unknown native vector coordinate '+raw)
        x,y,w,h=self.named[name]
        return x+(-w/2 if anchor=='west'else w/2 if anchor=='east'else 0),y+(h/2 if anchor=='north'else-h/2 if anchor=='south'else 0)*self.yflip

    def shape(self,body,opts,command):
        i=0;path=[];current=(0,0);start=None
        def coord(pos):
            raw,end=balanced(body,pos,'(',')');return self.coordinate(raw.replace(' ','')),end
        while i<len(body):
            if body[i].isspace():i+=1;continue
            if body.startswith('--cycle',i)or body.startswith('cycle',i):
                i+=7 if body.startswith('--cycle',i)else 5;path.append('Z');continue
            if body.startswith('--++',i):
                raw,i=balanced(body,i+4,'(',')')
                if ':'in raw:
                    angle,radius=map(float,raw.split(':'));p=(radius*math.cos(math.radians(angle)),radius*math.sin(math.radians(angle)))
                else:p=self.coordinate(raw)
                current=(current[0]+p[0],current[1]+p[1]);path.append(f'L{current[0]:g},{current[1]:g}');continue
            if body.startswith('--',i):i+=2;point,i=coord(i);current=point;path.append(f'L{point[0]:g},{point[1]:g}');continue
            if body.startswith('..controls',i):
                i+=10;a,i=coord(i)
                if body[i:i+3]!='and':raise ValueError('Malformed native Bezier')
                c,i=coord(i+3)
                if body[i:i+2]!='..':raise ValueError('Malformed native Bezier endpoint')
                current,i=coord(i+2);path.append(f'C{a[0]:g},{a[1]:g} {c[0]:g},{c[1]:g} {current[0]:g},{current[1]:g}');continue
            if body.startswith('rectangle',i):
                point,i=coord(i+9);x,y=current;z,w=point
                if opts.get('use as bounding box'):
                    self.bounds=(min(x,z),min(y,w),abs(z-x),abs(w-y));return
                self.parts.append('<rect '+attrs(x=min(x,z),y=min(y,w),width=abs(z-x),height=abs(w-y),rx=number(opts.get('rounded corners'),0))+' '+self.paint(opts,command)+'/>');return
            ellipse=next((v for v in ['ellipse','circle','arc']if body.startswith(v,i)),None)
            if ellipse:
                raw,i=balanced(body,i+len(ellipse),'[',']');spec=options(raw)
                rx=number(spec.get('x radius',spec.get('radius')));ry=number(spec.get('y radius',spec.get('radius')))
                if ellipse!='arc':
                    self.parts.append('<ellipse '+attrs(cx=current[0],cy=current[1],rx=rx,ry=ry)+' '+self.paint(opts,command)+'/>');return
                a=number(spec['start angle']);z=number(spec['end angle']);delta=z-a
                center=(current[0]-rx*math.cos(math.radians(a)),current[1]-ry*math.sin(math.radians(a)))
                current=(center[0]+rx*math.cos(math.radians(z)),center[1]+ry*math.sin(math.radians(z)))
                path.append(f'A{rx:g},{ry:g} 0 {int(abs(delta)>180)} {int(delta>0)} {current[0]:g},{current[1]:g}');continue
            if body[i]=='(':
                current,i=coord(i);start=current;path.append(f'M{current[0]:g},{current[1]:g}');continue
            raise ValueError('Unsupported native vector path: '+body[i:])
        markup='<path d="'+' '.join(path)+'" '+self.paint(opts,command)+'/>'
        if command=='clip':
            ident=self.prefix+'-clip-'+str(len(self.defs));self.defs.append(f'<clipPath id="{ident}"><path d="'+ ' '.join(path)+'"/></clipPath>');self.parts.append(f'<g clip-path="url(#{ident})">');self.stack[-1]+=1
        else:self.parts.append(markup)

    def node(self,body,opts):
        match=re.match(r'(?:\(([^)]+)\))?\s*at\s*\(([^)]+)\)\s*',body)
        if not match:raise ValueError('Unsupported native vector node: '+body[:80])
        name,coord=match.groups();x,y=self.coordinate(coord.replace(' ',''));raw,end=balanced(body,match.end())
        if body[end:].strip():raise ValueError('Unexpected native node suffix')
        font=dict(self.font)
        fontspec=opts.get('font','')
        for role in re.findall(r'\\([A-Za-z]+)',fontspec):
            if role in ROLES:self.select_font(font,role)
        size=re.search(r'\\fontsize\{('+NUM+r')\}\{('+NUM+r')\}',fontspec)
        if size:font.update(size=float(size[1]),baseline=float(size[2]))
        graphic=re.fullmatch(r'\\includegraphics\[([^]]+)\]\{([^}]+)\}',raw)
        if graphic:
            from PIL import Image
            spec=options(graphic[1]);path=Path(graphic[2]);data=path.read_bytes();key=hashlib.sha256(data).hexdigest();iw,ih=Image.open(path).size
            w=number(spec.get('width'));h=number(spec.get('height'),w*ih/iw)
            target='assets/illustrations/'+key[:20]+path.suffix.lower();self.images[key]={'path':target,'data':data,'source_path':path}
            self.parts.append(f'<image href="../{target}" '+attrs(x=x,y=y-h*self.yflip,width=w,height=h,transform=f'translate(0 {2*y-h*self.yflip}) scale(1 -1)'if self.yflip==1 else None)+'/>'if self.yflip==-1 else f'<image href="../{target}" x="{x}" y="{-y-h}" width="{w}" height="{h}" transform="scale(1 -1)"/>')
            return
        runs=self.parse_text(raw,font);lines=[[]]
        for run in runs:
            if run.get('break'):lines.append([])
            else:
                self.text.append(run['text']);run['width']=self.widths(run['font'],run['text']);lines[-1].append(run)
        widths=[sum(r['width']for r in line)for line in lines];w=max(widths,default=0);baseline=font['baseline'];h=font['size']+(len(lines)-1)*baseline
        pad=number(opts.get('inner sep'),0);px=number(opts.get('inner xsep'),pad);py=number(opts.get('inner ysep'),pad)
        outerw=max(w+2*px,number(opts.get('minimum width')));outerh=max(h+2*py,number(opts.get('minimum height')))
        anchor=opts.get('anchor','center');ox=0 if 'west'in anchor else -outerw if 'east'in anchor else -outerw/2
        oy=0 if 'north'in anchor else -outerh if 'south'in anchor else -outerh/2
        if 'base'in anchor:oy=-font['size']*.8-py
        if name:self.named[name]=(x,y,outerw,outerh)
        self.parts.append('<g '+attrs(transform=f'translate({x:g} {y:g}) scale(1 {-self.yflip})'+(f' rotate({-number(opts["rotate"]):g})'if 'rotate'in opts else ''))+'>')
        if opts.get('draw')or opts.get('fill'):
            if opts.get('ellipse'):self.parts.append('<ellipse '+attrs(cx=ox+outerw/2,cy=oy+outerh/2,rx=outerw/2,ry=outerh/2)+' '+self.paint(opts,'draw')+'/>')
            else:self.parts.append('<rect '+attrs(x=ox,y=oy,width=outerw,height=outerh)+' '+self.paint(opts,'draw'if opts.get('draw')else'path')+'/>')
        for li,line in enumerate(lines):
            cursor=ox+(outerw-widths[li])/2;by=oy+(outerh-h)/2+font['size']*.8+li*baseline
            for run in line:
                f=run['font'];yy=by+run['dy']
                self.parts.append('<text '+attrs(x=cursor,y=yy,font_family=f['family'],font_size=f['size'],fill='black',stroke='none')+'>'+html.escape(run['text'])+'</text>')
                if 'ruby'in run:
                    self.parts.append('<text '+attrs(x=cursor+run['width']/2,y=yy-f['size'],font_family=f['family'],font_size=f['size']*.5,text_anchor='middle',fill='black',stroke='none')+'>'+html.escape(run['ruby'])+'</text>');self.text.append(run['ruby'])
                cursor+=run['width']
        self.parts.append('</g>')

    def render(self):
        source=re.sub(r'(?m)(?<!\\)%[^\n]*','',self.source).strip();i=0
        while i<len(source):
            if source[i].isspace():i+=1;continue
            match=re.match(r'\\(begin|end|draw|path|fill|clip|node)',source[i:])
            if not match:raise ValueError('Unsupported native vector command: '+source[i:i+60])
            command=match[1];i+=match.end()
            if command in ['begin','end']:
                env,i=balanced(source,i)
                if env not in ['scope','tikzpicture']:raise ValueError('Unsupported vector environment '+env)
                if command=='end':
                    self.parts.extend(['</g>']*self.stack.pop());continue
                raw=''
                if source[i:i+1]=='[':raw,i=balanced(source,i,'[',']')
                opts=options(raw)
                if env=='tikzpicture':
                    self.yflip=1 if number(opts.get('y'),1)>0 else -1
                    for key,val in opts.items():
                        if key.endswith('/.style'):self.styles[key[:-7]]=val[1:-1]
                    self.default={k:v for k,v in opts.items()if not k.endswith('/.style')and k not in ['x','y','baseline']}
                    self.default.update(options(self.styles.get('every node','')))
                    self.parts.append(f'<g transform="scale(1 {-self.yflip})">');self.stack.append(1)
                else:
                    self.parts.append('<g'+(' transform="rotate('+str(number(opts['rotate']))+')"'if 'rotate'in opts else'')+'>');self.stack.append(1)
                continue
            raw=''
            if source[i:i+1]=='[':raw,i=balanced(source,i,'[',']')
            start=i;depth=0
            while i<len(source):
                if source[i]=='{':depth+=1
                elif source[i]=='}':depth-=1
                elif source[i]==';'and depth==0:break
                i+=1
            if i==len(source):raise ValueError('Unterminated native shape')
            body=source[start:i].strip();i+=1;opts=self.expand_options(raw)
            if command=='node':self.node(body,opts)
            else:self.shape(body,opts,command)
        if not self.bounds or self.stack:raise ValueError('Incomplete native vector bounds')
        x,y,w,h=self.bounds;viewy=-y-h if self.yflip==1 else y
        return '<svg xmlns="http://www.w3.org/2000/svg" '+attrs(viewBox=f'{x:g} {viewy:g} {w:g} {h:g}',aria_hidden='true',focusable='false',**{'class':'native-artwork visual-only'})+'><defs>'+''.join(self.defs)+'</defs>'+''.join(self.parts)+'</svg>'


def project(source,model,prefix):
    from renditions import variant,tex_without_ruby
    prefix=prefix+'-'+variant(model)
    if variant(model)=='norubi':source,_=tex_without_ruby(source)
    vector=Vector(source,model,prefix);markup=vector.render()
    return {'svg':markup,'images':vector.images,'text':''.join(vector.text),'source_sha256':hashlib.sha256(source.encode()).hexdigest()}
