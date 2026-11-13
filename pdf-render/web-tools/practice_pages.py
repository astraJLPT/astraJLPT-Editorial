"""Refresh practice metadata and controls without regenerating authored paper bodies.

Time allowances exclude listening and breaks. Sample allowances use visible moji,
not question counts, compared with the nearest three complete modern papers.
Sources: https://www.jlpt.jp/e/guideline/testsections.html
https://www.jlpt.jp/e/topics/202009091599642827.html
https://www.jlpt.jp/reference/pdf/guidebook_s_e.pdf (original modern format).
https://ftp.jlpt.jp/tw/reference/pdf/guidebook1.pdf (old-test comparison).
"""
from pathlib import Path
from html.parser import HTMLParser
import copy,json,re,statistics
from bs4 import BeautifulSoup
from settings_ui import settings
from theme_editor import color_roles,FILL_CONTROLS
from theme_colors import theme_css

ROOT=Path(__file__).resolve().parents[2]
SITE=ROOT/'astraJLPT'
PAGE_DATA=re.compile(r'(<script\b[^>]*\bid="page-data"[^>]*>)(.*?)(</script>)',re.S)
READING={'reading','paired_reading','information_retrieval'}
GRAMMAR={'grammar','sentence_composition','cloze'}

def domain(task):
    return 'reading' if task in READING else 'grammar' if task in GRAMMAR else 'vocab'

class Content(HTMLParser):
    """Count each authored passage once; omit ruby readings and answer help."""
    VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    SKIP={'section-heading','question-no','option-number','option-feedback','result-text','star-solution','star-unavailable','developer-note','worked-example','visual-only','passage-label','sr-only','source-literal'}
    KEEP={'source-block','question-content','option-text','reading-notes'}
    def __init__(self,markup):
        super().__init__(convert_charrefs=True)
        self.stack=[];self.questions={};self.chars={k:0 for k in ('vocab','grammar','reading')};self.feed(markup)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs);classes=set(a.get('class','').split())
        parent=self.stack[-1][1:] if self.stack else (None,False,False)
        subject,keep,skip=parent
        if 'exam-section' in classes:subject=domain(a['data-task'])
        keep=keep or bool(classes&self.KEEP)
        skip=skip or tag in ('rt','rp','script','style') or bool(classes&self.SKIP)
        if 'question' in classes and subject:self.questions[a['id']]=subject
        if tag not in self.VOID:self.stack.append((tag,subject,keep,skip))
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:del self.stack[i:];break
    def handle_data(self,text):
        if self.stack:
            _,subject,keep,skip=self.stack[-1]
            if subject and keep and not skip:self.chars[subject]+=sum(not c.isspace() for c in text)

def minutes(paper):
    if paper['generation'].startswith('historical'):
        return {'1級':(45,90),'2級':(35,70),'3級':(35,70),'4級':(25,50)}[paper['level']]
    after=(paper['year'],paper.get('month') or 0)>=(2020,12)
    return {'N1':(110,), 'N2':(105,), 'N3':(30,70), 'N4':(25,55) if after else (30,60), 'N5':(20,40) if after else (25,50)}[paper['level']]

def timer_metadata(paper,chars,reference):
    allowance=minutes(paper);total=sum(allowance)
    note='Combined written sections; listening and breaks are excluded.'
    result={'seconds':total*60,'basis':'level-era','written_minutes':list(allowance),'note':note}
    if paper['content_kind']=='sample':
        candidates=sorted((p for p in reference.values() if p['paper']['level']==paper['level'] and p['paper']['generation']==paper['generation'] and p['paper']['content_kind']=='calendar' and not p['paper']['partial']),key=lambda p:(abs(p['paper']['year']-paper['year']),p['paper']['year'],p['paper'].get('month') or 0))[:3]
        if not candidates:raise ValueError('No complete sample timing reference: '+paper['unit'])
        groups=[('vocab','grammar','reading')] if len(allowance)==1 else [('vocab',),('grammar','reading')]
        ratios=[]
        for group in groups:
            denominator=statistics.median(sum(p['chars'][k] for k in group) for p in candidates)
            if not denominator:raise ValueError('Empty sample timing reference')
            ratios.append(sum(chars[k] for k in group)/denominator)
        adjusted=max(1,int(sum(m*r for m,r in zip(allowance,ratios))+.5))
        result.update(seconds=adjusted*60,basis='sample-moji-estimate',reference_units=[p['paper']['unit'] for p in candidates],moji=chars,ratios=ratios,note='Approximate sample allowance, proportional to visible text in nearby full papers. Listening and breaks are excluded.')
    return result

