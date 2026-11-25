"""Refresh accepted reader bodies using the packaged site shells and native models.

The installed HTML pages are the maintained presentation shells. This command
reprojects their question bodies; it does not recreate old release histories.
"""
from pathlib import Path
import argparse,copy,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(Path(__file__).resolve().parent),str(ROOT/'pdf-render/tools')]
import build as web
from bs4 import BeautifulSoup
from package_paths import resource
from release_contract import contract
from public_paths import html_path,site_pdf

def install_runtime_assets():
    # Reader shells load one bundle; these helpers must precede app.js.
    scripts=('theme-colors.js','reader-sizing.js','browser-memory.js','practice-model.js','practice-ui.js','app.js')
    (web.SITE/'assets/app.js').write_bytes(b'\n'.join(
        (web.WEB/'web-src'/name).read_bytes() for name in scripts))
    (web.SITE/'assets/pdf-typography.css').write_bytes(
        (web.WEB/'web-src/pdf-typography.css').read_bytes())
    (web.SITE/'assets/answer-marking.css').write_text(
        (web.WEB/'web-src/answer-marking.css').read_text('utf-8'),encoding='utf-8',newline='\n')
    (web.SITE/'assets/site.css').write_bytes(b'\n'.join(
        (web.WEB/'web-src'/name).read_bytes() for name in ('site.css','reader-options.css','practice.css')))
    from interface_assets import refresh
    refresh(web.SITE)
    from theme_colors import install_theme_assets
    install_theme_assets(web.SITE)

def refresh_asset_versions():
    from web_assets import version_resources
    changed=0
    for page in web.SITE.rglob('*.html'):
        previous=page.read_text(encoding='utf-8')
        current=version_resources(previous)
        if current!=previous:
            page.write_text(current,encoding='utf-8',newline='\n')
            changed+=1
    return changed

def parse_html(markup):
    """Keep HTML void elements empty across parser chunk boundaries."""
    from shared_styles import VOID
    soup=BeautifulSoup(markup,'html.parser')
    # Some html.parser versions can retain following siblings inside a void
    # element when parsing long documents. Match browser HTML semantics and
    # serialize a stable shell without losing or reordering those siblings.
    for node in soup.find_all(VOID):
        for child in reversed(list(node.contents)):node.insert_after(child.extract())
    return soup


def content(node):
    """Compare authored text/ruby once, excluding generated visual duplicates."""
    clone=copy.copy(node)
    for element in list(clone.select('a.developer-note, .star-solution, .star-unavailable, .visual-only')):
        if element.parent is not None:element.decompose()
    for word in clone.select('.wakachi'):
        word.unwrap()
    clone.smooth()
    return ''.join(clone.stripped_strings)


def changed_outputs(outputs):
    return {name:data for name,data in outputs.items()
            if not (web.SITE/name).is_file() or (web.SITE/name).read_bytes()!=data}


def version_selected(markup,outputs):
    def version(match):
        name=match[2];data=outputs[name] if name in outputs else (web.SITE/name).read_bytes()
        return match[1]+name+'?v='+hashlib.sha256(data).hexdigest()[:12]+'"'
    return re.sub(r'((?:href|src)="(?:\.\./)*)(assets/[^"?#]+\.(?:css|js))(?:\?v=[0-9a-fA-F]+)?"',version,markup)


