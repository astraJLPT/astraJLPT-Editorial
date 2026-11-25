"""Checks for native word boundaries and HTML passage typography."""
from pathlib import Path
import sys
import unittest

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'pdf-render/web-tools'), str(ROOT / 'pdf-render/tools')]
from richtex import unbox_adjacent_commas
from semantic_html import paired_frames, wrap_tail
from tex_html import render_heading


class PassageTypography(unittest.TestCase):
    def test_measured_gaps_and_natural_corner_brackets_reach_both_formats(self):
        from inline_layout import prepare_inline
        from model import compose, digest
        from richtex import RichTeX
        from tex_html import render_inline

        source = 'に「こま屋」に。午後3時'
        value = prepare_inline(source, {
            'content_sha256': digest(source),
            'fullwidth_corner_quotes': ['「こま屋」'],
            'measured_gaps': [{'text': '午後3時', 'after': '午後', 'width_em': 0.8}],
        })
        soup = BeautifulSoup(render_inline(value, compose('N4_07_2021')), 'html.parser')
        gap = soup.select_one('[data-inline-gap-em]')
        self.assertIn('display:inline-block', gap['style'])
        self.assertIn('width:0.8em', gap['style'])
        brackets = soup.select('[data-fullwidth-bracket]')
        self.assertEqual([b.get_text() for b in brackets], ['「', '」'])
        for bracket in brackets:
            self.assertIn('font-feature-settings:"palt" 0', bracket['style'])
        native = RichTeX(ROOT).value(value)
        self.assertEqual(native.count(r'\addjfontfeatures{RawFeature={-palt}}'), 2)
        self.assertIn(r'\hspace{0.8em}', native)

    def test_framed_word_groups_keep_natural_pitch_and_authored_alignment(self):
        from section_html import present

        soup = BeautifulSoup(
            '<section class="reading-passage"><h3>お知らせ</h3><p><span class="wakachi">'
            'きょうしつに</span></p><p class="passage-author">アリ</p></section>'
            '<section class="reading-passage"><p>連続した文章。</p></section>', 'html.parser')
        present(soup, {'section_count': 2, 'frame_style': 'box'}, {})
        spaced, continuous = soup.select('.document-section')
        self.assertIn('text-align:start', spaced['style'])
        self.assertNotIn('text-align:', continuous['style'])
        self.assertIn('text-align:center', spaced.h3['style'])
        self.assertIn('text-align:right', spaced.select_one('.passage-author')['style'])

    def test_unboxed_example_choices_leave_the_answer_table_intact(self):
        from example_layout import prepare_ordinary_choices
        from model import compose
        from tex_html import render_inline

        model = compose('N4_07_2021')
        model['modern_wakachi'] = True
        value = prepare_ordinary_choices('（れい）\n1 あ\n2 い\n3 う\n4 え', [1, 2, 3, 4])
        value['html'] += '<table><tr><td>（れい）</td><td>①②③●</td></tr></table>'
        soup = BeautifulSoup(render_inline(value, model, 'example'), 'html.parser')
        cells = soup.select('.example-native-options > span')
        self.assertEqual([''.join(c.get_text().split()) for c in cells], ['1あ', '2い', '3う', '4え'])
        self.assertEqual([table.get_text() for table in soup.find_all('table')], ['（れい）①②③●'])
        for cell in cells:
            gap = cell.select_one('.mixed-word-space.wakachi-gap')
            self.assertEqual(gap['data-native-space-em'], '0.4')
            self.assertIn('calc(var(--nominal-em) * 0.4)', gap['style'])

    def test_numbered_example_columns_keep_only_their_own_spaces(self):
        from richtex import RichTeX

        renderer = RichTeX(ROOT, word_space_em=0.4)
        renderer.modern_wakachi = renderer.keep_spaced_words = renderer.passage_word_flow = True
        renderer.example_choice_numerals = True
        choices = ['1　スプーン　です', '2　ストーブ', '3　デパート', '4　ニュース']
        row = renderer.example('　　'.join(choices), 'ordinary')
        self.assertEqual(row.count(r'\ExampleChoiceNumber{'), 4)
        self.assertIn(r'\mbox{スプーン}\hskip 1em\relax \mbox{です}', row)
        self.assertNotIn(r'\hskip 2.0em', row)

    def test_native_word_final_commas_keep_japanese_spacing(self):
        pairs = [
            (r'\mbox{て、}\mbox{下}', r'\mbox{て}、\mbox{下}'),
            (r'\mbox{て、}\allowbreak{}\ruby{下}{した}', r'\mbox{て}、\allowbreak{}\ruby{下}{した}'),
            (r'\mbox{から、}い', r'\mbox{から}、い'),
            (r'\mbox{、}1', '、1'),
            (r'\mbox{て、}\hspace{.3em}下', r'\mbox{て、}\hspace{.3em}下'),
            (r'\mbox{て、}\par', r'\mbox{て、}\par'),
        ]
        for source, expected in pairs:
            with self.subTest(source=source):
                self.assertEqual(unbox_adjacent_commas(source), expected)
                self.assertEqual(unbox_adjacent_commas(expected), expected)

    def test_comma_before_ruby_and_selector_uses_normal_heading_text(self):
        from model import compose
        model = compose('N5_12_2025')
        value = {'html': '見て、<ruby>下<rt>した</rt></ruby>。答えは、1・2・3・4から、いちばん'}
        soup = BeautifulSoup(render_heading(value, model, 'reading-s06', prepared=True), 'html.parser')
        self.assertEqual(soup.get_text().count('、'), 3)
        self.assertTrue(soup.find('rt', string='した'))
        self.assertFalse(soup.find('span', class_='heading-punctuation', string='、'))

    def test_quoted_underlines_cover_the_same_words_in_the_passage_and_question(self):
        from model import compose, Projection
        cases = [
            ('N1_2002', 'reading-b001', 'reading-q003', '演劇を創るということは、ラブレターを書くようなものだ'),
            ('N2_12_2013', 'reading-b005', 'reading-q005', 'この2タイプ'),
            ('N2_07_2025', 'reading-b011', 'reading-q016', '「分かる」とは「分ける」ことだ'),
            ('N2_07_2026', 'reading-b009', 'reading-q064', 'おすすめだ'),
        ]
        for unit, passage, question, phrase in cases:
            with self.subTest(unit=unit):
                sections = compose(unit)['canonical_editorial']['sections']
                items = {item['id']: item for section in sections for item in section['items']}
                for field in (items[passage]['content'], items[question]['stem']):
                    soup = BeautifulSoup(field['html'], 'html.parser')
                    marked = [Projection({'html': str(n)}).text.replace(' ', '') for n in soup.find_all('u')]
                    self.assertIn(phrase, marked)

    def test_passage_uses_existing_border_and_excludes_citation(self):
        soup = BeautifulSoup(
            '<p class="context-intro">導入</p><div class="source-native-frame" data-native-frame="box">'
            '<p>本文</p></div><p><span data-paragraph-role="citation">出典</span></p>', 'html.parser')
        frame = wrap_tail(soup, 'cloze-frame')
        self.assertEqual(frame.get_text(), '本文')
        self.assertEqual(len(soup.select('.cloze-frame, .source-native-frame')), 1)
        self.assertIn('text-align:right', soup.select_one('[data-paragraph-role]').parent['style'])

    def test_paired_passages_each_keep_their_own_frame_shape(self):
        soup = BeautifulSoup(
            '<p>A</p><div data-native-frame="rules"><p>甲</p></div><p></p>'
            '<p>B</p><div data-native-frame="box"><p>乙</p></div><p></p>', 'html.parser')
        paired_frames(soup, {})
        frames = soup.select('.paired-frame')
        self.assertEqual([f['data-frame-style'] for f in frames], ['horizontal_rules', 'box'])
        self.assertEqual([f.get_text() for f in frames], ['甲', '乙'])
        self.assertFalse(soup.select('[data-native-frame]'))


if __name__ == '__main__':
    unittest.main()
