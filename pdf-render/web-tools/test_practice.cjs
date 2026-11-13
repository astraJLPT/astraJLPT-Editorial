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
check('disabling the shared clock also pauses closed papers',()=>{
  const p={timerEnabled:true,timerDisabledTotal:0};const t=new P.Timer(null,600,P.clock(p,1000));
  P.setEnabled(p,false,61000);t.tick(P.clock(p,361000));assert.equal(t.seconds(),540);
  P.setEnabled(p,true,361000);t.tick(P.clock(p,421000));assert.equal(t.seconds(),480);
});
check('direction preserves elapsed time; count-up is unrestricted',()=>{
  const t=new P.Timer(null,600,1000);t.tick(61000,'up');assert.equal(t.seconds(),60);
  t.tick(601000,'up');assert.equal(t.seconds(),600);assert.equal(t.state.expired,false);
  t.tick(661000,'up');assert.equal(t.seconds(),660);assert.equal(t.state.running,true);
  t.tick(661000,'down');assert.equal(t.seconds(),0);assert.equal(t.state.expired,true);
  t.tick(661000,'up');assert.equal(t.seconds(),660);
});
check('countdown expires once and cannot become negative',()=>{
  const t=new P.Timer(null,60,1000);t.tick(120000);assert.equal(t.seconds(),0);
  assert.equal(t.state.expired,true);assert.equal(t.state.running,false);
  t.state.notified=true;t.tick(900000);assert.equal(t.state.notified,true);
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
check('hidden answers remain editable without altering first-try or completion history',()=>{
  let a=P.answer(undefined,2,1,false);assert.deepEqual(a,{selected:2});
  a=P.answer(a,1,1,false);assert.deepEqual(a,{selected:1});
  a=P.answer(a,2,1,true);assert.equal(a.firstCorrect,false);assert.equal(a.completed,false);
  a=P.answer(a,1,1,true);assert.equal(a.completed,true);assert.equal(a.attempts,2);
  const hidden=P.answer(a,3,1,false);assert.deepEqual(hidden,{...a,selected:3});
});
const q=[{id:'v',domain:'vocab',key:1},{id:'g',domain:'grammar',key:2},{id:'r',domain:'reading',key:3},{id:'x',domain:'reading',key:null}];
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
