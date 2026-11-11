"""Explicit Old listening components; no audio or automatic option defaults."""
import copy
import hashlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator, ValidationError
from historical_listening_contract import OWNERS, schema

ROOT = Path(__file__).resolve().parents[2]
SCOPE = ROOT / 'pdf-render/config/historical_listening_scope.json'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def bound_file(ref, area):
    value = ref['path']
    if not isinstance(value,str) or '\\' in value:
        raise ValueError('Document paths must be root-relative POSIX paths')
    path = Path(value)
    if path.is_absolute() or any(p in ('.','..') or p.lower()=='zdiamond_scans' for p in path.parts):
        raise ValueError('Unsafe document path')
    if not path.is_relative_to(Path(area)):
        raise ValueError('Document path outside its owned area')
    target = ROOT
    for part in path.parts:
        target /= part
        if target.is_symlink() or target.is_junction():
            raise ValueError('Linked document input is forbidden')
    if not target.is_file() or sha(target)!=ref['sha256']:
        raise ValueError('Stale or missing document source/asset')
    return target


def unique(rows, label):
    ids = [r['id'] for r in rows]
    if len(ids)!=len(set(ids)):
        raise ValueError('Duplicate '+label+' ID')
    return dict(zip(ids,rows))


def _locator(locator,sources,allowed_roles=None):
    if locator['source_id'] not in sources:
        raise ValueError('Unknown listening source')
    source = sources[locator['source_id']]
    if allowed_roles is not None and source['role'] not in allowed_roles:
        raise ValueError('Script/key evidence cannot supply question layout')
    if not locator['physical_pages'] and not locator.get('extraction_pointer'):
        raise ValueError('Non-paginated evidence needs an exact extraction pointer')
    return source


def _admissions(unit,sources):
    if not SCOPE.is_file():
        raise ValueError('Listening component mappings have not been admitted')
    scope = json.loads(SCOPE.read_text('utf-8-sig'))
    if scope.get('scope_id')!='historical-listening-documents-h22' or scope.get('owners')!=OWNERS:
        raise ValueError('Unexpected listening owner admission scope')
    admitted = scope.get('admitted',{}).get(unit)
    if admitted is None:
        raise ValueError('Listening source/page mapping has not been admitted')
    by_source = {}
    from reference_approvals import approved_reference
    for source in sources.values():
        bound_file(source,'src')
        if source['role']=='question_layout':
            matches = [w for w in admitted['question_witnesses']
                       if (w['source_path'],w['source_sha256'])==(source['path'],source['sha256'])]
            if len(matches)!=1 or source['authority']!='uars_question_layout':
                raise ValueError('Unadmitted listening question witness')
            witness=matches[0];approval=approved_reference(witness)
            if not approval or not set(witness['question_pages'])<=set(approval['approved_physical_pages']):
                raise ValueError('Listening question mapping exceeds exact UARS authority')
            by_source[source['id']]=witness
        elif source['role']=='script_content' and source['authority'] not in ('published_script','transcript_copy'):
            raise ValueError('A script source must state its actual content authority')
        elif source['role']=='answer_key' and source['authority']!='answer_key':
            raise ValueError('Answer key requires its own evidence role')
    return by_source


