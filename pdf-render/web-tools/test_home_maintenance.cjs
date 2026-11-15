/* One home-page visit compacts all owned papers without losing saved progress. */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const source=fs.readFileSync(path.join(__dirname,'../web-src/home-maintenance.js'),'utf8');
const prefix='astraJLPT:web:v1:',marker=prefix+'maintenance:compact-papers:1';
class Store {
  constructor(rows={}){this.rows=new Map(Object.entries(rows));this.writes=[];this.fail=null;}
  get length(){return this.rows.size;}
  key(i){return [...this.rows.keys()][i]??null;}
  getItem(k){return this.rows.get(k)??null;}
  setItem(k,v){if(k===this.fail)throw Error('QuotaExceededError');this.rows.set(k,String(v));this.writes.push(k);}
  removeItem(k){this.rows.delete(k);}
}
function visit(store){
  const queue=[];
  vm.runInNewContext(source,{localStorage:store,requestAnimationFrame:f=>queue.push(f),setTimeout:f=>queue.push(f)});
  return {queue,step(){queue.shift()?.();},finish(){while(queue.length)this.step();}};
}
const read=(store,key)=>JSON.parse(store.getItem(prefix+key));
const record={position:1423,extra:'preserved',answers:{a:{selected:2,firstCorrect:false,completed:true,attempts:3,firstFeedbackVersion:1},b:{selected:1,firstCorrect:true},c:{selected:3,firstCorrect:null},empty:{selected:null}},bindings:{a:'a-token',b:'b-token',c:'c-token',empty:'empty-token',unseen:'unused-token'}};
let checks=0;
function check(name,fn){fn();checks++;console.log('PASS '+name);}
check('fresh visitors perform no paper writes and completed visits are skipped',()=>{
  const store=new Store();visit(store).finish();assert.deepEqual(store.writes,[marker]);
  store.writes=[];visit(store).finish();assert.deepEqual(store.writes,[]);
});
check('one visit cleans all paper editions, retaining selections, booleans, bindings and positions',()=>{
  const rows={'unrelated':'keep',[prefix+'preferences']:JSON.stringify({remember:true,epoch:3,values:{theme:'light'}}),[prefix+'timer:N1_07_2011']:'{"elapsed":12345}'};
  for(let i=0;i<20;i++)rows[prefix+'paper:unit-'+i+(i%2?':norubi':'')]=JSON.stringify(record);
  const store=new Store(rows),v=visit(store);v.step();v.step();
  assert.equal(store.getItem(marker),null);v.finish();
  for(let i=0;i<20;i++){
    const after=read(store,'paper:unit-'+i+(i%2?':norubi':''));
    assert.deepEqual(after,{position:1423,extra:'preserved',answers:{a:{selected:2,firstCorrect:false},b:{selected:1,firstCorrect:true},c:{selected:3}},bindings:{a:'a-token',b:'b-token',c:'c-token'}});
  }
  assert.equal(store.getItem('unrelated'),'keep');
  assert.equal(store.getItem(prefix+'timer:N1_07_2011'),rows[prefix+'timer:N1_07_2011']);
  assert.equal(store.getItem(prefix+'preferences'),rows[prefix+'preferences']);
  assert.equal(store.getItem(marker),'1');
});
check('browsed but unanswered papers retain their reading positions',()=>{
  const store=new Store({[prefix+'paper:empty']:JSON.stringify({answers:{},position:750,bindings:{a:'unused'}})});
  visit(store).finish();assert.deepEqual(read(store,'paper:empty'),{answers:{},position:750,bindings:{}});
});
check('invalid JSON and unfamiliar record shapes are left untouched',()=>{
  const rows={[prefix+'paper:broken']:'{broken',[prefix+'paper:unknown']:'{"answers":null,"position":50}'};
  const store=new Store(rows);visit(store).finish();for(const [key,value]of Object.entries(rows))assert.equal(store.getItem(key),value);
});
check('failed replacements retain original records and can retry on a later visit',()=>{
  const key=prefix+'paper:full',raw=JSON.stringify(record),store=new Store({[key]:raw});store.fail=key;
  visit(store).finish();assert.equal(store.getItem(key),raw);assert.equal(store.getItem(marker),null);
  store.fail=null;visit(store).finish();assert.equal(read(store,'paper:full').answers.a.firstCorrect,false);assert.equal(store.getItem(marker),'1');
});
check('forget or an epoch change between batches stops cleanup without recreating records',()=>{
  for(const change of [{remember:false,epoch:1},{remember:true,epoch:1}]){
    const rows={};for(let i=0;i<20;i++)rows[prefix+'paper:'+i]=JSON.stringify(record);
    const store=new Store(rows),v=visit(store);v.step();v.step();
    store.rows.clear();store.setItem(prefix+'preferences',JSON.stringify(change));store.writes=[];v.finish();
    assert.deepEqual(store.writes,[]);assert.equal(store.length,1);
  }
});
check('opted-out and denied storage are harmless',()=>{
  const store=new Store({[prefix+'preferences']:'{"remember":false}',[prefix+'paper:a']:JSON.stringify(record)});
  visit(store).finish();assert.deepEqual(store.writes,[]);
  const denied={getItem(){throw Error('SecurityError');}};assert.doesNotThrow(()=>visit(denied).finish());
});
check('a concurrent paper save is retained and leaves cleanup retryable',()=>{
  const key=prefix+'paper:other-tab',store=new Store({[key]:JSON.stringify(record)}),get=store.getItem.bind(store);let reads=0;
  const latest=JSON.stringify({...record,position:9000});
  store.getItem=k=>{if(k===key&&++reads===2)store.rows.set(key,latest);return get(k);};
  visit(store).finish();assert.equal(store.getItem(key),latest);assert.equal(store.getItem(marker),null);
});
console.log(JSON.stringify({status:'pass',checks}));
