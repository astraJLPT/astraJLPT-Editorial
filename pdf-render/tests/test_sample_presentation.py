"""Regression coverage for the approved sample and modern heading repairs."""
from pathlib import Path
import copy,importlib.util,sys,tempfile,unittest
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'pdf-render/web-tools'),str(ROOT/'pdf-render/tools')]
import rebuild
from model import compose,digest,Projection
from renditions import select
from tex_html import render_heading,prepare_heading_boxes
from section_layout import prepare_sections
from font_profiles import installed_profile

UNITS=('N3_07_2025','N3_12_2023','N3_12_2024','N3_12_2025',
       'N4_sample_2009','N5_sample_2009','N4_07_2025','N4_12_2024',
       'N4_12_2025','N5_07_2025','N5_12_2025')

class SamplePresentation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.models={u:compose(u) for u in UNITS}

    def test_all_bound_headings_have_exactly_two_boxes_and_preserve_source(self):
        for unit,original in self.models.items():
            for sid,bound in original['style']['heading_number_boxes'].items():
                with self.subTest(unit=unit,section=sid):
                    m=copy.deepcopy(original);section=next(s for s in m['document']['sections'] if s['id']==sid)
                    source=copy.deepcopy(section['heading'])
                    output=BeautifulSoup(render_heading(source,m,sid),'html.parser')
                    boxes=output.select('.cloze-slot')
                    self.assertEqual([n.select_one('.visual-only').get_text() for n in boxes],bound['labels'])
                    for node in list(output.select('.visual-only')):node.decompose()
                    self.assertEqual(''.join(Projection({'html':str(output)}).text.split()),''.join(Projection(source).text.split()))
                    self.assertEqual(section['heading'],source)

    def test_stale_or_ambiguous_heading_binding_fails_closed(self):
        m=copy.deepcopy(self.models['N3_12_2025']);sid='vocab-s08'
        value=next(s['heading'] for s in m['document']['sections'] if s['id']==sid)
        bad={'html':value['html']+' [19]から[22]'}
        with self.assertRaisesRegex(ValueError,'Stale'):
            prepare_heading_boxes(bad,m,sid,bad)
        m['style']['heading_number_boxes'][sid]['content_sha256']=digest(bad)
        with self.assertRaisesRegex(ValueError,'exactly once'):
            prepare_heading_boxes(bad,m,sid,bad)

    def test_samples_use_exact_font_and_effective_scale(self):
        for unit,profile in [('N4_sample_2009','f4eee5aa5250fb09'),('N5_sample_2009','8f5b8b92d80fa170')]:
            m=self.models[unit];style=m['style'];cfg=style['instruction_selector'];horizontal=style.get('heading_horizontal_scale',1)
            self.assertEqual(cfg['display_digits'],'ascii')
            self.assertAlmostEqual(cfg['digit_horizontal_scale']*horizontal,.865)
            self.assertAlmostEqual(cfg['dot_horizontal_scale']*horizontal,1)
            self.assertAlmostEqual(cfg['cell_em']*horizontal,1)
            self.assertTrue(style['font_roles']['instruction_selector']['sha256'].startswith('8563d912f7a90640'))
            name,data=installed_profile(m,ROOT/'astraJLPT')
            self.assertEqual(name,'assets/fonts-'+profile+'.css')
            self.assertIn(b'font-family:"SelectorDigits";src:url("fonts/8563d912f7a90640-0.woff2?',data)
        self.assertEqual(self.models['N5_sample_2009']['style']['heading_horizontal_scale'],.92)

    def test_bound_section_selection_preserves_all_text_and_ruby(self):
        m=self.models['N5_sample_2009'];items={i['id']:i for s in m['document']['sections'] for i in s['items']}
        for bid in ['vocab-b004','vocab-b005','reading-b002']:
            value=items[bid]['content'];spec=m['style']['section_styles'][bid]
            prepared=prepare_sections(value,spec);a,b=Projection(value),Projection(prepared)
            self.assertEqual(a.text,b.text);self.assertEqual(a.ruby,b.ruby)
            soup=BeautifulSoup(prepared['html'],'html.parser')
            if bid.startswith('vocab'):
                self.assertRegex(soup.p.get_text(),r'^（[12]）$')
                self.assertIsNone(soup.p.find_parent('section'))
            else:
                self.assertEqual(spec['frame_style'],'folded_corner')
                self.assertEqual(spec.get('font_role','body'),'body')
                self.assertEqual(soup.section.p.get_text(),'アンナさん')

    def test_both_html_renditions_have_correct_frame_boundaries(self):
        web=rebuild.web
        for unit in ['N4_sample_2009','N5_sample_2009']:
            for variant in ['regular','norubi']:
                with self.subTest(unit=unit,variant=variant):
                    m=select(copy.deepcopy(self.models[unit]),variant)
                    m['web_metrics']=web.resolve_metrics(m,ROOT/'astraJLPT'/rebuild.site_pdf(unit,variant))
                    markup,_,_=web.paper(m,web.star_data([m]));soup=BeautifulSoup(markup,'html.parser')
                    self.assertFalse(soup.find(id='vocab-b003').select('.cloze-frame,.notice-frame'))
                    if variant=='norubi':self.assertFalse(soup.find_all('ruby'))
                    if unit.startswith('N5'):
                        for bid in ['vocab-b004','vocab-b005']:
                            block=soup.find(id=bid);label=block.select_one('.passage-label')
                            self.assertIsNotNone(label);self.assertIsNone(label.find_parent(class_='cloze-frame'))
                            self.assertEqual(len(block.select('.cloze-frame')),1)
                        self.assertEqual(len(soup.find(id='reading-b002').select('.native-folded-memo')),1)
                        self.assertFalse(soup.find(id='reading-b001').select('.native-folded-memo'))

    def test_native_sample_emission_consumes_the_same_bindings(self):
        spec=importlib.util.spec_from_file_location('sample_native_build',ROOT/'pdf-render/tools/build.py')
        native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
        work=ROOT/'pdf-render/work';work.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=work) as folder:
            for unit in ['N4_sample_2009','N5_sample_2009']:
                for variant in ['regular','norubi']:
                    m=select(copy.deepcopy(self.models[unit]),variant)
                    target=Path(folder)/unit/variant;target.mkdir(parents=True)
                    tex=native.generate(m,target)
                    ranges=[f for f in m['render_coverage']['features'] if f['kind']=='heading_number_boxes']
                    self.assertEqual([f['labels'] for f in ranges],[['5','9']])
                    if unit.startswith('N5'):self.assertIn(r'\FoldedMemo{16}',tex)

if __name__=='__main__':unittest.main()
