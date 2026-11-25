/* Practice controls use the same browser-memory contract as the reader. */
globalThis.AstraPracticeUI = function(context) {
  'use strict';
  const {$,$$,data,storage,prefix,prefs,persist,progress,remember,epoch}=context;
  const model=AstraPractice, paper=data.paper;
  let revealed=false,lastAuto=prefs().autoGrade;
  const feedbackVisible=()=>prefs().autoGrade||revealed;
  const banner=$('.reader-subbar');
  let fitBanner;
  if(banner){
    const start=$('.reader-start',banner),nav=$('.section-nav',banner),actions=$('.reader-actions',banner);
    let frame=0;
    const usedWidth=()=>{
      const style=getComputedStyle(banner);
      return start.getBoundingClientRect().width+nav.getBoundingClientRect().width+actions.getBoundingClientRect().width
        +parseFloat(style.paddingLeft)+parseFloat(style.paddingRight)+2*parseFloat(style.columnGap);
    };
    fitBanner=()=>{
      if(frame)return;
      frame=requestAnimationFrame(()=>{
        frame=0;
        const width=banner.clientWidth;
        banner.dataset.layout='full';
        banner.style.removeProperty('--banner-extra-gap');
        const roomy=usedWidth();
        if(roomy<=width)return;
        banner.style.setProperty('--banner-extra-gap','0px');
        const tight=usedWidth();
        if(tight<=width){
          // Distribute only the spare space back to the group and section gaps.
          banner.style.setProperty('--banner-extra-gap',(16*(width-tight)/(roomy-tight))+'px');
          return;
        }
        for(const layout of ['two-lines','timer-icons','top-icon','settings-icon','stacked']){
          banner.dataset.layout=layout;
          if(usedWidth()<=width)return;
        }
        banner.dataset.layout='overflow';
      });
    };
    const observer=new ResizeObserver(fitBanner);
    for(const node of [banner,start,nav,actions])observer.observe(node);
    document.fonts.ready.then(fitBanner);
  }
  function showDialog(id){
    const dialog=$(id);if(!dialog||dialog.open)return;
    $('#settings').open=false;
    dialog.showModal();
  }
  // These controls require scripting. Share their markup across both editions
  // and initialize it against the same anchors in previously cached readers.
  function timeUsed(id){
    return 'Time used: <span class="time-used-value" id="'+id+'"></span>';
  }
  // The level chooser has a generic example. A cached level with no metadata can still describe the paper limit.
  const seconds=paper?.timer.seconds??data.catalog_timer_seconds??($('main.catalog')?null:110*60);
  const limit=Number.isFinite(seconds)?model.format(seconds):'paper limit';
  const from=paper?'from ':'';
  $('[name=timer-enabled][value=yes]+span')?.insertAdjacentHTML('beforeend',
    '<small><b class="clock-preview" id="timer-limit-preview">'+limit+'</b></small>');
  $('[name=timer-direction][value=down]+span')?.insertAdjacentHTML('beforeend',
    '<small>'+from+'<b class="clock-preview" id="countdown-from">'+limit+'</b></small>');
  $('[name=timer-direction][value=up]+span')?.insertAdjacentHTML('beforeend',
    '<small>'+from+'<b class="clock-preview">0:00:00</b></small>');
  $('[name=timer-controls][value=show]+span')?.insertAdjacentHTML('beforeend',
    '<small class="timer-controls-preview" aria-hidden="true"><b><i>Ⅱ</i> pause</b> <b><i>↺</i> reset</b></small>');
  $('#timer-settings')?.insertAdjacentHTML('beforeend',
    `<div class="setting-row"><div><h3>↺ reset warning</h3><p>Shows the "are you sure?" screen when you click ↺ reset timer</p></div>
    <div class="segmented" role="group" aria-label="reset warning">
    <label><input type="radio" name="timer-reset-warning" value="show" checked><span>show<small>display warning first</small></span></label>
    <label><input type="radio" name="timer-reset-warning" value="hide"><span>hide<small>immediately ↺ reset</small></span></label></div></div>`);
  const scoreDialog=paper?$('#score-dialog'):null;
  if(paper){
    $('[name=star-behavior]').closest('.setting-row').insertAdjacentHTML('beforebegin',
      `<div class="setting-row"><div><h3>unclick answer</h3><p>Clear an answer to leave the question unanswered and reset its first try.</p></div>
      <div class="segmented grade-behavior" role="group" aria-label="unclick answer">
      <label><input type="radio" name="unclick-answer" value="allow" checked><span>allow<small><b class="unclick-click">click</b> again to <b class="unclick-clear">unclick</b></small></span></label>
      <label><input type="radio" name="unclick-answer" value="disable"><span>disable<small>don't allow unclick</small></span></label></div></div>`);
    $('[data-settings=marking]').insertAdjacentHTML('beforeend',
      `<div class="setting-row"><div><h3>auto-spoil</h3><p>(Not recommended) shows the correct answer even when you choose the wrong answer. you shouldn't use this; just try again if you get a question wrong.</p></div>
      <div class="segmented grade-behavior" role="group" aria-label="auto-spoil">
      <label><input type="radio" name="auto-spoil" value="no" checked><span>don't<small aria-hidden="true"><b class="wrong-badge">✕</b> ⟶ try again</small></span></label>
      <label><input type="radio" name="auto-spoil" value="yes"><span>spoil<small aria-hidden="true"><b class="wrong-badge">✕</b> ⟶ <b>✓</b></small></span></label></div></div>
      <div class="setting-row"><div><h3>spoil all</h3><p>(Not recommended) crRAshiNg oUT? no problem! why solve the exam if you can get it to automatically fill in all the correct answers for you!</p></div>
      <div class="segmented grade-behavior" role="group" aria-label="spoil all">
      <label><input type="radio" name="spoil-all" value="no" checked><span>don't</span></label>
      <label><input type="radio" name="spoil-all" value="yes"><span>spoil<small aria-hidden="true"><i class="paper-button-sample">spoil all</i></small></span></label></div></div>
      <div class="setting-row"><div><h3>clear/spoil warning</h3><p>Shows the "are you sure?" screen when you click Clear answers or spoil all.</p></div>
      <div class="segmented grade-behavior" role="group" aria-label="clear/spoil warning">
      <label><input type="radio" name="clear-spoil-warning" value="show" checked><span>show<small>display warning first</small></span></label>
      <label><input type="radio" name="clear-spoil-warning" value="hide"><span>hide<small>clear or spoil immediately</small></span></label></div></div>`);
    const spoilButton='<button type="button" data-paper-action="spoil" hidden>spoil all</button>';
    $('[data-practice=top]').insertAdjacentHTML('afterbegin',spoilButton);
    $('[data-practice=top]').insertAdjacentHTML('beforeend','<button type="button" data-paper-action="clear" hidden>Clear answers</button>');
    $('#clear-answers').insertAdjacentHTML('beforebegin',spoilButton);
    $('#score-total').insertAdjacentHTML('afterend',
      '<p id="score-timing">'+timeUsed('score-time')+'<span id="score-warning" hidden></span></p>');
    scoreDialog.insertAdjacentHTML('afterend',
      `<dialog id="timer-frozen-dialog" class="practice-dialog" aria-labelledby="timer-frozen-title" aria-describedby="timer-frozen-timing timer-frozen-description"><h2 id="timer-frozen-title">Timer frozen</h2><p id="timer-frozen-timing">${timeUsed('timer-frozen-time')}</p><p id="timer-frozen-description">You have attempted every question in the paper, your timer has been frozen.</p><button type="button" data-dialog-close autofocus>Close</button></dialog>
      <dialog id="timer-reset-dialog" class="practice-dialog practice-confirm" aria-labelledby="timer-reset-title" aria-describedby="timer-reset-description"><h2 id="timer-reset-title">are you sure?</h2><p id="timer-reset-description"></p>
      <label class="reset-warning-choice"><input id="timer-reset-skip" type="checkbox"> Don't show warning again</label>
      <div class="button-row"><button type="button" class="warning-cancel" data-dialog-close autofocus>cancel</button><button type="button" class="warning-confirm" id="confirm-timer-reset">reset timer</button></div></dialog>
      <dialog id="paper-action-dialog" class="practice-dialog practice-confirm" aria-labelledby="paper-action-title" aria-describedby="paper-action-description"><h2 id="paper-action-title">are you sure?</h2>
      <div class="table-flip" aria-hidden="true"><span>(╯°□°)╯︵ ┻━┻</span><span>┬─┬ノ( º _ ºノ)</span></div>
      <p id="paper-action-description"></p>
      <label class="reset-warning-choice"><input id="paper-action-skip" type="checkbox"> Don't show warning again</label>
      <div class="button-row"><button type="button" class="warning-cancel" id="cancel-paper-action" autofocus></button><button type="button" class="warning-confirm" id="confirm-paper-action"></button></div></dialog>`);
  }
  for(const button of $$('[data-dialog-close]'))button.addEventListener('click',()=>button.closest('dialog').close());
  let unanswered=0;
  const scoreTime=paper?$('#score-time'):null,scoreWarning=paper?$('#score-warning'):null;
  const frozenDialog=paper?$('#timer-frozen-dialog'):null,frozenTime=paper?$('#timer-frozen-time'):null;
  const resetDialog=paper?$('#timer-reset-dialog'):null,skipWarning=paper?$('#timer-reset-skip'):null;
  const actionDialog=paper?$('#paper-action-dialog'):null;
  const confirmations=paper?$$('dialog.practice-confirm'):[];
  const optionalActions=paper?$$('[data-paper-action]'):[];
  const limitPreview=$('#timer-limit-preview'),countdownFrom=$('#countdown-from');
  let cancelDelay;
  for(const button of [...optionalActions,...$$('#clear-answers')])button.addEventListener('click',()=>{
    const action=button.dataset.paperAction||'clear';
    context.syncPaper();
    if(action==='clear'&&!Object.keys(context.answers()).length)return;
    if(prefs().clearSpoilWarning===false){context.applyPaperAction(action);return;}
    clearTimeout(cancelDelay);
    const spoil=action==='spoil';
    actionDialog.dataset.action=action;
    delete actionDialog.dataset.restored;
    $('#paper-action-skip').checked=false;
    $('#paper-action-description').textContent=spoil?'this will automatically fill all the correct answers for you!':"Clear this paper's answers and practice counts?";
    $('#cancel-paper-action').textContent=spoil?'cancel':'Cancel';
    $('#confirm-paper-action').textContent=spoil?'spoil all':'Clear';
    button.focus({preventScroll:true});
    actionDialog.showModal();
  });
  $('#cancel-paper-action')?.addEventListener('click',()=>{
    if(!actionDialog.open||actionDialog.dataset.restored)return;
    if(actionDialog.dataset.action==='spoil'){
      actionDialog.dataset.restored='true';
      cancelDelay=setTimeout(()=>actionDialog.close(),200);
    }else actionDialog.close();
  });
  $('#confirm-paper-action')?.addEventListener('click',()=>{
    if(!actionDialog.open||actionDialog.dataset.restored)return;
    if($('#paper-action-skip').checked){
      prefs().clearSpoilWarning=false;
      $('[name=clear-spoil-warning][value=hide]').checked=true;
      persist();
    }
    context.applyPaperAction(actionDialog.dataset.action);
    actionDialog.close();
  });
  function renderTimeUsed(node){
    const elapsed=Math.floor(timer.state.elapsed/1000),limit=timer.state.limit/1000;
    const value=model.format(elapsed)+' / '+model.format(limit),overtime=elapsed>limit;
    if(node.textContent!==value)node.textContent=value;
    if(node.dataset.overtime!==String(overtime))node.dataset.overtime=String(overtime);
    return overtime;
  }
  function renderScoreTime(){
    const overtime=renderTimeUsed(scoreTime);
    if(scoreWarning.hidden!==(unanswered===0))scoreWarning.hidden=unanswered===0;
    if(!unanswered)return;
    let status='The timer is still running down.';
    if(!timer.advancing)status='The timer is paused.';
    else if(overtime)status='Time used is still being recorded in overtime.';
    else if(timer.state.direction==='up')status='The timer is still counting up.';
    else if(timer.expired)status='The countdown has reached zero.';
    const warning='Warning: '+unanswered+' unanswered question'+(unanswered===1?'':'s')+'. '+status;
    if(scoreWarning.textContent!==warning)scoreWarning.textContent=warning;
  }
  function refreshScore(){
    if(!paper)return;
    const score=model.score(data.questions,context.answers(),paper);
    const target=$('#score-sections');target.replaceChildren();
    for(const section of score.sections){
      const row=document.createElement('tr');
      const label=document.createElement('th'),points=document.createElement('td'),answers=document.createElement('td'),method=document.createElement('td');
      label.scope='row';label.textContent=section.label;
      if(section.score===null){points.textContent='Unavailable';answers.textContent='—';}
      else{
        points.textContent=section.score+' / '+section.maximum;
        const correct=document.createElement('span'),wrong=document.createElement('span');
        correct.className='score-correct';correct.textContent=section.correct+' correct';
        wrong.className='score-wrong';wrong.textContent=(section.answered-section.correct)+' wrong';
        answers.append(correct,' · ',wrong,' · '+(section.total-section.answered)+' unanswered');
        method.textContent=section.exact?'Verified historical weights':section.weighted?'Adjusted practice estimate':score.old?'Historical-scale estimate':'Practice estimate';
      }
      row.append(label,points,answers,method);target.append(row);
    }
    $('#score-total').textContent=score.questions?'Written subtotal: '+score.total+' / '+score.maximum:'Written subtotal: Unavailable';
    unanswered=score.questions-score.answered;
    timer.tick(Date.now(),prefs().timerDirection);renderScoreTime();
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
    if(paper&&feedbackVisible()){
      context.syncPaper();
      if(model.recordFirstFeedback(data.questions,context.answers()))context.saveAnswers();
    }
    document.body.dataset.gradesHidden=String(!feedbackVisible());
    for(const row of $$('[data-color-row=neutral]'))row.hidden=auto;
    for(const button of $$('[data-grade]')){button.hidden=auto;button.textContent=revealed?'Hide grade':'Grade now';button.setAttribute('aria-pressed',String(revealed));}
    for(const live of $$('.answer-announcement'))live.textContent='';
    progress();
  }
  for(const input of $$('[name=auto-grade]'))input.addEventListener('change',()=>{prefs().autoGrade=input.value==='show';grading();persist();});
  for(const input of $$('[name=unclick-answer]'))input.addEventListener('change',()=>{prefs().allowUnclick=input.value==='allow';persist();});
  for(const button of $$('[data-grade]'))button.addEventListener('click',()=>{revealed=!revealed;grading();if(revealed){refreshScore();showDialog('#score-dialog');renderTimer();}});

  const timerRecord=storage.openPractice('timer',paper,remember(),epoch);
  function paperComplete(){
    const counts=model.progress(data.questions,context.answers());
    return counts.total>0&&counts.answered===counts.total;
  }
  function readTimer(record,frozen){
    return new model.Timer(record,paper.timer.seconds,Date.now(),prefs().timerDirection,frozen,prefs().timerDisabledTotal||0);
  }
  const savedTimer=timerRecord&&remember()?timerRecord.read():null;
  let timer=paper?readTimer(savedTimer,paperComplete()):null;
  let timerRevision=timer?.state.revision||0;
  let timerWake=0,displayedTime='',displayedLabel='',displayedRunning;
  const timerDisplay=timer?$('#timer-display'):null,timerBanner=timer?$('#timer-banner'):null;
  const pauseControls=timer?$$('[data-timer-action=pause]').map(button=>({button,text:$('.timer-action-label',button),icon:$('.timer-action-icon',button)})):[];
  const timerFields=timer?[['timer-limit',$('#timer-limit')],['timer-current',$('#timer-current')]]:[];
  function saveTimer(edited=false){
    if(!timer||!remember())return;
    // An older background tab must not overwrite a newer pause/reset/edit.
    const existing=timerRecord.read();
    const revision=Number.isFinite(existing?.revision)?existing.revision:0;
    if(existing?.version===2&&revision>timerRevision&&!edited){adoptTimer(existing);return;}
    timer.state.revision=timerRevision=Math.max(Date.now(),timerRevision+1,revision+1);
    timerRecord.save(timer.state,epoch(),()=>timer.legacyRecord(prefs().timerDisabledTotal||0));
  }
  function adoptTimer(record){
    if(record?.version!==2||!Number.isFinite(record.revision)||record.revision<=timerRevision)return;
    timer=readTimer(record,record.frozen);timerRevision=record.revision;
  }
  function restoreTimer(){
    if(!paper)return;
    timer=readTimer(timerRecord.read(),paperComplete());
    timerRevision=timer.state.revision;
    renderTimer();
  }
  function setComplete(frozen,now=Date.now()){
    if(!timer||timer.state.frozen===frozen)return;
    if(remember())adoptTimer(timerRecord.read());
    if(timer.state.frozen!==frozen){
      timer.setFrozen(frozen,now);
      saveTimer();
    }
    renderTimer();
  }
  function renderBanner(){
    const value=model.format(timer.seconds());
    if(value!==displayedTime){timerDisplay.textContent=value;displayedTime=value;}
    const description=(prefs().timerDirection==='up'?'Elapsed time: ':'Time remaining: ')+value+(timer.state.frozen?' (frozen)':timer.advancing?'':' (paused)');
    if(description!==displayedLabel){timerDisplay.setAttribute('aria-label',description);displayedLabel=description;}
    if(timer.advancing!==displayedRunning){
      displayedRunning=timer.advancing;timerBanner.dataset.paused=String(!displayedRunning);
      for(const {button,text,icon} of pauseControls){
        const label=displayedRunning?'pause':'resume';
        button.setAttribute('aria-label',label+' timer');button.title=label+' timer';
        if(text){text.textContent=label;icon.textContent=displayedRunning?'Ⅱ':'▶';}else button.textContent=label;
      }
      fitBanner?.();
    }
    for(const [id,field] of timerFields){
      const next=id==='timer-limit'?model.format(timer.state.limit/1000):value;
      if(document.activeElement!==field&&!field.dataset.dirty&&field.value!==next)field.value=next;
    }
    if(timer.expired&&!timer.state.notified&&!timer.state.frozen&&!confirmations.some(dialog=>dialog.open)){
      timer.state.notified=true;saveTimer();showDialog('#time-up-dialog');
    }
  }
  function renderTimer(){
    clearTimeout(timerWake);timerWake=0;
    if(!timer)return;
    timer.tick(Date.now(),prefs().timerDirection);
    if(document.hidden)return;
    const limit=model.format(timer.state.limit/1000);
    if(limitPreview&&limitPreview.textContent!==limit)limitPreview.textContent=limit;
    if(countdownFrom&&countdownFrom.textContent!==limit)countdownFrom.textContent=limit;
    if(prefs().timerEnabled)renderBanner();
    if(scoreDialog.open)renderScoreTime();
    if(frozenDialog.open){
      if(timer.state.frozen)renderTimeUsed(frozenTime);else frozenDialog.close();
    }
    if(resetDialog.open)renderResetDescription();
    // Elapsed time comes from timestamps. A hidden timer and a countdown at
    // zero need no wakeups unless someone is actually watching the report.
    if(timer.advancing&&(scoreDialog.open||(prefs().timerEnabled&&!timer.expired))){
      timerWake=setTimeout(renderTimer,Math.max(16,1000-timer.state.elapsed%1000));
    }
  }
  function timerAction(action){
    if(!timer)return;
    context.syncPaper();
    adoptTimer(remember()?timerRecord.read():null);
    if(action==='pause'&&timer.state.frozen){renderTimeUsed(frozenTime);showDialog('#timer-frozen-dialog');return;}
    const now=Date.now();
    timer.tick(now,prefs().timerDirection);
    if(action==='pause')timer.state.running?timer.pause(now):timer.resume(now);
    if(action==='reset')timer.reset(now);
    if(action==='exam')timer.setLimit(paper.timer.seconds,now);
    for(const [,field] of timerFields){
      delete field.dataset.dirty;
      field.setCustomValidity('');
    }
    saveTimer(true);renderTimer();
    $('#timer-edit-status').textContent=action==='exam'?'Exam time limit restored.':action==='reset'?'Timer reset.':'';
  }
  function renderResetDescription(){
    const description=$('#timer-reset-description'),text=prefs().timerDirection==='up'?
      'this will reset your elapsed time to 0.':'this will reset the timer back to the time limit for this paper. your elapsed time will reset to 0.';
    if(description.textContent!==text)description.textContent=text;
  }
  for(const button of $$('[data-timer-action]'))button.addEventListener('click',()=>{
    const action=button.dataset.timerAction;
    if(action==='reset'&&prefs().timerResetWarning!==false){
      if(!resetDialog.open){
        skipWarning.checked=false;renderResetDescription();
        // WebKit pointer clicks can leave focus on an earlier control. The
        // dialog restores the focused element when it closes.
        button.focus({preventScroll:true});
        resetDialog.showModal();
      }
    }else timerAction(action);
  });
  $('#confirm-timer-reset')?.addEventListener('click',()=>{
    if(skipWarning.checked){
      prefs().timerResetWarning=false;
      $('[name=timer-reset-warning][value=hide]').checked=true;
      persist();
    }
    timerAction('reset');resetDialog.close();
  });
  for(const name of ['limit','current']){
    $('#timer-'+name)?.addEventListener('input',e=>{e.target.dataset.dirty='true';e.target.setCustomValidity('');});
    $('#timer-'+name+'-form')?.addEventListener('submit',e=>{
      e.preventDefault();const field=$('#timer-'+name),seconds=model.parse(field.value);
      if(seconds===null||name==='limit'&&seconds===0){field.setCustomValidity('Enter hours:minutes:seconds'+(name==='limit'?' with a time limit greater than zero.':'.'));field.reportValidity();return;}
      context.syncPaper();
      adoptTimer(remember()?timerRecord.read():null);
      timer[name==='limit'?'setLimit':'setCurrent'](seconds,Date.now());
      delete field.dataset.dirty;saveTimer(true);renderTimer();$('#timer-edit-status').textContent=(name==='limit'?'Time limit':'Current time')+' updated.';
    });
  }
  for(const input of $$('[name=timer-enabled]'))input.addEventListener('change',()=>{
    prefs().timerEnabled=input.value==='yes';persist();apply();
  });
  for(const [name,key]of[['timer-controls','bannerTimerControls'],['timer-reset-warning','timerResetWarning'],['clear-spoil-warning','clearSpoilWarning']])for(const input of $$('[name='+name+']'))input.addEventListener('change',()=>{
    if(input.value==='hide')prefs()[key]=false;else delete prefs()[key];
    persist();apply();
  });
  for(const [name,key]of[['auto-spoil','autoSpoil'],['spoil-all','spoilAll']])for(const input of $$('[name='+name+']'))input.addEventListener('change',()=>{
    if(input.value==='yes')prefs()[key]=true;else delete prefs()[key];
    persist();apply();
  });
  for(const input of $$('[name=timer-direction]'))input.addEventListener('change',()=>{
    if(timer)timer.tick(Date.now(),prefs().timerDirection);
    prefs().timerDirection=input.value;
    persist();apply();
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
    const showControls=prefs().bannerTimerControls!==false;
    const choices=[
      ['auto-grade',prefs().autoGrade?'show':'hide'],
      ['unclick-answer',prefs().allowUnclick?'allow':'disable'],
      ['auto-spoil',prefs().autoSpoil?'yes':'no'],
      ['spoil-all',prefs().spoilAll?'yes':'no'],
      ['clear-spoil-warning',prefs().clearSpoilWarning===false?'hide':'show'],
      ['timer-enabled',prefs().timerEnabled?'yes':'no'],
      ['timer-controls',showControls?'show':'hide'],
      ['timer-reset-warning',prefs().timerResetWarning===false?'hide':'show'],
      ['timer-direction',prefs().timerDirection]
    ];
    for(const [name,value] of choices){
      const input=$$('[name='+name+']').find(n=>n.value===value);if(input)input.checked=true;
    }
    if($('#timer-settings'))$('#timer-settings').hidden=!prefs().timerEnabled;
    if(timer){
      document.body.dataset.autoSpoil=String(prefs().autoSpoil===true);
      context.applyAutoSpoil();
      for(const button of optionalActions)button.hidden=!prefs().spoilAll;
      if(actionDialog.open&&actionDialog.dataset.action==='spoil'&&!prefs().spoilAll)actionDialog.close();
      $('#timer-banner').hidden=!prefs().timerEnabled;
      $('#timer-banner-controls').hidden=!showControls;
      renderTimer();
    }
    grading();sortCatalog();
  }
  if(timer){
    scoreDialog.addEventListener('close',renderTimer);
    for(const dialog of confirmations)dialog.addEventListener('close',renderTimer);
    window.addEventListener('storage',e=>{if(e.key===prefix+timerRecord.key&&remember()){adoptTimer(timerRecord.read());renderTimer();}});
    window.addEventListener('pagehide',()=>{clearTimeout(timerWake);timer.tick(Date.now(),prefs().timerDirection);saveTimer();});
    const wakeTimer=()=>{
      if(remember()){adoptTimer(timerRecord.read());context.syncPaper();}
      renderTimer();
    };
    window.addEventListener('focus',wakeTimer);
    window.addEventListener('pageshow',wakeTimer);
    document.addEventListener('visibilitychange',()=>{if(document.hidden){clearTimeout(timerWake);timerWake=0;}else wakeTimer();});
    if(![1,2].includes(savedTimer?.version)||savedTimer.frozen!==timer.state.frozen)saveTimer();
  }
  return {apply,refreshScore,setComplete,restoreTimer,get revealed(){return revealed;},get feedbackVisible(){return feedbackVisible();},save:()=>saveTimer(true)};
};
