"""Selected rebuilding is read-only until validated installation and stays scoped."""
from pathlib import Path
import copy,io,json,sys,tempfile,unittest
from contextlib import redirect_stdout
from unittest.mock import patch
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'pdf-render/web-tools'),str(ROOT/'pdf-render/tools')]
import rebuild
from font_profiles import installed_profile
from question_data import PAGE_DATA

UNITS=('N3_07_2025','N3_12_2023','N3_12_2024','N3_12_2025',
       'N4_sample_2009','N5_sample_2009','N4_07_2025','N4_12_2024',
       'N4_12_2025','N5_07_2025','N5_12_2025')

class ScopedRebuild(unittest.TestCase):
    def test_visual_furniture_is_counted_once_but_authored_changes_fail(self):
        old=BeautifulSoup('<p>[19]から[22]</p>','html.parser')
        new=BeautifulSoup('<p><span class="source-literal sr-only">[19]</span><span class="visual-only">19</span>から<span class="source-literal sr-only">[22]</span><span class="visual-only">22</span></p>','html.parser')
        self.assertEqual(rebuild.content(old),rebuild.content(new))
        new.select_one('.source-literal').string='[18]'
        self.assertNotEqual(rebuild.content(old),rebuild.content(new))

    def test_long_reader_keeps_void_controls_and_their_labels_as_siblings(self):
        controls=''.join(f'<div><input id="answer-{i}" type="radio"/><label for="answer-{i}">'+('answer text '*40)+'</label></div>' for i in range(500))
        markup='<html><head></head><body>'+controls+'</body></html>'
        soup=rebuild.parse_html(markup)
        self.assertEqual(len(soup.select('input + label')),500)
        self.assertTrue(all(not node.contents for node in soup.select('input')))
        self.assertEqual(soup.get_text(),('answer text '*40)*500)
        self.assertEqual(str(rebuild.parse_html(str(soup))),str(soup))

    def test_complete_selected_batch_has_no_writes_or_unrelated_outputs(self):
        allowed={rebuild.html_path(unit) for unit in UNITS}
        allowed|={'assets/fonts-f4eee5aa5250fb09.css','assets/fonts-8f5b8b92d80fa170.css'}
        with patch.object(Path,'write_bytes',side_effect=AssertionError('Unexpected write')),patch.object(Path,'write_text',side_effect=AssertionError('Unexpected write')),redirect_stdout(io.StringIO()):
            outputs,results=rebuild.prepare(UNITS)
        self.assertEqual(len(results),len(UNITS))
        self.assertLessEqual(set(outputs),allowed)
        for unit in UNITS:
            name=rebuild.html_path(unit)
            markup=outputs[name] if name in outputs else (rebuild.web.SITE/name).read_bytes()
            paper=json.loads(PAGE_DATA.search(markup.decode())[2])['paper']
            for variant,field in [('regular','release_sha256'),('norubi','norubi_pdf_sha256')]:
                self.assertEqual(paper[field],rebuild.web.sha(rebuild.web.SITE/rebuild.site_pdf(unit,variant)),name)

    def test_reviewed_n2_workbook_rebuilds_one_reader_without_writes(self):
        with patch.object(Path,'write_bytes',side_effect=AssertionError('Unexpected write')),patch.object(Path,'write_text',side_effect=AssertionError('Unexpected write')),redirect_stdout(io.StringIO()):
            outputs,results=rebuild.prepare(['N2_workbook_2018'])
        self.assertEqual([r['unit'] for r in results],['N2_workbook_2018'])
        self.assertLessEqual(set(outputs),{'papers/N2_workbook_2018.html','assets/fonts-ee4ad3289fbbce9b.css'})
        self.assertNotIn('assets/fonts-ee4ad3289fbbce9b.css',set(outputs))

    def test_late_validation_failure_does_not_write_an_earlier_unit(self):
        compose=rebuild.web.compose
        def changed(unit):
            m=compose(unit)
            if unit=='N5_sample_2009':m['style']['section_styles']['reading-b002']['content_sha256']='0'*64
            return m
        with patch.object(rebuild.web,'compose',side_effect=changed),patch.object(Path,'write_bytes',side_effect=AssertionError('Unexpected write')),patch.object(Path,'write_text',side_effect=AssertionError('Unexpected write')),redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(ValueError,'Stale semantic section'):
                rebuild.prepare(['N4_sample_2009','N5_sample_2009'])

    def test_failed_install_restores_existing_files_and_removes_new_files(self):
        work=ROOT/'pdf-render/work';work.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=work) as folder:
            site=Path(folder);(site/'first').write_bytes(b'original');(site/'last').write_bytes(b'old')
            writer=Path.write_bytes;failed=False
            def fail_once(path,data):
                nonlocal failed
                if path.name=='last' and not failed:failed=True;raise OSError('simulated write failure')
                return writer(path,data)
            with patch.object(rebuild.web,'SITE',site),patch.object(Path,'write_bytes',fail_once):
                with self.assertRaises(OSError):rebuild.install({'first':b'changed','new':b'new','last':b'changed'})
            self.assertEqual((site/'first').read_bytes(),b'original')
            self.assertEqual((site/'last').read_bytes(),b'old')
            self.assertFalse((site/'new').exists())

    def test_missing_selector_glyphs_rejected_without_resubsetting(self):
        m=rebuild.web.compose('N4_sample_2009')
        with patch('font_profiles.TTFont') as font:
            font.return_value.__enter__.return_value.getBestCmap.return_value={}
            with self.assertRaisesRegex(ValueError,'lacks required glyphs'):
                installed_profile(m,ROOT/'astraJLPT')

if __name__=='__main__':unittest.main()
