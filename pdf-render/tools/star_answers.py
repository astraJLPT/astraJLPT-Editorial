"""Content-bound STAR solutions authored in editorial JSON.

The position of the printed star and the linguistic permutation are separate
facts. Neither a conventional third position nor an inherited key supplies the
other fact. Hash only authored question fields, never the solution containing
the hash, or a ruby-enriched display rendition.
"""
import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator

from ruby_core import Projection

QUESTION_FIELDS = ('id', 'stem', 'options', 'key')
REVIEW_FIELDS = ('method', 'reviewer', 'basis', 'reviewed_order',
                'reviewed_question_sha256')
SLOTS = re.compile(r'(?<![_＿])(?:[_＿]+|★|☆)(?![_＿])')


@lru_cache(maxsize=1)
def record_validator():
    schema = Path(__file__).resolve().parents[1] / 'schema/star-answer.schema.json'
    return Draft202012Validator(json.loads(schema.read_text(encoding='utf-8')))


def question_binding(question):
    value = {key: question[key] for key in QUESTION_FIELDS}
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def review_binding(review):
    """Bind an independent judgment, excluding its hash and raw-record link.

    An omitted stage means ``initial``. Post-review evidence is a new judgment;
    retaining the initial record never makes it endorse the revised order.
    """
    value = {key: review[key] for key in REVIEW_FIELDS}
    value['stage'] = review.get('stage', 'initial')
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def decision_binding(decision):
    """Bind an editorial disposition without including its own hash."""
    value = {key: value for key, value in decision.items() if key != 'decision_sha256'}
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def review_content(question):
    """Language shown to blind reviewers; grading is adjudicated separately."""
    text, matches = slot_sequence(question['stem'])
    return (question['id'], text[:matches[0].start()], text[matches[-1].end():],
            tuple(Projection(value).text for value in question['options']))


# Only horizontal separators between Japanese letters are editorial word gaps.
JAPANESE_LETTER = r'[ぁ-ゖァ-ヺー一-龯々〆ヶ]'
WORD_GAP = re.compile(rf'(?<={JAPANESE_LETTER})[ 　]+(?={JAPANESE_LETTER})')


def same_except_word_spacing(previous, current):
    def unspace(value):
        if isinstance(value, dict):
            return {**value, 'html': WORD_GAP.sub('', value['html'])}
        return WORD_GAP.sub('', value)

    return (previous['id'] == current['id'] and previous['key'] == current['key']
            and unspace(previous['stem']) == unspace(current['stem'])
            and [unspace(v) for v in previous['options']]
            == [unspace(v) for v in current['options']])


def slot_sequence(stem):
    """Return exactly four source slots, supporting stars at any position."""
    text = Projection(stem).text
    matches = list(SLOTS.finditer(text))
    if len(matches) != 4 or sum(m.group() in ('★', '☆') for m in matches) != 1:
        raise ValueError('STAR stem must contain exactly four slots and one star')
    # Only whitespace may separate the four slots. A line wrap is whitespace;
    # meaningful text between fragments is a different task, not this contract.
    if any(text[a.end():b.start()].strip() for a, b in zip(matches, matches[1:])):
        raise ValueError('STAR slots must form one contiguous sequence')
    return text, matches


def star_position(stem):
    _, matches = slot_sequence(stem)
    return next(i for i, m in enumerate(matches, 1) if m.group() in ('★', '☆'))


