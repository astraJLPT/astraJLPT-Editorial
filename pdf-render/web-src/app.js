/* Local progressive enhancement. No network, account, or model dependency. */
(() => {
  'use strict';
  document.documentElement.classList.add('js');
  const $ = (s, root=document) => root.querySelector(s);
  const $$ = (s, root=document) => [...root.querySelectorAll(s)];
  // Retain text nodes: replacing them invalidates ancestor :has() selectors in
  // Chromium, even when a settings readout has no effect on the paper.
  function setText(node,value){
    if(!node||node.textContent===value)return;
    if(node.childNodes.length===1&&node.firstChild.nodeType===Node.TEXT_NODE)node.firstChild.data=value;
    else node.textContent=value;
  }
  const data = JSON.parse($('#page-data').textContent);
  const themeData = globalThis.AstraThemes;
  const themes = [...themeData.originals, ...themeData.monkeytype];
  if(data.paper&&!data.questions){
    const shared=globalThis.AstraQuestions;
    if(shared?.unit!==data.paper.unit||!Array.isArray(shared.questions))throw new Error('Missing question data for '+data.paper.unit);
    data.questions=shared.questions;
  }
  // Shared controls must exist before saved preferences and event handlers bind.
  const editor=$('#theme-editor-template');
  if(editor){editor.innerHTML=themeData.editorMarkup;editor.replaceWith(editor.content);}
  // Normalize cached shells before grading restores answers or updates labels.
  const progressRoot=$('#progress'),progressCount=$('#progress-count'),progressDetail=$('#progress-detail');
  let progressCorrect=progressRoot?.querySelector('.progress-correct');
  if(progressRoot&&!progressCorrect){
    progressCorrect=document.createElement('span');
    progressCorrect.className='progress-correct';progressCorrect.textContent='correct';
    progressRoot.replaceChildren(progressCount,progressCorrect,progressDetail);
  }
  const catalog=$('.theme-catalog');
  const catalogInputs=catalog?$$('input[name=theme]',catalog):[];
  // Keep parser-created radios: inserting 187 of them into a finished reader
  // is expensive in Firefox. Rebuild only empty/outdated cached shells.
  if(catalog&&(catalogInputs.length!==themeData.monkeytype.length||catalogInputs.some((input,i)=>input.value!==themeData.monkeytype[i].id))){
    const cards=document.createDocumentFragment();
    for(const theme of themeData.monkeytype){
      const card=document.createElement('label'),input=document.createElement('input'),name=document.createElement('span');
      card.className='theme-card';
      card.style.setProperty('--preview-bg',theme.colors.bg);
      card.style.setProperty('--preview-text',theme.colors.main);
      input.type='radio';input.name='theme';input.id='theme-'+theme.id;input.value=theme.id;
      name.textContent=theme.name;card.append(input,name);cards.append(card);
    }
    catalog.replaceChildren(cards);
  }
  const prefix = 'astraJLPT:web:v1:';
  const colorMath=AstraThemeColors, sizingPolicy=AstraReaderSizing, colorRoles=themeData.colorRoles, fillControls=themeData.fillControls;
  const editableColors=colorRoles.filter(r=>r.editable).map(role=>{
    const row=$('[data-color-row="'+role.id+'"]');
    return {role,row,field:$('[data-color-hex]',row),swatch:$('[data-color-swatch]',row),alpha:$('[data-color-alpha]',row),reset:$('[data-color-reset]',row)};
  });
  let effectiveColors={};
  const spacingPresets={original:{line:100,block:100},standard:{line:90,block:75},compact:{line:80,block:50}};
  const defaults = {theme:'astraJLPT_dark', rubi:'show', spacing:'standard', marking:'cell', star:true, border:false, text:'auto', textSource:'auto', zoom:'auto', line:90, block:75, spacingVersion:2,autoGrade:true,allowUnclick:true,timerEnabled:true,timerDirection:'down',catalogSort:'recommended'};
  let practiceUI=null;
  const storage = new AstraBrowserMemory(()=>localStorage,prefix);
  function normalizePreferences(values={}) {
    const next={...defaults,...values};
    if(next.rubi!=='hide')next.rubi='show';
    for(const key of ['autoGrade','allowUnclick','timerEnabled'])if(typeof next[key]!=='boolean')next[key]=defaults[key];
    // Old saves wrote timerControls=false even when untouched. Both controls
    // now default to show. Only an explicit hide needs space in the record.
    delete next.timerControls;
    for(const key of ['bannerTimerControls','timerResetWarning','clearSpoilWarning'])if(next[key]!==false)delete next[key];
    for(const key of ['autoSpoil','spoilAll'])if(next[key]!==true)delete next[key];
    if(!['down','up'].includes(next.timerDirection))next.timerDirection='down';
    if(!['recommended','newest','oldest'].includes(next.catalogSort))next.catalogSort='recommended';
    // Older timer records used a clock offset shared by all papers. Preserve
    // that offset for unopened saves; new timers use wall-clock timestamps.
    if(!(Number.isFinite(next.timerDisabledTotal)&&next.timerDisabledTotal>0))delete next.timerDisabledTotal;
    if(!next.timerEnabled&&Number.isFinite(next.timerDisabledAt)&&next.timerDisabledAt>0)
      next.timerDisabledTotal=(next.timerDisabledTotal||0)+Math.max(0,Date.now()-next.timerDisabledAt);
    delete next.timerDisabledAt;
    if(values.spacingVersion!==2){
      const preset=spacingPresets[next.spacing]||spacingPresets.standard;
      next.line=Math.round(preset.line*(Number(values.line)||100)/100);
      next.block=Math.round(preset.block*(Number(values.block)||100)/100);
      next.spacingVersion=2;
    }
    next.customColors=colorMath.sanitize(next.customColors,themes,colorRoles);
    next.fillOpacity=colorMath.sanitizeFills(next.fillOpacity,themes,fillControls);
    return next;
  }
  const saved = storage.preferences();
  let preferences=normalizePreferences(saved.values),remember=saved.remember,answers={},restoring=false;
  let previousPreferences=null,observedPreferences=JSON.stringify(saved),sessionEpoch=saved.epoch;
  const rubiControls=data.paper?$$('[name=rubi]'):[],readerTitle=document.title;
  // The native reader uses sibling selectors. In the enhanced reader keep
  // the radios in the settings panel's normal tab order and focus trap.
  for(const input of rubiControls){
    if(input.parentElement===document.body&&input.labels[0]){
      input.labels[0].prepend(input);
      input.removeAttribute('tabindex');
    }
  }
  function displayRubi(mode){
    document.body.dataset.rubi=mode;
    const title=mode==='hide'?readerTitle.replace(/ · astraJLPT$/,' · no rubi · astraJLPT'):readerTitle;
    if(document.title!==title)document.title=title;
  }
  if(data.paper)displayRubi(rubiControls.length?preferences.rubi:'show');
  function status() {
    setText($('#save-status'),!storage.available?'Browser storage is unavailable. You can still read and answer.':remember?'Saved on this browser. Settings are shared across pages. Your answers and position are saved in each paper.':'Saving is off. This visit stays in memory.');
  }
  function persist(enable=false) {
    if(!remember&&!enable)return;
    const record=storage.savePreferences(preferences,enable?null:previousPreferences,enable);
    if(record){
      const next=normalizePreferences(record.values),changed=JSON.stringify(next)!==JSON.stringify(preferences);
      preferences=next;previousPreferences=JSON.parse(JSON.stringify(next));observedPreferences=JSON.stringify(record);
      if(changed)apply();
    } else if(storage.available){remember=false;$('#remember').checked=false;}
    status();
  }
  function syncPreferences(record=storage.preferences()) {
    const serialized=JSON.stringify(record);
    if(!storage.available){status();return;}
    const newSession=record.remember&&(!remember||record.epoch!==sessionEpoch);
    if(serialized===observedPreferences&&!newSession)return;
    observedPreferences=serialized;remember=record.remember;
    if(remember){
      preferences=normalizePreferences(record.values);
      previousPreferences=JSON.parse(JSON.stringify(preferences));
      if(newSession){
        sessionEpoch=record.epoch;
        pendingBookmark=null;
        observedAnswers='';
        if(paperRecord)restoreSelections(paperRecord.read());
        practiceUI?.restoreTimer();
      }
      apply();
    }else{$('#remember').checked=false;status();}
  }
  function toast(message) {const t=$('#toast');t.textContent=message;t.hidden=false;clearTimeout(toast.timer);toast.timer=setTimeout(()=>t.hidden=true,4200);}
  function select(name,value) {const input=$$('input[name="'+name+'"]').find(i=>i.value===String(value));if(input)input.checked=true;}
  function wcagLuminance(rgb) {
    const f=x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4;
    return .2126*f(rgb[0])+.7152*f(rgb[1])+.0722*f(rgb[2]);
  }
  // User color overrides take precedence over the palette’s selected text-source mode.
  function updateThemeTextColor(theme) {
    const control=$('#monkeytype-text-source'),label=$('#monkeytype-text-status');
    const isMonkeytype=Boolean(theme?.adaptedColors);
    if(control)control.hidden=!isMonkeytype;
    if(!theme)return;
    const mode=['auto','sub','text'].includes(preferences.textSource)?preferences.textSource:'auto';
    const custom=preferences.customColors?.[theme.id]||{};
    const fills=preferences.fillOpacity?.[theme.id]||{};
    effectiveColors=colorMath.resolve(theme,mode,custom,colorRoles,fills);
    for(const role of colorRoles)document.body.style.setProperty('--'+role.id,colorMath.css(effectiveColors[role.id]));
    const bg=effectiveColors.bg;
    document.body.dataset.brightness=wcagLuminance(bg.slice(0,3).map(v=>v/255))>.179?'light':'dark';
    document.body.style.colorScheme=document.body.dataset.brightness;
    if(label)label.textContent='Custom colors override the selected text color source.';
    const count=Object.keys(custom).length+Object.keys(fills).length;
    $('#color-edit-status').textContent=theme.name+(count?' · '+count+' custom setting'+(count===1?'':'s'):' · Original colors');
    $('#reset-theme-colors').disabled=!count;
    for(const {role,field,swatch,alpha,reset} of editableColors){
      const color=effectiveColors[role.id];
      if(document.activeElement!==field){field.value=colorMath.hex(color);field.removeAttribute('aria-invalid');}
      swatch.value=colorMath.hex([...color.slice(0,3),1]);
      swatch.style.setProperty('--swatch-color',colorMath.css(color));
      if(alpha){alpha.value=Math.round(color[3]*1000)/10;alpha.nextElementSibling.textContent=Math.round(color[3]*1000)/10+'%';}
      reset.disabled=!custom[role.id];
    }
    for(const control of fillControls){
      const opacity=fills[control.id]??control.default;
      $('[data-fill-opacity="'+control.id+'"]').value=opacity;
      $('#opacity-'+control.id+'-output').textContent=opacity+'%';
      $('[data-fill-reset="'+control.id+'"]').disabled=!Object.hasOwn(fills,control.id);
    }
  }
  function brightness() {
    const id=$('input[name="theme"]:checked')?.value;
    if(id)document.body.dataset.theme=id;
    for(const button of $$('#quick-picks button'))button.setAttribute('aria-pressed',String(button.dataset.theme===id));
    updateThemeTextColor(themes.find(t=>t.id===id));
  }
  function setCustomColor(key,value){
    const role=colorRoles.find(r=>r.id===key),valid=colorMath.normalize(value,role.alpha);
    if(!valid)return false;
    preferences.customColors??={};
    preferences.customColors[preferences.theme]??={};
    preferences.customColors[preferences.theme][key]=valid;
    brightness();persist();return true;
  }
  for(const field of $$('[data-color-hex]')){
    field.addEventListener('input',()=>{field.setAttribute('aria-invalid',String(!setCustomColor(field.dataset.colorHex,field.value)));});
    field.addEventListener('blur',()=>{
      // Incomplete/invalid input never reaches CSS or storage; restore the last valid value.
      field.value=colorMath.hex(effectiveColors[field.dataset.colorHex]);field.removeAttribute('aria-invalid');
    });
    field.addEventListener('keydown',e=>{if(e.key==='Enter')field.blur();});
  }
  for(const field of $$('[data-color-swatch]'))field.addEventListener('input',()=>{
    const key=field.dataset.colorSwatch,c=colorMath.rgba(field.value);c[3]=effectiveColors[key][3];setCustomColor(key,colorMath.hex(c));
  });
  for(const field of $$('[data-color-alpha]'))field.addEventListener('input',()=>{
    const key=field.dataset.colorAlpha,c=[...effectiveColors[key]];c[3]=Number(field.value)/100;setCustomColor(key,colorMath.hex(c));
  });
  for(const button of $$('[data-color-reset]'))button.addEventListener('click',()=>{
    delete preferences.customColors?.[preferences.theme]?.[button.dataset.colorReset];brightness();persist();
  });
  for(const field of $$('[data-fill-opacity]'))field.addEventListener('input',()=>{
    const key=field.dataset.fillOpacity,value=Number(field.value),control=fillControls.find(c=>c.id===key);
    preferences.fillOpacity??={};preferences.fillOpacity[preferences.theme]??={};
    if(value===control.default)delete preferences.fillOpacity[preferences.theme][key];
    else preferences.fillOpacity[preferences.theme][key]=value;
    brightness();persist();
  });
  for(const button of $$('[data-fill-reset]'))button.addEventListener('click',()=>{
    delete preferences.fillOpacity?.[preferences.theme]?.[button.dataset.fillReset];brightness();persist();
  });
  $('#reset-theme-colors')?.addEventListener('click',()=>{
    delete preferences.customColors?.[preferences.theme];delete preferences.fillOpacity?.[preferences.theme];brightness();persist();
  });
  const settings=$('#settings'), panel=$('.settings-panel');
  let readingAnchor=null,settingsGeneration=0;
  function captureReading(){
    const nodes=$$('.paper .question,.paper .source-block,.paper .section-heading');
    const edge=($('.reader-subbar')?.getBoundingClientRect().bottom||0)+8;
    const node=nodes.find(n=>n.getBoundingClientRect().bottom>edge);
    return node?{node,top:node.getBoundingClientRect().top}:null;
  }
  function alignReading(anchor){
    if(anchor.node?.isConnected)window.scrollBy(0,anchor.node.getBoundingClientRect().top-anchor.top);
    // Automatic scrolling must not claim a newer bookmark from another tab.
    lastScrollY=window.scrollY;
  }
  function startSettingsVisit(){settingsGeneration++;readingAnchor=captureReading();}
  settings.querySelector('summary').addEventListener('pointerdown',()=>{if(!settings.open)startSettingsVisit();});
  settings.querySelector('summary').addEventListener('keydown',e=>{if(!settings.open&&(e.key==='Enter'||e.key===' '))startSettingsVisit();});
  settings.addEventListener('toggle',()=>{
    if(settings.open){if(!readingAnchor)startSettingsVisit();sizing();return;}
    const anchor=readingAnchor,generation=settingsGeneration;readingAnchor=null;
    requestAnimationFrame(()=>requestAnimationFrame(()=>{if(!settings.open&&generation===settingsGeneration&&anchor)alignReading(anchor);}));
  });
  const closeSettings=()=>{settings.open=false;settings.querySelector('summary').focus({preventScroll:true});};
  $('#close-settings')?.addEventListener('click',closeSettings);
  document.addEventListener('click',e=>{if(settings.open&&!settings.contains(e.target)&&!e.target.closest?.('dialog'))settings.open=false;});
  document.addEventListener('keydown',e=>{
    if(e.target.closest?.('dialog'))return;
    if(e.key==='Escape'&&settings.open){e.preventDefault();closeSettings();}
    if((e.altKey||e.ctrlKey)&&e.shiftKey&&e.key.toLowerCase()==='d'){e.preventDefault();setDev(!document.body.classList.contains('developer'));}
    if(e.key==='Tab'&&settings.open){const focus=$$('a,button,input,summary,[tabindex="0"]',settings).filter(x=>x.getClientRects().length);if(e.shiftKey&&document.activeElement===focus[0]){e.preventDefault();focus.at(-1).focus();}else if(!e.shiftKey&&document.activeElement===focus.at(-1)){e.preventDefault();focus[0].focus();}}
  });
  let dev=false;
  try{dev=sessionStorage.getItem(prefix+'developer')==='true';}catch(_){}
  function setDev(value,announce=true){
    document.body.classList.toggle('developer',value);
    if($('#historical'))$('#historical').hidden=!value;
    $('#boar')?.setAttribute('aria-pressed',String(value));
    try{sessionStorage.setItem(prefix+'developer',String(value));sessionStorage.removeItem(prefix+'historical');}catch(_){}
    if(announce)toast(value?'Developer mode and older chapters enabled.\nSHIFT+CLICK the top-left astraJLPT logo or\nALT+SHIFT+D to toggle Developer mode.':'Developer mode and older chapters hidden.');
  }
  setDev(Boolean(data.review)||dev,false);
  $('#disable-dev')?.addEventListener('click',()=>setDev(false));
  // Long press the wordmark for a touch-friendly hidden developer activation.
  let hold=0,held=false;
  $('#brand')?.addEventListener('pointerdown',()=>{held=false;hold=setTimeout(()=>{held=true;setDev(!document.body.classList.contains('developer'));},1800);});
  for(const ev of ['pointerup','pointercancel','pointerleave'])$('#brand')?.addEventListener(ev,()=>clearTimeout(hold));
  $('#brand')?.addEventListener('click',e=>{clearTimeout(hold);if(held){e.preventDefault();held=false;}else if(e.shiftKey){e.preventDefault();setDev(!document.body.classList.contains('developer'));}});
  $('#boar')?.addEventListener('click',()=>{setDev(!document.body.classList.contains('developer'));const target=$('#historical');if(target&&!target.hidden)target.scrollIntoView({behavior:'instant',block:'nearest'});});
  // Suggestions vary, selected theme does not. Never shuffle paper or option order.
  const quick=$('#quick-picks');
  if(quick){
    const pool=[...themeData.monkeytype];
    for(let n=0;n<3;n++){
      const random=crypto.getRandomValues(new Uint32Array(1))[0];
      const theme=pool.splice(random%pool.length,1)[0];
      const input=$('input[name="theme"][value="'+CSS.escape(theme.id)+'"]');
      const button=document.createElement('button');
      button.type='button';button.className='theme-card';button.textContent=theme.name;button.dataset.theme=theme.id;
      button.style.setProperty('--preview-bg',theme.colors.bg);button.style.setProperty('--preview-text',theme.colors.main);
      button.addEventListener('click',()=>input.click());quick.append(button);
    }
  }
  $('#theme-search')?.addEventListener('input',e=>{const term=e.target.value.trim().toLowerCase();for(const card of $$('.theme-catalog .theme-card'))card.hidden=!card.textContent.toLowerCase().includes(term);});
  function filterReview(){const kind=$('#review-filter')?.value||'all',term=($('#review-search')?.value||'').trim().toLowerCase();const groups=$$('.review-group');let shown=0;for(const group of groups){group.hidden=!(kind==='all'||group.dataset.kinds.split(' ').includes(kind))||!group.textContent.toLowerCase().includes(term);if(!group.hidden)shown++;}if($('#review-count'))$('#review-count').textContent=shown+' / '+groups.length+' item groups';}
  $('#review-filter')?.addEventListener('change',filterReview);$('#review-search')?.addEventListener('input',filterReview);filterReview();
  const paper=$('.paper'), stage=$('.paper-stage');
  let rubiAnchor=null;
  const sizingContainers=paper?[$('.exam-section',paper),...$$('.cloze-frame',paper)].filter(Boolean):[];
  let paperZoom=1, sizingFrame=0, paperFrame, currentLayout,lastSizingKey='',fittedLayoutKey='',fittedRubi,fontGeneration=0;
  // Keep one set of intrinsic widths per mode. Typography changes still
  // invalidate measurements through metricsKey, and each element has at most two entries.
  const rubiMetrics={
    show:{tables:new WeakMap(),options:new WeakMap()},
    hide:{tables:new WeakMap(),options:new WeakMap()}
  };
  const annotationOriginals=new WeakMap();
  const wordColumns=new Map();
  for(const word of paper?$$('.wakachi',paper):[]){
    const column=word.closest('.option-text,.example-options>span,.example-native-options>span,.example-source-options>span,p,h2,h3,h4,li,td,th,div');
    if(!column)continue;
    if(!wordColumns.has(column))wordColumns.set(column,[]);
    wordColumns.get(column).push(word);
  }
  const wrappedWords=[],wordBreaks=[],tightColumns=new Set();
  const originalHeadingRuby=new Map();
  const percentageControls=new Map();
  // Enhance the existing shell, including pages cached before these fields
  // existed. Each slider keeps its own label; the textbox has a separate name.
  for(const [id,key,outputId,label]of[['text-size','text','text-output','Text size'],['paper-zoom','zoom','zoom-output','Paper zoom']]){
    const slider=$('#'+id);if(!slider)continue;
    const wrapper=document.createElement('div'),caption=document.createElement('label'),readout=document.createElement('span');
    const mode=document.createElement('span'),field=document.createElement('input');
    wrapper.className='range-label sizing-control';caption.htmlFor=id;caption.textContent=label.toLowerCase();
    readout.id=outputId;readout.className='percentage-readout';mode.append(document.createTextNode(''));
    field.id=key+'-percent';field.type='text';field.inputMode='decimal';field.autocomplete='off';field.spellcheck=false;
    field.setAttribute('aria-label',label+' percentage');field.title='Enter a percentage; press Enter or leave the field to apply.';
    const control={slider,mode,field,value:'100',dirty:false};percentageControls.set(key,control);
    readout.append(mode,field,document.createTextNode('%'));
    slider.closest('.range-label').replaceWith(wrapper);wrapper.append(caption,readout,slider);
    field.addEventListener('input',()=>{control.dirty=true;});
    field.addEventListener('blur',()=>{
      if(!control.dirty)return;control.dirty=false;
      const raw=field.value.trim(),number=Number(raw.replace(/%$/,'').trim());
      if(/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)\s*%?$/.test(raw)&&Number.isFinite(number)){
        const value=Math.max(Number(slider.min),Math.min(Number(slider.max),Math.round(number)));
        field.value=String(value);changeSizing(key,value);
      }else field.value=control.value;
    });
    field.addEventListener('keydown',event=>{
      if(event.key==='Enter'){event.preventDefault();field.blur();}
      if(event.key==='Escape'){event.preventDefault();event.stopPropagation();control.dirty=false;field.value=control.value;field.blur();}
    });
  }
  function percentage(key,value,mode){
    const control=percentageControls.get(key);if(!control)return;
    control.value=String(value);if(!control.dirty)control.field.value=control.value;
    setText(control.mode,mode);
  }
  function sizing(){
    if(!sizingFrame)sizingFrame=requestAnimationFrame(()=>applySizing());
  }
  let headingMetricsKey='';
  if(paper){
    paperFrame=document.createElement('div');paperFrame.className='paper-frame';
    paper.before(paperFrame);paperFrame.append(paper);
  }
  function sizePaperFrame(){
    // A transform scales text and hitboxes together without CSS zoom's
    // browser-dependent font sizing. Reserve exactly the painted page size.
    const rect=paper.getBoundingClientRect();
    const width=rect.width+'px',height=rect.height+'px';
    if(paperFrame.style.width!==width)paperFrame.style.width=width;
    if(paperFrame.style.height!==height)paperFrame.style.height=height;
  }
  function fitTables(metricsKey,tableMetrics){
    // TeX weights divide the measure after padding and rules. Native table
    // columns ignore mixed percent/length calc values, so resolve those source
    // weights against the current untransformed CSS measure. Percent widths
    // remain the readable no-JavaScript fallback.
    const rows=$$('table[data-column-weights]').map(table=>({table,cols:$$('colgroup>col',table).filter(col=>col.closest('table')===table),weights:table.dataset.columnWeights.split(',').map(Number),samples:[],scrollLeft:table.parentElement.scrollLeft})).filter(row=>row.cols.length===row.weights.length&&getComputedStyle(row.table).display==='table');
    const byTable=new Map(rows.map(row=>[row.table,row]));
    for(const row of rows){
      row.total=row.weights.reduce((a,b)=>a+b,0);row.table.style.minWidth='';
      row.cols.forEach((col,i)=>col.style.width=(100*row.weights[i]/row.total)+'%');
      row.depth=0;for(let p=row.table.parentElement.closest('table');p;p=p.parentElement.closest('table'))row.depth++;
    }
    // Resolve descendants first. A parent's minimum must depend on a nested
    // table's intrinsic minimum, never its width from the preceding resize.
    for(const row of [...rows].sort((a,b)=>b.depth-a.depth)){
      const cached=tableMetrics.get(row.table);
      if(cached?.key===metricsKey){
        Object.assign(row,cached);row.table.style.minWidth=row.minimum+'px';continue;
      }
      const occupied=[];
      for(const [r,tr] of [...row.table.rows].entries()){
        let c=0;
        for(const cell of [...tr.cells]){
          while(occupied[r]?.[c])c++;
          const span=cell.colSpan,clone=cell.cloneNode(true);
          // Measure the actual unbreakable content, including whole ruby and
          // bound dates, with the cell's inherited fonts and padding intact.
          // Absolute probes never take part in table layout or accessibility.
          clone.style.cssText+=';position:absolute;visibility:hidden;display:block;width:min-content;min-width:0;max-width:none;height:auto;box-sizing:content-box';
          const originals=$$('table',cell),copies=$$('table',clone);
          originals.forEach((table,i)=>{
            const child=byTable.get(table);if(!child)return;
            const copy=copies[i];copy.style.width=child.minimum+'px';copy.style.minWidth=child.minimum+'px';
            const wrapper=copy.parentElement;
            if(wrapper.classList.contains('table-scroll'))wrapper.style.cssText+=';width:'+child.minimum+'px;min-width:'+child.minimum+'px;max-width:none;overflow:visible';
          });
          clone.setAttribute('aria-hidden','true');tr.append(clone);
          row.samples.push({clone,column:c,span});
          for(let y=r;y<r+cell.rowSpan;y++){occupied[y]??=[];for(let x=c;x<c+span;x++)occupied[y][x]=true;}
          c+=span;
        }
      }
      const cell=$('td,th',row.table),cs=getComputedStyle(cell),px=x=>parseFloat(x)||0;
      const rule=(px(cs.borderLeftWidth)+px(cs.borderRightWidth))/2;
      row.cellSpace=px(cs.paddingLeft)+px(cs.paddingRight)+rule;
      row.rule=rule;
      let minTextWidth=0;
      for(const {clone,column,span} of row.samples){
        const weight=row.weights.slice(column,column+span).reduce((a,b)=>a+b,0);
        const needed=Math.max(0,clone.getBoundingClientRect().width/paperZoom-span*row.cellSpace);
        if(weight)minTextWidth=Math.max(minTextWidth,needed*row.total/weight);
      }
      // Retain source column proportions. If a cell cannot fit, the existing
      // scroll wrapper exposes the wider table instead of overlapping cells.
      row.minimum=Math.ceil(minTextWidth+row.cols.length*row.cellSpace+rule);
      tableMetrics.set(row.table,{key:metricsKey,minimum:row.minimum,cellSpace:row.cellSpace,rule:row.rule});
      row.samples.forEach(({clone})=>clone.remove());row.table.style.minWidth=row.minimum+'px';
    }
    for(const row of rows){
      const width=parseFloat(getComputedStyle(row.table).width)||row.minimum;
      row.textWidth=Math.max(1,width-row.rule-row.cols.length*row.cellSpace);
      row.cols.forEach((col,i)=>col.style.width=(row.textWidth*row.weights[i]/row.total+row.cellSpace)+'px');
      // Resetting provisional widths can momentarily clamp an existing pan.
      // Restore it only after the final minimum and column widths are set.
      row.table.parentElement.scrollLeft=row.scrollLeft;
    }
  }
  function fitOptions(metricsKey,optionMetrics){
    if(!paper)return;
    const px=value=>parseFloat(value)||0;
    const rows=$$('.question').filter(q=>!q.hasAttribute('data-image-panels')).map(q=>({q,grid:$('.options-grid',q),wanted:Number(q.dataset.nativeCols)||1,samples:[]}));
    // Batch DOM writes before measurements; do not force layout per answer.
    for(const row of rows){
      const cached=optionMetrics.get(row.grid);
      if(cached?.key===metricsKey){row.requirements=cached.requirements;continue;}
      for(const el of $$('.option-text',row.q)){
      const clone=el.cloneNode(true);clone.style.cssText='position:absolute;visibility:hidden;white-space:nowrap;width:max-content;max-width:none';
      clone.setAttribute('aria-hidden','true');el.parentNode.append(clone);row.samples.push({el,clone});
      }
    }
    for(const row of rows){
      row.width=row.grid.getBoundingClientRect().width/paperZoom;
      row.gap=px(getComputedStyle(row.grid).columnGap);
      row.requirements??=row.samples.map(({el,clone})=>{
        const cell=getComputedStyle(el.parentElement),text=getComputedStyle(el);
        const tracks=cell.gridTemplateColumns.split(/\s+/).map(px);
        // The middle track holds the answer. Account for the real number and
        // feedback tracks, gaps, text margins and cell edges at every text size.
        const fixed=tracks[0]+tracks[2]+2*px(cell.columnGap)
          +['paddingLeft','paddingRight','borderLeftWidth','borderRightWidth','marginLeft','marginRight'].reduce((sum,key)=>sum+px(cell[key]),0)
          +px(text.marginLeft)+px(text.marginRight);
        return clone.getBoundingClientRect().width/paperZoom+fixed;
      });
      optionMetrics.set(row.grid,{key:metricsKey,requirements:row.requirements});
      row.required=Math.max(...row.requirements);
      row.weights=row.grid.dataset.columnWeights?.split(',').map(Number);
    }
    for(const row of rows){
      row.samples.forEach(({clone})=>clone.remove());let cols=row.wanted;
      // Round down to the browser's layout precision so boundary cases do not
      // choose four columns when the last fraction of a glyph cannot fit.
      const fits=count=>row.weights&&count===row.wanted
        ?row.requirements.every((required,i)=>Math.floor(row.width*row.weights[i%count]*64)/64>=required)
        :Math.floor((row.width-(count-1)*(row.weights?0:row.gap))/count*64)/64>=row.required;
      while(cols>1&&!fits(cols))cols=cols>2?2:1;
      row.grid.style.setProperty('--option-columns',String(cols));
      if(row.weights){
        row.grid.style.gridTemplateColumns=cols===row.wanted?row.weights.map(w=>(w*100)+'%').join(' '):'repeat('+cols+',minmax(0,1fr))';
        row.grid.style.columnGap=cols===row.wanted?((1-row.weights.reduce((a,b)=>a+b,0))/(cols-1)*100)+'%':'0';
      }
    }
    // Worked examples are unscored, but their printed choices need the same
    // measured four/two/one-column fitting as answer choices. Explicit source
    // vertical layouts retain their inline one-column rule.
    const examples=$$('.example-options,.example-native-options,.example-source-options').filter(grid=>!grid.hasAttribute('data-image-panels')).map(grid=>({grid,wanted:Number(grid.dataset.nativeCols)||4,samples:[]}));
    for(const row of examples){
      const cached=optionMetrics.get(row.grid);
      if(cached?.key===metricsKey){row.required=cached.required;continue;}
      for(const el of [...row.grid.children]){
      const clone=el.cloneNode(true);clone.style.cssText='position:absolute;visibility:hidden;white-space:nowrap;width:max-content;max-width:none';
      clone.setAttribute('aria-hidden','true');row.grid.append(clone);row.samples.push(clone);
      }
    }
    for(const row of examples){
      row.width=row.grid.getBoundingClientRect().width/paperZoom;
      row.gap=px(getComputedStyle(row.grid).columnGap);
      row.required??=Math.max(...row.samples.map(el=>el.getBoundingClientRect().width/paperZoom));
      optionMetrics.set(row.grid,{key:metricsKey,required:row.required});
    }
    for(const row of examples){
      row.samples.forEach(el=>el.remove());let cols=row.wanted;
      while(cols>1&&Math.floor((row.width-(cols-1)*row.gap)/cols*64)/64<row.required)cols=cols>2?2:1;
      row.grid.style.setProperty('--example-columns',String(cols));
    }
  }
  function fitHeadings(metricsKey){
    if(!paper||headingMetricsKey===metricsKey)return;
    const zoom=paperZoom;
    const rows=[];
    for(const heading of $$('.section-heading')){
      const label=$('.heading-label',heading);if(!label)continue;
      const cs=getComputedStyle(heading),ls=getComputedStyle(label);
      const em=parseFloat(cs.fontSize)/(parseFloat(cs.getPropertyValue('--glyph-scale'))||1);
      const horizontal=parseFloat(cs.getPropertyValue('--heading-horizontal-scale'))||1;
      const visual=$('.heading-label-visual',label);
      const pullback=parseFloat(cs.getPropertyValue('--heading-continuation-pullback-em'));
      rows.push({heading,label,horizontal,em,pullback,margin:parseFloat(ls.marginRight),width:visual?visual.getBoundingClientRect().width/zoom/horizontal:null});
    }
    // Two measurement phases keep each heading from forcing a document layout.
    for(const row of rows)if(row.width!==null)row.label.style.setProperty('--heading-label-width',row.width+'px');
    for(const row of rows)row.hang=Math.max(0,row.label.getBoundingClientRect().width/zoom/row.horizontal+row.margin-row.em*(Number.isFinite(row.pullback)?row.pullback:1));
    for(const row of rows)row.heading.style.setProperty('--heading-hang',row.hang+'px');
    headingMetricsKey=metricsKey;
  }
  function fitLongWords(){
    // Keep ordinary Japanese groups intact. Only measure individual words
    // when their column actually overflows, then apply all breaks together.
    const overflowing=[],breakBefore=[],splitRuby=[];
    // A long task label can leave too little room for an instruction word
    // or its choice sequence. Reclaim the hanging indent only on overflow.
    for(const heading of $$('.section-heading',paper)){
      if(heading.scrollWidth>heading.clientWidth+1)tightColumns.add(heading);
    }
    for(const entry of wordColumns){
      const [column,words]=entry;
      if(column.scrollWidth<=column.clientWidth+1)continue;
      overflowing.push(entry);
      // A glyph or a whole ruby needs a wider line when it cannot break.
      const style=getComputedStyle(column);
      const line=column.clientWidth-parseFloat(style.paddingLeft)-parseFloat(style.paddingRight);
      const box=column.getBoundingClientRect(),scale=box.width/(column.offsetWidth||1);
      const indented=parseFloat(style.textIndent)>0&&words[0].getBoundingClientRect().right>box.right+.5;
      if(indented&&column.matches('p,li'))tightColumns.add(column);
      const container=column.closest('.section-heading,.options-grid,.dialogue,.question-content,.reading-passage,.notice-frame');
      if(container&&(indented||line+.5<parseFloat(style.fontSize)||(preferences.rubi==='show'&&$$('ruby',column).some(ruby=>ruby.getBoundingClientRect().width>line*scale+.5)))){
        tightColumns.add(container);
      }
    }
    for(const column of tightColumns)column.classList.add('wide-word-column');
    if(preferences.rubi==='show'){
      for(const heading of tightColumns){
        if(!heading.matches('.section-heading')||heading.scrollWidth<=heading.clientWidth+1)continue;
        const line=heading.getBoundingClientRect();
        for(const ruby of $$('ruby',heading)){
          if(ruby.textContent==='文章全体ぶんしょうぜんたい'&&ruby.getBoundingClientRect().width>line.width+.5)splitRuby.push(ruby);
          const next=ruby.nextSibling;
          if(next?.nodeName!=='RUBY')continue;
          const end=next.getBoundingClientRect();
          if(end.right>line.right+.5&&ruby.getBoundingClientRect().width+end.width>line.width+.5)breakBefore.push(next);
        }
      }
    }
    // Changing a grid can also resize children that originally fit their tracks.
    for(const [column,words] of tightColumns.size?wordColumns:overflowing){
      const width=column.clientWidth;
      if(!width||column.scrollWidth<=width+1)continue;
      const box=column.getBoundingClientRect(),style=getComputedStyle(column);
      const scale=box.width/column.offsetWidth;
      const line=(width-parseFloat(style.paddingLeft)-parseFloat(style.paddingRight))*scale;
      const right=box.right-(parseFloat(style.borderRightWidth)+parseFloat(style.paddingRight))*scale;
      for(const word of words){
        const rect=word.getBoundingClientRect();
        if(rect.right<=right+.5)continue;
        if(rect.width>line+.5)wrappedWords.push(word);
        else if(word.previousSibling?.matches?.('.wakachi'))breakBefore.push(word);
      }
    }
    for(const word of wrappedWords)word.classList.add('wakachi-wrap');
    for(const word of breakBefore){
      const br=document.createElement('wbr');word.before(br);wordBreaks.push(br);
    }
    // The workbooks supply the reading for each half of this compound.
    for(const ruby of splitRuby){
      const parts=document.createElement('span');
      parts.innerHTML='<ruby>文章<rt>ぶんしょう</rt></ruby><wbr><ruby>全体<rt>ぜんたい</rt></ruby>';
      originalHeadingRuby.set(parts,ruby);
      ruby.replaceWith(parts);
    }
  }
  function fitAnnotations(modeOnly){
    const terms=$$('.annotated-term',paper).filter(term=>!term.closest('.vertical-frame'));
    const probes=[];
    for(const term of terms){
      const base=$(':scope>.annotation-base',term),initial=$('.annotation-initial',base);
      if(initial){
        const label=$('.annotation-label',initial),first=$('.annotation-initial-base',initial);
        const splitRuby=initial.closest('ruby');
        term.append(label);
        const original=modeOnly?annotationOriginals.get(base):null;
        annotationOriginals.delete(base);
        if(original){
          base.replaceChildren(...original.childNodes);
        }else{
          while(first.firstChild)initial.before(first.firstChild);
          initial.remove();
        }
        splitRuby?.normalize();
      }
      term.classList.remove('annotation-breakable');
      const probe=base.cloneNode(true);
      probe.style.cssText='position:absolute;visibility:hidden;display:block;white-space:nowrap;width:max-content;max-width:none';
      probe.setAttribute('aria-hidden','true');term.append(probe);
      probes.push({term,base,probe});
    }
    for(const row of probes){
      const container=row.term.closest('p,td,.source-block');
      row.long=row.probe.getBoundingClientRect().width>(container?.getBoundingClientRect().width||paper.clientWidth)/4;
    }
    for(const {term,base,probe,long} of probes){
      probe.remove();if(!long)continue;
      const walker=document.createTreeWalker(base,NodeFilter.SHOW_TEXT,{acceptNode(node){return node.parentElement.closest('rt,rp,.source-literal,.visual-only')||!node.data.length?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT;}});
      const first=walker.nextNode();if(!first)continue;
      const range=document.createRange();range.setStart(base,0);
      const ruby=first.parentElement.closest('ruby');
      // With the reading hidden, anchor the note to one glyph in place.
      // Extracting across its ruby wrapper would split the reading on Show.
      const insideRuby=ruby&&base.contains(ruby)&&preferences.rubi==='hide';
      if(insideRuby)range.setStart(first,0);
      if(ruby&&base.contains(ruby)&&!insideRuby)range.setEndAfter(ruby);
      else range.setEnd(first,[...first.data][0].length);
      // A range ending inside a styled prefix splits its wrapper. Reuse the
      // intact measurement copy so switching modes cannot accumulate spacers.
      if(!insideRuby&&first.parentElement!==base&&range.endContainer!==base)annotationOriginals.set(base,probe);
      const anchor=document.createElement('span'),content=document.createElement('span');
      anchor.className='annotation-initial';content.className='annotation-initial-base';
      content.append(range.extractContents());anchor.append(content,$(':scope>.annotation-label',term));
      if(insideRuby)first.before(anchor);else base.prepend(anchor);
      term.classList.add('annotation-breakable');
    }
  }
  function applySizing(layoutOnly=false){
    cancelAnimationFrame(sizingFrame);sizingFrame=0;
    if(!paper)return;
    const width=sizingPolicy.A4,available=Math.max(1,stage.clientWidth-parseFloat(getComputedStyle(stage).paddingLeft)-parseFloat(getComputedStyle(stage).paddingRight));
    const mobile=window.innerWidth<=650;
    const key=JSON.stringify([available,mobile,preferences.rubi,preferences.marking==='margin',preferences.text,preferences.zoom,preferences.zoomWidth,preferences.zoomMargins,preferences.line,preferences.block,fontGeneration]);
    if(key===lastSizingKey){rubiAnchor=null;return;}
    lastSizingKey=key;
    const cs=getComputedStyle(paper),bodyPt=parseFloat(cs.getPropertyValue('--body-pt'))||11.3,glyphScale=parseFloat(cs.getPropertyValue('--glyph-scale'))||1;
    const sourceMargins=['top','right','bottom','left'].map(side=>parseFloat(cs.getPropertyValue('--margin-'+side))||0);
    const sourcePx=bodyPt*96/72.27*glyphScale;
    const scale=preferences.text==='auto'?sizingPolicy.autoText(available,sourcePx):Number(preferences.text)/100;
    document.body.style.setProperty('--text-scale',String(scale));
    document.body.style.setProperty('--line-preset','1');document.body.style.setProperty('--block-preset','1');
    document.body.style.setProperty('--line-adjust',String(Number(preferences.line)/100));document.body.style.setProperty('--block-adjust',String(Number(preferences.block)/100));
    // Let the same CSS rhythm as section transitions own the top inset, also
    // without JS. Do not restore a fixed top padding from a saved zoom state.
    paper.style.removeProperty('padding-top');
    currentLayout=sizingPolicy.layout(preferences,available,sourceMargins,parseFloat(getComputedStyle(paper).paddingTop));
    const {zoom,responsive}=currentLayout,layout=currentLayout.width;
    paperZoom=zoom;
    paper.dataset.layout=responsive?'responsive':'fixed';
    paper.dataset.narrow=String(responsive&&currentLayout.baseWidth<=650);
    // Intrinsic text widths survive a container resize or magnification change.
    // Font completion, text size, spacing and responsive CSS invalidate them.
    const metricsKey=JSON.stringify([scale,preferences.line,preferences.block,mobile,paper.dataset.narrow,fontGeneration]);
    paper.style.width=layout+'px';paper.style.maxWidth='none';paper.style.transform=zoom===1?'none':'scale('+zoom+')';
    const margins=currentLayout.margins;
    ['Right','Bottom','Left'].forEach((side,i)=>{paper.style['padding'+side]=margins[i+1]+'px';});
    paper.style.setProperty('--reader-left',margins[3]+'px');paper.style.setProperty('--reader-right',margins[1]+'px');
    percentage('text',preferences.text==='auto'?Math.round(scale*100):preferences.text,preferences.text==='auto'?'auto · ':'');
    $('#text-size').value=preferences.text==='auto'?Math.round(scale*100):preferences.text;
    const percent=Math.round(zoom*100),zoomControl=$('#paper-zoom');
    // Fit width is a shortcut, not a lower bound on manual magnification.
    zoomControl.min=Math.max(1,Math.min(25,Math.floor(available/width*100),percent));
    zoomControl.max=Math.max(500,Math.ceil(available/width*100),percent);
    zoomControl.value=percent;
    const mode=responsive?'screen':'A4';
    percentage('zoom',percent,(preferences.zoom==='auto'?'auto · ':preferences.zoom==='fit'?'fit · ':'')+mode+' · ');
    zoomControl.setAttribute('aria-valuetext',(preferences.zoom==='auto'?'Auto, ':'')+percent+'% of '+(responsive?'screen layout':'A4')+(preferences.zoom==='fit'?', fit to screen width':''));
    for(const button of $$('[data-zoom]'))button.setAttribute('aria-pressed',String(button.dataset.zoom===preferences.zoom||(button.dataset.zoom==='reference'&&!responsive&&Math.abs(layout-width)<.01&&Number(preferences.zoom)===100)));
    $('#auto-text').setAttribute('aria-pressed',String(preferences.text==='auto'));
    $('#source-text').setAttribute('aria-pressed',String(Number(preferences.text)===100));
    $('#line-adjust').value=preferences.line;$('#block-adjust').value=preferences.block;
    setText($('#line-output'),preferences.line+'%');setText($('#block-output'),preferences.block+'%');
    if(layoutOnly)return;
    // Magnification trims spare margins without changing the text measure.
    // Refit only after typography, responsive rules or that measure change.
    // Cloze frames can extend into trimmed margins. Include their resolved
    // widths, and the browser's rounded column width, before reusing a fit.
    const layoutKey=JSON.stringify([metricsKey,responsive,preferences.marking==='margin',Math.round((layout-margins[1]-margins[3])*64),...sizingContainers.map(node=>getComputedStyle(node).width)]);
    if(layoutKey!==fittedLayoutKey||preferences.rubi!==fittedRubi){
      for(const word of wrappedWords)word.classList.remove('wakachi-wrap');
      for(const br of wordBreaks)br.remove();
      for(const [parts,ruby] of originalHeadingRuby)parts.replaceWith(ruby);
      originalHeadingRuby.clear();
      for(const column of tightColumns)column.classList.remove('wide-word-column');
      wrappedWords.length=0;wordBreaks.length=0;tightColumns.clear();
      const metrics=rubiMetrics[preferences.rubi];
      fitHeadings(metricsKey+preferences.rubi);fitTables(metricsKey,metrics.tables);fitOptions(metricsKey,metrics.options);
      fitAnnotations(layoutKey===fittedLayoutKey);fitLongWords();
      fittedLayoutKey=layoutKey;fittedRubi=preferences.rubi;
    }
    sizePaperFrame();
    if(rubiAnchor){
      alignReading(rubiAnchor);
      rubiAnchor=null;
    }
  }
  function reflectReaderOptions(){
    if(!paper)return;
    const body=document.body;
    const mode=rubiControls.length?preferences.rubi:'show';
    if(body.dataset.rubi!==mode){
      if(body.dataset.rubi&&window.scrollY>0&&!rubiAnchor){
        const node=readingNode(readerEdge());
        rubiAnchor={node,top:node?.getBoundingClientRect().top};
      }
      displayRubi(mode);
    }
    body.dataset.marking=$('[name=marking]:checked')?.value||'cell';
    body.dataset.spacing=preferences.spacing;
    body.toggleAttribute('data-show-star-order',Boolean(preferences.star));
    body.toggleAttribute('data-visible-paper',Boolean(preferences.border));
  }
  function apply(){
    for(const input of rubiControls)input.checked=input.value===preferences.rubi;
    for(const name of ['theme','marking'])select(name,preferences[name]);
    select('text-source',preferences.textSource||'auto');
    select('star-behavior',preferences.star?'show':'hide');
    for(const i of $$('[name=spacing]'))i.checked=i.value===preferences.spacing;
    if($('#visible-paper'))$('#visible-paper').checked=preferences.border;
    $('#remember').checked=remember;
    for(const [id,key] of [['line-adjust','line'],['block-adjust','block']])if($('#'+id))$('#'+id).value=preferences[key];
    reflectReaderOptions();brightness();sizing();status();practiceUI?.apply();
  }
  for(const name of ['theme','spacing','marking','rubi'])for(const input of $$('input[name="'+name+'"]'))input.addEventListener('change',()=>{
    preferences[name]=input.value;
    if(name==='theme')brightness();
    else{
      if(name==='spacing')Object.assign(preferences,spacingPresets[input.value]);
      reflectReaderOptions();sizing();
    }
    persist();
  });
  for(const i of $$('input[name="text-source"]'))i.addEventListener('change',()=>{preferences.textSource=i.value;brightness();persist();});
  for(const i of $$('[name=star-behavior]'))i.addEventListener('change',()=>{preferences.star=i.value==='show';reflectReaderOptions();persist();});
  $('#visible-paper')?.addEventListener('change',e=>{preferences.border=e.target.checked;reflectReaderOptions();persist();});
  function changeSizing(key,value){
    // Detach Auto from the layout already on screen. Never make the first
    // slider movement replace a narrow page with a full A4 sheet.
    if(key==='zoom'&&preferences.zoom==='auto'){
      // Resolve a pending Auto layout before detaching, but measure text only
      // once, at the final magnification, to retain identical glyph placement.
      if(!currentLayout||sizingFrame)applySizing(true);
      preferences.zoomWidth=currentLayout.baseWidth;
      preferences.zoomMargins=[...currentLayout.baseMargins];
    }
    preferences[key]=value;
    if(key==='line'||key==='block'){preferences.spacing=Object.keys(spacingPresets).find(k=>spacingPresets[k].line===preferences.line&&spacingPresets[k].block===preferences.block)||'custom';for(const i of $$('[name=spacing]'))i.checked=i.value===preferences.spacing;reflectReaderOptions();}
    sizing();persist();
  }
  for(const [id,key]of[['text-size','text'],['paper-zoom','zoom'],['line-adjust','line'],['block-adjust','block']])$('#'+id)?.addEventListener('input',e=>changeSizing(key,Number(e.target.value)));
  $('#auto-text')?.addEventListener('click',()=>{preferences.text='auto';apply();persist();});
  $('#source-text')?.addEventListener('click',()=>{preferences.text=100;apply();persist();});
  for(const b of $$('[data-zoom]'))b.addEventListener('click',()=>{preferences.zoom=b.dataset.zoom;delete preferences.zoomWidth;delete preferences.zoomMargins;apply();persist();});
  let lastScrollY=window.scrollY,pendingBookmark=null,scrollSaveTimer;
  const paperRecord=storage.openPractice('paper',data.paper,remember,()=>sessionEpoch);
  const gradableQuestions=(data.questions||[]).filter(AstraPractice.gradable);
  const bindings=Object.fromEntries(gradableQuestions.map(q=>[q.id,q.binding]));
  let observedAnswers='';
  let autoSpoil=preferences.autoSpoil===true;
  function markSpoiledChoice(question,selected){
    const key=Number(question.dataset.key);
    const correct=document.getElementById(question.id+'-'+key);
    const show=autoSpoil&&selected!==undefined&&selected!==key;
    if(!correct||correct.hasAttribute('data-spoiled')===show)return;
    correct.toggleAttribute('data-spoiled',show);
    if(show){
      const mark=document.createElement('span');
      mark.className='margin-answer spoiled-margin';
      mark.dataset.choice=String(key);
      mark.setAttribute('aria-hidden','true');
      $('.margin-answer',question).after(mark);
    }else $('.spoiled-margin',question)?.remove();
  }
  function applyAutoSpoil(){
    const enabled=preferences.autoSpoil===true;
    if(autoSpoil===enabled)return;
    autoSpoil=enabled;
    for(const [id,record] of Object.entries(answers))markSpoiledChoice(document.getElementById(id),record.selected);
  }
  function replaceSelections(next){
    for(const id of new Set([...Object.keys(answers),...Object.keys(next)])){
      const selected=next[id]?.selected,previous=answers[id]?.selected;
      if(selected===previous)continue;
      const input=document.getElementById(id+'-'+(selected??previous));
      input.checked=selected!==undefined;
      const question=input.closest('.question');
      markSpoiledChoice(question,selected);
      $('.answer-announcement',question).textContent='';
    }
    answers=next;
  }
  function restoreSelections(session){
    const saved=session?.answers||{},signature=JSON.stringify(saved);
    if(signature===observedAnswers)return false;
    observedAnswers=signature;
    const restored={};
    for(const [id,record] of Object.entries(saved)){
      if(!bindings[id]||session.bindings?.[id]!==bindings[id]||!Number.isInteger(record?.selected))continue;
      const input=document.getElementById(id+'-'+record.selected);
      if(input&&!input.disabled)restored[id]=AstraPractice.restoreAnswer(record);
    }
    replaceSelections(restored);
    return true;
  }
  function syncPaper(){
    if(!paperRecord)return;
    const current=storage.preferences();
    if(current.epoch!==sessionEpoch||current.remember!==remember)syncPreferences(current);
    if(!remember||!storage.available)return;
    const record=paperRecord.read();
    if(record&&restoreSelections(record)){
      if(practiceUI?.feedbackVisible&&AstraPractice.recordFirstFeedback(gradableQuestions,answers))saveAnswers();
      progress();
    }
  }
  function saveAnswers(){
    if(!remember||!paperRecord)return;
    const saved=paperRecord.read();
    const record={answers,position:saved?.position??0,bindings:Object.fromEntries(Object.keys(answers).map(id=>[id,bindings[id]]))};
    if(Number.isFinite(saved?.positionUpdatedAt))record.positionUpdatedAt=saved.positionUpdatedAt;
    if(saved?.anchor)record.anchor=saved.anchor;
    if(paperRecord.save(record,sessionEpoch))observedAnswers=JSON.stringify(answers);
    status();
  }
  function progress(now=Date.now()){
    if(!data.paper)return;
    const counts=AstraPractice.progress(gradableQuestions,answers),visible=practiceUI?.feedbackVisible??preferences.autoGrade;
    const count=(visible?counts.correct:'?')+' / '+counts.total;
    const detail=preferences.autoGrade?(counts.firstTotal?'First try '+counts.firstCorrect+'/'+counts.firstTotal:''):'Answered '+counts.answered+'/'+counts.total;
    setText(progressCount,count);setText(progressDetail,detail);
    progressCorrect.toggleAttribute('hidden',!visible);
    const label=count+(visible?' correct':' grade hidden')+(detail?' · '+detail:'');
    if(progressRoot.getAttribute('aria-label')!==label)progressRoot.setAttribute('aria-label',label);
    if(progressRoot.title!==label)progressRoot.title=label;
    practiceUI?.setComplete(counts.total>0&&counts.answered===counts.total,now);
    if($('#score-dialog')?.open)practiceUI?.refreshScore();
  }
  function clearSelected(input){
    if(!preferences.allowUnclick||!input.matches('.answer-radio:enabled:checked'))return;
    const now=Date.now();
    const id=input.name;
    if(answers[id]?.selected!==Number(input.value))return;
    syncPaper();
    if(answers[id]?.selected!==Number(input.value))return;
    delete answers[id];input.checked=false;
    const question=input.closest('.question');
    markSpoiledChoice(question);
    $('.answer-announcement',question).textContent='Answer cleared.';
    saveAnswers();progress(now);
  }
  paper?.addEventListener('click',event=>clearSelected(event.target));
  // Browsers differ on whether Space clicks an already-checked radio.
  // Own that activation only; new choices and arrow keys stay native.
  let spaceSelection=null;
  paper?.addEventListener('keydown',event=>{
    if(event.key!==' ')return;
    if(!event.repeat)spaceSelection=preferences.allowUnclick&&event.target.matches('.answer-radio:enabled:checked')?event.target:null;
    if(spaceSelection===event.target)event.preventDefault();
  });
  paper?.addEventListener('keyup',event=>{
    if(event.key!==' '||spaceSelection!==event.target)return;
    event.preventDefault();spaceSelection=null;clearSelected(event.target);
  });
  paper?.addEventListener('change',event=>{
    const input=event.target;
    if(!input.matches('.answer-radio:enabled:checked'))return;
    const now=Date.now();
    syncPaper();
    const q=input.closest('.question'),id=q.id,correct=input.dataset.correct==='true';
    const visible=practiceUI.feedbackVisible;
    input.checked=true;
    answers[id]=AstraPractice.answer(answers[id],Number(input.value),Number(q.dataset.key),visible);
    markSpoiledChoice(q,Number(input.value));
    let announcement=visible?(correct?'Correct.':'Incorrect. Try again.'):'Answer selected.';
    if(autoSpoil&&!correct)announcement=visible?'Incorrect. The correct answer is '+q.dataset.key+'.':'Answer selected. Options '+[Number(input.value),Number(q.dataset.key)].sort().join(' and ')+' are marked.';
    $('.answer-announcement',q).textContent=announcement;
    saveAnswers();progress(now);
  });
  if(remember&&paperRecord){
    const session=paperRecord.read();restoreSelections(session);
    const savedPosition=Number(session?.position);
    if(Number.isFinite(savedPosition)&&savedPosition>0&&!location.hash){
      restoring=true;
      document.fonts.ready.then(()=>requestAnimationFrame(()=>requestAnimationFrame(()=>{
        window.scrollTo(0,savedPosition);
        const anchor=session.anchor,node=anchor&&document.getElementById(anchor.id);
        if(node&&paper.contains(node)&&Number.isFinite(anchor.offset)){
          window.scrollBy(0,node.getBoundingClientRect().top-readerEdge()-anchor.offset);
        }
        lastScrollY=window.scrollY;restoring=false;
      })));
    }
  }
  function readerEdge(){return Math.max(0,$('.reader-subbar').getBoundingClientRect().bottom);}
  function readingNode(edge){
    const hit=document.elementsFromPoint(document.documentElement.clientWidth/2,edge+12).find(el=>paper.contains(el));
    if(!hit)return settings.open?readingAnchor?.node.closest('[id]'):null;
    return hit.closest('.question[id],.source-block[id],.source-heading[id]')||captureReading()?.node.closest('[id]');
  }
  function savePosition(){
    const bookmark=pendingBookmark;pendingBookmark=null;
    if(!bookmark||!remember||!paperRecord)return;
    const saved=paperRecord.read()||{answers:{},bindings:{}};
    if(saved.positionUpdatedAt>bookmark.positionUpdatedAt)return;
    const edge=readerEdge(),node=bookmark.position>0&&readingNode(edge);
    bookmark.anchor=node?{id:node.id,offset:node.getBoundingClientRect().top-edge}:null;
    paperRecord.save({...saved,...bookmark},sessionEpoch);
  }
  window.addEventListener('scroll',()=>{
    if(restoring||rubiAnchor||lastScrollY===window.scrollY)return;
    lastScrollY=window.scrollY;
    if(!remember||!paperRecord)return;
    pendingBookmark={position:lastScrollY,positionUpdatedAt:Date.now()};
    clearTimeout(scrollSaveTimer);scrollSaveTimer=setTimeout(savePosition,250);
  },{passive:true});
  window.addEventListener('pagehide',savePosition);
  window.addEventListener('storage',e=>{if(e.key===null||e.key===prefix+'preferences')syncPreferences();else if(paperRecord&&e.key===prefix+paperRecord.key)syncPaper();});
  window.addEventListener('focus',()=>syncPreferences());
  document.addEventListener('visibilitychange',()=>{if(!document.hidden)syncPreferences();});
  function forget(){remember=false;pendingBookmark=null;storage.forget();observedPreferences=JSON.stringify(storage.preferences());$('#remember').checked=false;status();}
  $('#remember').addEventListener('change',e=>{
    if(!e.target.checked){forget();return;}
    const current=storage.preferences();
    if(current.remember&&storage.available){syncPreferences(current);return;}
    // Re-enabling in this tab explicitly saves the visit that is on screen.
    sessionEpoch=current.epoch;remember=true;persist(true);
    saveAnswers();
    if(paperRecord){
      pendingBookmark={position:window.scrollY,positionUpdatedAt:Date.now()};savePosition();
      practiceUI?.save();
    }
    status();
  });
  function confirmBrowserAction(trigger,description,action){
    const id=trigger.id+'-dialog';
    document.body.insertAdjacentHTML('beforeend',`<dialog id="${id}" class="practice-dialog practice-confirm" aria-labelledby="${id}-title" aria-describedby="${id}-description">
      <h2 id="${id}-title">are you sure?</h2><p id="${id}-description"></p>
      <div class="button-row"><button type="button" class="warning-cancel" data-dialog-close autofocus>cancel</button>
      <button type="button" class="warning-confirm"></button></div></dialog>`);
    const dialog=document.getElementById(id);
    $('p',dialog).textContent=description;
    const confirm=$('.warning-confirm',dialog);
    confirm.textContent=trigger.textContent;
    trigger.addEventListener('click',()=>{
      trigger.focus({preventScroll:true});
      dialog.showModal();
    });
    confirm.addEventListener('click',()=>{
      if(!dialog.open)return;
      action();
      dialog.close();
    });
  }
  confirmBrowserAction($('#reset-preferences'),'This will restore your settings for this site to their defaults on this browser. This action cannot be undone.',()=>{
    preferences=normalizePreferences({timerDisabledTotal:preferences.timerDisabledTotal});
    previousPreferences=null;
    apply();
    persist();
  });
  confirmBrowserAction($('#forget'),'This will turn off saving and delete all saved data for this site on this browser, including your settings, answers, practice counts, timers, and reading positions. This action cannot be undone.',()=>{
    forget();
    toast('Saved data removed. Current answers remain until you leave.');
  });
  function applyPaperAction(action){
    if(action!=='clear'&&!(action==='spoil'&&preferences.spoilAll))return;
    syncPaper();
    const now=Date.now();
    const next={};
    if(action==='spoil'){
      for(const q of gradableQuestions)next[q.id]=AstraPractice.answer(answers[q.id],q.key,q.key,practiceUI.feedbackVisible);
    }
    replaceSelections(next);
    saveAnswers();
    progress(now);
  }
  practiceUI=AstraPracticeUI({$,$$,data,storage,prefix,prefs:()=>preferences,persist,progress,saveAnswers,syncPaper,applyAutoSpoil,applyPaperAction,answers:()=>answers,remember:()=>remember,epoch:()=>sessionEpoch});
  apply();progress();persist();
  if(paper){
    document.fonts.ready.then(()=>{fontGeneration++;sizing();});
    new ResizeObserver(sizePaperFrame).observe(paper);
    let frame;window.addEventListener('resize',()=>{cancelAnimationFrame(frame);frame=requestAnimationFrame(sizing);});
  }
})();
