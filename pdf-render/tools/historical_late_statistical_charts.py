"""Source-bound 2006–08 charts. Printed values and approximate traces stay distinct."""
import math
from decimal import Decimal
from richtex import text_tex

N1_SOURCE='e3555741c8f14b855a32e7d09b42eb790492e3818a85a875f99d84703c752e00'
N2_SOURCE='115e8c098ee3caed702d29a24d2ce0c883c3ad9152e21eee4200fc4e80f2a3fb'
IDENTITIES={
    'company_choice_lines':{('N1_2008','reading-b009',108,N1_SOURCE),('N2_2008','reading-b009',97,N2_SOURCE)},
    'national_condition_lines':{('N1_2007','reading-b009',148,N1_SOURCE),('N2_2007','reading-b009',132,N2_SOURCE)},
    'career_preparation_bars':{('N1_2006','reading-b009',187,N1_SOURCE),('N2_2006','reading-b008',166,N2_SOURCE)}}
COMPANY_SERIES=[
    ('会社の将来を考えて','filled_circle',[27,9]),
    ('仕事がおもしろいから','filled_triangle',[16,21]),
    ('実力主義の会社だから','asterisk',[6,3]),
    ('給料が高いから','plus',[4,3]),
    ('一流会社だから','star',[3,5]),
    ('寮グランドなど福利厚生が充実しているから','hollow_diamond',[1,2]),
    ('労働時間が短く、休日が多いから','cross',[0,1]),
    ('自分の能力、個性が生かせるから','filled_diamond',[19,29]),
    ('技術が覚えられるから','filled_square',[7,14]),
    ('どこも行くところがなくやむなく','hollow_circle',[5,3]),
    ('地理的条件が良いから','hollow_down_triangle',[4,4]),
    ('経営者に魅力を感じたから','hollow_square',[1,5]),
    ('先輩が多いから','hollow_triangle',[1,1])]
CONDITION_YEARS=[1973,1978,1988,1993,1998,2003]
CONDITION_TICKS=[1973,1978,1983,1988,1993,1998,2003]
CONDITION_SERIES=[
    ('ア','hollow_circle','solid',[211,193,175,169,216,211]),
    ('イ','hollow_square','dashdot',[326,275,345,291,333,297]),
    ('ウ','filled_triangle','dashed',[389,319,261,255,378,397]),
    ('エ','filled_circle','dotted',[297,303,209,228,501,501]),
    ('オ','filled_square','fine_dotted',[462,426,467,450,537,542])]
CAREER_ROWS=[['48.7','45.7','5.7'],['60.7','34.6','4.6'],['82.6','14.2','3.3'],
             ['67.5','27.6','4.9'],['61.2','34.1','4.8'],['59.6','36.7','3.7']]
CAREER_TITLES=['質問1「どうしたらその職業につくことができるのかを調べること」',
               '質問2「その職業につくために努力していること」']
CAREER_CAPTION='（グラフはBenesse教育研究開発センター「第1回子ども生活実態基本調査」による）'
PATTERNS={'solid':'','dashdot':'dash pattern=on 5pt off 3pt on .8pt off 3pt',
          'dashed':'dash pattern=on 6pt off 4pt','dotted':'dash pattern=on .8pt off 3pt',
          'fine_dotted':'dash pattern=on .4pt off 1.2pt,line width=.5pt',
          'thin_solid':'line width=.5pt'}