def replace_settings(markup,fresh):
    start=re.search(r'<details\b[^>]*\bid="settings"[^>]*>',markup)
    if not start:return markup
    depth=0
    for tag in re.finditer(r'</?details\b[^>]*>',markup[start.start():]):
        depth+=-1 if tag[0].startswith('</') else 1
        if depth==0:return markup[:start.start()]+fresh+markup[start.start()+tag.end():]
    raise ValueError('Unclosed settings')

TIMER='''<span id="timer-banner" class="timer-banner js-only"><span id="timer-display" role="timer" aria-live="off">0:00:00</span><span id="timer-banner-controls" hidden><button type="button" data-timer-action="pause" aria-label="Pause timer"><span class="timer-action-icon" aria-hidden="true">Ⅱ</span><span class="timer-action-label">pause</span></button><button type="button" data-timer-action="reset" aria-label="Reset timer"><span class="timer-action-icon" aria-hidden="true">↺</span><span class="timer-action-label">reset timer</span></button></span></span>'''

def grade_bar(position):
    return f'<div class="grade-toolbar js-only" data-practice="{position}"><button type="button" class="grade-button" data-grade aria-pressed="false" hidden>Grade now</button></div>'

DIALOGS='''<dialog id="time-up-dialog" class="practice-dialog" aria-labelledby="time-up-title" data-practice="time-up"><h2 id="time-up-title">Time’s up</h2><p>Your countdown has finished. You can keep answering or adjust the timer.</p><button type="button" data-dialog-close autofocus>Close</button></dialog>
<dialog id="score-dialog" class="practice-dialog" aria-labelledby="score-title" data-practice="score"><h2 id="score-title">Your practice score</h2><div class="score-table-wrap"><table><caption class="sr-only">Scores for the available written sections</caption><thead><tr><th scope="col">Section</th><th scope="col">Score</th><th scope="col">Answers</th><th scope="col">Method</th></tr></thead><tbody id="score-sections"></tbody></table></div><p id="score-total"></p><p id="score-explanation" class="score-note"></p><p id="score-coverage" class="score-note"></p><p id="score-source"></p><p class="developer-only">Think you can outsmart this calculator? Send a pull request. Some .xlsx files that can help you are in <a href="https://github.com/astraJLPT/astraJLPT-Editorial/tree/main/additional-assets/saiten-pr" target="_blank" rel="noopener">additional-assets/saiten-pr/</a>. The calculator is accepting challengers.</p><button type="button" data-dialog-close autofocus>Close</button></dialog>'''

SORT='''<label class="catalog-sort js-only" for="catalog-sort">Sort by: <select id="catalog-sort"><option value="recommended">Recommended first</option><option value="newest">Newest first</option><option value="oldest">Oldest first</option></select></label>'''

def reader(markup,data,timing,registry):
    paper=data['paper'];paper['timer']=timing
    content=Content(markup)
    for question in data['questions']:question['domain']=content.questions[question['id']]
    profile=registry['profiles'].get(paper['unit'])
    if profile:
        paper['scoring']=copy.deepcopy(profile)
        source=registry['sources'][profile['source']]
        paper['scoring']['source_path']=source['path'].removeprefix('astraJLPT/')
    else:paper.pop('scoring',None)
    if 'id="timer-banner"' not in markup:
        markup=re.sub(r'(<a\b[^>]*class="return-top"[^>]*>.*?</a>)',lambda m:'<div class="reader-start">'+m[1]+TIMER+'</div>',markup,count=1,flags=re.S)
    markup=re.sub(r'<div class="grade-toolbar js-only" data-practice="[^"]+">.*?</div>','',markup,flags=re.S)
    markup=re.sub(r'(<main\b[^>]*class="paper-stage"[^>]*>)',lambda m:m[1]+grade_bar('top'),markup,count=1)
    markup=markup.replace('<div class="paper-end">',grade_bar('bottom')+'<div class="paper-end">',1)
    markup=re.sub(r'\s*<dialog\b[^>]*data-practice="[^"]+"[^>]*>.*?</dialog>\s*','',markup,flags=re.S)
    markup=markup.replace('</body>',DIALOGS+'</body>')
    encoded=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    return PAGE_DATA.sub(lambda m:m[1]+encoded+m[3],markup)

