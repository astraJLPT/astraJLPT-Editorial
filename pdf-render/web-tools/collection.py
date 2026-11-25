"""Explicit website collection and exact release/edition selection."""
import calendar
import hashlib
import json
import re
from pathlib import Path
from public_paths import RENAMED, approved_transition, publication as workbook_publication

PATH = Path(__file__).resolve().parents[1] / 'web-src/collection.json'
MODERN = 'modern-2010'
HISTORICAL = 'historical-1991-2009'


def modern_unit(unit, first=2010, last=2026):
    match = re.fullmatch(r'N[1-5]_(07|12)_(\d{4})', unit)
    return bool(match and first <= int(match[2]) <= last)


def sample_unit(unit):
    return bool(re.fullmatch(r'N[1-5]_sample_2009', unit))


def load():
    from release_contract import contract
    config=json.loads(PATH.read_text('utf-8'))
    included={row['unit'] for row in config['units'] if row['status']=='included'}
    if included!=set(contract()['owners']):raise ValueError('Collection differs from accepted written roster')
    return config


CONFIG = load()
ENTRIES = {r['unit']: r for r in CONFIG['units']}
RETAINED = tuple(r['unit'] for r in CONFIG['units'] if r['status']=='included')
# Keep the original catalog font profile stable as the collection grows.
PILOTS = ('N1_07_2026', 'N2_07_2026', 'N3_07_2026')
UNITS = tuple(u for u in PILOTS if ENTRIES[u]['status'] == 'included') + tuple(
    r['unit'] for r in CONFIG['units'] if r['status'] == 'included' and r['unit'] not in PILOTS)


def release_for(unit, releases):
    entry = ENTRIES[unit]
    matches = [r for r in releases if r['unit'] == unit and r.get('internal_render_edition', r['edition']) == entry['edition']
               and r['pdf'] == entry['release_pdf'] and r['sha256'] == entry['release_sha256']]
    if len(matches) != 1:
        raise ValueError('Missing, ambiguous or changed selected PDF release: ' + unit)
    return matches[0]


def date_info(unit):
    row = ENTRIES.get(unit)
    if row:
        generation, level, date = row['generation'], row['public_level'], row['sitting']
        if row['content_kind']=='practice_set':
            return {'generation':generation, 'content_kind':'practice_set', 'level':level, 'catalog_level':level,
                    'year':row['legacy_sitting']['year'], 'month':row['legacy_sitting']['month'],
                    'sitting':row['catalog_title'], 'publication':row['publication'],
                    'legacy_sitting':row['legacy_sitting']}
        if row['content_kind']=='workbook':
            p=row['publication']
            return {'generation':generation,'content_kind':'workbook','level':level,'catalog_level':level,
                    'year':p['year'],'month':None,'sitting':str(p['year'])+' · '+p['title'],
                    'publication':p,'legacy_sitting':row['legacy_sitting']}
        if row['content_kind'] == 'sample':
            return {'generation': generation, 'content_kind': 'sample', 'level': level, 'catalog_level': level,
                    'year': row['publication']['year'], 'month': None, 'sitting': '2009 official sample',
                    'publication': row['publication']}
    elif modern_unit(unit):
        level, month, year = unit.split('_')
        generation, date = MODERN, {'month': int(month), 'year': int(year)}
    else:
        raise ValueError('No authoritative sitting: ' + unit)
    return {'generation': generation, 'content_kind': 'historical' if generation == HISTORICAL else 'calendar',
            'level': level, 'catalog_level': 'old-' + unit[1] if generation == HISTORICAL else level,
            **date, 'sitting': calendar.month_name[date['month']] + ' ' + str(date['year'])}


def validate_identity(unit,m):
    from release_contract import owner
    expected=owner(unit)
    if m['public_output']['class']!=expected['public_output']['class'] or m['preservation']['question_count']!=expected['question_count']:
        raise ValueError('Changed accepted public identity or question count')
    if m.get('selected_component','written')!='written':raise ValueError('Written components only')


def domains(m):
    tasks = set(m['tasks'].values())
    return [label for group, label in [({'kanji_reading','reading_test','orthography_test','orthography','word_formation','context','paraphrase','usage','vocabulary'}, 'Vocabulary'),
                                      ({'grammar','sentence_composition','cloze'}, 'Grammar'),
                                      ({'reading','paired_reading','information_retrieval'}, 'Reading')] if tasks & group]
