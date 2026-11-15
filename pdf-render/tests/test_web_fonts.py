"""Font source identity, WOFF2 generation, and full-program preservation."""
from pathlib import Path
import copy,hashlib,json,sys,tempfile,unittest
from unittest.mock import patch
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'pdf-render/web-tools'),str(ROOT/'pdf-render/tools')]
import rebuild
import font_profiles as fonts
from release_contract import contract
SITE=ROOT/'astraJLPT'


class WebFonts(unittest.TestCase):
    def test_reviewed_source_keeps_identity_and_uses_explicit_shared_payload(self):
        model=rebuild.web.compose('N2_workbook_2018')
        spec=fonts.role_specs(model)['WorkbookKyokaIcaProMediumReviewed']
        source=fonts.resource(spec['path'])
        self.assertEqual(source.name,'4de9dcf655bb-kyoka_ica_pro_medium_reviewed.otf')
        self.assertEqual(fonts.font_digest(source),spec['sha256'])
        logical=fonts.logical_font_target(spec['sha256'])
        self.assertEqual(logical,'assets/fonts/4de9dcf655bbf938-0.woff')
        self.assertEqual(fonts.installed_asset(logical,SITE),'assets/fonts/959cec1c93044516-0.woff2')
        name,data=fonts.installed_profile(model,SITE)
        self.assertEqual(name,'assets/fonts-ee4ad3289fbbce9b.css')
        self.assertEqual(data,(SITE/name).read_bytes())
        self.assertIn(b'font-family:"WorkbookKyokaIcaProMediumReviewed";src:url("fonts/959cec1c93044516-0.woff2?',data)

    def test_all_owner_profiles_resolve_without_writing(self):
        with patch.object(Path,'write_bytes',side_effect=AssertionError('Unexpected write')),patch.object(Path,'write_text',side_effect=AssertionError('Unexpected write')):
            for unit in contract()['owners']:
                with self.subTest(unit=unit):
                    model=rebuild.web.compose(unit)
                    name,data=fonts.installed_profile(model,SITE)
                    self.assertEqual((SITE/name).read_bytes(),data)

    def test_unknown_missing_escaping_and_corrupt_assets_fail_closed(self):
        with self.assertRaisesRegex(ValueError,'Unregistered WOFF2'):
            fonts.installed_asset('assets/fonts/'+'0'*16+'-0.woff',SITE)
        logical='assets/fonts/4de9dcf655bbf938-0.woff'
        with patch.object(fonts,'resource',return_value=ROOT/'outside.woff2'):
            with self.assertRaisesRegex(ValueError,'escapes website'):
                fonts.installed_asset(logical,SITE)
        work=ROOT/'pdf-render/work';work.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=work) as folder:
            site=Path(folder)
            with self.assertRaisesRegex(ValueError,'Missing installed'):
                fonts.installed_asset(logical,site)
            target='assets/fonts/959cec1c93044516-0.woff2';p=site/target;p.parent.mkdir(parents=True)
            payload=(SITE/target).read_bytes();p.write_bytes(payload[:-1]+bytes([payload[-1]^1]))
            with self.assertRaisesRegex(ValueError,'Changed installed'):
                fonts.installed_asset(logical,site)

    def test_changed_reviewed_source_binding_is_rejected(self):
        model=copy.deepcopy(rebuild.web.compose('N2_workbook_2018'))
        role=next(k for k,v in model['style']['font_roles'].items() if v.get('sha256','').startswith('4de9dcf655bb'))
        model['style']['font_roles'][role]['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'Font binding changed'):
            fonts.installed_profile(model,SITE)

    def test_full_programs_include_heros_and_both_type1_faces(self):
        manifest=json.loads((ROOT/'pdf-render/fonts/manifest.json').read_text('utf-8'))
        entries={Path(row['path']).name:row for row in manifest['fonts']}
        for name,face,size in [('791b31aa1db8-cmex10.pfb',b'CMEX10',30251),('503d59829700-lcircle1.pfb',b'LCIRCLE10',10594)]:
            row=entries[name];payload=(ROOT/row['path']).read_bytes()
            self.assertEqual(len(payload),size)
            self.assertEqual(hashlib.sha256(payload).hexdigest(),row['sha256'])
            self.assertIn(b'/FontName /'+face,payload)
            self.assertTrue(payload.startswith(b'\x80\x01'))
        heros=entries['b170162835f4-heros_bold_retained.otf']
        self.assertEqual(heros['sha256'],'b170162835f4efc288886dd4231406dc47e19b614cf4416836635599d44a7d60')
        for row in manifest['fonts']:
            self.assertEqual(fonts.font_digest(ROOT/row['path']),row['sha256'])

    def test_builder_emits_woff2_deduplicates_and_keeps_logical_profile_identity(self):
        import image_html
        work=ROOT/'pdf-render/work';work.mkdir(exist_ok=True)
        sources={
            'Canonical':{'path':'pdf-render/fonts/959cec1c9304-1738154915_A-OTF-KyokaICAPro-Medium.otf'},
            'Reviewed':{'path':'pdf-render/fonts/4de9dcf655bb-kyoka_ica_pro_medium_reviewed.otf'}}
        model={'unit':'font-fixture','document':{},'style':{'fonts':{}}}
        with tempfile.TemporaryDirectory(dir=work) as folder:
            site=Path(folder);(site/'work').mkdir();(site/'build-manifest.json').write_text('{"outputs":[]}',encoding='utf-8')
            with patch.object(rebuild.web,'SITE',site),patch.object(rebuild.web,'GENERATED',[]),patch.object(rebuild.web,'INPUTS',{}),patch.object(fonts,'role_specs',return_value=sources),patch.object(image_html,'artwork',return_value={}):
                first=rebuild.web.font_assets([model])
                before={p.relative_to(site).as_posix():p.read_bytes() for p in (site/'assets').rglob('*') if p.is_file()}
                second=rebuild.web.font_assets([model])
                self.assertEqual(first,second)
                self.assertEqual(before,{p.relative_to(site).as_posix():p.read_bytes() for p in (site/'assets').rglob('*') if p.is_file()})
            registry=json.loads((site/'data/font-assets.json').read_text('utf-8'))
            self.assertEqual(len(registry['fonts']),1)
            self.assertEqual(len(next(iter(registry['fonts'].values()))['derived_sources']),2)
            identities=registry['profile_source_targets']['assets/fonts.css']
            self.assertEqual(identities['Reviewed'],'assets/fonts/4de9dcf655bbf938-0.woff')
            self.assertEqual(len(list((site/'assets/fonts').glob('*.woff2'))),2)
            self.assertFalse(list((site/'assets/fonts').glob('*.woff')))
            for p in (site/'assets/fonts').glob('*.woff2'):
                with TTFont(p) as font:self.assertEqual(font.flavor,'woff2')
            self.assertIn('format("woff2")',(site/'assets/fonts.css').read_text('utf-8'))
            self.assertTrue(all(':all-layout-woff2-v1' in key for key in json.loads((site/'work/font-subsets.json').read_text('utf-8'))))


class FontSubsets(unittest.TestCase):
    def test_all_paper_faces_are_covered_and_ui_font_is_not_trimmed(self):
        import font_subsets as optimize
        installed={p.name for p in (SITE/'assets/fonts').glob('*.woff2')}
        self.assertEqual(set(optimize.TARGETS),installed-{'RobotoMono-Regular.woff2'})
        self.assertNotIn('RobotoMono-Regular.woff2',optimize.TARGETS)

    def test_corpus_includes_linked_scripts_css_and_both_renditions(self):
        import font_subsets as optimize
        work=ROOT/'pdf-render/work';work.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=work) as folder:
            site=Path(folder);(site/'assets').mkdir();(site/'papers').mkdir();(site/'papers-norubi').mkdir()
            (site/'assets/fonts.css').write_text('@font-face{src:url("fonts/fixture.woff2")} .mark::before{content:"\\4E09"}','utf-8')
            (site/'assets/questions.js').write_text('const text="\\u4e8c";','utf-8')
            markup='<link href="../assets/fonts.css" rel="stylesheet"/><script src="../assets/questions.js"></script>'
            (site/'papers/a.html').write_text(markup+'一','utf-8');(site/'papers-norubi/a.html').write_text(markup+'四&#x4e94;','utf-8')
            (site/'unrelated.html').write_text('🧬','utf-8')
            result=optimize.corpora(site,['fixture.woff2'])['fixture.woff2']
            self.assertTrue(set(map(ord,'一二三四五'))<=result['characters'])
            self.assertNotIn(ord('🧬'),result['characters'])
            self.assertEqual(len(result['pages']),2)

    def test_trim_prepares_in_memory_and_is_repeatable(self):
        import font_subsets as optimize
        work=ROOT/'pdf-render/work';work.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=work) as folder:
            site=Path(folder);(site/'assets/fonts').mkdir(parents=True);(site/'papers').mkdir()
            name='RobotoMono-Regular.woff2';payload=(SITE/'assets/fonts'/name).read_bytes()
            (site/'assets/fonts'/name).write_bytes(payload)
            css='@font-face{font-family:"UI";src:url("fonts/'+name+'?v='+hashlib.sha256(payload).hexdigest()[:12]+'")}';(site/'assets/fonts.css').write_text(css,'utf-8')
            html='<link href="../assets/fonts.css?v='+hashlib.sha256(css.encode()).hexdigest()[:12]+'" rel="stylesheet"><p>ABCD 1234</p>'
            (site/'papers/a.html').write_text(html,'utf-8')
            with patch.object(Path,'write_bytes',side_effect=AssertionError('Unexpected write')),patch.object(Path,'write_text',side_effect=AssertionError('Unexpected write')):
                outputs,report=optimize.prepare(site,[name])
            self.assertLess(report['after_bytes'],report['before_bytes'])
            self.assertEqual(set(outputs),{'assets/fonts/'+name,'assets/fonts.css','papers/a.html'})
            for key,data in outputs.items():(site/key).write_bytes(data)
            repeated,second=optimize.prepare(site,[name]);self.assertEqual(repeated,{})
            self.assertTrue(second['fonts'][0]['outlines_advances_and_line_metrics_equal'])

    def test_removed_required_glyph_and_changed_advance_are_rejected(self):
        from io import BytesIO
        import font_subsets as optimize
        original=(SITE/'assets/fonts/RobotoMono-Regular.woff2').read_bytes()
        candidate,proof=optimize.subset_payload(original,{ord('A')})
        with self.assertRaisesRegex(ValueError,'coverage lost'):
            optimize.verify_subset(original,candidate,{ord('A'),ord('B')})
        font=TTFont(BytesIO(candidate));glyph=font.getBestCmap()[ord('A')]
        advance,bearing=font['hmtx'][glyph];font['hmtx'][glyph]=(advance+1,bearing)
        out=BytesIO();font.save(out);font.close()
        with self.assertRaisesRegex(ValueError,'advance changed'):
            optimize.verify_subset(original,out.getvalue(),{ord('A')})


if __name__=='__main__':unittest.main()
