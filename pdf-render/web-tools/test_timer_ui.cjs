/* Exercise timer scheduling, elapsed time and storage events without real waits. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
class Element {
  constructor(){this.listeners={};this.dataset={};this.open=false;this._text='';this.mutations=0;this.value='';}
  set textContent(value){this._text=value;this.mutations++;}
  get textContent(){return this._text;}
  addEventListener(name,fn){this.listeners[name]=fn;}
  setAttribute(name,value){this[name]=value;this.mutations++;}
  close(){this.open=false;}
  showModal(){this.open=true;this.opens=(this.opens||0)+1;}
  setCustomValidity(){}
  reportValidity(){}
}
function reader({running=true,enabled=true,seconds=600}={}){
  let now=10000,id=0;const tasks=new Map(),nodes=new Map(),events={},documentEvents={},records=new Map();
  const node=key=>{if(!nodes.has(key))nodes.set(key,new Element());return nodes.get(key);};
  const pause=node('pause');pause.dataset.timerAction='pause';
  const reset=node('reset');reset.dataset.timerAction='reset';
  const buttons=[pause,reset];
  const $=selector=>['.reader-subbar','#catalog-sort'].includes(selector)?null:node(selector);
  const $$=selector=>selector==='[data-timer-action=pause]'?[pause]:selector==='[data-timer-action]'?buttons:[];
  const preferences={autoGrade:true,timerEnabled:enabled,timerDirection:'down',timerControls:true,timerDisabledTotal:0,timerDisabledAt:enabled?null:now};
  records.set('timer:test',{version:1,limit:seconds*1000,elapsed:0,startedAt:now,running,direction:'down',expired:false,notified:false,revision:1});
  const document={body:node('body'),hidden:false,activeElement:null,addEventListener:(e,f)=>documentEvents[e]=f};
  const context={document,window:{addEventListener:(e,f)=>events[e]=f},Date:class extends Date{static now(){return now;}},
    setTimeout(fn,delay){const key=++id;tasks.set(key,{fn,at:now+delay});return key;},clearTimeout(key){tasks.delete(key);}};
  vm.createContext(context);
  for(const name of ['practice-model.js','practice-ui.js'])vm.runInContext(fs.readFileSync(path.join(__dirname,'../web-src',name),'utf8'),context);
  const ui=context.AstraPracticeUI({$,$$,data:{paper:{unit:'test',level:'N1',timer:{seconds}},questions:[]},
    storage:{read:key=>records.get(key),savePaper(key,value){records.set(key,JSON.parse(JSON.stringify(value)));}},prefix:'test:',prefs:()=>preferences,
    persist(){},progress(){},remember:()=>true,epoch:()=>0,editEpoch(){},answers:()=>({}),saveAnswers(){}});
  ui.apply();
  return {ui,preferences,document,events,records,tasks,node,model:context.AstraPractice,
    now:()=>now,advance(ms){now+=ms;const due=[...tasks].filter(([,task])=>task.at<=now);for(const [key,task]of due){if(tasks.delete(key))task.fn();}},
    action(value){buttons.find(b=>b.dataset.timerAction===value).listeners.click();},
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
check('pause and disable eliminate recurring work while resume preserves elapsed time',()=>{
  const r=reader();r.advance(1200);r.action('pause');const paused=r.time();assert.equal(r.tasks.size,0);
  r.advance(30000);r.events.focus();assert.equal(r.time(),paused);assert.equal(r.tasks.size,0);
  r.action('pause');assert.equal(r.tasks.size,1);r.advance(1000);assert.equal(r.time(),'0:09:58');
  r.model.setEnabled(r.preferences,false);r.ui.apply();assert.equal(r.tasks.size,0);
  r.advance(20000);r.model.setEnabled(r.preferences,true);r.ui.apply();assert.equal(r.time(),'0:09:58');
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
  const next={...r.records.get('timer:test'),running:false,elapsed:8000,startedAt:r.now(),revision:999999};
  r.records.set('timer:test',next);r.events.storage({key:'test:timer:test'});
  assert.equal(r.time(),'0:09:52');assert.equal(r.tasks.size,0);
  r.advance(10000);r.events.pagehide();assert.equal(r.records.get('timer:test').elapsed,8000);
});
check('dirty editor fields survive ticks; submitting edits and reset still work',()=>{
  const r=reader(),field=r.node('#timer-current');field.value='0:00:05';field.listeners.input({target:field});
  r.advance(1000);assert.equal(field.value,'0:00:05');
  r.node('#timer-current-form').listeners.submit({preventDefault(){}});assert.equal(r.time(),'0:00:05');
  r.advance(1000);assert.equal(r.time(),'0:00:04');r.action('reset');assert.equal(r.time(),'0:10:00');
});
check('count-up uses elapsed seconds and initially paused or disabled timers stay idle',()=>{
  const r=reader();r.preferences.timerDirection='up';r.ui.apply();r.advance(2500);assert.equal(r.time(),'0:00:02');
  assert.equal(reader({running:false}).tasks.size,0);assert.equal(reader({enabled:false}).tasks.size,0);
});
console.log(JSON.stringify({status:'pass',checks}));
