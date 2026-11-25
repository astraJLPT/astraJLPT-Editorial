/* Origin-wide preferences and per-paper progress. */
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
  write(key, value, onQuota) {
    try {
      const store=this.getStorage(),encoded=JSON.stringify(value);
      try {store.setItem(this.prefix+key,encoded);}
      catch (error) {
        if(error.name!=='QuotaExceededError'||!onQuota?.(store,encoded))throw error;
      }
      return true;
    } catch (_) {this.available=false;return false;}
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
  openPractice(kind, paper, remember, epoch) {
    if(!paper)return null;
    const suffix=':'+(paper.storage_unit||paper.unit)+(paper.variant==='norubi'?':norubi':'');
    const key=kind+'2'+suffix,openedEpoch=epoch();
    // Import this visit's old save until the first current write. Older tabs
    // can still save to their key and Forget invalidates the imported snapshot.
    const legacyKey=kind+suffix;
    let legacy=remember&&this.read(key)===null?this.read(legacyKey):null;
    const recoverQuota=(store,encoded,legacyValue)=>{
      if(paper.variant==='norubi'||epoch()!==openedEpoch||(kind!=='paper'&&kind!=='timer'))return false;
      const source=this.prefix+legacyKey,target=this.prefix+key,original=store.getItem(source);
      if(original===null)return false;
      if(legacy&&JSON.stringify(JSON.parse(original))!==JSON.stringify(legacy))return false;
      const current=store.getItem(target);
      if(current!==null){
        // A successful migration can leave two copies. The current save stays
        // durable throughout the retry, including after reopening the reader.
        const saved=JSON.parse(current);
        const hasProgress=kind==='timer'?[1,2].includes(saved?.version):saved?.answers||Number.isFinite(saved?.position);
        if(!hasProgress)return false;
        store.removeItem(source);
        try {store.setItem(target,encoded);}
        catch (error) {
          if(store.getItem(source)===null)store.setItem(source,original);
          throw error;
        }
        legacy=null;
      }else{
        // Without a current copy, replace the imported record atomically.
        if(!legacy)return false;
        const replacement=legacyValue?JSON.stringify(legacyValue()):encoded;
        store.setItem(source,replacement);
        legacy=JSON.parse(replacement);
      }
      return true;
    };
    return {key,read:()=>this.read(key)??(epoch()===openedEpoch?legacy:null),
      save:(value,expectedEpoch,legacyValue)=>this.savePaper(key,value,expectedEpoch,
        (store,encoded)=>recoverQuota(store,encoded,legacyValue))};
  }
  savePaper(key, value, epoch, onQuota) {
    const current=this.preferences();
    return current.remember&&current.epoch===epoch&&this.write(key,value,onQuota);
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
