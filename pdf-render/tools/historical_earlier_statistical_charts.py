"""Inspected 1991/2002–05 chart families; literal labels and traces are distinct."""
import copy,math
from richtex import text_tex
from historical_late_statistical_charts import Drawing,PATTERNS,N1_SOURCE,N2_SOURCE

L4_SOURCE='6da6084a74b617608dfaef9bc70072dd8ea7bac410ef77de7ae90f5603c569db'
IDENTITIES={
    'scale_comparison_bars':{('N1_2005','reading-b003',223,N1_SOURCE)},
    'conversation_opinion_lines':{('N1_2005','reading-b009',227,N1_SOURCE),('N2_2005','reading-b009',200,N2_SOURCE)},
    'education_goal_bars':{('N1_2004','reading-b010',265,N1_SOURCE),('N2_2004','reading-b009',233,N2_SOURCE)},
    'phone_reading_bars':{('N1_2003','reading-b009',303,N1_SOURCE),('N2_2003','reading-b009',265,N2_SOURCE)},
    'employment_intent_option':{('N1_2002','reading-q023',338,N1_SOURCE),('N1_2002','reading-q023',339,N1_SOURCE),('N2_2002','reading-q021',299,N2_SOURCE)},
    'score_distribution_option':{('N4_1991','reading-q044',48,L4_SOURCE)},
    'smoking_distribution_option':{('N4_1991','reading-q045',48,L4_SOURCE)}}
OPINION_VALUES=[['35.5','39.1','38.9','36.4','26.6','26.3'],['22.3','30.5','29.1','41.1','41.2','31.8'],['19.8','18.6','14.0','8.9','17.1','19.5'],['17.4','10.0','14.9','11.2','11.1','12.8']]
EDUCATION_VALUES=[[27,16,13,39,3,2],[24,15,11,45,3,2,1],[18,17,8,47,6,4,1]]
EDUCATION_BREAKS=[[166,383,509,614,930,953,970],[166,356,476,563,923,946,962,970],[166,308,444,506,882,930,962,970]]
EMPLOYMENT_TRACES=[
    dict(image_sha256='e93a52a0811d04f09c41b367effcc30e72715c1ed4e917480daf0df08adadb2a',axis=[310,1247],breaks=[[492,647],[380,742],[723,997],[559,1042]]),
    dict(image_sha256='8e7eaa28ed5b2589b96dbdea0f8495a3c1c8a8df19a30f6aeaf6228811f04016',axis=[309,1244],breaks=[[562,993],[786,1041],[489,645],[377,739]]),
    dict(image_sha256='8b912d7dbf9516ca920c922c236f1ce3095292c9efe6250bdd92008ef02511ca',axis=[308,1243],breaks=[[721,994],[558,1042],[377,739],[489,645]]),
    dict(image_sha256='16b70830e59a44db6366ae76ec9aebcc25e549cf3352618b01767022611b526f',axis=[309,1244],breaks=[[722,996],[559,1043],[490,646],[378,740]])]
SCORE_VALUES=[[10,15,5,10],[10,20,15,10],[15,15,5,10],[10,15,20,5]]
SMOKING_TRACES=[
    dict(image_sha256='f21cb0be857dac727cd4d238506ec6479c2656d63354bf4c29629ec3d6db3863',center=[89,94],rays=[[89,25],[139,143],[20,94],[40,46]],clockwise_labels=['ぜんぜんすわない人','たくさんすう人','ときどきすう人','すこしすう人']),
    dict(image_sha256='3c10e0582ff677cff1643586adc635fef563e26b274e262ae8600e5d1e7b9771',center=[92,93],rays=[[91,23],[94,162],[24,93],[65,28]],clockwise_labels=['ぜんぜんすわない人','すこしすう人','たくさんすう人','ときどきすう人']),
    dict(image_sha256='5abf41435e7d1733901672f31fdd2bd2ee7f8ba9fceac35bb47a0713f2d74505',center=[94,97],rays=[[94,28],[94,166],[29,122],[43,49]],clockwise_labels=['ぜんぜんすわない人','すこしすう人','ときどきすう人','たくさんすう人']),
    dict(image_sha256='6324944bffa31087eb6c66946e88f7d7c9dc8ece294b418298d80a30550102a2',center=[94,95],rays=[[94,26],[94,165],[24,96],[44,47]],clockwise_labels=['ぜんぜんすわない人','ときどきすう人','たくさんすう人','すこしすう人'])]