def validate(question, *, require=True):
    record = question.get('star')
    if record is None:
        if require:
            raise ValueError('Missing canonical STAR solution: ' + question['id'])
        return None
    errors = sorted(record_validator().iter_errors(record), key=lambda error: str(error.path))
    if errors:
        raise ValueError('Invalid STAR record for ' + question['id'] + ': ' + errors[0].message)
    position = star_position(question['stem'])
    question_sha256 = question_binding(question)
    if record['question_sha256'] != question_sha256:
        raise ValueError('Stale STAR question binding: ' + question['id'])
    if type(record['star_position']) is not int or record['star_position'] != position:
        raise ValueError('STAR position differs from authored stem: ' + question['id'])
    if len(question['options']) != 4:
        raise ValueError('STAR questions require four option fragments')
    status, order = record['status'], record['order']
    independent_reviews = {}
    for evidence in record['order_evidence']:
        if evidence['method'] != 'independent_linguistic_review':
            continue
        snapshot = evidence.get('reviewed_question')
        spacing_only = snapshot is not None and same_except_word_spacing(snapshot, question)
        if snapshot is not None:
            if (question_binding(snapshot) != evidence['reviewed_question_sha256'] or
                    (not spacing_only and review_content(snapshot) != review_content(question))):
                raise ValueError('Stale STAR historical review snapshot: ' + question['id'])
        if evidence['reviewed_question_sha256'] != question_sha256:
            # Preserve the independently hashed original for a typesetting change
            # or a separately accepted key/slot decision.
            if snapshot is None or (status != 'accepted' and not spacing_only):
                raise ValueError('Stale STAR independent review question binding: ' + question['id'])
        if evidence['review_binding_sha256'] != review_binding(evidence):
            raise ValueError('Stale STAR independent review binding: ' + question['id'])
        independent_reviews.setdefault(evidence['reviewer'], []).append(evidence)
    if status == 'held':
        if order is not None or not record.get('hold_reason', '').strip():
            raise ValueError('Held STAR records need null order and a reason')
        return record
    if status not in ('verified', 'accepted') or not isinstance(order, list) or len(order) != 4:
        raise ValueError('Invalid STAR review status or permutation')
    if any(type(n) is not int for n in order) or sorted(order) != [1, 2, 3, 4]:
        raise ValueError('STAR order must use each option exactly once')
    if order[position - 1] != question['key']:
        raise ValueError('STAR order disagrees with current answer key: ' + question['id'])
    if not record.get('order_evidence') or not record.get('position_evidence'):
        raise ValueError('Verified STAR records need order and position evidence')
    if len(independent_reviews) < 2:
        raise ValueError('Verified STAR records require two independent reviewers')
    if status == 'accepted':
        decision = record['decision']
        if decision['decision_sha256'] != decision_binding(decision):
            raise ValueError('Stale STAR editorial decision binding: ' + question['id'])
        expected = {'question_sha256': question_sha256, 'order': order,
                    'star_position': position, 'key': question['key']}
        if any(decision[key] != value for key, value in expected.items()):
            raise ValueError('STAR editorial decision differs from published answer: ' + question['id'])
        if not any(e.get('position_scope', 'question_blank') == 'question_blank'
                   for e in record['position_evidence']):
            raise ValueError('Accepted STAR record requires question-layout evidence')
        return record
    for reviewer, reviews in independent_reviews.items():
        stage = 'post_review' if any(e.get('stage') == 'post_review' for e in reviews) else 'initial'
        effective = [e for e in reviews if e.get('stage', 'initial') == stage]
        if any(e['reviewed_order'] != order for e in effective):
            raise ValueError('Independent STAR review does not endorse published order: ' + reviewer)
    for evidence in record['position_evidence']:
        if (evidence['observed_position'] != position or
                evidence.get('position_scope', 'question_blank') != 'question_blank'):
            raise ValueError('STAR source position conflicts with authored stem')
    return record


def reconstruct(question, order):
    text, matches = slot_sequence(question['stem'])
    fragments = [Projection(value).text for value in question['options']]
    return text[:matches[0].start()] + ''.join(fragments[n - 1] for n in order) + text[matches[-1].end():]


def validate_document(editorial, *, require=True):
    counts = {'questions': 0, 'verified': 0, 'accepted': 0, 'held': 0}
    for section in editorial['sections']:
        task = editorial['layout']['sections'][section['id']]['task']
        for question in section['items']:
            is_star = task == 'sentence_composition' and 'stem' in question
            if not is_star:
                if 'star' in question:
                    raise ValueError('STAR metadata on a non-STAR question')
                continue
            counts['questions'] += 1
            record = validate(question, require=require)
            if record:
                counts[record['status']] += 1
    return counts
