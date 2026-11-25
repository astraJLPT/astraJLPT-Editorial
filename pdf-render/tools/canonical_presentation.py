"""Exact canonical-text evidence for inferred presentation, without scan claims."""
from pathlib import Path
from model import ROOT, Projection, digest, file_hash, read


def verify(unit, evidence):
    fields={'question_soft_wrap':'stem','native_notice_range':'content','current_text_roles':'content'}
    field=fields.get(evidence.get('role'))
    if (evidence.get('kind') != 'current_semantic_role_v2'
            or evidence.get('state') != 'inferred'
            or evidence.get('historical_claim') is not False
            or field is None
            or not evidence.get('reason')
            or evidence.get('field') != '/'+field
            or any(k in evidence for k in ('physical_pages', 'source_path', 'source_sha256'))):
        raise ValueError('Invalid canonical-only presentation evidence')
    expected = ROOT/'editorial-json'/unit[:2]/unit/('editorial_'+unit+'.json')
    binding = evidence['canonical']
    if set(binding)!={'path'} or __import__('package_paths').resource(binding['path']) != expected.resolve():
        raise ValueError('Stale canonical presentation input')
    doc = read(expected)
    items = [i for s in doc['sections'] for i in s['items'] if i['id'] == evidence['item_id']]
    if (doc['unit'] != unit or len(items) != 1 or field not in items[0]
            or digest(items[0][field]) != evidence['value_sha256']):
        raise ValueError('Stale canonical presentation field')
    return True
