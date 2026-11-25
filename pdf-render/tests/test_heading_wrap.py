"""Wrapping contracts shared by the paper editions."""
from pathlib import Path
import sys
import unittest

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'pdf-render/web-tools'), str(ROOT / 'pdf-render/tools')]
from richtex import heading_word_glue
from tex_html import heading_flow
from wakachi import bind_groups, spaced_task


class HeadingWrap(unittest.TestCase):
    def test_short_spaced_groups_cross_inline_markup_but_leave_gaps_outside(self):
        source = ('　<ruby>考<rt>かんが</rt></ruby>えて、　<u>もの</u>を '
                  'かきますか。 とてもながくてひとつのぎょうにおさまらない')
        for web in (True, False):
            soup = BeautifulSoup(source, 'html.parser')
            original = soup.get_text()
            bind_groups(soup, web=web)
            selector = '.wakachi' if web else '[data-bounded-word]'
            words = [node.get_text() for node in soup.select(selector)]
            self.assertEqual(words[:2], ['考えて、', 'ものを'])
            self.assertEqual(soup.select_one(selector).rt.string, 'かんが')
            self.assertEqual(soup.get_text(), original)
            self.assertTrue(str(soup.contents[0]).startswith('　'))
            self.assertTrue(all(' ' not in w and '　' not in w and 'ながく' not in w for w in words))
            if web:
                self.assertIn('かきますか。', words)
            else:
                self.assertEqual(len(soup.select('[data-wakachi-wide-gap]')), 1)

    def test_grouping_applies_to_the_modern_spaced_sections(self):
        self.assertTrue(spaced_task({'unit':'N4_workbook_2018'}, 'grammar'))
        self.assertTrue(spaced_task({'unit':'N5_workbook_2018'}, 'information_retrieval'))
        self.assertFalse(spaced_task({'unit':'N4_workbook_2018'}, 'reading'))
        self.assertFalse(spaced_task({'unit':'N4_2002','exam':{'generation':'historical-1991-2009'}}, 'grammar'))
        self.assertFalse(spaced_task({'unit':'N3_07_2024'}, 'grammar'))

    def test_spaced_list_items_titles_and_calibrated_numerals(self):
        soup = BeautifulSoup('<ol><li>中で ものを</li></ol><h3>つぎの さくぶん</h3>'
                             '<span class="tex-latin"><span class="content-digits">'
                             '<span style="transform:scaleX(.8)">300</span></span></span>'
                             '<ruby>円<rt>えん</rt></ruby>でした。', 'html.parser')
        bind_groups(soup, web=True)
        self.assertEqual([node.get_text() for node in soup.select('.wakachi')],
                         ['中で', 'ものを', 'つぎの', 'さくぶん', '300円でした。'])

    def test_native_word_spacing_is_discardable_only_in_running_text(self):
        original = r'ぶんが　\mbox{あります}。　　\HistoricalDoubleUnderline{　}\ruby{字}{じ}\{　\}'
        expected = (r'ぶんが\hskip 1\zw\relax \mbox{あります}。\hskip 2\zw\relax '
                    r'\HistoricalDoubleUnderline{　}\ruby{字}{じ}\{\hskip 1\zw\relax \}')
        self.assertEqual(heading_word_glue(original), expected)
        self.assertEqual(heading_word_glue(expected), expected)

    def test_responsive_spaces_preserve_source_and_fixed_furniture(self):
        soup = BeautifulSoup(
            'ぶんが<span class="tex-word-space">　</span>あります。'
            '<span class="mixed-word-space" data-native-space-em="0.7" '
            'data-native-space-role="authored_word_glue"> </span>'
            '<span class="heading-selector">1<span class="tex-word-space"> </span>2</span>'
            '<u><span class="tex-word-space">　</span></u>', 'html.parser')
        original = soup.get_text()
        heading_flow(soup)
        self.assertEqual(soup.get_text(), original)
        self.assertEqual(soup.select_one('.heading-wide-space').get_text(), '　')
        ascii_gap = soup.select_one('.heading-word-space')
        self.assertEqual(ascii_gap['data-native-space-em'], '0.7')
        self.assertEqual(ascii_gap.get_text(), ' ')
        self.assertEqual(len(soup.select('.tex-word-space')), 2)
        self.assertFalse(soup.select('wbr'))

    def test_sentence_spacing_is_emitted_once(self):
        from model import compose
        from tex_html import render_heading
        model = compose('N4_workbook_2018')
        heading = '見てください。答えは、1・2・3・4からえらんでください。'
        soup = BeautifulSoup(render_heading(heading, model, 'reading-s03', prepared=True), 'html.parser')
        self.assertEqual(len(soup.select('[data-instruction-boundary]')), 1)
        self.assertEqual(soup.select_one('.heading-selector').previous_sibling.name, 'wbr')

    def test_legal_breaks_outside_selector_and_adjacent_phrases(self):
        soup = BeautifulSoup(
            '答えは、<span class="heading-selector">1・2・3・4から</span>'
            '<span class="heading-no-break">いちばん</span>'
            '<span class="heading-no-break">いい</span>'
            '「<span class="heading-selector">1・2・3・4</span>」'
            'A<span class="heading-selector">1・2・3・4</span>'
            '２<span class="heading-selector">1・2・3・4</span>'
            '。<span class="instruction-number-sequence"><span class="heading-selector">'
            '1・2・3・4</span><wbr/>から</span>', 'html.parser')
        original = soup.get_text()
        heading_flow(soup)
        self.assertEqual(soup.get_text(), original)
        self.assertEqual([b.next_sibling.get_text() for b in soup.find_all('wbr')],
                         ['1・2・3・4から', 'いい', '1・2・3・4から', 'から'])
        self.assertFalse(soup.select('.heading-selector wbr,.heading-no-break wbr'))
        once = str(soup)
        heading_flow(soup)
        self.assertEqual(str(soup), once)


if __name__ == '__main__':
    unittest.main()
