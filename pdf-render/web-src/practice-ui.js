/* Practice controls use the same browser-memory contract as the reader. */
globalThis.AstraPracticeUI = function(context) {
  'use strict';
  const {$,$$,data,storage,prefix,prefs,persist,progress,remember,epoch,editEpoch}=context;
  const model=AstraPractice, paper=data.paper;
  let revealed=false,lastAuto=prefs().autoGrade;
  const feedbackVisible=()=>prefs().autoGrade||revealed;
  const banner=$('.reader-subbar');
  if(banner){
    const start=$('.reader-start',banner),nav=$('.section-nav',banner),actions=$('.reader-actions',banner);
    let frame;
    const fit=()=>{
      cancelAnimationFrame(frame);
      frame=requestAnimationFrame(()=>{
        // Keep the section links at the viewport center while the two sides
        // fit equally. Then compress by measured content, including counters.
        for(const layout of ['wide','labels','compact','stacked','wrap']){
          banner.dataset.layout=layout;
          const style=getComputedStyle(banner),space=banner.clientWidth-parseFloat(style.paddingLeft)-parseFloat(style.paddingRight);
          const left=start.getBoundingClientRect().width,right=actions.getBoundingClientRect().width;
          const sides=layout==='wide'||layout==='labels'?2*Math.max(left,right):left+right;
          if(sides+nav.getBoundingClientRect().width+2*parseFloat(style.columnGap)<=space+.5)break;
        }
      });
    };
    const observer=new ResizeObserver(fit);
    for(const node of [banner,start,nav,actions])observer.observe(node);
    document.fonts.ready.then(fit);
  }
  function showDialog(id){
    const dialog=$(id);if(!dialog||dialog.open)return;
    $('#settings').open=false;
    dialog.showModal();
  }
  for(const button of $$('[data-dialog-close]'))button.addEventListener('click',()=>button.closest('dialog').close());
  function refreshScore(){
    if(!paper)return;
    const score=model.score(data.questions,context.answers(),paper);
    const target=$('#score-sections');target.replaceChildren();
    for(const section of score.sections){
      const row=document.createElement('tr');
      const values=[section.label,section.score===null?'Unavailable':section.score+' / '+section.maximum,
        section.score===null?'—':section.correct+' correct · '+(section.answered-section.correct)+' wrong · '+(section.total-section.answered)+' unanswered',
        section.score===null?'':section.exact?'Verified historical weights':section.weighted?'Adjusted practice estimate':score.old?'Historical-scale estimate':'Practice estimate'];
      values.forEach((value,i)=>{const cell=document.createElement(i===0?'th':'td');if(i===0)cell.scope='row';cell.textContent=value;row.append(cell);});target.append(row);
    }
    $('#score-total').textContent=score.questions?'Written subtotal: '+score.total+' / '+score.maximum:'Written subtotal: Unavailable';
    $('#score-explanation').textContent=score.old?
      'Historical scores use vocabulary /100 and reading + grammar /200. Verified sections use the original question weights, normalized to the section maximum and rounded to the nearest whole number. Other sections estimate correct answers ÷ scored questions × the section maximum.':
      'Practice estimate: correct answers ÷ scored questions × the section maximum, rounded to the nearest whole number. This is a simple estimate, not the official JLPT scaled score.';
    $('#score-coverage').textContent=[
      score.excluded?score.excluded+' question'+(score.excluded===1?' is':'s are')+' excluded because the answer key is unconfirmed.':'',
      paper.partial?'This paper is partial; available questions are scored as a practice estimate.':''
    ].filter(Boolean).join(' ');
    const source=$('#score-source');source.replaceChildren();
    if(paper.scoring?.source_path){const link=document.createElement('a');link.href='../'+paper.scoring.source_path;link.target='_blank';link.rel='noopener';link.textContent='Original point-allocation tables ↗';source.append(link);}
    return score;
  }
  function grading(){
    const auto=prefs().autoGrade;
    if(auto!==lastAuto){revealed=false;lastAuto=auto;$('#score-dialog')?.close();}
    if(paper&&feedbackVisible()&&model.recordFirstFeedback(data.questions,context.answers()))context.saveAnswers();
    document.body.dataset.gradesHidden=String(!feedbackVisible());
    for(const row of $$('[data-color-row=neutral]'))row.hidden=auto;
    for(const button of $$('[data-grade]')){button.hidden=auto;button.textContent=revealed?'Hide grade':'Grade now';button.setAttribute('aria-pressed',String(revealed));}
    for(const live of $$('.answer-announcement'))live.textContent='';
    progress();
  }
  for(const input of $$('[name=auto-grade]'))input.addEventListener('change',()=>{prefs().autoGrade=input.value==='show';grading();persist();});
  for(const button of $$('[data-grade]'))button.addEventListener('click',()=>{revealed=!revealed;grading();if(revealed){refreshScore();showDialog('#score-dialog');}});

  const timerKey=paper?'timer:'+(paper.storage_unit||paper.unit)+(paper.variant==='norubi'?':norubi':''):null;
  const timer=paper?new model.Timer(remember()?storage.read(timerKey):null,paper.timer.seconds,model.clock(prefs()),prefs().timerDirection):null;
  let clockState=timer?JSON.stringify(timer.state):'',timerRevision=timer?.state.revision||0;
  let timerWake=0,displayedTime='',displayedLabel='',displayedRunning;
  const timerDisplay=timer?$('#timer-display'):null,timerBanner=timer?$('#timer-banner'):null;
  const pauseControls=timer?$$('[data-timer-action=pause]').map(button=>({button,text:$('.timer-action-label',button),icon:$('.timer-action-icon',button)})):[];
  const timerFields=timer?[['timer-limit',$('#timer-limit')],['timer-current',$('#timer-current')]]:[];
  function saveTimer(edited=false){
    if(!timer||!remember())return;
    if(edited)editEpoch();
    // An older background tab must not overwrite a newer pause/reset/edit.
    const existing=storage.read(timerKey);
    if(existing?.revision>timerRevision&&!edited){adoptTimer(existing);return;}
    timer.state.revision=timerRevision=Math.max(Date.now(),timerRevision+1);
    storage.savePaper(timerKey,{...timer.state},epoch());
  }
  function adoptTimer(record){
    if(record?.version!==1||record.revision<=timerRevision)return;
    const next=new model.Timer(record,paper.timer.seconds,model.clock(prefs()),prefs().timerDirection);
    timer.state=next.state;timerRevision=record.revision;
  }
  function renderTimer(){
    clearTimeout(timerWake);timerWake=0;
    if(!timer)return;
    timer.tick(model.clock(prefs()),prefs().timerDirection);
    // Timestamps keep time while hidden. Only visible, changing values need
    // DOM work; a paused/disabled timer has no recurring wake-up at all.
    if(document.hidden||!prefs().timerEnabled)return;
    const value=model.format(timer.seconds());
    if(value!==displayedTime){timerDisplay.textContent=value;displayedTime=value;}
    const description=(prefs().timerDirection==='up'?'Elapsed time: ':'Time remaining: ')+value+(timer.state.running?'':' (paused)');
    if(description!==displayedLabel){timerDisplay.setAttribute('aria-label',description);displayedLabel=description;}
    if(timer.state.running!==displayedRunning){
      displayedRunning=timer.state.running;timerBanner.dataset.paused=String(!displayedRunning);
      for(const {button,text,icon} of pauseControls){
        const label=displayedRunning?'pause':'resume';
        button.setAttribute('aria-label',label+' timer');button.title=label+' timer';
        if(text){text.textContent=label;icon.textContent=displayedRunning?'Ⅱ':'▶';}else button.textContent=label;
      }
    }
    for(const [id,field] of timerFields){
      const next=id==='timer-limit'?model.format(timer.state.limit/1000):value;
      if(document.activeElement!==field&&!field.dataset.dirty&&field.value!==next)field.value=next;
    }
    if(timer.state.expired&&!timer.state.notified&&prefs().timerEnabled&&prefs().timerDirection==='down'&&!document.hidden){
      timer.state.notified=true;saveTimer();showDialog('#time-up-dialog');
    }
    if(timer.state.running){
      const remainder=(prefs().timerDirection==='up'?timer.state.elapsed:timer.state.limit-timer.state.elapsed)%1000;
      const delay=prefs().timerDirection==='up'?1000-remainder:remainder||1000;
      timerWake=setTimeout(renderTimer,Math.max(16,Math.ceil(delay)));
    }
  }
  function timerAction(action){
    if(!timer)return;
    adoptTimer(remember()?storage.read(timerKey):null);
    const now=model.clock(prefs());
    timer.tick(now,prefs().timerDirection);
    if(action==='pause')timer.state.running?timer.pause(now):timer.resume(now);
    if(action==='reset')timer.reset(now);
    if(action==='exam')timer.setLimit(paper.timer.seconds,now);
    for(const field of $$('#timer-settings input[type=text]'))delete field.dataset.dirty;
    saveTimer(true);renderTimer();
    $('#timer-edit-status').textContent=action==='exam'?'Exam time limit restored.':action==='reset'?'Timer reset.':'';
  }
  for(const button of $$('[data-timer-action]'))button.addEventListener('click',()=>timerAction(button.dataset.timerAction));
  for(const name of ['limit','current']){
    $('#timer-'+name)?.addEventListener('input',e=>{e.target.dataset.dirty='true';e.target.setCustomValidity('');});
    $('#timer-'+name+'-form')?.addEventListener('submit',e=>{
      e.preventDefault();const field=$('#timer-'+name),seconds=model.parse(field.value);
      if(seconds===null||name==='limit'&&seconds===0){field.setCustomValidity('Enter hours:minutes:seconds'+(name==='limit'?' with a time limit greater than zero.':'.'));field.reportValidity();return;}
      adoptTimer(remember()?storage.read(timerKey):null);
      timer[name==='limit'?'setLimit':'setCurrent'](seconds,model.clock(prefs()));
      delete field.dataset.dirty;saveTimer(true);renderTimer();$('#timer-edit-status').textContent=(name==='limit'?'Time limit':'Current time')+' updated.';
    });
  }
  for(const input of $$('[name=timer-enabled]'))input.addEventListener('change',()=>{
    model.setEnabled(prefs(),input.value==='yes');persist();apply();saveTimer(true);
  });
  for(const [name,key]of[['timer-controls','timerControls'],['timer-direction','timerDirection']])for(const input of $$('[name='+name+']'))input.addEventListener('change',()=>{
    if(timer)timer.tick(model.clock(prefs()),prefs().timerDirection);
    prefs()[key]=name==='timer-controls'?input.value==='show':input.value;
    persist();apply();saveTimer(true);
  });
  function sortCatalog(){
    const select=$('#catalog-sort');if(!select)return;
    select.value=prefs().catalogSort;
    const cards=$$('.paper-grid>.paper-card');cards.sort((a,b)=>model.compare(a.dataset,b.dataset,select.value));
    for(const card of cards)card.parentElement.append(card);
    const note=$('#catalog-order-note');note.textContent=select.value==='recommended'?'Ordered with higher quality papers presented first.':select.value==='newest'?'Ordered from newest to oldest.':'Ordered from oldest to newest.';
  }
  $('#catalog-sort')?.addEventListener('change',e=>{prefs().catalogSort=e.target.value;sortCatalog();persist();});
  function apply(){
    for(const [name,value]of[['auto-grade',prefs().autoGrade?'show':'hide'],['timer-enabled',prefs().timerEnabled?'yes':'no'],['timer-controls',prefs().timerControls?'show':'hide'],['timer-direction',prefs().timerDirection]]){
      const input=$$('[name='+name+']').find(n=>n.value===value);if(input)input.checked=true;
    }
    if($('#timer-settings'))$('#timer-settings').hidden=!prefs().timerEnabled;
    if(timer){
      $('#timer-banner').hidden=!prefs().timerEnabled;
      $('#timer-banner-controls').hidden=!prefs().timerControls;
      renderTimer();
    }
    grading();sortCatalog();
  }
  if(timer){
    window.addEventListener('storage',e=>{if(e.key===prefix+timerKey&&remember()){adoptTimer(storage.read(timerKey));renderTimer();}});
    window.addEventListener('pagehide',()=>{clearTimeout(timerWake);timer.tick(model.clock(prefs()),prefs().timerDirection);saveTimer();});
    const wakeTimer=()=>{if(remember())adoptTimer(storage.read(timerKey));renderTimer();};
    window.addEventListener('focus',wakeTimer);
    window.addEventListener('pageshow',wakeTimer);
    document.addEventListener('visibilitychange',()=>{if(document.hidden){clearTimeout(timerWake);timerWake=0;}else wakeTimer();});
    if(clockState!==JSON.stringify(timer.state)||!storage.read(timerKey))saveTimer();
  }
  return {apply,refreshScore,get revealed(){return revealed;},get feedbackVisible(){return feedbackVisible();},save:()=>saveTimer(true)};
};