def catalog(markup,reference):
    soup=BeautifulSoup(markup,'html.parser');back=soup.select_one('.back-link')
    if not soup.select_one('#catalog-sort'):
        row=soup.new_tag('div',attrs={'class':'catalog-navigation'});back.wrap(row)
        row.append(BeautifulSoup(SORT,'html.parser'))
    for rank,card in enumerate(soup.select('.paper-grid>.paper-card')):
        unit=Path(card.select_one('.paper-cover')['href']).stem
        p=reference[unit]['paper']
        card['data-rank']=str(rank) if not card.has_attr('data-rank') else card['data-rank']
        card['data-year']=str(p['year']);card['data-month']=str(p.get('month') or 0)
    note=soup.select_one('.collection-note')
    if not soup.select_one('#catalog-order-note'):
        for text in list(note.find_all(string=True)):
            if str(text).startswith('Ordered with higher quality'):text.extract()
        order=soup.new_tag('span',id='catalog-order-note');order.string='Ordered with higher quality papers presented first.'
        note.insert(0,order)
    order=note.select_one('#catalog-order-note')
    for sibling in list(order.next_siblings):
        if getattr(sibling,'name',None)=='br' or not str(sibling).strip():sibling.extract()
        else:break
    order.insert_after(soup.new_tag('br'))
    return str(soup)

def refresh():
    themes_path=SITE/'assets/theme-data.js'
    themes=json.loads(themes_path.read_text('utf8').removeprefix('globalThis.AstraThemes = ').rstrip().removesuffix(';'))
    themes['colorRoles']=color_roles();themes['fillControls']=FILL_CONTROLS
    themes_path.write_text('globalThis.AstraThemes = '+json.dumps(themes,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf8',newline='\n')
    (SITE/'assets/themes.css').write_text(theme_css(themes),encoding='utf8',newline='\n')
    registry=json.loads((ROOT/'pdf-render/web-src/historical-scoring.json').read_text('utf8'))
    reference={}
    for path in sorted((SITE/'papers').glob('*.html')):
        markup=path.read_text('utf8');match=PAGE_DATA.search(markup)
        if not match:continue
        data=json.loads(match[2]);reference[data['paper']['unit']]={'paper':data['paper'],'chars':Content(markup).chars}
    timings={unit:timer_metadata(row['paper'],row['chars'],reference) for unit,row in reference.items()}
    # Refreshing a shell must reuse the installed shared declarations, rather
    # than reintroducing every palette's inline preview colors on every page.
    from shared_styles import ASSET,RULE,Tags,replace_styles
    sheet=SITE/ASSET
    classes={value:key for key,value in RULE.findall(sheet.read_text('utf8'))} if sheet.exists() else {}
    settings_cache={}
    for is_reader in (True,False):
        fresh=settings(themes,reader=is_reader,labelled=True)
        settings_cache[is_reader]=replace_styles(fresh,Tags(fresh).rows,classes)[0]
    changed=0
    for path in sorted(SITE.rglob('*.html')):
        markup=path.read_text('utf8');match=PAGE_DATA.search(markup)
        if not match:continue
        data=json.loads(match[2]);is_reader='paper' in data
        new=replace_settings(markup,settings_cache[is_reader])
        if is_reader:new=reader(new,data,timings[data['paper']['unit']],registry)
        elif path.parent.name=='levels':new=catalog(new,reference)
        if new!=markup:path.write_text(new,encoding='utf8',newline='\n');changed+=1
    from rebuild import install_runtime_assets,refresh_asset_versions
    install_runtime_assets();refresh_asset_versions()
    print(json.dumps({'practice_pages_refreshed':changed,'papers':len(reference),'sample_minutes':{u:t['seconds']//60 for u,t in timings.items() if t['basis']=='sample-moji-estimate'}},ensure_ascii=False),flush=True)

if __name__=='__main__':refresh()
