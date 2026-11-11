"""Source-bound life-goals and transport charts, with live labels.

Printed life-goals values are literal witness data. Radar coordinates are
approximate traces of unlabelled markers, never exact historical measurements.
"""
import math
from richtex import text_tex

LIFE_VALUES = [
    [81,73,55,60,58,57,57,55,59,62,69,73],
    [71,62,52,48,46,38,44,52,51,54,59,61],
    [26,37,47,51,53,60,55,44,48,44,37,31],
    [18,27,43,39,40,40,41,43,40,35,28,23]]
AGES = ['16～','20～','25～','30～','35～','40～','45～','50～','55～','60～','65～','70歳以上']
AXES = ['通勤','買物','病院','レジャー','自動車','鉄道']
MAXIMA = [60,30,30,120,60,60]
SOURCE_IDENTITIES = {
    'life_goals_lines': {
        ('N1_2000','reading-b006',416,'e3555741c8f14b855a32e7d09b42eb790492e3818a85a875f99d84703c752e00'),
        ('N2_2000','reading-b009',371,'115e8c098ee3caed702d29a24d2ce0c883c3ad9152e21eee4200fc4e80f2a3fb')},
    'transport_radars': {
        ('N1_2001','reading-b008',376,'e3555741c8f14b855a32e7d09b42eb790492e3818a85a875f99d84703c752e00'),
        ('N2_2001','reading-b007',333,'115e8c098ee3caed702d29a24d2ce0c883c3ad9152e21eee4200fc4e80f2a3fb')}}


def fractions(panel, gender):
    """Project observed marker centres onto each independently traced axis."""
    cx,cy=panel['center_pixels'];out=[]
    for (ax,ay),(px,py) in zip(panel['axis_endpoints_pixels'],panel['marker_pixels'][gender]):
        dx,dy=ax-cx,ay-cy
        out.append(((px-cx)*dx+(py-cy)*dy)/(dx*dx+dy*dy))
    return out


def validate(art):
    kind=art['kind'];d=art['data']
    identity=(art['unit'],art['item_id'],art['source']['physical_page'],art['source']['source_sha256'])
    if kind not in SOURCE_IDENTITIES or identity not in SOURCE_IDENTITIES[kind]:
        raise ValueError('Statistical chart requires its inspected owner, item and source')
    if kind=='life_goals_lines':
        if set(d)!={'coordinate_status','ages','series','axis','caption'}:
            raise ValueError('Unexpected life-goals chart fields')
        if d['coordinate_status']!='printed_integer_values_no_normalization' or d['ages']!=AGES:
            raise ValueError('Life-goals category order or precision changed')
        if d['axis']!=dict(minimum=0,maximum=90,tick=10,unit='%'):
            raise ValueError('Life-goals percentage axis changed')
        expected=[('現在中心',1993,'solid','filled_circle'),('現在中心',1973,'dashed','filled_circle'),
                  ('未来中心',1973,'dashed','hollow_triangle'),('未来中心',1993,'solid','hollow_triangle')]
        if len(d['series'])!=4:raise ValueError('Four life-goals series required')
        for s,identity,values in zip(d['series'],expected,LIFE_VALUES):
            if set(s)!={'label','year','line','marker','values'} or (s['label'],s['year'],s['line'],s['marker'])!=identity:
                raise ValueError('Life-goals series identity or pattern changed')
            if s['values']!=values or any(type(v)is not int for v in s['values']):
                raise ValueError('Printed life-goals values changed')
        if d['caption']!='1－2図　生活目標―「現在中心」・「未来中心」（年層別）':
            raise ValueError('Life-goals caption changed')
    else:
        if set(d)!={'coordinate_status','axes_clockwise_from_north','axis_maxima_minutes','series','panels','trace_witness','label_policy'}:
            raise ValueError('Unexpected radar chart fields')
        if d['coordinate_status']!='approximate_digitization_not_exact_historical_data' or d['label_policy']!='axis_labels_only_no_invented_point_values':
            raise ValueError('Radar point uncertainty must remain explicit')
        if d['axes_clockwise_from_north']!=AXES or d['axis_maxima_minutes']!=MAXIMA:
            raise ValueError('Radar axis orientation or separate maxima changed')
        if d['series']!=[dict(gender='男性',marker='filled_circle'),dict(gender='女性',marker='hollow_circle')]:
            raise ValueError('Radar gender markers changed')
        if [p.get('label')for p in d['panels']]!=['東京区部','A地域','B地域']:
            raise ValueError('Radar panel order changed')
        witness=d['trace_witness']
        if witness.get('image_sha256')!='51c08c315d0b3a37125999f542e5a9146b9edfa505ed0d033dfbaa8a3b2659a1' or witness.get('physical_page')!=376:
            raise ValueError('Radar trace witness changed')
        for panel in d['panels']:
            if set(panel)!={'label','inspection_crop_pixels','center_pixels','axis_endpoints_pixels','marker_pixels'}:
                raise ValueError('Unexpected radar trace fields')
            if len(panel['axis_endpoints_pixels'])!=6 or set(panel['marker_pixels'])!={'男性','女性'}:
                raise ValueError('Six independently scaled axes and two series required')
            c=panel['center_pixels'];points=[c,*panel['axis_endpoints_pixels']]
            for gender in ['男性','女性']:
                if len(panel['marker_pixels'][gender])!=6:raise ValueError('Six radar points per series required')
                points+=panel['marker_pixels'][gender]
            if any(len(p)!=2 or any(type(v)not in (int,float) or not math.isfinite(v)for v in p)for p in points):
                raise ValueError('Invalid traced pixel coordinate')
            if any(math.dist(c,p)<50 for p in panel['axis_endpoints_pixels']):raise ValueError('Degenerate radar axis')
            for gender in ['男性','女性']:
                if any(not 0<r<1.25 for r in fractions(panel,gender)):
                    raise ValueError('Radar marker lies outside inspected range')
        b=d['panels'][2]
        if not 1<fractions(b,'女性')[3]<1.15:
            raise ValueError('B female leisure marker must remain just beyond120; do not clamp it to axis')
        if not fractions(b,'男性')[4]>3*fractions(b,'男性')[5]:
            raise ValueError('B male automobile/rail contrast lost')
    return d


