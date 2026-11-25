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
from html.parser import HTMLParser
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
    return re.sub(r'((?:href|src)="(?:\.\./)*)(assets/(?:[^"?#]+\.(?:css|js)|(?:boar|favicon)\.png))(?:\?v=[0-9a-fA-F]+)?"',version,markup)


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


def native_reader_options():
    """Use native settings radios for the same reader rules when scripts are disabled."""
    source=(Path(__file__).resolve().parents[1]/'web-src/reader-options.css').read_text(encoding='utf-8')
    # Sibling selectors reach the paper and both PDF links without CSS :has().
    for mode in ('show','hide'):
        source=source.replace(f'body[data-rubi={mode}]',f'#rubi-{mode}:checked ~ *')
    source=re.sub(r"""body\[data-(marking|spacing)\s*=\s*(["\x27]?)([\w-]+)\2\s*\]""",
                  r'body:has(input[name=\1][value=\3]:checked)',source)
    for control in ('show-star-order','visible-paper'):
        source=source.replace(f'body[data-{control}]',f'body:has(#{control}:checked)')
    return source+'''
body>input[name=rubi]{position:fixed;top:0;left:0}
#rubi-show:checked ~ .reader-subbar label[for=rubi-show],
#rubi-hide:checked ~ .reader-subbar label[for=rubi-hide]{color:var(--accent);box-shadow:inset 0 -2px var(--accent)}
#rubi-show:focus ~ .reader-subbar label[for=rubi-show],
#rubi-hide:focus ~ .reader-subbar label[for=rubi-hide]{outline:2px solid var(--accent)}
'''


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


