/* Color math shared by the editor and its non-browser regression checks. */
globalThis.AstraThemeColors = (() => {
  'use strict';
  function normalize(value, alpha=true) {
    if(typeof value!=='string'||!/^#(?:[\da-f]{3}|[\da-f]{4}|[\da-f]{6}|[\da-f]{8})$/i.test(value.trim()))return null;
    let h=value.trim().slice(1).toLowerCase();
    if(h.length<5)h=[...h].map(c=>c+c).join('');
    if(!alpha&&h.length===8&&h.slice(6)!=='ff')return null;
    return '#'+(h.endsWith('ff')&&h.length===8?h.slice(0,6):h);
  }
  function rgba(value) {
    const h=normalize(value).slice(1);
    return [0,2,4].map(i=>parseInt(h.slice(i,i+2),16)).concat(h.length===8?parseInt(h.slice(6),16)/255:1);
  }
  const byte=v=>Math.max(0,Math.min(255,Math.round(v))).toString(16).padStart(2,'0');
  const hex=c=>'#'+c.slice(0,3).map(byte).join('')+(c[3]<1?byte(c[3]*255):'');
  const css=c=>`rgba(${c[0]}, ${c[1]}, ${c[2]}, ${c[3]})`;
  function resolve(theme, mode, overrides, roles, fills={}) {
    const source={...theme.editorColors[mode]};
    for(const role of roles){
      if(role.formula){
        const opacity=fills[role.fillControl];
        source[role.id]=role.fillControl&&validOpacity(opacity)?role.formula.replace(/[\d.]+%/,opacity+'%'):role.formula;
      }
      if(role.editable&&Object.hasOwn(overrides||{},role.id)){
        const value=normalize(overrides[role.id],role.alpha);
        if(value)source[role.id]=value;
      }
    }
    const resolved={},active=new Set();
    function expression(value) {
      if(value==='transparent')return [0,0,0,0];
      if(normalize(value))return rgba(value);
      const ref=/^var\(--([\w-]+)\)$/.exec(value);
      if(ref)return color(ref[1]);
      const mix=/^color-mix\(in srgb,\s*(var\(--[\w-]+\)|#[\da-f]+)\s+([\d.]+)%,\s*(transparent|var\(--[\w-]+\)|#[\da-f]+)\)$/i.exec(value);
      if(!mix)throw new Error('Unsupported theme color: '+value);
      const a=expression(mix[1]),b=expression(mix[3]),w=Number(mix[2])/100;
      const opacity=a[3]*w+b[3]*(1-w);
      return a.slice(0,3).map((v,i)=>opacity?(v*a[3]*w+b[i]*b[3]*(1-w))/opacity:0).concat(opacity);
    }
    function color(id) {
      if(resolved[id])return resolved[id];
      if(active.has(id))throw new Error('Cyclic color: '+id);
      active.add(id);resolved[id]=expression(source[id]);active.delete(id);return resolved[id];
    }
    for(const role of roles)color(role.id);
    return resolved;
  }
  function sanitize(value,themes,roles) {
    const result={};
    if(!value||typeof value!=='object'||Array.isArray(value))return result;
    for(const theme of themes){
      const incoming=Object.hasOwn(value,theme.id)?value[theme.id]:null;
      if(!incoming||typeof incoming!=='object'||Array.isArray(incoming))continue;
      const colors={};
      for(const role of roles){
        if(!role.editable)continue;
        const color=Object.hasOwn(incoming,role.id)?normalize(incoming[role.id],role.alpha):null;
        if(color)colors[role.id]=color;
      }
      if(Object.keys(colors).length)result[theme.id]=colors;
    }
    return result;
  }
  function validOpacity(value){return typeof value==='number'&&Number.isFinite(value)&&value>=0&&value<=100;}
  function sanitizeFills(value,themes,controls){
    const result={};
    if(!value||typeof value!=='object'||Array.isArray(value))return result;
    for(const theme of themes){
      const incoming=Object.hasOwn(value,theme.id)?value[theme.id]:null;
      if(!incoming||typeof incoming!=='object'||Array.isArray(incoming))continue;
      const fills={};
      for(const control of controls){
        const v=Object.hasOwn(incoming,control.id)?incoming[control.id]:null;
        if(validOpacity(v)&&Math.round(v)!==control.default)fills[control.id]=Math.round(v);
      }
      if(Object.keys(fills).length)result[theme.id]=fills;
    }
    return result;
  }
  return {normalize,rgba,hex,css,resolve,sanitize,sanitizeFills};
})();
