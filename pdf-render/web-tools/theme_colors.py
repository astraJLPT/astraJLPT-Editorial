"""Approved palette-only theme adaptation (2026-11-03 handoff, Part A).

Build-time decisions only. Source palettes come from the pinned, bundled
Monkeytype data; fixtures are used by verification, never by this generator.
"""
import copy
import importlib.util
import math
import re
from theme_editor import color_roles, editor_css, editor_markup, FILL_CONTROLS

MODES = ('auto', 'sub', 'text')
FALLBACK = {
    'dmg': ('caret', 'sub', 'caret'),
    'macroblank': ('caret', 'sub', 'caret'),
    'our_theme': ('sub',) * 3,
    'shadow': ('sub',) * 3,
    'trackday': ('sub',) * 3,
}
NATIVE_BORDERS = {
    'jlpt_paper': ('#bababa', '#cecece', '#bababa'),
    'astraJLPT_dark': ('#444953', '#292b31', '#444953'),
    'astraJLPT_sepia': ('#b4a692', '#d7ccba', '#b4a692'),
}
CSS_ROLES = {
    'body': 'text', 'correct': 'correct', 'correctInk': 'correct-ink',
    'wrong': 'wrong', 'edgeSource': 'edge',
    'edgeSoft': 'edge-soft', 'edgeStrong': 'edge-strong',
    'logoPrimary': 'logo-primary', 'logoSecondary': 'logo-secondary',
}


def channels(value):
    if not re.fullmatch(r'#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})', value):
        raise ValueError('Invalid source color: ' + value)
    h = value[1:]
    if len(h) in (3, 4):
        h = ''.join(c * 2 for c in h)
    return [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)], int(h[6:8], 16) / 255 if len(h) == 8 else 1


def linear(x):
    return x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4


def luminance(rgb):
    return sum(a * linear(b) for a, b in zip((.2126, .7152, .0722), rgb))


def contrast(fg, bg, opacity=1):
    rgb, alpha = channels(fg)
    paper, paper_alpha = channels(bg)
    if paper_alpha != 1:
        raise ValueError('Paper must be opaque')
    alpha *= opacity
    a = luminance([v * alpha + b * (1 - alpha) for v, b in zip(rgb, paper)])
    b = luminance(paper)
    return (max(a, b) + .05) / (min(a, b) + .05)


def oklab(color):
    r, g, b = map(linear, channels(color)[0])
    l = math.cbrt(.4122214708*r + .5363325363*g + .0514459929*b)
    m = math.cbrt(.2119034982*r + .6806995451*g + .1073969566*b)
    s = math.cbrt(.0883024619*r + .2817188376*g + .6299787005*b)
    return (.2104542553*l + .7936177850*m - .0040720468*s,
            1.9779984951*l - 2.4285922050*m + .4505937099*s,
            .0259040371*l + .7827717662*m - .8086757660*s)


def distance(a, b):
    return math.dist(oklab(a), oklab(b))


def distinct(a, b):
    return distance(a, b) >= .08


def best(candidates, paper):
    # max retains the first item on exact ties; never round decisions.
    return max(candidates, key=lambda c: contrast(c, paper), default=None)


def edge_mix(source, paper, target):
    lo, hi = 0, 1
    if contrast(source, paper) >= target:
        for _ in range(60):
            mid = (lo + hi) / 2
            if contrast(source, paper, mid) >= target:
                hi = mid
            else:
                lo = mid
    return f'color-mix(in srgb, {source} {100 * hi:.2f}%, transparent)'


def adapt(theme, mode):
    if mode not in MODES:
        raise ValueError('Invalid text-source mode: ' + mode)
    p = theme['colors']
    for key in ('bg', 'main', 'caret', 'sub', 'text', 'error', 'colorfulError', 'errorExtra'):
        channels(p[key])
    paper = p['bg']
    choice = ('sub' if contrast(p['sub'], paper) > contrast(p['text'], paper) else 'text') if mode == 'auto' else mode
    body = p[choice]
    correct, correct_source, wrong, wrong_source = p['main'], 'main', p['error'], 'error'
    if distance(p['main'], body) < .045:
        for source in ('sub', 'caret'):
            c = p[source]
            if contrast(c, paper) >= 3 and distinct(c, body) and distinct(c, p['error']):
                correct, correct_source = c, source
                break
    if correct == p['main'] and not distinct(p['main'], p['error']):
        for source in ('colorfulError', 'errorExtra'):
            c = p[source]
            if contrast(c, paper) >= 3 and distinct(c, p['main']) and distinct(c, body):
                wrong, wrong_source = c, source
                break
        else:
            # Unknown fallback palettes fail at build time for review.
            correct_source = FALLBACK[theme['id']][MODES.index(mode)]
            correct = p[correct_source]
    if not distinct(correct, wrong):
        sources = [k for k in ('sub', 'caret', 'main') if distinct(p[k], wrong)]
        if not sources:
            raise ValueError('No distinct original correct color: ' + theme['id'])
        correct_source = max(sources, key=lambda k: contrast(p[k], paper))
        correct = p[correct_source]
    if contrast(correct, paper) >= 3 and distinct(correct, body) and distinct(correct, wrong):
        ink = correct
    else:
        candidates = [c for c in (p['text'], p['main'], p['caret'], p['sub'], body) if distinct(c, wrong)]
        readable = [c for c in candidates if contrast(c, paper) >= 4.5]
        ink = best(readable or candidates, paper) or correct
    edge = p['sub'] if contrast(p['sub'], paper) >= 1.8 or contrast(p['sub'], paper) >= contrast(p['text'], paper) else p['text']
    logos = [body, p['sub'], p['text']]
    logo = next((c for c in logos if contrast(c, paper) >= 4.5 and distance(c, p['main']) >= .09), None)
    if logo is None:
        logo = best([c for c in logos if distance(c, p['main']) >= .09], paper) or body
    return dict(correct=correct, correctInk=ink, correctSource=correct_source,
                edgeSoft=edge_mix(edge, paper, 1.30), edgeStrong=edge_mix(edge, paper, 1.80), edgeSource=edge,
                logoPrimary=p['main'], logoSecondary=logo, body=body, wrong=wrong,
                wrongSource=wrong_source)


