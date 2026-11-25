"""Evidence-based public PDF identity, independent of the ruby render edition.

Only the Approved files table confers scan approval. A selected witness, a
filename, old model publication=None or a rejected-file mention does not.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'pdf-render'
APPROVAL = ROOT / 'editorial-json/user_approved_reference_scans.md'
PUBLICATIONS = ROOT / 'editorial-json/publication_registry.json'


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def sha(p):
    with Path(p).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def binding(p):
    return {'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p)}


def approved_paths(text):
    """Do not accidentally parse rejected candidates or audit/departure links."""
    if text.count('## Approved files') != 1:
        raise ValueError('Missing or ambiguous approved-file table')
    section = text.split('## Approved files', 1)[1].split('\n## ', 1)[0]
    result = {}
    for unit, source in re.findall(r'^\|\s*(N[1-5]_\d{2}_\d{4})\s*\|.*?\]\(<([^>]+)>\)', section, re.M):
        p = Path(source)
        if p.is_absolute():
            if not p.is_relative_to(ROOT):
                raise ValueError('Approved source outside the workspace')
            source = p.relative_to(ROOT).as_posix()
        if unit in result:
            raise ValueError('Duplicate scan approval for ' + unit)
        result[unit] = source
    return result


def classify(unit, witness, publications, approvals):
    """Pure classifier. approvals are exact path/hash/page records, never labels."""
    if not re.fullmatch(r'N[1-5]_\d{2}_\d{4}', unit):
        raise ValueError('Invalid immutable unit identity')
    owned = [p for p in publications if p.get('content_unit') == unit and p.get('content_kind') == 'workbook']
    if len(owned) > 1:
        raise ValueError('Ambiguous workbook ownership')
    if any(unit in p.get('legacy_aliases', []) for p in publications):
        raise ValueError('A historical alias cannot become a public content owner')
    if owned:
        p = owned[0]
        if not p.get('publication_id') or not isinstance(p.get('publication_year'), int) or not p.get('canonical_content_revision'):
            raise ValueError('Incomplete workbook identity')
        return {'class': 'workbook', 'basis': 'registered_workbook_owner',
                'publication': {'kind': 'workbook', 'publication_id': p['publication_id'],
                                'year': p['publication_year'], 'title': p['title']}}
    approved = approvals.get(unit)
    if approved and witness.get('source_path') == approved['path']:
        if witness.get('source_sha256') != approved['sha256']:
            raise ValueError('Approved source hash differs from the bound witness')
        pages = approved.get('written_physical_pages')
        if not pages or any(type(n) is not int or n < 1 for n in pages) or len(set(pages)) != len(pages):
            raise ValueError('Approval requires an exact nonempty physical-page scope')
        if unit == 'N2_07_2018' and not set(pages) <= (set(range(2, 10)) | set(range(11, 30))):
            raise ValueError('N2 July 2018 forbidden or unapproved source page')
        return {'class': 'base', 'basis': 'user_approved_exact_reference', 'approved_reference': approved}
    return {'class': 'restored', 'basis': 'no_approved_exact_reference',
            'historical_appearance': 'editorial_restoration_not_authenticated'}


def identity(unit, witness=None, edition=None):
    from era_registry import for_unit
    return for_unit(unit).identity(unit, witness, edition)


def paths(unit):
    result = identity(unit)
    return BASE / result['complete_path'], BASE / result['body_path']


def validate_paths(model):
    expected = identity(model['unit'], model['input'], model['edition'])
    if model.get('public_output') != expected:
        raise ValueError('Stale or missing public-output evidence')
    for field, key in [('output', 'complete_path'), ('body_output', 'body_path')]:
        if model[field]['path'] != expected[key]:
            raise ValueError('Incorrect public path: ' + model[field]['path'])
    return expected


