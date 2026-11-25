"""Exact H26 source-label restoration; original raster and geometry are retained."""
from PIL import Image


def expected(art):
    key=(art['unit'],art['item_id'],art['source']['physical_page'])
    sha={'N1_1998':'8560bf8ef92b4e2d58559b3e14882b76d3307586f5d55b0e7fa33cc2f5fa931f',
         'N2_1998':'0a6634758dce0a258ffaf92c6c8ea1a738a4b8ceb52cd75cb44a4d8d340dfa64',
         'N1_1997':'8560bf8ef92b4e2d58559b3e14882b76d3307586f5d55b0e7fa33cc2f5fa931f',
         'N1_2008':'e3555741c8f14b855a32e7d09b42eb790492e3818a85a875f99d84703c752e00'}
    if art['source']['source_sha256']!=sha.get(art['unit']):raise ValueError('Stale label restoration source')
    if key==('N1_1998','reading-b007',368):
        return dict(canvas=[781,530],labels=[
            dict(text='大阪50キロ圏',ruby=['大阪','おおさか'],mask=[262,467,373,500],anchor=[266,494],font_pt=18),
            dict(text='名古屋50キロ圏',ruby=['名古屋','なごや'],mask=[413,480,538,501],ruby_mask=[413,468,468,480],anchor=[414,494],font_pt=18),
            dict(text='東京50キロ圏',mask=[615,478,728,501],anchor=[617,494],font_pt=18)],
            preserved='All source map contours, three area symbols, leader lines and unchanged native pies/title/legend')
    if key==('N2_1998','reading-b007',342):
        return dict(canvas=[781,530],labels=[
            dict(text='大阪50キロ圏',ruby=['大阪','おおさか'],mask=[260,466,371,499],anchor=[263,493],font_pt=18),
            dict(text='名古屋50キロ圏',ruby=['名古屋','なごや'],mask=[408,477,536,499],ruby_mask=[408,466,468,477],anchor=[410,493],font_pt=18),
            dict(text='東京50キロ圏',mask=[612,474,721,499],anchor=[614,493],font_pt=18)],
            preserved='All map contours, symbols, leader lines and the existing native pie/legend data')
    if key==('N1_1997','reading-b007',315):
        return dict(canvas=[476,163],labels=[dict(text='虹のたもと',mask=[3,105,105,129],anchor=[6,126],font_pt=20)],
            preserved='Original rainbow, arrow including its tail, and baseline; no ruby added to the diagram label')
    if key==('N1_2008','reading-b009',108):
        return dict(canvas=[793,1006],labels=[dict(text='14',mask=[578,653,604,678],anchor=[579,675],font_pt=23)],
            preserved='All plotted points, filled-square marker, lines, axes, legend, other labels and image dimensions')
    raise ValueError('Uninspected source label overlay')


def validate(art,asset_path):
    if art.get('data')!=expected(art):raise ValueError('Altered source-label restoration specification')
    with Image.open(asset_path(art['image']))as im:
        if list(im.size)!=art['data']['canvas']:raise ValueError('Label overlay canvas differs from original pixels')
    for label in art['data']['labels']:
        x0,y0,x1,y1=label['mask'];w,h=art['data']['canvas']
        if not 0<=x0<x1<=w or not 0<=y0<y1<=h:raise ValueError('Unsafe label mask')


def labels_tex(art):
    from richtex import text_tex
    h=art['data']['canvas'][1];lines=[]
    for label in art['data']['labels']:
        x0,y0,x1,y1=label['mask'];x,y=label['anchor'];size=label['font_pt']
        lines.append(rf'\fill[white]({x0},{h-y1})rectangle({x1},{h-y0});')
        if 'ruby_mask'in label:
            x0,y0,x1,y1=label['ruby_mask'];lines.append(rf'\fill[white]({x0},{h-y1})rectangle({x1},{h-y0});')
        value=text_tex(label['text'])
        if 'ruby'in label:
            base,reading=label['ruby'];value=r'\ruby{'+text_tex(base)+'}{'+text_tex(reading)+'}'+text_tex(label['text'][len(base):])
        lines.append(rf'\node[anchor=base west,inner sep=0pt,font=\rmfamily\mcfamily\fontsize{{{size}}}{{{size+3}}}\selectfont]at({x},{h-y})'+'{'+value+'};')
    return '\n'.join(lines)


def tex(art,asset_path):
    w,h=art['data']['canvas'];p=asset_path(art['image']).as_posix()
    return (r'\begin{tikzpicture}[x=1pt,y=1pt]'+rf'\path[use as bounding box](0,0)rectangle({w},{h});'
        +r'\node[anchor=south west,inner sep=0pt]at(0,0){\includegraphics[width='+str(w)+'pt,height='+str(h)+'pt]{'+p+'}};'
        +labels_tex(art)+r'\end{tikzpicture}')