class _Tags(HTMLParser):
    """Locate actual tags without serializing or inspecting script text as HTML."""
    def __init__(self, markup):
        super().__init__(convert_charrefs=False)
        self.markup = markup
        self.lines = [0] + [m.end() for m in re.finditer('\n', markup)]
        self.tags = []
        self.open_raw = {}
        self.feed(markup)
        self.close()
        if self.open_raw:
            raise ValueError('Unclosed resource element: ' + ', '.join(self.open_raw))

    def position(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        if tag not in {'link','script','style','img','image','a','body','source','video','audio','iframe','embed','object'}:
            return
        if len(attrs) != len({name for name, value in attrs}):
            raise ValueError('Duplicate attributes on resource element: ' + tag)
        start = self.position()
        raw = self.get_starttag_text()
        entry = {'tag':tag, 'attrs':dict(attrs), 'start':start, 'end':start+len(raw), 'raw':raw}
        self.tags.append(entry)
        if tag in {'script','style'}:
            if tag in self.open_raw:
                raise ValueError('Nested resource element: ' + tag)
            self.open_raw[tag] = entry

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag in {'script','style'}:
            raise ValueError('Self-closing script/style is not supported')

    def handle_endtag(self, tag):
        if tag in self.open_raw:
            entry = self.open_raw.pop(tag)
            entry['content_end'] = self.position()
            entry['close_end'] = self.markup.index('>', self.position()) + 1


def _replace_spans(markup, changes):
    cursor = 0
    pieces = []
    for start, end, replacement in sorted(changes):
        if start < cursor:
            raise ValueError('Overlapping resource replacements')
        pieces.extend((markup[cursor:start], replacement))
        cursor = end
    pieces.append(markup[cursor:])
    return ''.join(pieces)


def _attributes(attrs, excluded=()):
    return ''.join(' ' + name + ('' if value is None else '="' + html.escape(value, quote=True) + '"')
                   for name, value in attrs.items() if name not in excluded)


def _set_attribute(raw, name, value):
    pattern = r'(\s+' + re.escape(name) + r'\s*=\s*)(?:"[^"]*"|\x27[^\x27]*\x27|[^\s>]+)'
    result, count = re.subn(pattern, lambda m:m[1]+'"'+html.escape(value, quote=True)+'"', raw, flags=re.I)
    if count != 1:
        raise ValueError('Expected one resource attribute: ' + name)
    return result


def assert_embedded_resources(markup):
    """Reject unresolved rendering dependencies; ordinary navigation stays external."""
    for entry in _Tags(markup).tags:
        tag, attrs = entry['tag'], entry['attrs']
        keys = {'script':('src',),'img':('src','srcset'),'image':('href','xlink:href'),
                'source':('src','srcset'),'video':('src','poster'),'audio':('src',),
                'iframe':('src',),'embed':('src',),'object':('data',)}.get(tag, ())
        if tag == 'link' and set(attrs.get('rel','').lower().split()) & {'stylesheet','icon'}:
            keys = ('href',)
        for key in keys:
            if key in attrs and not (attrs[key] or '').startswith(('data:', '#')):
                raise ValueError('Unembedded resource: ' + tag + '[' + key + ']')
        if tag == 'style':
            css = markup[entry['end']:entry['content_end']]
            if re.search(r'@import\b', css, re.I):
                raise ValueError('Unembedded CSS import')
            for found in CSS_URL.finditer(css):
                if not found[1].startswith(('data:', '#')):
                    raise ValueError('Unembedded CSS resource: ' + found[1])


def inline_resources(markup, page):
    """Embed dependency tags while preserving every intervening byte of markup."""
    data_cache = {}
    def data_uri(path):
        if path not in data_cache:
            mime = {'.woff':'font/woff', '.woff2':'font/woff2', '.png':'image/png',
                    '.jpg':'image/jpeg', '.jpeg':'image/jpeg', '.svg':'image/svg+xml'}[path.suffix.lower()]
            data_cache[path] = 'data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode('ascii')
        return data_cache[path]

    changes = []
    for entry in _Tags(markup).tags:
        tag, attrs = entry['tag'], entry['attrs']
        start, end = entry['start'], entry['end']
        rel = set(attrs.get('rel','').lower().split())
        if tag == 'link' and 'stylesheet' in rel:
            if 'alternate' in rel or 'disabled' in attrs:
                raise ValueError('Alternate/disabled stylesheet export is not supported')
            path = local_resource(page, attrs.get('href',''))
            css = path.read_text(encoding='utf-8')
            def embed_url(found):
                url = found[1]
                if url.startswith(('data:', '#')):
                    return found[0]
                if url in ('moonlight.png', 'pearl.png'):
                    return 'none'  # Catalog-only artwork is unused in readers.
                return 'url("' + data_uri(local_resource(path, url)) + '")'
            retained = _attributes(attrs, {'href','rel','integrity','crossorigin','referrerpolicy','fetchpriority'})
            changes.append((start, end, '<style'+retained+'>'+CSS_URL.sub(embed_url, css)+'</style>'))
        elif tag == 'script' and 'src' in attrs:
            path = local_resource(page, attrs['src'])
            if 'async' in attrs or attrs.get('type','').lower() == 'module':
                raise ValueError('Asynchronous/module script export is not supported')
            text = path.read_text(encoding='utf-8')
            if 'defer' in attrs and path.name == 'app.js':
                text = "document.addEventListener('DOMContentLoaded',()=>{\n" + text + "\n},{once:true});"
            retained = _attributes(attrs, {'src','defer','integrity','crossorigin','referrerpolicy','fetchpriority'})
            changes.append((start, entry['close_end'], '<script'+retained+'>'+text.replace('</script','<\\/script')+'</script>'))
        elif tag in {'img','image'} or tag == 'link' and 'icon' in rel:
            key = 'src' if tag == 'img' else 'xlink:href' if 'xlink:href' in attrs else 'href'
            url = attrs.get(key)
            if url and not url.startswith(('data:', '#')):
                replacement = _set_attribute(entry['raw'], key, data_uri(local_resource(page, url)))
                changes.append((start, end, replacement))
    result = _replace_spans(markup, changes)
    assert_embedded_resources(result)
    return result


def rebase_links(markup, page, destination):
    """Rebase actual navigation/resource attributes without changing script strings."""
    changes = []
    for entry in _Tags(markup).tags:
        raw = entry['raw']
        for key in ('href','src','xlink:href'):
            url = entry['attrs'].get(key)
            if not url:
                continue
            parsed = urlsplit(url)
            if parsed.scheme or parsed.netloc or url.startswith('#'):
                continue
            target = local_resource(page, url)
            relative = Path(os.path.relpath(target, Path(destination).parent)).as_posix()
            if parsed.query:
                relative += '?' + parsed.query
            if parsed.fragment:
                relative += '#' + parsed.fragment
            raw = _set_attribute(raw, key, relative)
        if raw != entry['raw']:
            changes.append((entry['start'], entry['end'], raw))
    return _replace_spans(markup, changes)


def standalone_html(page, destination=None):
    markup = Path(page).read_text(encoding='utf-8')
    if not any(t['tag']=='body' and 'reader-page' in t['attrs'].get('class','').split() for t in _Tags(markup).tags):
        raise ValueError('Only generated paper readers can be exported')
    markup = inline_resources(markup, page)
    return rebase_links(markup, page, destination) if destination else markup
