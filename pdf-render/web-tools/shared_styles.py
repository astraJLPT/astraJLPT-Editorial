"""Share repeated final HTML declarations without reserializing paper content.

Run after all renderer transforms. Runtime-owned styles and measurement-clone
roots stay inline. The two-ID :not selector is always true (an element cannot
have two IDs) and preserves precedence over our ordinary author rules, while
existing !important declarations and subsequent JS inline writes still win.
"""
from collections import Counter
import hashlib
import html
from html.parser import HTMLParser
from pathlib import PurePosixPath
import re

ASSET = 'assets/paper-shared.css'
PREFIX = 'ps-'
PRIORITY = ':not(#astra-inline-a#astra-inline-b)'
STYLE = re.compile(r'''\sstyle\s*=\s*("[^"]*"|'[^']*')''', re.I)
CLASS = re.compile(r'''\bclass\s*=\s*("[^"]*"|'[^']*')''', re.I)
# BeautifulSoup reorders attributes and emits void tags as <link .../> during
# incremental rebuilds. Remove the existing dependency in either serialization.
LINK = re.compile(
    r'''<link\b(?=[^<>]*\srel\s*=\s*(["'])stylesheet\1)'''
    r'''(?=[^<>]*\shref\s*=\s*(["'])(?:\.\./)*assets/paper-shared\.css(?:\?v=[a-f0-9]+)?\2)[^<>]*>''',
    re.I)
RULE = re.compile(r'\.(ps-[0-9a-z]+)' + re.escape(PRIORITY) + r'\{([^{}]*)\}\n')
VOID = set('area base br col embed hr img input link meta param source track wbr'.split())
RUNTIME_ROOTS = {'paper', 'option-text', 'annotation-base'}
EXAMPLES = {'example-options', 'example-native-options', 'example-source-options'}


class Tags(HTMLParser):
    def __init__(self, markup):
        super().__init__(convert_charrefs=False)
        self.lines = [0] + [m.end() for m in re.finditer('\n', markup)]
        self.stack = []
        self.rows = []
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = set((attrs.get('class') or '').split())
        raw = self.get_starttag_text()
        match = STYLE.search(raw)
        value = attrs.get('style', '')
        # URL bases change in external CSS; !important inline precedence is
        # special. Neither is optimized. Keep anything cleared by runtime JS.
        unsafe = (tag in {'html', 'body', 'table', 'col'} or classes & RUNTIME_ROOTS
                  or (self.stack and self.stack[-1][1] & EXAMPLES)
                  or re.search(r'url\s*\(|!\s*important|[{}<>]', value, re.I))
        if match and value and not unsafe:
            line, col = self.getpos()
            self.rows.append((self.lines[line-1]+col, raw, value))
        if tag not in VOID:
            self.stack.append((tag, classes))

    def handle_startendtag(self, tag, attrs):
        depth = len(self.stack)
        self.handle_starttag(tag, attrs)
        del self.stack[depth:]

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


def base36(n):
    result = ''
    while n:
        n, digit = divmod(n, 36)
        result = '0123456789abcdefghijklmnopqrstuvwxyz'[digit] + result
    return result or '0'


def restore_styles(markup, rules):
    """Expand a prior shared sheet before a repeated/incremental build."""
    if not rules:
        return markup
    def restore(match):
        raw = match[0]
        cm = CLASS.search(raw)
        if not cm:
            return raw
        names = html.unescape(cm[1][1:-1]).split()
        shared = [n for n in names if n in rules]
        if not shared:
            return raw
        if len(shared) != 1 or STYLE.search(raw):
            raise ValueError('Unexpected shared/inline style combination')
        key = shared[0]
        names.remove(key)
        replacement = ('class="' + html.escape(' '.join(names), quote=True) + '" ') if names else ''
        replacement += 'style="' + html.escape(rules[key], quote=True) + '"'
        return raw[:cm.start()] + replacement + raw[cm.end():]
    # Generated start tags have no literal '<' or '>' in attribute values.
    markup = re.sub(r'<[A-Za-z][^<>]*>', restore, markup)
    return LINK.sub('', markup)


