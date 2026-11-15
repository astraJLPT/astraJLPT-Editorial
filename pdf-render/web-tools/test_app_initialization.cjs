/* Browser regression checks for current scripts loading cached reader shells.
 * Requires Playwright; ASTRA_ENGINE selects chromium (default) or firefox.
 * ASTRA_BROWSER can select an installed binary.
 * Fixtures and browser storage stay in memory. No repository files are written.
 */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const browsers=require('playwright'),engine=process.env.ASTRA_ENGINE||'chromium';
const site=path.resolve(__dirname,'../../astraJLPT'),origin='http://astra.test';
const shared={};vm.runInNewContext(fs.readFileSync(path.join(site,'assets/theme-data.js'),'utf8'),shared);
const themes=JSON.parse(JSON.stringify(shared.AstraThemes.monkeytype));
function cachedShell(markup,kind){
  const catalog=/<div class="theme-grid theme-catalog">.*?<\/div>/s;
  assert.ok(catalog.test(markup),'Expected the parser-created theme catalog');
  if(kind==='empty')markup=markup.replace(catalog,'<div class="theme-grid theme-catalog"></div>');
  return markup.replace('<template id="theme-editor-template"></template>',shared.AstraThemes.editorMarkup)
    .replace('<span class="progress-correct">correct</span>','<span class="progress-completed">completed</span>');
}
const types={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.woff2':'font/woff2','.png':'image/png','.svg':'image/svg+xml'};
async function routePage(page,cached){
  await page.route('**/*',async route=>{
    const url=new URL(route.request().url()),name=decodeURIComponent(url.pathname).slice(1),target=path.resolve(site,name);
    if(url.origin!==origin||!target.startsWith(site+path.sep))return route.abort();
    let body=fs.readFileSync(target);
    if(name.endsWith('.html')){
      body=body.toString('utf8');if(cached())body=cachedShell(body,cached());
      // Runs during parsing, before the deferred application bundle.
      body=body.replace('</body>','<script>window.parsedPaletteInputs=[...document.querySelectorAll(".theme-catalog input")];</script></body>');
    }
    await route.fulfill({body,contentType:types[path.extname(name)]||'application/octet-stream'});
  });
}
async function snapshot(page){
  return page.evaluate(()=>({
    themes:document.querySelectorAll('.theme-catalog input[name=theme]').length,
    duplicateIds:[...document.querySelectorAll('[id]')].map(e=>e.id).filter((id,i,all)=>all.indexOf(id)!==i),
    theme:document.querySelector('[name=theme]:checked')?.value,
    oldLabels:document.querySelectorAll('.progress-completed').length,
    currentLabels:document.querySelectorAll('.progress-correct').length,
    selected:[...document.querySelectorAll('.answer-radio:checked')].map(e=>e.id),
    autoGrade:document.querySelector('[name=auto-grade]:checked')?.value,
    answers:Object.fromEntries(Object.keys(localStorage).filter(k=>k.includes(':paper:')).map(k=>[k,JSON.parse(localStorage[k]).answers]))
  }));
}
function checkShell(state,reader){
  assert.equal(state.themes,themes.length);assert.deepEqual(state.duplicateIds,[]);
  assert.equal(state.oldLabels,0);assert.equal(state.currentLabels,reader?1:0);
}
async function settle(page){
  await page.evaluate(async()=>{await document.fonts.ready;for(let i=0;i<3;i++)await new Promise(r=>requestAnimationFrame(r));});
}
async function checkPalette(page,kind){
  const state=await page.evaluate(()=>{
    const inputs=[...document.querySelectorAll('.theme-catalog input')];
    return {parsed:window.parsedPaletteInputs.length,retained:window.parsedPaletteInputs.every((input,i)=>input===inputs[i]),
      palettes:inputs.map(input=>{const css=getComputedStyle(input.closest('.theme-card'));return {id:input.value,bg:css.getPropertyValue('--preview-bg').trim(),text:css.getPropertyValue('--preview-text').trim()};})};
  });
  assert.equal(state.parsed,kind==='empty'?0:187);assert.ok(state.retained,'Parsed palette radios must not be rebuilt');
  assert.deepEqual(state.palettes,themes.map(t=>({id:t.id,bg:t.colors.bg,text:t.colors.main})));
}
async function checkAppearance(page){
  await page.evaluate(()=>{document.querySelector('#settings').open=true;document.querySelector('[name=settings-view][value=appearance]').click();});
  await settle(page);
  const gap=await page.evaluate(()=>document.querySelector('.theme-picker>details').getBoundingClientRect().top-document.querySelector('#quick-picks').getBoundingClientRect().bottom);
  assert.ok(Math.abs(gap-18)<.1,'Palette catalog must have an 18px top gap; got '+gap);
  await page.evaluate(()=>document.querySelector('.theme-picker>details').open=true);
  const term=themes[0].name.toLowerCase();await page.locator('#theme-search').fill(term);
  const visible=await page.locator('.theme-catalog .theme-card:not([hidden]) input').evaluateAll(inputs=>inputs.map(input=>input.value));
  assert.deepEqual(visible,themes.filter(t=>t.name.toLowerCase().includes(term)).map(t=>t.id));
  await page.locator('#theme-search').fill('');
  assert.equal(await page.locator('.theme-catalog .theme-card:not([hidden])').count(),187);
  await page.evaluate(()=>{document.querySelector('.theme-picker>details').open=false;document.querySelector('#settings').open=false;});
}
async function setText(page,value){
  await page.evaluate(value=>{const field=document.querySelector('#text-size');field.value=value;field.dispatchEvent(new Event('input',{bubbles:true}));},value);
  await settle(page);
}
async function checkText(page,expected){
  await settle(page);
  const state=await page.evaluate(()=>({value:document.querySelector('#text-size').value,output:document.querySelector('#text-output').textContent,entry:document.querySelector('#text-percent').value,scale:Number(document.body.style.getPropertyValue('--text-scale')),auto:document.querySelector('#auto-text').getAttribute('aria-pressed')}));
  if(expected==='auto'){
    assert.equal(state.auto,'true');assert.equal(state.value,String(Math.round(state.scale*100)));assert.equal(state.entry,state.value);assert.equal(state.output,'auto · %');
  }else{
    assert.equal(state.auto,'false');assert.equal(state.value,String(expected));assert.equal(state.entry,state.value);assert.equal(state.output,'%');assert.equal(state.scale,expected/100);
  }
}
async function checkTextControls(page,context,width,crossTab){
  await checkText(page,'auto');await setText(page,130);await checkText(page,130);
  await page.reload();await checkText(page,130);
  await page.evaluate(()=>document.querySelector('#source-text').click());await checkText(page,100);
  await page.evaluate(()=>document.querySelector('#auto-text').click());await checkText(page,'auto');
  await page.setViewportSize({width:width===390?1280:390,height:900});await checkText(page,'auto');
  await page.setViewportSize({width,height:900});await checkText(page,'auto');
  if(crossTab){
    const other=await context.newPage(),errors=[];other.on('pageerror',error=>errors.push(error.message));await routePage(other,()=>false);await other.goto(page.url());
    await setText(other,160);await page.waitForFunction(()=>document.querySelector('#text-size').value==='160');await checkText(page,160);
    await other.evaluate(()=>document.querySelector('#source-text').click());await page.waitForFunction(()=>document.querySelector('#text-size').value==='100');await checkText(page,100);
    assert.deepEqual(errors,[]);await other.close();
  }
  await setText(page,175);await page.evaluate(()=>document.querySelector('#reset-preferences').click());await checkText(page,'auto');
}
(async()=>{
  const browser=await browsers[engine].launch({headless:true,...(process.env.ASTRA_BROWSER?{executablePath:process.env.ASTRA_BROWSER}:{})});
  let pageCases=0,legacyAnswerCases=0;
  try{
    for(const width of [1280,390])for(const file of ['index.html','levels/N5.html','papers/N5_sample_2009.html','papers-norubi/N5_sample_2009.html']){
      const reader=file.startsWith('papers'),context=await browser.newContext({viewport:{width,height:900}}),page=await context.newPage(),errors=[];
      let cached=false;page.on('pageerror',error=>errors.push(error.message));await routePage(page,()=>cached);
      await page.goto(origin+'/'+file);
      await checkPalette(page,'current');await checkAppearance(page);
      if(reader)await checkTextControls(page,context,width,file==='papers/N5_sample_2009.html');
      await page.evaluate(reader=>{
        const remember=document.querySelector('#remember');if(!remember.checked)remember.click();
        document.querySelector('.theme-catalog input[name=theme]').click();
        if(reader){
          const choice=document.querySelector('.answer-radio[data-correct=true]');
          document.querySelector('label[for="'+choice.id+'"]').click();
          document.querySelector('[name=auto-grade][value=hide]').click();
        }
      },reader);
      const before=await snapshot(page);checkShell(before,reader);
      for(const kind of ['inline','empty']){
        cached=kind;await page.reload();const after=await snapshot(page);checkShell(after,reader);await checkPalette(page,kind);
        assert.deepEqual(after,before,'Cached '+kind+' shells must preserve saved choices, preferences, and first feedback');
      }
      if(reader){
        await page.evaluate(()=>document.querySelector('[data-grade]').click());
        assert.equal(await page.locator('#score-dialog').evaluate(node=>node.open),true);
        await page.evaluate(()=>document.querySelector('#score-dialog').close());
      }
      assert.deepEqual(errors,[]);await page.close();const storageState=await context.storageState();await context.close();pageCases++;
      if(reader){
        // Seed a fresh context: unloading an active page would otherwise save
        // its current records over a fixture written directly to localStorage.
        for(const savedOrigin of storageState.origins)for(const entry of savedOrigin.localStorage)if(entry.name.includes(':paper:')){
          const record=JSON.parse(entry.value);
          for(const answer of Object.values(record.answers)){delete answer.firstFeedbackVersion;answer.completed=true;answer.firstCorrect=true;}
          entry.value=JSON.stringify(record);
        }
        const legacyContext=await browser.newContext({storageState,viewport:{width,height:900}}),legacy=await legacyContext.newPage(),legacyErrors=[];
        legacy.on('pageerror',error=>legacyErrors.push(error.message));await routePage(legacy,()=>'inline');await legacy.goto(origin+'/'+file);
        await legacy.evaluate(()=>document.querySelector('[data-grade]').click());
        assert.equal(await legacy.locator('#score-dialog').evaluate(node=>node.open),true);
        await legacy.evaluate(()=>{document.querySelector('#score-dialog').close();document.querySelector('[name=auto-grade][value=show]').click();});
        const restored=await snapshot(legacy);checkShell(restored,true);
        assert.equal(restored.theme,before.theme);assert.deepEqual(restored.selected,before.selected);
        assert.match(await legacy.locator('#progress').getAttribute('aria-label'),/First try 1\/1/);
        assert.doesNotMatch(await legacy.locator('#progress').getAttribute('aria-label'),/unavailable|earlier feedback/);
        assert.deepEqual(legacyErrors,[]);await legacyContext.close();legacyAnswerCases++;
      }
      console.log('PASS '+file+' at '+width+'px');
    }
    console.log(JSON.stringify({result:'pass',engine,current_and_two_cached_shell_cases:pageCases,legacy_answer_cases:legacyAnswerCases,slider_gap_and_palette_checks:true,repository_writes:false}));
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