def expected_data(kind,unit,option=None):
    if kind=='scale_comparison_bars':
        return dict(coordinate_status='exact_values_explicit_in_adjacent_source_passage',values=[10,11,12,13],axes=[dict(minimum=0,maximum=14,tick=2),dict(minimum=9,maximum=14,tick=1)],bar_fill='black',point_labels='none_in_source')
    if kind=='conversation_opinion_lines':
        return dict(coordinate_status='literal_printed_one_decimal_values_no_normalization',series=[dict(label=n,marker=m,line=l,values=v)for n,m,l,v in zip('ABCD',['filled_diamond','filled_square','filled_triangle','filled_circle'],['solid','dashdot','dashed','dotted'],OPINION_VALUES)],age_groups=['16–19歳','20–29歳','30–39歳','40–49歳','50–59歳','60歳以上'],axis=dict(minimum=0,maximum=45,tick=5,unit='%'),outer_frame=unit=='N1_2005',legend_markers=unit=='N1_2005')
    if kind=='education_goal_bars':
        return dict(coordinate_status='literal_printed_integers_with_approximate_pixel_traced_segment_geometry',years=[1982,1992,2002],values=copy.deepcopy(EDUCATION_VALUES),category_rows=[['高校','専門学校、各種学校','短大、高専','大学・大学院','まだ決めていない','わからない、無回答']]+[['高校','専門学校、各種学校','短大、高専','大学','大学院','まだ決めていない','わからない、無回答']]*2,trace_witness=dict(image_sha256='4a470bac7bd9260d917ebbc5304166c2a07c8662fe34e0deca710c0a22e36d93',boundaries=copy.deepcopy(EDUCATION_BREAKS)),normalization='none_printed_row_totals_100_101_101_preserved',patterns=['black','horizontal lines','dots','north west lines','white','black'],printed_percent_symbols='first_four_values_of_1982_only')
    if kind=='phone_reading_bars':
        return dict(coordinate_status='approximate_pixel_trace_no_numeric_segment_labels',groups=['全体','「本を１冊も読まない」','読書量１～３冊','４～６冊','７～９冊','10冊以上'],categories=['持たない者','持つ者'],legend_fills=['white','black'],bar_order=['持つ者','持たない者'],axis=dict(minimum=0,maximum=100,tick=10,unit='%'),trace_witness=dict(image_sha256='d183478f705d40ff774c187856b1155dd17152e4aa37e1273a66e39f9a10a508',axis=[505,1566],boundaries=[1301,1355,1226,1189,957,1042]))
    if type(option)is not int or not 1<=option<=4:raise ValueError('Four exact option identities are required')
    if kind=='employment_intent_option':
        return dict(option=option,coordinate_status='approximate_pixel_trace_no_invented_segment_value_labels',rows=['男性就職前','男性就職後半年','女性就職前','女性就職後半年'],categories=['定年派','転職派','その他'],patterns=['north west lines','black','dots'],axis=dict(minimum=0,maximum=100,tick=10,unit='%'),trace_witness=copy.deepcopy(EMPLOYMENT_TRACES[option-1]),ruby_profile=unit)
    if kind=='score_distribution_option':
        return dict(option=option,coordinate_status='bar_heights_aligned_with_printed_axis_ticks',values=SCORE_VALUES[option-1],categories=list('ABCD'),axis=dict(minimum=0,maximum=20,tick=5,unit='人'),bar_fill='black',point_labels='none_in_source')
    if kind=='smoking_distribution_option':
        return dict(option=option,coordinate_status='approximate_pixel_traced_rays_no_numeric_sector_labels',trace_witness=copy.deepcopy(SMOKING_TRACES[option-1]),reference_marks='eight_observed_circumference_marks',fill='white')
    raise ValueError('Unknown inspected earlier chart')

def validate(art):
    k=art['kind'];s=art['source'];identity=(art['unit'],art['item_id'],s['physical_page'],s['source_sha256'])
    if k not in IDENTITIES or identity not in IDENTITIES[k]:raise ValueError('Earlier chart requires exact inspected owner/item/page/source')
    d=art['data']
    if d!=expected_data(k,art['unit'],d.get('option')):raise ValueError('Source labels, values, geometry, precision or option identity changed')
    if k=='employment_intent_option'and art['unit']=='N1_2002'and s['physical_page']!=(338 if d['option']==1 else 339):raise ValueError('N1 option physical page mismatch')
    return d

def scale_tex(art):
    d=validate(art);g=Drawing(1176,222,21)
    for p,axis in enumerate(d['axes']):
        ox=p*596;left,top,width,height=ox+60,18,500,180
        g.rect(ox+4,4,574,212,'line width=.6pt')
        g.path([(left,top),(left,top+height),(left+width,top+height)],'line width=.7pt')
        for v in range(axis['minimum'],15,axis['tick']):
            y=top+height*(14-v)/(14-axis['minimum']);g.node(left-9,y,str(v),'anchor=east')
        for i,v in enumerate(d['values']):
            h=height*(v-axis['minimum'])/(14-axis['minimum']);g.rect(left+20+i*120,top+height-h,72,h,'fill=black')
    return g.finish()

