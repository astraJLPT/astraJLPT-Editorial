"""Native vector charts from explicit semantic data; no source-image crops."""
from decimal import Decimal,InvalidOperation
import math

def pies(node,conv):
    if not getattr(conv,'source_target_markers',False):raise ValueError('Historical chart outside historical edition')
    if node.get('data-native-chart')!='historical-2009-pies':raise ValueError('Unknown historical chart kind')
    rows=node.find_all('tr')
    expected=['グラフ','基礎研究費','応用研究費','開発研究費']
    if len(rows)!=5 or [c.get_text(strip=True) for c in rows[0].find_all(['th','td'],recursive=False)]!=expected:raise ValueError('Invalid pie chart headers/row count')
    parsed=[]
    for label,row in zip('アイウエ',rows[1:]):
        cells=row.find_all(['th','td'],recursive=False)
        if len(cells)!=4 or cells[0].get_text(strip=True)!=label:raise ValueError('Invalid pie label/order')
        texts=[c.get_text(strip=True) for c in cells[1:]]
        if any(not t.endswith('%') for t in texts):raise ValueError('Pie values require explicit percent units')
        try:values=[Decimal(t[:-1]) for t in texts]
        except InvalidOperation:raise ValueError('Invalid percentage')
        if any(not x.is_finite() or not 0<x<100 for x in values) or sum(values)!=100:raise ValueError('Pie values must be positive and total exactly 100')
        parsed.append((label,texts,values))
    out=[r'\par\addvspace{10pt}\noindent\begin{minipage}{\linewidth}\centering',r'{\bfseries グラフ}\par\vspace{6pt}']
    for n,(label,texts,values) in enumerate(parsed):
        out.append(r'\begin{minipage}{.47\linewidth}\centering{\bfseries '+label+r'}\par\vspace{3pt}\begin{tikzpicture}[x=1cm,y=1cm]')
        out.append(r'\path[use as bounding box] (-2.15,-2.05) rectangle (2.15,2.05);')
        start=90.0
        for j,(text,value) in enumerate(zip(texts,values)):
            end=start-float(value)*3.6
            fill=['fill=black','fill=white,pattern=dots,pattern color=black','fill=white'][j]
            out.append(f'\\filldraw[{fill},draw=black,line width=.35pt] (0,0) -- ({start:.5f}:1.5) arc[start angle={start:.5f},end angle={end:.5f},radius=1.5] -- cycle;')
            mid=(start+end)/2;small=value<10
            # Keep long horizontal labels clear of the circle while leaving
            # narrower sectors enough room on either side of their bisector.
            radius=1.88 if small else (.90 if abs(math.cos(math.radians(mid)))>.90 else 1.07)
            if small:out.append(f'\\draw[line width=.35pt] ({mid:.5f}:1.4) -- ({mid:.5f}:1.66);')
            color='white' if j==0 and not small else 'black'
            label_clearance=',fill=white,inner sep=.6pt' if j==1 else ''
            out.append(f'\\node[text={color}{label_clearance},font=\\fontsize{{9.5}}{{12}}\\selectfont] at ({mid:.5f}:{radius})'+'{'+conv.text(text)+'};')
            start=end
        out.append(r'\end{tikzpicture}\end{minipage}')
        out.append(r'\hfill' if n%2==0 else r'\par\vspace{7pt}')
    out.append(r'{\fontsize{9.5}{14}\selectfont')
    for j,label in enumerate(expected[1:]):
        fill=['fill=black','fill=white,pattern=dots,pattern color=black','fill=white'][j]
        out.append(r'\tikz[baseline=-.5pt]{\filldraw['+fill+r',draw=black,line width=.35pt](0,0)rectangle(10pt,7pt);}\hspace{.35em}'+conv.text(label)+(r'\hspace{1em}' if j<2 else ''))
    out.append(r'\par}\end{minipage}\par\addvspace{10pt}')
    conv.features.append({'kind':'historical_four_pies','labels':list('アイウエ'),'series':expected[1:],'values':[[str(x) for x in row[2]] for row in parsed],
      'native_vectors':True,'layout':'two_by_two_below_passage','fills':['black','dots','white'],
      'basis':'canonical repaired percentages; H17-STYLE-002 below-passage placement; source category fills reviewed H27 S09-F01'})
    return '\n'.join(out)
