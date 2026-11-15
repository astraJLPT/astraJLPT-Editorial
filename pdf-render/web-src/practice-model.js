/* Deterministic practice rules, shared with the regression checks. */
globalThis.AstraPractice = (() => {
  'use strict';
  const finite = (v, fallback=0) => typeof v==='number'&&Number.isFinite(v)&&v>=0?v:fallback;
  const direction = value => value==='up'?'up':'down';
  // A shared stopped clock pauses even papers which are not currently open.
  function clock(preferences, now=Date.now()) {
    return now-finite(preferences.timerDisabledTotal)-(preferences.timerEnabled===false?
      Math.max(0,now-finite(preferences.timerDisabledAt,now)):0);
  }
  function setEnabled(preferences, enabled, now=Date.now()) {
    if(enabled===(preferences.timerEnabled!==false))return;
    if(enabled){
      preferences.timerDisabledTotal=finite(preferences.timerDisabledTotal)+Math.max(0,now-finite(preferences.timerDisabledAt,now));
      preferences.timerDisabledAt=null;
    }else preferences.timerDisabledAt=now;
    preferences.timerEnabled=enabled;
  }
  class Timer {
    constructor(saved, limitSeconds, now, mode='down') {
      const valid=saved?.version===1;
      this.state={version:1,limit:finite(valid?saved.limit:null,limitSeconds*1000),
        elapsed:finite(valid?saved.elapsed:null),startedAt:finite(valid?saved.startedAt:null,now),
        running:valid?saved.running===true:true,direction:valid?direction(saved.direction):direction(mode),
        expired:valid&&saved.expired===true,notified:valid&&saved.notified===true,
        revision:finite(valid?saved.revision:null)};
      this.tick(now,mode);
    }
    tick(now, mode=this.state.direction) {
      const s=this.state;
      if(s.running){
        s.elapsed+=Math.max(0,now-s.startedAt);
        if(s.direction==='down'&&s.elapsed>=s.limit){s.elapsed=s.limit;s.running=false;s.expired=true;}
      }
      s.startedAt=now;s.direction=direction(mode);
      if(s.direction==='down'&&s.elapsed>=s.limit){s.running=false;s.expired=true;}
      return this.seconds();
    }
    seconds() {
      const s=this.state;
      return s.direction==='up'?Math.floor(s.elapsed/1000):Math.max(0,Math.ceil((s.limit-s.elapsed)/1000));
    }
    pause(now){this.tick(now);this.state.running=false;}
    resume(now){this.tick(now);if(this.state.direction==='up'||this.state.elapsed<this.state.limit)this.state.running=true;}
    reset(now){const s=this.state;s.elapsed=0;s.startedAt=now;s.expired=false;s.notified=false;}
    setLimit(seconds, now){this.tick(now);const s=this.state;s.limit=seconds*1000;s.expired=false;s.notified=false;this.tick(now);}
    setCurrent(seconds, now){
      this.tick(now);const s=this.state;
      if(s.direction==='down'){s.limit=Math.max(s.limit,seconds*1000);s.elapsed=s.limit-seconds*1000;}
      else s.elapsed=seconds*1000;
      s.startedAt=now;s.expired=false;s.notified=false;this.tick(now);
    }
  }
  function format(seconds) {
    seconds=Math.max(0,Math.floor(seconds));
    return Math.floor(seconds/3600)+':'+String(Math.floor(seconds/60)%60).padStart(2,'0')+':'+String(seconds%60).padStart(2,'0');
  }
  function parse(value) {
    const match=/^(\d{1,6}):([0-5]\d):([0-5]\d)$/.exec(value.trim());
    return match?Number(match[1])*3600+Number(match[2])*60+Number(match[3]):null;
  }
  const option=value=>Number.isInteger(value)&&value>=1&&value<=4;
  const gradable=q=>option(q.key);
  function restoreAnswer(saved) {
    const next={selected:saved.selected};
    if(typeof saved.firstCorrect==='boolean')next.firstCorrect=saved.firstCorrect;
    return next;
  }
  function firstFeedback(record, key) {
    if(!record||typeof record.firstCorrect==='boolean'||!option(record.selected)||!option(key))return false;
    record.firstCorrect=record.selected===key;
    return true;
  }
  function answer(previous, selected, key, feedbackVisible) {
    const next=previous?restoreAnswer(previous):{};
    next.selected=selected;
    if(feedbackVisible)firstFeedback(next,key);
    return next;
  }
  function recordFirstFeedback(questions, answers) {
    let changed=false;
    for(const q of questions)if(firstFeedback(answers[q.id],q.key))changed=true;
    return changed;
  }
  function progress(questions, answers) {
    const rows=questions.filter(gradable),selected=rows.filter(q=>option(answers[q.id]?.selected));
    const tracked=selected.map(q=>answers[q.id]).filter(a=>typeof a.firstCorrect==='boolean');
    return {total:rows.length,answered:selected.length,correct:selected.filter(q=>answers[q.id].selected===q.key).length,
      firstCorrect:tracked.filter(a=>a.firstCorrect).length,firstTotal:tracked.length};
  }
  function score(questions, answers, paper) {
    const old=paper.generation?.startsWith('historical');
    const combined=!old&&['N4','N5'].includes(paper.level);
    const definitions=old?[
      ['vocabulary','文字・語彙',100,q=>q.domain==='vocab'],
      ['reading_grammar','読解・文法',200,q=>q.domain!=='vocab']
    ]:combined?[
      ['written','語彙・文法・読解',120,()=>true]
    ]:[
      ['knowledge','語彙・文法',60,q=>q.domain!=='reading'],
      ['reading','読解',60,q=>q.domain==='reading']
    ];
    const sections=definitions.map(([id,label,maximum,belongs])=>{
      const all=questions.filter(belongs),rows=all.filter(gradable);
      const profile=paper.scoring?.sections?.[id];
      const weighted=Boolean(profile&&all.every(q=>finite(profile.weights[q.id])>0));
      const weight=q=>weighted?profile.weights[q.id]:1;
      const denominator=rows.reduce((n,q)=>n+weight(q),0);
      const correct=rows.filter(q=>answers[q.id]?.selected===q.key);
      const earned=correct.reduce((n,q)=>n+weight(q),0);
      return {id,label,maximum,total:rows.length,correct:correct.length,
        answered:rows.filter(q=>option(answers[q.id]?.selected)).length,
        excluded:all.length-rows.length,weighted,denominator,earned,
        exact:weighted&&all.length===rows.length&&!paper.partial&&denominator===profile.raw_maximum,
        score:denominator?Math.round(earned/denominator*maximum):null};
    });
    const available=sections.filter(s=>s.score!==null);
    return {sections,old,combined,total:available.reduce((n,s)=>n+s.score,0),
      maximum:available.reduce((n,s)=>n+s.maximum,0),expectedMaximum:sections.reduce((n,s)=>n+s.maximum,0),
      correct:available.reduce((n,s)=>n+s.correct,0),answered:available.reduce((n,s)=>n+s.answered,0),
      questions:available.reduce((n,s)=>n+s.total,0),excluded:sections.reduce((n,s)=>n+s.excluded,0),
      exact:available.length===sections.length&&available.every(s=>s.exact)};
  }
  function compare(a,b,mode) {
    if(mode==='newest'||mode==='oldest'){
      const order=(Number(a.year)-Number(b.year))||(Number(a.month||0)-Number(b.month||0));
      if(order)return mode==='newest'?-order:order;
    }
    return Number(a.rank)-Number(b.rank);
  }
  return {Timer,clock,setEnabled,format,parse,answer,restoreAnswer,recordFirstFeedback,progress,score,gradable,compare};
})();
