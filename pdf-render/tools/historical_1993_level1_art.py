"""Native source-bound 1993 Level1/2 room chart and Level1 group choices."""
from richtex import text_tex
SOURCE='fdd0d022acc4a1fffd3f9e5785b4a32d3d5a58d28c3d9c2bdeb9f65b10f5fe43'

def data(kind,option=None):
    if kind=='private_room_graph':
        return dict(coordinate_status='printed_numeric_values',axis=dict(minimum=0,maximum=100,step=10,unit='％'),households=[1,2,3,4,5,'6以上'],series=[
            dict(tag='a',line='dashdot',values=[0,52.8,89.1,97.8,92.3,95.6]),
            dict(tag='b',line='dashed',values=[5.0,3.4,9.0,21.8,27.8,42.6]),
            dict(tag='c',line='solid',values=[0,1.3,4.3,13.1,16.4,23.5])],
            labels='all printed values; shared origin0 once',geometry='source_traced_regularized_axes_and_label_positions')
    if kind!='animal_group_option' or type(option)is not int or option not in range(1,5):
        raise ValueError('Unknown1993source diagram/option')
    heads=['集まり','集団','群れ','動物'];members=[['集団','群れ'],['集まり','群れ'],['集まり','集団'],['集まり','群れ','集団']]
    return dict(option=option,header=heads[option-1],members=members[option-1],member_writing='vertical',border='rounded',geometry='source_traced_regularized_curves')

def validate(art):
    kind=art['kind']
    owners={'private_room_graph':{('N1_1993','reading-b007',33),('N2_1993','reading-b005',67)},'animal_group_option':{('N1_1993','reading-q020',34)}}
    if (art['unit'],art['item_id'],art['source']['physical_page'])not in owners[kind]or art['source']['source_sha256']!=SOURCE:
        raise ValueError('1993art requires exact reviewed owner/item/source')
    if art.get('data')!=data(kind,art.get('data',{}).get('option')):
        raise ValueError('1993art printed values,labels,relationships or option order changed')
    return art['data']

def tex(art):
    d=validate(art)
    if art['kind']=='animal_group_option':
        out=[r'\begin{tikzpicture}[x=1pt,y=-1pt,line width=.6pt,every node/.style={inner sep=0pt,font=\rmfamily\mcfamily\fontsize{18}{20}\selectfont}]',r'\path[use as bounding box](0,0)rectangle(180,155);',r'\draw[rounded corners=32pt](5,48)rectangle(175,145);',r'\node at(90,20){'+text_tex(d['header'])+'};']
        n=len(d['members']);cell=170/n
        for i in range(1,n):out.append(r'\draw'+f'({5+cell*i:.4f},48)--({5+cell*i:.4f},145);')
        for i,word in enumerate(d['members']):
            ys=[78,124]if len(word)==2 else[73,98,123]
            for y,c in zip(ys,word):out.append(r'\node'+f' at({5+cell*(i+.5):.4f},{y})'+'{'+text_tex(c)+'};')
        out.append(r'\end{tikzpicture}');return '\n'.join(out)
    out=[r'\begin{tikzpicture}[x=1pt,y=1pt,line width=.45pt,every node/.style={inner sep=0pt,font=\rmfamily\mcfamily\fontsize{9}{10}\selectfont}]',r'\path[use as bounding box](-20,-66)rectangle(305,248);',r'\draw(0,230)--(0,0)--(304,0);',r'\node[anchor=south]at(-8,233){(\%)};']
    for y in range(0,101,10):
        out.append(r'\draw'+f'(0,{y*2.3:.4f})--(4,{y*2.3:.4f});')
        out.append(r'\node[anchor=east]'+f' at(-3,{y*2.3:.4f})'+'{'+str(y)+'};')
    for i in range(6):
        x=25+43*i
        out.append(r'\draw'+f'({x},0)--({x},4);')
        out.append(r'\node'+f' at({x},-9)'+'{'+str(i+1)+'};')
        if i<5:
            for j,c in enumerate('部屋世帯'):out.append(r'\node'+f' at({x},{-21-j*10})'+'{'+c+'};')
        else:
            for j,c in enumerate('部屋'):out.append(r'\node'+f' at({x-4},{-21-j*10})'+'{'+c+'};')
            for j,c in enumerate('以上世帯'):out.append(r'\node'+f' at({x+6},{-21-j*10})'+'{'+c+'};')
    styles={'solid':'','dashed':'dash pattern=on2.5pt off1.8pt','dashdot':'dash pattern=on6pt off2pt on.7pt off2pt'}
    for series in d['series']:
        points='--'.join(f'({25+43*i},{v*2.3:.4f})' for i,v in enumerate(series['values']))
        out.append(r'\draw['+styles[series['line']]+']'+points+';')
        for i,v in enumerate(series['values']):
            if i==0 and series['tag']!='b':continue
            x=25+43*i;y=v*2.3+6
            if i==0:x-=9
            if series['tag']=='a' and i in (1,2):x-=8
            if series['tag']=='b' and i in (2,4):x-=8
            if i==1 and series['tag']=='c':x-=26;y=5.6
            if i==2 and series['tag']=='c':x-=3;y-=1
            out.append(r'\node'+f' at({x},{y:.4f})'+'{'+f'{v:.1f}'+'};')
        y=series['values'][-1]*2.3
        out.append(r'\draw[latex-]'+f'(247,{y:.4f})--(273,{y:.4f});')
        out.append(r'\node[anchor=west]'+f' at(278,{y:.4f})'+'{〔'+series['tag']+'〕};')
    out.append(r'\node[anchor=east]at(24,4){0};')
    out.append(r'\end{tikzpicture}');return '\n'.join(out)
