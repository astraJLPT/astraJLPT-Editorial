"""Current editorial authority. No archived payloads or change-log replay."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def editorial_path(unit):
    from era_registry import for_unit
    for_unit(unit)
    return ROOT / f'editorial-json/{unit[:2]}/{unit}/editorial_{unit}.json'


def payload(editorial):
    version = editorial.get('schema_version')
    if version != '4.1.0':
        raise ValueError('Unsupported current editorial contract')
    if 'sources' in editorial or 'listening_documents' in editorial:
        raise ValueError('The v4 release contains written content without legacy imports')
    result = {key: copy.deepcopy(editorial[key]) for key in
              ('schema_version', 'unit', 'sections')}
    # Solutions are canonical editorial metadata, not printed question fields.
    # Keep them out of aggregate typography/ruby bindings and the native body.
    for section in result['sections']:
        for item in section['items']:
            item.pop('star', None)
    return result


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def value_at(document, pointer):
    value = document
    for key in pointer.strip('/').split('/'):
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def resolve_defaults(path, editorial):
    from package_paths import resource
    target = resource(editorial['defaults']['path'])
    from era_registry import for_editorial
    expected = for_editorial(editorial).defaults(editorial['unit']).resolve()
    if target != expected:
        raise ValueError('Defaults must name the maintained level profile')
    return target


def file_digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
