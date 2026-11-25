/* Storage behavior with two clients, including writes before event delivery. */
const assert=require('node:assert/strict');
require('../web-src/browser-memory.js');
const Memory=globalThis.AstraBrowserMemory,prefix='astraJLPT:test:';
class Store {
  constructor(){this.rows=new Map();this.writes=0;}
  get length(){return this.rows.size;}
  key(i){return [...this.rows.keys()][i]??null;}
  getItem(k){return this.rows.get(k)??null;}
  setItem(k,v){this.rows.set(k,String(v));this.writes++;}
  removeItem(k){this.rows.delete(k);}
}
let checks=0;
function check(name,fn){fn();checks++;console.log('PASS '+name);}
const store=new Store(),a=new Memory(()=>store,prefix),b=new Memory(()=>store,prefix);
const defaults={theme:'dark',line:90,spacingVersion:2};
check('new visitors remember without a prior record',()=>{
  assert.equal(a.preferences().remember,true);
  a.savePreferences(defaults);
  assert.deepEqual(b.preferences().values,defaults);
});
check('different fields changed in stale tabs are retained',()=>{
  a.savePreferences({...defaults,theme:'light'},defaults);
  b.savePreferences({...defaults,line:80},defaults);
  assert.deepEqual(a.preferences().values,{theme:'light',line:80,spacingVersion:2});
});
check('reset can replace saved custom settings',()=>{
  a.savePreferences({...defaults,customColors:{light:{bg:'#eeeeee'}}});
  a.savePreferences(defaults);
  assert.deepEqual(b.preferences().values,defaults);
});
const paper={answers:{'vocab-q001':{selected:2,completed:true,firstCorrect:true,attempts:1}},position:1432,bindings:{'vocab-q001':'frozen-binding'}};
check('paper and rendition records remain independent',()=>{
  assert.ok(a.savePaper('paper:N1_07_2011',paper,0));
  assert.ok(b.savePaper('paper:N3_07_2011',{...paper,position:42},0));
  assert.ok(b.savePaper('paper:N1_07_2011:norubi',{...paper,answers:{}},0));
  assert.deepEqual(b.read('paper:N1_07_2011'),paper);
  assert.equal(a.read('paper:N3_07_2011').position,42);
  assert.deepEqual(a.read('paper:N1_07_2011:norubi').answers,{});
});
check('current readers import the active old unit and ignore stale writes and forgotten epochs',()=>{
  let epoch=0;
  const unit={unit:'new-name',storage_unit:'N1_07_2011'},open=variant=>a.openPractice('paper',{...unit,variant},true,()=>epoch);
  const before=store.writes,ruby=open('rubi'),plain=open('norubi');
  assert.equal(store.writes,before);assert.deepEqual(ruby.read(),paper);assert.deepEqual(plain.read().answers,{});
  a.savePaper(ruby.key,{answers:{}},epoch);
  b.savePaper('paper:N1_07_2011',paper,epoch);assert.deepEqual(open('rubi').read(),{answers:{}});
  epoch++;assert.equal(plain.read(),null);
});
check('a failed in-place save or stale import preserves the last good paper',()=>{
  const store=new Store(),m=new Memory(()=>store,prefix),unit={unit:'test'},key=prefix+'paper:test';
  m.savePaper('paper:test',paper,0);
  const imported=m.openPractice('paper',unit,true,()=>0);
  store.setItem=()=>{throw new DOMException('Storage full','QuotaExceededError');};
  assert.equal(imported.save({...paper,position:50},0),false);
  assert.deepEqual(JSON.parse(store.getItem(key)),paper);
  const other={...paper,position:99};store.rows.set(key,JSON.stringify(other));
  store.setItem=(name,value)=>{
    if(name!==key)throw new DOMException('Storage full','QuotaExceededError');
    store.rows.set(name,value);
  };
  assert.equal(imported.save({...paper,position:10},0),false);
  assert.deepEqual(JSON.parse(store.getItem(key)),other);
});
check('a quota retry that still fails restores the superseded copy and retains the current save',()=>{
  const store=new Store(),memory=new Memory(()=>store,prefix);
  const older=prefix+'paper:test',current=prefix+'paper2:test',original=JSON.stringify(paper,null,2);
  const migrated=JSON.stringify({...paper,position:600});
  store.setItem(older,original);store.setItem(current,migrated);
  const removed=[];
  store.removeItem=key=>{removed.push(key);store.rows.delete(key);};
  store.setItem=(key,value)=>{
    if(key===current)throw new DOMException('Storage full','QuotaExceededError');
    store.rows.set(key,value);
  };
  const record=memory.openPractice('paper',{unit:'test'},true,()=>0);
  assert.equal(record.save({...paper,position:700},0),false);
  assert.deepEqual(removed,[older]);assert.equal(store.getItem(older),original);assert.equal(store.getItem(current),migrated);
  // A corrupt current copy must never authorize removing the only readable save.
  store.rows.set(current,'{invalid');removed.length=0;
  assert.equal(memory.openPractice('paper',{unit:'test'},true,()=>0).save(paper,0),false);
  assert.deepEqual(removed,[]);assert.equal(store.getItem(older),original);
});
check('forget keeps unrelated storage and prevents stale writes',()=>{
  store.setItem('unrelated','keep');a.forget();
  assert.equal(store.getItem('unrelated'),'keep');
  assert.equal(b.preferences().remember,false);
  assert.equal(b.read('paper:N1_07_2011'),null);
  assert.equal(b.savePaper('paper:N1_07_2011',paper,0),false);
  assert.equal(b.savePreferences(defaults),null);
  assert.equal(b.preferences().remember,false);
});
check('explicit re-enable cannot revive another tab’s pending old records',()=>{
  const current=a.savePreferences(defaults,null,true);
  assert.equal(current.epoch,1);
  assert.equal(b.savePaper('paper:N1_07_2011',paper,0),false);
  assert.ok(a.savePaper('paper:N1_07_2011',paper,current.epoch));
});
check('legacy opt-out survives a new visit',()=>{
  store.setItem(prefix+'preferences',JSON.stringify({remember:false}));
  const fresh=new Memory(()=>store,prefix);
  assert.equal(fresh.preferences().remember,false);
  assert.equal(fresh.savePreferences(defaults),null);
});
check('legacy remembered preferences and progress need no migration',()=>{
  store.setItem(prefix+'preferences',JSON.stringify({remember:true,values:defaults}));
  assert.deepEqual(b.preferences(),{remember:true,values:defaults,epoch:0});
  assert.deepEqual(b.read('paper:N1_07_2011'),paper);
});
check('denied storage does not throw or disable in-memory use',()=>{
  const denied=new Memory(()=>{throw Error('SecurityError');},prefix);
  assert.equal(denied.preferences().remember,true);
  assert.equal(denied.available,false);
  assert.equal(denied.savePreferences(defaults),null);
  assert.equal(denied.savePaper('paper:a',paper,0),false);
  assert.doesNotThrow(()=>denied.forget());
});
check('quota failure and malformed records are handled',()=>{
  const full=new Memory(()=>({getItem(){return null;},setItem(){throw Error('QuotaExceededError');}}),prefix);
  assert.equal(full.savePreferences(defaults),null);assert.equal(full.available,false);
  store.setItem(prefix+'preferences','{invalid');
  assert.equal(b.preferences().remember,true);assert.equal(b.available,true);
  assert.ok(b.savePreferences(defaults));
});
console.log(JSON.stringify({status:'pass',checks}));
