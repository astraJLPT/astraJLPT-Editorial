"""Hash-bound glyph and illustration roles; asset bytes are never transformed."""
import base64
import hashlib
from bs4 import BeautifulSoup
from model import iter_fields

def configure(document,styles):
    hashes=set()
    for f in iter_fields(document):
        value=f['value']
        if not isinstance(value,dict):continue
        for image in BeautifulSoup(value['html'],'html.parser').find_all('img'):
            src=image.get('src','')
            if src.startswith('data:image/'):
                hashes.add(hashlib.sha256(base64.b64decode(src.split(',',1)[1])).hexdigest())
    if not isinstance(styles,dict) or set(styles)-hashes:raise ValueError('Unknown or stale embedded image selector')
    for style in styles.values():
        role=style.get('role')
        allowed={'role','basis','height_em','raise_em'} if role=='glyph' else {'role','basis','width_fraction'}
        if role not in ['glyph','illustration'] or set(style)-allowed or not style.get('basis'):
            raise ValueError('Invalid embedded image role/control')
        if any(type(value) not in [int,float] for key,value in style.items() if key in ['height_em','raise_em','width_fraction']):
            raise ValueError('Image dimensions must be numbers, not booleans')
        if role=='glyph':
            if not .5<=style.get('height_em',0)<=2.5 or not -.5<=style.get('raise_em',0)<=.5:raise ValueError('Invalid glyph dimensions')
        elif not .1<=style.get('width_fraction',0)<=1:raise ValueError('Invalid illustration width')
    return styles

def render(path,style):
    if style['role']=='glyph':
        return r'\raisebox{'+str(style.get('raise_em',0))+r'em}{\includegraphics[height='+str(style['height_em'])+'em]{'+path.as_posix()+'}}'
    return r'\par\addvspace{8pt}\noindent\includegraphics[width='+str(style['width_fraction'])+r'\linewidth]{'+path.as_posix()+r'}\par\addvspace{8pt}'
