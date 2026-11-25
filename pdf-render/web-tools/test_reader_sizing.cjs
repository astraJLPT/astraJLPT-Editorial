/* Policy regressions: readable columns, independent controls, and margin use. */
const assert=require('node:assert/strict');
require('../web-src/reader-sizing.js');
const S=globalThis.AstraReaderSizing,source=14.4433,margins=[102.0472,109.6063,128.5039,109.6063];
let checks=0;
function check(value){assert.ok(value);checks++;}
function near(a,b){check(Math.abs(a-b)<.001);}
const opening=46.4*96/72.27*.75;
const layout=(p,w,m=margins,top=opening)=>S.layout(p,w,m,top);
const column=p=>p.width-p.margins[1]-p.margins[3];
const frozen=p=>({zoom:p.zoom*100,zoomWidth:p.baseWidth,zoomMargins:p.baseMargins});
let previousColumn=0;
for(const available of [280,320,375,393,480,600,650,730,750,S.A4,850,900,1000,S.A4*1.4,1280,2560]){
  const page=layout({zoom:'auto'},available),text=S.autoText(available,source);
  check(page.width*page.zoom<=available+.001);
  check(page.zoom>=1&&page.zoom<=1.4);
  check(text>=1&&text<=17/source);
  // Making the window wider must not shrink the visible reading column.
  check(column(page)*page.zoom>=previousColumn-.001);previousColumn=column(page)*page.zoom;
  const manual=layout(frozen(page),available);
  near(column(manual),column(page));near(manual.width*manual.zoom,page.width*page.zoom);
  const smaller=layout({...frozen(page),zoom:page.zoom*100-1},available);
  check(smaller.width*smaller.zoom<manual.width*manual.zoom);
  for(const zoom of [25,100,140,175,500]){
    const fixed=layout({zoom},available);
    near(fixed.width,S.A4);
    near(column(fixed),S.A4-margins[1]-margins[3]);
    check(fixed.zoom===zoom/100);
    check(S.autoText(available,source)===text);
  }
}
for(const width of [525,730]){
  const page=layout({zoom:'auto'},width);
  near(page.margins[1]*page.zoom,14);near(page.margins[3]*page.zoom,14);
}
check(Math.round(S.autoText(375,source)*100)===118);
check(S.autoText(1280,source)===1&&S.autoText(2560,source)===1);
check(S.autoText(375,20)===1&&S.autoText(375,8)===1.8);
// Increasing zoom consumes blank sides before introducing horizontal scrolling.
const auto=layout({zoom:'auto'},1112),prefs=frozen(auto);
let lastMargin=Infinity,lastColumn=0;
for(const zoom of [140,141,150,175,190,200,500]){
  const page=layout({...prefs,zoom},1112),side=(page.margins[1]+page.margins[3])*page.zoom;
  near(column(page),column(auto));check(side<=lastMargin+.001);lastMargin=side;
  check(column(page)*page.zoom>lastColumn);lastColumn=column(page)*page.zoom;
  if(zoom<=175)check(page.width*page.zoom<=1112+.001);
  else{check(page.width*page.zoom>1112);near(side,28);}
}
// PDF shortcuts retain side/bottom margins; only the initial web inset differs.
for(const zoom of ['reference','fit']){
  const page=layout({...prefs,zoom},393);
  near(page.width,S.A4);near(page.margins[0],opening);
  check(page.margins.slice(1).every((v,i)=>v===margins[i+1]));
}
// Old saved Auto snapshots must not restore the large PDF top margin.
for(const zoom of ['auto','reference','fit',25,100,140,500])for(const top of [opening*.1,opening,opening*2]){
  const original=[...margins];
  const page=layout({zoom,zoomWidth:600,zoomMargins:[102,14,80,14]},1000,original,top);
  near(page.margins[0],top);near(page.baseMargins[0],top);
  assert.deepEqual(original,margins);checks++;
}
const narrow=layout({zoom:'auto'},375),saved={...frozen(narrow),zoom:125};
near(column(layout(saved,1280)),column(layout(saved,320)));
near(column(layout({zoom:100,zoomWidth:'invalid',zoomMargins:[Infinity,0,0,0]},393)),S.A4-margins[1]-margins[3]);
const asymmetric=[100,70,120,120],asymAuto=layout({zoom:'auto'},950,asymmetric);
near(column(layout({...frozen(asymAuto),zoom:150},950,asymmetric)),column(asymAuto));
for(const width of [S.A4*.6,S.A4*.65,S.A4, (S.A4-margins[1]-margins[3])*1.4+28,S.A4*1.4]){
  const a=layout({zoom:'auto'},width-.01),b=layout({zoom:'auto'},width+.01);
  check(Math.abs(a.width*a.zoom-b.width*b.zoom)<.03);
  check(Math.abs(column(a)*a.zoom-column(b)*b.zoom)<.03);
  check(Math.abs(S.autoText(width-.01,source)-S.autoText(width+.01,source))<.001);
}
console.log(JSON.stringify({checks,passed:checks}));
