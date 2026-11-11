"""Individually reviewed 1994 enrolment choices in approximate image coordinates.

The source prints no data labels at the 72 sampled vertices. Their pixel
positions describe geometry only; they are never emitted as precise values.
"""
from richtex import text_tex
OWNER=('N1_1994','reading-q018',169,'8560bf8ef92b4e2d58559b3e14882b76d3307586f5d55b0e7fa33cc2f5fa931f')
N2_OWNER=('N2_1994','reading-q021',161,'0a6634758dce0a258ffaf92c6c8ea1a738a4b8ceb52cd75cb44a4d8d340dfa64')
YEARS=[1965,1970,1975,1980,1985,1990]
X=[59,103,147,191,236,281]
TRACES=[
 [[176,168,163,113,89,72],[200,195,188,141,104,64],[224,220,213,170,129,58]],
 [[175,145,86,93,95,119],[200,171,106,110,111,113],[223,195,131,128,124,105]],
 [[174,148,82,90,93,101],[199,174,102,106,106,109],[224,197,133,128,124,116]],
 [[174,167,162,111,90,74],[201,194,188,139,108,85],[225,220,214,171,132,97]]]
N2_TRACES=[
 [[177,171,166,117,93,78],[201,197,189,143,110,69],[225,222,214,173,133,62]],
 [[177,149,88,96,98,122],[200,174,109,112,114,116],[225,197,133,131,128,108]],
 [[175,148,84,92,94,103],[201,174,105,108,109,111],[222,198,133,129,124,117]],
 [[177,170,165,117,96,77],[203,197,189,144,110,88],[225,221,213,173,132,99]]]

def data(option,unit='N1_1994'):
 if type(option)is not int or option not in range(1,5):raise ValueError('Source graph option must be1–4')
 if unit not in [OWNER[0],N2_OWNER[0]]:raise ValueError('Unreviewed enrolment graph owner')
 traces=N2_TRACES if unit==N2_OWNER[0]else TRACES
 tick=(43 if option==3 else 43.25)if unit==N2_OWNER[0]else 44.2
 return dict(option=option,coordinate_status='approximate_digitization_not_exact_historical_data',years=YEARS,x_pixels=X,baseline_pixel=270 if option==3 else 273,tick_pixels_per_ten=tick,printed_y_ticks=[0,10,20,30,40],y_axis_top_pixel=12 if unit==N2_OWNER[0]else 8,series=[dict(label=label,line=line,marker=marker,y_pixels=ys)for(label,line,marker),ys in zip([('男子','short_dashed','diamond'),('全体','solid','circle'),('女子','dash_dot','square')],traces[option-1])])
def validate(art):
 if(art['unit'],art['item_id'],art['source']['physical_page'],art['source']['source_sha256'])not in [OWNER,N2_OWNER]:raise ValueError('Enrolment graph requires exact reviewed source and question')
 d=art['data']
 if d!=data(d.get('option'),art['unit']):raise ValueError('Source graph option/order, axes, labels or approximate trace changed')
 return d
def tex(art):
 d=validate(art);base=d['baseline_pixel'];top=d['y_axis_top_pixel'];out=[r'\begin{tikzpicture}[x=1pt,y=-1pt,line width=.75pt,every node/.style={inner sep=0pt,font=\rmfamily\mcfamily\fontsize{14}{16}\selectfont}]',r'\path[use as bounding box](0,0)rectangle(345,307);',rf'\draw(59,{top})--(59,{base})--(325,{base});']
 def node(x,y,text,opts=''):out.append(rf'\node[{opts}]at({x},{y})'+'{'+text_tex(text)+'};')
 node(28,42,'進学率');node(31,58,'（%）')
 for v in d['printed_y_ticks']:
  yy=base-v*d['tick_pixels_per_ten']/10;out.append(rf'\draw(55,{yy})--(59,{yy});');node(52,yy,str(v),'anchor=east')
 for x,y in zip(d['x_pixels'],d['years']):
  out.append(rf'\draw({x},{base})--({x},{base+5});');node(x,base+17,str(y))
 node(313,base+17,'（年）')
 styles={'short_dashed':'dash pattern=on 2.2pt off 3pt','solid':'solid','dash_dot':'dash pattern=on 6pt off 2pt on 1pt off 2pt'}
 for s in d['series']:
  pts=list(zip(d['x_pixels'],s['y_pixels']));out.append(r'\draw['+styles[s['line']]+']'+'--'.join(f'({x},{y})'for x,y in pts)+';')
  for x,y in pts:
   if s['marker']=='circle':out.append(rf'\fill({x},{y})circle[radius=1.65pt];')
   elif s['marker']=='square':out.append(rf'\fill({x-1.7},{y-1.7})rectangle({x+1.7},{y+1.7});')
   else:out.append(rf'\fill({x},{y-2})--({x+2},{y})--({x},{y+2})--({x-2},{y})--cycle;')
 if d['option']in[1,4]:labels=[('男子',168,85,(174,94),(187,118)),('女子',263,190,(244,180),(214,151)),('全体',228,231,(208,220),(153,184))]
 else:labels=[('男子',111,70,(121,80),(132,103)),('女子',184,185,(164,175),(141,157)),('全体',126,235,(119,224),(88,183))]
 for label,x,y,a,b in labels:
  node(x,y,label);out.append(r'\draw[-{Stealth[length=3.5pt,width=3pt]}]'+f'({a[0]},{a[1]})--({b[0]},{b[1]});')
 out.append(r'\end{tikzpicture}');return '\n'.join(out)
