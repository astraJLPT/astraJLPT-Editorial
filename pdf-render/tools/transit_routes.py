"""Native presentation of an explicitly selected semantic transport-route table."""
import copy
from bs4 import NavigableString, Tag
from model import Projection


def render(conv, rows, grid, ncols, presentation):
    allowed = {'cell_flow', 'column_weights', 'body_pt', 'baseline_pt', 'before_pt', 'after_pt', 'approved_duration'}
    if set(presentation) - allowed:
        raise ValueError('Transit routes cannot silently ignore other table styles')
    if ncols != 5 or not rows or len(rows) % 2:
        raise ValueError('Transit routes require paired heading/five-cell rows')
    weights = presentation.get('column_weights', [22, 17, 24, 17, 20])
    if len(weights) != 5 or any(isinstance(w, bool) or not isinstance(w, (int, float)) or w <= 0 for w in weights):
        raise ValueError('Invalid transit route widths')
    total = sum(weights)
    widths = [w / total for w in weights]
    starts = [sum(widths[:c]) for c in range(5)]
    centers = [starts[c] + widths[c] / 2 for c in range(5)]

    def body(cell):
        return ''.join(conv.node(n, 'cell') for n in cell.children).replace(r'\Para ', r'\par ')

    def leg(cell):
        cell = copy.deepcopy(cell)
        children = [n for n in cell.children if not isinstance(n, NavigableString) or n.strip()]
        if (len(cell.find_all('br')) != 1 or not isinstance(children[0], NavigableString)
                or not isinstance(children[-1], NavigableString)
                or not str(children[0]).lstrip().startswith('→')
                or not str(children[-1]).rstrip().endswith('→')
                or Projection({'html':str(cell)}).text.count('→') != 2):
            raise ValueError('Transit leg requires exactly two endpoint arrows and one line break')
        children[0].replace_with(str(children[0]).lstrip()[1:].lstrip())
        children[-1].replace_with(str(children[-1]).rstrip()[:-1].rstrip())
        chunks = [[], []]
        index = 0
        for node in cell.children:
            if isinstance(node, Tag) and node.name == 'br':
                index += 1
            else:
                chunks[index].append(node)
        if any(not Projection({'html':''.join(map(str, chunk))}).text.strip() for chunk in chunks):
            raise ValueError('Transit leg is missing its mode or duration')
        result = [''.join(conv.node(n, 'cell') for n in chunks[0])]
        if presentation.get('approved_duration') == 'D19':
            from workbook_duration import tex
            result.append(tex(conv, ''.join(map(str, chunks[1]))))
        else:
            result.append(''.join(conv.node(n, 'cell') for n in chunks[1]))
        return result

    pieces = []
    for r in range(0, len(rows), 2):
        header = grid.get((r, 0))
        if (header is None or header[1:] != (1, 5) or header[0].name != 'th'
                or any(grid.get((r, c)) is not None for c in range(1, 5))):
            raise ValueError('Transit route heading must span all five columns')
        cells = []
        for c in range(5):
            entry = grid.get((r + 1, c))
            if entry is None or entry[1:] != (1, 1) or entry[0].name != 'td':
                raise ValueError('Transit route body must have five ordinary cells')
            cells.append(entry[0])
        diagram = [r'\begin{tikzpicture}']
        for c in [1, 3]:
            mode, duration = leg(cells[c])
            diagram.append(r'\draw[line width=3.5pt,black!55] (' + str(starts[c]) + r'\linewidth,0pt) -- (' + str(starts[c]+widths[c]) + r'\linewidth,0pt);')
            for text, y in [(mode, 17), (duration, -17)]:
                diagram.append(r'\node[inner sep=0pt,align=center] at (' + str(centers[c]) + r'\linewidth,' + str(y) + 'pt) {' + text + '};')
        for c in [0, 2, 4]:
            if '→' in Projection({'html':str(cells[c])}).text:
                raise ValueError('Transit station cannot contain a connector arrow')
            diagram.append(r'\node[draw=black!55,line width=.45pt,fill=black!18,minimum height=67pt,inner sep=4pt,align=center,text width=\dimexpr ' + str(widths[c]) + r'\linewidth-8pt\relax] at (' + str(centers[c]) + r'\linewidth,0pt) {' + body(cells[c]) + '};')
        diagram.append(r'\end{tikzpicture}')
        pieces.append(r'\par\noindent\begin{minipage}{\linewidth}\noindent\begin{tikzpicture}\draw[dash pattern=on 3pt off 3pt,line width=.65pt] (.325pt,0) -- (\dimexpr\linewidth-.325pt\relax,0);\end{tikzpicture}\par\vspace{9pt}\noindent ' + body(header[0]) + r'\par\vspace{5pt}\noindent ' + ''.join(diagram) + r'\end{minipage}\par')
    conv.features.append({'kind':'transit_routes', 'semantic_rows':len(rows), 'semantic_columns':5,
        'routes':len(rows)//2, 'station_boxes':len(rows)//2*3,
        'canonical_endpoint_arrows_presented_as_native_connections':len(rows)//2*4})
    size = presentation.get('body_pt', 11.25)
    baseline = presentation.get('baseline_pt', 20)
    return (r'\Para {\fontsize{' + str(size) + '}{' + str(baseline) + r'}\selectfont\vspace{'
            + str(presentation.get('before_pt', 4)) + 'pt}'
            + r'\vspace{10pt}'.join(pieces) + r'\par\vspace{'
            + str(presentation.get('after_pt', 0)) + r'pt}}\Para ')