def opinion_tex(art):
    d=validate(art);g=Drawing(780,570,18)
    if d['outer_frame']:g.rect(2,2,776,566,'line width=.5pt')
    left,top,width,height=145,65,610,450
    g.rect(left,top,width,height,'line width=.5pt')
    for v in range(0,46,5):
        y=top+height*(45-v)/45;g.path([(left,y),(left+width,y)],'line width=.4pt');g.node(left-10,y,str(v)+r'\%','anchor=east')
    xs=[195,298,401,504,607,710]
    for x,label in zip(xs,d['age_groups']):g.node(x,545,text_tex(label),r'font=\rmfamily\mcfamily\fontsize{17}{20}\selectfont')
    g.rect(8,18,94,132,'line width=.5pt')
    all_points=[]
    for i,s in enumerate(d['series']):
        pts=[(x,top+height*(45-float(v))/45)for x,v in zip(xs,s['values'])];all_points.append(pts)
        g.path(pts,PATTERNS[s['line']]);yy=36+i*32;g.path([(18,yy),(72,yy)],PATTERNS[s['line']])
        if d['legend_markers']:g.marker(45,yy,s['marker'],3.5)
        g.node(89,yy,s['label'])
    offsets=[[(0,22),(0,-22),(0,-22),(0,23),(0,-22),(0,-22)],[(28,0),(12,-22),(16,23),(0,-22),(0,23),(0,-22)],[(26,12),(24,14),(-4,28),(22,18),(0,-22),(0,-22)],[(-4,30),(12,25),(18,-24),(0,-22),(0,24),(0,24)]]
    for i,(s,pts)in enumerate(zip(d['series'],all_points)):
        for x,y in pts:g.marker(x,y,s['marker'],4)
        g.node(pts[0][0]-18,pts[0][1],s['label'],'anchor=east')
        for (x,y),v,(dx,dy)in zip(pts,s['values'],offsets[i]):g.node(x+dx,y+dy,v+r'\%',r'fill=white,inner sep=.5pt')
    return g.finish()

def education_tex(art):
    d=validate(art);g=Drawing(1072,605,29)
    for row,(year,values,bounds,y)in enumerate(zip(d['years'],d['values'],d['trace_witness']['boundaries'],[230,382,534])):
        g.node(145,y,str(year)+'年','anchor=east')
        for i,(a,b,value)in enumerate(zip(bounds,bounds[1:],values)):
            pattern= ['black','horizontal lines','dots','north west lines'] [i]if i<4 else('black'if i==len(values)-1 else'white')
            opts='fill='+('black'if pattern=='black'else'white')
            if pattern not in ['black','white']:opts+=',pattern='+pattern+',pattern color=black'
            g.rect(a,y-29,b-a,58,opts)
            label=str(value)+(r'\%'if row==0 and i<4 else'')
            if i==len(values)-1 and row>0:g.node((a+b)/2,y+49,label)
            else:g.node((a+b)/2,y,label,r'fill=white,inner sep=1pt')
        if row>0:
            for i,title,x,yy in [(3,'大学',745 if row==1 else 700,y-56),(4,'大学院',905 if row==1 else 875,y-56)]:
                mid=(bounds[i]+bounds[i+1])/2;g.path([(x,yy+16),(mid,y-26)],'line width=.6pt');g.node(x,yy,text_tex(title),r'font=\rmfamily\mcfamily\fontsize{25}{29}\selectfont')
    titles=[(274,167,'高校'),(446,145,r'\shortstack{専門学校、\\各種学校}'),(562,145,r'\shortstack{短大、\\高専}'),(732,145,r'\shortstack{大学・\\大学院}'),(880,145,r'\shortstack{まだ決めて\\いない}'),(946,65,r'\shortstack{わからない、\\無回答}')]
    for i,(x,y,t)in enumerate(titles):
        mid=(EDUCATION_BREAKS[0][i]+EDUCATION_BREAKS[0][i+1])/2
        g.path([(x,y+(24 if i!=0 else 18)),(mid,203)],'line width=.6pt');g.node(x,y,t,r'font=\rmfamily\mcfamily\fontsize{25}{29}\selectfont')
    return g.finish()

def phone_tex(art):
    d=validate(art);g=Drawing(900,395,16)
    left,top,width,height=230,14,486,339
    g.rect(left,top,width,height,'line width=.5pt')
    for v in range(0,101,10):
        x=left+width*v/100
        if 0<v<100:g.path([(x,top),(x,top+height)],'dash pattern=on 3pt off 3pt,line width=.5pt')
        g.node(x,375,str(v)+r'\%',r'font=\rmfamily\fontsize{15}{18}\selectfont')
    t=d['trace_witness'];start,end=t['axis']
    for label,edge,y in zip(d['groups'],t['boundaries'],[43,100,157,214,271,328]):
        g.node(left-12,y,text_tex(label),'anchor=east');w=width*(edge-start)/(end-start)
        g.rect(left,y-11,width,22,'fill=white');g.rect(left,y-11,w,22,'fill=black')
    g.rect(740,151,150,76,'line width=.5pt')
    for label,fill,y in zip(d['categories'],d['legend_fills'],[173,205]):
        g.rect(752,y-8,16,16,'fill='+fill);g.node(777,y,text_tex(label),'anchor=west')
    return g.finish()