def validate(art):
    kind=art['kind']
    identity=(art['unit'],art['item_id'],art['source']['physical_page'],art['source']['source_sha256'])
    if kind not in IDENTITIES or identity not in IDENTITIES[kind]:
        raise ValueError('Late statistical chart requires its inspected owner/item/source')
    d=art['data']
    if kind=='company_choice_lines':
        if set(d)!={'coordinate_status','years','axis','series','shared_value_label_policy','note_profile'}:
            raise ValueError('Invalid company-chart fields')
        expected=[dict(label=a,marker=b,values=c)for a,b,c in COMPANY_SERIES]
        if d['coordinate_status']!='printed_integer_values_with_documented_14_repair' or d['series']!=expected:
            raise ValueError('Company series, printed values or documented correction changed')
        if d['years']!=[1971,2007] or d['axis']!=dict(minimum=0,maximum=35,tick=5,unit='%'):
            raise ValueError('Company axis or year order changed')
        if d['shared_value_label_policy']!='one_label_per_observed_common_endpoint_value_all_series_retained' or d['note_profile']!=art['unit']:
            raise ValueError('Company shared-label or owner-note policy changed')
    elif kind=='national_condition_lines':
        if set(d)!={'coordinate_status','years','year_ticks','axis','trace_witness','series','point_label_policy'}:
            raise ValueError('Invalid condition-chart fields')
        if d['coordinate_status']!='approximate_pixel_digitization_not_exact_historical_data' or d['years']!=CONDITION_YEARS or d['year_ticks']!=CONDITION_TICKS:
            raise ValueError('Condition precision or missing1983point changed')
        if d['axis']!=dict(minimum=0,maximum=100,tick=10,unit='%') or d['point_label_policy']!='no_invented_numeric_point_labels':
            raise ValueError('Condition axis or point labels changed')
        expected=[dict(label=a,marker=b,line=c,marker_y_pixels=e)for a,b,c,e in CONDITION_SERIES]
        # The N2own witness has a solid square-marker series; N1is fine dotted.
        # Point coordinates share the clearer N1trace, but line patterns do not.
        if art['unit']=='N2_2007':expected[-1]['line']='thin_solid'
        if d['series']!=expected or d['trace_witness']!=dict(image_sha256='8291311a393cf9519d948015bd4232494326c58d276acff0b2ba0de7c363d250',zero_y=689,hundred_y=106,marker_x_pixels=[140,244,451,555,658,762]):
            raise ValueError('Condition source trace or series identity changed')
    else:
        if set(d)!={'coordinate_status','titles','groups','categories','patterns','rows','axis','geometry','caption','document_witness'}:
            raise ValueError('Invalid career-chart fields')
        if d['coordinate_status']!='literal_printed_one_decimal_values_no_normalization' or d['titles']!=CAREER_TITLES or d['rows']!=CAREER_ROWS:
            raise ValueError('Career printed values, order or titles changed')
        if d['groups']!=['小学生','中学生','高校生'] or d['categories']!=['ある','ない','無回答・不明'] or d['patterns']!=['north east lines','white','dots']:
            raise ValueError('Career category, pattern or school order changed')
        if d['axis']!=dict(minimum=0,maximum=100,tick=10,unit='%') or d['geometry']!='printed_first_two_segments_final_boundary_at_observed_100_percent_endpoint' or d['caption']!=CAREER_CAPTION:
            raise ValueError('Career geometry, scale or caption changed')
        expected={'N1_2006':('527ab2b0e6019ef9556622890ccbfb7cde9eca04d9f53be035f1081492bc4b59','8def703f183ae39d950c0823b16b52fe7690f6c4b7aa84216c545dcec7f96120'),
                  'N2_2006':('92e2246c531ab144976d7a8a9f5db64bbfc24072a056976d76d153d606d2387f','e0fde0e201d056cd26e465eb8d22c22b90c260044538a9aafed4add2078f6c70')}[art['unit']]
        if d['document_witness']!=dict(source_sha256=expected[0],image_sha256=expected[1]):
            raise ValueError('Career recovery requires its own retained document witness')
    return d