def validate_documents(unit,documents,check_files=True):
    try:
        Draft202012Validator(schema()).validate(documents)
    except ValidationError as exc:
        raise ValueError('Invalid listening contract at /'+'/'.join(map(str,exc.absolute_path))+': '+exc.message) from exc
    if unit not in OWNERS:
        raise ValueError('Listening documents are outside the ten admitted H22 owners')
    sources=unique(documents['sources'],'source');inventory=unique(documents['inventory'],'question')
    admissions=_admissions(unit,sources) if check_files else None
    global_ids=set(inventory)
    def evidence(locators,roles=None,question=False):
        for loc in locators:
            source=_locator(loc,sources,roles)
            if check_files and question:
                witness=admissions[loc['source_id']]
                if not set(loc['physical_pages'])<=set(witness['question_pages']):
                    raise ValueError('Outside admitted listening question pages')
                for page in loc['physical_pages']:
                    region=witness.get('mixed_page_regions',{}).get(str(page))
                    if region is not None and loc['region']!=region:
                        raise ValueError('Mixed listening page requires its exact approved region')
    group_numbers=set()
    for question in inventory.values():
        key=(question['group'],question['kind'],question['number'])
        if key in group_numbers:raise ValueError('Duplicate listening group/question number')
        group_numbers.add(key)
        if question['printed_state'] in ('none','unrecovered') and question['printed_options']:
            raise ValueError('Absent printed options cannot be invented')
        evidence(question['evidence'])
    scored={k for k,q in inventory.items() if q['kind']=='scored'}
    for name,component in [('questions',documents['questions']),('script',documents['script'])]:
        question_component=name=='questions'
        if component['id']!=unit+':'+component['kind']:
            raise ValueError('Listening component has another owner identity')
        pages=unique(component['pages'],'page');emitted=set();dialogues=set()
        for page in pages.values():
            if page['id'] in global_ids:raise ValueError('Duplicate listening document ID')
            global_ids.add(page['id'])
            evidence(page['evidence'],{'question_layout'} if question_component else None,question_component)
            for block in page['blocks']:
                if block['id'] in global_ids:raise ValueError('Duplicate listening block ID')
                global_ids.add(block['id'])
                if not set(block['question_ids'])<=set(inventory):raise ValueError('Unmapped listening question ID')
                if block['kind'] not in ('blank','editorial_note') and not block['evidence']:
                    raise ValueError('Printed/source content needs evidence')
                roles={'question_layout'} if question_component else {'script_content'} if block['kind']=='dialogue' else {'answer_key','script_content'} if block['kind']=='answer' else None
                evidence(block['evidence'],roles,question_component)
                if block['kind']!='editorial_note':emitted.update(block['question_ids'])
                if block['kind']=='dialogue':dialogues.update(block['question_ids'])
                if block['kind']=='figure' and check_files:
                    asset_path=bound_file(block['asset'],'preprocess/assets')
                    if asset_path.suffix.lower()=='.json':
                        from historical_listening_artwork import load
                        load(block['asset'])
                    provenance=json.loads(bound_file(block['asset']['provenance'],'preprocess/assets').read_text('utf-8-sig'))
                    if provenance['asset_sha256']!=block['asset']['sha256']:
                        raise ValueError('Figure provenance names different pixels')
                    candidates=[sources[e['source_id']]for e in block['evidence']
                                if provenance['physical_page'] in e['physical_pages']]
                    if not any((s['path'],s['sha256'])==(provenance['source_path'],provenance['source_sha256'])for s in candidates):
                        raise ValueError('Figure extraction differs from block evidence')
        coverage=component['coverage'];available=set(coverage['available_scored_ids']);reviewed=set(coverage['reviewed_scored_ids']);missing=set(coverage['known_missing_ids'])
        if not reviewed<=available<=scored or not missing<=scored or available&missing:
            raise ValueError('Invalid listening coverage denominator or overlap')
        expected=emitted&scored if question_component else dialogues&scored
        if available!=expected:raise ValueError('Available listening coverage differs from emitted content')
        total=coverage['known_total_scored']
        if total is not None and total!=len(scored):raise ValueError('Known scored inventory total differs')
        if total is None and not coverage['unknown_extent']:raise ValueError('Unknown total cannot imply known coverage')
        if coverage['state']=='complete_available' and (missing or coverage['unknown_extent'] or available!=scored):
            raise ValueError('Incomplete listening component cannot be relabeled complete')
        gaps=unique(component['gaps'],'gap')
        gap_ids=set()
        for gap in gaps.values():
            if not set(gap['question_ids'])<=set(inventory):raise ValueError('Gap has unknown listening question IDs')
            gap_ids.update(gap['question_ids']);evidence(gap['source_attempts'])
        if not missing<=gap_ids or (coverage['unknown_extent'] and not gaps):
            raise ValueError('Missing/unknown listening material needs an exact gap record')
    return documents


def validate_editorial_components(editorial):
    if editorial.get('schema_version')!='4.1.0':
        raise ValueError('Unsupported historical written contract')
    if editorial.get('exam',{}).get('generation')!='historical-1991-2009':
        raise ValueError('Historical components are for Old owners only')
    if 'listening_documents' in editorial:
        raise ValueError('Listening is outside the v4 release package')


