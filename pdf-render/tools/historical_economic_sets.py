"""Source158 category relationships: native lines and literal Japanese labels."""
from richtex import text_tex
OWNER=('N2_1994','reading-q017',158,'0a6634758dce0a258ffaf92c6c8ea1a738a4b8ceb52cd75cb44a4d8d340dfa64')
def data(option):
 if type(option)is not int or option not in range(1,5):raise ValueError('Category diagram option must be1–4')
 headers=['モノ','商品','サービス',None];members=[['商品','サービス'],['モノ','サービス'],['モノ','商品'],['モノ','商品','サービス']]
 return dict(option=option,header=headers[option-1],members=members[option-1],relationship='shared_parent'if option<4 else'peer_partition',member_writing='vertical',border='rounded',geometry='source_traced_regularized_curves',header_in_top_gap=option<4)
def validate(art):
 if(art['unit'],art['item_id'],art['source']['physical_page'],art['source']['source_sha256'])!=OWNER:raise ValueError('Category diagram requires exact reviewed source and question')
 d=art['data']
 if d!=data(d.get('option')):raise ValueError('Category labels, nesting or option order changed')
 return d
def tex(art):
 d=validate(art);out=[r'\begin{tikzpicture}[x=1pt,y=-1pt,line width=.65pt,every node/.style={inner sep=0pt,font=\rmfamily\mcfamily\fontsize{18}{20}\selectfont}]',r'\path[use as bounding box](0,0)rectangle(180,180);']
 def node(x,y,t,rotate=False):out.append(r'\node'+('[rotate=90]'if rotate else'')+f' at({x},{y})'+'{'+text_tex(t)+'};')
 if d['header']:
  out.append(r'\draw(59,20)..controls(35,20)and(20,35)..(20,58)--(20,132)..controls(20,156)and(35,170)..(58,170)--(117,170)..controls(141,170)and(155,155)..(155,132)--(155,58)..controls(155,35)and(141,20)..(116,20);')
  out.append(r'\draw(87.5,40)--(87.5,170);')
  header=d['header'];step=30 if len(header)==2 else 18
  for i,c in enumerate(header):node(87.5+(i-(len(header)-1)/2)*step,18,c)
  xs=[54,121]
 else:
  out.append(r'\draw[rounded corners=35pt](5,30)rectangle(175,162);\draw(61,30)--(61,162);\draw(118,30)--(118,162);');xs=[33,89.5,146.5]
 for x,word in zip(xs,d['members']):
  ys=[65,126]if len(word)==2 else[65,86,107,128]
  for y,c in zip(ys,word):node(x,y,c,rotate=c=='ー')
 out.append(r'\end{tikzpicture}');return '\n'.join(out)
