"""Old-Level 1–4 contract for 1991–2009 and the exact admitted N4_1990 owner."""
import copy
import json
import re
from pathlib import Path

from reference_approvals import REGISTRY, approved_reference, sha, registry_sha

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_ROOT = ROOT / 'pdf-render/schema/historical-1991-2009'
SCOPE_PATH = ROOT / 'pdf-render/config/historical_scope.json'
GENERATION = 'historical-1991-2009'
SOURCE_TARGET_MARKERS = True
EXTRA_TEX = ROOT / 'pdf-render/tex/historical-2009.tex'


def read(path):
    return json.loads(path.read_text('utf-8-sig'))


def scope():
    value = read(SCOPE_PATH)
    units = value['units']
    if (value.get('scope_id') != 'historical-1991-2009-written'
            or len(units) != len(set(units)) or list(value['admitted']) != units):
        raise ValueError('Invalid historical admission scope')
    for unit in units:
        match = re.fullmatch(r'N([1-4])_(?:(07|12)_)?(199[1-9]|200[0-9])', unit)
        if not match and unit != 'N4_1990':
            raise ValueError('Historical admission outside era')
        level, month, year = match.groups() if match else ('4', None, '1990')
        entry = value['admitted'][unit]
        if (entry.get('status') != 'admitted' or entry['historical_level'] != level + '級'
                or entry['sitting']['year'] != int(year)
                or (month and entry['sitting']['month'] != int(month))):
            raise ValueError('Invalid historical admission identity')
    return value


def entry(unit):
    value = scope()
    if unit not in value['admitted']:
        raise ValueError('Historical paper has not passed admission')
    result = value['admitted'][unit]
    if not __import__('release_contract').verify_source(result['source_path'],result['source_sha256']):
        raise ValueError('Historical witness changed')
    return result


def defaults(unit):
    entry(unit)
    return SCHEMA_ROOT / f'level{unit[1]}/defaults.json'


admit = entry


def validate_identity(staged):
    admitted = entry(staged['unit'])
    if (staged['exam']['generation'] != GENERATION
            or staged['exam']['historical_level'] != admitted['historical_level']):
        raise ValueError('Historical exam identity mismatch')
    witness = staged['provenance']['source_witness']
    if any(witness.get(k) != admitted[k] for k in ['source_path', 'source_sha256']):
        raise ValueError('Unbound historical source')
    if 'booklets' in staged['layout']:
        raise ValueError('Old covers use historical_booklets; Modern booklet metadata is unsupported')
    if 'historical_booklets' in staged['layout']:
        from historical_booklets import validate
        validate(staged)
    from historical_listening import validate_editorial_components
    validate_editorial_components(staged)


def scope_binding():
    return {'id': scope()['scope_id'], 'path': SCOPE_PATH.relative_to(ROOT).as_posix(), 'sha256': sha(SCOPE_PATH)}


def validate_style(staged, style):
    # Dimensions and fonts are checked against this era's defaults schema by the
    # common resolver. Further size policy belongs here, independent of modern.
    validate_identity(staged)


def coverage_warning(model):
    recovery = entry(model['unit']).get('partial_recovery')
    if recovery is None:
        if model['coverage'] != 'whole_available_written':
            raise ValueError('Unadmitted historical partial coverage')
        return None
    if model['coverage'] != 'partial_available_written':
        raise ValueError('Historical partial coverage cannot be relabeled complete')
    expected = recovery['question_ids']
    actual = {part: [i['id'] for s in model['document']['sections'] if s['part'] == part
                     for i in s['items'] if 'stem' in i] for part in expected}
    all_ids = [i['id'] for s in model['document']['sections'] for i in s['items'] if 'stem' in i]
    examples = sum(i.get('type') == 'example' for s in model['document']['sections'] for i in s['items'])
    if (actual != expected or sum(map(len, expected.values())) != len(all_ids)
            or examples != recovery['worked_examples'] or not recovery.get('warning')):
        raise ValueError('Historical partial recovery differs from reviewed question coverage')
    return recovery['warning']


def finish_model(model, staged):
    model['exam'] = copy.deepcopy(staged['exam'])
    model['partial_warning'] = coverage_warning(model)
    model['selected_component'] = 'written'
    model['available_components'] = ['written']


def identity(unit,witness=None,edition=None):
    from release_contract import identity as resolve
    return resolve(unit,witness,edition)


def presentation(unit, evidence):
    admitted = entry(unit)
    witnesses = [admitted, *admitted.get('presentation_witnesses', [])]
    matched = [w for w in witnesses if all(evidence.get(k) == w[k] for k in ['source_path', 'source_sha256'])]
    if len(matched) != 1:
        raise ValueError('Unbound historical presentation witness')
    witness = matched[0]
    if not __import__('release_contract').verify_source(witness['source_path'],witness['source_sha256']):
        raise ValueError('Historical witness changed')
    if evidence.get('historical_claim') is not False or not evidence.get('region'):
        raise ValueError('Historical presentation requires an exact region and bounded claim')
    pages = evidence.get('physical_pages', [])
    if (not pages or any(type(p) is not int for p in pages) or len(pages) != len(set(pages))
            or any(p not in witness['question_pages'] for p in pages)):
        raise ValueError('Outside reviewed historical question pages')
    for page in pages:
        if str(page) in witness.get('mixed_page_regions', {}) and evidence['region'] != witness['mixed_page_regions'][str(page)]:
            raise ValueError('Mixed page requires its exact written region')
    if evidence.get('state') == 'inferred':
        return None  # Existing inferred choices do not become approved automatically.
    approved = approved_reference(witness)
    if (evidence.get('state') != 'approved' or approved is None
            or evidence.get('reference_id') != approved['reference_id']
            or evidence.get('approval_registry_sha256') != approved['approval_registry']['sha256']
            or evidence.get('subject') != 'question_page_layout'
            or evidence.get('exclusions_acknowledged') is not True
            or not set(pages) <= set(approved['approved_physical_pages'])):
        raise ValueError('Historical presentation lacks exact approved file/page authority')
    return approved


def running_matter(model):
    admitted = entry(model['unit'])
    date = admitted['sitting']
    labels = {'vocabulary': '文', 'reading_grammar': '読'}
    booklets = {s['booklet'] for s in model['layout']['sections'].values()}
    if booklets - set(labels):
        raise ValueError('Unsupported historical booklet')
    level = {'1級':'I','2級':'II','3級':'III','4級':'IV'}[admitted['historical_level']]
    prefix = f"{date['year'] % 100:02} - {level}"
    return {'booklet_prefixes': {b: prefix + ' - ' + labels[b] for b in sorted(booklets)},
            'page_number': 'renderer_booklet', 'basis': 'inferred_metadata_prefix_generated_page',
            'evidence': {'authority': 'admitted historical source title', 'historical_claim': False,
                         'identity_basis': 'H21 user-selected YY - old Roman level - 文/読 convention, ASCII separators, generated booklet folio; full sitting remains in cover/metadata.'}}


def target_groups(model):
    from historical_groups import collect
    return collect(model)


def assemble(model, diagnostic, target, work, environment):
    from historical_cover import assemble as render_cover
    return render_cover(model, diagnostic, target, work, environment)


# Compatibility for already-authored diagnostics. New admission is an explicit
# preparation edit to the maintained scope, never a side effect of discovery.
UNITS = tuple(read(SCOPE_PATH)['units'])