class Drawing:
    def __init__(self,width,height,font=14):
        self.lines=[rf'\begin{{tikzpicture}}[x=1pt,y=-1pt,line width=.7pt,every node/.style={{inner sep=0pt,font=\rmfamily\mcfamily\fontsize{{{font}}}{{{font+2}}}\selectfont}}]',rf'\path[use as bounding box](0,0)rectangle({width},{height});']
    def node(self,x,y,t,opts=''):
        self.lines.append(rf'\node[{opts}]at({x:.3f},{y:.3f}){{'+t+'};')
    def path(self,pts,opts=''):
        self.lines.append(r'\draw['+opts+']'+'--'.join(f'({x:.3f},{y:.3f})'for x,y in pts)+';')
    def rect(self,x,y,w,h,opts=''):
        self.lines.append(rf'\draw[{opts}]({x:.3f},{y:.3f})rectangle({x+w:.3f},{y+h:.3f});')
    def marker(self,x,y,kind,r=4,opaque=True):
        fill=('white'if opaque else'none')if kind.startswith('hollow')else'black'
        if 'circle'in kind:
            self.lines.append(rf'\draw[fill={fill},line width=.8pt]({x:.3f},{y:.3f})circle[radius={r}pt];')
        elif 'square'in kind:self.rect(x-r,y-r,r*2,r*2,'fill='+fill)
        elif 'diamond'in kind:self.path([(x,y-r*1.3),(x+r*1.2,y),(x,y+r*1.3),(x-r*1.2,y),(x,y-r*1.3)],'fill='+fill)
        elif 'triangle'in kind:
            flip=-1 if 'down'in kind else 1
            self.path([(x,y-r*1.3*flip),(x+r*1.2,y+r*.9*flip),(x-r*1.2,y+r*.9*flip),(x,y-r*1.3*flip)],'fill='+fill)
        elif kind=='star':
            pts=[(x+math.cos(-math.pi/2+k*math.pi/5)*(r*1.3 if k%2==0 else r*.5),y+math.sin(-math.pi/2+k*math.pi/5)*(r*1.3 if k%2==0 else r*.5))for k in range(10)]
            self.path(pts+[pts[0]],'fill=black')
        else:
            if kind in ['plus','asterisk']:
                self.path([(x-r*1.3,y),(x+r*1.3,y)],'line width='+('1.3pt'if kind=='plus'else'.65pt'))
                self.path([(x,y-r*1.3),(x,y+r*1.3)],'line width='+('1.3pt'if kind=='plus'else'.65pt'))
            if kind in ['cross','asterisk']:
                self.path([(x-r,y-r),(x+r,y+r)])
                self.path([(x-r,y+r),(x+r,y-r)])
    def finish(self):return '\n'.join(self.lines+[r'\end{tikzpicture}'])

def company_legend(unit,index,label):
    def note(n):return r'\textsuperscript{\fontsize{8}{9}\selectfont(注'+str(n)+')}'
    if index==5:
        a,b=(2,3)if unit=='N1_2008'else(4,5)
        return r'\shortstack[l]{寮グランド'+note(a)+r'など\ruby{福利厚生}{ふくりこうせい}'+note(b)+r'が\\充実'+(note(6)if unit=='N2_2008'else'')+'しているから}'
    if index==7 and unit=='N2_2008':return '自分の能力、個性'+note(1)+'が生かせる'+note(2)+'から'
    if index==9:return 'どこも行くところがなくやむなく'+note(1 if unit=='N1_2008'else 3)
    return text_tex(label)

def company_tex(art):
    d=validate(art)
    g=Drawing(800,1020,15)
    g.rect(5,5,790,245)
    for i,s in enumerate(d['series']):
        col=0 if i<7 else 1
        row=i if col==0 else i-7
        x=24 if col==0 else 425
        y=[25,57,89,121,153,193,233][row]
        g.path([(x,y),(x+30,y)])
        g.marker(x+15,y,s['marker'],4)
        g.node(x+40,y,company_legend(art['unit'],i,s['label']),r'anchor=west,font=\rmfamily\mcfamily\fontsize{13}{15}\selectfont')
    left,top,width,height=60,300,680,650
    g.rect(left,top,width,height)
    g.node(left-18,top-22,r'\%')
    for v in range(0,36,5):
        y=top+height*(35-v)/35
        g.path([(left,y),(left+5,y)])
        g.node(left-10,y,str(v),'anchor=east')
    xs=[230,570]
    endpoints={}
    for s in d['series']:
        pts=[(x,top+height*(35-v)/35)for x,v in zip(xs,s['values'])]
        g.path(pts,'line width=.75pt')
        for x,y in pts:endpoints.setdefault((x,y),[]).append(s['marker'])
    for (x,y),markers in endpoints.items():
        if len(markers)==1:
            g.marker(x,y,markers[0],4.5)
            continue
        # Source series genuinely coincide. Clear crossing lines once, then
        # retain every outline and draw the interior marks without white erasure.
        g.lines.append(rf'\fill[white]({x:.3f},{y:.3f})circle[radius=6.3pt];')
        for marker in markers:
            if marker.startswith('hollow'):g.marker(x,y,marker,4.5,opaque=False)
        for marker in markers:
            if not marker.startswith('hollow'):g.marker(x,y,marker,3.3)
    # Coincident source endpoints share one printed label; no series is dropped.
    for side,x in enumerate(xs):
        for v in sorted({s['values'][side]for s in d['series']}):
            y=top+height*(35-v)/35
            g.node(x+(-13 if side==0 else 13),y,str(v),'anchor='+('east'if side==0 else'west'))
    for x,t in zip(xs,['昭和46(1971)年度','平成19(2007)年度']):g.node(x,982,text_tex(t))
    return g.finish()

