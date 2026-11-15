/* Percentage entry, slider scheduling, and palette equivalence in real browsers.
 * ASTRA_ENGINE / ASTRA_BROWSER select a browser. ASTRA_LAYOUT_BASELINE optionally
 * compares theme rendering with a Git checkpoint. Screenshots are opt-in and
 * written only to ASTRA_SCREENSHOTS; browser profiles and storage are isolated.
 */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process');
const browsers=require('playwright'),engine=process.env.ASTRA_ENGINE||'chromium';
const root=path.resolve(__dirname,'../..'),site=path.join(root,'astraJLPT'),origin='http://controls.test',prefix='astraJLPT:web:v1:';
const baseline=process.env.ASTRA_LAYOUT_BASELINE,cache=new Map();
const types={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.woff2':'font/woff2','.png':'image/png','.svg':'image/svg+xml'};
function asset(name,reference){
  const key=reference+':'+name;if(cache.has(key))return cache.get(key);
  const old=reference&&baseline&&(name.endsWith('.html')||['assets/app.js','assets/site.css','assets/themes.css'].includes(name));
  const body=old?cp.execFileSync('git',['-c','safe.directory='+root.replaceAll('\\','/'),'show',baseline+':astraJLPT/'+name],{cwd:root,maxBuffer:4e6,windowsHide:true}):fs.readFileSync(path.join(site,name));
  cache.set(key,body);return body;
}
async function route(page,reference=false){
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/*',async r=>{const u=new URL(r.request().url()),name=decodeURIComponent(u.pathname.slice(1));assert.ok(u.origin===origin&&!name.includes('..'));await r.fulfill({body:asset(name,reference),contentType:types[path.extname(name)]||'application/octet-stream'});});return errors;
}
async function settle(page){await page.evaluate(async()=>{await document.fonts.ready;for(let i=0;i<4;i++)await new Promise(r=>requestAnimationFrame(r));});}
async function preferences(page){return page.evaluate(key=>JSON.parse(localStorage.getItem(key)).values,prefix+'preferences');}
async function enter(page,key,value,action='Enter'){
  const field=page.locator('#'+key+'-percent');await field.fill(value);await field.press(action);await settle(page);
}
async function snapshot(page){return page.evaluate(()=>{
  const paper=document.querySelector('.paper'),p=paper.getBoundingClientRect();
  return [p.width,p.height,...[...paper.querySelectorAll('.question,.section-heading,.options-grid,table,.annotated-term')].flatMap(e=>{const r=e.getBoundingClientRect();return [r.x-p.x,r.y-p.y,r.width,r.height];})];
});}
function sameGeometry(a,b){assert.equal(a.length,b.length);assert.ok(a.every((n,i)=>Math.abs(n-b[i])<.15),'Typed and slider values must render the same paper');}
async function checkLayout(page){
  const boxes=await page.evaluate(()=>['text','zoom'].map(key=>{
    const field=document.querySelector('#'+key+'-percent'),row=field.closest('.sizing-control');
    const rect=e=>{const r=e.getBoundingClientRect();return {left:r.left,right:r.right,width:r.width,height:r.height};};
    return {field:rect(field),row:rect(row),slider:rect(row.querySelector('[type=range]')),label:rect(row.querySelector('label')),readout:rect(field.parentElement),viewport:innerWidth,name:field.getAttribute('aria-label'),labelFor:row.querySelector('label').htmlFor};
  }));
  for(const box of boxes){assert.ok(box.field.width>=35&&box.field.height>=26);assert.ok(box.label.right<box.readout.left+1);assert.ok(box.readout.right<=box.row.right+1);assert.ok(box.row.left>=0&&box.row.right<=box.viewport);assert.match(box.name,/percentage$/);assert.ok(box.labelFor);}
  for(const key of ['left','right','width','height'])assert.ok(Math.abs(boxes[0].field[key]-boxes[1].field[key])<.1,'Symmetric percentage fields: '+key);
  for(const key of ['left','width'])assert.ok(Math.abs(boxes[0].slider[key]-boxes[1].slider[key])<.1,'Aligned sliders: '+key);
}
async function palette(page,id,scripting){
  return page.evaluate(({id,scripting})=>{
    const radio=document.querySelector('#theme-'+id);radio.checked=true;if(scripting)radio.dispatchEvent(new Event('change',{bubbles:true}));
    const body=getComputedStyle(document.body),logo=getComputedStyle(document.querySelector('.wordmark'));
    return {background:body.backgroundColor,color:body.color,scheme:body.colorScheme,logo:logo.color,vars:['--bg','--raised','--text','--muted','--edge','--accent','--correct','--wrong','--theme-label'].map(k=>body.getPropertyValue(k).trim())};
  },{id,scripting});
}
(async()=>{
  const browser=await browsers[engine].launch({headless:true,...(process.env.ASTRA_BROWSER?{executablePath:process.env.ASTRA_BROWSER}:{})});let checks=0;
  try{
    for(const width of [1280,390,320])for(const directory of ['papers','papers-norubi']){
      const context=await browser.newContext({viewport:{width,height:900}});
      await context.addInitScript(prefix=>{if(!localStorage.getItem(prefix+'preferences'))localStorage.setItem(prefix+'preferences',JSON.stringify({remember:true,values:{timerEnabled:false,spacingVersion:2}}));},prefix);
      const page=await context.newPage(),errors=await route(page),requests=[];page.on('request',r=>requests.push(r.url()));
      await page.goto(origin+'/'+directory+'/N5_sample_2009.html');await settle(page);
      assert.equal(requests.some(u=>u.includes('themes-no-script.css')),false,'JS readers must not download the fallback palettes');
      await page.evaluate(()=>{document.querySelector('#settings').open=true;document.querySelector('[name=settings-view][value=reading]').click();});await settle(page);
      await checkLayout(page);
      if(process.env.ASTRA_SCREENSHOTS&&directory==='papers'){
        fs.mkdirSync(process.env.ASTRA_SCREENSHOTS,{recursive:true});await page.screenshot({path:path.join(process.env.ASTRA_SCREENSHOTS,engine+'-controls-'+width+'.png')});
      }
      const original=await snapshot(page),saved=await preferences(page);
      await page.locator('#text-percent').fill('137.6%');
      assert.deepEqual(await preferences(page),saved,'Typing must not reflow or save each partial keystroke');sameGeometry(await snapshot(page),original);
      await page.locator('#text-percent').press('Enter');await settle(page);
      assert.equal((await preferences(page)).text,138);assert.equal(await page.locator('#text-percent').inputValue(),'138');
      for(const invalid of ['', 'abc', 'NaN', 'Infinity', '1e2']){await enter(page,'text',invalid);assert.equal(await page.locator('#text-percent').inputValue(),'138');assert.equal((await preferences(page)).text,138);}
      await enter(page,'text','9999');assert.equal((await preferences(page)).text,500);
      await enter(page,'text','-4','Tab');assert.equal((await preferences(page)).text,25);
      await enter(page,'text','130');const typed=await snapshot(page);
      await page.evaluate(()=>{document.querySelector('#auto-text').click();const slider=document.querySelector('#text-size');slider.value=130;slider.dispatchEvent(new Event('input',{bubbles:true}));});await settle(page);sameGeometry(await snapshot(page),typed);
      await enter(page,'text','180','Escape');assert.equal((await preferences(page)).text,130);assert.equal(await page.locator('#text-percent').inputValue(),'130');assert.equal(await page.locator('#settings').evaluate(e=>e.open),true);
      await page.locator('#text-size').focus();await page.locator('#text-size').press('ArrowRight');await settle(page);assert.equal(await page.locator('#text-percent').inputValue(),'131');
      const batch=await page.evaluate(async()=>{
        const prototype=CSSStyleDeclaration.prototype,original=prototype.setProperty;let writes=0;
        prototype.setProperty=function(name,...args){if(this===document.body.style&&name==='--text-scale')writes++;return original.call(this,name,...args);};
        try{const slider=document.querySelector('#text-size');for(let n=110;n<=140;n++){slider.value=n;slider.dispatchEvent(new Event('input',{bubbles:true}));}for(let i=0;i<4;i++)await new Promise(r=>requestAnimationFrame(r));return {writes,scale:document.body.style.getPropertyValue('--text-scale')};}finally{prototype.setProperty=original;}
      });assert.equal(batch.writes,1,'One sizing transaction per input burst');assert.equal(batch.scale,'1.4');
      await enter(page,'text','100');await enter(page,'zoom','150.6');assert.equal((await preferences(page)).zoom,151);assert.ok(Number.isFinite((await preferences(page)).zoomWidth));
      const typedZoom=await snapshot(page);
      await page.evaluate(()=>{document.querySelector('[data-zoom=auto]').click();const slider=document.querySelector('#paper-zoom');slider.value=151;slider.dispatchEvent(new Event('input',{bubbles:true}));});await settle(page);sameGeometry(await snapshot(page),typedZoom);
      const bounds=await page.locator('#paper-zoom').evaluate(e=>({min:Number(e.min),max:Number(e.max)}));
      await enter(page,'zoom','9999');assert.equal((await preferences(page)).zoom,bounds.max);
      await enter(page,'zoom','0');assert.equal((await preferences(page)).zoom,bounds.min);
      await page.evaluate(()=>document.querySelector('[data-zoom=fit]').click());await settle(page);assert.match(await page.locator('#zoom-output').textContent(),/^fit · A4 · %$/);
      await enter(page,'zoom','130');assert.equal((await preferences(page)).zoomWidth,undefined);
      await page.evaluate(()=>document.querySelector('.answer-radio[data-correct=true]').click());
      const answers=await page.evaluate(prefix=>Object.fromEntries(Object.keys(localStorage).filter(k=>k.startsWith(prefix+'paper:')).map(k=>[k,JSON.parse(localStorage[k]).answers])),prefix);
      await page.evaluate(()=>{document.querySelector('#settings').open=true;});await settle(page);
      await enter(page,'text','125');await enter(page,'zoom','165');await page.reload();await settle(page);
      assert.equal(await page.locator('#text-percent').inputValue(),'125');assert.equal(await page.locator('#zoom-percent').inputValue(),'165');
      assert.deepEqual(await page.evaluate(prefix=>Object.fromEntries(Object.keys(localStorage).filter(k=>k.startsWith(prefix+'paper:')).map(k=>[k,JSON.parse(localStorage[k]).answers])),prefix),answers,'Sizing and reload preserve first feedback and answers');
      assert.deepEqual(errors,[]);await context.close();checks++;console.log('PASS percentage controls '+directory+' at '+width+'px');
    }
    // All palette declarations must be identical; only their state selector moves.
    if(baseline){
      const pictures=[];
      for(const reference of [true,false]){
        const context=await browser.newContext({viewport:{width:1280,height:900}});
        await context.addInitScript(prefix=>localStorage.setItem(prefix+'preferences',JSON.stringify({remember:true,values:{timerEnabled:false,spacingVersion:2}})),prefix);
        const page=await context.newPage(),errors=await route(page,reference);
        await page.goto(origin+'/papers-norubi/N1_1999.html');await settle(page);
        await page.evaluate(()=>{for(const [id,value]of [['text-size',125],['paper-zoom',175]]){const slider=document.querySelector('#'+id);slider.value=value;slider.dispatchEvent(new Event('input',{bubbles:true}));}});await settle(page);
        pictures.push(await page.screenshot({animations:'disabled'}));assert.deepEqual(errors,[]);await context.close();
      }
      assert.ok(pictures[0].equals(pictures[1]),'Simultaneous text and zoom changes must retain pixel-identical heading rendering');checks++;
      console.log('PASS paper pixels after simultaneous text-size and zoom changes');
      const oldRules=[...asset('assets/themes.css',true).toString().matchAll(/body:has\(#theme-([^:)]+):checked\)\{([^}]+)\}/g)].map(m=>[m[1],m[2]]);
      const newRules=[...asset('assets/themes.css',false).toString().matchAll(/body\[data-theme="([^"]+)"\]\{([^}]+)\}/g)].map(m=>[m[1],m[2]]);
      assert.equal(oldRules.length,190);assert.deepEqual(newRules,oldRules);
      for(const scripting of [true,false]){
        const currentContext=await browser.newContext({javaScriptEnabled:scripting}),referenceContext=await browser.newContext({javaScriptEnabled:scripting});
        const current=await currentContext.newPage(),reference=await referenceContext.newPage(),errors=await route(current),oldErrors=await route(reference,true);
        await current.goto(origin+'/index.html');await reference.goto(origin+'/index.html');
        for(const [id]of oldRules)assert.deepEqual(await palette(current,id,scripting),await palette(reference,id,scripting),'Palette '+id+'; JS='+scripting);
        assert.deepEqual(errors,[]);assert.deepEqual(oldErrors,[]);await currentContext.close();await referenceContext.close();checks++;
        console.log('PASS all 190 palettes with JavaScript '+(scripting?'enabled':'disabled'));
      }
    }
    console.log(JSON.stringify({status:'pass',engine,checks,baseline:baseline||null}));
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
