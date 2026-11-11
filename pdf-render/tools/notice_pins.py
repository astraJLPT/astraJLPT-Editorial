"""One native corner-pin family for explicitly authored physical documents."""


def decorate(frame, pins):
    bounds = {'radius_pdf_pt': (2, 8), 'fill_gray': (0, 1), 'inset_pt': (5, 20)}
    if set(pins) != {'shape', *bounds} or pins['shape'] != 'single_circle':
        raise ValueError('Unsupported observed pin shape')
    if any(isinstance(pins[k], bool) or not isinstance(pins[k], (int, float))
           or not low <= pins[k] <= high for k, (low, high) in bounds.items()):
        raise ValueError('Invalid native corner-pin geometry')
    r = pins['radius_pdf_pt']
    k = r*.5522847498
    path = f'{r:g} 0 m {r:g} {k:g} {k:g} {r:g} 0 {r:g} c {-k:g} {r:g} {-r:g} {k:g} {-r:g} 0 c {-r:g} {-k:g} {-k:g} {-r:g} 0 {-r:g} c {k:g} {-r:g} {r:g} {-k:g} {r:g} 0 c'
    return (r'{\renewcommand\NoticePinInset{'+str(pins['inset_pt'])
            +r'pt}\renewcommand\NoticePin{\pdfextension literal{q '
            +str(pins['fill_gray'])+' g 0 G .4 w '+path+r' B Q}}'+frame+'}')
