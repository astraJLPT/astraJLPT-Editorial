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

/* Deterministic practice rules, shared with the regression checks. */
globalThis.AstraPractice = (() => {
  'use strict';
  const finite = (v, fallback=0) => typeof v==='number'&&Number.isFinite(v)&&v>=0?v:fallback;
  const direction = value => value==='up'?'up':'down';
  // A shared stopped clock pauses even papers which are not currently open.
  function clock(preferences, now=Date.now()) {
    return now-finite(preferences.timerDisabledTotal)-(preferences.timerEnabled===false?
      Math.max(0,now-finite(preferences.timerDisabledAt,now)):0);
  }
  function setEnabled(preferences, enabled, now=Date.now()) {
    if(enabled===(preferences.timerEnabled!==false))return;
    if(enabled){
      preferences.timerDisabledTotal=finite(preferences.timerDisabledTotal)+Math.max(0,now-finite(preferences.timerDisabledAt,now));
      preferences.timerDisabledAt=null;
    }else preferences.timerDisabledAt=now;
    preferences.timerEnabled=enabled;
  }
  class Timer {
    constructor(saved, limitSeconds, now, mode='down') {
      const valid=saved?.version===1;
      this.state={version:1,limit:finite(valid?saved.limit:null,limitSeconds*1000),
        elapsed:finite(valid?saved.elapsed:null),startedAt:finite(valid?saved.startedAt:null,now),
        running:valid?saved.running===true:true,direction:valid?direction(saved.direction):direction(mode),
        expired:valid&&saved.expired===true,notified:valid&&saved.notified===true,
        revision:finite(valid?saved.revision:null)};
      this.tick(now,mode);
    }
    tick(now, mode=this.state.direction) {
      const s=this.state;
      if(s.running){
        s.elapsed+=Math.max(0,now-s.startedAt);
        if(s.direction==='down'&&s.elapsed>=s.limit){s.elapsed=s.limit;s.running=false;s.expired=true;}
      }
      s.startedAt=now;s.direction=direction(mode);
      if(s.direction==='down'&&s.elapsed>=s.limit){s.running=false;s.expired=true;}
      return this.seconds();
    }
    seconds() {
      const s=this.state;
      return s.direction==='up'?Math.floor(s.elapsed/1000):Math.max(0,Math.ceil((s.limit-s.elapsed)/1000));
    }
    pause(now){this.tick(now);this.state.running=false;}
    resume(now){this.tick(now);if(this.state.direction==='up'||this.state.elapsed<this.state.limit)this.state.running=true;}
    reset(now){const s=this.state;s.elapsed=0;s.startedAt=now;s.expired=false;s.notified=false;}
    setLimit(seconds, now){this.tick(now);const s=this.state;s.limit=seconds*1000;s.expired=false;s.notified=false;this.tick(now);}
    setCurrent(seconds, now){
      this.tick(now);const s=this.state;
      if(s.direction==='down'){s.limit=Math.max(s.limit,seconds*1000);s.elapsed=s.limit-seconds*1000;}
      else s.elapsed=seconds*1000;
      s.startedAt=now;s.expired=false;s.notified=false;this.tick(now);
    }
  }
  function format(seconds) {
    seconds=Math.max(0,Math.floor(seconds));
    return Math.floor(seconds/3600)+':'+String(Math.floor(seconds/60)%60).padStart(2,'0')+':'+String(seconds%60).padStart(2,'0');
  }
  function parse(value) {
    const match=/^(\d{1,6}):([0-5]\d):([0-5]\d)$/.exec(value.trim());
    return match?Number(match[1])*3600+Number(match[2])*60+Number(match[3]):null;
  }
  const option=value=>Number.isInteger(value)&&value>=1&&value<=4;
  const gradable=q=>option(q.key);
  function restoreAnswer(saved) {
    const next={selected:saved.selected};
    if(typeof saved.firstCorrect==='boolean')next.firstCorrect=saved.firstCorrect;
    return next;
  }
  function firstFeedback(record, key) {
    if(!record||typeof record.firstCorrect==='boolean'||!option(record.selected)||!option(key))return false;
    record.firstCorrect=record.selected===key;
    return true;
  }
  function answer(previous, selected, key, feedbackVisible) {
    const next=previous?restoreAnswer(previous):{};
    next.selected=selected;
    if(feedbackVisible)firstFeedback(next,key);
    return next;
  }
  function recordFirstFeedback(questions, answers) {
    let changed=false;
    for(const q of questions)if(firstFeedback(answers[q.id],q.key))changed=true;
    return changed;
  }
  function progress(questions, answers) {
    const rows=questions.filter(gradable),selected=rows.filter(q=>option(answers[q.id]?.selected));
    const tracked=selected.map(q=>answers[q.id]).filter(a=>typeof a.firstCorrect==='boolean');
    return {total:rows.length,answered:selected.length,correct:selected.filter(q=>answers[q.id].selected===q.key).length,
      firstCorrect:tracked.filter(a=>a.firstCorrect).length,firstTotal:tracked.length};
  }
  function score(questions, answers, paper) {
    const old=paper.generation?.startsWith('historical');
    const combined=!old&&['N4','N5'].includes(paper.level);
    const definitions=old?[
      ['vocabulary','文字・語彙',100,q=>q.domain==='vocab'],
      ['reading_grammar','読解・文法',200,q=>q.domain!=='vocab']
    ]:combined?[
      ['written','語彙・文法・読解',120,()=>true]
    ]:[
      ['knowledge','語彙・文法',60,q=>q.domain!=='reading'],
      ['reading','読解',60,q=>q.domain==='reading']
    ];
    const sections=definitions.map(([id,label,maximum,belongs])=>{
      const all=questions.filter(belongs),rows=all.filter(gradable);
      const profile=paper.scoring?.sections?.[id];
      const weighted=Boolean(profile&&all.every(q=>finite(profile.weights[q.id])>0));
      const weight=q=>weighted?profile.weights[q.id]:1;
      const denominator=rows.reduce((n,q)=>n+weight(q),0);
      const correct=rows.filter(q=>answers[q.id]?.selected===q.key);
      const earned=correct.reduce((n,q)=>n+weight(q),0);
      return {id,label,maximum,total:rows.length,correct:correct.length,
        answered:rows.filter(q=>option(answers[q.id]?.selected)).length,
        excluded:all.length-rows.length,weighted,denominator,earned,
        exact:weighted&&all.length===rows.length&&!paper.partial&&denominator===profile.raw_maximum,
        score:denominator?Math.round(earned/denominator*maximum):null};
    });
    const available=sections.filter(s=>s.score!==null);
    return {sections,old,combined,total:available.reduce((n,s)=>n+s.score,0),
      maximum:available.reduce((n,s)=>n+s.maximum,0),expectedMaximum:sections.reduce((n,s)=>n+s.maximum,0),
      correct:available.reduce((n,s)=>n+s.correct,0),answered:available.reduce((n,s)=>n+s.answered,0),
      questions:available.reduce((n,s)=>n+s.total,0),excluded:sections.reduce((n,s)=>n+s.excluded,0),
      exact:available.length===sections.length&&available.every(s=>s.exact)};
  }
  function compare(a,b,mode) {
    if(mode==='newest'||mode==='oldest'){
      const order=(Number(a.year)-Number(b.year))||(Number(a.month||0)-Number(b.month||0));
      if(order)return mode==='newest'?-order:order;
    }
    return Number(a.rank)-Number(b.rank);
  }
  return {Timer,clock,setEnabled,format,parse,answer,restoreAnswer,recordFirstFeedback,progress,score,gradable,compare};
})();

