/* Reader settings layout, percentage entry, slider scheduling, and palette equivalence in real browsers.
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
  const old=reference&&baseline&&(name.endsWith('.html')||['assets/app.js','assets/site.css','assets/themes.css','assets/themes-no-script.css','assets/answer-marking.css','assets/pdf-typography.css'].includes(name));
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
function sameGeometry(a,b,reason='Typed and slider values must render the same paper'){assert.equal(a.length,b.length);const i=a.findIndex((n,i)=>Math.abs(n-b[i])>=.15);assert.ok(i<0,reason+' (coordinate '+i+', '+a[i]+' vs '+b[i]+')');}
async function checkLayout(page){
  const boxes=await page.evaluate(()=>['text','zoom'].map(key=>{
    const field=document.querySelector('#'+key+'-percent'),row=field.closest('.sizing-control');
    const rect=e=>{const r=e.getBoundingClientRect();return {left:r.left,right:r.right,width:r.width,height:r.height};};
    return {field:rect(field),row:rect(row),slider:rect(row.querySelector('[type=range]')),label:rect(row.querySelector('label')),readout:rect(field.parentElement),viewport:innerWidth,name:field.getAttribute('aria-label'),labelFor:row.querySelector('label').htmlFor};
  }));
  for(const box of boxes){assert.ok(box.field.width>=35&&box.field.height>=26);assert.ok(box.label.right<box.readout.left+1);assert.ok(box.readout.right<=box.row.right+1);assert.ok(box.row.left>=0&&box.row.right<=box.viewport);assert.match(box.name,/percentage$/);assert.ok(box.labelFor);}
  for(const key of ['left','right','width','height'])assert.ok(Math.abs(boxes[0].field[key]-boxes[1].field[key])<.1,'Symmetric percentage fields: '+key);
  for(const key of ['left','width'])assert.ok(Math.abs(boxes[0].slider[key]-boxes[1].slider[key])<.1,'Aligned sliders: '+key);
  const samples=await page.locator('.rubi-setting label').evaluateAll(labels=>labels.map(label=>{
    const small=label.querySelector('small'),ruby=small.querySelector('ruby');
    const bounds=node=>{const range=document.createRange();range.selectNodeContents(node);return range.getBoundingClientRect();};
    const titleText=small.parentElement.firstChild,title=bounds(titleText),base=bounds((ruby||small).firstChild).top;
    // Measure the visible gap between show and み, excluding both fonts' unused ascent and descent.
    const canvas=document.createElement('canvas').getContext('2d');
    const inkBounds=(node,box=bounds(node))=>{
      const font=getComputedStyle(node.parentElement);
      canvas.font=font.fontWeight+' '+font.fontSize+' '+font.fontFamily;
      const ink=canvas.measureText(node.data);
      return {top:box.top+ink.fontBoundingBoxAscent-ink.actualBoundingBoxAscent,
        bottom:box.bottom-ink.fontBoundingBoxDescent+ink.actualBoundingBoxDescent};
    };
    const clearance=ruby?inkBounds(ruby.querySelector('rt').firstChild).top-inkBounds(titleText,title).bottom:null;
    return {base,captionGap:base-title.bottom,clearance,height:label.getBoundingClientRect().height,
      fits:small.scrollWidth<=label.clientWidth,face:getComputedStyle(small).fontFamily};
  }));
  assert.equal(samples.length,2);
  assert.ok(samples.every(sample=>sample.height===64&&sample.fits&&sample.face.includes('Body')));
  assert.ok(Math.abs(samples[0].base-samples[1].base)<.2,'Japanese samples align');
  assert.ok(samples.every(sample=>sample.captionGap<=8),'Keep both Japanese captions close to their English labels');
  assert.ok(samples[0].clearance>=3,'Leave space between the English label and み');
}
async function checkRubiFirstPaint(browser){
  const unit='N3_07_2012';
  for(const [remember,rubi] of [[true,'hide'],[true,'show'],[false,'hide']]){
    const mode=remember?rubi:'show';
    const context=await browser.newContext({viewport:{width:390,height:844},storageState:{cookies:[],origins:[
      {origin,localStorage:[{name:prefix+'preferences',value:JSON.stringify({remember,values:{rubi}})}]}]}});
    let release;
    const blocked=new Promise(resolve=>{release=resolve;});
    try{
      const page=await context.newPage(),errors=await route(page);
      await page.route('**/assets/app.js*',async request=>{await blocked;await request.fallback();});
      await page.addInitScript(()=>{
        function sample(){
          const readings=[...document.querySelectorAll('.paper rt')];
          const links=[...document.querySelectorAll('.paper-nav a[data-rubi-only]')];
          if(!readings.length||links.length!==2)return requestAnimationFrame(sample);
          window.firstReaderFrame={
            readings:readings.some(rt=>rt.getClientRects().length),
            pdfs:links.filter(link=>link.getClientRects().length).map(link=>link.getAttribute('href')),
            radio:document.querySelector('[name=rubi]:checked').value
          };
        }
        requestAnimationFrame(sample);
      });
      await page.goto(origin+'/papers/'+unit+'.html',{waitUntil:'commit'});
      await page.waitForFunction(()=>window.firstReaderFrame);
      if(engine==='chromium')await page.waitForFunction(()=>performance.getEntriesByName('first-contentful-paint').length);
      const pdf='../assets/'+(mode==='hide'?'pdfs-norubi':'pdfs')+'/'+unit+'.pdf';
      assert.deepEqual(await page.evaluate(()=>window.firstReaderFrame),{readings:mode==='show',pdfs:[pdf],radio:mode});
      assert.equal(await page.evaluate(()=>document.documentElement.classList.contains('js')),false);
      release();await page.waitForLoadState('load');await settle(page);
      assert.equal(await page.locator('.paper rt').first().isVisible(),mode==='show');
      assert.deepEqual(await page.locator('.paper-nav a[data-rubi-only]:visible').evaluateAll(a=>a.map(el=>el.getAttribute('href'))),[pdf]);
      assert.deepEqual(errors,[]);
    }finally{release();await context.close();}
  }
}
function headingCompoundWraps(rubies){
  const second=rubies.find(ruby=>ruby.textContent==='全体ぜんたい');
  let first=second?.previousElementSibling;
  if(first?.matches('wbr'))first=first.previousElementSibling;
  if(first?.textContent!=='文章ぶんしょう')return false;
  const bounds=node=>{const range=document.createRange();range.selectNodeContents(node);return range.getBoundingClientRect();};
  const aligned=[first,second].every(ruby=>{
    const base=bounds(ruby.firstChild),reading=bounds(ruby.querySelector('rt'));
    const center=(reading.left+reading.right)/2;
    return reading.height>0&&reading.top<base.top&&center>base.left&&center<base.right;
  });
  return aligned&&bounds(first.firstChild).bottom<=bounds(second.firstChild).top+1;
}
async function checkEnlargedHeadings(browser){
  const page=await browser.newPage({viewport:{width:320,height:760}});
  try{
    const errors=await route(page);
    const units=['N4_07_2013','N4_07_2023','N5_07_2023','N4_1996','N4_2001','N3_07_2024','N3_07_2025',
      'N3_12_2023','N3_12_2024','N3_12_2025','N3_set_2011_2012','N3_workbook_2018'];
    const headingRuby=()=>page.locator('.section-heading ruby').evaluateAll(nodes=>
      nodes.map(ruby=>[ruby.outerHTML,ruby.previousSibling?.nodeName==='WBR']));
    for(const unit of units){
      await page.goto(origin+'/papers/'+unit+'.html');
      let fittedRuby;
      for(const size of [200,250,350,500,250]){
        await page.locator('#text-size').evaluate((input,size)=>{
          input.value=size;input.dispatchEvent(new Event('input',{bubbles:true}));
        },size);
        for(const mode of ['hide','show']){
          await page.locator('#rubi-'+mode).evaluate(input=>input.click());await settle(page);
          const clipped=await page.evaluate(()=>{
            const bounds=document.querySelector('.paper-frame').getBoundingClientRect(),clipped=[];
            for(const heading of document.querySelectorAll('.section-heading')){
              const text=document.createTreeWalker(heading,NodeFilter.SHOW_TEXT),range=document.createRange();
              for(let node;(node=text.nextNode());){
                if(node.parentElement.closest('.sr-only,rp,[data-preserved-space]'))continue;
                for(let i=0;i<node.length;i++){
                  // Test the printed words and digits; punctuation can have optical overhang.
                  if(!/[\p{Letter}\p{Number}]/u.test(node.data[i]))continue;
                  range.setStart(node,i);range.setEnd(node,i+1);const rect=range.getBoundingClientRect();
                  if(rect.width&&rect.height&&(rect.left<bounds.left-1||rect.right>bounds.right+1))
                    clipped.push([heading.closest('[id]').id,node.data[i]]);
                }
              }
            }
            return clipped;
          });
          const description=unit+' at 320px, '+size+'%, rubi '+mode;
          assert.deepEqual(clipped,[],description);
          if(unit.startsWith('N3')&&size===500&&mode==='show'){
            const wrapped=await page.locator('.section-heading ruby').evaluateAll(headingCompoundWraps);
            assert.ok(wrapped,description+' keeps each reading over its word on separate lines');
          }
        }
        if(unit.startsWith('N3')&&size===250){
          const current=await headingRuby();
          if(fittedRuby)assert.deepEqual(current,fittedRuby,unit+' restores its original ruby at 250%');
          fittedRuby=current;
        }
        if(unit.startsWith('N3')&&size===500){
          await page.setViewportSize({width:768,height:760});await settle(page);
          assert.deepEqual(await headingRuby(),fittedRuby,unit+' restores its original ruby on a wider line');
          await page.setViewportSize({width:320,height:760});await settle(page);
        }
      }
    }
    assert.deepEqual(errors,[]);
  }finally{await page.close();}
}
async function checkExampleAnswerLabels(browser) {
  const papers = [
    ['N4_07_2021', 5], ['N4_07_2024', 5], ['N4_07_2025', 5],
    ['N4_12_2024', 5], ['N4_12_2025', 5], ['N4_workbook_2018', 5],
    ['N5_07_2024', 5], ['N5_07_2025', 6], ['N5_12_2021', 6], ['N5_12_2025', 6],
    ['N5_sample_2009', 2], ['N5_workbook_2012', 6], ['N5_workbook_2018', 6]
  ];
  const sizes = [[null, null], [100, 80], [100, 100], [100, 125], [125, 150], [150, 175], [200, 200]];
  const page = await browser.newPage({viewport: {width: 1600, height: 900}});
  try {
    const errors = await route(page);
    for (const [unit, count] of papers) {
      await page.goto(origin + '/papers/' + unit + '.html');
      for (const [text, zoom] of sizes) {
        await page.evaluate(([text, zoom]) => {
          if (zoom === null) {
            document.querySelector('#auto-text').click();
            document.querySelector('[data-zoom=auto]').click();
          } else {
            for (const [id, value] of [['text-size', text], ['paper-zoom', zoom]]) {
              const slider = document.getElementById(id);
              slider.value = String(value);
              slider.dispatchEvent(new Event('input', {bubbles: true}));
            }
          }
        }, [text, zoom]);
        await settle(page);
        const description = unit + ' at text ' + (text ?? 'auto') + ', zoom ' + (zoom ?? 'auto');
        const readout = await page.evaluate(() => [
          Number(document.querySelector('#text-size').value), Number(document.querySelector('#paper-zoom').value),
          document.querySelector('#auto-text').getAttribute('aria-pressed'),
          document.querySelector('[data-zoom=auto]').getAttribute('aria-pressed')
        ]);
        assert.deepEqual(readout, [text ?? 100, zoom ?? 140, String(text === null), String(zoom === null)], description);
        const labels = page.locator('.example-answer-table .answer-example-label').filter({hasText: /^（れい）$/});
        const examples = await labels.evaluateAll((labels, scale) => labels.map(label => {
          const walker = document.createTreeWalker(label, NodeFilter.SHOW_TEXT);
          const range = document.createRange(), tops = [];
          while (walker.nextNode()) {
            range.selectNodeContents(walker.currentNode);
            for (const rect of range.getClientRects()) if (rect.width && rect.height) tops.push(rect.top);
          }
          const bubbles = [...label.closest('tr').querySelectorAll('.answer-bubble')];
          // Collapsed table borders can move a cell's measured center by half a layout pixel.
          const centered = bubbles.every(bubble => {
            const b = bubble.getBoundingClientRect(), c = bubble.closest('td,th').getBoundingClientRect();
            return b.width > 0 && b.height > 0 &&
              Math.abs((b.left + b.right - c.left - c.right) / 2) <= .75 * scale &&
              Math.abs((b.top + b.bottom - c.top - c.bottom) / 2) <= .75 * scale;
          });
          return {id: label.closest('[data-source-id]').id, oneLine: tops.length > 0 && Math.max(...tops) - Math.min(...tops) < 1,
            bubbleCount: bubbles.length, centered};
        }), readout[1] / 100);
        assert.equal(examples.length, count, description);
        for (const example of examples) {
          assert.ok(example.oneLine, description + ' ' + example.id + ' keeps （れい） on one line');
          assert.equal(example.bubbleCount, 4, description + ' ' + example.id);
          assert.ok(example.centered, description + ' ' + example.id + ' centers all four bubbles');
        }
      }
    }
    assert.deepEqual(errors, []);
  } finally {
    await page.close();
  }
}
async function checkN4ChoiceSuffix(browser){
  const page=await browser.newPage({viewport:{width:390,height:760}});
  try{
    const errors=await route(page);
    for(const unit of ['N4_12_2024','N4_07_2025','N4_12_2025']){
      await page.goto(origin+'/papers/'+unit+'.html');
      await page.locator('#text-size').evaluate(input=>{
        input.value='250';input.dispatchEvent(new Event('input',{bubbles:true}));
      });
      for(const mode of ['show','hide']){
        await page.locator('#rubi-'+mode).evaluate(input=>input.click());await settle(page);
        const suffix=await page.locator('#vocab-s01 .section-heading .selector-suffix').evaluate(node=>{
          const range=document.createRange();range.selectNodeContents(node);
          const rects=Array.from(range.getClientRects()).filter(rect=>rect.width&&rect.height);
          const frame=node.closest('.paper-frame').getBoundingClientRect();
          return {text:node.textContent,lines:new Set(rects.map(rect=>Math.round(rect.top))).size,
            visible:rects.every(rect=>rect.left>=frame.left-1&&rect.right<=frame.right+1)};
        });
        assert.deepEqual(suffix,{text:'から',lines:1,visible:true},unit+' choice suffix at 390px, 250%, rubi '+mode);
      }
    }
    assert.deepEqual(errors,[]);
  }finally{await page.close();}
}
async function checkRubiMeasurements(browser){
  const page=await browser.newPage({viewport:{width:390,height:844}});
  try{
    const errors=await route(page);
    await page.goto(origin+'/papers/N4_07_2023.html');await settle(page);
    await page.evaluate(()=>{
      window.probes={options:0,tables:0};
      new MutationObserver(batch=>{
        for(const record of batch)for(const node of record.addedNodes){
          if(node.nodeType!==1||node.style.visibility!=='hidden'||node.getAttribute('aria-hidden')!=='true')continue;
          if(node.matches('.option-text'))window.probes.options++;
          if(node.matches('td,th'))window.probes.tables++;
        }
      }).observe(document.querySelector('.paper'),{childList:true,subtree:true});
    });
    const toggle=async mode=>{await page.locator('#rubi-'+mode).evaluate(input=>input.click());await settle(page);};
    const show=await snapshot(page);await toggle('hide');const hide=await snapshot(page);
    const cold=await page.evaluate(()=>({...window.probes}));assert.ok(cold.options>0&&cold.tables>0);
    await toggle('show');sameGeometry(await snapshot(page),show);
    await toggle('hide');sameGeometry(await snapshot(page),hide);
    assert.deepEqual(await page.evaluate(()=>window.probes),cold,'Both warmed modes reuse intrinsic measurements');
    await page.locator('#text-size').evaluate(input=>{input.value=175;input.dispatchEvent(new Event('input',{bubbles:true}));});
    await settle(page);
    const changed=await page.evaluate(()=>({...window.probes}));
    assert.ok(changed.options>cold.options&&changed.tables>cold.tables);
    await toggle('show');
    const other=await page.evaluate(()=>window.probes);
    assert.ok(other.options>changed.options&&other.tables>changed.tables,'New text size invalidates both modes');
    assert.deepEqual(errors,[]);
  }finally{await page.close();}
}
async function checkRubi(browser){
  for(const scripting of [true,false]){
    const context=await browser.newContext({javaScriptEnabled:scripting,viewport:{width:390,height:840}});
    try{
      const page=await context.newPage(),errors=await route(page),unit='N2_2002';
      const legacyKey=prefix+'paper2:'+unit+':norubi';
      if(scripting)await context.addInitScript(key=>{if(!localStorage.getItem(key))localStorage.setItem(key,'{"position":987}');},legacyKey);
      await page.goto(origin+'/papers/'+unit+'.html');
      if(scripting)await settle(page);
      else await page.waitForLoadState('networkidle');
      const choose=mode=>page.locator('[name=rubi][value='+mode+']').evaluate(input=>input.click());
      assert.equal(await page.locator('[data-settings=reading] h3').first().textContent(),'rubi');
      assert.equal(await page.locator('[name=rubi][value=show]').isChecked(),true);
      if(scripting)await page.locator('.answer-radio:enabled').first().evaluate(input=>input.click());
      assert.equal(await page.locator('.paper .source-literal img').count(),0);
      assert.ok(await page.locator('.paper .source-literal[role=img][aria-label]').count());
      const original=await snapshot(page);
      const requests=[];page.on('request',request=>requests.push(request.url()));
      for(const mode of ['hide','show','hide']){
        await choose(mode);
        if(scripting)await settle(page);
        const state=await page.evaluate(()=>{
          const visible=selector=>getComputedStyle(document.querySelector(selector)).display!=='none';
          return {reading:visible('.paper rt'),diagram:visible('.paper .rubi-reading'),preview:visible('.rubi-setting rt'),
            pdf:[...document.querySelectorAll('.paper-nav a[data-rubi-only]')].find(a=>a.getClientRects().length).getAttribute('href')};
        });
        assert.equal(state.reading,mode==='show');assert.equal(state.diagram,mode==='show');assert.equal(state.preview,true);
        assert.equal(state.pdf,'../assets/'+(mode==='show'?'pdfs':'pdfs-norubi')+'/'+unit+'.pdf');
        if(mode==='show')sameGeometry(await snapshot(page),original,'Show must restore the original geometry, scripting='+scripting);
        if(scripting){
          assert.equal((await page.title()).includes(' · no rubi'),mode==='hide');
          assert.equal(await page.locator('.answer-radio:checked').count(),1);
        }
      }
      assert.deepEqual(requests,[]);
      if(scripting){
        assert.equal(await page.evaluate(key=>localStorage.getItem(key),legacyKey),'{"position":987}');
        await page.goto(origin+'/papers/N2_workbook_2018.html');await settle(page);
        assert.equal(await page.locator('[name=rubi][value=hide]').isChecked(),true);
        assert.match(await page.locator('.paper-nav a[data-rubi-only=hide]:visible').getAttribute('href'),/\.workbook\.norubi\.pdf$/);
        await page.reload();assert.equal(await page.locator('[name=rubi][value=hide]').isChecked(),true);
      }
      if(!scripting){
        // Simulate a native reader that discards selectors containing :has().
        await page.evaluate(()=>{
          function strip(sheet){
            for(let i=sheet.cssRules.length-1;i>=0;i--){
              const rule=sheet.cssRules[i];
              if(rule.selectorText?.includes(':has('))sheet.deleteRule(i);
              else if(rule.cssRules)strip(rule);
            }
          }
          for(const sheet of document.styleSheets)strip(sheet);
        });
        await page.locator('#settings>summary').click();
        for(const mode of ['show','hide']){
          await page.locator('.rubi-setting label[for=rubi-'+mode+']').click();
          assert.equal(await page.locator('.paper rt').first().isVisible(),mode==='show');
          assert.equal(await page.locator('.paper .rubi-reading').first().isVisible(),mode==='show');
          assert.equal(await page.locator('.paper-nav a[data-rubi-only='+mode+']').isVisible(),true);
        }
        await page.locator('.rubi-setting .skip-link').press('Enter');
        await page.keyboard.press('Space');
        assert.equal(await page.locator('#rubi-show').isChecked(),true);
        await page.keyboard.press('ArrowRight');
        assert.equal(await page.locator('#rubi-hide').isChecked(),true);
      }
      assert.deepEqual(errors,[]);
    }finally{await context.close();}
  }
}
async function checkPaperPresets(page,width){
  const presets=await page.locator('.spacing-setting .segmented label').evaluateAll(labels=>labels.map(label=>{
    const caption=label.querySelector('small'),bounds=caption.getBoundingClientRect();
    return {height:label.getBoundingClientRect().height,captionTop:bounds.top,
      wrapped:bounds.height>parseFloat(getComputedStyle(caption).lineHeight)+1,
      fits:label.scrollWidth<=label.clientWidth+1&&label.scrollHeight<=label.clientHeight+1};
  }));
  assert.equal(presets.length,3);
  const height=presets[0].wrapped?68:56;
  assert.ok(presets.every(preset=>preset.wrapped===presets[0].wrapped&&Math.abs(preset.captionTop-presets[0].captionTop)<.1),
    'Paper percentage captions must line up at '+width+'px');
  assert.ok(presets.every(preset=>preset.fits&&preset.height===height),'Paper spacing presets at '+width+'px');
}
async function checkTimerEditorAlignment(page,width){
  const edges=await page.locator('.timer-adjust').evaluate(row=>{
    const pairs=['timer-direction','timer-reset-warning'].map(name=>
      row.parentElement.querySelector('[name='+name+']').closest('.segmented'));
    const actions=row.querySelector('.button-row');
    return {
      left:[...pairs,...row.querySelectorAll('.timer-field label'),actions.firstElementChild].map(e=>e.getBoundingClientRect().left),
      right:[...pairs,...row.querySelectorAll('.timer-field button'),actions.lastElementChild].map(e=>e.getBoundingClientRect().right)
    };
  });
  for(const positions of Object.values(edges)){
    assert.ok(Math.max(...positions)-Math.min(...positions)<.1,'Timer editor alignment at '+width+'px');
  }
}
async function checkHeadingWordPositions(page, selector, description) {
  const positions = () => page.locator(selector).evaluate(heading => {
    const left = heading.getBoundingClientRect().left;
    return [...heading.querySelectorAll('.heading-no-break, ruby, rt')].flatMap(word =>
      [...word.getClientRects()].map(rect => rect.x - left));
  });
  const actual = await positions();
  // The literal space determines the advance, soft breaks and space available to adjacent readings.
  const plainSpaces = await page.addStyleTag({content:
    '.section-heading .heading-wide-space::before,.section-heading .heading-wide-space::after{content:none!important}'});
  try {
    const reference = await positions();
    assert.equal(actual.length, reference.length, description);
    assert.ok(actual.every((x, i) => Math.abs(x - reference[i]) < 0.15), description + ' word and ruby positions');
  } finally {
    await plainSpaces.evaluate(style => style.remove());
  }
}
async function checkWorkbookFurigana(page, description) {
  const heading = page.locator('#vocab-s07 h2');
  const ruby = heading.locator('ruby').filter({hasText: '一ひと'});
  await ruby.evaluate(el => el.setAttribute('data-check-ruby', ''));
  // Color only the ink. Wrapping the ruby in a reference box changes its layout in WebKit.
  const shot = await heading.screenshot({scale: 'css', style:
    '#vocab-s07 h2{background:white;color:lime} [data-check-ruby]{color:blue} [data-check-ruby] rt{color:red}'});
  await ruby.evaluate(el => el.removeAttribute('data-check-ruby'));
  const result = await page.evaluate(async png => {
    const image = new Image();
    image.src = 'data:image/png;base64,' + png;
    await image.decode();
    const canvas = document.createElement('canvas');
    canvas.width = image.width; canvas.height = image.height;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(image, 0, 0);
    const pixels = ctx.getImageData(0, 0, image.width, image.height).data;
    const bounds = () => ({left: image.width, right: -1, top: image.height, bottom: -1});
    const reading = bounds(), base = bounds();
    for (let y = 0; y < image.height; y++) for (let x = 0; x < image.width; x++) {
      const i = 4 * (y * image.width + x), tint = pixels[i] - pixels[i + 2];
      if (pixels[i + 1] > 100 || Math.abs(tint) < 120) continue;
      const box = tint > 0 ? reading : base;
      box.left = Math.min(box.left, x); box.right = Math.max(box.right, x);
      box.top = Math.min(box.top, y); box.bottom = Math.max(box.bottom, y);
    }
    let preceding = -1;
    for (let y = 0; y <= reading.bottom; y++) for (let x = reading.left; x <= reading.right; x++) {
      const i = 4 * (y * image.width + x);
      if (pixels[i + 1] - Math.max(pixels[i], pixels[i + 2]) > 100) preceding = y;
    }
    return {reading, base, preceding};
  }, shot.toString('base64'));
  const {reading, base, preceding} = result;
  assert.ok(preceding >= 0 && reading.right >= reading.left && base.right >= base.left, description + ' visible glyphs');
  const clearance = (reading.bottom - reading.top + 1) / 2;
  assert.ok(reading.top - preceding - 1 >= clearance && base.top - reading.bottom - 1 >= clearance, description + ' clear lines around ひと');
  assert.ok(Math.abs(reading.left + reading.right - base.left - base.right) <= 4, description + ' ひと centered over 一');
}
async function checkNarrowWords(browser) {
  for (const javaScriptEnabled of [true, false]) {
    const context = await browser.newContext({javaScriptEnabled, viewport: {width: 320, height: 720}});
    try {
      const page = await context.newPage(), errors = await route(page);
      const cases = [['N5_workbook_2012', '#vocab-q039', 'ありがとうございます。」', 320]];
      if (javaScriptEnabled) cases.push(['N5_sample_2009', '#vocab-q006', 'べんきょうできません。', 390, 200],
        ['N4_workbook_2018', '#vocab-q001', 'いそがしかった', 390, 200],
        ['N4_07_2025', '#reading-q012', 'あのう、', 390, 200, true],
        ['N5_sample_2009', '#reading-q001', '土曜日どようび', 320, 250, true],
        ['N5_workbook_2018', '#reading-q006', '高木大学たかぎだいがくに', 320, 250, true],
        ['N5_workbook_2012', '#reading-b005', '中川先生なかがわせんせいに', 320, 250, true],
        ['N5_sample_2009', '#vocab-b003', 'ジョンさんと', 320, 250, true],
        ['N5_07_2024', '#vocab-b004', 'やすくないです。', 320, 250, true],
        ['N5_12_2021', '#reading-q009', '（タクシーで）', 320, 250, true],
        ['N5_workbook_2018', '#reading-q004', '朝あさご飯はんを', 320, 250, true],
        ['N5_12_2012', '#reading-q004', '学校がっこうで', 320, 250, true],
        ['N5_12_2021', '#reading-q019', '午後ごごから', 320, 250, true],
        ['N5_07_2024', '#reading-q018', '大友おおともさんは', 320, 250, true]);
      for (const [unit, question, text, width, size, margin] of cases) {
        await page.setViewportSize({width, height: 720});
        await page.goto(origin + '/papers/' + unit + '.html');
        if (javaScriptEnabled) {
          if (margin) await page.locator('[name=marking][value=margin]').evaluate(input => input.click());
          if (size) await page.locator('#text-size').evaluate((input, value) => {
            input.value = value; input.dispatchEvent(new Event('input', {bubbles: true}));
          }, size);
          await settle(page);
        }
        const group = page.locator(question + ' .wakachi').filter({hasText: text}).first();
        const fits = () => group.evaluate(el => {
          const col = el.closest('.dialogue-utterance,.option-text,.question-content,.example-native-options>span,p');
          const cell = col.getBoundingClientRect();
          const fragments = [...el.getClientRects()];
          return cell.width > 0 && fragments.length > 0 && fragments.every(rect => rect.left >= cell.left - 1 && rect.right <= cell.right + 1);
        });
        assert.ok(await fits(), unit + ' keeps ' + text + ' inside its column');
        if (margin && question === '#reading-q006') {
          await page.locator('[name=auto-spoil][value=yes]').evaluate(input => input.click());
          await page.locator(question + ' .answer-radio[data-correct=false]').first().evaluate(input => input.click());
          const clear = await page.locator(question).evaluate(q =>
            q.querySelector('.spoiled-margin').getBoundingClientRect().bottom <= q.querySelector('.question-content').getBoundingClientRect().top);
          assert.ok(clear, 'Reflowed text clears both margin marks');
        }
        if (javaScriptEnabled) {
          await page.setViewportSize({width: 1600, height: 900});
          await page.locator('#source-text').evaluate(button => button.click());
          await settle(page);
          assert.equal(await group.evaluate(el => getComputedStyle(el).whiteSpace), 'nowrap', unit + ' restores whole words');
        }
      }
      assert.deepEqual(errors, []);
    } finally { await context.close(); }
  }
}
async function checkInstructionSpacing(browser) {
  const context = await browser.newContext({viewport: {width: 1280, height: 720}, deviceScaleFactor: 2});
  try {
    const page = await context.newPage();
    const errors = await route(page);
    for (const unit of ['N5_12_2025', 'N5_workbook_2012', 'N5_workbook_2018']) {
      await page.goto(origin + '/papers/' + unit + '.html');
      await settle(page);
      for (const preset of ['original', 'standard', 'compact']) {
        await page.locator('input[name="spacing"][value="' + preset + '"]').evaluate(input => input.click());
        await settle(page);
        if (unit === 'N5_12_2025') {
          // At Auto text and zoom this instruction occupies three plain lines.
          const lines = await page.locator('#vocab-s01 h2').evaluate(heading => {
            const paper = heading.closest('.paper');
            const zoom = new DOMMatrix(getComputedStyle(paper).transform).d;
            return heading.getBoundingClientRect().height / (zoom * parseFloat(getComputedStyle(heading).lineHeight));
          });
          assert.ok(Math.abs(lines - 3) < 0.02, unit + ' ' + preset + ' line pitch');
        } else {
          await checkWorkbookFurigana(page, unit + ' ' + preset);
          await page.locator('#text-size').evaluate(input => {
            input.value = 250;
            input.dispatchEvent(new Event('input', {bubbles: true}));
          });
          await settle(page);
          await checkHeadingWordPositions(page, '#vocab-s07 h2', unit + ' ' + preset);
          await page.locator('#auto-text').evaluate(button => button.click());
          await settle(page);
        }
      }
    }
    await page.setViewportSize({width: 700, height: 720});
    await page.goto(origin + '/papers/N4_workbook_2018.html');
    await settle(page);
    await checkHeadingWordPositions(page, '#vocab-s08 h2', 'N4 workbook overhanging reading');
    await page.setViewportSize({width: 1600, height: 875});
    for (const preset of ['original', 'standard', 'compact']) {
      await page.locator('input[name="spacing"][value="' + preset + '"]').evaluate(input => input.click());
      for (const [section, size, word] of [['vocab-s01', 123, 'かきますか。'], ['vocab-s05', 100, 'ものを']]) {
        await page.evaluate(size => {
          for (const [id, value] of [['paper-zoom', 140], ['text-size', size]]) {
            const input = document.getElementById(id);
            input.value = value;
            input.dispatchEvent(new Event('input', {bubbles: true}));
          }
        }, size);
        await settle(page);
        const oneLine = await page.locator('#' + section + ' h2 .wakachi').evaluateAll((words, text) => {
          const group = words.find(node => node.textContent === text);
          if (!group) return false;
          const boxes = [...group.getClientRects()];
          // An inline group can have several fragments on the same baseline.
          return boxes.every(box => Math.abs(box.top - boxes[0].top) < parseFloat(getComputedStyle(group).fontSize) / 2);
        }, word);
        assert.ok(oneLine, preset + ' wraps before the complete group ' + word);
      }
    }
    assert.deepEqual(errors, []);
  } finally {
    await context.close();
  }
}
async function checkPracticeChoices(browser){
  const page=await browser.newPage(),errors=await route(page);
  await page.goto(origin+'/papers/N5_sample_2009.html');
  await page.locator('#settings>summary').click();
  for(const width of [1280,768,651,480,390,320]){
    await page.setViewportSize({width,height:900});
    for(const tab of ['reading','marking','timer']){
      await page.locator('[name=settings-view][value='+tab+']+span').click();
      await settle(page);
      const gaps=await page.locator('[data-settings='+tab+'] .setting-row h3+p').evaluateAll(descriptions=>
        descriptions.map(p=>p.getBoundingClientRect().top-p.previousElementSibling.getBoundingClientRect().bottom));
      assert.ok(gaps.length&&gaps.every(gap=>Math.abs(gap-9)<.1),'Heading spacing in '+tab+' at '+width+'px');
      if(tab==='reading'){await checkPaperPresets(page,width);continue;}
      if(tab==='timer')await checkTimerEditorAlignment(page,width);
      if(tab==='marking'){
        const offsets=await page.evaluate(()=>[...document.querySelectorAll('[name=auto-grade],[name=auto-spoil]')].map(input=>{
          const span=input.nextElementSibling,title=new Range(),sample=new Range();
          title.selectNodeContents(span.firstChild);sample.selectNodeContents(span.querySelector('small'));
          const position=()=>[title.getBoundingClientRect().top,sample.getBoundingClientRect().top,input.closest('label').getBoundingClientRect().height];
          const current=position();
          // The previously accepted pair is centered with a 5 px caption gap.
          span.style.setProperty('--choice-caption-gap','5px');span.style.marginBottom='0';
          const previous=position();
          span.style.removeProperty('--choice-caption-gap');span.style.removeProperty('margin-bottom');
          return [input.name,...current.map((value,i)=>value-previous[i])];
        }));
        assert.deepEqual(offsets,[['auto-grade',-1,0,0],['auto-grade',-1,0,0],['auto-spoil',0,0,0],['auto-spoil',0,0,0]],'Button typography at '+width);
      }
      const pairs=await page.locator('[data-settings='+tab+'] .segmented').evaluateAll(groups=>groups.map(group=>{
        const row=group.closest('.setting-row'),bounds=group.getBoundingClientRect();
        const labels=[...group.querySelectorAll('label')],checked=group.querySelector(':checked');
        const sizes=labels.map(label=>{
          const {width,height}=label.getBoundingClientRect();
          return {width,height,fits:label.scrollHeight<=label.clientHeight+1&&label.scrollWidth<=label.clientWidth+1};
        });
        return {name:checked.name,sizes,width:bounds.width,available:row.clientWidth,
          stacked:bounds.top>=row.querySelector('p').getBoundingClientRect().bottom,
          underline:getComputedStyle(checked.closest('label')).boxShadow};
      }));
      assert.equal(pairs.length,tab==='timer'?4:6);
      for(const pair of pairs){
        const message=pair.name+' at '+width+'px',[first,second]=pair.sizes;
        assert.deepEqual(first,second,message);
        assert.ok(first.fits&&[56,68].includes(first.height),message);
        assert.equal(pair.width,Math.min(400,pair.available),message);
        assert.equal(pair.stacked,width<=768,message);
        assert.match(pair.underline,/-2px.*-3px/,message);
        if(tab==='timer')assert.equal(first.height,width===320?68:56,message);
        else if(['auto-grade','auto-spoil'].includes(pair.name))assert.equal(first.height,68,message);
        else if(width>=768||pair.name==='spoil-all')assert.equal(first.height,56,message);
      }
    }
  }
  assert.deepEqual(errors,[]);
  await page.close();
}
async function checkReaderOptionStyles(browser){
  for(const scripting of [true,false]){
    const context=await browser.newContext({javaScriptEnabled:scripting}),page=await context.newPage();
    const errors=await route(page),requests=[];page.on('request',r=>requests.push(r.url()));
    try{
      await page.goto(origin+'/papers/N5_sample_2009.html');
      const state=await page.evaluate(()=>{
        const choose=(name,value)=>document.querySelector('[name='+name+'][value='+value+']').click();
        const paper=document.querySelector('.paper'),q=paper.querySelector('.question:has(.star-solution)');
        q.querySelector('input[data-correct=true]').click();
        choose('marking','margin');
        const gutter=q.querySelector('.margin-answer'),margin=getComputedStyle(gutter).display;
        choose('marking','rounded-cell');
        const rounded=getComputedStyle(q.querySelector(':checked+.option')).borderTopLeftRadius;
        choose('star-behavior','hide');const hidden=getComputedStyle(q.querySelector('.star-solution')).visibility;
        choose('star-behavior','show');const shown=getComputedStyle(q.querySelector('.star-solution')).visibility;
        document.querySelector('#visible-paper').click();choose('spacing','compact');
        return {margin,rounded,hidden,shown,border:getComputedStyle(paper).outlineStyle,
          plain:getComputedStyle(gutter).display,preset:getComputedStyle(paper).getPropertyValue('--line-preset').trim()};
      });
      assert.equal(state.margin,'block');assert.equal(state.plain,'none');assert.ok(parseFloat(state.rounded)>0);
      assert.equal(state.hidden,'hidden');assert.equal(state.shown,'visible');assert.equal(state.border,'solid');
      assert.equal(requests.some(url=>url.includes('themes-no-script.css')),!scripting);
      if(scripting){
        await page.reload();
        const saved=await page.locator('body').evaluate(b=>[b.dataset.marking,b.dataset.spacing,b.hasAttribute('data-show-star-order'),b.hasAttribute('data-visible-paper')]);
        assert.deepEqual(saved,['rounded-cell','compact',true,true]);
        const peer=await context.newPage(),peerErrors=await route(peer);
        await peer.goto(page.url());
        await peer.locator('[name=marking][value=bold]').evaluate(el=>el.click());
        await peer.locator('#block-adjust').evaluate(el=>{el.value='83';el.dispatchEvent(new Event('input',{bubbles:true}));});
        await page.waitForFunction(()=>document.body.dataset.marking==='bold'&&document.body.dataset.spacing==='custom');
        assert.equal(await page.locator('[name=spacing]:checked').count(),0);
        assert.deepEqual(peerErrors,[]);
      }else assert.equal(Number(state.preset),.8);
      assert.deepEqual(errors,[]);
    }finally{await context.close();}
  }
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
    await checkRubiFirstPaint(browser);checks++;console.log('PASS saved rubi readings and PDF in the first visible frame');
    await checkEnlargedHeadings(browser);checks++;console.log('PASS enlarged instruction headings fit the mobile paper');
    await checkExampleAnswerLabels(browser);checks++;console.log('PASS 67 N4 and N5 answer-sheet labels and their bubbles at seven sizes');
    await checkN4ChoiceSuffix(browser);checks++;console.log('PASS N4 numbered choices keep から together at 390px and 250%');
    await checkRubiMeasurements(browser);checks++;console.log('PASS warmed rubi option and table measurements');
    await checkNarrowWords(browser);checks++;console.log('PASS long Japanese groups fit their columns on narrow screens');
    await checkInstructionSpacing(browser);checks++;console.log('PASS instruction line spacing and workbook furigana at every preset');
    await checkReaderOptionStyles(browser);checks++;console.log('PASS native and scripted marking, STAR, spacing and border controls');
    await checkPracticeChoices(browser);checks++;console.log('PASS settings spacing, choice sizes and underlines, and timer editor alignment');
    await checkRubi(browser);checks++;console.log('PASS reader rubi, diagram readings, PDF choice and shared progress');
    for(const width of [1280,390,320])for(const rubi of ['show','hide']){
      const context=await browser.newContext({viewport:{width,height:900}});
      await context.addInitScript(({prefix,rubi})=>{if(!localStorage.getItem(prefix+'preferences'))localStorage.setItem(prefix+'preferences',JSON.stringify({remember:true,values:{timerEnabled:false,spacingVersion:2,rubi}}));},{prefix,rubi});
      const page=await context.newPage(),errors=await route(page),requests=[];page.on('request',r=>requests.push(r.url()));
      await page.goto(origin+'/papers/N5_sample_2009.html');await settle(page);
      assert.equal(requests.some(u=>u.includes('themes-no-script.css')),false,'JS readers must not download the fallback palettes');
      await page.evaluate(()=>{document.querySelector('#settings').open=true;document.querySelector('[name=settings-view][value=reading]').click();});await settle(page);
      await checkLayout(page);
      if(process.env.ASTRA_SCREENSHOTS&&rubi==='show'){
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
      const answers=await page.evaluate(prefix=>Object.fromEntries(Object.keys(localStorage).filter(k=>k.startsWith(prefix+'paper2:')).map(k=>[k,JSON.parse(localStorage[k]).answers])),prefix);
      await page.evaluate(()=>{document.querySelector('#settings').open=true;});await settle(page);
      await enter(page,'text','125');await enter(page,'zoom','165');await page.reload();await settle(page);
      assert.equal(await page.locator('#text-percent').inputValue(),'125');assert.equal(await page.locator('#zoom-percent').inputValue(),'165');
      assert.deepEqual(await page.evaluate(prefix=>Object.fromEntries(Object.keys(localStorage).filter(k=>k.startsWith(prefix+'paper2:')).map(k=>[k,JSON.parse(localStorage[k]).answers])),prefix),answers,'Sizing and reload preserve first feedback and answers');
      assert.deepEqual(errors,[]);await context.close();checks++;console.log('PASS percentage controls '+rubi+' at '+width+'px');
    }
    // All palette declarations must be identical; only their state selector moves.
    if(baseline){
      const pictures=[];
      for(const reference of [true,false]){
        const context=await browser.newContext({viewport:{width:1280,height:900}});
        await context.addInitScript(prefix=>localStorage.setItem(prefix+'preferences',JSON.stringify({remember:true,values:{timerEnabled:false,spacingVersion:2}})),prefix);
        const page=await context.newPage(),errors=await route(page,reference);
        await page.goto(origin+'/papers/N1_1999.html');await settle(page);
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
