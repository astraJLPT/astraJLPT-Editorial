"""Approved 2026-11-09 typography, applied by semantic role after composition.

The pinned policy changes presentation only. Canonical content, ruby and owner
identities remain the responsibility of their existing validated contracts.
"""
import copy
import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / 'pdf-render/config/workbook_typography.json'
NUMERAL_SCALE = .865


def macro(font_id):
    name = 'Workbook' + ''.join(part.title() for part in font_id.split('_'))
    names = ('Zero','One','Two','Three','Four','Five','Six','Seven','Eight','Nine')
    return re.sub('[0-9]', lambda m: names[int(m[0])], name)


@lru_cache(maxsize=1)
def policy():
    return json.loads(POLICY.read_text('utf-8'))


def font(font_id, **options):
    selected = policy()['fonts'][font_id]
    return {'path': selected['path'], 'sha256': selected['sha256'],
            'bold_same_face': True, **options}


def resolve(model):
    if (model.get('ruby_release') or {}).get('id')=='rubi-typography-20261109-v1':
        import sys
        sys.path.insert(0,str(ROOT/'pdf-render/editorial-tools'))
        from workbook_transition import rebind_style
        model['style'],settings_rebindings=rebind_style(model['unit'],model['style'])
    else:settings_rebindings=[]
    style = model['style']
    roles = style['font_roles']
    changes = []
    if model['unit'] in ('N1_workbook_2018','N2_workbook_2018','N3_workbook_2018'):
        # The owner remains stable; the authenticated publication replaces
        # the old sitting claim on generated cover facts only.
        for booklet in model['layout']['booklets']:
            booklet['cover'].update(publication=copy.deepcopy(model['publication']),
                                    minutes=None,date_label=None)
        changes.append('Approved 2018 workbook publication cover identity')
    if roles['choice_numeral'].get('horizontal_scale') == .82:
        roles['choice_numeral']['horizontal_scale'] = .8
        changes.append('D04: editorial choice-role standardization 0.82 -> 0.80')
    from era_registry import for_unit
    modern = (for_unit(model['unit']).GENERATION == 'modern-2010'
              and 'sample' not in model['unit'] and int(model['unit'][-4:]) >= 2010)
    if modern:
        for role in ('instruction_latin', 'instruction_japanese',
                     'task_label', 'task_label_japanese'):
            roles[role] = font('futogo_b101_pr6n_bold')
        roles['instruction_numeral'] = font('futogo_b101_pr6n_bold', horizontal_scale=NUMERAL_SCALE)
        roles['instruction_selector'] = font('futogo_b101_pr6n_bold')
        # The old N5 wrapper scaled Japanese and numeral ink together. The
        # approved numeral role now owns its one effective ink transform.
        if model['unit'].startswith('N5') and style.get('heading_horizontal_scale') == .92:
            style['heading_horizontal_scale'] = 1
        horizontal = style.get('heading_horizontal_scale', 1)
        style['instruction_selector'] = {
            'role': 'instruction_selector', 'cell_em': 1.0 / horizontal,
            'digit_horizontal_scale': NUMERAL_SCALE / horizontal,
            'dot_horizontal_scale': 1 / horizontal,
            'suffix_gap_em': 0, 'display_digits': 'ascii',
            'basis': 'D01-D03: ASCII FutoGo ink at 0.865; independent native full-em selector cells and unsqueezed dot'}
        style['approved_administrative_numerals'] = True
        changes.append('D01-D03: approved FutoGo administrative roles')
    model['workbook_typography'] = {'policy_id': policy()['policy_id'],
                                   'changes': changes, 'numeral_xscale': NUMERAL_SCALE,
                                   'canonical_setting_rebindings':settings_rebindings}
    local = policy().get('owners', {}).get(model['unit'], {})
    if local:
        model['workbook_typography']['local'] = copy.deepcopy(local)
        from model import Projection, digest
        items = {i['id']: i for s in model['document']['sections'] for i in s['items']}
        for row in local.get('spans', []):
            item = items[row['target']]
            if row['text'] not in Projection(item['content']).text:
                raise ValueError('Stale approved font span: ' + model['unit'] + '/' + row['target'])
        for target, patch in local.get('section_styles', {}).items():
            style['section_styles'][target].update(copy.deepcopy(patch))
        if local.get('duration'):
            target = local['duration']['target']
            style['table_styles'][target]['0']['approved_duration'] = 'D19'
            roles['workbook_gothicbbb_pr6_medium'] = font('gothicbbb_pr6_medium', scale=1)
        if local.get('native_2012_furniture'):
            furniture = local['native_2012_furniture']
            from model import file_hash
            for source in furniture['sources']:
                if not __import__('release_contract').verify_source(source['path'], source['sha256']):
                    raise ValueError('Changed 2012 typography source')
            roles['workbook_shingo_pro_regular_exact2012'] = font('shingo_pro_regular_exact2012', scale=1, features=['vert','vrt2'])
            roles['workbook_franklin_book_italic_exact2012'] = font('franklin_book_italic_exact2012', scale=1)
            style['workbook_native_2012_furniture'] = copy.deepcopy(furniture)
            groups = furniture['groups']
            task_groups = {}
            for task in set(model['tasks'].values()):
                task_groups[task] = ('reading' if task in ('reading','paired_reading','information_retrieval')
                                     else 'grammar' if task in ('grammar','sentence_composition','cloze') else 'vocabulary')
            style['task_edge_tabs'] = {'basis':'observed_label_generated_outer_parity',
                'policy_decision':'observed-task-edge-tabs','evidence':{'kind':'approved_workbook_2012_furniture'},
                'geometry':furniture['geometry'],'groups':groups,'task_groups':task_groups}
    for font_id in {r['font_id'] for r in local.get('spans', [])}:
        roles['workbook_' + font_id] = font(font_id)


