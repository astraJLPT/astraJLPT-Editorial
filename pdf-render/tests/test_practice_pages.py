"""Era boundaries, sample text counts, and reader metadata and PDF bindings."""
from pathlib import Path
import hashlib,json,re,sys,unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'pdf-render/web-tools'))
from practice_pages import Content,PAGE_DATA,minutes,timer_metadata,reader,catalog,catalog_timer_example,dialogs
from question_data import read_page_data,asset_path
from web_assets import inline_resources,theme_data
from bs4 import BeautifulSoup

class PracticePages(unittest.TestCase):
    def assert_reader_controls(self, markup, unit, label):
        soup=BeautifulSoup(markup,'html.parser')
        scripts=soup.select('script#question-data')
        self.assertEqual(len(scripts),1,label)
        self.assertIn('defer',scripts[0].attrs,label)
        script=scripts[0].get('src','')
        expected='../'+asset_path(unit)
        digest=hashlib.sha256((ROOT/'astraJLPT'/asset_path(unit)).read_bytes()).hexdigest()[:12]
        self.assertEqual(script,expected+'?v='+digest,label)
        self.assertEqual(len(soup.select('#timer-display')),1,label)
        self.assertEqual(len(soup.select('[data-grade]')),2,label)
        self.assertEqual(len(soup.select('#score-dialog')),1,label)

    def test_reader_controls_accept_attribute_forms_and_reject_real_errors(self):
        unit='N5_sample_2009';asset=asset_path(unit)
        digest=hashlib.sha256((ROOT/'astraJLPT'/asset).read_bytes()).hexdigest()[:12]
        source='../'+asset+'?v='+digest
        for attribute in ('defer','defer=""',"defer='defer'"):
            markup=f'<script {attribute} src="{source}" id="question-data"></script><span id="timer-display"></span><button data-grade></button><button data-grade=""></button><dialog id="score-dialog"></dialog>'
            self.assert_reader_controls(markup,unit,attribute)
        for bad in [markup.replace('id="question-data"','id="missing"'),markup.replace("defer='defer'",''),markup.replace(digest,'0'*12),markup.replace('N5_sample_2009.js','N4_sample_2009.js'),markup.replace('<button data-grade></button>',''),markup+'<button data-grade></button>']:
            with self.assertRaises(AssertionError):self.assert_reader_controls(bad,unit,'invalid fixture')
    def test_standalone_scripts_accept_bare_and_serialized_defer_attributes(self):
        page=ROOT/'astraJLPT/papers/N5_sample_2009.html'
        for attribute in ('defer','defer=""'):
            markup=f'<script id="question-data" src="../assets/questions/N5_sample_2009.js" {attribute}></script><script {attribute} id="theme-data" src="../assets/theme-data.js"></script><script src="../assets/app.js" {attribute}></script>'
            soup=BeautifulSoup(inline_resources(markup,page),'html.parser')
            scripts=soup.select('script')
            self.assertEqual(len(scripts),3)
            self.assertTrue(all(not s.has_attr('src') and not s.has_attr('defer') for s in scripts))
            self.assertIn('globalThis.AstraQuestions = ',scripts[0].get_text())
            self.assertEqual(len(theme_data(soup,page)['monkeytype']),187)
    def test_result_titles_keep_full_catalog_names_and_historical_levels(self):
        for unit,title in {
            'N1_12_2023':'N1 December 2023',
            'N1_workbook_2018':'N1 2018 · Official Practice Workbook Vol. 2',
            'N2_workbook_2012':'N2 2012 · Official Practice Workbook',
            'N1_set_2011_2012':'N1 Exam 2011/2012 · Workbook',
            'N3_set_2011_2012':'N3 Exam 2011/2012 · Workbook',
            'N1_sample_2009':'N1 2009 official sample',
            'N1_1999':'1級 December 1999',
            'N1_07_2009':'1級 July 2009',
        }.items():
            heading=BeautifulSoup(dialogs(unit),'html.parser').select_one('#score-title')
            self.assertEqual(heading.get_text(),title,unit)
        heading=BeautifulSoup(dialogs('N1_workbook_2018'),'html.parser').select_one('#score-title')
        self.assertEqual(heading.select_one('.score-title-main').get_text(),'N1 2018')
        self.assertEqual(heading.select_one('.score-title-volume').get_text(),'Vol. 2')
    def test_all_result_titles_match_the_actual_level_cards(self):
        titles={}
        for page in (ROOT/'astraJLPT/levels').glob('*.html'):
            soup=BeautifulSoup(page.read_text('utf8'),'html.parser')
            level=soup.select_one('h1').get_text().removeprefix('Old ')
            for link in soup.select('.paper-card h2 a'):
                unit=Path(link['href']).stem
                label=link.get_text().replace('↗','').strip().removeprefix(level+' · ')
                titles[unit]=level+' '+label
        self.assertEqual(len(titles),201)
        for unit,title in titles.items():
            markup=(ROOT/'astraJLPT/papers'/(unit+'.html')).read_text('utf8')
            heading=re.search(r'<h2 id="score-title">(.*?)</h2>',markup,re.S)[1]
            self.assertEqual(BeautifulSoup(heading,'html.parser').get_text(),title,unit)
            self.assertIn('class="progress-correct">correct</span>',markup)
            self.assertNotIn('progress-completed',markup)
    def test_homepage_generator_links_to_all_modern_and_historical_levels(self):
        from catalog_html import homepage
        page=BeautifulSoup(homepage([]),'html.parser')
        self.assertEqual([a['href'] for a in page.select('.level-card')],[f'levels/N{i}.html' for i in range(5,0,-1)])
        self.assertEqual([a['href'] for a in page.select('#historical a')],[f'levels/old-{i}.html' for i in range(1,5)])
        self.assertFalse(page.select('script'))
    def test_native_reader_option_selectors_are_absent_from_the_scripted_stylesheets(self):
        from settings_ui import MARKS
        assets=ROOT/'astraJLPT/assets'
        active='\n'.join((assets/name).read_text('utf8') for name in ('site.css','answer-marking.css','pdf-typography.css'))
        native=(assets/'themes-no-script.css').read_text('utf8')
        root_check=r'body(?:\[[^\]]+\])*:has\((?:input\[name=[\"\x27]?(?:marking|spacing|rubi)|#(?:visible-paper|show-star-order))'
        self.assertNotRegex(active,root_check)
        for group,values in [('marking',[key for key,_ in MARKS]),('spacing',['original','standard','compact']),('rubi',['show','hide'])]:
            for value in values:
                self.assertIn(f'body[data-{group}={value}]',active)
                selector=f'#rubi-{value}:checked ~' if group=='rubi' else f'body:has(input[name={group}][value={value}]:checked)'
                self.assertIn(selector,native)
        for control in ('visible-paper','show-star-order'):
            self.assertIn(f'body[data-{control}]',active)
            self.assertIn(f'body:has(#{control}:checked)',native)

    def test_catalog_timer_follows_latest_sitting_and_uses_its_actual_limit(self):
        older = {'unit':'july','year':2025,'month':7,'content_kind':'calendar','timer':{'seconds':5400}}
        latest = dict(older,unit='december',month=12,timer={'seconds':4800})
        sample = dict(older,unit='sample',year=2026,content_kind='sample')
        for papers in ([sample,older,latest], [latest,sample,older]):
            self.assertEqual(catalog_timer_example(papers), {'catalog_timer_seconds':4800})
            self.assertEqual(catalog_timer_example(papers,{'december':{'seconds':4500}}), {'catalog_timer_seconds':4500})
        self.assertEqual(catalog_timer_example([sample]), {})

    def test_catalog_refresh_keeps_one_note_break_and_is_repeatable(self):
        markup='<main><a class="back-link" href="../index.html">All levels</a><p class="collection-note">Ordered with higher quality papers presented first.<br>Principal source PDF available here.</p></main>'
        once=catalog(markup,{})
        self.assertEqual(once.count('<br/>'),1)
        self.assertEqual(catalog(once,{}),once)
    def test_catalogs_and_home_share_global_timer_controls_without_paper_fields(self):
        for page in [ROOT/'astraJLPT/index.html',*sorted((ROOT/'astraJLPT/levels').glob('*.html'))]:
            markup=page.read_text('utf8')
            for name in ('timer-enabled','timer-controls','timer-direction'):
                self.assertIn('name="'+name+'"',markup,page.name)
            self.assertNotIn('id="timer-limit"',markup,page.name)
            self.assertNotIn('id="timer-display"',markup,page.name)
            self.assertIn('id="theme-editor-template"',markup,page.name)
    def test_palettes_are_parsed_with_shared_previews_and_editor_stays_shared(self):
        pages=cards=0
        for page in (ROOT/'astraJLPT').rglob('*.html'):
            markup=page.read_text('utf8')
            if not PAGE_DATA.search(markup):continue
            pages+=1
            self.assertEqual(markup.count('id="theme-editor-template"'),1,page.name)
            self.assertNotIn('data-color-row=',markup,page.name)
            for label in re.findall(r'<label\b[^>]*class="[^"]*\btheme-card\b[^"]*"[^>]*>',markup):
                self.assertNotIn('style=',label,page.name)
                self.assertRegex(label,r'\bps-[0-9a-z]+\b',page.name)
                cards+=1
        self.assertEqual(pages,417)  # Home, nine levels, 201 papers, 201 reviews and five sources.
        self.assertEqual(cards,pages*(3+187))
        themes=json.loads((ROOT/'astraJLPT/assets/theme-data.js').read_text('utf8').removeprefix('globalThis.AstraThemes = ').rstrip().removesuffix(';'))
        self.assertEqual(len(themes['monkeytype']),187)
        self.assertIn('data-color-row="neutral"',themes['editorMarkup'])
        self.assertIn('gradeless answer',themes['editorMarkup'])
    def test_repeated_reader_refresh_does_not_accumulate_controls_or_whitespace(self):
        markup=(ROOT/'astraJLPT/papers/N1_1996.html').read_text('utf8')
        data=read_page_data(markup)
        registry=json.loads((ROOT/'pdf-render/web-src/historical-scoring.json').read_text('utf8'))
        once=reader(markup,data,data['paper']['timer'],registry)
        self.assertEqual(reader(once,data,data['paper']['timer'],registry),once)
    def test_december_2020_boundary_and_old_level_identity(self):
        p={'generation':'modern-2010','level':'N4','year':2020,'month':7}
        self.assertEqual(sum(minutes(p)),90)
        p['month']=12;self.assertEqual(sum(minutes(p)),80)
        p['level']='N5';self.assertEqual(sum(minutes(p)),60)
        p['generation']='historical-1991-2009';p['level']='4級';self.assertEqual(sum(minutes(p)),75)
        p['level']='1級';self.assertEqual(sum(minutes(p)),135)
    def test_moji_ignores_ruby_and_answer_help_and_counts_shared_text_once(self):
        markup='<section class="exam-section" data-task="reading"><div class="source-block"><p>日本<ruby>語<rt>ご</rt></ruby></p></div><article class="question" id="q1"><div class="question-content">意味</div><span class="option-text">選択</span><span class="star-solution">除外</span></article></section>'
        count=Content(markup)
        self.assertEqual(count.chars,{'vocab':0,'grammar':0,'reading':7})
        self.assertEqual(count.questions,{'q1':'reading'})
    def test_sample_uses_text_ratios_for_each_timed_booklet(self):
        paper={'unit':'N3_sample_2009','level':'N3','generation':'modern-2010','content_kind':'sample','year':2009,'month':None}
        reference={str(n):{'paper':{**paper,'unit':str(n),'content_kind':'calendar','year':2010+n,'partial':False},'chars':{'vocab':100,'grammar':100,'reading':200}} for n in range(3)}
        result=timer_metadata(paper,{'vocab':50,'grammar':50,'reading':100},reference)
        self.assertEqual(result['seconds'],50*60)
        self.assertEqual(result['ratios'],[.5,.5])
    def test_all_readers_share_answer_bindings_and_link_both_pdfs(self):
        from public_paths import html_path,site_pdf
        owners=json.loads((ROOT/'pdf-render/contracts/accepted-release.json').read_text('utf8'))['owners']
        site=ROOT/'astraJLPT'
        readers=set()
        for page in (site/'papers').glob('*.html'):
            markup=page.read_text('utf8');match=PAGE_DATA.search(markup)
            if not match:continue  # Redirect from a former unit ID.
            data=read_page_data(markup);paper=data['paper'];unit=paper['unit']
            self.assertNotIn('questions',json.loads(match[2]),page.name)
            self.assert_reader_controls(markup,unit,page.name)
            self.assertGreater(paper['timer']['seconds'],0)
            self.assertTrue(all(q['domain'] in {'vocab','grammar','reading'} for q in data['questions']))
            tokens=[{k:v for k,v in q.items() if k!='domain'} for q in data['questions']]
            digest=hashlib.sha256(json.dumps(tokens,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            for variant,mode,field in [('regular','show','release_sha256'),('norubi','hide','norubi_pdf_sha256')]:
                self.assertEqual(digest,owners[unit]['reader_semantics'][variant]['answer_tokens_sha256'],page.name)
                pdf=site_pdf(unit,variant)
                self.assertRegex(markup,rf'<a(?=[^>]*data-rubi-only="{mode}")(?=[^>]*href="../{re.escape(pdf)}")[^>]*>')
                self.assertEqual(paper[field],hashlib.sha256((site/pdf).read_bytes()).hexdigest())
            self.assertEqual(paper['public_path'],html_path(unit))
            self.assertEqual(paper['pdf_path'],site_pdf(unit))
            self.assertNotIn('2020–2026 collection',markup.split('<main',1)[0])
            readers.add(unit)
        self.assertEqual(readers,set(owners))
        self.assertEqual(len(list((site/'assets/questions').glob('*.js'))),201)

if __name__=='__main__':unittest.main()
