"""Source-bound1993Level2 consciousness diagrams, with live vertical labels."""
from richtex import text_tex
SOURCE='fdd0d022acc4a1fffd3f9e5785b4a32d3d5a58d28c3d9c2bdeb9f65b10f5fe43'
def data(option):
    if type(option)is not int or option not in range(1,5):raise ValueError('Invalid consciousness option')
    labels=[['無意識','意識','意識'],['意識','無意識','無意識'],['無意識','意識','無意識'],['意識','無意識','意識']]
    upper,left,right=labels[option-1]
    return dict(option=option,upper_right=upper,lower_left=left,lower_right=right,top_ratio=[0,2],bottom_ratio=[49,51],dashed_spans=[49,49],bars='left ends at shared dividing line; right extends above it',geometry='schematic source-traced relationships; lengths not a precise numeric scale',writing='vertical Japanese labels; horizontal ratios')
def validate(art):
    if (art['kind'],art['unit'],art['item_id'],art['source']['physical_page'],art['source']['source_sha256'])!=('consciousness_option','N2_1993','reading-q014',65,SOURCE):raise ValueError('Unreviewed consciousness owner/item/source')
    if art.get('data')!=data(art.get('data',{}).get('option')):raise ValueError('Changed consciousness labels, ratios or order')
    return art['data']
def tex(art):
    d=validate(art)
    out=[r'\begin{tikzpicture}[x=1pt,y=-1pt,line width=.4pt,every node/.style={inner sep=0pt,font=\rmfamily\mcfamily\fontsize{12}{14}\selectfont}]',r'\path[use as bounding box](0,0)rectangle(160,220);',r'\draw(0,65)--(160,65);',r'\draw(0,180)--(160,180);',r'\draw[line width=2pt](34,65)--(34,180);',r'\draw[line width=2pt](119,50)--(119,180);']
    for x in [34,119]:
        out.append(r'\draw[dash pattern=on3pt off2pt]'+f'({x},65)..controls({x-22},96)and({x-22},149)..({x},180);')
        out.append(r'\node[fill=white,inner sep=.6pt]'+f'at({x-19},122)'+'{49};')
    for y,values in [(37,d['top_ratio']),(202,d['bottom_ratio'])]:
        for x,label in zip([34,76.5,119],[values[0],':',values[1]]):out.append(r'\node '+f'at({x},{y})'+'{'+str(label)+'};')
    for x,center,word in [(140,33,d['upper_right']),(54,122,d['lower_left']),(140,122,d['lower_right'])]:
        step=14 if len(word)==3 else 28
        for j,char in enumerate(word):out.append(r'\node '+f'at({x},{center+(j-(len(word)-1)/2)*step})'+'{'+text_tex(char)+'};')
    out.append(r'\end{tikzpicture}');return '\n'.join(out)
