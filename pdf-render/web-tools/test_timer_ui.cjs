/* Exercise timer scheduling, elapsed time and storage events without real waits. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
class Element {
  constructor(){this.listeners={};this.dataset={};this.open=false;this._text='';this.mutations=0;this.value='';}
  set textContent(value){this._text=value;this.mutations++;}
  get textContent(){return this._text;}
  addEventListener(name,fn){this.listeners[name]=fn;}
  closest(){return this;}
  insertAdjacentHTML(){}
  setAttribute(name,value){this[name]=value;this.mutations++;}
  close(){this.open=false;}
  showModal(){this.open=true;this.opens=(this.opens||0)+1;}
  setCustomValidity(){}
  reportValidity(){}
}
function reader({running=true,enabled=true,seconds=600,fresh=false}={}){
  let now=10000,id=0;const tasks=new Map(),nodes=new Map(),events={},documentEvents={},records=new Map();
  const node=key=>{if(!nodes.has(key))nodes.set(key,new Element());return nodes.get(key);};
  const pause=node('pause');pause.dataset.timerAction='pause';
  const reset=node('reset');reset.dataset.timerAction='reset';
  const buttons=[pause,reset];
  const $=selector=>['.reader-subbar','#catalog-sort'].includes(selector)?null:node(selector);
  const confirmations=['#timer-reset-dialog','#paper-action-dialog','#reset-preferences-dialog','#forget-dialog'].map(node);
  const $$=selector=>{
    if(selector==='dialog.practice-confirm')return confirmations;
    if(selector==='[data-timer-action=pause]')return [pause];
    return selector==='[data-timer-action]'?buttons:[];
  };
  const preferences={autoGrade:true,timerEnabled:enabled,timerDirection:'down',timerDisabledTotal:0,timerDisabledAt:enabled?null:now};
  if(!fresh)records.set('timer:test',{version:1,limit:seconds*1000,elapsed:0,startedAt:now,running,direction:'down',expired:false,notified:false,revision:1});
  const document={body:node('body'),hidden:false,activeElement:null,addEventListener:(e,f)=>documentEvents[e]=f};
  reset.focus=()=>{document.activeElement=reset;};
  const context={document,window:{addEventListener:(e,f)=>events[e]=f},Date:class extends Date{static now(){return now;}},
    setTimeout(fn,delay){const key=++id;tasks.set(key,{fn,at:now+delay});return key;},clearTimeout(key){tasks.delete(key);}};
  vm.createContext(context);
  for(const name of ['browser-memory.js','practice-model.js','practice-ui.js'])vm.runInContext(fs.readFileSync(path.join(__dirname,'../web-src',name),'utf8'),context);
  const ui=context.AstraPracticeUI({$,$$,data:{paper:{unit:'test',level:'N1',timer:{seconds}},questions:[]},
    storage:{openPractice:context.AstraBrowserMemory.prototype.openPractice,read:key=>records.get(key)??null,savePaper(key,value){records.set(key,JSON.parse(JSON.stringify(value)));}},prefix:'test:',prefs:()=>preferences,
    persist(){},progress(){},syncPaper(){},applyAutoSpoil(){},remember:()=>true,epoch:()=>0,answers:()=>({}),saveAnswers(){}});
  ui.apply();
  return {ui,preferences,document,events,records,tasks,node,model:context.AstraPractice,
    now:()=>now,advance(ms){now+=ms;const due=[...tasks].filter(([,task])=>task.at<=now);for(const [key,task]of due){if(tasks.delete(key))task.fn();}},
    action(value){buttons.find(b=>b.dataset.timerAction===value).listeners.click();},
    confirmReset(){node('#confirm-timer-reset').listeners.click();},
    visibility(hidden){document.hidden=hidden;documentEvents.visibilitychange();},
    time:()=>node('#timer-display').textContent};
}
let checks=0;
function check(name,fn){fn();checks++;console.log('PASS '+name);}
check('running timers update at displayed-second boundaries without rewriting pause controls',()=>{
  const r=reader(),pause=r.node('pause').mutations;
  assert.equal(r.time(),'0:10:00');assert.equal(r.tasks.size,1);
  r.advance(500);assert.equal(r.time(),'0:10:00');assert.equal(r.node('pause').mutations,pause);
  r.advance(500);assert.equal(r.time(),'0:09:59');assert.equal(r.node('pause').mutations,pause);
});
check('pause stops elapsed time; disabling hides the clock without scheduling work',()=>{
  const r=reader();r.advance(1200);r.action('pause');const paused=r.time();assert.equal(r.tasks.size,0);
  r.advance(30000);r.events.focus();assert.equal(r.time(),paused);assert.equal(r.tasks.size,0);
  r.action('pause');assert.equal(r.tasks.size,1);r.advance(1000);assert.equal(r.time(),'0:09:58');
  r.preferences.timerEnabled=false;r.ui.apply();assert.equal(r.tasks.size,0);
  r.advance(20000);r.preferences.timerEnabled=true;r.ui.apply();assert.equal(r.time(),'0:09:38');
});
check('completion freezes at the answer, permits edits, and preserves the manual pause choice',()=>{
  const r=reader();r.advance(7000);r.ui.setComplete(true);r.advance(25000);
  assert.equal(r.time(),'0:09:53');assert.equal(r.tasks.size,0);assert.equal(r.records.get('timer2:test').frozen,true);
  r.action('pause');assert.equal(r.node('#timer-frozen-dialog').opens,1);
  assert.equal(r.node('#timer-frozen-time').textContent,'0:00:07 / 0:10:00');
  r.node('#timer-frozen-dialog').close();
  r.action('reset');r.confirmReset();assert.equal(r.time(),'0:10:00');assert.equal(r.tasks.size,0);
  r.ui.setComplete(false);r.advance(1000);assert.equal(r.time(),'0:09:59');
  r.action('pause');r.ui.setComplete(true);r.ui.setComplete(false);r.advance(3000);
  assert.equal(r.time(),'0:09:59');assert.equal(r.tasks.size,0);
});
check('another current reader can reopen a completed paper without changing its manual pause choice',()=>{
  const r=reader({fresh:true});r.ui.setComplete(true);
  const frozen=r.records.get('timer2:test');
  assert.equal(frozen.version,2);assert.equal(frozen.frozen,true);assert.equal(frozen.running,true);
  const reopened=new r.model.Timer(frozen,600,r.now(),'down',true);
  r.records.set('timer2:test',{...reopened.state,revision:frozen.revision+1});
  r.events.storage({key:'test:timer2:test'});r.ui.setComplete(false);r.advance(1000);
  assert.equal(r.time(),'0:09:59');
});
check('hidden pages do no recurring work and catch up on return',()=>{
  const r=reader();r.visibility(true);const before=r.node('#timer-display').mutations;
  assert.equal(r.tasks.size,0);r.advance(61000);assert.equal(r.node('#timer-display').mutations,before);
  r.visibility(false);assert.equal(r.time(),'0:08:59');assert.equal(r.tasks.size,1);
});
check('expiry while hidden is announced once on return',()=>{
  const r=reader({seconds:2});r.visibility(true);r.advance(3000);
  assert.equal(r.node('#time-up-dialog').open,false);r.visibility(false);
  assert.equal(r.time(),'0:00:00');assert.equal(r.node('#time-up-dialog').opens,1);assert.equal(r.tasks.size,0);
  r.events.focus();r.events.pageshow();assert.equal(r.node('#time-up-dialog').opens,1);
});
check('cross-tab pause revisions are adopted and an old pagehide cannot overwrite them',()=>{
  const r=reader();r.advance(1000);
  const next={...r.records.get('timer:test'),version:2,frozen:false,running:false,elapsed:8000,startedAt:r.now(),revision:999999};
  r.records.set('timer2:test',next);r.events.storage({key:'test:timer2:test'});
  assert.equal(r.time(),'0:09:52');assert.equal(r.tasks.size,0);
  r.advance(10000);r.events.pagehide();assert.equal(r.records.get('timer2:test').elapsed,8000);
});
check('a stale legacy pause cannot reset a current frozen result',()=>{
  const r=reader();r.advance(9000);r.ui.setComplete(true);
  const frozen=r.records.get('timer2:test');assert.equal(frozen.version,2);
  assert.equal(frozen.frozen,true);assert.equal(frozen.elapsed,9000);
  r.records.set('timer:test',{...r.records.get('timer:test'),running:false,elapsed:0,revision:frozen.revision+1});
  r.events.storage({key:'test:timer:test'});r.events.focus();r.advance(4000);r.events.pagehide();
  assert.equal(r.records.get('timer2:test').elapsed,9000);r.ui.restoreTimer();
  assert.equal(r.time(),'0:09:51');
});
check('dirty editor fields survive ticks; submitting edits and reset still work',()=>{
  const r=reader(),field=r.node('#timer-current');field.value='0:00:05';field.listeners.input({target:field});
  r.advance(1000);assert.equal(field.value,'0:00:05');
  r.node('#timer-current-form').listeners.submit({preventDefault(){}});assert.equal(r.time(),'0:00:05');
  r.advance(1000);assert.equal(r.time(),'0:00:04');r.action('reset');r.confirmReset();assert.equal(r.time(),'0:10:00');
});
check('the confirmation keeps recording time and defers expiry until the reader resolves it',()=>{
  const r=reader({seconds:2});r.action('reset');r.advance(3000);
  assert.equal(r.node('#time-up-dialog').open,false);assert.equal(r.time(),'0:00:00');
  const dialog=r.node('#timer-reset-dialog');dialog.close();dialog.listeners.close();
  assert.equal(r.node('#time-up-dialog').opens,1);
  r.node('#time-up-dialog').close();r.action('reset');r.confirmReset();
  assert.equal(r.time(),'0:00:02');assert.equal(r.tasks.size,1);
});
check('count-up uses elapsed seconds and initially paused or disabled timers stay idle',()=>{
  const r=reader();r.preferences.timerDirection='up';r.ui.apply();r.advance(2500);assert.equal(r.time(),'0:00:02');
  assert.equal(reader({running:false}).tasks.size,0);assert.equal(reader({enabled:false}).tasks.size,0);
});
check('clear and spoil confirmations defer expiry and respect a completion freeze',()=>{
  for(const complete of [false,true]){
    const r=reader({seconds:2}),dialog=r.node('#paper-action-dialog');
    dialog.showModal();r.advance(3000);
    assert.equal(r.node('#time-up-dialog').open,false);
    if(complete)r.ui.setComplete(true);
    dialog.close();dialog.listeners.close();
    assert.equal(r.node('#time-up-dialog').open,!complete);
  }
});
check('timer expiry waits for either browser-settings confirmation',()=>{
  for(const id of ['#reset-preferences-dialog','#forget-dialog']){
    const r=reader({seconds:2}),dialog=r.node(id);
    dialog.showModal();r.advance(3000);
    assert.equal(r.node('#time-up-dialog').open,false);
    dialog.close();dialog.listeners.close();
    assert.equal(r.node('#time-up-dialog').opens,1);
  }
});
console.log(JSON.stringify({status:'pass',checks}));
