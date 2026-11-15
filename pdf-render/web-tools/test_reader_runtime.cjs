/* Real-browser checks for resizing, saved progress, and home-only maintenance.
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
  const body=reference&&baseline&&(name.endsWith('.html')||['assets/app.js','assets/site.css','assets/themes.css'].includes(name))
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
(async()=>{
  const browser=await browsers[engine].launch({headless:true,...(process.env.ASTRA_BROWSER?{executablePath:process.env.ASTRA_BROWSER}:{})});let checks=0;
  try{
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
    const saved=await page.evaluate(key=>JSON.parse(localStorage.getItem(key)),prefix+'paper:'+unit);
    assert.equal(saved.answers[q[0].id].firstCorrect,false);assert.equal(saved.answers[q[1].id].firstCorrect,true);assert.equal(Object.keys(saved.bindings).length,2);
    assert.equal(saved.position,1300);assert.deepEqual(Object.keys(saved.answers[q[0].id]).sort(),['firstCorrect','selected']);
    await page.evaluate(()=>document.querySelector('#score-dialog').close());
    await page.goto(origin+'/index.html');await page.waitForFunction(marker=>localStorage.getItem(marker)==='1',prefix+'maintenance:compact-papers:1');
    assert.deepEqual(errors,[]);await context.close();checks++;console.log('PASS bookmarked paper keeps progress before home cleanup');

    const all=[];let papers=0;
    for(const directory of ['papers','papers-norubi'])for(const name of fs.readdirSync(path.join(site,directory))){
      if(!name.endsWith('.html'))continue;const markup=asset(directory+'/'+name,false).toString(),match=/<script[^>]*id="page-data"[^>]*>(.*?)<\/script>/s.exec(markup);if(!match)continue;
      const data=JSON.parse(match[1]),key=prefix+'paper:'+(data.paper.storage_unit||data.paper.unit)+(directory==='papers-norubi'?':norubi':'');
      const binding=Object.fromEntries(questions(data.paper.unit).map(q=>[q.id,q.binding]));all.push({name:key,value:JSON.stringify({answers:{},bindings:binding,position:++papers})});
    }
    assert.equal(papers,402);all.push({name:'unrelated',value:'retain'},{name:prefix+'timer:retained',value:'{"elapsed":1200}'});
    const homeContext=await browser.newContext({storageState:{cookies:[],origins:[{origin,localStorage:all}]}}),home=await homeContext.newPage();const homeErrors=await route(home);let fetchedQuestions=0;
    home.on('request',r=>{if(r.url().includes('/assets/questions/'))fetchedQuestions++;});
    await home.goto(origin+'/index.html');await home.waitForFunction(marker=>localStorage.getItem(marker)==='1',prefix+'maintenance:compact-papers:1');
    const cleaned=await home.evaluate(prefix=>Object.keys(localStorage).filter(k=>k.startsWith(prefix+'paper:')).map(k=>JSON.parse(localStorage[k])),prefix);
    assert.equal(cleaned.length,402);assert.ok(cleaned.every(r=>r.position>0&&Object.keys(r.bindings).length===0));assert.equal(fetchedQuestions,0);
    assert.equal(await home.evaluate(()=>localStorage.getItem('unrelated')),'retain');assert.equal(await home.evaluate(key=>localStorage.getItem(key),prefix+'timer:retained'),'{"elapsed":1200}');
    assert.deepEqual(homeErrors,[]);await homeContext.close();checks++;console.log('PASS one home visit cleans all 402 readers without question downloads');
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
