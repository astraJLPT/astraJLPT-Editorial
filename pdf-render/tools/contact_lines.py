"""Bound contact groups with native gaps; accepted digits and ruby remain exact."""
import re
from model import Projection
from notice_layout import html_lines


def render(conv, raw, binding):
    lines=html_lines(raw)
    if len(lines)!=2:raise ValueError('Grouped contact requires office and terminal contact lines')
    projection=Projection({'html':lines[-1]})
    groups=binding['segments']
    roles=[g['role']for g in groups]
    if roles!=['postal','address','telephone','hours']:raise ValueError('Invalid contact segment roles')
    fixed=all('width_bp'in g for g in groups)
    if any('width_bp'in g for g in groups)and not fixed:raise ValueError('Fixed contact columns require all four widths')
    pattern=r'\s*'+r'\s*'.join('('+re.escape(g['text'])+')' for g in groups)+r'\s*'
    match=re.fullmatch(pattern,projection.text)
    if not match:raise ValueError('Contact segments must cover exact existing contact values')
    rendered=[]
    for index,group in enumerate(groups,1):
        a,b=match.span(index)
        if any(r['start']<a<r['end'] or r['start']<b<r['end']for r in projection.ruby):raise ValueError('Contact segment splits ruby')
        ra,rb=projection.mapping[a][0],projection.mapping[b-1][1]
        for ruby in projection.ruby:
            if ruby['start']==a:ra=projection.raw.rfind('<ruby',0,ra+1)
            if ruby['end']==b:rb=projection.raw.find('</ruby>',rb)+7
        fragment={'html':projection.raw[ra:rb]}
        if Projection(fragment).text!=group['text']:raise ValueError('Contact segment crosses markup')
        gap=group.get('gap_before_em',0)
        if isinstance(gap,bool)or not isinstance(gap,(int,float))or not 0<=gap<=2:raise ValueError('Invalid contact group gap')
        body=conv.value(fragment,'notice')
        if 'ascii_letterspace' in group:
            tracking=group['ascii_letterspace']
            if isinstance(tracking,bool)or not isinstance(tracking,(int,float))or not 0<=tracking<=20:
                raise ValueError('Invalid source-bound contact ASCII tracking')
            body=r'{\addfontfeatures{LetterSpace='+str(tracking)+r'}'+body+'}'
        if fixed:
            width=group['width_bp']
            if isinstance(width,bool)or not isinstance(width,(int,float))or not 20<=width<=150 or gap:
                raise ValueError('Invalid fixed contact segment width or conflicting gap')
            body=(r'{\sbox0{'+body+r'}\ifdim\wd0>'+str(width)+r'bp\PackageError{JLPT}{Contact field exceeds its bound column}{Check the native field and source geometry.}\fi\makebox['+str(width)+r'bp][l]{\usebox0}}')
        else:body=r'\mbox{'+body+'}'
        rendered.append((r'\hspace{'+str(gap)+'em}'if index>1 else'')+body)
    office=conv.value({'html':lines[0]},'notice')
    gap=binding['office_after_pt']
    if not 0<=gap<=24:raise ValueError('Invalid office/contact clearance')
    conv.features.append({'kind':'segmented_contact','segments':groups,'office_after_pt':gap})
    return office+r'\par\nobreak\vspace{'+str(gap)+r'pt}\noindent '+''.join(rendered)