def replace_styles(markup, rows, classes):
    changes = []
    for start, raw, value in rows:
        key = classes.get(value)
        if not key:
            continue
        sm = STYLE.search(raw)
        new = raw[:sm.start()] + raw[sm.end():]
        cm = CLASS.search(new)
        if cm:
            new = new[:cm.end()-1] + ' ' + key + new[cm.end()-1:]
        else:
            new = new[:-2] + ' class="'+key+'"/>' if new.endswith('/>') else new[:-1] + ' class="'+key+'">'
        changes.append((start, start+len(raw), new))
    chunks = []
    cursor = 0
    for start, end, replacement in changes:
        chunks.extend((markup[cursor:start], replacement))
        cursor = end
    chunks.append(markup[cursor:])
    return ''.join(chunks), len(changes)


def share_site_styles(site, generated, write):
    old_rules = dict(RULE.findall((site/ASSET).read_text(encoding='utf8'))) if (site/ASSET).exists() else {}
    pages = {}
    counts = Counter()
    before = 0
    for name in sorted(set(generated)):
        if not name.endswith('.html'):
            continue
        markup = (site/name).read_text(encoding='utf8')
        before += len(markup.encode('utf8'))
        markup = restore_styles(markup, old_rules)
        rows = Tags(markup).rows
        pages[name] = (markup, rows)
        counts.update(value for _, _, value in rows)
    # Leave rare/tiny declarations inline when a shared rule would cost more.
    values = sorted(v for v, n in counts.items()
                    if n > 1 and n*(len(html.escape(v, quote=True).encode('utf8'))-10) > len(v.encode('utf8'))+80)
    classes = {v: PREFIX+base36(i) for i, v in enumerate(values)}
    css = ('/* Generated by tools/shared_styles.py. Keep normal priority; JS inline overrides remain authoritative. */\n'
           + ''.join('.'+classes[v]+PRIORITY+'{'+v+'}\n' for v in values))
    write(ASSET, css)
    digest = hashlib.sha256(css.encode('utf8')).hexdigest()[:12]
    occurrences = 0
    after = len(css.encode('utf8'))
    for name, (markup, rows) in pages.items():
        result, count = replace_styles(markup, rows, classes)
        if count:
            depth = len(PurePosixPath(name).parts)-1
            link = '<link rel="stylesheet" href="'+('../'*depth)+ASSET+'?v='+digest+'">'
            if result.count('</head>') != 1:
                raise ValueError('Missing final head: ' + name)
            result = result.replace('</head>', link+'</head>')
        occurrences += count
        after += len(result.encode('utf8'))
        write(name, result)
    return {'rules':len(classes), 'occurrences':occurrences,
            'html_before_bytes':before, 'html_and_shared_css_after_bytes':after,
            'saved_bytes':before-after, 'shared_css_bytes':len(css.encode('utf8'))}


def reuse_site_styles(site,name,markup):
    """Reuse installed class identities without changing the shared stylesheet."""
    sheet=site/ASSET
    if not sheet.is_file():raise ValueError('Missing installed shared stylesheet')
    css=sheet.read_text(encoding='utf-8');rules=dict(RULE.findall(css))
    markup=restore_styles(markup,rules)
    result,_=replace_styles(markup,Tags(markup).rows,{value:key for key,value in rules.items()})
    if re.search(r'\bps-[0-9a-z]+\b',result):
        depth=len(PurePosixPath(name).parts)-1
        digest=hashlib.sha256(sheet.read_bytes()).hexdigest()[:12]
        link='<link rel="stylesheet" href="'+('../'*depth)+ASSET+'?v='+digest+'">'
        if result.count('</head>')!=1:raise ValueError('Missing final head: '+name)
        result=result.replace('</head>',link+'</head>')
    return result
