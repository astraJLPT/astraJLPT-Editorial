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