def life_tex(art):
    d=validate(art)
    lines=[r'\begin{tikzpicture}[x=1pt,y=1pt,line width=.55pt,every node/.style={inner sep=0pt,font=\rmfamily\mcfamily\fontsize{12}{14}\selectfont}]',
           r'\path[use as bounding box](0,0)rectangle(600,350);']
    def xy(i,v):return 75+i*32.5,54+v*3
    def node(x,y,t,opts=''):lines.append(rf'\node[{opts}]at({x:.3f},{y:.3f}){{'+t+'};')
    lines += [r'\draw(45,54)--(45,324);',r'\draw(45,54)--(432.5,54);']
    for value in range(0,91,10):
        y=54+3*value;lines.append(rf'\draw(41,{y})--(45,{y});');node(34,y,str(value),'anchor=east')
    node(29,310,r'\%')
    for i,label in enumerate(d['ages']):
        x,_=xy(i,0);lines.append(rf'\draw({x},54)--({x},50);')
        node(x,42,text_tex(label)if i<11 else r'\shortstack{70歳\\以上}','anchor=north')
    # Source-like offsets keep all printed labels readable where curves approach.
    offsets=[[(0,12)]*12,
             [(0,-13),(-7,-14),(-13,0),(0,-13),(0,-13),(-9,-14),(0,12),(9,8),(0,-14),(0,-14),(0,-14),(0,-14)],
             [(0,13),(0,13),(9,7),(0,13),(0,13),(0,13),(0,-13),(13,-3),(0,13),(0,13),(0,13),(0,13)],
             [(0,-14),(0,-14),(0,-14),(0,-14),(0,-14),(10,12),(0,-14),(0,-14),(0,-14),(0,-14),(0,-14),(0,-14)]]
    offsets[0][5]=(0,-11);offsets[0][6]=(0,12)
    offsets[2][4]=(10,8)
    offsets[2][6]=(-10,-3);offsets[1][6]=(10,8)
    offsets[1][7]=(12,1);offsets[2][7]=(12,2);offsets[3][7]=(0,-15)
    offsets[1][9]=(0,12)
    for j,s in enumerate(d['series']):
        pts=[xy(i,v)for i,v in enumerate(s['values'])]
        style='line width=.85pt'+(',dash pattern=on 2pt off 3pt'if s['line']=='dashed'else'')
        lines.append(r'\draw['+style+']'+'--'.join(f'({x:.3f},{y:.3f})'for x,y in pts)+';')
        for (x,y),v,(dx,dy) in zip(pts,s['values'],offsets[j]):
            if s['marker']=='filled_circle':lines.append(rf'\fill({x:.3f},{y:.3f})circle[radius=2.5pt];')
            else:lines.append(rf'\draw[fill=white,line width=.65pt]({x-3:.3f},{y-2:.3f})--({x+3:.3f},{y-2:.3f})--({x:.3f},{y+3.5:.3f})--cycle;')
            node(x+dx,y+dy,str(v),'fill=white,inner sep=.3pt')
        end=pts[-1][1];lines.append(rf'\draw[densely dotted,<-,line width=.45pt](449,{end:.3f})--(515,{end:.3f});')
        node(547,end,"'"+str(s['year'])[2:]+'年')
    node(544,300,'「現在中心」');node(544,98,'「未来中心」')
    node(300,7,text_tex(d['caption']),r'font=\rmfamily\mcfamily\fontsize{12.5}{15}\selectfont')
    lines.append(r'\end{tikzpicture}');return '\n'.join(lines)


