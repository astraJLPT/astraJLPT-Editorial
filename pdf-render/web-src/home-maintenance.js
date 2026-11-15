/* The following lines of code are safe to remove for users who never visited
 * the website in the previous release. Keep this block while supporting
 * returning visitors. It is embedded only in index.html.
 */
(() => {
  'use strict';
  const prefix='astraJLPT:web:v1:',marker=prefix+'maintenance:compact-papers:1';
  const object=value=>value!==null&&typeof value==='object'&&!Array.isArray(value);
  let store,epoch,keys,index=0,failed=false;
  function preferences(){return JSON.parse(store.getItem(prefix+'preferences')||'{}')||{};}
  function allowed(){const p=preferences();return p.remember!==false&&(p.epoch||0)===epoch;}
  function batch(){
    try {
      if(!allowed())return;
      const end=Math.min(index+8,keys.length);
      for(;index<end;index++){
        const key=keys[index],raw=store.getItem(key);
        if(raw===null)continue;
        let record;
        try {record=JSON.parse(raw);}catch(_){continue;}
        if(!object(record)||!object(record.answers)||!object(record.bindings))continue;
        const entries=Object.entries(record.answers).filter(([,a])=>object(a)&&Number.isInteger(a.selected)&&a.selected>=1&&a.selected<=4);
        const answers=Object.fromEntries(entries.map(([id,a])=>[id,typeof a.firstCorrect==='boolean'?{selected:a.selected,firstCorrect:a.firstCorrect}:{selected:a.selected}]));
        const bindings=Object.fromEntries(entries.filter(([id])=>Object.hasOwn(record.bindings,id)).map(([id])=>[id,record.bindings[id]]));
        const compact=JSON.stringify({...record,answers,bindings});
        if(compact===raw)continue;
        // Re-read before replacing a record: another tab may have saved it.
        if(!allowed())return;
        if(store.getItem(key)!==raw){failed=true;continue;}
        try {store.setItem(key,compact);}catch(_){failed=true;}
      }
      if(index<keys.length)setTimeout(batch,0);
      else if(!failed&&allowed())store.setItem(marker,'1');
    }catch(_){/* Restricted storage must not interrupt reading or navigation. */}
  }
  function start(){
    try {
      store=localStorage;
      if(store.getItem(marker)==='1')return;
      const p=preferences();if(p.remember===false)return;
      epoch=p.epoch||0;keys=[];
      for(let i=0;i<store.length;i++){const key=store.key(i);if(key?.startsWith(prefix+'paper:'))keys.push(key);}
      batch();
    }catch(_){}
  }
  // Yield the first paint; each later batch also gives navigation time to run.
  requestAnimationFrame(()=>setTimeout(start,0));
})();
