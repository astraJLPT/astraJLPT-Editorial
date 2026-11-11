"""Native rendering of the independently inspected 1995 gender-equality charts.

Printed labels are data. The final geometric boundary alone follows the observed
100% endpoint because separately rounded printed rows total99.9–100.3%.
"""
from decimal import Decimal
import re
from richtex import text_tex

GEOMETRY='printed_first_five_segments_final_boundary_at_observed_100_percent_endpoint'
# Source215, transcribed independently of the drawing coordinates. The known
# secondary12.8 reading must not silently replace the primary12.1 cell.
PRINTED_ROWS=[
    ['16.8','47.0','29.1','3.9','0.6','2.7'],
    ['8.9','39.2','42.9','5.7','0.6','2.7'],
    ['28.4','50.4','12.1','2.7','0.3','6.0'],
    ['20.3','53.4','19.3','2.6','0.5','3.9'],
    ['17.2','37.7','30.8','1.3','0.3','12.7'],
    ['10.0','30.5','48.4','3.1','0.6','7.7']]
N2_PRINTED_ROWS=[row[:]for row in PRINTED_ROWS]
# The two approved copies differ here. Never normalize one owner to the other.
N2_PRINTED_ROWS[0][4]='0.5'
N2_PRINTED_ROWS[5][4]='0.5'
SOURCE_ROWS={
    ('N1_1995','reading-q019',215,'8560bf8ef92b4e2d58559b3e14882b76d3307586f5d55b0e7fa33cc2f5fa931f'):PRINTED_ROWS,
    ('N2_1995','reading-q018',201,'0a6634758dce0a258ffaf92c6c8ea1a738a4b8ceb52cd75cb44a4d8d340dfa64'):N2_PRINTED_ROWS}

def validate(art):
    identity=(art['unit'],art['item_id'],art['source']['physical_page'],art['source']['source_sha256'])
    if identity not in SOURCE_ROWS:
        raise ValueError('Stacked chart requires its exact inspected source and question')
    d=art['data']
    if set(d)!={'title','categories','patterns','rows','geometry','label_policy','axis'} or d['title']!='男女の地位の平等感':
        raise ValueError('Invalid stacked-chart data fields')
    if d['categories']!=['男性の方が非常に優遇されている','どちらかといえば男性の方が優遇されている','平等',
        'どちらかといえば女性の方が優遇されている','女性の方が非常に優遇されている','わからない']:
        raise ValueError('Source category order changed')
    if d['patterns']!=['crosshatch','north east lines','white','horizontal lines','black','white']:
        raise ValueError('Source category patterns changed')
    if d['geometry']!=GEOMETRY or d['label_policy']!='retain_every_printed_decimal_without_normalization' or d['axis']!=dict(minimum=0,maximum=100,tick=10,unit='%'):
        raise ValueError('Invalid chart axis, geometry or label policy')
    identities=[(g,gender,n)for g in 'ABC'for gender,n in [('女性',1971),('男性',1553)]]
    if len(d['rows'])!=6:raise ValueError('Six source rows required')
    if [row.get('percentages')for row in d['rows']]!=SOURCE_ROWS[identity]:
        raise ValueError('Printed source percentages or row order changed')
    for row,identity in zip(d['rows'],identities):
        if set(row)!={'group','gender','respondents','percentages'}or(row['group'],row['gender'],row['respondents'])!=identity:
            raise ValueError('Source group/gender/respondent order changed')
        labels=row['percentages']
        if len(labels)!=6 or any(not isinstance(v,str)or not re.fullmatch(r'\d{1,2}\.\d',v)for v in labels):
            raise ValueError('Six literal one-decimal printed values required')
        nums=[Decimal(v)for v in labels]
        if any(v<0 or v>100 for v in nums)or abs(sum(nums)-100)>Decimal('.3') or sum(nums[:5])>=100:
            raise ValueError('Printed row is inconsistent with the observed percentage scale')
    return d

def boundaries(row):
    result=[Decimal(0)]
    for value in row['percentages'][:5]:result.append(result[-1]+Decimal(value))
    return [float(v)for v in result]+[100.0]

