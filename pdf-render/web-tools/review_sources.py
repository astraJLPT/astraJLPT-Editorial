"""Bind review scores and source links to a file or an explicit written set."""
from pathlib import Path
import json
from functools import lru_cache


def assessment(m, entry):
    from package_paths import source_identity
    witness = m['input']
    result = dict(entry or {})
    source_set = result.get('principal_source_set', {})
    bound = ((source_identity(result.get('principal_path')), result.get('principal_sha256')) == (witness['source_path'], witness['source_sha256'])
             or (source_identity(source_set.get('manifest_path')), source_set.get('manifest_sha256')) == (witness['source_path'], witness['source_sha256']))
    if not bound or result.get('review_status') != 'complete_written_review':
        result['uncertainty_index'] = None
        result['web_assessment_note'] = 'Unassessed for the selected source; missing or unmatched review evidence is not a zero-concern score.'
    result['principal_path'] = witness['source_path']
    result['principal_sha256'] = witness['source_sha256']
    return result


def members(m):
    return [{'witness_id': r['witness_id'], **r['principal'], 'pages': r['written_body_physical_pages']}
            for r in m['input'].get('source_set_members', [])]


def bundle(m,hub,copy,sha):
    from package_paths import BASE,ROOT
    assets=json.loads((BASE/'contracts/principal-assets.json').read_text('utf-8'))[m['unit']]
    links={'default':'../'+assets[0]['path']}
    for asset in assets:
        target=ROOT/'astraJLPT'/asset['path']
        if not target.is_file():target=ROOT/'additional-assets/principals'/Path(asset['path']).name
        if sha(target)!=asset['sha256']:raise ValueError('Changed packaged principal')
        links[asset['role']]='../'+asset['path']
    for member in members(m):
        match=next(a for a in assets if a['sha256']==member['sha256'])
        links[member['path']]=links[member['witness_id']]='../'+match['path']
    m['web_principal_assets']=assets
    return assets[0]['path'],links
