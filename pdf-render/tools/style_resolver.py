"""Versioned shared -> level -> explicit variant -> unit style resolution."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / 'pdf-render/schema'


def merge(base, override):
    """Merge nonempty objects; explicit {}, [], false and null replace a node."""
    if not isinstance(base, dict) or not isinstance(override, dict):
        return copy.deepcopy(override)
    result = copy.deepcopy(base)
    for key, value in override.items():
        result[key] = merge(result[key], value) if value and isinstance(value, dict) and isinstance(result.get(key), dict) else copy.deepcopy(value)
    return result


def leaves(value, prefix=()):
    if isinstance(value, dict) and value:
        for key, child in value.items():
            yield from leaves(child, prefix + (key,))
    else:
        yield prefix, value


def select_variants(shared, profile, staged):
    # A unit selection replaces the level selection, including an explicit [].
    selected = staged['style_variants'] if 'style_variants' in staged else profile.get('style_variants', [])
    if not isinstance(selected, list) or any(not isinstance(key, str) for key in selected):
        raise ValueError('Selected style variants must be a list of identifiers')
    if len(selected) != len(set(selected)):
        raise ValueError('Duplicate selected style variant')
    variants = shared.get('variants', {})
    rows = []
    year = int(staged['unit'][-4:])
    for key in selected:
        if key not in variants:
            raise ValueError('Unknown selected style variant: ' + key)
        v = variants[key]
        a = v['applicability']
        if staged['exam']['historical_level'] not in a['levels'] or staged['exam']['generation'] not in a['generations']:
            raise ValueError('Inapplicable style variant: ' + key)
        if not a.get('year_min', 0) <= year <= a.get('year_max', 9999):
            raise ValueError('Style variant outside period: ' + key)
        if type(v['priority']) is not int:
            raise ValueError('Variant priority must be an integer')
        rows.append((v['priority'], key, v['renderer_conventions']))
    # Equal-priority writes to the same node or its parent/child are rejected,
    # even when values happen to agree. Order in JSON never decides a conflict.
    for index, (priority, key, patch) in enumerate(rows):
        for other_priority, other_key, other_patch in rows[:index]:
            if priority != other_priority:
                continue
            for path, _ in leaves(patch):
                for other_path, _ in leaves(other_patch):
                    if path[:len(other_path)] == other_path or other_path[:len(path)] == path:
                        raise ValueError(f'Conflicting variants {other_key} / {key} at equal priority')
    return sorted(rows, key=lambda row: (row[0], row[1]))


def resolve(profile_path, profile, staged):
    from era_registry import for_editorial
    era = for_editorial(staged)
    ref = profile.get('shared_defaults')
    shared = {'renderer_conventions': {}, 'variants': {}}
    identity = None
    if ref is not None:
        path = (Path(profile_path).parent / ref['path']).resolve()
        if path != (era.SCHEMA_ROOT / 'shared/defaults.json').resolve():
            raise ValueError('Shared defaults outside maintained shared directory')
        shared = json.loads(path.read_text(encoding='utf-8'))
        if (ref['shared_id'], ref['revision']) != (shared['shared_id'], shared['revision']):
            raise ValueError('Shared defaults identity/revision mismatch')
        identity = {'id': shared['shared_id'], 'revision': shared['revision'], 'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    style = merge(shared['renderer_conventions'], profile['renderer_conventions'])
    rows = select_variants(shared, profile, staged)
    for _, _, patch in rows:
        style = merge(style, patch)
    style = merge(style, staged.get('render_overrides', {}))
    # Validate the resolved dimensions as well as the sparse profile. A null
    # remains null and fails here; it cannot disappear into a fallback.
    import jsonschema
    contract = json.loads((era.SCHEMA_ROOT / 'defaults.schema.json').read_text(encoding='utf-8'))
    resolved_profile = {**profile, 'renderer_conventions': style}
    resolved_profile.pop('shared_defaults', None)
    jsonschema.validate(resolved_profile, contract)
    for settings in list(style.get('block_styles',{}).values()) + [t for tables in style.get('table_styles',{}).values() for t in tables.values()]:
        family=settings.pop('typography_family',None)
        if family is None:continue
        if 'body_pt' in settings or 'baseline_pt' in settings:raise ValueError('Shared typography family conflicts with local size')
        if family=='memo':typography=style['memo_typography']
        else:
            prefix={'notice':'notice_','table':'table_','body':''}[family]
            typography={key:style[prefix+key] for key in ['body_pt','baseline_pt']}
        settings.update(typography)
    return style, identity, [{'id': key, 'priority': priority} for priority, key, _ in rows]
