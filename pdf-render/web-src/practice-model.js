/* Deterministic practice rules, shared with the regression checks. */
globalThis.AstraPractice = (() => {
  'use strict';
  const finite = (v, fallback=0) => typeof v==='number'&&Number.isFinite(v)&&v>=0?v:fallback;
  const direction = value => value==='up'?'up':'down';
  class Timer {
    constructor(saved, limitSeconds, now, mode='down', frozen=saved?.frozen===true, legacyOffset=0) {
      // The frozen flag identifies a current timer saved in the old slot.
      // Earlier compatible saves also supplied the wall clock and pause flag.
      if(saved?.version===1&&(typeof saved.frozen==='boolean'||
        (Number.isFinite(saved.wallStartedAt)&&typeof saved.manualRunning==='boolean'))){
        saved={...saved,version:2,startedAt:saved.wallStartedAt??saved.startedAt,running:saved.manualRunning??saved.running};
      }
      const legacy=saved?.version===1;
      if(!legacy&&saved?.version!==2)saved=null;
      const limit=finite(saved?.limit,limitSeconds*1000);
      let elapsed=finite(saved?.elapsed);
      if(saved?.running&&!frozen&&!saved.frozen){
        // Old timestamps excluded intervals when the timer was disabled.
        const clockNow=legacy?now-legacyOffset:now;
        const away=Math.max(0,clockNow-finite(saved.startedAt,clockNow));
        elapsed+=legacy&&saved.direction==='down'?Math.min(away,Math.max(0,limit-elapsed)):away;
      }
      const stoppedAtDeadline=legacy&&saved.direction==='down'&&saved.expired===true&&elapsed>=limit;
      this.state={version:2,limit,elapsed,startedAt:now,direction:direction(mode),frozen,
        running:!saved||saved.running===true||stoppedAtDeadline,
        notified:saved?.notified===true,revision:finite(saved?.revision)};
    }
    legacyRecord(offset=0){
      const record={...this.state,version:1};
      // Both readers default to countdown and an unannounced deadline.
      if(record.direction==='down')delete record.direction;
      if(!record.notified)delete record.notified;
      const running=this.advancing&&!this.expired;
      if(running!==record.running||this.expired){
        record.manualRunning=record.running;
        record.running=running;
        if(this.expired)record.expired=true;
      }
      // A paused clock needs no offset. When the two clocks or their running
      // states differ, older readers use startedAt and the new reader uses wallStartedAt.
      if((running&&offset)||record.manualRunning!==undefined){
        record.wallStartedAt=record.startedAt;
        record.startedAt-=offset;
      }
      return record;
    }
    get advancing(){return this.state.running&&!this.state.frozen;}
    get expired(){return this.state.direction==='down'&&this.state.elapsed>=this.state.limit;}
    tick(now, mode=this.state.direction) {
      const s=this.state;
      if(this.advancing)s.elapsed+=Math.max(0,now-s.startedAt);
      s.startedAt=now;s.direction=direction(mode);
      return this.seconds();
    }
    seconds() {
      const s=this.state;
      return s.direction==='up'?Math.floor(s.elapsed/1000):Math.max(0,Math.ceil((s.limit-s.elapsed)/1000));
    }
    setFrozen(frozen,now){this.tick(now);this.state.frozen=frozen;}
    pause(now){if(!this.state.frozen){this.tick(now);this.state.running=false;}}
    resume(now){if(!this.state.frozen){this.tick(now);this.state.running=true;}}
    reset(now){const s=this.state;s.elapsed=0;s.startedAt=now;s.notified=false;}
    setLimit(seconds, now){this.tick(now);this.state.limit=seconds*1000;this.state.notified=false;}
    setCurrent(seconds, now){
      this.tick(now);const s=this.state;
      if(s.direction==='down'){s.limit=Math.max(s.limit,seconds*1000);s.elapsed=s.limit-seconds*1000;}
      else s.elapsed=seconds*1000;
      s.notified=false;
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
    const counts={total:0,answered:0,correct:0,firstCorrect:0,firstTotal:0};
    for(const q of questions){
      if(!gradable(q))continue;
      counts.total++;
      const record=answers[q.id];
      if(!option(record?.selected))continue;
      counts.answered++;
      if(record.selected===q.key)counts.correct++;
      if(typeof record.firstCorrect==='boolean'){
        counts.firstTotal++;
        if(record.firstCorrect)counts.firstCorrect++;
      }
    }
    return counts;
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
  return {Timer,format,parse,answer,restoreAnswer,recordFirstFeedback,progress,score,gradable,compare};
})();
