"""Refresh small interface assets without regenerating paper bodies or fonts."""
from io import BytesIO
from pathlib import Path
import re
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
SITE=ROOT/'astraJLPT'


def install_images(site=SITE):
    original=ROOT/'additional-assets/boar-original.png'
    with Image.open(original) as image:
        if image.width*2!=image.height*3:
            raise ValueError('The boar original must retain its 3:2 aspect ratio')
        footer=image.resize((264,176),Image.Resampling.LANCZOS)
        favicon=Image.new('RGBA',(64,64),(0,0,0,0))
        small=image.resize((60,40),Image.Resampling.LANCZOS).convert('RGBA')
        favicon.alpha_composite(small,(2,12))
    for name,image in [('boar.png',footer),('favicon.png',favicon)]:
        out=BytesIO();image.save(out,format='PNG',optimize=True)
        target=site/'assets'/name
        if not target.exists() or target.read_bytes()!=out.getvalue():target.write_bytes(out.getvalue())


def refresh(site=SITE):
    from catalog_html import card_fallback
    install_images(site)
    changed=0
    for page in site.rglob('*.html'):
        before=page.read_text('utf8')
        markup=re.sub(r'(rel="icon" href="(?:\.\./)*assets/)boar\.png(?:\?v=[0-9a-f]+)?',r'\1favicon.png',before)
        if page==site/'index.html':
            markup=re.sub(r'(<a class="level-card level-n([1-5])"[^>]*><span class="card-art"[^>]*>).*?(</span>)',
                          lambda m:m[1]+card_fallback(int(m[2]))+m[3],markup,flags=re.S)
        if markup!=before:
            page.write_text(markup,encoding='utf8',newline='\n');changed+=1
    return changed


if __name__=='__main__':
    print({'interface_pages_refreshed':refresh()})
