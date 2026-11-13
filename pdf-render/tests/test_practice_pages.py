"""Era boundaries, sample text counts, and paired reader metadata."""
from pathlib import Path
import json,re,sys,unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'pdf-render/web-tools'))
from practice_pages import Content,PAGE_DATA,minutes,timer_metadata,reader,catalog

class PracticePages(unittest.TestCase):
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
            self.assertIn('gradeless answer',markup,page.name)
    def test_palette_previews_keep_the_shared_styles_on_every_settings_page(self):
        pages=cards=0
        for page in (ROOT/'astraJLPT').rglob('*.html'):
            markup=page.read_text('utf8')
            if not PAGE_DATA.search(markup):continue
            pages+=1
            for label in re.findall(r'<label\b[^>]*class="[^"]*\btheme-card\b[^"]*"[^>]*>',markup):
                self.assertNotIn('style=',label,page.name)
                self.assertRegex(label,r'\bps-[0-9a-z]+\b',page.name)
                cards+=1
        self.assertEqual(pages,618)
        self.assertEqual(cards,618*190)
    def test_repeated_reader_refresh_does_not_accumulate_controls_or_whitespace(self):
        markup=(ROOT/'astraJLPT/papers/N1_1996.html').read_text('utf8')
        data=json.loads(PAGE_DATA.search(markup)[2])
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
    def test_all_402_readers_have_controls_and_paired_metadata(self):
        records={}
        for directory in ('papers','papers-norubi'):
            for page in (ROOT/'astraJLPT'/directory).glob('*.html'):
                markup=page.read_text('utf8');match=PAGE_DATA.search(markup)
                if not match:continue # Stable redirects for former unit IDs.
                data=json.loads(match[2]);paper=data['paper'];unit=paper['unit']
                self.assertEqual(markup.count('id="timer-display"'),1,page.name)
                self.assertEqual(markup.count('data-grade '),2,page.name)
                self.assertEqual(markup.count('id="score-dialog"'),1,page.name)
                self.assertGreater(paper['timer']['seconds'],0)
                self.assertTrue(all(q['domain'] in {'vocab','grammar','reading'} for q in data['questions']))
                self.assertNotIn('2020–2026 collection',markup.split('<main',1)[0])
                records[directory,unit]=data
        self.assertEqual(len(records),402)
        for (directory,unit),regular in records.items():
            if directory!='papers':continue
            other=records['papers-norubi',unit]
            self.assertEqual(regular['paper']['timer'],other['paper']['timer'])
            self.assertEqual(regular['questions'],other['questions'])
            self.assertEqual(regular['paper'].get('scoring'),other['paper'].get('scoring'))

if __name__=='__main__':unittest.main()
