"""Refresh accepted reader bodies using the packaged site shells and native models.

The installed HTML pages are the maintained presentation shells. This command
reprojects their question bodies; it does not recreate old release histories.
"""
from pathlib import Path
import argparse,copy,json,sys
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
    (web.SITE/'assets/site.css').write_bytes(b'\n'.join(
        (web.WEB/'web-src'/name).read_bytes() for name in ('site.css','practice.css')))

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

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    from unit_identity import ALIASES,canonical_unit
    parser.add_argument('--unit',action='append',choices=tuple(contract()['owners'])+tuple(ALIASES))
    parser.add_argument('--write',action='store_true',help='Replace validated reader bodies; otherwise check only')
    args=parser.parse_args();units=list(dict.fromkeys(canonical_unit(u) for u in args.unit)) if args.unit else list(contract()['owners'])
    results=[]
    for unit in units:
        model=web.compose(unit);orders=web.star_data([model])
        from review_refresh import prepare as prepare_review, reader as refresh_reader, page as refresh_review
        review=prepare_review(model,web)
        for variant in ('regular','norubi'):
            from renditions import select
            m=select(copy.deepcopy(model),variant)
            pdf=ROOT/'astraJLPT'/site_pdf(unit,variant)
            m['web_metrics']=web.resolve_metrics(m,pdf)
            from image_html import inventory
            for image in inventory(m).values():
                target=ROOT/'astraJLPT'/image['path']
                if not target.is_file() or target.read_bytes()!=image['data']:
                    raise ValueError('Installed illustration differs: '+str(target))
            markup,nav,questions=web.paper(m,orders)
            page=ROOT/'astraJLPT'/html_path(unit,variant)
            soup=BeautifulSoup(page.read_text('utf-8'),'html.parser');old=soup.select_one('.paper.editorial')
            fresh=BeautifulSoup(markup,'html.parser')
            for note in old.select('a.developer-note'):
                parent=note.parent
                if parent.get('id') and (target:=fresh.find(id=parent['id'])):target.append(copy.copy(note))
            def content(node):
                clone=copy.copy(node)
                # Answer help is regenerated from separately validated canonical
                # STAR metadata. The authored question/passage text remains exact.
                for element in clone.select('a.developer-note, .star-solution, .star-unavailable'):element.decompose()
                return ''.join(clone.stripped_strings)
            if content(old)!=content(fresh):raise ValueError('Reader text changed: '+unit+'/'+variant)
            old_ids=[n['id'] for n in old.select('[id]')];new_ids=[n['id'] for n in fresh.select('[id]')]
            if old_ids!=new_ids:raise ValueError('Reader IDs changed: '+unit+'/'+variant)
            if args.write:
                old.clear()
                for child in list(fresh.contents):old.append(child.extract())
                refresh_reader(soup,unit,review,web.safe_json)
                page.write_text(str(soup),encoding='utf-8',newline='\n')
            results.append({'unit':unit,'variant':variant,'questions':len(questions),'status':'pass'})
        if args.write:
            review_path=web.SITE/'reviews'/f'{unit}.html'
            review_page=BeautifulSoup(review_path.read_text('utf-8'),'html.parser')
            refresh_review(review_page,review)
            review_path.write_text(str(review_page),encoding='utf-8',newline='\n')
        print(unit,'paired HTML bodies verified',flush=True)
    if args.write:
        install_runtime_assets()
        from shared_styles import share_site_styles
        files=[p.relative_to(web.SITE).as_posix() for p in web.SITE.rglob('*.html')]
        share_site_styles(web.SITE,files,web.write)
        from package_sources import rewrite_site
        rewrite_site()
        from practice_pages import refresh
        refresh()
        refresh_asset_versions()
    print(json.dumps({'owners':len(units),'paired_bodies':len(results),'written':args.write,'result':'pass'}),flush=True)
if __name__=='__main__':main()
