"""The reader consumes source-bound editorial solutions for every star slot."""
import copy
import hashlib
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'pdf-render/web-tools'), str(ROOT / 'pdf-render/tools'),
               str(ROOT / 'rubi-restore/tools')]
from test_star_answers import question
from web_star import star_data
from web_assets import version_resources


def model(position):
    q = question(position)
    record = q.pop('star')
    return {'unit': 'N1_test', 'canonical_editorial': {'sections': [{'items': [q]}]},
            'document': {'sections': [{'id': 's1', 'items': [copy.deepcopy(q)]}]},
            'tasks': {'s1': 'sentence_composition'}, 'star_answers': {'q1': record},
            'input': {'editorial_sha256': '1' * 64}}


class WebStar(unittest.TestCase):
    def test_every_position_and_no_sidecar_argument(self):
        for position in range(1, 5):
            result = star_data([model(position)])['N1_test:q1']
            self.assertEqual(result['star_slot'], position)
            self.assertEqual(result['order'][position - 1], result['key'])
            self.assertEqual(result['reconstructed_sentence'], '彼は 本を読む人だ。')

    def test_display_ruby_does_not_invalidate_authored_binding(self):
        m = model(3)
        m['document']['sections'][0]['items'][0]['options'][2] = {'html': '<ruby>本<rt>ほん</rt></ruby>'}
        result = star_data([m])['N1_test:q1']
        self.assertEqual(result['fragments'][2], '本')
        self.assertEqual(result['question_binding'], m['star_answers']['q1']['question_sha256'])

    def test_changed_display_fragment_is_rejected(self):
        m = model(3)
        m['document']['sections'][0]['items'][0]['options'][2] = '漫画'
        with self.assertRaisesRegex(ValueError, 'display content differs'):
            star_data([m])

    def test_held_question_has_no_published_solution(self):
        m = model(3)
        m['star_answers']['q1'].update(status='held', order=None, hold_reason='Key conflict')
        result = star_data([m])['N1_test:q1']
        self.assertIsNone(result['order'])
        self.assertIsNone(result['reconstructed_sentence'])

    def test_missing_record_cannot_silently_fall_back(self):
        m = model(3)
        m['star_answers'].clear()
        with self.assertRaisesRegex(ValueError, 'Missing canonical STAR'):
            star_data([m])

    def test_changed_order_cannot_publish_with_stale_reviews(self):
        m = model(3)
        m['star_answers']['q1']['order'] = [1, 3, 2, 4]
        with self.assertRaisesRegex(ValueError, 'does not endorse published order'):
            star_data([m])


class ResourceVersions(unittest.TestCase):
    def test_new_and_existing_versions_use_current_asset_bytes(self):
        css, script = b'body{color:blue}', b'window.readerReady=true;'
        files = {'site.css': css, 'app.js': script}
        markup = ('<link href="../assets/site.css?v=abcdef123456">'
                  '<script src="../../assets/app.js?v=DEADBEEF"></script>'
                  '<link href="assets/site.css">')
        with patch.object(Path, 'read_bytes', autospec=True, side_effect=lambda path: files[path.name]):
            result = version_resources(markup)
        css_hash = hashlib.sha256(css).hexdigest()[:12]
        script_hash = hashlib.sha256(script).hexdigest()[:12]
        self.assertEqual(result, '<link href="../assets/site.css?v=' + css_hash + '">'
                         '<script src="../../assets/app.js?v=' + script_hash + '"></script>'
                         '<link href="assets/site.css?v=' + css_hash + '">')

    def test_versioning_is_idempotent_and_refreshes_changed_assets(self):
        markup = '<script src="../assets/app.js?v=deadbeef"></script>'
        with patch.object(Path, 'read_bytes', return_value=b'first'):
            first = version_resources(markup)
            self.assertEqual(version_resources(first), first)
        with patch.object(Path, 'read_bytes', return_value=b'second'):
            second = version_resources(first)
        self.assertNotEqual(second, first)
        self.assertIn('?v=' + hashlib.sha256(b'second').hexdigest()[:12], second)

    def test_external_and_other_query_urls_remain_unchanged(self):
        markup = ('<script src="https://example.com/assets/app.js?v=deadbeef"></script>'
                  '<link href="//example.com/assets/site.css?v=deadbeef">'
                  '<link href="../assets/site.css?theme=dark">'
                  '<link href="../assets/site.css?v=deadbeef&amp;theme=dark">'
                  '<link href="../assets/site.css#theme">'
                  '<img src="../assets/cover.png?v=deadbeef">')
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('Unexpected resource read')):
            self.assertEqual(version_resources(markup), markup)


if __name__ == '__main__':
    unittest.main()
