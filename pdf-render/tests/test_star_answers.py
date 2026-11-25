"""Guard against wrong-slot grading and self-referential/rendition bindings."""
from pathlib import Path
import copy
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'pdf-render/tools'), str(ROOT / 'rubi-restore/tools')]
from star_answers import (decision_binding, question_binding, reconstruct,
                          review_binding, star_position, validate)


def independent_review(q, reviewer, order, *, stage='initial'):
    review = {'method': 'independent_linguistic_review', 'reviewer': reviewer,
              'basis': 'Blindly derived 本を読む人だ.', 'stage': stage,
              'reviewed_order': list(order), 'reviewed_question_sha256': question_binding(q)}
    review['review_binding_sha256'] = review_binding(review)
    return review


def question(position):
    slots = ['_'] * 4
    slots[position - 1] = '<u>★</u>'
    q = {'id': 'q1', 'stem': {'html': '彼は ' + ' '.join(slots) + '。'},
         'options': ['を', '読む', '本', '人だ'], 'key': [3, 1, 2, 4][position - 1]}
    q['star'] = {'order': [3, 1, 2, 4], 'star_position': position,
                 'question_sha256': question_binding(q), 'status': 'verified',
                 'order_evidence': [
                     independent_review(q, name, [3, 1, 2, 4])
                     for name in ('solver', 'reviewer')],
                 'position_evidence': [{'observed_position': position,
                     'source_path': 'src/test.pdf', 'source_sha256': '0' * 64,
                     'physical_page': 1, 'method': 'visual_page_review',
                     'basis': 'Inspected all four printed slots.'}]}
    return q


def accept(q):
    record = q['star']
    record['status'] = 'accepted'
    record['decision'] = {
        'authority': 'user', 'date': '2026-11-11',
        'question_sha256': question_binding(q), 'order': list(record['order']),
        'star_position': record['star_position'], 'key': q['key'],
        'rationale': 'User accepted this answer after reviewing the alternatives.',
        'remaining_uncertainty': 'Historical source key remains disputed.',
        'case_ids': ['test-q1-order']}
    record['decision']['decision_sha256'] = decision_binding(record['decision'])
    return q


