"""Verify the packaged file inventory, installed PDFs and local website links."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parent
SITE=ROOT/'astraJLPT'
MANIFEST=ROOT/'pdf-render/contracts/package-files.json'
def digest(p):
    with p.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
class Links(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.targets=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        for key in ('src','href'):
            if attrs.get(key):self.targets.append(attrs[key])
def main():
    manifest=json.loads(MANIFEST.read_text('utf-8'))
    failures=[]
    if (SITE/'papers-norubi').exists():failures.append('Retired papers-norubi HTML directory is present')
    for name,record in manifest['files'].items():
        target=ROOT/name
        if not target.is_file() or digest(target)!=record['sha256']:failures.append('Changed/missing package file: '+name)
    installed=json.loads((ROOT/'pdf-render/contracts/installed-pdfs.json').read_text('utf-8'))
    if len(installed)!=402:failures.append('Expected 402 installed PDFs')
    for name,record in installed.items():
        if digest(ROOT/name)!=record['sha256']:failures.append('Installed PDF differs: '+name)
    links=0
    for path in SITE.rglob('*.html'):
        parser=Links();parser.feed(path.read_text('utf-8'))
        for href in parser.targets:
            u=urlsplit(href)
            if u.scheme or u.netloc or not u.path:continue
            target=(path.parent/unquote(u.path)).resolve()
            if not target.is_relative_to(SITE) or not target.is_file():failures.append('Broken site link: '+path.relative_to(SITE).as_posix()+' -> '+href)
            links+=1
    for path in SITE.rglob('*.css'):
        for href in re.findall(r'url\([\"\']?([^\)\"\']+)',path.read_text('utf-8')):
            u=urlsplit(href)
            if u.scheme or u.netloc or not u.path:continue
            if not (path.parent/unquote(u.path)).resolve().is_file():failures.append('Broken CSS asset: '+href)
    size=sum(p.stat().st_size for p in SITE.rglob('*') if p.is_file())
    if size>1_000_000_000:failures.append('Website exceeds the conservative 1 GB budget')
    result={'result':'fail' if failures else 'pass','packaged_files':len(manifest['files']),'paired_pdf_files':len(installed),'local_html_links':links,'website_bytes':size,'failures':failures[:30]}
    print(json.dumps(result,indent=2))
    return bool(failures)
if __name__=='__main__':raise SystemExit(main())