def prepare(units,refresh_reviews=False):
    """Prepare every selected output in memory before any installation."""
    from font_profiles import installed_profile
    from shared_styles import reuse_site_styles
    from review_refresh import prepare as prepare_review, reader as refresh_reader, page as refresh_review
    from renditions import select
    from image_html import artwork,inventory
    outputs={};results=[]
    for unit in units:
        m=select(web.compose(unit),'regular');orders=web.star_data([m])
        font_name,font_data=installed_profile(m,web.SITE)
        if font_name in outputs and outputs[font_name]!=font_data:raise ValueError('Conflicting font profile')
        outputs[font_name]=font_data
        review=prepare_review(m,web) if refresh_reviews else None
        pdf=web.SITE/site_pdf(unit)
        m['web_metrics']=web.resolve_metrics(m,pdf)
        markup,nav,questions=web.paper(m,orders)
        fresh=parse_html(markup)
        # The original for a native SVG remains embedded in its editorial.
        # A bitmap reused in the drawing itself is still a published dependency.
        vectors={key for key,row in artwork(m).items() if not row.get('raster')}
        images={node.get('src') or node.get('href') for node in fresh.find_all(['img','image'])} if vectors else set()
        for key,row in inventory(m).items():
            if key in vectors and '../'+row['path'] not in images:continue
            target=web.SITE/row['path']
            if not target.is_file() or target.read_bytes()!=row['data']:
                raise ValueError('Installed illustration differs: '+str(target))
        name=html_path(unit);page=web.SITE/name
        soup=parse_html(page.read_text('utf-8'));old=soup.select_one('.paper.editorial')
        if old is None:raise ValueError('Missing installed reader body: '+name)
        for note in old.select('a.developer-note'):
            parent=note.parent
            if parent.get('id') and (target:=fresh.find(id=parent['id'])):target.append(copy.copy(note))
        if content(old)!=content(fresh):raise ValueError('Reader text changed: '+unit)
        if [n['id'] for n in old.select('[id]')]!=[n['id'] for n in fresh.select('[id]')]:
            raise ValueError('Reader IDs changed: '+unit)
        old.clear()
        for child in list(fresh.contents):old.append(child.extract())
        if review:refresh_reader(soup,unit,review,web.safe_json)
        profiles=[n for n in soup.select('link[rel="stylesheet"]')
                  if re.search(r'/assets/fonts(?:-[0-9a-f]+)?\.css(?:\?|$)',n.get('href',''))]
        if len(profiles)!=1:raise ValueError('Expected one reader font profile: '+name)
        profiles[0]['href']='../'+font_name
        node=soup.select_one('#page-data');data=json.loads(node.string)
        data['paper']['public_path']=name
        data['paper']['pdf_path']=site_pdf(unit)
        data['paper']['release_sha256']=web.sha(pdf)
        data['paper']['norubi_pdf_sha256']=web.sha(web.SITE/site_pdf(unit,'norubi'))
        node.string=web.safe_json(data)
        result=reuse_site_styles(web.SITE,name,str(soup))
        outputs[name]=version_selected(result,outputs).encode('utf-8')
        results.append({'unit':unit,'questions':len(questions),'status':'pass'})
        if review:
            name='reviews/'+unit+'.html';page=web.SITE/name
            soup=parse_html(page.read_text('utf-8'));refresh_review(soup,review)
            from package_sources import rewrite_review
            packaged,_=rewrite_review(page,str(soup))
            outputs[name]=version_selected(reuse_site_styles(web.SITE,name,packaged),outputs).encode('utf-8')
        print(unit,'HTML reader verified',flush=True)
    return changed_outputs(outputs),results


def install(outputs):
    """Install a fully prepared batch; restore original bytes on a write failure."""
    targets={name:(web.SITE/name).resolve() for name in outputs}
    for name,path in targets.items():
        if not path.is_relative_to(web.SITE.resolve()):raise ValueError('Output escapes site: '+name)
        if not path.parent.is_dir():raise ValueError('Missing installed output directory: '+name)
    previous={name:path.read_bytes() if path.exists() else None for name,path in targets.items()}
    attempted=[]
    try:
        for name,path in targets.items():
            attempted.append(name);path.write_bytes(outputs[name])
    except BaseException:
        for name in reversed(attempted):
            if previous[name] is None:targets[name].unlink(missing_ok=True)
            else:targets[name].write_bytes(previous[name])
        raise


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    from unit_identity import ALIASES,canonical_unit
    parser.add_argument('--unit',action='append',choices=tuple(contract()['owners'])+tuple(ALIASES))
    parser.add_argument('--write',action='store_true',help='Install the fully validated selected batch; otherwise report changes without writing')
    parser.add_argument('--refresh-reviews',action='store_true',help='Also refresh the selected public review registers')
    parser.add_argument('--refresh-shared-assets',action='store_true',help='Explicit full-site runtime/practice/style refresh; requires --write and no --unit')
    args=parser.parse_args()
    if args.refresh_shared_assets and (not args.write or args.unit):
        parser.error('--refresh-shared-assets requires --write without --unit')
    units=list(dict.fromkeys(canonical_unit(u) for u in args.unit)) if args.unit else list(contract()['owners'])
    outputs,results=prepare(units,args.refresh_reviews)
    if args.write:install(outputs)
    if args.refresh_shared_assets:
        install_runtime_assets()
        from shared_styles import share_site_styles
        share_site_styles(web.SITE,[p.relative_to(web.SITE).as_posix() for p in web.SITE.rglob('*.html')],web.write)
        from package_sources import rewrite_site
        rewrite_site()
        from practice_pages import refresh
        refresh()
        refresh_asset_versions()
    print(json.dumps({'owners':len(units),'reader_bodies':len(results),'written':args.write,
                      'changed_files':sorted(outputs),'result':'pass'}),flush=True)
if __name__=='__main__':main()
