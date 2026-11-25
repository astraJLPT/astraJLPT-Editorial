"""Source-bound 1992 sleep charts; printed values are never normalized."""
from richtex import text_tex

SOURCE='8560bf8ef92b4e2d58559b3e14882b76d3307586f5d55b0e7fa33cc2f5fa931f'
SOURCES={'N1_1992':('reading-b004',81,SOURCE),
         'N2_1992':('reading-b007',80,'0a6634758dce0a258ffaf92c6c8ea1a738a4b8ceb52cd75cb44a4d8d340dfa64')}

def data(unit='N1_1992'):
    if unit not in SOURCES:raise ValueError('Unreviewed sleep-chart owner')
    result=dict(title='「すいみん」時間量分布の変化（平日）',
        categories=['6時間以下','6～7時間','7～8時間','8～9時間','9時間以上'],
        rows=[dict(year='’70年',values=[7,18,35,25,15]),dict(year='’75年',values=[7,20,35,25,13]),
              dict(year='’80年',values=[8,21,35,24,13]),dict(year='’85年',values=[10,24,35,21,11]),dict(year='’90年',values=[12,25,32,20,12])],
        percent_sign='first_row_first_cell_only',boundary_connectors='dotted',category_arrows=True,
        geometry='approximate_source_pixel_trace_with_regularized_horizontal_bars_not_recalculated_percentages',
        source_crop_boundaries=[[69,91,150,263,344,392],[69,92,156,269,351,392],[69,94,163,276,351,392],[69,102,181,293,357,392],[69,110,191,294,355,392]],
        printed_totals=[100,100,101,101,101],label_policy='all25printed_values_unchanged')
    if unit=='N2_1992':
        result['source_crop_boundaries']=[[70,94,152,263,343,393],[70,95,159,270,350,393],[70,98,165,276,350,393],[70,104,182,294,358,393],[70,109,191,294,353,393]]
    return result

def validate(art):
    identity=(art['unit'],art['item_id'],art['source']['physical_page'],art['source']['source_sha256'])
    unit=art['unit']
    if art.get('kind')!='sleep_distribution_bars' or unit not in SOURCES or identity!=(unit,*SOURCES[unit]):
        raise ValueError('Sleep chart requires exact reviewed source/owner/passage')
    if art.get('data')!=data(unit):
        raise ValueError('Sleep chart labels, values, order or source geometry changed')
    return art['data']

def tex(art):
    d=validate(art)
    level2=art['unit']=='N2_1992'
    out=[r'\begin{tikzpicture}[x=1pt,y=-1pt,line width=.55pt,every node/.style={inner sep=0pt,font=\rmfamily\mcfamily\fontsize{13}{15}\selectfont}]',
         r'\path[use as bounding box](0,0)rectangle(405,250);'if level2 else r'\path[use as bounding box](0,0)rectangle(406,238);']
    def node(x,y,value,style=''):
        out.append(r'\node['+style+f']at({x:.3f},{y:.3f})'+'{'+value+'};')
    def line(x1,y1,x2,y2,style=''):
        out.append(r'\draw['+style+f']({x1:.3f},{y1:.3f})--({x2:.3f},{y2:.3f});')
    # The original crops use a more prominent title and category labels than
    # the former reconstruction. These sizes accompany the source-width chart.
    title_size='15' if level2 else '16.5'
    node(235 if level2 else 225,14,text_tex(d['title']),r'font=\rmfamily\mcfamily\bfseries\fontsize{'+title_size+r'}{18}\selectfont')
    xs=[62,128,204,298,368]if level2 else[62,124,205,298,368];arrows=[82,122,208,303,368]if level2 else[80,121,207,303,367]
    for x,ax,label in zip(xs,arrows,d['categories']):
        node(x,60 if level2 else 50,text_tex(label),r'font=\rmfamily\mcfamily\bfseries\fontsize{10.5}{12}\selectfont')
        line(ax,70 if level2 else 61,ax,80 if level2 else 71,'-latex,line width=.45pt')
    ys=[85,118,150,183,216]if level2 else[76,109,141,174,207];height=26 if level2 else 24
    for j,(row,bounds,y)in enumerate(zip(d['rows'],d['source_crop_boundaries'],ys)):
        # U+2019 abbreviates a year here. Keep the same character in the Latin
        # font, avoiding the full Japanese punctuation cell before its digits.
        year=r'{\ltjalchar"2019\relax '+row['year'][1:3]+'}'+text_tex(row['year'][3:])
        node(55,y+12,year,r'anchor=east,font=\rmfamily\mcfamily\fontsize{18}{20}\selectfont')
        out.append(r'\draw'+f'({bounds[0]},{y})rectangle({bounds[-1]},{y+height});')
        for x in bounds[1:-1]:line(x,y,x,y+height)
        for k,(lo,hi,value)in enumerate(zip(bounds,bounds[1:],row['values'])):
            node((lo+hi)/2,y+12,str(value)+(r'\%'if(j,k)==(0,0)else''))
        if j<4:
            for x,nx in zip(bounds[1:-1],d['source_crop_boundaries'][j+1][1:-1]):
                line(x,y+height,nx,ys[j+1],'densely dotted,line width=.4pt')
    out.append(r'\end{tikzpicture}')
    return '\n'.join(out)
