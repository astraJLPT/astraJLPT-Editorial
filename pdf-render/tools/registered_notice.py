"""Optional page-bound frame with normal native text flow inside it."""
import math


def render(content, style):
    f=style['page_frame']
    if set(f)!={'x_bp','y_bp','width_bp','height_bp','rule_bp','page_bottom_bp'}:
        raise ValueError('Unknown registered notice frame property')
    if any(isinstance(v,bool)or not isinstance(v,(int,float))or not math.isfinite(v)for v in f.values()):
        raise ValueError('Invalid registered notice dimensions')
    x,y,w,h,rule=(f[k]for k in ['x_bp','y_bp','width_bp','height_bp','rule_bp'])
    if not (0<=x and 0<=y and 200<=w and 100<=h and x+w<=595.28 and y+h<=841.89 and .2<=rule<=1.5 and 20<=f['page_bottom_bp']<=100):
        raise ValueError('Registered notice frame exceeds A4 page')
    pad=style['frame_padding_pt'];top=style.get('frame_top_pt',pad);bottom=style.get('frame_bottom_pt',pad)
    inner_w=w-2*rule-2*pad*72/72.27
    inner_h=h-2*rule
    if inner_w<=0 or top+bottom>=inner_h:raise ValueError('Invalid registered notice padding')
    fmt=lambda v:format(v,'.6f').rstrip('0').rstrip('.')
    measure=(r'\setbox\MeasuredNoticeBox=\vbox{\hsize='+fmt(inner_w)+r'bp\linewidth=\hsize\textwidth=\hsize '+content+r'\par}'
             r'\typeout{Registered notice content height: \the\dimexpr\ht\MeasuredNoticeBox+\dp\MeasuredNoticeBox\relax}'
             r'\ifdim\dimexpr\ht\MeasuredNoticeBox+\dp\MeasuredNoticeBox+'+str(top+bottom)+r'pt\relax>'+fmt(inner_h)+r'bp '
             r'\PackageError{JLPT}{Registered notice exceeds its fixed frame}{Reduce only source-supported gaps or correct the bound dimensions.}\fi ')
    box=(r'\setlength\fboxsep{0pt}\setlength\fboxrule{'+fmt(rule)+r'bp}'
         r'\fbox{\vbox to '+fmt(inner_h)+r'bp{\vskip '+str(top)+r'pt\hbox{\hskip '+str(pad)+r'pt\box\MeasuredNoticeBox\hskip '+str(pad)+r'pt}\vfil}}')
    return (r'\begingroup'+measure+r'\global\setbox\RegisteredNoticeFrame=\hbox{'+box+'}'
            r'\AddToHookNext{shipout/foreground}{\put(0,0){\kern '+fmt(x)+r'bp\raisebox{-'+fmt(y+h)+r'bp}[0pt][0pt]{\raisebox{\depth}{\copy\RegisteredNoticeFrame}}}}'
            r'\mbox{}\par\endgroup')
