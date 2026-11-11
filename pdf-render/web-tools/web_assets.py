"""Local resource resolution and optional packaging of the production reader.

No content rendering lives here. A standalone export inlines the very same
generated HTML/CSS/JS/fonts used by the normal shared-asset website.
"""
import base64
import html
import json
import os
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

SITE = Path(__file__).resolve().parents[2]/'astraJLPT'
THEME_PREFIX = 'globalThis.AstraThemes = '
CSS_URL = re.compile(r'url\([\"\']?([^\"\')]+)[\"\']?\)')


def version_resources(markup, site=SITE):
    """Keep shared filenames while invalidating stale browser CSS/JS caches."""
    import hashlib
    def version(match):
        name=match[2];path=Path(site)/name
        digest=hashlib.sha256(path.read_bytes()).hexdigest()[:12]
        return match[1]+name+'?v='+digest+'"'
    return re.sub(r'((?:href|src)="(?:\.\./)*)(assets/[^"?#]+\.(?:css|js))(?:\?v=[0-9a-fA-F]+)?"',version,markup)


def local_resource(page, url):
    parsed = urlsplit(html.unescape(url))
    if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith('/'):
        raise ValueError('Expected a relative local resource: ' + url)
    path = (Path(page).parent / unquote(parsed.path)).resolve()
    if not path.is_relative_to(SITE.resolve()):
        raise ValueError('Resource escapes the website: ' + url)
    if not path.is_file():
        raise FileNotFoundError('Missing website resource: ' + str(path))
    return path


def page_css(soup, page):
    return '\n'.join([s.get_text() for s in soup.select('style')] + [
        local_resource(page, s['href']).read_text(encoding='utf-8')
        for s in soup.select('link[rel="stylesheet"]')])


def page_scripts(soup, page):
    return '\n'.join(local_resource(page, s['src']).read_text(encoding='utf-8')
                     if s.has_attr('src') else s.get_text()
                     for s in soup.select('script:not([type="application/json"])'))


def theme_data(soup, page):
    node = soup.select_one('#theme-data')
    text = local_resource(page, node['src']).read_text(encoding='utf-8') if node.has_attr('src') else node.get_text()
    if not text.startswith(THEME_PREFIX) or not text.rstrip().endswith(';'):
        raise ValueError('Unexpected shared theme-data format')
    return json.loads(text[len(THEME_PREFIX):].rstrip()[:-1])


def inline_resources(markup, page):
    """Embed dependencies only; preserve the renderer's markup byte for byte."""
    def data_uri(path):
        mime = {'.woff': 'font/woff', '.woff2': 'font/woff2', '.png': 'image/png',
                '.jpg': 'image/jpeg', '.svg': 'image/svg+xml'}[path.suffix.lower()]
        return 'data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode('ascii')

    def stylesheet(match):
        path = local_resource(page, match[1])
        css = path.read_text(encoding='utf-8')
        def embed_url(found):
            url = found[1]
            if url.startswith(('data:', '#')):
                return found[0]
            # Catalog artwork never appears in a paper. Do not put its images
            # into every optional single-paper export.
            if url in ('moonlight.png', 'pearl.png'):
                return 'none'
            return 'url("' + data_uri(local_resource(path, url)) + '")'
        return '<style>' + CSS_URL.sub(embed_url, css) + '</style>'

    markup = re.sub(r'<link rel="stylesheet" href="([^"]+)">', stylesheet, markup)
    def script(match):
        text = local_resource(page, match[2]).read_text(encoding='utf-8')
        attrs = (match[1] + match[3]).replace(' defer', '')
        return '<script' + attrs + '>' + text.replace('</script', '<\\/script') + '</script>'
    markup = re.sub(r'<script([^>]*) src="([^"]+)"([^>]*)></script>', script, markup)
    markup = re.sub(r'(<img\b[^>]* src=")([^"]+)(")',
                    lambda m: m[0] if m[2].startswith('data:') else m[1] + data_uri(local_resource(page, m[2])) + m[3], markup)
    # Authored vector figures can contain source-bound raster pieces. These
    # are dependencies of the paper just like ordinary HTML images.
    markup = re.sub(r'(<image\b[^>]* href=")([^"]+)(")',
                    lambda m: m[0] if m[2].startswith('data:') else m[1] + data_uri(local_resource(page, m[2])) + m[3], markup)
    return markup


def rebase_links(markup, page, destination):
    """Keep local navigation usable when a fixture/export lives under work/."""
    def rebase(match):
        url = html.unescape(match[2])
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc or url.startswith('#'):
            return match[0]
        target = local_resource(page, url)
        relative = Path(os.path.relpath(target, Path(destination).parent)).as_posix()
        if parsed.query:
            relative += '?' + parsed.query
        if parsed.fragment:
            relative += '#' + parsed.fragment
        return match[1] + html.escape(relative, quote=True) + match[3]
    return re.sub(r'((?:href|src)=")([^"]+)(")', rebase, markup)


def standalone_html(page, destination=None):
    markup = Path(page).read_text(encoding='utf-8')
    if 'class="reader-page"' not in markup:
        raise ValueError('Only generated paper readers can be exported')
    markup = inline_resources(markup, page)
    return rebase_links(markup, page, destination) if destination else markup
