/* Shared sizing policy. Inputs are CSS pixels, never device or browser IDs. */
(() => {
  'use strict';
  const A4=210*96/25.4;
  const AUTO_MAX=1.4,GUTTER=14;
  const clamp=(n,lo,hi)=>Math.min(hi,Math.max(lo,n));
  function transition(width,start,end){
    const t=clamp((width-start)/(end-start),0,1);
    return t*t*(3-2*t);
  }
  function autoText(available,sourcePx){
    const narrow=clamp(17/sourcePx,1,1.8);
    // Retain a readable narrow-screen starting size; reach source typography
    // when an A4 layout fits. Paper magnification is deliberately not an input.
    return narrow+(1-narrow)*transition(available,A4*.65,A4);
  }
  function margins(width,source,zoom=1){
    const t=transition(width,A4*.6,A4);
    const result=source.map((n,i)=>[24,GUTTER,30,GUTTER][i]+(n-[24,GUTTER,30,GUTTER][i])*t);
    // Give the reading column room first. Restore PDF side margins only as
    // the viewport can afford them, without narrowing the painted text column.
    const maxColumn=(A4-source[1]-source[3])*AUTO_MAX;
    const column=Math.min(Math.max(1,width*zoom-2*GUTTER),maxColumn);
    const spare=Math.max(0,width-column/zoom),total=source[1]+source[3];
    result[1]=spare*(total?source[1]/total:.5);
    result[3]=spare-result[1];
    return result;
  }
  function layout(preferences,available,source,openingTop=source[0]){
    const space=Math.max(1,available);
    let baseWidth=A4,zoom=1,baseMargins=[...source],trim=false;
    if(preferences.zoom==='auto'){
      baseWidth=Math.min(A4,space);
      zoom=clamp(space/A4,1,AUTO_MAX);
      baseMargins=margins(baseWidth,source,zoom);
    }else if(preferences.zoom==='fit')zoom=space/A4;
    else if(preferences.zoom!=='reference'){
      zoom=clamp(Number(preferences.zoom)/100||1,.01,10);
      const frozen=preferences.zoomWidth;
      if(typeof frozen==='number'&&Number.isFinite(frozen)){
        trim=true;
        baseWidth=clamp(frozen,1,A4);
        baseMargins=baseWidth<A4?margins(baseWidth,source):[...source];
        const saved=preferences.zoomMargins;
        if(Array.isArray(saved)&&saved.length===4&&saved.every(n=>typeof n==='number'&&Number.isFinite(n)&&n>=0)&&saved[1]+saved[3]<baseWidth)baseMargins=[...saved];
      }
    }
    // CSS supplies the current section-sized opening inset after Text size
    // and block spacing resolve. Old detached snapshots must not freeze it.
    baseMargins[0]=openingTop;
    const padding=[...baseMargins];
    let width=baseWidth;
    if(trim){
      // Trim blank sides and the paper width by the same amount. The content
      // column and its line breaks stay unchanged while magnification grows.
      const left=Math.max(0,padding[3]-GUTTER/zoom),right=Math.max(0,padding[1]-GUTTER/zoom);
      const capacity=left+right,cut=Math.min(Math.max(0,baseWidth-space/zoom),capacity);
      if(capacity){padding[3]-=cut*left/capacity;padding[1]-=cut*right/capacity;width-=cut;}
    }
    const responsive=baseWidth<A4-.01||Math.abs(baseMargins[1]-source[1])>.01||Math.abs(baseMargins[3]-source[3])>.01;
    return {width,baseWidth,zoom,margins:padding,baseMargins,responsive};
  }
  globalThis.AstraReaderSizing=Object.freeze({A4,AUTO_MAX,GUTTER,autoText,layout,margins});
})();