def tex(art):
    d=validate(art);lines=[r'\begin{tikzpicture}[x=1pt,y=-1pt,line width=.65pt,every node/.style={inner sep=0pt,font=\rmfamily\mcfamily\fontsize{14}{16}\selectfont}]',
        r'\path[use as bounding box](0,0)rectangle(595,475);']
    def node(x,y,text,extra=''):
        lines.append(rf'\node[{extra}]at({x:.3f},{y:.3f}){{'+text+'};')
    def draw(coords,extra=''):
        lines.append(r'\draw['+extra+']'+'--'.join(f'({x:.3f},{y:.3f})'for x,y in coords)+';')
    node(350,14,text_tex(d['title']),r'font=\rmfamily\mcfamily\bfseries\fontsize{15}{17}\selectfont')
    headers=[['男性の方が','非常に優遇','されている'],['どちらかと','いえば男性','の方が優遇','されている'],['平　等'],
        ['どちらかと','いえば女性','の方が優遇','されている'],['女性の方が','非常に優遇','されている'],['わか','らな','い']]
    left=[156,235,305,354,433,512];right=[235,305,354,433,512,568]
    for x,parts in zip(left,headers):
        node(x+3,45,r'\shortstack[l]{'+r'\\'.join(text_tex(p)for p in parts)+'}',r'anchor=north west,font=\rmfamily\mcfamily\fontsize{13}{15}\selectfont')
    row_y=[134,190,246,302,358,414];x0=156;scale=3.8;height=25
    for x in left:draw([(x,42),(x,104)],'line width=.45pt')
    first=boundaries(d['rows'][0])
    for k,x in enumerate(right):draw([(x,101),(x,108),(x0+scale*first[k+1],row_y[0]-height/2)],'dashed,line width=.4pt')
    node(86,118,'（該当者数）',r'font=\rmfamily\mcfamily\fontsize{12.5}{15}\selectfont')
    # All36 printed values stay literal. Small sectors use source-positioned
    # outside labels; the first row's last2.7 also sits outside the common edge.
    small={0:{3:(478,107),4:(515,107),5:(559,134)},1:{4:(516,165),5:(559,190)},
           2:{3:(505,219),4:(537,219)},3:{3:(505,275),4:(537,275),5:(559,302)},
           4:{3:(480,331),4:(514,331)},5:{3:(488,387),4:(525,387)}}
    for j,(row,y)in enumerate(zip(d['rows'],row_y)):
        b=boundaries(row)
        node(146,y,text_tex(row['gender']+f"（{row['respondents']:,}人）"),'anchor=east')
        for k,(a,z,pattern,label)in enumerate(zip(b,b[1:],d['patterns'],row['percentages'])):
            low=x0+scale*a;high=x0+scale*z
            opts='fill='+('black'if pattern=='black'else'white')
            if pattern not in ('white','black'):opts+=',pattern='+pattern+',pattern color=black'
            lines.append(rf'\path[{opts}]({low:.3f},{y-height/2:.3f})rectangle({high:.3f},{y+height/2:.3f});')
            draw([(low,y-height/2),(low,y+height/2)])
            if k in small.get(j,{}):
                tx,ty=small[j][k];node(tx,ty,label)
                if k in (3,4):draw([(tx,ty+8),((low+high)/2,y-height/2)],'densely dotted,line width=.45pt')
            else:
                node((low+high)/2,y,label,'fill=white,inner sep=.8pt')
        draw([(x0,y-height/2),(x0+380,y-height/2),(x0+380,y+height/2),(x0,y+height/2),(x0,y-height/2)])
        if j%2==0:
            nxt=boundaries(d['rows'][j+1])
            for k in range(1,6):draw([(x0+scale*b[k],y+height/2),(x0+scale*nxt[k],row_y[j+1]-height/2)],'densely dotted,line width=.45pt')
    for g,y in zip('ABC',[162,274,386]):
        node(24,y,g,r'font=\rmfamily\fontsize{32}{36}\selectfont')
        draw([(58,y-28),(45,y-28),(45,y+28),(58,y+28)],'line width=.55pt')
    draw([(156,444),(536,444)],'line width=.6pt')
    for v in range(0,101,10):
        x=156+3.8*v;draw([(x,440),(x,446)],'line width=.6pt');node(x,456,str(v),'anchor=north')
    node(555,456,r'(\%)','anchor=north west')
    lines.append(r'\end{tikzpicture}')
    return '\n'.join(lines)
