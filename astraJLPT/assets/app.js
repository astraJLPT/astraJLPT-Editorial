/* Color math shared by the editor and its non-browser regression checks. */
globalThis.AstraThemeColors = (() => {
  'use strict';
  function normalize(value, alpha=true) {
    if(typeof value!=='string'||!/^#(?:[\da-f]{3}|[\da-f]{4}|[\da-f]{6}|[\da-f]{8})$/i.test(value.trim()))return null;
    let h=value.trim().slice(1).toLowerCase();
    if(h.length<5)h=[...h].map(c=>c+c).join('');
    if(!alpha&&h.length===8&&h.slice(6)!=='ff')return null;
    return '#'+(h.endsWith('ff')&&h.length===8?h.slice(0,6):h);
  }
  function rgba(value) {
    const h=normalize(value).slice(1);
    return [0,2,4].map(i=>parseInt(h.slice(i,i+2),16)).concat(h.length===8?parseInt(h.slice(6),16)/255:1);
  }
  const byte=v=>Math.max(0,Math.min(255,Math.round(v))).toString(16).padStart(2,'0');
  const hex=c=>'#'+c.slice(0,3).map(byte).join('')+(c[3]<1?byte(c[3]*255):'');
  const css=c=>`rgba(${c[0]}, ${c[1]}, ${c[2]}, ${c[3]})`;
  function resolve(theme, mode, overrides, roles, fills={}) {
    const source={...theme.editorColors[mode]};
    for(const role of roles){
      if(role.formula){
        const opacity=fills[role.fillControl];
        source[role.id]=role.fillControl&&validOpacity(opacity)?role.formula.replace(/[\d.]+%/,opacity+'%'):role.formula;
      }
      if(role.editable&&Object.hasOwn(overrides||{},role.id)){
        const value=normalize(overrides[role.id],role.alpha);
        if(value)source[role.id]=value;
      }
    }
    const resolved={},active=new Set();
    function expression(value) {
      if(value==='transparent')return [0,0,0,0];
      if(normalize(value))return rgba(value);
      const ref=/^var\(--([\w-]+)\)$/.exec(value);
      if(ref)return color(ref[1]);
      const mix=/^color-mix\(in srgb,\s*(var\(--[\w-]+\)|#[\da-f]+)\s+([\d.]+)%,\s*(transparent|var\(--[\w-]+\)|#[\da-f]+)\)$/i.exec(value);
      if(!mix)throw new Error('Unsupported theme color: '+value);
      const a=expression(mix[1]),b=expression(mix[3]),w=Number(mix[2])/100;
      const opacity=a[3]*w+b[3]*(1-w);
      return a.slice(0,3).map((v,i)=>opacity?(v*a[3]*w+b[i]*b[3]*(1-w))/opacity:0).concat(opacity);
    }
    function color(id) {
      if(resolved[id])return resolved[id];
      if(active.has(id))throw new Error('Cyclic color: '+id);
      active.add(id);resolved[id]=expression(source[id]);active.delete(id);return resolved[id];
    }
    for(const role of roles)color(role.id);
    return resolved;
  }
  function sanitize(value,themes,roles) {
    const result={};
    if(!value||typeof value!=='object'||Array.isArray(value))return result;
    for(const theme of themes){
      const incoming=Object.hasOwn(value,theme.id)?value[theme.id]:null;
      if(!incoming||typeof incoming!=='object'||Array.isArray(incoming))continue;
      const colors={};
      for(const role of roles){
        if(!role.editable)continue;
        const color=Object.hasOwn(incoming,role.id)?normalize(incoming[role.id],role.alpha):null;
        if(color)colors[role.id]=color;
      }
      if(Object.keys(colors).length)result[theme.id]=colors;
    }
    return result;
  }
  function validOpacity(value){return typeof value==='number'&&Number.isFinite(value)&&value>=0&&value<=100;}
  function sanitizeFills(value,themes,controls){
    const result={};
    if(!value||typeof value!=='object'||Array.isArray(value))return result;
    for(const theme of themes){
      const incoming=Object.hasOwn(value,theme.id)?value[theme.id]:null;
      if(!incoming||typeof incoming!=='object'||Array.isArray(incoming))continue;
      const fills={};
      for(const control of controls){
        const v=Object.hasOwn(incoming,control.id)?incoming[control.id]:null;
        if(validOpacity(v)&&Math.round(v)!==control.default)fills[control.id]=Math.round(v);
      }
      if(Object.keys(fills).length)result[theme.id]=fills;
    }
    return result;
  }
  return {normalize,rgba,hex,css,resolve,sanitize,sanitizeFills};
})();

/* Shared sizing policy. Inputs are CSS pixels, never device or browser IDs. */
(() => {
  'use strict';
  const A4=210*96/25.4;
  const AUTO_MAX=1.4,GUTTER=14;
  const clamp=(n,lo,hi)=>Math.min(hi,Math.max(lo,n));
  function transition(width,start,end){
    const t=clamp((width-start)/(end-start),0,1);
    return t*t*(3-2*t);
  }
  function autoText(available,sourcePx){
    const narrow=clamp(17/sourcePx,1,1.8);
    // Retain a readable narrow-screen starting size; reach source typography
    // when an A4 layout fits. Paper magnification is deliberately not an input.
    return narrow+(1-narrow)*transition(available,A4*.65,A4);
  }
  function margins(width,source,zoom=1){
    const t=transition(width,A4*.6,A4);
    const result=source.map((n,i)=>[24,GUTTER,30,GUTTER][i]+(n-[24,GUTTER,30,GUTTER][i])*t);
    // Give the reading column room first. Restore PDF side margins only as
    // the viewport can afford them, without narrowing the painted text column.
    const maxColumn=(A4-source[1]-source[3])*AUTO_MAX;
    const column=Math.min(Math.max(1,width*zoom-2*GUTTER),maxColumn);
    const spare=Math.max(0,width-column/zoom),total=source[1]+source[3];
    result[1]=spare*(total?source[1]/total:.5);
    result[3]=spare-result[1];
    return result;
  }
  function layout(preferences,available,source,openingTop=source[0]){
    const space=Math.max(1,available);
    let baseWidth=A4,zoom=1,baseMargins=[...source],trim=false;
    if(preferences.zoom==='auto'){
      baseWidth=Math.min(A4,space);
      zoom=clamp(space/A4,1,AUTO_MAX);
      baseMargins=margins(baseWidth,source,zoom);
    }else if(preferences.zoom==='fit')zoom=space/A4;
    else if(preferences.zoom!=='reference'){
      zoom=clamp(Number(preferences.zoom)/100||1,.01,10);
      const frozen=preferences.zoomWidth;
      if(typeof frozen==='number'&&Number.isFinite(frozen)){
        trim=true;
        baseWidth=clamp(frozen,1,A4);
        baseMargins=baseWidth<A4?margins(baseWidth,source):[...source];
        const saved=preferences.zoomMargins;
        if(Array.isArray(saved)&&saved.length===4&&saved.every(n=>typeof n==='number'&&Number.isFinite(n)&&n>=0)&&saved[1]+saved[3]<baseWidth)baseMargins=[...saved];
      }
    }
    // CSS supplies the current section-sized opening inset after Text size
    // and block spacing resolve. Old detached snapshots must not freeze it.
    baseMargins[0]=openingTop;
    const padding=[...baseMargins];
    let width=baseWidth;
    if(trim){
      // Trim blank sides and the paper width by the same amount. The content
      // column and its line breaks stay unchanged while magnification grows.
      const left=Math.max(0,padding[3]-GUTTER/zoom),right=Math.max(0,padding[1]-GUTTER/zoom);
      const capacity=left+right,cut=Math.min(Math.max(0,baseWidth-space/zoom),capacity);
      if(capacity){padding[3]-=cut*left/capacity;padding[1]-=cut*right/capacity;width-=cut;}
    }
    const responsive=baseWidth<A4-.01||Math.abs(baseMargins[1]-source[1])>.01||Math.abs(baseMargins[3]-source[3])>.01;
    return {width,baseWidth,zoom,margins:padding,baseMargins,responsive};
  }
  globalThis.AstraReaderSizing=Object.freeze({A4,AUTO_MAX,GUTTER,autoText,layout,margins});
})();

/* Origin-wide preferences; paper records retain their stable unit keys. */
globalThis.AstraBrowserMemory = class {
  constructor(getStorage, prefix) {
    this.getStorage=getStorage;this.prefix=prefix;this.available=true;
  }
  read(key) {
    let raw;
    try {raw=this.getStorage().getItem(this.prefix+key);}
    catch (_) {this.available=false;return null;}
    try {return JSON.parse(raw);} catch (_) {return null;}
  }
  write(key, value) {
    try {this.getStorage().setItem(this.prefix+key,JSON.stringify(value));return true;}
    catch (_) {this.available=false;return false;}
  }
  preferences() {
    const saved=this.read('preferences');
    return {remember:saved?.remember!==false,
      values:saved?.remember===true&&saved.values&&typeof saved.values==='object'&&!Array.isArray(saved.values)?saved.values:{},
      epoch:Number.isSafeInteger(saved?.epoch)?saved.epoch:0};
  }
  savePreferences(values, previous=null, enable=false) {
    const latest=this.preferences();
    // Check the current flag at write time, even before another tab's event arrives.
    if(!enable&&!latest.remember)return null;
    const merged=previous?{...latest.values}:{...values};
    if(previous)for(const key of new Set([...Object.keys(previous),...Object.keys(values)])) {
      if(JSON.stringify(previous[key])===JSON.stringify(values[key]))continue;
      if(Object.hasOwn(values,key))merged[key]=values[key];else delete merged[key];
    }
    const record={remember:true,values:merged,epoch:latest.epoch};
    return this.write('preferences',record)?record:null;
  }
  savePaper(key, value, epoch) {
    const current=this.preferences();
    return current.remember&&current.epoch===epoch&&this.write(key,value);
  }
  forget() {
    const epoch=this.preferences().epoch+1;
    // Publish opt-out before clearing records so open tabs cannot recreate them.
    this.write('preferences',{remember:false,epoch});
    try {
      const store=this.getStorage();
      for(let i=store.length-1;i>=0;i--) {
        const key=store.key(i);
        if(key?.startsWith(this.prefix)&&key!==this.prefix+'preferences')store.removeItem(key);
      }
    } catch (_) {this.available=false;}
  }
};

/* Local progressive enhancement. No network, account, or model dependency. */
(() => {
  'use strict';
  document.documentElement.classList.add('js');
  const $ = (s, root=document) => root.querySelector(s);
  const $$ = (s, root=document) => [...root.querySelectorAll(s)];
  const data = JSON.parse($('#page-data').textContent);
  const themeData = globalThis.AstraThemes;
  const themes = [...themeData.originals, ...themeData.monkeytype];
  const prefix = 'astraJLPT:web:v1:';
  const colorMath=AstraThemeColors, sizingPolicy=AstraReaderSizing, colorRoles=themeData.colorRoles, fillControls=themeData.fillControls;
  const editableColors=colorRoles.filter(r=>r.editable).map(role=>{
    const row=$('[data-color-row="'+role.id+'"]');
    return {role,row,field:$('[data-color-hex]',row),swatch:$('[data-color-swatch]',row),alpha:$('[data-color-alpha]',row),reset:$('[data-color-reset]',row)};
  });
  let effectiveColors={};
  const spacingPresets={original:{line:100,block:100},standard:{line:90,block:75},compact:{line:80,block:50}};
  const defaults = {theme:'astraJLPT_dark', spacing:'standard', marking:'cell', star:true, border:false, text:'auto', textSource:'auto', zoom:'auto', line:90, block:75, spacingVersion:2};
  const storage = new AstraBrowserMemory(()=>localStorage,prefix);
  function normalizePreferences(values={}) {
    const next={...defaults,...values};
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
  function status() {
    const s=$('#save-status'); if(s) s.textContent=!storage.available?'Browser storage is unavailable. You can still read and answer.':remember?'Saved on this browser. Preferences are shared across pages; answers and position belong to each paper.':'Saving is off. This visit stays in memory.';
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
  function syncPreferences() {
    const record=storage.preferences(),serialized=JSON.stringify(record);
    if(!storage.available){status();return;}
    if(serialized===observedPreferences)return;
    observedPreferences=serialized;remember=record.remember;
    if(remember){
      preferences=normalizePreferences(record.values);
      previousPreferences=JSON.parse(JSON.stringify(preferences));apply();
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
  function startSettingsVisit(){settingsGeneration++;readingAnchor=captureReading();}
  settings.querySelector('summary').addEventListener('pointerdown',()=>{if(!settings.open)startSettingsVisit();});
  settings.querySelector('summary').addEventListener('keydown',e=>{if(!settings.open&&(e.key==='Enter'||e.key===' '))startSettingsVisit();});
  settings.addEventListener('toggle',()=>{
    if(settings.open){if(!readingAnchor)startSettingsVisit();sizing();return;}
    const anchor=readingAnchor,generation=settingsGeneration;readingAnchor=null;
    requestAnimationFrame(()=>requestAnimationFrame(()=>{if(!settings.open&&generation===settingsGeneration&&anchor?.node.isConnected)window.scrollBy(0,anchor.node.getBoundingClientRect().top-anchor.top);}));
  });
  const closeSettings=()=>{settings.open=false;settings.querySelector('summary').focus({preventScroll:true});};
  $('#close-settings')?.addEventListener('click',closeSettings);
  document.addEventListener('click',e=>{if(settings.open&&!settings.contains(e.target))settings.open=false;});
  document.addEventListener('keydown',e=>{
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
  let unlockCount=0;
  $('#developer-unlock')?.addEventListener('click',()=>{unlockCount++;if(unlockCount===7){unlockCount=0;setDev(!document.body.classList.contains('developer'));$('#developer-hint').textContent='Developer switch toggled.';}else if(unlockCount>=3)$('#developer-hint').textContent=(7-unlockCount)+' more taps for developer tools.';});
  $('#boar')?.addEventListener('click',()=>{setDev(!document.body.classList.contains('developer'));const target=$('#historical');if(target&&!target.hidden)target.scrollIntoView({behavior:'instant',block:'nearest'});});
  // Suggestions vary, selected theme does not. Never shuffle paper or option order.
  const quick=$('#quick-picks');
  if(quick){const pool=[...themeData.monkeytype];for(let n=0;n<3;n++){const a=new Uint32Array(1);crypto.getRandomValues(a);const index=a[0]%pool.length,t=pool.splice(index,1)[0];const button=document.createElement('button');button.type='button';button.className='theme-card';button.textContent=t.name;button.dataset.theme=t.id;button.style.setProperty('--preview-bg',t.colors.bg);button.style.setProperty('--preview-text',t.colors.main);button.addEventListener('click',()=>{select('theme',t.id);preferences.theme=t.id;brightness();persist();});quick.append(button);}}
  $('#theme-search')?.addEventListener('input',e=>{const term=e.target.value.trim().toLowerCase();for(const card of $$('.theme-catalog .theme-card'))card.hidden=!card.textContent.toLowerCase().includes(term);});
  function filterReview(){const kind=$('#review-filter')?.value||'all',term=($('#review-search')?.value||'').trim().toLowerCase();const groups=$$('.review-group');let shown=0;for(const group of groups){group.hidden=!(kind==='all'||group.dataset.kinds.split(' ').includes(kind))||!group.textContent.toLowerCase().includes(term);if(!group.hidden)shown++;}if($('#review-count'))$('#review-count').textContent=shown+' / '+groups.length+' item groups';}
  $('#review-filter')?.addEventListener('change',filterReview);$('#review-search')?.addEventListener('input',filterReview);filterReview();
  const paper=$('.paper'), stage=$('.paper-stage');
  let paperZoom=1, sizingFrame=0, paperFrame, currentLayout;
  if(paper){
    paperFrame=document.createElement('div');paperFrame.className='paper-frame';
    paper.before(paperFrame);paperFrame.append(paper);
  }
  function sizePaperFrame(){
    // A transform scales text and hitboxes together without CSS zoom's
    // browser-dependent font sizing. Reserve exactly the painted page size.
    const rect=paper.getBoundingClientRect();
    paperFrame.style.width=rect.width+'px';paperFrame.style.height=rect.height+'px';
  }
  function fitTables(){
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
  function fitOptions(){
    if(!paper)return;
    const px=value=>parseFloat(value)||0;
    const rows=$$('.question').filter(q=>!q.hasAttribute('data-image-panels')).map(q=>({q,grid:$('.options-grid',q),wanted:Number(q.dataset.nativeCols)||1,samples:[]}));
    // Batch DOM writes before measurements; do not force layout per answer.
    for(const row of rows)for(const el of $$('.option-text',row.q)){
      const clone=el.cloneNode(true);clone.style.cssText='position:absolute;visibility:hidden;white-space:nowrap;width:max-content;max-width:none';
      clone.setAttribute('aria-hidden','true');el.parentNode.append(clone);row.samples.push({el,clone});
    }
    for(const row of rows){
      row.width=row.grid.getBoundingClientRect().width/paperZoom;
      row.gap=px(getComputedStyle(row.grid).columnGap);
      row.requirements=row.samples.map(({el,clone})=>{
        const cell=getComputedStyle(el.parentElement),text=getComputedStyle(el);
        const tracks=cell.gridTemplateColumns.split(/\s+/).map(px);
        // The middle track holds the answer. Account for the real number and
        // feedback tracks, gaps, text margins and cell edges at every text size.
        const fixed=tracks[0]+tracks[2]+2*px(cell.columnGap)
          +['paddingLeft','paddingRight','borderLeftWidth','borderRightWidth','marginLeft','marginRight'].reduce((sum,key)=>sum+px(cell[key]),0)
          +px(text.marginLeft)+px(text.marginRight);
        return clone.getBoundingClientRect().width/paperZoom+fixed;
      });
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
    for(const row of examples)for(const el of [...row.grid.children]){
      const clone=el.cloneNode(true);clone.style.cssText='position:absolute;visibility:hidden;white-space:nowrap;width:max-content;max-width:none';
      clone.setAttribute('aria-hidden','true');row.grid.append(clone);row.samples.push(clone);
    }
    for(const row of examples){
      row.width=row.grid.getBoundingClientRect().width/paperZoom;
      row.required=Math.max(...row.samples.map(el=>el.getBoundingClientRect().width/paperZoom));
    }
    for(const row of examples){
      row.samples.forEach(el=>el.remove());let cols=row.wanted;
      while(cols>1&&Math.floor(row.width/cols*64)/64<row.required)cols=cols===4?2:1;
      row.grid.style.setProperty('--example-columns',String(cols));
    }
  }
  function fitHeadings(){
    if(!paper)return;
    const zoom=paperZoom;
    for(const heading of $$('.section-heading')){
      const label=$('.heading-label',heading);if(!label)continue;
      const cs=getComputedStyle(heading),ls=getComputedStyle(label);
      const em=parseFloat(cs.fontSize)/(parseFloat(cs.getPropertyValue('--glyph-scale'))||1);
      const horizontal=parseFloat(cs.getPropertyValue('--heading-horizontal-scale'))||1;
      const visual=$('.heading-label-visual',label);
      if(visual)label.style.setProperty('--heading-label-width',visual.getBoundingClientRect().width/zoom/horizontal+'px');
      const pullback=parseFloat(cs.getPropertyValue('--heading-continuation-pullback-em'));
      heading.style.setProperty('--heading-hang',Math.max(0,label.getBoundingClientRect().width/zoom/horizontal+parseFloat(ls.marginRight)-em*(Number.isFinite(pullback)?pullback:1))+'px');
    }
  }
  function fitAnnotations(){
    const terms=$$('.annotated-term').filter(term=>!term.closest('.vertical-frame'));
    const probes=[];
    for(const term of terms){
      const base=$(':scope>.annotation-base',term),initial=$('.annotation-initial',base);
      if(initial){
        const label=$('.annotation-label',initial),first=$('.annotation-initial-base',initial);
        while(first.firstChild)initial.before(first.firstChild);
        term.append(label);initial.remove();
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
      if(ruby&&base.contains(ruby))range.setEndAfter(ruby);
      else range.setEnd(first,[...first.data][0].length);
      const anchor=document.createElement('span'),content=document.createElement('span');
      anchor.className='annotation-initial';content.className='annotation-initial-base';
      content.append(range.extractContents());anchor.append(content,$(':scope>.annotation-label',term));base.prepend(anchor);
      term.classList.add('annotation-breakable');
    }
  }
  function sizing(){
    if(!paper)return;
    const width=sizingPolicy.A4,available=Math.max(1,stage.clientWidth-parseFloat(getComputedStyle(stage).paddingLeft)-parseFloat(getComputedStyle(stage).paddingRight));
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
    paper.style.width=layout+'px';paper.style.maxWidth='none';paper.style.transform=zoom===1?'none':'scale('+zoom+')';
    const margins=currentLayout.margins;
    ['Right','Bottom','Left'].forEach((side,i)=>{paper.style['padding'+side]=margins[i+1]+'px';});
    paper.style.setProperty('--reader-left',margins[3]+'px');paper.style.setProperty('--reader-right',margins[1]+'px');
    $('#text-output').textContent=preferences.text==='auto'?'auto · '+Math.round(scale*100)+'%':preferences.text+'%';
    if(preferences.text==='auto')$('#text-size').value=Math.round(scale*100);
    const percent=Math.round(zoom*100),zoomControl=$('#paper-zoom');
    // Fit width is a shortcut, not a lower bound on manual magnification.
    zoomControl.min=Math.max(1,Math.min(25,Math.floor(available/width*100),percent));
    zoomControl.max=Math.max(500,Math.ceil(available/width*100),percent);
    zoomControl.value=percent;
    const mode=responsive?'screen':'A4';
    $('#zoom-output').textContent=(preferences.zoom==='auto'?'auto · ':preferences.zoom==='fit'?'fit · ':'')+mode+' · '+percent+'%';
    zoomControl.setAttribute('aria-valuetext',(preferences.zoom==='auto'?'Auto, ':'')+percent+'% of '+(responsive?'screen layout':'A4')+(preferences.zoom==='fit'?', fit to screen width':''));
    for(const button of $$('[data-zoom]'))button.setAttribute('aria-pressed',String(button.dataset.zoom===preferences.zoom||(button.dataset.zoom==='reference'&&!responsive&&Math.abs(layout-width)<.01&&Number(preferences.zoom)===100)));
    $('#auto-text').setAttribute('aria-pressed',String(preferences.text==='auto'));
    $('#source-text').setAttribute('aria-pressed',String(Number(preferences.text)===100));
    $('#line-adjust').value=preferences.line;$('#block-adjust').value=preferences.block;
    $('#line-output').textContent=preferences.line+'%';$('#block-output').textContent=preferences.block+'%';
    cancelAnimationFrame(sizingFrame);
    sizingFrame=requestAnimationFrame(()=>{fitHeadings();fitTables();fitOptions();fitAnnotations();sizePaperFrame();});
  }
  function apply(){for(const name of ['theme','spacing','marking'])select(name,preferences[name]);select('text-source',preferences.textSource||'auto');select('star-behavior',preferences.star?'show':'hide');for(const i of $$('[name=spacing]'))i.checked=i.value===preferences.spacing;brightness();if($('#visible-paper'))$('#visible-paper').checked=preferences.border;$('#remember').checked=remember;for(const [id,key]of[['line-adjust','line'],['block-adjust','block']])if($('#'+id))$('#'+id).value=preferences[key];if($('#text-size'))$('#text-size').value=preferences.text==='auto'?100:preferences.text;if($('#paper-zoom'))$('#paper-zoom').value=isNaN(Number(preferences.zoom))?100:preferences.zoom;sizing();status();}
  for(const name of ['theme','spacing','marking'])for(const input of $$('input[name="'+name+'"]'))input.addEventListener('change',()=>{preferences[name]=input.value;if(name==='spacing')Object.assign(preferences,spacingPresets[input.value]);brightness();persist();if(name==='spacing')sizing();});
  for(const i of $$('input[name="text-source"]'))i.addEventListener('change',()=>{preferences.textSource=i.value;brightness();persist();});
  for(const i of $$('[name=star-behavior]'))i.addEventListener('change',()=>{preferences.star=i.value==='show';persist();});
  $('#visible-paper')?.addEventListener('change',e=>{preferences.border=e.target.checked;persist();});
  for(const [id,key]of[['text-size','text'],['paper-zoom','zoom'],['line-adjust','line'],['block-adjust','block']])$('#'+id)?.addEventListener('input',e=>{
    // Detach Auto from the layout already on screen. Never make the first
    // slider movement replace a narrow page with a full A4 sheet.
    if(key==='zoom'&&preferences.zoom==='auto'){
      preferences.zoomWidth=currentLayout.baseWidth;
      preferences.zoomMargins=[...currentLayout.baseMargins];
    }
    preferences[key]=Number(e.target.value);
    if(key==='line'||key==='block'){preferences.spacing=Object.keys(spacingPresets).find(k=>spacingPresets[k].line===preferences.line&&spacingPresets[k].block===preferences.block)||'custom';for(const i of $$('[name=spacing]'))i.checked=i.value===preferences.spacing;}
    sizing();persist();
  });
  $('#auto-text')?.addEventListener('click',()=>{preferences.text='auto';apply();persist();});
  $('#source-text')?.addEventListener('click',()=>{preferences.text=100;apply();persist();});
  for(const b of $$('[data-zoom]'))b.addEventListener('click',()=>{preferences.zoom=b.dataset.zoom;delete preferences.zoomWidth;delete preferences.zoomMargins;apply();persist();});
  let position=0;
  const sessionKey=data.paper?'paper:'+(data.paper.storage_unit||data.paper.unit)+(data.paper.variant==='norubi'?':norubi':''):null;
  const gradableQuestions=(data.questions||[]).filter(q=>Number.isInteger(q.key)&&q.key>=1&&q.key<=4);
  const bindings=Object.fromEntries(gradableQuestions.map(q=>[q.id,q.binding]));
  function saveAnswers(edited=false){
    if(!remember||!sessionKey||restoring)return;
    if(edited)sessionEpoch=storage.preferences().epoch;
    storage.savePaper(sessionKey,{answers,position,bindings},sessionEpoch);status();
  }
  function progress(){if(!data.paper)return;const rows=Object.values(answers);const complete=rows.filter(a=>a.completed).length,attempts=rows.length,first=rows.filter(a=>a.firstCorrect).length;const count=complete+' / '+gradableQuestions.length,detail=attempts?'First try '+first+'/'+attempts:'';$('#progress-count').textContent=count;$('#progress-detail').textContent=detail;const label=count+' completed'+(detail?' · '+detail:'');$('#progress').setAttribute('aria-label',label);$('#progress').title=label;}
  for(const input of $$('.answer-radio'))input.addEventListener('change',()=>{
    if(input.disabled)return;
    const q=input.closest('.question'),id=q.id,correct=input.dataset.correct==='true';
    const previous=answers[id];answers[id]={selected:Number(input.value),firstCorrect:previous?previous.firstCorrect:correct,completed:Boolean(previous?.completed||correct),attempts:(previous?.attempts||0)+1};
    $('.answer-announcement',q).textContent=correct?'Correct.':'Incorrect. Try again.';
    progress();saveAnswers(true);
  });
  if(remember&&sessionKey){const session=storage.read(sessionKey);if(session){for(const [id,a]of Object.entries(session.answers||{})){if(!bindings[id]||session.bindings?.[id]!==bindings[id])continue;const input=$('#'+id+'-'+a.selected);if(input&&!input.disabled){answers[id]=a;input.checked=true;}}position=Number.isFinite(Number(session.position))?Math.max(0,Number(session.position)):0;if(position&&!location.hash){restoring=true;const resume=position;document.fonts.ready.then(()=>requestAnimationFrame(()=>requestAnimationFrame(()=>{window.scrollTo(0,resume);position=window.scrollY;restoring=false;})));}}}
  let saveTimer;
  window.addEventListener('scroll',()=>{if(restoring)return;position=window.scrollY;clearTimeout(saveTimer);saveTimer=setTimeout(saveAnswers,250);},{passive:true});
  window.addEventListener('pagehide',()=>saveAnswers());
  window.addEventListener('storage',e=>{if(e.key===null||e.key===prefix+'preferences')syncPreferences();});
  window.addEventListener('focus',syncPreferences);
  document.addEventListener('visibilitychange',()=>{if(!document.hidden)syncPreferences();});
  function forget(){remember=false;storage.forget();observedPreferences=JSON.stringify(storage.preferences());$('#remember').checked=false;status();}
  $('#remember').addEventListener('change',e=>{if(e.target.checked){remember=true;persist(true);saveAnswers(true);status();}else forget();});
  $('#forget').addEventListener('click',()=>{forget();toast('Saved data removed. Current answers remain until you leave.');});
  $('#reset-preferences').addEventListener('click',()=>{preferences=normalizePreferences();previousPreferences=null;apply();persist();});
  $('#clear-answers')?.addEventListener('click',()=>{if(!Object.keys(answers).length)return;if(!confirm('Clear this paper’s answers and practice counts?'))return;answers={};for(const i of $$('.answer-radio'))i.checked=false;for(const i of $$('.margin-answer,.answer-announcement'))i.textContent='';progress();saveAnswers();});
  apply();progress();persist();
  if(paper){
    document.fonts.ready.then(sizing);
    new ResizeObserver(sizePaperFrame).observe(paper);
    let frame;window.addEventListener('resize',()=>{cancelAnimationFrame(frame);frame=requestAnimationFrame(sizing);});
  }
})();
