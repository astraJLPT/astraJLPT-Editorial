"""Keep additional repository principals explicit and unavailable as website links."""
from pathlib import Path
from urllib.parse import unquote,urlsplit
import html,re
ROOT=Path(__file__).resolve().parents[2]
SITE=ROOT/'astraJLPT'
PATTERN=re.compile(r'<a\b(?P<attrs>[^>]*\bhref=(?P<quote>[\"\'])(?P<href>[^\"\']+)(?P=quote)[^>]*)>(?P<label>.*?)</a>',re.S|re.I)

def rewrite_review(path,source):
    count=0
    def replace(match):
        nonlocal count
        href=html.unescape(match['href']);url=urlsplit(href)
        if url.scheme or url.netloc:return match[0]
        target=(path.parent/unquote(url.path)).resolve()
        if not target.is_relative_to(SITE/'assets/principals') or target.exists():return match[0]
        extra=ROOT/'additional-assets/principals'/target.name
        if not extra.is_file():raise ValueError('Missing principal in both locations: '+target.name)
        location=extra.relative_to(ROOT).as_posix()
        page=' ('+html.escape(url.fragment)+')' if url.fragment else ''
        count+=1
        return '<span class="principal-repository-source">Principal source'+page+': <code>'+html.escape(location)+'</code> — open this file from the GitHub repository; it is not hosted on this website.</span>'
    result=PATTERN.sub(replace,source)
    return result,count

def rewrite_site():
    changed=[];links=0
    for path in (SITE/'reviews').glob('*.html'):
        source=path.read_text('utf-8')
        result,count=rewrite_review(path,source)
        if count:path.write_text(result,encoding='utf-8',newline='\n');changed.append(path.name);links+=count
    return {'pages':len(changed),'links_replaced':links}
if __name__=='__main__':print(rewrite_site())
