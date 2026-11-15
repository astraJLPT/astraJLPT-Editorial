"""Conservatively trim selected installed WOFF2 fonts without replacing full sources.

Run after complete font generation when content changes. This operation only
removes glyphs from installed web derivatives; it cannot restore absent glyphs.
The default is read-only. --write installs the fully prepared, validated batch.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from io import BytesIO
import argparse,hashlib,html,json,re
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
ROOT=Path(__file__).resolve().parents[2]
SITE=ROOT/'astraJLPT'
TARGETS=tuple(n+'-0.woff2' for n in (
    '05817e8ecde26621','0a314d5e5f29d41a','0bb6f1fb10846713',
    '15157483588f2778','15be144b9a98afb1','1bca3052abd0e355',
    '1fd6d7dddab714f8','209c0865e199cf3b','2fc6ff3c5253dca9',
    '5905a6fb914d6f27','6221621b838198c5','6c4a4b643461def5',
    '766f06ac8761f82f','7edc03446d857c7e','8563d912f7a90640',
    '86e2572e8b691610','959cec1c93044516','9b7ef20fcf763648',
    '9e8a6af516706030','b298a5a5884e87d4','b338caa746daa6ac',
    'bc454d70b8f90662','c8f5180d2b136338','cad552553cf2a75a','cf33366000ee2314'))
# The UI face accepts user input; retain its complete installed character set.
FONT_URL=re.compile(r'fonts/([^"\x27?\s)]+\.woff2)')

def digest(data):return hashlib.sha256(data).hexdigest()

class _Dependencies(HTMLParser):
    def __init__(self,markup):
        super().__init__();self.profiles=[];self.scripts=[];self.feed(markup)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='link' and 'stylesheet' in attrs.get('rel','').split() and attrs.get('href'):
            name=Path(urlsplit(attrs['href']).path).name
            if re.fullmatch(r'fonts(?:-[0-9a-f]+)?\.css',name):self.profiles.append(name)
        if tag=='script' and attrs.get('src'):self.scripts.append(attrs['src'])
    def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs)


def corpora(site,names=TARGETS):
    """Include complete declaring pages, their scripts, CSS and generated symbols."""
    site=Path(site).resolve();names=set(names)
    profiles={p.name:set(FONT_URL.findall(p.read_text('utf-8'))) for p in (site/'assets').glob('fonts*.css')}
    uses={n:[] for n in names};pages={}
    for page in sorted(site.rglob('*.html')):
        text=page.read_text('utf-8');deps=_Dependencies(text)
        active=set().union(*(profiles.get(p,set()) for p in deps.profiles)) & names
        if not active:continue
        for source in deps.scripts:
            url=urlsplit(source)
            if url.scheme or url.netloc:raise ValueError('Expected local script: '+source)
            path=(page.parent/unquote(url.path)).resolve()
            if not path.is_relative_to(site):raise ValueError('Script escapes website')
            text+='\n'+path.read_text('utf-8')
        chars=set(map(ord,text))
        chars.update(map(ord,html.unescape(text)))
        chars.update(int(m[1],16) for m in re.finditer(r'\\u([0-9a-fA-F]{4})',text))
        pages[page.relative_to(site).as_posix()]=chars
        for name in active:uses[name].append(page.relative_to(site).as_posix())
    common=''.join(p.read_text('utf-8') for p in (site/'assets').glob('*.css'))+'0123456789１２３４５６７８９０（）・★例答注'
    shared=set(map(ord,common))
    shared.update(int(m[1],16) for m in re.finditer(r'\\([0-9a-fA-F]{1,6})(?:\s)?',common) if int(m[1],16)<=0x10ffff)
    result={}
    for name,owners in uses.items():
        if not owners:raise ValueError('Font has no declaring pages: '+name)
        chars=shared.copy()
        for page in owners:chars.update(pages[page])
        result[name]={'characters':chars,'pages':owners}
    return result


def verify_subset(original,candidate,characters):
    """Check retained glyph outlines, advances, hint programs and line metrics."""
    with TTFont(BytesIO(original)) as old,TTFont(BytesIO(candidate)) as new:
        a=old.getBestCmap();b=new.getBestCmap();required=set(a)&set(characters)
        if not required<=set(b):raise ValueError('Required glyph coverage lost')
        if any(a[cp]!=glyph for cp,glyph in b.items()):raise ValueError('Character mapping changed')
        glyphs=new.getGlyphOrder()
        if not set(glyphs)<=set(old.getGlyphOrder()):raise ValueError('Unexpected replacement glyph')
        left=old.getGlyphSet();right=new.getGlyphSet()
        for name in glyphs:
            p=RecordingPen();q=RecordingPen();left[name].draw(p);right[name].draw(q)
            if p.value!=q.value:raise ValueError('Glyph outline changed: '+name)
            for table in ('hmtx','vmtx'):
                if table in old and old[table][name]!=new[table][name]:raise ValueError('Glyph advance changed: '+name)
            if 'glyf' in old:
                x=old['glyf'][name];y=new['glyf'][name]
                if (x.program.getBytecode() if hasattr(x,'program') else b'')!=(y.program.getBytecode() if hasattr(y,'program') else b''):
                    raise ValueError('Glyph hinting changed: '+name)
        for table,fields in {'head':('unitsPerEm',),'hhea':('ascent','descent','lineGap'),'OS/2':('sTypoAscender','sTypoDescender','sTypoLineGap','usWinAscent','usWinDescent')}.items():
            for field in fields:
                if getattr(old[table],field)!=getattr(new[table],field):raise ValueError('Font line metrics changed')
        return {'required_characters':len(required),'retained_characters':len(b),'glyphs_before':len(old.getGlyphOrder()),'glyphs_after':len(glyphs),'outlines_advances_and_line_metrics_equal':True}


def subset_payload(payload,characters):
    font=TTFont(BytesIO(payload),recalcTimestamp=False)
    options=subset.Options();options.flavor='woff2';options.layout_features=['*'];options.recalc_timestamp=False;options.glyph_names=True
    # Retain stable names for unencoded layout glyphs when GIDs are compacted.
    if 'glyf' in font and font['post'].formatType==3.0:
        font['post'].formatType=2.0;font['post'].extraNames=[];font['post'].mapping={}
    worker=subset.Subsetter(options=options);worker.populate(unicodes=characters);worker.subset(font)
    font.flavor='woff2';out=BytesIO();font.save(out);font.close()
    candidate=out.getvalue();proof=verify_subset(payload,candidate,characters)
    if len(candidate)>len(payload):return payload,proof
    return candidate,proof


def prepare(site=SITE,names=TARGETS):
    """Prepare fonts and exact URL-hash updates without writing any file."""
    site=Path(site);bindings=corpora(site,names);outputs={};fonts=[]
    for name in sorted(bindings):
        target='assets/fonts/'+name;original=(site/target).read_bytes();binding=bindings[name]
        candidate,proof=subset_payload(original,binding['characters'])
        if candidate!=original:outputs[target]=candidate
        fonts.append({'path':target,'pages':binding['pages'],'before_bytes':len(original),'after_bytes':len(candidate),'input_sha256':digest(original),'output_sha256':digest(candidate),'corpus_sha256':digest(json.dumps(sorted(binding['characters'])).encode()),**proof})
    for css in (site/'assets').glob('fonts*.css'):
        original=css.read_bytes()
        def version(m):
            key='assets/'+m[1].decode()
            return m[1]+b'?v='+digest(outputs[key])[:12].encode() if key in outputs else m[0]
        current=re.sub(rb'(fonts/[^"?]+\.woff2)\?v=[0-9a-f]+',version,original)
        if current!=original:outputs[css.relative_to(site).as_posix()]=current
    for page in site.rglob('*.html'):
        original=page.read_bytes()
        def version(m):
            key=m[1].decode()
            return m[1]+b'?v='+digest(outputs[key])[:12].encode() if key in outputs else m[0]
        current=re.sub(rb'(assets/fonts(?:-[0-9a-f]+)?\.css)\?v=[0-9a-f]+',version,original)
        if current!=original:outputs[page.relative_to(site).as_posix()]=current
    return outputs,{'fonts':fonts,'before_bytes':sum(r['before_bytes'] for r in fonts),'after_bytes':sum(r['after_bytes'] for r in fonts),'changed_files':sorted(outputs)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true',help='Install the fully validated batch; package records must then be refreshed')
    args=parser.parse_args();outputs,report=prepare()
    if args.write:
        from rebuild import install
        install(outputs)
    report.update(written=args.write,result='pass')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
