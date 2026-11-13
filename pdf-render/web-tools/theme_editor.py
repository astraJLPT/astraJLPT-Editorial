"""Shared editable color contract: settings, CSS defaults and runtime metadata."""
from html import escape

BASE = [
    ('bg', 'background', 'Main colors', False),
    ('text', 'reading text', 'Main colors', False),
    ('muted', 'secondary text', 'Main colors', False),
    ('accent', 'interface accent', 'Main colors', False),
    ('correct', 'correct', 'Main colors', False),
    ('wrong', 'wrong', 'Main colors', False),
    ('neutral', 'gradeless answer', 'Main colors', False),
    ('raised', 'buttons & controls', 'Advanced colors', False),
    ('correct-ink', 'correct text & numbers', 'Advanced colors', False),
    ('edge', 'paper outline', 'Advanced colors', False),
    ('edge-soft', 'soft dividers', 'Advanced colors', True),
    ('edge-strong', 'strong borders', 'Advanced colors', True),
    ('logo-secondary', 'wordmark · JLPT', 'Advanced colors', False),
]
FILL_CONTROLS = [dict(id='cell-fill', label='cell fill', default=11),
                 dict(id='fill', label='fill style', default=30)]

# Derived shades always follow their sources; only BASE roles have color pickers.
DERIVED = [
    ('option-hover', 'Answer hover', 'Interface & wordmark', 'text', 4),
    ('email-rule', 'Passage rules', 'Interface & wordmark', 'text', 55),
    ('accent-wash', 'Accent wash', 'Interface & wordmark', 'accent', 9),
    ('accent-edge', 'Accent highlight', 'Interface & wordmark', 'accent', 40),
]
STATE_ROLES = [('cell-fill', 'Cell fill · 11%', 'Answer fills', 11),
               ('fill', 'Fill style · 30%', 'Answer fills', 30),
               ('review-fill', 'Review highlight · 20%', 'Answer fills', 20),
               ('flame-core', 'Flame core', 'Flame colors', 48)]
for effect, group, values in [
    ('neon', 'Neon colors', (70, 38, 58, 28)),
    ('flame', 'Flame colors', (70, 35, 67, 32, 75, 38)),
    ('great', 'Great Flame colors', (90, 80, 60, 40, 65, 50, 95, 85, 67, 42, 72, 83, 63, 38, 68)),
]:
    for value in values:
        STATE_ROLES.append((f'{effect}-glow-{value}', f'Glow · {value}%', group, value))
for key, label, group, value in STATE_ROLES:
    for state in ('correct', 'wrong', 'neutral'):
        DERIVED.append((f'{state}-{key}', state.title() + ' · ' + label, group, state, value))


def color_roles():
    roles = [dict(id=k, label=label, group=group, alpha=alpha, editable=True) for k, label, group, alpha in BASE]
    next(r for r in roles if r['id'] == 'neutral')['formula'] = 'var(--text)'
    roles.append(dict(id='logo-primary', formula='var(--accent)'))
    for k, label, group, source, percentage in DERIVED:
        target = 'var(--text)' if k.endswith('flame-core') else 'transparent'
        roles.append(dict(id=k, label=label, group=group, alpha=target == 'transparent',
                          formula=f'color-mix(in srgb, var(--{source}) {percentage}%, {target})'))
        if any(k == f'{state}-{effect}' for state in ('correct', 'wrong', 'neutral') for effect in ('cell-fill', 'fill')):
            roles[-1]['fillControl'] = k.split('-', 1)[1]
    for key, label, color in [('shadow-soft', 'Soft shadows', '#00000033'),
                              ('shadow-medium', 'Toast shadow', '#00000044'),
                              ('shadow-strong', 'Panel & hover shadows', '#00000077')]:
        roles.append(dict(id=key, label=label, group='Interface & wordmark', alpha=True, formula=color))
    return roles


def editor_css():
    rules = ['body{--paper:var(--bg);' + ''.join('--'+r['id']+':'+r['formula']+';' for r in color_roles() if 'formula' in r) + '}']
    for state, correct in [('correct', 'true'), ('wrong', 'false')]:
        selectors = [f'.answer-radio[data-correct="{correct}"]:checked+.option',
                     f'.question:has(.answer-radio[data-correct="{correct}"]:checked)',
                     f'.sample-option[data-correct="{correct}"]']
        if correct == 'true':
            selectors.append('.marking-grid .mark-icon')
        rules.append(','.join(selectors)+'{'+''.join(f'--state-{key}:var(--{state}-{key});' for key, *_ in STATE_ROLES)+'}')
    rules.append('body[data-grades-hidden="true"] .paper :is(.answer-radio:checked+.option,.question:has(.answer-radio:checked)){--state:var(--neutral);--state-ink:var(--neutral);--margin-state:var(--neutral);--margin-symbol:"•";'+''.join(f'--state-{key}:var(--neutral-{key});' for key, *_ in STATE_ROLES)+'}')
    return '\n'.join(rules)


def editor_markup():
    def row(role):
        key, label = role['id'], escape(role['label'])
        result = f'''<div class="color-row" data-color-row="{key}">
<label for="color-{key}">{label}</label>
<div class="color-inputs"><input type="color" id="swatch-{key}" aria-label="{label} swatch" data-color-swatch="{key}">
<input type="text" id="color-{key}" data-color-hex="{key}" aria-label="{label} hex" spellcheck="false" autocomplete="off" maxlength="9" aria-describedby="color-format-help">
<button type="button" data-color-reset="{key}" aria-label="Reset {label}" title="Reset {label}">↺</button></div>'''
        if role['alpha']:
            result += f'<label class="color-opacity">opacity<input type="range" min="0" max="100" step="0.1" data-color-alpha="{key}" aria-label="{label} opacity"><output></output></label>'
        return result+'</div>'
    result = '''<aside class="theme-editor js-only" aria-label="Customize theme colors"><div class="color-editor-heading"><h3>colors</h3><button type="button" id="reset-theme-colors" aria-label="Reset this theme">reset</button></div><span class="sr-only" id="color-format-help">Choose a swatch or enter hex. Transparent borders accept #RRGGBBAA. Reset restores the theme color.</span><span class="sr-only" id="color-edit-status" role="status" aria-live="polite"></span><div class="main-colors">'''
    roles = [r for r in color_roles() if r.get('editable')]
    result += ''.join(row(r) for r in roles if r['group'] == 'Main colors')
    result += '</div><details class="advanced-colors"><summary>more colors</summary><div class="advanced-color-grid">'
    result += ''.join(row(r) for r in roles if r['group'] == 'Advanced colors')
    result += '</div><div class="fill-opacity-controls"><h4>fill opacity</h4><p>Applies to correct, wrong and gradeless answers.</p>'
    for control in FILL_CONTROLS:
        key, label = control['id'], control['label']
        result += f'''<div class="fill-opacity-row"><label for="opacity-{key}">{label}<output id="opacity-{key}-output">{control['default']}%</output></label><div><input id="opacity-{key}" type="range" min="0" max="100" step="1" value="{control['default']}" data-fill-opacity="{key}" aria-label="{label} opacity"><button type="button" data-fill-reset="{key}" aria-label="Reset {label} opacity" title="Reset {label} opacity">↺</button></div></div>'''
    return result+'</div></details></aside>'