/* Practice controls use the same browser-memory contract as the reader. */
globalThis.AstraPracticeUI = function(context) {
  'use strict';
  const {$,$$,data,storage,prefix,prefs,persist,progress,remember,epoch,editEpoch}=context;
  const model=AstraPractice, paper=data.paper;
  let revealed=false,lastAuto=prefs().autoGrade;
  const feedbackVisible=()=>prefs().autoGrade||revealed;
  const banner=$('.reader-subbar');
  if(banner){
    const start=$('.reader-start',banner),nav=$('.section-nav',banner),actions=$('.reader-actions',banner);
    let frame;
    const fit=()=>{
      cancelAnimationFrame(frame);
      frame=requestAnimationFrame(()=>{
        // Keep the section links at the viewport center while the two sides
        // fit equally. Then compress by measured content, including counters.
        for(const layout of ['wide','labels','compact','stacked','wrap']){
          banner.dataset.layout=layout;
          const style=getComputedStyle(banner),space=banner.clientWidth-parseFloat(style.paddingLeft)-parseFloat(style.paddingRight);
          const left=start.getBoundingClientRect().width,right=actions.getBoundingClientRect().width;
          const sides=layout==='wide'||layout==='labels'?2*Math.max(left,right):left+right;
          if(sides+nav.getBoundingClientRect().width+2*parseFloat(style.columnGap)<=space+.5)break;
        }
      });
    };
    const observer=new ResizeObserver(fit);
    for(const node of [banner,start,nav,actions])observer.observe(node);
    document.fonts.ready.then(fit);
  }
  function showDialog(id){
    const dialog=$(id);if(!dialog||dialog.open)return;
    $('#settings').open=false;
    dialog.showModal();
  }
  for(const button of $$('[data-dialog-close]'))button.addEventListener('click',()=>button.closest('dialog').close());
  function refreshScore(){
    if(!paper)return;
    const score=model.score(data.questions,context.answers(),paper);
    const target=$('#score-sections');target.replaceChildren();
    for(const section of score.sections){
      const row=document.createElement('tr');
      const values=[section.label,section.score===null?'Unavailable':section.score+' / '+section.maximum,
        section.score===null?'—':section.correct+' correct · '+(section.answered-section.correct)+' wrong · '+(section.total-section.answered)+' unanswered',
        section.score===null?'':section.exact?'Verified historical weights':section.weighted?'Adjusted practice estimate':score.old?'Historical-scale estimate':'Practice estimate'];
      values.forEach((value,i)=>{const cell=document.createElement(i===0?'th':'td');if(i===0)cell.scope='row';cell.textContent=value;row.append(cell);});target.append(row);
    }
    $('#score-total').textContent=score.questions?'Written subtotal: '+score.total+' / '+score.maximum:'Written subtotal: Unavailable';
    $('#score-explanation').textContent=score.old?
      'Historical scores use vocabulary /100 and reading + grammar /200. Verified sections use the original question weights, normalized to the section maximum and rounded to the nearest whole number. Other sections estimate correct answers ÷ scored questions × the section maximum.':
      'Practice estimate: correct answers ÷ scored questions × the section maximum, rounded to the nearest whole number. This is a simple estimate, not the official JLPT scaled score.';
    $('#score-coverage').textContent=[
      score.excluded?score.excluded+' question'+(score.excluded===1?' is':'s are')+' excluded because the answer key is unconfirmed.':'',
      paper.partial?'This paper is partial; available questions are scored as a practice estimate.':''
    ].filter(Boolean).join(' ');
    const source=$('#score-source');source.replaceChildren();
    if(paper.scoring?.source_path){const link=document.createElement('a');link.href='../'+paper.scoring.source_path;link.target='_blank';link.rel='noopener';link.textContent='Original point-allocation tables ↗';source.append(link);}
    return score;
  }
  function grading(){
    const auto=prefs().autoGrade;
    if(auto!==lastAuto){revealed=false;lastAuto=auto;$('#score-dialog')?.close();}
    if(paper&&feedbackVisible()&&model.recordFirstFeedback(data.questions,context.answers()))context.saveAnswers();
    document.body.dataset.gradesHidden=String(!feedbackVisible());
    for(const row of $$('[data-color-row=neutral]'))row.hidden=auto;
    for(const button of $$('[data-grade]')){button.hidden=auto;button.textContent=revealed?'Hide grade':'Grade now';button.setAttribute('aria-pressed',String(revealed));}
    for(const live of $$('.answer-announcement'))live.textContent='';
    progress();
  }
  for(const input of $$('[name=auto-grade]'))input.addEventListener('change',()=>{prefs().autoGrade=input.value==='show';grading();persist();});
  for(const button of $$('[data-grade]'))button.addEventListener('click',()=>{revealed=!revealed;grading();if(revealed){refreshScore();showDialog('#score-dialog');}});

  const timerKey=paper?'timer:'+(paper.storage_unit||paper.unit)+(paper.variant==='norubi'?':norubi':''):null;
  const timer=paper?new model.Timer(remember()?storage.read(timerKey):null,paper.timer.seconds,model.clock(prefs()),prefs().timerDirection):null;
  let clockState=timer?JSON.stringify(timer.state):'',timerRevision=timer?.state.revision||0;
  let timerWake=0,displayedTime='',displayedLabel='',displayedRunning;
  const timerDisplay=timer?$('#timer-display'):null,timerBanner=timer?$('#timer-banner'):null;
  const pauseControls=timer?$$('[data-timer-action=pause]').map(button=>({button,text:$('.timer-action-label',button),icon:$('.timer-action-icon',button)})):[];
  const timerFields=timer?[['timer-limit',$('#timer-limit')],['timer-current',$('#timer-current')]]:[];
  function saveTimer(edited=false){
    if(!timer||!remember())return;
    if(edited)editEpoch();
    // An older background tab must not overwrite a newer pause/reset/edit.
    const existing=storage.read(timerKey);
    if(existing?.revision>timerRevision&&!edited){adoptTimer(existing);return;}
    timer.state.revision=timerRevision=Math.max(Date.now(),timerRevision+1);
    storage.savePaper(timerKey,{...timer.state},epoch());
  }
  function adoptTimer(record){
    if(record?.version!==1||record.revision<=timerRevision)return;
    const next=new model.Timer(record,paper.timer.seconds,model.clock(prefs()),prefs().timerDirection);
    timer.state=next.state;timerRevision=record.revision;
  }
  function renderTimer(){
    clearTimeout(timerWake);timerWake=0;
    if(!timer)return;
    timer.tick(model.clock(prefs()),prefs().timerDirection);
    // Timestamps keep time while hidden. Only visible, changing values need
    // DOM work; a paused/disabled timer has no recurring wake-up at all.
    if(document.hidden||!prefs().timerEnabled)return;
    const value=model.format(timer.seconds());
    if(value!==displayedTime){timerDisplay.textContent=value;displayedTime=value;}
    const description=(prefs().timerDirection==='up'?'Elapsed time: ':'Time remaining: ')+value+(timer.state.running?'':' (paused)');
    if(description!==displayedLabel){timerDisplay.setAttribute('aria-label',description);displayedLabel=description;}
    if(timer.state.running!==displayedRunning){
      displayedRunning=timer.state.running;timerBanner.dataset.paused=String(!displayedRunning);
      for(const {button,text,icon} of pauseControls){
        const label=displayedRunning?'pause':'resume';
        button.setAttribute('aria-label',label+' timer');button.title=label+' timer';
        if(text){text.textContent=label;icon.textContent=displayedRunning?'Ⅱ':'▶';}else button.textContent=label;
      }
    }
    for(const [id,field] of timerFields){
      const next=id==='timer-limit'?model.format(timer.state.limit/1000):value;
      if(document.activeElement!==field&&!field.dataset.dirty&&field.value!==next)field.value=next;
    }
    if(timer.state.expired&&!timer.state.notified&&prefs().timerEnabled&&prefs().timerDirection==='down'&&!document.hidden){
      timer.state.notified=true;saveTimer();showDialog('#time-up-dialog');
    }
    if(timer.state.running){
      const remainder=(prefs().timerDirection==='up'?timer.state.elapsed:timer.state.limit-timer.state.elapsed)%1000;
      const delay=prefs().timerDirection==='up'?1000-remainder:remainder||1000;
      timerWake=setTimeout(renderTimer,Math.max(16,Math.ceil(delay)));
    }
  }
  function timerAction(action){
    if(!timer)return;
    adoptTimer(remember()?storage.read(timerKey):null);
    const now=model.clock(prefs());
    timer.tick(now,prefs().timerDirection);
    if(action==='pause')timer.state.running?timer.pause(now):timer.resume(now);
    if(action==='reset')timer.reset(now);
    if(action==='exam')timer.setLimit(paper.timer.seconds,now);
    for(const field of $$('#timer-settings input[type=text]'))delete field.dataset.dirty;
    saveTimer(true);renderTimer();
    $('#timer-edit-status').textContent=action==='exam'?'Exam time limit restored.':action==='reset'?'Timer reset.':'';
  }
  for(const button of $$('[data-timer-action]'))button.addEventListener('click',()=>timerAction(button.dataset.timerAction));
  for(const name of ['limit','current']){
    $('#timer-'+name)?.addEventListener('input',e=>{e.target.dataset.dirty='true';e.target.setCustomValidity('');});
    $('#timer-'+name+'-form')?.addEventListener('submit',e=>{
      e.preventDefault();const field=$('#timer-'+name),seconds=model.parse(field.value);
      if(seconds===null||name==='limit'&&seconds===0){field.setCustomValidity('Enter hours:minutes:seconds'+(name==='limit'?' with a time limit greater than zero.':'.'));field.reportValidity();return;}
      adoptTimer(remember()?storage.read(timerKey):null);
      timer[name==='limit'?'setLimit':'setCurrent'](seconds,model.clock(prefs()));
      delete field.dataset.dirty;saveTimer(true);renderTimer();$('#timer-edit-status').textContent=(name==='limit'?'Time limit':'Current time')+' updated.';
    });
  }
  for(const input of $$('[name=timer-enabled]'))input.addEventListener('change',()=>{
    model.setEnabled(prefs(),input.value==='yes');persist();apply();saveTimer(true);
  });
  for(const [name,key]of[['timer-controls','timerControls'],['timer-direction','timerDirection']])for(const input of $$('[name='+name+']'))input.addEventListener('change',()=>{
    if(timer)timer.tick(model.clock(prefs()),prefs().timerDirection);
    prefs()[key]=name==='timer-controls'?input.value==='show':input.value;
    persist();apply();saveTimer(true);
  });
  function sortCatalog(){
    const select=$('#catalog-sort');if(!select)return;
    select.value=prefs().catalogSort;
    const cards=$$('.paper-grid>.paper-card');cards.sort((a,b)=>model.compare(a.dataset,b.dataset,select.value));
    for(const card of cards)card.parentElement.append(card);
    const note=$('#catalog-order-note');note.textContent=select.value==='recommended'?'Ordered with higher quality papers presented first.':select.value==='newest'?'Ordered from newest to oldest.':'Ordered from oldest to newest.';
  }
  $('#catalog-sort')?.addEventListener('change',e=>{prefs().catalogSort=e.target.value;sortCatalog();persist();});
  function apply(){
    for(const [name,value]of[['auto-grade',prefs().autoGrade?'show':'hide'],['timer-enabled',prefs().timerEnabled?'yes':'no'],['timer-controls',prefs().timerControls?'show':'hide'],['timer-direction',prefs().timerDirection]]){
      const input=$$('[name='+name+']').find(n=>n.value===value);if(input)input.checked=true;
    }
    if($('#timer-settings'))$('#timer-settings').hidden=!prefs().timerEnabled;
    if(timer){
      $('#timer-banner').hidden=!prefs().timerEnabled;
      $('#timer-banner-controls').hidden=!prefs().timerControls;
      renderTimer();
    }
    grading();sortCatalog();
  }
  if(timer){
    window.addEventListener('storage',e=>{if(e.key===prefix+timerKey&&remember()){adoptTimer(storage.read(timerKey));renderTimer();}});
    window.addEventListener('pagehide',()=>{clearTimeout(timerWake);timer.tick(model.clock(prefs()),prefs().timerDirection);saveTimer();});
    const wakeTimer=()=>{if(remember())adoptTimer(storage.read(timerKey));renderTimer();};
    window.addEventListener('focus',wakeTimer);
    window.addEventListener('pageshow',wakeTimer);
    document.addEventListener('visibilitychange',()=>{if(document.hidden){clearTimeout(timerWake);timerWake=0;}else wakeTimer();});
    if(clockState!==JSON.stringify(timer.state)||!storage.read(timerKey))saveTimer();
  }
  return {apply,refreshScore,get revealed(){return revealed;},get feedbackVisible(){return feedbackVisible();},save:()=>saveTimer(true)};
};

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
  const progressRoot=$('#progress');
  if(progressRoot&&!$('.progress-correct',progressRoot)){
    const count=$('#progress-count',progressRoot),detail=$('#progress-detail',progressRoot);
    const correct=document.createElement('span');
    correct.className='progress-correct';correct.textContent='correct';
    progressRoot.replaceChildren(count,correct,detail);
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
  const defaults = {theme:'astraJLPT_dark', spacing:'standard', marking:'cell', star:true, border:false, text:'auto', textSource:'auto', zoom:'auto', line:90, block:75, spacingVersion:2,autoGrade:true,timerEnabled:true,timerControls:false,timerDirection:'down',timerDisabledTotal:0,timerDisabledAt:null,catalogSort:'recommended'};
  let practiceUI=null;
  const storage = new AstraBrowserMemory(()=>localStorage,prefix);
  function normalizePreferences(values={}) {
    const next={...defaults,...values};
    for(const key of ['autoGrade','timerEnabled','timerControls'])if(typeof next[key]!=='boolean')next[key]=defaults[key];
    if(!['down','up'].includes(next.timerDirection))next.timerDirection='down';
    if(!['recommended','newest','oldest'].includes(next.catalogSort))next.catalogSort='recommended';
    if(!Number.isFinite(next.timerDisabledTotal)||next.timerDisabledTotal<0)next.timerDisabledTotal=0;
    if(!next.timerEnabled&&(!Number.isFinite(next.timerDisabledAt)||next.timerDisabledAt<=0))next.timerDisabledAt=Date.now();
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
    setText($('#save-status'),!storage.available?'Browser storage is unavailable. You can still read and answer.':remember?'Saved on this browser. Preferences are shared across pages; answers and position belong to each paper.':'Saving is off. This visit stays in memory.');
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
    if(id)document.body.dataset.theme=id;
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
  $('#boar')?.addEventListener('click',()=>{setDev(!document.body.classList.contains('developer'));const target=$('#historical');if(target&&!target.hidden)target.scrollIntoView({behavior:'instant',block:'nearest'});});
  // Suggestions vary, selected theme does not. Never shuffle paper or option order.
  const quick=$('#quick-picks');
  if(quick){const pool=[...themeData.monkeytype];for(let n=0;n<3;n++){const a=new Uint32Array(1);crypto.getRandomValues(a);const index=a[0]%pool.length,t=pool.splice(index,1)[0];const button=document.createElement('button');button.type='button';button.className='theme-card';button.textContent=t.name;button.dataset.theme=t.id;button.style.setProperty('--preview-bg',t.colors.bg);button.style.setProperty('--preview-text',t.colors.main);button.addEventListener('click',()=>{select('theme',t.id);preferences.theme=t.id;brightness();persist();});quick.append(button);}}
  $('#theme-search')?.addEventListener('input',e=>{const term=e.target.value.trim().toLowerCase();for(const card of $$('.theme-catalog .theme-card'))card.hidden=!card.textContent.toLowerCase().includes(term);});
  function filterReview(){const kind=$('#review-filter')?.value||'all',term=($('#review-search')?.value||'').trim().toLowerCase();const groups=$$('.review-group');let shown=0;for(const group of groups){group.hidden=!(kind==='all'||group.dataset.kinds.split(' ').includes(kind))||!group.textContent.toLowerCase().includes(term);if(!group.hidden)shown++;}if($('#review-count'))$('#review-count').textContent=shown+' / '+groups.length+' item groups';}
  $('#review-filter')?.addEventListener('change',filterReview);$('#review-search')?.addEventListener('input',filterReview);filterReview();
  const paper=$('.paper'), stage=$('.paper-stage');
  const sizingContainers=paper?[$('.exam-section',paper),...$$('.cloze-frame',paper)].filter(Boolean):[];
  let paperZoom=1, sizingFrame=0, paperFrame, currentLayout,lastSizingKey='',fittedLayoutKey='',fontGeneration=0;
  const tableMetrics=new WeakMap(),optionMetrics=new WeakMap();
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
  function fitTables(metricsKey){
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
  function fitOptions(metricsKey){
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
      row.required??=Math.max(...row.samples.map(el=>el.getBoundingClientRect().width/paperZoom));
      optionMetrics.set(row.grid,{key:metricsKey,required:row.required});
    }
    for(const row of examples){
      row.samples.forEach(el=>el.remove());let cols=row.wanted;
      while(cols>1&&Math.floor(row.width/cols*64)/64<row.required)cols=cols===4?2:1;
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
  function applySizing(layoutOnly=false){
    cancelAnimationFrame(sizingFrame);sizingFrame=0;
    if(!paper)return;
    const width=sizingPolicy.A4,available=Math.max(1,stage.clientWidth-parseFloat(getComputedStyle(stage).paddingLeft)-parseFloat(getComputedStyle(stage).paddingRight));
    const mobile=window.innerWidth<=650;
    const key=JSON.stringify([available,mobile,preferences.text,preferences.zoom,preferences.zoomWidth,preferences.zoomMargins,preferences.line,preferences.block,fontGeneration]);
    if(key===lastSizingKey)return;
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
    const layoutKey=JSON.stringify([metricsKey,responsive,Math.round((layout-margins[1]-margins[3])*64),...sizingContainers.map(node=>getComputedStyle(node).width)]);
    if(layoutKey!==fittedLayoutKey){fitHeadings(metricsKey);fitTables(metricsKey);fitOptions(metricsKey);fitAnnotations();fittedLayoutKey=layoutKey;}
    sizePaperFrame();
  }
  function apply(){for(const name of ['theme','spacing','marking'])select(name,preferences[name]);select('text-source',preferences.textSource||'auto');select('star-behavior',preferences.star?'show':'hide');for(const i of $$('[name=spacing]'))i.checked=i.value===preferences.spacing;brightness();if($('#visible-paper'))$('#visible-paper').checked=preferences.border;$('#remember').checked=remember;for(const [id,key]of[['line-adjust','line'],['block-adjust','block']])if($('#'+id))$('#'+id).value=preferences[key];sizing();status();practiceUI?.apply();}
  for(const name of ['theme','spacing','marking'])for(const input of $$('input[name="'+name+'"]'))input.addEventListener('change',()=>{preferences[name]=input.value;if(name==='spacing')Object.assign(preferences,spacingPresets[input.value]);brightness();persist();if(name==='spacing')sizing();});
  for(const i of $$('input[name="text-source"]'))i.addEventListener('change',()=>{preferences.textSource=i.value;brightness();persist();});
  for(const i of $$('[name=star-behavior]'))i.addEventListener('change',()=>{preferences.star=i.value==='show';persist();});
  $('#visible-paper')?.addEventListener('change',e=>{preferences.border=e.target.checked;persist();});
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
    if(key==='line'||key==='block'){preferences.spacing=Object.keys(spacingPresets).find(k=>spacingPresets[k].line===preferences.line&&spacingPresets[k].block===preferences.block)||'custom';for(const i of $$('[name=spacing]'))i.checked=i.value===preferences.spacing;}
    sizing();persist();
  }
  for(const [id,key]of[['text-size','text'],['paper-zoom','zoom'],['line-adjust','line'],['block-adjust','block']])$('#'+id)?.addEventListener('input',e=>changeSizing(key,Number(e.target.value)));
  $('#auto-text')?.addEventListener('click',()=>{preferences.text='auto';apply();persist();});
  $('#source-text')?.addEventListener('click',()=>{preferences.text=100;apply();persist();});
  for(const b of $$('[data-zoom]'))b.addEventListener('click',()=>{preferences.zoom=b.dataset.zoom;delete preferences.zoomWidth;delete preferences.zoomMargins;apply();persist();});
  let position=0;
  const sessionKey=data.paper?'paper:'+(data.paper.storage_unit||data.paper.unit)+(data.paper.variant==='norubi'?':norubi':''):null;
  const gradableQuestions=(data.questions||[]).filter(q=>Number.isInteger(q.key)&&q.key>=1&&q.key<=4);
  const bindings=Object.fromEntries(gradableQuestions.map(q=>[q.id,q.binding]));
  function saveAnswers(edited=false){
    if(!remember||!sessionKey)return;
    if(edited)sessionEpoch=storage.preferences().epoch;
    const savedBindings=Object.fromEntries(Object.keys(answers).map(id=>[id,bindings[id]]));
    storage.savePaper(sessionKey,{answers,position,bindings:savedBindings},sessionEpoch);status();
  }
  function progress(){
    if(!data.paper)return;
    const counts=AstraPractice.progress(gradableQuestions,answers),visible=practiceUI?.feedbackVisible??preferences.autoGrade;
    const count=(visible?counts.correct:'?')+' / '+counts.total;
    const detail=preferences.autoGrade?(counts.firstTotal?'First try '+counts.firstCorrect+'/'+counts.firstTotal:''):'Answered '+counts.answered+'/'+counts.total;
    $('#progress-count').textContent=count;$('#progress-detail').textContent=detail;
    $('.progress-correct').hidden=!visible;
    const label=count+(visible?' correct':' grade hidden')+(detail?' · '+detail:'');
    $('#progress').setAttribute('aria-label',label);$('#progress').title=label;
    if($('#score-dialog')?.open)practiceUI?.refreshScore();
  }
  for(const input of $$('.answer-radio'))input.addEventListener('change',()=>{
    if(input.disabled)return;
    const q=input.closest('.question'),id=q.id,correct=input.dataset.correct==='true';
    const visible=practiceUI.feedbackVisible;
    answers[id]=AstraPractice.answer(answers[id],Number(input.value),data.questions.find(q=>q.id===id).key,visible);
    $('.answer-announcement',q).textContent=visible?(correct?'Correct.':'Incorrect. Try again.'):'Answer selected.';
    progress();saveAnswers(true);
  });
  if(remember&&sessionKey){const session=storage.read(sessionKey);if(session){for(const [id,a]of Object.entries(session.answers||{})){if(!bindings[id]||session.bindings?.[id]!==bindings[id]||!a||!Number.isInteger(a.selected))continue;const input=$('#'+id+'-'+a.selected);if(input&&!input.disabled){answers[id]=AstraPractice.restoreAnswer(a);input.checked=true;}}position=Number.isFinite(Number(session.position))?Math.max(0,Number(session.position)):0;if(position&&!location.hash){restoring=true;const resume=position;document.fonts.ready.then(()=>requestAnimationFrame(()=>requestAnimationFrame(()=>{window.scrollTo(0,resume);position=window.scrollY;restoring=false;})));}}}
  let scrollSaveTimer;
  window.addEventListener('scroll',()=>{if(restoring)return;position=window.scrollY;clearTimeout(scrollSaveTimer);scrollSaveTimer=setTimeout(saveAnswers,250);},{passive:true});
  window.addEventListener('pagehide',()=>saveAnswers());
  window.addEventListener('storage',e=>{if(e.key===null||e.key===prefix+'preferences')syncPreferences();});
  window.addEventListener('focus',syncPreferences);
  document.addEventListener('visibilitychange',()=>{if(!document.hidden)syncPreferences();});
  function forget(){remember=false;storage.forget();observedPreferences=JSON.stringify(storage.preferences());$('#remember').checked=false;status();}
  $('#remember').addEventListener('change',e=>{if(e.target.checked){remember=true;persist(true);saveAnswers(true);practiceUI?.save();status();}else forget();});
  $('#forget').addEventListener('click',()=>{forget();toast('Saved data removed. Current answers remain until you leave.');});
  $('#reset-preferences').addEventListener('click',()=>{AstraPractice.setEnabled(preferences,true);const disabledTotal=preferences.timerDisabledTotal;preferences=normalizePreferences({timerDisabledTotal:disabledTotal});previousPreferences=null;apply();persist();});
  $('#clear-answers')?.addEventListener('click',()=>{if(!Object.keys(answers).length)return;if(!confirm('Clear this paper’s answers and practice counts?'))return;answers={};for(const i of $$('.answer-radio'))i.checked=false;for(const i of $$('.margin-answer,.answer-announcement'))i.textContent='';progress();saveAnswers();});
  practiceUI=AstraPracticeUI({$,$$,data,storage,prefix,prefs:()=>preferences,persist,progress,saveAnswers,answers:()=>answers,remember:()=>remember,epoch:()=>sessionEpoch,editEpoch:()=>{sessionEpoch=storage.preferences().epoch;}});
  apply();progress();persist();
  if(paper){
    document.fonts.ready.then(()=>{fontGeneration++;sizing();});
    new ResizeObserver(sizePaperFrame).observe(paper);
    let frame;window.addEventListener('resize',()=>{cancelAnimationFrame(frame);frame=requestAnimationFrame(sizing);});
  }
})();