def prepare(themes, vendor, track):
    themes = copy.deepcopy(themes)
    # One permanent surface. Native paper colors replace the old outer background.
    for theme in themes['originals']:
        theme['colors']['bg'] = theme['colors'].pop('paper')
        if theme['id'] == 'jlpt_paper':
            theme['colors']['text'] = '#000000'
    importer = track(vendor / 'tools/import_monkeytype.py')
    spec = importlib.util.spec_from_file_location('pinned_theme_import', importer)
    parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser)
    source = track(vendor / 'vendor/monkeytype/themes.ts')
    import hashlib
    if hashlib.sha256(source.read_bytes()).hexdigest() != parser.SOURCE_SHA256:
        raise ValueError('Pinned Monkeytype source changed; review theme rules first')
    palettes = parser.parse_themes(source.read_text(encoding='utf-8'))
    for theme in themes['monkeytype']:
        original = palettes[theme['id']]
        if any(original[k] != v for k, v in theme['colors'].items()):
            raise ValueError('Original palette drift: ' + theme['id'])
        for k in ('errorExtra', 'colorfulError'):
            theme['colors'][k] = original[k]
        theme['adaptedColors'] = {mode: adapt(theme, mode) for mode in MODES}
    themes['colorRoles'] = color_roles()
    themes['fillControls'] = FILL_CONTROLS
    themes['editorMarkup'] = editor_markup()
    for theme in themes['originals'] + themes['monkeytype']:
        theme['editorColors'] = {mode: editor_values(theme, mode) for mode in MODES}
    return themes


def theme_values(theme, mode='auto'):
    c = theme['colors']
    if theme['id'] in NATIVE_BORDERS:
        vals = {k: c[k] for k in ('bg', 'raised', 'text', 'muted', 'edge', 'accent', 'correct', 'wrong')}
        vals.update(zip(('edge', 'edge-soft', 'edge-strong'), NATIVE_BORDERS[theme['id']]))
        vals.update({'correct-ink': 'var(--correct)', 'logo-primary': 'var(--accent)', 'logo-secondary': 'var(--text)'})
    else:
        vals = dict(bg=c['bg'], raised=c['subAlt'], muted=c['sub'], accent=c['main'])
        vals.update({css: theme['adaptedColors'][mode][key] for key, css in CSS_ROLES.items()})
    return vals


def editor_values(theme, mode):
    vals = theme_values(theme, mode)
    # Expose genuine dependencies; editing a child explicitly breaks only that link.
    for role, parent in [('logo-primary', 'accent'), ('logo-secondary', 'text'), ('correct-ink', 'correct')]:
        if vals[role] == vals[parent]:
            vals[role] = f'var(--{parent})'
    if vals['correct-ink'] == vals['text']:
        vals['correct-ink'] = 'var(--text)'
    for role in ('edge-soft', 'edge-strong'):
        vals[role] = vals[role].replace(vals['edge'], 'var(--edge)')
    return vals


def theme_css(themes, no_script=False):
    # A page-wide :has() for every palette makes Chromium reconsider the whole
    # reader when fitting probes are inserted. JS reflects the selected ID on
    # body; the original radio-driven rules remain available without scripting.
    rules = [] if no_script else [editor_css()]
    for theme in themes['originals'] + themes['monkeytype']:
        vals = theme_values(theme)
        name = theme['name'].replace('"', '\\"')
        scheme = 'dark' if theme.get('dark', theme['id'] == 'astraJLPT_dark') else 'light'
        selector = 'body:has(#theme-' + theme['id'] + ':checked)' if no_script else 'body[data-theme="' + theme['id'] + '"]'
        rules.append(selector + '{' + ''.join('--' + k + ':' + v + ';' for k, v in vals.items()) + '--theme-label:"' + name + '";color-scheme:' + scheme + '}')
    return '\n'.join(rules)


def install_theme_assets(site):
    import json
    from web_assets import native_reader_options
    source = (site/'assets/theme-data.js').read_text(encoding='utf-8')
    themes = json.loads(source.removeprefix('globalThis.AstraThemes = ').rstrip().removesuffix(';'))
    for name, no_script in [('themes.css', False), ('themes-no-script.css', True)]:
        css=theme_css(themes,no_script)
        if no_script:css+='\n'+native_reader_options()
        (site/'assets'/name).write_text(css, encoding='utf-8', newline='\n')