def employment_tex(art):
    d=validate(art);g=Drawing(800,310,17);g.rect(2,2,796,306,'line width=.5pt')
    left,top,width,height=157,25,470,218
    g.rect(left,top,width,height,'line width=.5pt')
    for v in range(0,101,10):
        x=left+width*v/100
        if 0<v<100:g.path([(x,top),(x,top+height)],'line width=.4pt')
        g.node(x,263,str(v)+r'\%',r'font=\rmfamily\fontsize{16}{19}\selectfont')
    t=d['trace_witness'];start,end=t['axis']
    for i,(label,bs,y)in enumerate(zip(d['rows'],t['breaks'],[68,106,163,201])):
        text='男性'+r'\ruby{就職}{しゅうしょく}'+'前'if i==0 and art['unit']=='N2_2002'else text_tex(label)
        g.node(145,y,text,r'anchor=east,font=\rmfamily\mcfamily\fontsize{15.5}{19}\selectfont')
        bounds=[left]+[left+width*(v-start)/(end-start)for v in bs]+[left+width]
        for a,b,pattern in zip(bounds,bounds[1:],d['patterns']):
            opts='fill='+('black'if pattern=='black'else'white')
            if pattern!='black':opts+=',pattern='+pattern+',pattern color=black'
            g.rect(a,y-11,b-a,22,opts)
    g.rect(642,81,145,116,'line width=.5pt')
    for i,(label,pattern,y)in enumerate(zip(d['categories'],d['patterns'],[104,140,176])):
        opts='fill='+('black'if pattern=='black'else'white')
        if pattern!='black':opts+=',pattern='+pattern+',pattern color=black'
        g.rect(656,y-8,16,16,opts)
        if art['unit']=='N2_2002'and i<2:label=r'\ruby{'+label+'}{'+['ていねんは','てんしょくは'][i]+'}'
        g.node(682,y,label,'anchor=west')
    return g.finish()

def score_tex(art):
    d=validate(art);g=Drawing(180,190,13);g.rect(2,3,176,183,'line width=.7pt')
    left,top,width,height=27,30,142,133
    g.path([(left,top-7),(left,top+height),(left+width,top+height)])
    g.node(17,16,'人')
    for v in range(0,21,5):g.node(left-5,top+height*(20-v)/20,str(v),'anchor=east')
    for i,(v,label)in enumerate(zip(d['values'],d['categories'])):
        x=43+i*33;h=height*v/20;g.rect(x-8,top+height-h,17,h,'fill=black');g.node(x,177,label)
    return g.finish()

def smoking_tex(art):
    d=validate(art);g=Drawing(180,190,11);g.rect(2,3,176,183,'line width=.7pt')
    cx,cy,r=92,95,69;trace=d['trace_witness'];sx,sy=trace['center']
    g.lines.append(rf'\draw({cx},{cy})circle[radius={r}pt];')
    for x,y in trace['rays']:
        angle=math.atan2(y-sy,x-sx);g.path([(cx,cy),(cx+r*math.cos(angle),cy+r*math.sin(angle))])
    for i in range(8):
        a=i*math.pi/4;g.lines.append(rf'\fill({cx+73*math.cos(a):.3f},{cy+73*math.sin(a):.3f})circle[radius=.7pt];')
    positions=[[[124,83],[72,127],[31,75],[70,47]],[[125,95],[60,124],[55,72],[29,21]],[[126,97],[66,134],[58,88],[34,21]],[[125,97],[61,125],[31,76],[71,47]]][d['option']-1]
    splits={'ぜんぜんすわない人':r'ぜんぜん\\すわない人','たくさんすう人':r'たくさん\\すう人','ときどきすう人':r'ときどき\\すう人','すこしすう人':r'すこし\\すう人'}
    for (x,y),label in zip(positions,trace['clockwise_labels']):g.node(x,y,r'\shortstack{'+splits[label]+'}',r'fill=white,inner sep=.2pt')
    if d['option']in [2,3]:g.path([(55,21),(75,21),(75,39)],'line width=.6pt')
    return g.finish()

def tex(art):
    return {'scale_comparison_bars':scale_tex,'conversation_opinion_lines':opinion_tex,'education_goal_bars':education_tex,'phone_reading_bars':phone_tex,'employment_intent_option':employment_tex,'score_distribution_option':score_tex,'smoking_distribution_option':smoking_tex}[art['kind']](art)
