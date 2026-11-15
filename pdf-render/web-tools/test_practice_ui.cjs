/* Exercise real grading controls with browser I/O replaced by an in-memory DOM. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
require('../web-src/practice-model.js');
const P=AstraPractice,questions=[{id:'v',key:1,domain:'vocab'},{id:'g',key:2,domain:'grammar'}];
class Element {
  constructor(){this.listeners={};this.dataset={};this.children=[];this.open=false;}
  addEventListener(name,fn){this.listeners[name]=fn;}
  click(){this.listeners.click?.({target:this});}
  change(){this.listeners.change?.({target:this});}
  setAttribute(name,value){this[name]=value;}
  append(child){this.children.push(child);}
  replaceChildren(){this.children=[];}
  close(){this.open=false;}
  showModal(){this.open=true;}
}
function reader(autoGrade=false,saved={}){
  const nodes=new Map(),get=id=>{if(!nodes.has(id))nodes.set(id,new Element());return nodes.get(id);};
  const inputs=['show','hide'].map(value=>Object.assign(new Element(),{value})),buttons=[new Element(),new Element()];
  const $=selector=>['.reader-subbar','#catalog-sort'].includes(selector)?null:get(selector);
  const $$=selector=>selector==='[name=auto-grade]'?inputs:selector==='[data-grade]'?buttons:[];
  const preferences={autoGrade,timerEnabled:false,timerDirection:'down'},answers=Object.fromEntries(Object.entries(saved).map(([id,a])=>[id,P.restoreAnswer(a)]));
  const snapshots=[],document={body:new Element(),createElement:()=>new Element(),addEventListener(){}};
  const context={AstraPractice:P,document,window:{addEventListener(){}},setTimeout(){},clearTimeout(){}};
  vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(__dirname,'../web-src/practice-ui.js'),'utf8'),context);
  const saveAnswers=()=>snapshots.push(JSON.parse(JSON.stringify(answers)));
  const ui=context.AstraPracticeUI({$,$$,data:{paper:{unit:'test',level:'N1',timer:{seconds:600}},questions},
    storage:{read(){return null;},savePaper(){}},prefix:'test:',prefs:()=>preferences,persist(){},progress(){},saveAnswers,
    answers:()=>answers,remember:()=>false,epoch:()=>0,editEpoch(){}});
  ui.apply();
  return {ui,answers,snapshots,preferences,document,get,buttons,
    auto(value){inputs[value?0:1].change();},
    choose(id,value){answers[id]=P.answer(answers[id],value,questions.find(q=>q.id===id).key,ui.feedbackVisible);saveAnswers();}};
}
let checks=0;
function check(name,fn){fn();checks++;console.log('PASS '+name);}
check('Grade now freezes hidden revisions and saves immediately; Hide grade leaves history intact',()=>{
  const r=reader();r.choose('v',2);r.choose('v',1);
  assert.equal(P.progress(questions,r.answers).firstTotal,0);
  r.buttons[0].click();
  assert.equal(r.ui.feedbackVisible,true);assert.equal(r.get('#score-dialog').open,true);
  assert.equal(r.snapshots.at(-1).v.firstCorrect,true);
  r.get('#score-dialog').close();r.buttons[1].click();
  assert.equal(r.ui.feedbackVisible,false);r.choose('v',2);r.buttons[0].click();
  assert.equal(r.answers.v.firstCorrect,true);assert.equal(P.progress(questions,r.answers).correct,0);
});
check('switching auto-grade on records existing answers; repeated toggles cannot rewrite results',()=>{
  const r=reader();r.choose('v',1);r.auto(true);
  assert.equal(P.progress(questions,r.answers).correct,1);assert.equal(r.snapshots.at(-1).v.firstCorrect,true);
  r.choose('v',2);const snapshots=r.snapshots.length;
  r.auto(false);assert.equal(r.document.body.dataset.gradesHidden,'true');
  r.auto(true);r.auto(false);r.auto(true);
  assert.equal(r.snapshots.length,snapshots);assert.equal(r.answers.v.firstCorrect,true);
  assert.equal(P.progress(questions,r.answers).correct,0);
});
check('answers made while manual grades remain visible also record first feedback',()=>{
  const r=reader();r.choose('v',2);r.buttons[0].click();r.get('#score-dialog').close();
  r.choose('v',1);r.choose('g',1);
  assert.equal(r.answers.v.firstCorrect,false);assert.equal(r.answers.g.firstCorrect,false);
  r.auto(true);r.choose('g',2);
  assert.equal(P.progress(questions,r.answers).firstCorrect,0);
  assert.equal(P.progress(questions,r.answers).correct,2);
});
check('shared preference changes and reloads capture pending feedback exactly once',()=>{
  const pending={v:P.answer(undefined,1,1,false)};
  const r=reader(false,pending);assert.equal(r.snapshots.length,0);
  r.preferences.autoGrade=true;r.ui.apply();assert.equal(r.snapshots.length,1);
  const loaded=reader(true,r.snapshots[0]);assert.equal(loaded.snapshots.length,0);
  assert.equal(loaded.answers.v.firstCorrect,true);
  const pendingReload=reader(true,pending);
  assert.equal(pendingReload.snapshots.length,1);assert.equal(pendingReload.snapshots[0].v.firstCorrect,true);
});
check('saved first results survive controls and reload without extra metadata',()=>{
  const r=reader(true,{v:{selected:1,completed:true,firstCorrect:true}});
  assert.equal(r.snapshots.length,0);assert.equal(r.answers.v.firstCorrect,true);
  r.auto(false);r.buttons[0].click();r.get('#score-dialog').close();r.choose('v',2);r.auto(true);
  assert.equal(r.answers.v.firstCorrect,true);assert.equal(P.progress(questions,r.answers).firstTotal,1);
  assert.deepEqual(r.answers.v,{selected:2,firstCorrect:true});
});
console.log(JSON.stringify({status:'pass',checks}));