def prepare(value, rows):
    """Mark exact approved text spans without changing text, ruby or structure.

    Each text-node segment is wrapped independently. Complete ruby atoms keep
    their readings inside the same selected family; structural tags stay put.
    """
    import html
    from model import Projection
    if not rows:
        return value
    raw = value['html'] if isinstance(value, dict) else html.escape(value).replace('\n', '<br/>')
    if 'data-workbook-font=' in raw:
        return value
    projection = Projection({'html': raw})
    edits = []
    emphasis=[]
    for pattern in (r'<(b|strong)\b[^>]*>.*?</\1>',r'<p\b[^>]*style=["\'][^"\']*font-weight\s*:\s*(?:bold|[6-9]00)[^"\']*["\'][^>]*>.*?</p>'):
        emphasis.extend(match.span()for match in re.finditer(pattern,raw,re.S|re.I))
    for row in rows:
        for match in re.finditer(re.escape(row['text']), projection.text):
            start, end = match.span()
            if row.get('scope')=='authored_emphasis':
                a=projection.mapping[start][0];b=projection.mapping[end-1][1]
                if not any(x<=a and b<=y for x,y in emphasis):continue
            ruby = [r for r in projection.ruby if r['start'] < end and r['end'] > start]
            if any(r['start'] < start or r['end'] > end for r in ruby):
                raise ValueError('Approved font span would split ruby')
            covered = set()
            for atom in re.finditer(r'<span\b(?=[^>]*data-citation-)[^>]*>.*?</span>', raw, re.S):
                indices = [j for j in range(start, end) if projection.mapping[j] is not None and atom.start() <= projection.mapping[j][0] < atom.end()]
                if indices:
                    all_indices = [j for j, pos in enumerate(projection.mapping) if pos is not None and atom.start() <= pos[0] < atom.end()]
                    if indices != all_indices:
                        raise ValueError('Font span splits a semantic citation atom')
                    edits.append((atom.start(), atom.end(), row['font_id']))
                    covered.update(indices)
            for r in ruby:
                if r['start'] in covered:
                    continue
                a = raw.rfind('<ruby', 0, projection.mapping[r['start']][0] + 1)
                b = raw.find('</ruby>', projection.mapping[r['end'] - 1][1]) + 7
                edits.append((a, b, row['font_id']))
                covered.update(range(r['start'], r['end']))
            segments = []
            for index in range(start, end):
                pos = projection.mapping[index]
                if index in covered or pos is None:
                    continue
                if segments and segments[-1][2] == pos[2] and segments[-1][1] == pos[0]:
                    segments[-1] = (segments[-1][0], pos[1], pos[2])
                else:
                    segments.append(pos[:3])
            edits.extend((a, b, row['font_id']) for a, b, _ in segments)
    edits = sorted(set(edits))
    if any(a[1] > b[0] for a, b in zip(edits, edits[1:])):
        raise ValueError('Overlapping approved font spans')
    for start, end, font_id in reversed(edits):
        raw = raw[:start] + '<span data-workbook-font="' + font_id + '" data-document-font-override="true">' + raw[start:end] + '</span>' + raw[end:]
    result = {'html': raw}
    after = Projection(result)
    if after.text != projection.text or after.ruby != projection.ruby:
        raise ValueError('Approved font markup changed content or ruby')
    return result if edits else value


def html_fonts(soup):
    for node in soup.select('[data-workbook-font]'):
        family = macro(node['data-workbook-font'])
        node['style'] = node.get('style', '') + f';font-family:{family};font-weight:400;'
        for child in node.select('.tex-latin,.content-digits'):
            child['style'] = child.get('style', '') + f';font-family:{family};font-weight:400;'

