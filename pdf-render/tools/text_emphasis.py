"""Native kenten for explicit canonical CSS emphasis, distinct from readings."""
import re


def render(conv, node):
    declarations = dict(part.split(':', 1) for part in node.get('style', '').split(';') if ':' in part)
    declarations = {k.strip(): v.strip() for k, v in declarations.items()}
    values = [declarations[k] for k in ['text-emphasis', 'text-emphasis-style', '-webkit-text-emphasis'] if k in declarations]
    forms = {'filled dot': 'dot', 'dot': 'dot', 'sesame': 'sesame', 'filled sesame': 'sesame'}
    if not values or any(v not in forms for v in values) or len({forms[v] for v in values}) != 1:
        raise ValueError('Unsupported or contradictory text emphasis')
    if declarations.get('text-emphasis-position', 'over right') not in ['over', 'over right']:
        raise ValueError('Unsupported text emphasis position')
    text = node.get_text()
    # The inventory contains plain Japanese spans only. Never flatten ruby or
    # other inline markup into per-character kenten as a guessed fallback.
    if node.find() or not re.fullmatch(r'[\u3005\u3007\u3041-\u30ff\u3400-\u9fff]+', text):
        raise ValueError('Text emphasis needs an intact plain Japanese span')
    form = forms[values[0]]
    mark = r'\textbullet' if form == 'dot' else '﹅'
    conv.features.append({'kind': 'native_text_emphasis', 'text': text,
                          'mark': form, 'mark_count': len(text), 'basis': 'explicit canonical CSS'})
    return r'\ltjkenten[kenten={' + mark + '}]{' + conv.text(text) + '}'
