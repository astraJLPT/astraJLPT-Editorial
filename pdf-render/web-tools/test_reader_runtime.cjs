/* Real-browser checks for resizing, saved progress and timed practice.
 * Optional ASTRA_LAYOUT_BASELINE compares geometry with a local Git checkpoint.
 * Resources and browser storage are isolated from the user's browsing profile.
 */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),cp=require('node:child_process');
const browsers=require('playwright'),engine=process.env.ASTRA_ENGINE||'chromium';
const root=path.resolve(__dirname,'../..'),site=path.join(root,'astraJLPT'),origin='http://runtime.test',prefix='astraJLPT:web:v1:';
const types={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.woff2':'font/woff2','.png':'image/png','.svg':'image/svg+xml'};
const cache=new Map(),baseline=process.env.ASTRA_LAYOUT_BASELINE;
function asset(name,reference){
  const key=String(reference)+':'+name;if(cache.has(key))return cache.get(key);
  const body=reference&&baseline&&(name.endsWith('.html')||['assets/app.js','assets/site.css','assets/themes.css','assets/themes-no-script.css','assets/answer-marking.css','assets/pdf-typography.css'].includes(name))
    ?cp.execFileSync('git',['-c','safe.directory='+root.replaceAll('\\','/'),'show',baseline+':astraJLPT/'+name],{cwd:root,maxBuffer:4e6,windowsHide:true})
    :fs.readFileSync(path.join(site,name));cache.set(key,body);return body;
}
async function route(page,reference=false){
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/*',async r=>{const u=new URL(r.request().url());if(u.origin!==origin)return r.abort();const name=decodeURIComponent(u.pathname.slice(1));assert.ok(!name.includes('..'));await r.fulfill({body:asset(name,reference),contentType:types[path.extname(name)]||'application/octet-stream'});});
  return errors;
}
async function settle(page){
  await page.evaluate(async()=>{await document.fonts.ready;for(let i=0;i<4;i++)await new Promise(r=>requestAnimationFrame(r));});
}
async function setRubi(page,mode){
  await page.locator('[name=rubi][value='+mode+']').evaluate(input=>input.click());
  await settle(page);
}
async function checkExampleBubbles(browser){
  const page=await browser.newPage({viewport:{width:390,height:844}});
  try{
    await route(page);
    for(const rubi of ['show','hide']){
      for(const unit of ['N4_workbook_2012','N5_workbook_2012','N3_1996','N4_1996']){
        await page.goto(origin+'/papers/'+unit+'.html');await setRubi(page,rubi);
        const offsets=await page.locator('.example-answer-table:has(.answer-example-label)').evaluateAll(tables=>
          tables.map(table=>{
            const row=table.getBoundingClientRect();
            return [...table.querySelectorAll('.answer-bubble')].map(bubble=>{
              const rect=bubble.getBoundingClientRect();
              return rect.y+rect.height/2-(row.y+row.height/2);
            });
          }));
        assert.ok(offsets.length>0&&offsets.every(row=>row.length===4&&row.every(d=>Math.abs(d)<0.1)),
          'Four vertically centered example bubbles in '+rubi+'/'+unit);
      }
    }
  }finally{await page.close();}
}
async function checkMobileExamples(browser){
  const page=await browser.newPage({viewport:{width:390,height:844}});
  try{
    await route(page);
    await page.goto(origin+'/papers/N1_1996.html');await settle(page);
    const list=page.getByRole('list').filter({hasText:'飽和'});
    assert.equal(await list.getByRole('listitem').count(),4);
    const markers=await list.locator('li').first().evaluate(li=>[
      getComputedStyle(li).listStyleType,getComputedStyle(li,'::before').content
    ]);
    assert.deepEqual(markers,['none','counter(list-item)']);
    for(const [unit,first,vertical,short] of [['N4_workbook_2012','vocab-b060','vocab-b063','vocab-b065'],['N4_2000','vocab-b013','vocab-b014','reading-b005']]){
      await page.goto(origin+'/papers/'+unit+'.html');
      for(const width of [320,390,1280]){
        await page.setViewportSize({width,height:844});await settle(page);
        const columns=id=>page.locator('#'+id+' ol').evaluate(grid=>getComputedStyle(grid).gridTemplateColumns.split(/\s+/).length);
        assert.equal(await columns(vertical),1);
        if(width===1280)assert.equal(await columns(short),4);
        else assert.ok(await columns(first)<=2,unit+' example must fit at '+width);
      }
    }
    await page.setViewportSize({width:390,height:844});
    await page.goto(origin+'/papers/N4_07_2023.html');await settle(page);
    const gap=await page.locator('#reading-q012 .context-blank').evaluate(blank=>{
      const marks=blank.lastChild;
      if(marks.nodeType!==Node.TEXT_NODE||marks.data!=='。｣')return Infinity;
      const range=document.createRange();
      range.selectNodeContents(blank.querySelector('.blank-close').firstChild);
      const close=range.getBoundingClientRect();
      range.selectNodeContents(marks);
      return Math.abs(range.getBoundingClientRect().top-close.top)/close.height;
    });
    assert.ok(gap<.5,'The closing punctuation must share the line with the answer blank');
  }finally{await page.close();}
}
async function geometry(page){return page.evaluate(()=>{
  const p=document.querySelector('.paper').getBoundingClientRect();
  const rect=e=>{const r=e.getBoundingClientRect();return [r.left-p.left,r.top-p.top,r.width,r.height];};
  const nodes=[...document.querySelectorAll('.question,.section-heading,table[data-column-weights],.options-grid,.annotated-term,.example-options,.example-native-options,.example-source-options')];
  return {paper:[p.width,p.height],nodes:nodes.map(rect),labels:nodes.map(n=>n.tagName+'#'+n.id+'.'+n.className)};
});}
function compare(actual,expected,label){
  assert.equal(actual.nodes.length,expected.nodes.length,label+' nodes');let delta=0;
  const a=[...actual.paper,...actual.nodes.flat()],b=[...expected.paper,...expected.nodes.flat()];
  for(let i=0;i<a.length;i++)delta=Math.max(delta,Math.abs(a[i]-b[i]));
  const differences=actual.nodes.map((r,i)=>({node:actual.labels[i],actual:r,expected:expected.nodes[i],delta:Math.max(...r.map((v,j)=>Math.abs(v-expected.nodes[i][j])))})).filter(r=>r.delta>=.15).sort((a,b)=>b.delta-a.delta).slice(0,5);
  assert.ok(delta<.15,label+' geometry delta '+delta+' '+JSON.stringify(differences));return delta;
}
function questions(unit){const context={};vm.runInNewContext(asset('assets/questions/'+unit+'.js',false).toString(),context);return context.AstraQuestions.questions;}
async function checkTimerPreferences(browser){
  const preferenceKey=prefix+'preferences',saved={remember:true,values:{timerControls:false,allowUnclick:false,spacingVersion:2}};
  const context=await browser.newContext({storageState:{cookies:[],origins:[{origin,localStorage:[{name:preferenceKey,value:JSON.stringify(saved)}]}]}});
  const page=await context.newPage(),errors=await route(page);
  const click=selector=>page.locator(selector).evaluate(el=>el.click());
  const choice=name=>page.locator('[name='+name+']:checked').inputValue();
  const record=()=>page.evaluate(key=>JSON.parse(localStorage.getItem(key)),preferenceKey);
  const bannerReset='#timer-banner [data-timer-action=reset]',settingsReset='#timer-settings [data-timer-action=reset]';
  const dialog=page.locator('#timer-reset-dialog'),box=dialog.getByRole('checkbox',{name:"Don't show warning again"});
  const confirm=dialog.getByRole('button',{name:'reset timer',exact:true});
  try{
    await context.addInitScript(()=>{Date.now=()=>Date.UTC(2026,10,23);});
    await page.goto(origin+'/papers/N1_12_2025.html');
    assert.equal(await choice('timer-controls'),'show');assert.equal(await choice('unclick-answer'),'disable');
    assert.equal(Object.hasOwn((await record()).values,'timerControls'),false);
    assert.equal(await choice('timer-reset-warning'),'show');assert.equal(await page.locator('#timer-banner-controls').isVisible(),true);
    const peer=await context.newPage(),peerErrors=await route(peer);
    await peer.goto(origin+'/index.html');
    assert.equal(await peer.locator('#timer-limit-preview').textContent(),'1:50:00');
    await click('[name=timer-controls][value=hide]');
    await peer.waitForFunction(()=>document.querySelector('[name=timer-controls][value=hide]').checked);
    await page.reload();assert.equal(await choice('timer-controls'),'hide');
    assert.equal(await page.locator('#timer-banner-controls').isVisible(),false);
    await click('[name=timer-controls][value=show]');
    await page.locator('#settings>summary').click();await click('[name=settings-view][value=timer]');
    await page.locator('#timer-limit').fill('0:00:00');await page.locator('#timer-limit-form button').click();
    assert.equal(await page.locator('#timer-limit').evaluate(el=>el.validity.customError),true);
    await page.locator('#timer-settings [data-timer-action=exam]').click();
    assert.equal(await page.locator('#timer-limit').inputValue(),'1:50:00');
    assert.equal(await page.locator('#timer-limit').evaluate(el=>el.checkValidity()),true);
    await page.locator('#timer-limit-form button').click();
    assert.equal(await page.locator('#timer-edit-status').textContent(),'Time limit updated.');
    await page.locator('#timer-limit').fill('0:00:30');await page.locator('#timer-limit-form button').click();
    assert.equal(await page.locator('#timer-limit-preview').textContent(),'0:00:30');
    await page.locator('#timer-current').fill('0:00:12');await page.locator('#timer-current-form button').click();
    await page.locator(settingsReset).click();
    assert.equal(await dialog.getByRole('heading').textContent(),'are you sure?');assert.equal(await box.isChecked(),false);
    assert.equal(await page.locator('#timer-reset-description').textContent(),'this will reset the timer back to the time limit for this paper. your elapsed time will reset to 0.');
    await box.check();await dialog.getByRole('button',{name:'cancel'}).click();
    assert.equal(await choice('timer-reset-warning'),'show');assert.equal(await page.locator('#timer-display').textContent(),'0:00:12');
    assert.equal(await page.locator('#settings').evaluate(el=>el.open),true);
    assert.equal(await page.locator(settingsReset).evaluate(el=>el===document.activeElement),true);
    await page.locator(settingsReset).click();assert.equal(await box.isChecked(),false);
    await box.check();await page.keyboard.press('Escape');await dialog.waitFor({state:'hidden'});
    assert.equal(await page.locator('#settings').evaluate(el=>el.open),true);
    assert.equal(await page.locator(settingsReset).evaluate(el=>el===document.activeElement),true);
    await page.locator(settingsReset).click();assert.equal(await box.isChecked(),false);
    await confirm.click();assert.equal(await page.locator('#timer-display').textContent(),'0:00:30');
    assert.equal(await choice('timer-reset-warning'),'show');assert.equal(Object.hasOwn((await record()).values,'timerResetWarning'),false);
    await page.locator('#close-settings').click();await page.locator(bannerReset).click();
    await box.check();await confirm.click();assert.equal(await choice('timer-reset-warning'),'hide');
    assert.equal(await page.locator(bannerReset).evaluate(el=>el===document.activeElement),true);
    await peer.waitForFunction(()=>document.querySelector('[name=timer-reset-warning][value=hide]').checked);
    await page.reload();await page.locator(bannerReset).click();assert.equal(await dialog.isVisible(),false);
    await peer.locator('[name=timer-reset-warning][value=show]').evaluate(el=>el.click());
    await page.waitForFunction(()=>document.querySelector('[name=timer-reset-warning][value=show]').checked);
    await click('[name=timer-direction][value=up]');await page.locator(bannerReset).click();
    assert.equal(await box.isChecked(),false);assert.equal(await page.locator('#timer-reset-description').textContent(),'this will reset your elapsed time to 0.');
    await confirm.click();assert.equal(await page.locator('#timer-display').textContent(),'0:00:00');
    assert.equal(await page.locator('#timer-limit-preview').textContent(),'0:00:30');
    await click('[name=timer-enabled][value=no]');assert.equal(await page.locator('#timer-limit-preview').textContent(),'0:00:30');
    await click('[name=timer-enabled][value=yes]');await click('#remember');
    await page.locator(bannerReset).click();await box.check();await confirm.click();
    assert.equal(await choice('timer-reset-warning'),'hide');assert.deepEqual(await record(),{remember:false,epoch:1});
    await page.reload();assert.equal(await choice('timer-reset-warning'),'show');assert.equal(await page.locator('#remember').isChecked(),false);
    assert.deepEqual(errors,[]);assert.deepEqual(peerErrors,[]);
  }finally{await context.close();}
}
async function checkBanner(browser,rubi){
  const context=await browser.newContext({viewport:{width:1280,height:850}});
  const page=await context.newPage(),errors=await route(page);
  try{
    await page.goto(origin+'/papers/N1_12_2025.html');await setRubi(page,rubi);
    await page.evaluate(paused=>{
      if(paused){document.querySelector('[name=auto-grade][value=hide]').click();document.querySelector('#timer-banner [data-timer-action=pause]').click();}
      for(const node of [...document.querySelectorAll('.question[data-gradable=true]')].slice(0,3))node.querySelector('input').click();
    },rubi==='show');
    const layouts=new Set();
    let previous=[true,true,true],alreadyStacked=false;
    for(const width of [1280,910,830,700,665,651,650,640,590,560,545,530,510,450,420,400,390,385,380,375,370,360,335,320,315,300,290,280,270,265]){
      await page.setViewportSize({width,height:850});await settle(page);
      const state=await page.locator('.reader-subbar').evaluate(bar=>{
        const node=s=>bar.querySelector(s),rect=s=>node(s).getBoundingClientRect();
        const start=rect('.reader-start'),nav=rect('.section-nav'),actions=rect('.reader-actions');
        const controls=['.return-top','#timer-banner [data-timer-action=pause]','#timer-banner [data-timer-action=reset]','.settings summary'];
        const [top,pause,reset,settings]=controls.map(rect);
        return {layout:bar.dataset.layout,width:bar.clientWidth,height:bar.getBoundingClientRect().height,overflow:bar.scrollWidth-bar.clientWidth,
          labels:['.timer-action-label','.return-top-label','.settings-label-text'].map(s=>rect(s).width>0),stacked:reset.top>pause.top,
          gap:reset.left-pause.right,overlap:start.right>nav.left+.1||nav.right>actions.left+.1,
          heights:[top.height,pause.height,reset.height,settings.height],radii:controls.map(s=>getComputedStyle(node(s)).borderRadius),
          center:nav.left+nav.width/2,controlNames:controls.slice(1,3).map(s=>node(s).getAttribute('aria-label'))};
      });
      const label=rubi+' at '+width;layouts.add(state.layout);
      assert.equal(state.height,width>650&&!state.stacked?45:48,label);assert.ok(!state.overlap,label+' groups overlap');
      if(state.width>=265)assert.equal(state.overflow,0,label+' scrolls horizontally');
      assert.deepEqual(state.radii,['3px','3px','3px','3px'],label);
      assert.deepEqual(state.heights,state.stacked?[36,23,23,36]:[36,36,36,36],label);
      assert.ok(!state.labels[0]||state.labels[1],label+' timer words returned before top');
      assert.ok(!state.labels[1]||state.labels[2],label+' settings hidden before top');
      assert.ok(state.labels.every((visible,i)=>!visible||previous[i]),label+' a label reappeared');
      assert.ok(!alreadyStacked||state.stacked,label+' timer buttons unstacked');
      if(!state.stacked)assert.ok(Math.abs(state.gap)<.1,label+' separated timer hitboxes');
      assert.ok(state.controlNames.every(Boolean),label+' icon buttons need accessible names');
      if(width===1280)assert.ok(Math.abs(state.center-state.width/2)<1,label+' section links centered');
      if(width===650)assert.deepEqual(state.labels,[true,true,true],label+' full labels fit');
      if(width===315)assert.equal(state.stacked,false,label+' timer buttons still fit side by side');
      previous=state.labels;alreadyStacked=state.stacked;
    }
    assert.ok(layouts.has('two-lines')&&layouts.has('timer-icons')&&layouts.has('stacked'),[...layouts].join(', '));
    await page.locator('[name=timer-enabled][value=no]').evaluate(el=>el.click());await settle(page);
    assert.equal(await page.locator('#timer-banner').isVisible(),false);assert.equal(await page.locator('.reader-subbar').evaluate(el=>el.scrollWidth-el.clientWidth),0);
    // A finished historical paper has three-digit totals in both feedback modes.
    await page.goto(origin+'/papers/N1_1996.html');
    await page.evaluate(()=>{
      document.querySelector('[name=timer-enabled][value=yes]').click();
      document.querySelector('[name=spoil-all][value=yes]').click();
      document.querySelector('.paper-end [data-paper-action=spoil]').click();
      document.querySelector('#confirm-paper-action').click();
    });
    for(const mode of ['show','hide']){
      await page.locator('[name=auto-grade][value='+mode+']').evaluate(el=>el.click());await settle(page);
      assert.match(await page.locator('#progress-detail').textContent(),/121\/121/);
      assert.ok(await page.locator('.reader-subbar').evaluate(bar=>{
        const box=bar.getBoundingClientRect(),progress=bar.querySelector('#progress').getBoundingClientRect();
        return bar.scrollWidth===bar.clientWidth&&progress.top>=box.top&&progress.bottom<=box.bottom;
      }),rubi+' completed score must fit inside the toolbar at 265 px');
    }
    assert.deepEqual(errors,[]);
  }finally{await context.close();}
}
async function fillStorage(page,headroom){
  return page.evaluate(headroom=>{
    const fill=size=>localStorage.setItem('quota-test-filler','x'.repeat(size));
    let low=0,high=16*1024*1024;
    while(high-low>1){
      const mid=Math.floor((high+low)/2);
      try{fill(mid);low=mid;}catch(error){if(error.name!=='QuotaExceededError')throw error;high=mid;}
    }
    const size=low-headroom;fill(size);return size;
  },headroom);
}
async function assertCopyExceedsQuota(page,source,target){
  const result=await page.evaluate(({source,target})=>{
    try{localStorage.setItem(target,localStorage.getItem(source));return 'copied';}
    catch(error){return error.name;}
  },{source,target});
  assert.equal(result,'QuotaExceededError','Fixture must exceed real browser quota when copying the record');
}
async function checkNearQuotaSave(browser){
  const unit='N1_1999',rows=questions(unit).filter(q=>Number.isInteger(q.key)).slice(0,81);
  const legacyKey=prefix+'paper:'+unit,currentKey=prefix+'paper2:'+unit;
  const answers=Object.fromEntries(rows.slice(0,80).map(q=>[q.id,{selected:1,firstCorrect:false}]));
  const bindings=Object.fromEntries(rows.slice(0,80).map(q=>[q.id,q.binding]));
  const initial=JSON.stringify({answers,bindings,position:0});
  const entries=[
    {name:prefix+'preferences',value:JSON.stringify({remember:true,values:{timerEnabled:false,spacingVersion:2}})},
    {name:legacyKey,value:initial},{name:legacyKey+':norubi',value:'{"position":987}'}
  ];
  const context=await browser.newContext({storageState:{cookies:[],origins:[{origin,localStorage:entries}]}});
  try{
    const page=await context.newPage(),errors=await route(page),id=rows[0].id;
    await page.goto(origin+'/papers/'+unit+'.html');await settle(page);
    assert.equal(await page.locator('.answer-radio:checked').count(),80);
    const filler=await fillStorage(page,1600);
    await assertCopyExceedsQuota(page,legacyKey,currentKey);
    const choose=value=>page.locator('#'+id+'-'+value).evaluate(input=>input.click());
    await choose(2);await choose(3);
    await page.evaluate(()=>window.scrollTo(0,800));
    await page.waitForFunction(key=>JSON.parse(localStorage.getItem(key)).position===800,legacyKey);
    await page.reload();await settle(page);
    assert.equal(await page.locator('#'+id+'-3').isChecked(),true);
    assert.equal(await page.locator('.answer-radio:checked').count(),80);
    assert.match(await page.locator('#save-status').textContent(),/Saved on this browser/);
    const recovered=await page.evaluate(({legacyKey,currentKey})=>({
      paper:JSON.parse(localStorage.getItem(currentKey)??localStorage.getItem(legacyKey)),
      filler:localStorage.getItem('quota-test-filler').length,retired:localStorage.getItem(legacyKey+':norubi')
    }),{legacyKey,currentKey});
    assert.deepEqual(recovered.paper.answers,{...answers,[id]:{selected:3,firstCorrect:false}});
    assert.deepEqual(recovered.paper.bindings,bindings);assert.equal(recovered.paper.position,800);
    assert.equal(recovered.filler,filler);assert.equal(recovered.retired,'{"position":987}');
    // Leave just enough space for the 80-answer migration, then reopen the
    // paper so the next save cannot depend on a migration snapshot in memory.
    const copySize=await page.evaluate(key=>localStorage.getItem(key).length,legacyKey);
    const remainingFiller=await fillStorage(page,currentKey.length+copySize+24);
    await choose(4);
    const migrated=await page.evaluate(key=>JSON.parse(localStorage.getItem(key)),currentKey);
    assert.equal(Object.keys(migrated.answers).length,80);assert.equal(migrated.answers[id].selected,4);
    await page.reload();await settle(page);
    assert.equal(await page.locator('#'+id+'-4').isChecked(),true);
    const extra=rows[80],extraRadio=page.locator('#'+extra.id+'-'+extra.key);
    await extraRadio.evaluate(input=>input.click());
    await page.reload();await settle(page);
    assert.equal(await extraRadio.isChecked(),true,'Answer 81 must survive reload after the migration fits');
    assert.equal(await page.locator('.answer-radio:checked').count(),81);
    const final=await page.evaluate(({legacyKey,currentKey})=>({
      paper:JSON.parse(localStorage.getItem(currentKey)),filler:localStorage.getItem('quota-test-filler').length,
      retired:localStorage.getItem(legacyKey+':norubi')
    }),{legacyKey,currentKey});
    assert.deepEqual(final.paper.answers,{...answers,[id]:{selected:4,firstCorrect:false},[extra.id]:{selected:extra.key,firstCorrect:true}});
    assert.deepEqual(final.paper.bindings,{...bindings,[extra.id]:extra.binding});
    assert.equal(final.paper.position,800);
    assert.equal(final.filler,remainingFiller);assert.equal(final.retired,'{"position":987}');
    assert.deepEqual(errors,[]);
  }finally{await context.close();}
}
async function checkNearQuotaTimer(browser,legacyOffset=0,headroom=150){
  const unit='N1_1999',legacyKey=prefix+'timer:'+unit,currentKey=prefix+'timer2:'+unit;
  const now=Date.now(),timer={version:1,limit:8100000,elapsed:12000,startedAt:now-legacyOffset,
    running:true,direction:'down',expired:false,notified:false,revision:now};
  const retired=JSON.stringify({...timer,running:false,elapsed:987});
  const entries=[{name:legacyKey,value:JSON.stringify(timer)},
    {name:legacyKey+':norubi',value:retired},
    {name:prefix+'preferences',value:JSON.stringify({remember:true,values:{timerEnabled:true,timerDisabledTotal:legacyOffset,spacingVersion:2}})}];
  const context=await browser.newContext({storageState:{cookies:[],origins:[{origin,localStorage:entries}]}});
  try{
    const page=await context.newPage(),errors=await route(page);
    await page.goto(origin+'/levels/N1.html');await settle(page);
    const filler=await fillStorage(page,headroom);
    await assertCopyExceedsQuota(page,legacyKey,currentKey);
    await page.goto(origin+'/papers/'+unit+'.html');await settle(page);
    const banner=page.locator('#timer-banner'),pause=banner.locator('[data-timer-action=pause]');
    assert.equal(await banner.getAttribute('data-paused'),'false');
    await pause.evaluate(button=>button.click());
    assert.equal(await banner.getAttribute('data-paused'),'true');
    const paused=await page.locator('#timer-display').textContent();
    await page.reload();await settle(page);
    assert.equal(await banner.getAttribute('data-paused'),'true','An imported timer must stay paused after reload');
    await page.waitForTimeout(1100);
    assert.equal(await page.locator('#timer-display').textContent(),paused);
    const saved=await page.evaluate(({legacyKey,currentKey})=>({
      timer:JSON.parse(localStorage.getItem(currentKey)??localStorage.getItem(legacyKey)),
      filler:localStorage.getItem('quota-test-filler').length,retired:localStorage.getItem(legacyKey+':norubi')
    }),{legacyKey,currentKey});
    assert.equal(saved.timer.running,false);assert.ok(saved.timer.elapsed>=timer.elapsed);
    assert.ok(saved.timer.elapsed<=timer.elapsed+Date.now()-now+1000,'The historical clock offset must not count as study time');
    assert.equal(saved.timer.limit,timer.limit);
    assert.equal(saved.filler,filler);assert.equal(saved.retired,retired);
    assert.deepEqual(errors,[]);
  }finally{await context.close();}
}
async function checkSharedSession(browser,rubi){
  const context=await browser.newContext(),reader=await context.newPage(),peer=await context.newPage();
  const errors=[await route(reader),await route(peer)],unit='N1_12_2025';
  const url=origin+'/papers/'+unit+'.html',session=prefix+'paper2:'+unit;
  const qs=Array.from(questions(unit)).filter(q=>Number.isInteger(q.key)).slice(0,3);
  const click=(page,selector)=>page.locator(selector).first().evaluate(el=>el.click());
  const answer=(page,index)=>click(page,'#'+qs[index].id+'-'+qs[index].key);
  const record=()=>reader.evaluate(key=>JSON.parse(localStorage.getItem(key)),session);
  try{
    await reader.goto(url);await setRubi(reader,rubi);await peer.goto(url);await settle(reader);await settle(peer);
    await reader.evaluate(()=>window.scrollTo(0,2400));
    await reader.waitForFunction(key=>JSON.parse(localStorage.getItem(key))?.position===2400,session);
    await answer(peer,0);assert.equal((await record()).position,2400);
    await peer.goto(origin+'/levels/N1.html');assert.equal((await record()).position,2400);
    await reader.reload();await reader.waitForFunction(()=>window.scrollY===2400);
    // A tab that has merely restored a bookmark must not claim it on unload.
    await peer.goto(url);await peer.waitForFunction(()=>window.scrollY===2400);
    await reader.evaluate(()=>window.scrollTo(0,1000));
    await reader.waitForFunction(key=>JSON.parse(localStorage.getItem(key))?.position===1000,session);
    await peer.goto(origin+'/levels/N1.html');assert.equal((await record()).position,1000);
    // Saving is restarted on the catalog, which has no paper state of its own.
    await click(reader,'#timer-banner [data-timer-action=pause]');
    await click(peer,'#remember');await reader.waitForFunction(()=>!document.querySelector('#remember').checked);
    assert.equal(await record(),null);
    await click(peer,'#remember');await reader.waitForFunction(()=>document.querySelector('#remember').checked);
    assert.equal(await reader.locator('.answer-radio:checked').count(),0);
    assert.equal(await reader.locator('#timer-banner').getAttribute('data-paused'),'false');
    await peer.goto(url);await answer(peer,1);await answer(reader,2);
    await peer.waitForFunction(id=>document.getElementById(id).checked,qs[2].id+'-'+qs[2].key);
    const saved=await record();
    assert.deepEqual(Object.keys(saved.answers).sort(),qs.slice(1).map(q=>q.id).sort());
    for(const q of qs.slice(1))assert.deepEqual(saved.answers[q.id],{selected:q.key,firstCorrect:true});
    await reader.reload();assert.equal(await reader.locator('.answer-radio:checked').count(),2);
    // Suspend incoming events like a background tab. Its unrelated settings edit
    // can observe the new preferences before its first answer synchronizes.
    await reader.evaluate(()=>window.addEventListener('storage',e=>e.stopImmediatePropagation(),true));
    await click(peer,'#remember');await click(peer,'#remember');
    await click(peer,'#clear-answers');await click(peer,'#confirm-paper-action');await answer(peer,0);
    await click(reader,'[name=timer-controls][value=hide]');
    await answer(reader,2);
    assert.deepEqual(Object.keys((await record()).answers).sort(),[qs[0].id,qs[2].id].sort());
    for(const messages of errors)assert.deepEqual(messages,[]);
  }finally{await context.close();}
}
async function checkRubiBookmarks(browser){
  const context=await browser.newContext({viewport:{width:390,height:840}});
  try{
    const older=await context.newPage(),latest=await context.newPage();
    const errors=[await route(older),await route(latest)],url=origin+'/papers/N5_workbook_2012.html';
    const key=prefix+'paper2:N5_07_2010'; // The workbook's existing storage identity.
    const offset=node=>node.getBoundingClientRect().top-document.querySelector('.reader-subbar').getBoundingClientRect().bottom;
    async function mark(page,id){
      const target=page.locator('#'+id);
      await target.evaluate(node=>node.scrollIntoView());await settle(page);
      await page.evaluate(dy=>window.scrollBy(0,dy),(await target.evaluate(offset))+25);
      await page.waitForFunction(([key,id])=>JSON.parse(localStorage.getItem(key))?.anchor?.id===id,[key,id]);
    }
    await older.goto(url);await settle(older);await mark(older,'vocab-q047');
    await latest.goto(url);await settle(latest);await mark(latest,'reading-q001');
    const read=()=>older.evaluate(key=>JSON.parse(localStorage.getItem(key)),key);
    const saved=await read();
    await latest.locator('#reading-q001 .answer-radio').first().evaluate(el=>el.click());
    await latest.goto(origin+'/papers/N4_sample_2009.html');await setRubi(latest,'hide');
    await older.waitForFunction(()=>document.body.dataset.rubi==='hide');await settle(older);
    await older.goto(origin+'/levels/N5.html'); // Flush any pending bookmark from the passive tab.
    assert.equal((await read()).positionUpdatedAt,saved.positionUpdatedAt);
    await latest.goto(url);await settle(latest);
    assert.ok(Math.abs(await latest.locator('#reading-q001').evaluate(offset)-saved.anchor.offset)<2);
    assert.equal(await latest.locator('#reading-q001 .answer-radio:checked').count(),1);
    for(const messages of errors)assert.deepEqual(messages,[]);
  }finally{await context.close();}
}
async function checkSharedFirstTry(browser,rubi){
  const context=await browser.newContext(),shown=await context.newPage(),hidden=await context.newPage();
  const errors=[await route(shown),await route(hidden)],unit='N1_12_2025';
  const session=prefix+'paper2:'+unit;
  const click=(page,selector)=>page.locator(selector).first().evaluate(node=>node.click());
  try{
    const url=origin+'/papers/'+unit+'.html';
    await shown.goto(url);await setRubi(shown,rubi);await click(shown,'[name=auto-grade][value=hide]');await hidden.goto(url);
    const q=hidden.locator('.question[data-gradable=true]').first();
    const id=await q.getAttribute('id'),key=Number(await q.getAttribute('data-key')),wrong=key%4+1;
    await click(hidden,'#'+id+'-'+wrong);
    await shown.waitForFunction(id=>document.getElementById(id).checked,id+'-'+wrong);
    const saved=()=>hidden.evaluate(({session,id})=>JSON.parse(localStorage.getItem(session)).answers[id],{session,id});
    assert.deepEqual(await saved(),{selected:wrong});
    await click(hidden,'#'+id+'-'+wrong); // Unclick before feedback resets the pending try.
    await shown.waitForFunction(id=>!document.getElementById(id).checked,id+'-'+wrong);
    await hidden.evaluate(()=>window.scrollTo(0,240));
    await hidden.waitForFunction(session=>JSON.parse(localStorage.getItem(session)).position>=200,session);
    await click(shown,'[data-grade]');await click(shown,'#score-dialog [data-dialog-close]');
    assert.equal(await shown.locator('body').getAttribute('data-grades-hidden'),'false');
    assert.equal(await hidden.locator('body').getAttribute('data-grades-hidden'),'true');
    await click(hidden,'#'+id+'-'+wrong);
    await shown.waitForFunction(({session,id})=>JSON.parse(localStorage.getItem(session)).answers[id]?.firstCorrect===false,{session,id});
    assert.ok(await hidden.evaluate(session=>JSON.parse(localStorage.getItem(session)).position>=200,session));
    await click(hidden,'#'+id+'-'+key);await click(hidden,'[name=auto-grade][value=show]');
    await shown.waitForFunction(()=>document.querySelector('#progress-detail').textContent==='First try 0/1');
    assert.deepEqual(await saved(),{selected:key,firstCorrect:false});
    assert.match(await shown.locator('#progress-count').textContent(),/^1 \/ /);
    await hidden.reload();assert.equal(await hidden.locator('#progress-detail').textContent(),'First try 0/1');
    await click(hidden,'#'+id+'-'+key);await click(hidden,'#'+id+'-'+key);
    await shown.waitForFunction(()=>document.querySelector('#progress-detail').textContent==='First try 1/1');
    assert.deepEqual(errors,[[],[]]);
  }finally{await context.close();}
}
async function checkSpoiling(browser,rubi){
  const unit='N1_workbook_2018',rows=questions(unit),mobile=rubi==='hide';
  const context=await browser.newContext({viewport:{width:mobile?390:1280,height:800},hasTouch:mobile,reducedMotion:'reduce'});
  const page=await context.newPage(),errors=await route(page);
  const click=selector=>page.locator(selector).first().evaluate(node=>node.click());
  const select=(name,value)=>click('[name="'+name+'"][value="'+value+'"]');
  const checked=()=>page.locator('.answer-radio:checked').count();
  const dialog=page.locator('#paper-action-dialog');
  const optional=page.locator('[data-paper-action]:visible');
  try{
    await page.goto(origin+'/papers/'+unit+'.html');await setRubi(page,rubi);
    await settle(page);
    assert.equal(await optional.count(),0);
    assert.equal(await page.locator('#clear-answers').isVisible(),true);
    const question=page.locator('.question:has(.star-solution)').first();
    const id=await question.getAttribute('id'),key=Number(await question.getAttribute('data-key')),wrong=key%4+1;
    const choose=value=>click('#'+id+'-'+value);
    const order=question.locator('.star-solution'),extra=question.locator('[data-spoiled]');
    const styles=()=>question.evaluate(q=>{
      const option=q.querySelector('[data-correct=true]+.option'),number=option.querySelector('.option-number'),word=option.querySelector('.option-text');
      const snapshot={};
      for(const input of document.querySelectorAll('[name=marking]')){
        input.click();
        const box=getComputedStyle(option),text=getComputedStyle(word),ring=getComputedStyle(number,'::before');
        snapshot[input.value]=[box.outlineColor,box.backgroundColor,box.borderRadius,text.color,text.textShadow,text.webkitTextStroke,ring.content,ring.borderTopColor,getComputedStyle(number,'::after').display];
      }
      return snapshot;
    });
    await choose(wrong);
    assert.equal(await extra.count(),0);
    await select('auto-spoil','yes');
    assert.equal(await extra.inputValue(),String(key));
    assert.equal(await extra.isChecked(),false);
    assert.equal(await checked(),1);
    assert.equal(await order.isVisible(),true);
    const graded=await styles();
    const gutter=await question.locator('.margin-answer').evaluateAll(nodes=>nodes.map(node=>{
      const content=getComputedStyle(node,'::before').content;
      return {digit:content==='attr(data-choice)'?JSON.stringify(node.dataset.choice):content,
        symbol:getComputedStyle(node,'::after').content,y:node.getBoundingClientRect().top};
    }));
    assert.deepEqual(gutter.map(m=>[m.digit,m.symbol]),[['"'+wrong+'"','"✕"'],['"'+key+'"','"✓"']]);
    assert.ok(gutter[1].y>gutter[0].y);
    await select('star-behavior','hide');assert.equal(await order.isVisible(),false);
    await select('star-behavior','show');await select('auto-grade','hide');
    const neutral=await styles();
    await select('marking','number');
    const number=question.locator('.answer-radio:checked + .option .option-number');
    assert.equal(await number.evaluate(n=>getComputedStyle(n,'::before').transform),'none','Hidden grades use the neutral number ring');
    await select('marking','margin');
    assert.equal(await order.isVisible(),true);
    assert.equal(await question.locator('.option-feedback:visible').count(),0);
    assert.equal(await question.locator('.spoiled-margin').evaluate(n=>getComputedStyle(n,'::after').content),'"•"');
    await choose(key);assert.equal(await extra.count(),0);assert.equal(await checked(),1);
    assert.deepEqual(await styles(),neutral,'Neutral revealed and selected choices use the same twelve styles');
    await select('auto-grade','show');
    assert.deepEqual(await styles(),graded,'Revealed correct choices use the real markings');
    await choose(key);assert.equal(await checked(),0);assert.equal(await order.isVisible(),false);
    await choose(wrong);await page.reload();await settle(page);
    assert.equal(await extra.count(),1);
    await select('unclick-answer','disable');await choose(wrong);assert.equal(await extra.count(),1);
    await select('unclick-answer','allow');await choose(wrong);assert.equal(await extra.count(),0);
    await select('spoil-all','yes');await select('auto-grade','hide');
    assert.equal(await optional.count(),3);
    const edges=await page.evaluate(()=>{
      const rect=selector=>document.querySelector(selector).getBoundingClientRect();
      const top=rect('[data-practice=top]'),grade=rect('[data-practice=top] [data-grade]');
      return [rect('[data-practice=top] [data-paper-action=spoil]').left-rect('.paper-end [data-paper-action=spoil]').left,
        rect('[data-practice=top] [data-paper-action=clear]').right-rect('#clear-answers').right,(grade.left+grade.right-top.left-top.right)/2];
    });
    assert.ok(edges.every(x=>Math.abs(x)<1),'Top and bottom actions share their insets and grading is centered');
    const topSpoil=page.locator('[data-practice=top] [data-paper-action=spoil]');
    await topSpoil.click();
    assert.equal(await dialog.locator('h2').textContent(),'are you sure?');
    assert.equal(await dialog.locator('.table-flip span').first().textContent(),'(╯°□°)╯︵ ┻━┻');
    const cancel=dialog.locator('#cancel-paper-action');
    await dialog.locator('input').check();
    if(!mobile){
      await cancel.hover();assert.equal(await dialog.locator('.table-flip span').last().isVisible(),true);
    }
    await cancel.evaluate(el=>el.addEventListener('click',()=>{window.cancelPreview=el.closest('dialog').open&&getComputedStyle(document.querySelector('.table-flip span+span')).display!=='none';},{once:true}));
    if(mobile)await cancel.tap();else await cancel.click();
    assert.equal(await page.evaluate(()=>window.cancelPreview),true);
    await dialog.waitFor({state:'hidden'});assert.equal(await checked(),0);
    assert.equal(await topSpoil.evaluate(el=>document.activeElement===el),true);
    assert.equal(await page.locator('[name=clear-spoil-warning]:checked').inputValue(),'show');
    // A neutral bulk fill stays pending until the first explicit grade.
    await click('.paper-end [data-paper-action=spoil]');await click('#confirm-paper-action');
    const paperKey=await page.evaluate(prefix=>Object.keys(localStorage).find(k=>k.startsWith(prefix+'paper2:')),prefix);
    const savedAnswers=()=>page.evaluate(k=>JSON.parse(localStorage[k]).answers,paperKey);
    assert.equal(Object.values(await savedAnswers()).filter(a=>'firstCorrect' in a).length,0);
    await click('[data-grade]');await click('#score-dialog [data-dialog-close]');
    assert.equal(Object.values(await savedAnswers()).filter(a=>a.firstCorrect).length,70);
    await click('#clear-answers');
    assert.equal(await cancel.textContent(),'Cancel');assert.equal(await dialog.locator('#confirm-paper-action').textContent(),'Clear');
    await click('#confirm-paper-action');await select('auto-grade','show');
    await page.evaluate(rows=>rows.slice(0,40).forEach((q,i)=>document.getElementById(q.id+'-'+(i<31?q.key:q.key%4+1)).click()),rows);
    assert.equal(await page.locator('#progress-detail').textContent(),'First try 31/40');
    await click('.paper-end [data-paper-action=spoil]');await dialog.locator('input').check();await click('#confirm-paper-action');
    assert.equal(await page.locator('#progress-detail').textContent(),'First try 61/70');
    assert.equal(await page.locator('#progress-count').textContent(),'70 / 70');
    assert.equal(await page.locator('#timer-banner').getAttribute('data-paused'),'true');
    const last=rows.at(-1);await click('#'+last.id+'-'+last.key);
    assert.equal(await page.locator('#progress-detail').textContent(),'First try 60/69');
    await click('[data-practice=top] [data-paper-action=spoil]');assert.equal(await dialog.isVisible(),false);
    await click('[data-paper-action=clear]');assert.equal(await checked(),0);
    assert.equal(await page.locator('#timer-banner').getAttribute('data-paused'),'false');
    assert.equal(await page.locator('[name=timer-reset-warning]:checked').inputValue(),'show');
    await select('spoil-all','no');await select('clear-spoil-warning','show');await choose(wrong);
    const clear=page.locator('#clear-answers');
    await clear.click();await cancel.click();assert.equal(await checked(),1);
    assert.equal(await clear.evaluate(el=>document.activeElement===el),true);
    await select('spoil-all','yes');
    // Reopen the shared dialog before the close event from Clear is delivered.
    await page.evaluate(()=>{
      const dialog=document.querySelector('#paper-action-dialog');
      document.querySelector('#clear-answers').click();
      const closed=new Promise(resolve=>dialog.addEventListener('close',resolve,{once:true}));
      document.querySelector('#confirm-paper-action').click();
      document.querySelector('.paper-end [data-paper-action=spoil]').click();
      return closed;
    });
    assert.equal(await dialog.isVisible(),true);
    await click('#confirm-paper-action');
    assert.equal(await checked(),rows.filter(q=>Number.isInteger(q.key)).length);
    assert.equal(await dialog.isVisible(),false);
    assert.deepEqual(errors,[]);
  }finally{await context.close();}
}
async function checkTimedPaper(browser,rubi){
  const unit='N1_workbook_2018',rows=questions(unit),first=rows[0],second=rows[1];
  const context=await browser.newContext({viewport:{width:rubi==='show'?1280:390,height:900}});
  const page=await context.newPage(),errors=await route(page);
  await context.addInitScript(()=>{
    let now=Date.UTC(2026,10,20);Date.now=()=>now;
    window.advancePracticeTime=seconds=>{now+=seconds*1000;window.dispatchEvent(new Event('focus'));};
  });
  const click=selector=>page.locator(selector).first().evaluate(node=>node.click());
  const answer=(q,value)=>page.locator('label[for="'+q.id+'-'+value+'"]').click();
  const grade=()=>click('[data-grade]');
  const closeScore=()=>click('#score-dialog [data-dialog-close]');
  const advance=seconds=>page.evaluate(n=>window.advancePracticeTime(n),seconds);
  const setTime=(name,value)=>page.evaluate(([name,value])=>{
    document.querySelector('#timer-'+name).value=value;
    document.querySelector('#timer-'+name+'-form').requestSubmit();
  },[name,value]);
  try{
    await page.goto(origin+'/papers/'+unit+'.html');await setRubi(page,rubi);
    assert.equal(await page.locator('[name=unclick-answer]:checked').inputValue(),'allow');
    const settings=await page.locator('[data-settings=marking]').evaluate(root=>({
      headings:[...root.querySelectorAll('h3')].slice(0,3).map(h=>h.textContent),
      labels:[...root.querySelectorAll('[name=unclick-answer]+span')].map(el=>el.firstChild.textContent),
      descriptions:[...root.querySelectorAll('[name=unclick-answer]+span small')].map(el=>el.textContent),
      font:getComputedStyle(root.querySelector('.unclick-click')).font,
      reference:getComputedStyle(root.querySelector('[name=auto-grade][value=hide]+span small')).font
    }));
    assert.deepEqual(settings.headings,['answer mode','unclick answer','STAR behavior']);
    assert.deepEqual(settings.labels,['allow','disable']);
    assert.deepEqual(settings.descriptions,['click again to unclick',"don't allow unclick"]);
    assert.equal(settings.font,settings.reference);
    const wrong=first.key%4+1,nextWrong=wrong%4+1;
    await answer(first,wrong);
    const writes=await page.evaluate(id=>{
      const observer=new MutationObserver(()=>{});
      observer.observe(document.querySelector('#progress'),{subtree:true,childList:true,characterData:true,attributes:true});
      document.getElementById(id).click();
      const count=observer.takeRecords().length;observer.disconnect();return count;
    },first.id+'-'+nextWrong);
    assert.equal(writes,0,'Switching between incorrect choices must reuse the progress display');
    assert.equal(await page.locator('#'+first.id+'-'+nextWrong).isChecked(),true);
    await answer(first,first.key);
    assert.match(await page.locator('#progress').getAttribute('aria-label'),/First try 0\/1/);
    await answer(first,first.key);
    assert.equal(await page.locator('.answer-radio:checked').count(),0);
    assert.doesNotMatch(await page.locator('#progress').getAttribute('aria-label'),/First try/);
    await answer(first,first.key);
    assert.match(await page.locator('#progress').getAttribute('aria-label'),/First try 1\/1/);
    await click('[name=unclick-answer][value=disable]');await page.reload();
    await answer(first,first.key);assert.equal(await page.locator('.answer-radio:checked').count(),1);
    await click('[name=unclick-answer][value=allow]');
    await page.locator('#'+first.id+'-'+first.key).focus();await page.keyboard.press('Space');
    assert.equal(await page.locator('.answer-radio:checked').count(),0,'Space clears the selected radio');
    await page.keyboard.press('Space');await page.keyboard.press('ArrowRight');
    assert.equal(await page.locator('.answer-radio:checked').count(),1);
    assert.equal(await page.locator('#'+first.id+'-'+first.key).isChecked(),false);
    await answer(first,first.key);await answer(second,second.key%4+1);
    await click('[name=auto-grade][value=hide]');
    await click('[name=timer-enabled][value=no]');
    await advance(5519);await grade();
    assert.equal(await page.locator('#score-total').textContent(),'Written subtotal: 1 / 120');
    assert.equal(await page.locator('#score-time').textContent(),'1:31:59 / 1:50:00');
    const breakdown=await page.locator('#score-sections tr').first().locator('td').nth(1).evaluate(cell=>({
      text:cell.textContent,correct:cell.querySelector('.score-correct').textContent,wrong:cell.querySelector('.score-wrong').textContent,
      correctColor:getComputedStyle(cell.querySelector('.score-correct')).color,wrongColor:getComputedStyle(cell.querySelector('.score-wrong')).color,
      correctTheme:getComputedStyle(document.querySelector('.unclick-click')).color,wrongTheme:getComputedStyle(document.querySelector('.unclick-clear')).color
    }));
    assert.equal(breakdown.text,'1 correct · 1 wrong · 43 unanswered');
    assert.equal(breakdown.correct,'1 correct');assert.equal(breakdown.wrong,'1 wrong');
    assert.equal(breakdown.correctColor,breakdown.correctTheme);assert.equal(breakdown.wrongColor,breakdown.wrongTheme);
    assert.equal(await page.locator('#score-time').getAttribute('data-overtime'),'false');
    assert.equal(await page.locator('#score-warning').textContent(),'Warning: 68 unanswered questions. The timer is still running down.');
    await advance(1081);assert.equal(await page.locator('#score-time').textContent(),'1:50:00 / 1:50:00');
    assert.equal(await page.locator('#score-time').getAttribute('data-overtime'),'false');
    await advance(1264);assert.equal(await page.locator('#score-time').textContent(),'2:11:04 / 1:50:00');
    assert.equal(await page.locator('#score-time').getAttribute('data-overtime'),'true');
    assert.match(await page.locator('#score-warning').textContent(),/overtime/);
    assert.equal(await page.locator('#time-up-dialog').isVisible(),false);
    await closeScore();await grade(); // Hide grade before continuing.
    await click('[name=timer-enabled][value=yes]');
    if(await page.locator('#time-up-dialog').isVisible())await click('#time-up-dialog [data-dialog-close]');
    assert.equal(await page.locator('#timer-display').textContent(),'0:00:00');
    await click('[data-timer-action=reset]');await click('#confirm-timer-reset');await click('[name=timer-enabled][value=no]');
    await advance(600);await click('[name=timer-enabled][value=yes]');
    assert.equal(await page.locator('#timer-display').textContent(),'1:40:00');
    if(rubi==='show')await click('[name=auto-grade][value=show]');
    await page.evaluate(()=>{
      for(const q of document.querySelectorAll('.question[data-gradable=true]')){
        if(!q.querySelector(':checked'))q.querySelector('.answer-radio').click();
      }
    });
    await advance(300);assert.equal(await page.locator('#timer-display').textContent(),'1:40:00');
    await click('[data-timer-action=pause]');assert.equal(await page.locator('#timer-frozen-dialog').isVisible(),true);
    assert.equal(await page.locator('#timer-frozen-description').textContent(),'You have attempted every question in the paper, your timer has been frozen.');
    assert.equal(await page.locator('#timer-frozen-time').textContent(),'0:10:00 / 1:50:00');
    await click('#timer-frozen-dialog [data-dialog-close]');
    await click('[name=timer-direction][value=up]');await setTime('current','2:11:04');await click('[data-timer-action=pause]');
    assert.equal(await page.locator('#timer-frozen-time').textContent(),'2:11:04 / 1:50:00');
    assert.equal(await page.locator('#timer-frozen-time').getAttribute('data-overtime'),'true');
    await click('#timer-frozen-dialog [data-dialog-close]');await click('[data-timer-action=reset]');await click('#confirm-timer-reset');
    await advance(120);
    assert.equal(await page.locator('#timer-display').textContent(),'0:00:00','Reset preserves a completed paper’s freeze');
    await click('[name=timer-direction][value=down]');
    await setTime('limit','2:00:00');await setTime('current','1:45:00');await advance(30);
    await click('[name=auto-grade][value=hide]');await grade();
    assert.equal(await page.locator('#score-time').textContent(),'0:15:00 / 2:00:00');
    assert.equal(await page.locator('#score-warning').isVisible(),false);
    await closeScore();await page.reload();await advance(60);
    assert.equal(await page.locator('#timer-display').textContent(),'1:45:00');
    await answer(first,first.key);await advance(5);
    assert.equal(await page.locator('#timer-display').textContent(),'1:44:55');
    await grade();assert.match(await page.locator('#score-warning').textContent(),/^Warning: 1 unanswered question\./);
    await closeScore();await click('[name=timer-direction][value=up]');await grade();await grade();
    assert.match(await page.locator('#score-warning').textContent(),/counting up/);
    await closeScore();await click('[data-timer-action=pause]');await grade();await grade();
    assert.match(await page.locator('#score-warning').textContent(),/timer is paused/);
    await closeScore();
    if(rubi==='show'){
      const peer=await context.newPage(),peerErrors=await route(peer);
      await peer.goto(page.url());
      await answer(first,first.key);
      await peer.waitForFunction(()=>document.querySelectorAll('.answer-radio:checked').length===70);
      await peer.locator('label[for="'+first.id+'-'+first.key+'"]').click();
      await page.waitForFunction(()=>document.querySelectorAll('.answer-radio:checked').length===69);
      await peer.close();await page.reload();
      assert.equal(await page.locator('.answer-radio:checked').count(),69);
      assert.equal(await page.locator('#timer-banner').getAttribute('data-paused'),'true');
      assert.deepEqual(peerErrors,[]);
    }
    assert.deepEqual(errors,[]);
  }finally{await context.close();}
}
(async()=>{
  const browser=await browsers[engine].launch({headless:true,...(process.env.ASTRA_BROWSER?{executablePath:process.env.ASTRA_BROWSER}:{})});let checks=0;
  try{
    await checkNearQuotaSave(browser);checks++;console.log('PASS edited answers, bookmarks, and answer 81 after near-quota migration');
    await checkNearQuotaTimer(browser);await checkNearQuotaTimer(browser,54000,16);
    checks++;console.log('PASS paused imported timers survive near-quota reloads with and without a clock offset');
    await checkExampleBubbles(browser);checks++;
    await checkMobileExamples(browser);checks++;
    for(const unit of ['N1_1999','N3_07_2012','N5_sample_2009']){
      const context=await browser.newContext({viewport:{width:1280,height:900}}),page=await context.newPage(),errors=await route(page);
      await context.addInitScript(({prefix})=>{if(!localStorage.getItem(prefix+'preferences'))localStorage.setItem(prefix+'preferences',JSON.stringify({remember:true,values:{timerEnabled:false,spacingVersion:2}}));},{prefix});
      await page.goto(origin+'/papers/'+unit+'.html');await settle(page);
      const referenceContext=await browser.newContext({storageState:await context.storageState(),viewport:{width:1280,height:900}}),reference=await referenceContext.newPage();
      const referenceErrors=await route(reference,true);await reference.goto(origin+'/papers/'+unit+'.html');await settle(reference);
      for(const width of [1280,1100,390,900,650,1280]){
        await page.setViewportSize({width,height:900});await settle(page);
        await reference.setViewportSize({width,height:900});await settle(reference);
        compare(await geometry(page),await geometry(reference),unit+' at '+width);assert.deepEqual(referenceErrors,[]);checks++;
      }
      await page.evaluate(()=>{window.auditProbes=0;new MutationObserver(rows=>{for(const row of rows)for(const n of row.addedNodes)if(n.nodeType===1&&n.getAttribute('aria-hidden')==='true'&&n.style.visibility==='hidden')window.auditProbes++;}).observe(document.querySelector('.paper'),{subtree:true,childList:true});document.querySelector('#settings').open=true;window.dispatchEvent(new Event('resize'));});
      await settle(page);assert.equal(await page.evaluate(()=>window.auditProbes),0,'Opening settings must reuse measurements');
      await page.evaluate(()=>{const field=document.querySelector('#text-size');field.value=130;field.dispatchEvent(new Event('input',{bubbles:true}));});await settle(page);
      assert.ok(await page.evaluate(()=>window.auditProbes)>0,'Text changes must invalidate measurements');
      await reference.evaluate(()=>{document.querySelector('#settings').open=true;const field=document.querySelector('#text-size');field.value=130;field.dispatchEvent(new Event('input',{bubbles:true}));});await settle(reference);
      compare(await geometry(page),await geometry(reference),unit+' enlarged text');
      for(const target of [page,reference])await target.evaluate(()=>{document.querySelector('#auto-text').click();const field=document.querySelector('#paper-zoom');field.value=170;field.dispatchEvent(new Event('input',{bubbles:true}));});
      await settle(page);await settle(reference);compare(await geometry(page),await geometry(reference),unit+' detached manual zoom');
      for(const width of [780,690,650,390]){await page.setViewportSize({width,height:900});await reference.setViewportSize({width,height:900});await settle(page);await settle(reference);compare(await geometry(page),await geometry(reference),unit+' manual zoom at '+width);}
      for(const target of [page,reference])await target.evaluate(()=>{document.querySelector('[name=spacing][value=compact]').click();document.querySelector('[data-zoom=fit]').click();});
      await settle(page);await settle(reference);compare(await geometry(page),await geometry(reference),unit+' compact spacing and fit width');
      for(const width of [390,1280]){
        for(const target of [page,reference]){
          await target.setViewportSize({width,height:900});
          await target.evaluate(()=>{document.querySelector('#source-text').click();document.querySelector('[name=spacing][value=standard]').click();document.querySelector('[data-zoom=auto]').click();});await settle(target);
        }
        for(const percent of [25,100,140,151,175,250,500,100]){
          for(const target of [page,reference]){await target.evaluate(value=>{const slider=document.querySelector('#paper-zoom');slider.value=value;slider.dispatchEvent(new Event('input',{bubbles:true}));},percent);await settle(target);}
          compare(await geometry(page),await geometry(reference),unit+' zoom '+percent+' at '+width);checks++;
        }
        // Two controls can change before a paint on a busy machine. Auto must
        // establish the same layout before manual magnification detaches it.
        for(const target of [page,reference])await target.evaluate(()=>{document.querySelector('[data-zoom=fit]').click();document.querySelector('[data-zoom=auto]').click();const slider=document.querySelector('#paper-zoom');slider.value=170;slider.dispatchEvent(new Event('input',{bubbles:true}));});
        await settle(page);await settle(reference);compare(await geometry(page),await geometry(reference),unit+' pending Auto at '+width);checks++;
      }
      await referenceContext.close();
      assert.deepEqual(errors,[]);await context.close();checks++;console.log('PASS resize and text-size geometry '+unit);
    }
    const unit='N5_sample_2009',q=questions(unit).filter(q=>Number.isInteger(q.key)),record={answers:{[q[0].id]:{selected:q[0].key,firstCorrect:false,attempts:2},[q[1].id]:{selected:q[1].key,firstCorrect:null}},position:1300,bindings:Object.fromEntries(q.map(q=>[q.id,q.binding]))};
    const rows=[{name:prefix+'preferences',value:JSON.stringify({remember:true,values:{autoGrade:false,timerEnabled:false,spacingVersion:2}})},{name:prefix+'paper:'+unit,value:JSON.stringify(record)}];
    const context=await browser.newContext({storageState:{cookies:[],origins:[{origin,localStorage:rows}]} ,viewport:{width:1280,height:900}}),page=await context.newPage();const errors=await route(page);
    await page.goto(origin+'/papers/'+unit+'.html');await settle(page);
    assert.equal(await page.evaluate(marker=>localStorage.getItem(marker),prefix+'maintenance:compact-papers:1'),null,'Direct readers must not run all-unit cleanup');
    assert.ok(Math.abs(await page.evaluate(()=>scrollY)-1300)<2,'Reading position restored');
    assert.equal(await page.locator('.answer-radio:checked').count(),2);
    await page.evaluate(()=>document.querySelector('[data-grade]').click());
    const saved=await page.evaluate(key=>JSON.parse(localStorage.getItem(key)),prefix+'paper2:'+unit);
    assert.equal(saved.answers[q[0].id].firstCorrect,false);assert.equal(saved.answers[q[1].id].firstCorrect,true);assert.equal(Object.keys(saved.bindings).length,2);
    assert.equal(saved.position,1300);assert.deepEqual(Object.keys(saved.answers[q[0].id]).sort(),['firstCorrect','selected']);
    await page.evaluate(()=>document.querySelector('#score-dialog').close());
    // A pre-update tab flushes its original answers and bookmark on pagehide.
    const peer=await context.newPage();await route(peer);await peer.goto(origin+'/levels/N5.html');
    await peer.evaluate(({key,record})=>window.addEventListener('pagehide',()=>localStorage.setItem(key,JSON.stringify(record))),{key:prefix+'paper:'+unit,record});
    const radio='#'+q[2].id+'-'+q[2].key;
    await page.locator(radio).evaluate(input=>input.click());
    await peer.goto(origin+'/index.html');await page.reload();await settle(page);
    assert.equal(await page.locator(radio).isChecked(),true);
    for(const id of ['clear-answers','confirm-paper-action'])await page.locator('#'+id).evaluate(button=>button.click());
    await page.reload();assert.equal(await page.locator('.answer-radio:checked').count(),0);
    assert.deepEqual(errors,[]);await context.close();checks++;console.log('PASS old bookmarks import and stale tab saves leave current answers intact');
    await checkRubiBookmarks(browser);checks++;console.log('PASS bookmarks across rubi changes and background tabs');
    for(const rubi of ['show','hide']){
      await checkSpoiling(browser,rubi);checks++;console.log('PASS auto-spoil, bulk fill and shared warnings '+rubi);
      await checkTimedPaper(browser,rubi);checks++;console.log('PASS answer selection and timed scoring '+rubi);
      await checkSharedSession(browser,rubi);checks++;console.log('PASS forget, new answers and bookmarks across tabs '+rubi);
      await checkSharedFirstTry(browser,rubi);checks++;console.log('PASS first feedback across graded and ungraded tabs '+rubi);
      await checkBanner(browser,rubi);checks++;console.log('PASS responsive banner '+rubi);
    }
    await checkTimerPreferences(browser);checks++;console.log('PASS timer controls, migration, and reset confirmation');
    const clockContext=await browser.newContext(),clockPage=await clockContext.newPage(),clockErrors=await route(clockPage);
    await clockPage.goto(origin+'/papers/N5_sample_2009.html');await clockPage.bringToFront();await settle(clockPage);
    const initial=await clockPage.locator('#timer-display').textContent();
    await clockPage.waitForFunction(value=>document.querySelector('#timer-display').textContent!==value,initial,{timeout:5000});
    await clockPage.evaluate(()=>document.querySelector('[data-timer-action=pause]').click());
    const paused=await clockPage.locator('#timer-display').textContent();await clockPage.waitForTimeout(1100);
    assert.equal(await clockPage.locator('#timer-display').textContent(),paused);
    await clockPage.evaluate(()=>document.querySelector('[data-timer-action=pause]').click());
    await clockPage.waitForFunction(value=>document.querySelector('#timer-display').textContent!==value,paused,{timeout:5000});
    assert.deepEqual(clockErrors,[]);await clockContext.close();checks++;console.log('PASS visible timer advances, pauses and resumes');
    console.log(JSON.stringify({status:'pass',checks,layoutBaseline:baseline||'fresh current reader'}));
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