class StarAnswers(unittest.TestCase):
    def test_accepted_decision_preserves_dissent_without_claiming_consensus(self):
        q = question(3)
        q['star']['order_evidence'][0] = independent_review(q, 'solver', [1, 3, 2, 4])
        accept(q)
        self.assertEqual(validate(q)['status'], 'accepted')
        self.assertEqual(q['star']['order_evidence'][0]['reviewed_order'], [1, 3, 2, 4])

    def test_accepted_decision_is_required_and_bound_to_exact_answer(self):
        q = accept(question(3))
        del q['star']['decision']
        with self.assertRaises(ValueError):
            validate(q)
        for field, value in [('order', [1, 3, 2, 4]), ('key', 1),
                             ('star_position', 2), ('question_sha256', 'f' * 64)]:
            q = accept(question(3))
            decision = q['star']['decision']
            decision[field] = value
            decision['decision_sha256'] = decision_binding(decision)
            with self.assertRaisesRegex(ValueError, 'differs from published answer'):
                validate(q)

    def test_changed_acceptance_reason_invalidates_decision(self):
        q = accept(question(3))
        q['star']['decision']['rationale'] = 'Changed decision'
        with self.assertRaisesRegex(ValueError, 'editorial decision binding'):
            validate(q)

    def test_acceptance_cannot_bypass_permutation_key_or_question_binding(self):
        for field, value in [('order', [3, 1, 2, 2]), ('order', [3, 2, 1, 4]),
                             ('question_sha256', 'f' * 64)]:
            q = accept(question(3))
            q['star'][field] = value
            with self.assertRaises(ValueError):
                validate(q)

    def test_key_correction_keeps_original_blind_review_hashes(self):
        q = question(3)
        q['key'] = 4  # The inherited key was wrong; blind reviewers still solved it.
        snapshot = {key: copy.deepcopy(q[key]) for key in ('id', 'stem', 'options', 'key')}
        q['star']['order_evidence'] = [independent_review(q, r, [3, 1, 2, 4])
                                     for r in ('solver', 'reviewer')]
        before = copy.deepcopy(q['star']['order_evidence'])
        q['key'] = 2
        q['star']['question_sha256'] = question_binding(q)
        accept(q)
        with self.assertRaisesRegex(ValueError, 'independent review question binding'):
            validate(q)
        for e in q['star']['order_evidence']:
            e['reviewed_question'] = copy.deepcopy(snapshot)
        validate(q)
        for current, original in zip(q['star']['order_evidence'], before):
            self.assertEqual({k: v for k, v in current.items() if k != 'reviewed_question'}, original)

    def test_historical_snapshot_cannot_cover_a_new_linguistic_question(self):
        q = question(3)
        snapshot = {key: copy.deepcopy(q[key]) for key in ('id', 'stem', 'options', 'key')}
        for e in q['star']['order_evidence']:
            e['reviewed_question'] = copy.deepcopy(snapshot)
        q['options'][1] = '買う'
        q['star']['question_sha256'] = question_binding(q)
        accept(q)
        with self.assertRaisesRegex(ValueError, 'historical review snapshot'):
            validate(q)

    def test_spacing_only_preserves_the_original_blind_review(self):
        q = question(3)
        snapshot = {k: copy.deepcopy(q[k]) for k in ('id', 'stem', 'options', 'key')}
        for review in q['star']['order_evidence']:
            review['reviewed_question'] = copy.deepcopy(snapshot)
        q['options'][3] = '人 だ'
        q['star']['question_sha256'] = question_binding(q)
        self.assertEqual(validate(q)['status'], 'verified')
        for incorrect in ['別 だ', '人  だ ', '人\nだ']:
            q['options'][3] = incorrect
            q['star']['question_sha256'] = question_binding(q)
            with self.assertRaisesRegex(ValueError, 'historical review snapshot'):
                validate(q)

    def test_accepted_placement_conflict_is_explicit(self):
        q = accept(question(2))
        q['star']['decision']['authority'] = 'delegated_source_adjudication'
        q['star']['decision']['decision_sha256'] = decision_binding(q['star']['decision'])
        q['star']['position_evidence'][0]['observed_position'] = 3
        validate(q)
        q['star']['position_evidence'][0]['position_scope'] = 'worked_constituent'
        with self.assertRaisesRegex(ValueError, 'question-layout evidence'):
            validate(q)

    def test_decision_does_not_silently_turn_dissent_into_verified_consensus(self):
        q = accept(question(3))
        q['star']['status'] = 'verified'
        with self.assertRaises(ValueError):
            validate(q)

    def test_all_four_positions_use_their_own_key(self):
        for position in range(1, 5):
            q = question(position)
            self.assertEqual(star_position(q['stem']), position)
            self.assertEqual(validate(q)['order'], [3, 1, 2, 4])
            self.assertEqual(reconstruct(q, q['star']['order']), '彼は 本を読む人だ。')

    def test_layout_whitespace_ruby_and_long_underlines(self):
        q = question(2)
        q['stem'] = {'html': '<ruby>彼<rt>かれ</rt></ruby>は ____ <u>★</u><br>＿＿＿ ____。'}
        self.assertEqual(star_position(q['stem']), 2)

    def test_changed_question_invalidates_solution(self):
        for field, value in [('key', 4), ('options', ['を', '買う', '本', '人だ']),
                             ('stem', '別の文 _ _ ★ _。')]:
            q = question(3)
            q[field] = value
            with self.assertRaisesRegex(ValueError, 'Stale STAR'):
                validate(q)

    def test_solution_metadata_is_outside_binding(self):
        q = question(3)
        before = question_binding(q)
        q['star']['order_evidence'].append({'method': 'source_explanation'})
        self.assertEqual(question_binding(q), before)

    def test_wrong_source_position_and_duplicate_fragments_rejected(self):
        q = question(1)
        q['star']['position_evidence'][0]['observed_position'] = 3
        with self.assertRaisesRegex(ValueError, 'source position'):
            validate(q)
        q = question(1)
        q['star']['order'] = [3, 1, 2, 2]
        with self.assertRaises(ValueError):
            validate(q)

    def test_key_agreement_is_checked_after_binding(self):
        q = question(1)
        q['key'] = 2
        q['star']['question_sha256'] = question_binding(q)
        for evidence in q['star']['order_evidence']:
            evidence['reviewed_question_sha256'] = question_binding(q)
            evidence['review_binding_sha256'] = review_binding(evidence)
        with self.assertRaisesRegex(ValueError, 'answer key'):
            validate(q)

    def test_held_question_never_publishes_a_candidate(self):
        q = question(1)
        q['star'].update(status='held', order=None, hold_reason='Conflicting source position')
        validate(q)
        q['star']['order'] = [3, 1, 2, 4]
        with self.assertRaises(ValueError):
            validate(q)

    def test_independent_reviewers_are_required(self):
        q = question(3)
        q['star']['order_evidence'][1]['reviewer'] = 'solver'
        q['star']['order_evidence'][1]['review_binding_sha256'] = review_binding(q['star']['order_evidence'][1])
        with self.assertRaisesRegex(ValueError, 'two independent reviewers'):
            validate(q)

    def test_changed_order_cannot_reuse_old_reviews(self):
        q = question(3)
        q['star']['order'] = [1, 3, 2, 4]  # Keeps the starred answer unchanged.
        with self.assertRaisesRegex(ValueError, 'does not endorse published order'):
            validate(q)

    def test_review_claims_cannot_change_without_rebinding(self):
        for field, value in [('reviewed_order', [1, 3, 2, 4]), ('reviewer', 'replacement'),
                             ('basis', 'A different rationale.'), ('stage', 'post_review')]:
            q = question(3)
            q['star']['order_evidence'][0][field] = value
            with self.assertRaisesRegex(ValueError, 'independent review binding'):
                validate(q)

    def test_rebound_question_cannot_reuse_old_reviews(self):
        q = question(3)
        q['options'][1] = '買う'
        q['star']['question_sha256'] = question_binding(q)
        with self.assertRaisesRegex(ValueError, 'independent review question binding'):
            validate(q)

    def test_post_review_supersedes_initial_judgment(self):
        q = question(3)
        initial = q['star']['order_evidence'][0]
        initial['reviewed_order'] = [1, 3, 2, 4]
        initial['review_binding_sha256'] = review_binding(initial)
        with self.assertRaisesRegex(ValueError, 'does not endorse published order'):
            validate(q)
        q['star']['order_evidence'].append(independent_review(q, 'solver', q['star']['order'], stage='post_review'))
        validate(q)
        self.assertEqual(initial['reviewed_order'], [1, 3, 2, 4])

    def test_post_review_dissent_cannot_fall_back_to_initial_agreement(self):
        q = question(3)
        q['star']['order_evidence'].append(independent_review(q, 'solver', [1, 3, 2, 4], stage='post_review'))
        with self.assertRaisesRegex(ValueError, 'does not endorse published order'):
            validate(q)

    def test_held_question_preserves_bound_contrary_reviews(self):
        q = question(3)
        q['star']['order_evidence'][0] = independent_review(q, 'solver', [1, 3, 2, 4])
        q['star'].update(status='held', order=None, hold_reason='Reviewers disagree')
        validate(q)
        q['star']['order_evidence'][0]['basis'] = 'Edited after the review.'
        with self.assertRaisesRegex(ValueError, 'independent review binding'):
            validate(q)

    def test_raw_record_link_is_separate_from_review_binding(self):
        evidence = question(3)['star']['order_evidence'][0]
        before = review_binding(evidence)
        evidence['record_sha256'] = 'f' * 64
        self.assertEqual(review_binding(evidence), before)
        implicit_stage = copy.deepcopy(evidence)
        del implicit_stage['stage']
        self.assertEqual(review_binding(implicit_stage), before)

    def test_incomplete_source_evidence_is_rejected(self):
        q = question(3)
        del q['star']['position_evidence'][0]['source_sha256']
        with self.assertRaisesRegex(ValueError, 'Invalid STAR record'):
            validate(q)

    def test_source_evidence_accepts_page_locator_or_both(self):
        for status in ('verified', 'held'):
            for location in ({'physical_page': 1}, {'locator': 'printed question 1'},
                             {'physical_page': 1, 'locator': 'top half, printed question 1'}):
                with self.subTest(status=status, location=location):
                    q = question(3)
                    if status == 'held':
                        q['star'].update(status='held', order=None, hold_reason='Pending review')
                    evidence = q['star']['position_evidence'][0]
                    del evidence['physical_page']
                    evidence.update(location)
                    validate(q)

    def test_source_evidence_still_requires_a_valid_location(self):
        for location in ({}, {'physical_page': 0}, {'locator': ''},
                         {'physical_page': 1, 'locator': ''},
                         {'physical_page': 0, 'locator': 'top half'}):
            with self.subTest(location=location):
                q = question(3)
                evidence = q['star']['position_evidence'][0]
                del evidence['physical_page']
                evidence.update(location)
                with self.assertRaisesRegex(ValueError, 'Invalid STAR record'):
                    validate(q)

    def test_held_source_conflict_is_preserved(self):
        q = question(3)
        q['star']['position_evidence'][0]['observed_position'] = 2
        q['star'].update(status='held', order=None, hold_reason='Source position conflicts')
        validate(q)
        self.assertEqual(q['star']['position_evidence'][0]['observed_position'], 2)
        self.assertEqual(q['star']['star_position'], 3)

    def test_held_question_still_requires_current_content_and_reason(self):
        q = question(3)
        q['star'].update(status='held', order=None, hold_reason='   ')
        with self.assertRaisesRegex(ValueError, 'null order and a reason'):
            validate(q)
        q['star']['hold_reason'] = 'Pending review'
        q['options'][1] = '買う'
        with self.assertRaisesRegex(ValueError, 'Stale STAR question binding'):
            validate(q)

    def test_two_stages_from_one_reviewer_are_not_two_reviewers(self):
        q = question(3)
        q['star']['order_evidence'] = [
            independent_review(q, 'solver', q['star']['order'], stage=stage)
            for stage in ('initial', 'post_review')]
        with self.assertRaisesRegex(ValueError, 'two independent reviewers'):
            validate(q)

    def test_conflicting_post_reviews_cannot_be_resolved_by_list_order(self):
        for orders in (([3, 1, 2, 4], [1, 3, 2, 4]),
                       ([1, 3, 2, 4], [3, 1, 2, 4])):
            with self.subTest(orders=orders):
                q = question(3)
                q['star']['order_evidence'].extend(
                    independent_review(q, 'solver', order, stage='post_review') for order in orders)
                with self.assertRaisesRegex(ValueError, 'does not endorse published order'):
                    validate(q)

    def test_missing_or_ambiguous_slots_fail(self):
        for stem in ['_ ★ _', '_ ★ _ ★', '_ _ ★ _ _', '_ x _ ★ _']:
            with self.assertRaises(ValueError):
                star_position(stem)


if __name__ == '__main__':
    unittest.main()