def condition_tex(art):
    d=validate(art)
    g=Drawing(600,485,13)
    g.rect(2,2,596,481,'line width=.5pt')
    left,top,width,height=49,54,430,345
    g.node(24,28,r'(\%)')
    g.path([(left,top),(left,top+height),(left+width,top+height)])
    for v in range(0,101,10):
        y=top+height*(100-v)/100
        g.path([(left,y),(left+width,y)],'line width=.4pt')
        g.node(left-8,y,str(v),'anchor=east')
    def xp(y):return left+30+(y-1973)*((width-60)/30)
    for year in d['year_ticks']:
        x=xp(year)
        g.path([(x,top+height),(x,top+height-4)])
        g.node(x,428,str(year))
    g.node(517,428,'（年）')
    g.rect(494,174,92,138,'line width=.5pt')
    trace=d['trace_witness']
    for index,s in enumerate(d['series']):
        pts=[(xp(y),top+(p-trace['hundred_y'])/(trace['zero_y']-trace['hundred_y'])*height)for y,p in zip(d['years'],s['marker_y_pixels'])]
        opts=PATTERNS[s['line']]
        g.path(pts,opts)
        for x,y in pts:g.marker(x,y,s['marker'],3.3)
        yy=189+index*26
        g.path([(501,yy),(551,yy)],opts)
        g.marker(526,yy,s['marker'],3.3)
        g.node(570,yy,text_tex(s['label']))
    return g.finish()

def career_tex(art):
    d=validate(art)
    g=Drawing(620,820,14)
    left,scale,height=70,4.9,31
    for panel in range(2):
        offset=panel*390
        g.node(315,offset+18,text_tex(d['titles'][panel]),r'font=\InstructionJapanese\fontsize{12}{15}\selectfont')
        for x,label,pattern in zip([215,325,425],d['categories'],d['patterns']):
            opts='fill=white'+(',pattern='+pattern+',pattern color=black'if pattern!='white'else'')
            g.rect(x-20,offset+41,14,12,opts)
            g.node(x,offset+47,text_tex(label),'anchor=west')
        for row in range(3):
            y=offset+103+row*87
            labels=d['rows'][panel*3+row]
            b=[0,float(Decimal(labels[0])),float(Decimal(labels[0])+Decimal(labels[1])),100]
            g.node(left-10,y,text_tex(d['groups'][row]),'anchor=east')
            for k,(a,z,label,pattern)in enumerate(zip(b,b[1:],labels,d['patterns'])):
                x=left+a*scale
                opts='fill=white'+(',pattern='+pattern+',pattern color=black'if pattern!='white'else'')
                g.rect(x,y-height/2,(z-a)*scale,height,opts)
                if k==2 and row==2:
                    g.path([(left+scale*(a+z)/2,y),(579,y)],'line width=.4pt')
                    g.node(584,y,label,'anchor=west,fill=white,inner sep=.5pt')
                else:g.node(left+scale*(a+z)/2,y,label,r'fill=white,inner sep=.7pt,font=\rmfamily\fontsize{12}{14}\selectfont')
        axis_y=offset+320
        g.path([(left,axis_y),(left+scale*100,axis_y)])
        for v in range(0,101,10):
            x=left+scale*v
            g.path([(x,axis_y),(x,axis_y-4)])
            g.node(x,axis_y+18,str(v)+r'\%',r'font=\rmfamily\fontsize{12}{14}\selectfont')
    g.node(310,795,text_tex(d['caption']),r'font=\rmfamily\mcfamily\fontsize{10.5}{13}\selectfont')
    return g.finish()

def tex(art):
    return {'company_choice_lines':company_tex,'national_condition_lines':condition_tex,'career_preparation_bars':career_tex}[art['kind']](art)
