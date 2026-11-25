/* Public behavior: away-time, pause/edit, grading history, historical scoring. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
require('../web-src/practice-model.js');require('../web-src/theme-colors.js');
const P=AstraPractice;let checks=0;
function check(name,fn){fn();checks++;console.log('PASS '+name);}
check('reload and a throttled background clock preserve real elapsed time',()=>{
  const t=new P.Timer(null,6600,1000);t.tick(601000);assert.equal(t.seconds(),6000);
  const reloaded=new P.Timer(JSON.parse(JSON.stringify(t.state)),6600,901000);assert.equal(reloaded.seconds(),5700);
  reloaded.pause(901000);reloaded.tick(1901000);assert.equal(reloaded.seconds(),5700);
  reloaded.resume(1901000);reloaded.tick(1961000);assert.equal(reloaded.seconds(),5640);
});
check('v1-compatible saves retain overtime and the manual choice while frozen',()=>{
  const saved={version:1,limit:10000,elapsed:15000,startedAt:23000,running:false,expired:true,
    wallStartedAt:35000,manualRunning:true,direction:'down'};
  const restored=new P.Timer(saved,10,40000,'down',false,12000);
  assert.equal(restored.state.elapsed,20000);assert.equal(restored.advancing,true);
  for(const manualRunning of [true,false]){
    const reopened=new P.Timer({...saved,frozen:true,manualRunning},10,70000,'down',true,12000);
    assert.equal(reopened.state.elapsed,15000);reopened.setFrozen(false,70000);assert.equal(reopened.advancing,manualRunning);
  }
});
check('in-place timer records restore the same pause, overtime, and frozen state as current records',()=>{
  const timer=new P.Timer(null,10,1000);
  function roundTrip(now,offset=0){
    const saved=timer.legacyRecord(offset);
    assert.equal(saved.version,1);
    const read=record=>new P.Timer(record,10,now,'down',timer.state.frozen,offset).state;
    assert.deepEqual(read(saved),read(timer.state));
    return saved;
  }
  assert.equal(roundTrip(21000).running,true); // Countdown passes its limit while the page is closed.
  const offsetClock=roundTrip(21000,500);
  assert.equal(offsetClock.wallStartedAt,1000);assert.equal(offsetClock.startedAt,500);
  timer.pause(5000);assert.equal(roundTrip(21000,54000).running,false);
  timer.resume(6000);timer.setFrozen(true,8000);
  const frozen=roundTrip(21000,1000);
  assert.equal(frozen.running,false);assert.equal(frozen.manualRunning,true);
  assert.equal(frozen.startedAt,7000);assert.equal(frozen.wallStartedAt,8000);
  timer.setFrozen(false,22000);timer.tick(30000);
  const overtime=roundTrip(32000);assert.equal(overtime.expired,true);assert.equal(overtime.manualRunning,true);
});
check('previous timers retain elapsed time, historical offsets and completed results',()=>{
  const old={version:1,limit:600000,elapsed:5000,startedAt:1000,running:true,direction:'down'};
  assert.equal(new P.Timer(old,600,91000,'down',false,80000).state.elapsed,15000);
  const complete=new P.Timer(old,600,990000,'down',true);
  complete.tick(1000000);assert.equal(complete.state.elapsed,5000);
  complete.setFrozen(false,1001000);complete.tick(1003000);assert.equal(complete.state.elapsed,7000);
  const expired=new P.Timer({...old,expired:true,running:false,elapsed:600000},600,1000000);
  expired.tick(1010000);assert.equal(expired.state.elapsed,610000);
  const paused=new P.Timer({...old,direction:'up',expired:true,running:false,elapsed:610000},600,1000000,'up');
  paused.tick(1010000);assert.equal(paused.state.elapsed,610000);
});
check('direction preserves elapsed time; count-up is unrestricted',()=>{
  const t=new P.Timer(null,600,1000);t.tick(61000,'up');assert.equal(t.seconds(),60);
  t.tick(601000,'up');assert.equal(t.seconds(),600);assert.equal(t.expired,false);
  t.tick(661000,'up');assert.equal(t.seconds(),660);assert.equal(t.state.running,true);
  t.tick(661000,'down');assert.equal(t.seconds(),0);assert.equal(t.expired,true);
  t.tick(661000,'up');assert.equal(t.seconds(),660);
});
check('countdown expires once and cannot become negative',()=>{
  const t=new P.Timer(null,60,1000);t.tick(120000);assert.equal(t.seconds(),0);
  assert.equal(t.expired,true);assert.equal(t.advancing,true);assert.equal(t.state.elapsed,119000);
  t.state.notified=true;t.tick(900000);assert.equal(t.state.notified,true);assert.equal(t.state.elapsed,899000);
});
check('time limit and current time can both be raised or shortened',()=>{
  const t=new P.Timer(null,600,1000);t.pause(61000);
  t.setLimit(1200,61000);assert.equal(t.seconds(),1140);
  t.setCurrent(1800,61000);assert.equal(t.seconds(),1800);assert.equal(t.state.limit,1800000);
  t.setCurrent(30,61000);assert.equal(t.seconds(),30);
  t.reset(61000);assert.equal(t.seconds(),1800);assert.equal(t.state.running,false);
  t.tick(61000,'up');t.reset(61000);assert.equal(t.seconds(),0);
});
check('time parsing rejects ambiguous/invalid fields without restricting exam extensions',()=>{
  assert.equal(P.parse('12:34:56'),45296);assert.equal(P.format(45296),'12:34:56');
  for(const value of ['-1:00:00','1:60:00','1:00:60','1:2:3','Infinity'])assert.equal(P.parse(value),null);
});
const q=[{id:'v',domain:'vocab',key:1},{id:'g',domain:'grammar',key:2},{id:'r',domain:'reading',key:3},{id:'x',domain:'reading',key:null}];
check('current correctness falls after a wrong revision while answered and first try remain stable',()=>{
  const answers={v:P.answer(undefined,1,1,true),g:P.answer(undefined,2,2,true)};
  assert.deepEqual(P.progress(q,answers),{total:3,answered:2,correct:2,firstCorrect:2,firstTotal:2});
  answers.v=P.answer(answers.v,2,1,true);
  assert.deepEqual(P.progress(q,answers),{total:3,answered:2,correct:1,firstCorrect:2,firstTotal:2});
  assert.equal(P.score(q,answers,{level:'N1'}).correct,1);
});
check('hidden revisions count only when feedback is first shown',()=>{
  const answers={v:P.answer(undefined,2,1,false)};
  answers.v=P.answer(answers.v,1,1,false);
  assert.equal(P.progress(q,answers).firstTotal,0);
  assert.equal(P.recordFirstFeedback(q,answers),true);
  assert.equal(answers.v.firstCorrect,true);
  answers.v=P.answer(answers.v,2,1,false);
  assert.equal(P.recordFirstFeedback(q,answers),false);
  assert.equal(answers.v.firstCorrect,true);
  assert.equal(P.progress(q,answers).correct,0);
});
check('feedback for a wrong answer stays a failed first try after hidden or visible corrections',()=>{
  const answers={v:P.answer(undefined,2,1,false)};
  P.recordFirstFeedback(q,answers);
  answers.v=P.answer(answers.v,1,1,true);
  const counts=P.progress(q,answers);
  assert.equal(counts.correct,1);assert.equal(counts.firstCorrect,0);assert.equal(counts.firstTotal,1);
});
check('reload preserves both pending answers and frozen first results',()=>{
  const answers={v:P.answer(undefined,2,1,false),g:P.answer(undefined,1,2,true)};
  const loaded=Object.fromEntries(Object.entries(JSON.parse(JSON.stringify(answers))).map(([id,a])=>[id,P.restoreAnswer(a)]));
  loaded.v=P.answer(loaded.v,1,1,false);loaded.g=P.answer(loaded.g,2,2,false);
  assert.equal(P.recordFirstFeedback(q,loaded),true);
  assert.equal(loaded.v.firstCorrect,true);assert.equal(loaded.g.firstCorrect,false);
  const snapshot=JSON.stringify(loaded);
  assert.equal(P.recordFirstFeedback(q,loaded),false);assert.equal(JSON.stringify(loaded),snapshot);
});
check('saved first-try booleans survive restoration and later corrections',()=>{
  for(const result of [true,false]){
    const saved={selected:1,firstCorrect:result,completed:true,attempts:2};
    const answers={v:P.restoreAnswer(saved)};
    assert.equal(answers.v.selected,1);assert.equal(P.recordFirstFeedback(q,answers),false);
    answers.v=P.answer(answers.v,2,1,true);answers.v=P.answer(answers.v,1,1,true);
    assert.deepEqual(P.progress(q,answers),{total:3,answered:1,correct:1,firstCorrect:Number(result),firstTotal:1});
    assert.deepEqual(P.restoreAnswer(JSON.parse(JSON.stringify(answers.v))),{selected:1,firstCorrect:result});
  }
});
check('missing or null first results remain pending until feedback appears',()=>{
  for(const saved of [{selected:1},{selected:1,firstCorrect:null},{selected:1,firstFeedbackVersion:1}]){
    const answers={v:P.restoreAnswer(saved)};
    assert.deepEqual(answers.v,{selected:1});
    assert.equal(P.progress(q,answers).firstTotal,0);
    assert.equal(P.recordFirstFeedback(q,answers),true);
    assert.deepEqual(answers.v,{selected:1,firstCorrect:true});
  }
});
check('unconfirmed keys and invalid selections do not enter progress or first try',()=>{
  const answers={v:P.answer(undefined,1,1,false),g:P.answer(undefined,5,2,false),x:P.answer(undefined,1,null,true)};
  P.recordFirstFeedback(q,answers);
  assert.deepEqual(P.progress(q,answers),{total:3,answered:1,correct:1,firstCorrect:1,firstTotal:1});
  assert.equal(Object.hasOwn(answers.x,'firstCorrect'),false);
});
check('modern scores use current selection and exclude unconfirmed keys',()=>{
  const score=P.score(q,{v:{selected:1},g:{selected:1,completed:true},r:{selected:3}},{level:'N1',generation:'modern-2010'});
  assert.equal(score.total,90);assert.equal(score.excluded,1);assert.equal(score.questions,3);
  assert.equal(P.score(q,{v:{selected:1},r:{selected:3}},{level:'N4',generation:'modern-2010'}).total,80);
});
check('missing sections are unavailable; historical estimates keep /100 + /200',()=>{
  const score=P.score(q.slice(0,2),{v:{selected:1}},{level:'1級',generation:'historical-1991-2009'});
  assert.deepEqual(score.sections.map(s=>s.maximum),[100,200]);assert.equal(score.total,100);
  assert.equal(P.score(q.slice(0,1),{}, {level:'N1',generation:'modern-2010'}).sections[1].score,null);
});
check('all verified historical tables cover stable question IDs and reproduce their maximum',()=>{
  const registry=JSON.parse(fs.readFileSync(path.join(__dirname,'../web-src/historical-scoring.json'),'utf8'));
  for(const [unit,profile]of Object.entries(registry.profiles)){
    const html=fs.readFileSync(path.join(__dirname,'../../astraJLPT/papers',unit+'.html'),'utf8');
    const data=JSON.parse(/<script[^>]*id="page-data"[^>]*>(.*?)<\/script>/s.exec(html)[1]);
    const source=fs.readFileSync(path.join(__dirname,'../../astraJLPT/assets/questions',unit+'.js'),'utf8');
    const shared=JSON.parse(source.replace(/^globalThis.AstraQuestions = /,'').trim().replace(/;$/,''));
    assert.equal(shared.unit,unit);data.questions=shared.questions;
    const all=Object.fromEntries(data.questions.filter(P.gradable).map(q=>[q.id,{selected:q.key}]));
    const score=P.score(data.questions,all,data.paper);
    for(const [id,section]of Object.entries(profile.sections)){
      assert.equal(Object.values(section.weights).reduce((a,b)=>a+b,0),section.raw_maximum,unit+'/'+id);
      const result=score.sections.find(s=>s.id===id);assert.equal(result.weighted,true,unit+'/'+id);assert.equal(result.score,section.maximum,unit+'/'+id);
    }
  }
});
check('neutral follows reading text, accepts overrides, and shares fill opacity',()=>{
  const source=fs.readFileSync(path.join(__dirname,'../../astraJLPT/assets/theme-data.js'),'utf8');
  const data=JSON.parse(source.replace(/^globalThis.AstraThemes = /,'').trim().replace(/;$/,''));
  const theme=data.originals[0],roles=data.colorRoles;
  const a=AstraThemeColors.resolve(theme,'auto',{text:'#123456'},roles,{'cell-fill':25});
  assert.deepEqual(a.neutral,a.text);assert.equal(a['neutral-cell-fill'][3],.25);
  const b=AstraThemeColors.resolve(theme,'auto',{neutral:'#abcdef'},roles);assert.deepEqual(b.neutral,[171,205,239,1]);
});
check('chronological sorting uses month and recommended ordering remains reversible',()=>{
  const rows=[{rank:0,year:2018,month:0},{rank:1,year:2020,month:7},{rank:2,year:2020,month:12},{rank:3,year:2009,month:0}];
  assert.deepEqual([...rows].sort((a,b)=>P.compare(a,b,'newest')).map(r=>r.rank),[2,1,0,3]);
  assert.deepEqual([...rows].sort((a,b)=>P.compare(a,b,'oldest')).map(r=>r.rank),[3,0,1,2]);
});
console.log(JSON.stringify({status:'pass',checks}));
