"""Modern written-paper policy, 2010–2026."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_ROOT = ROOT / 'pdf-render/schema'
GENERATION = 'modern-2010'
SOURCE_TARGET_MARKERS = False
EXTRA_TEX = None


def defaults(unit):
    return SCHEMA_ROOT / unit[:2] / 'defaults.json'


def admit(unit):
    from render_scope import ENTRIES
    if unit not in ENTRIES:
        raise ValueError('Outside admitted modern renderer scope')
    return ENTRIES[unit]


def validate_identity(staged):
    admit(staged['unit'])
    if (staged['exam']['generation'] != GENERATION
            or staged['exam']['historical_level'] != staged['unit'][:2]):
        raise ValueError('Modern exam identity mismatch')
    from h28_identity import SAMPLES, validate_publication
    publication = staged['provenance'].get('publication_identity', {})
    if staged['unit'] in SAMPLES or publication.get('kind') in ['sample', 'practice_set']:
        validate_publication(staged['unit'], publication)


def scope_binding():
    from render_scope import SCOPE, SCOPE_PATH
    from current_editorial import file_digest
    return {'id': SCOPE['scope_id'], 'path': SCOPE_PATH.relative_to(ROOT).as_posix(),
            'sha256': file_digest(SCOPE_PATH)}


def validate_style(staged, style):
    from typography_policy import validate
    validate(staged, style)


def finish_model(model, staged):
    if model['coverage'] == 'partial_available_written':
        if (model['unit'] != 'N3_07_2026' or model['preservation']['question_count'] != 20
                or set(model['tasks'].values()) - {'reading_test', 'orthography_test', 'vocabulary', 'grammar', 'sentence_composition'}):
            raise ValueError('Outside the exact authorized partial recovery')
        model['partial_warning'] = 'Partial practice: six vocabulary and fourteen grammar questions, plus one recovered worked example. No recovered reading passages. Original numbering gaps and uncertainty retained.'


def identity(unit, witness=None, edition=None):
    from modern_public_output import identity as resolve
    return resolve(unit, witness, edition)


def presentation(unit, evidence):
    from modern_presentation import source_binding
    return source_binding(unit, evidence)


def running_matter(model):
    from modern_running_matter import resolve
    return resolve(model)


def target_groups(model):
    return {}, set()


def assemble(model, body_path, target, work, environment):
    """Complete the era adapter used by the maintained isolated native runner."""
    from assemble import assemble as assemble_native
    return assemble_native(model, body_path, target, work, environment)