def radar_tex(art):
    d=validate(art)
    lines=[r'\begin{tikzpicture}[x=1pt,y=1pt,line width=.8pt,every node/.style={inner sep=0pt,font=\rmfamily\mcfamily\fontsize{18}{21}\selectfont}]',
           r'\path[use as bounding box](0,0)rectangle(1000,375);']
    def node(x,y,t,opts=''):lines.append(rf'\node[{opts}]at({x:.3f},{y:.3f}){{'+t+'};')
    def path(points,opts=''):lines.append(r'\draw['+opts+']'+'--'.join(f'({x:.3f},{y:.3f})'for x,y in points)+';')
    directions=[(math.cos(math.radians(a)),math.sin(math.radians(a)))for a in [90,30,-30,-90,-150,150]]
    for panel_index,(p,cx,radius)in enumerate(zip(d['panels'],[210,555,850],[108,95,95])):
        cy=170;outer=[(cx+dx*radius,cy+dy*radius)for dx,dy in directions]
        node(cx,350,text_tex(p['label']),r'draw,inner xsep=9pt,inner ysep=4pt,font=\InstructionJapanese\fontsize{20}{23}\selectfont')
        for k,(a,b)in enumerate(zip(outer,outer[1:]+outer[:1])):
            dashed=k in ([1,4]if panel_index==0 else[4]if panel_index==2 else[])
            path([a,b],'dash pattern=on 5pt off 4pt'if dashed else'')
        for k,(x,y)in enumerate(outer):
            path([(cx,cy),(x,y)],'dash pattern=on 5pt off 4pt,line width=.7pt')
            if k==0:
                tx,ty=x,y+18;node(tx,ty,str(MAXIMA[k])+'分');node(tx,ty+23,'①')
            elif k==3:
                tx,ty=x+(60 if panel_index==2 else 0),y-18;node(tx,ty,'120分');node(tx,ty-23,'④')
            else:
                tx=x+(25 if k in (1,2)else-25);ty=y
                node(tx,ty+13,'①②③④⑤⑥'[k]);node(tx,ty-10,str(MAXIMA[k])+'分')
        if panel_index==0:
            for x,y,t in [(270,312,'通勤'),(379,236,'買物'),(379,112,'病院'),(292,23,'レジャー'),(40,112,'自動車'),(40,236,'鉄道')]:node(x,y,t)
        if panel_index==2:path([(cx,cy-radius),(cx,cy-radius-40)],'->,dash pattern=on 5pt off 4pt')
        for gender in ['男性','女性']:
            ratios=fractions(p,gender)
            pts=[(cx+dx*radius*v,cy+dy*radius*v)for (dx,dy),v in zip(directions,ratios)]
            path(pts+[pts[0]],'line width=1pt')
            for x,y in pts:
                fill='black'if gender=='男性'else'white'
                lines.append(rf'\draw[fill={fill},line width=.8pt]({x:.3f},{y:.3f})circle[radius=2.8pt];')
        node(cx,cy,'0','fill=white,inner sep=2pt')
    lines.append(r'\end{tikzpicture}');return '\n'.join(lines)


def tex(art):
    return life_tex(art)if art['kind']=='life_goals_lines'else radar_tex(art)
