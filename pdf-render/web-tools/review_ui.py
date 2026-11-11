"""Human-readable views of the existing registers. Never writes audit data."""
import difflib
import html
import json
from collections import defaultdict
from public_paths import html_path

def esc(value):return html.escape(str(value),quote=True)
def value_text(value):
    if value is None:return 'Not recorded'
    if isinstance(value,dict) and 'html'in value:return value['html']
    return value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2)

def comparison(before,after):
    a,b=value_text(before),value_text(after); ops=difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes()
    changed=[op for op in ops if op[0]!='equal'];first=changed[0] if changed else ('equal',0,120,0,120)
    def excerpt(old):
        text=a if old else b;begin=max(0,first[1 if old else 3]-90);end=min(len(text),first[2 if old else 4]+140)
        out='…' if begin else ''
        for kind,i,j,k,l in ops:
            start,stop=(i,j) if old else (k,l);s=esc(text[max(begin,start):min(end,stop)]) if min(end,stop)>max(begin,start) else ''
            out+=f'<mark class="diff-{"old"if old else"new"}">{s}</mark>' if kind!='equal' and s else s
        return out+('…' if end<len(text) else '')
    return excerpt(True),excerpt(False)

def registers(m,registers,principal,decorate,source_links=None):
    source_links=source_links or {}
    by_item=defaultdict(list);mapping={};order=[];allitems={}
    for section in m['document']['sections']:
        order.append(section['id']);allitems[section['id']]=section
        for item in section['items']:order.append(item['id']);allitems[item['id']]=item
    for kind,rows in registers.items():
        for row in rows:by_item[row.get('item_id')].append((kind,row))
    groups=[]
    for target in sorted(by_item,key=lambda k:order.index(k) if k in order else -1):
        rows=by_item[target];anchor='review-'+(target or 'coverage');mapping[target]=anchor
        flags=set();blocks=[]
        for kind,row in rows:
            difference=kind=='principal_differences';status='difference' if difference else row.get('status','unresolved');flags.add(status)
            rid=kind+'-'+row.get('difference_id',row.get('case_id'));p=row.get('principal',{});old=p.get('reading') if difference else row.get('before');new=row.get('editorial_reading') if difference else row.get('current_value')
            old_label='Principal' if difference else 'Before'
            if not difference and old is None:
                old_label='Alternative'
                old=next((a['value'] for a in row.get('alternatives',[]) if 'value'in a),None)
            left,right=comparison(old,new);label='Principal difference' if difference else status.replace('_',' ').capitalize()
            if old is None:left='No alternative recorded';right=esc(value_text(new))
            where=p.get('locator',row.get('context',''));pages=p.get('physical_pages',[])
            selected=source_links.get(p.get('witness_id'),source_links.get(p.get('path'),principal))
            link=selected+('#page='+str(pages[0]) if pages else '')
            evidence=''
            for e in row.get('evidence',[]):
                url=e.get('url');page=e.get('physical_pages',[])
                selected=source_links.get(e.get('witness_id'),source_links.get(e.get('path'),principal))
                href=url if url and url.startswith(('https://','http://')) else selected+('#page='+str(page[0]) if page else '')
                evidence+=f'<li><a href="{esc(href)}" target="_blank" rel="noopener">{esc(e.get("source_label","Source"))}</a> · {esc(e.get("locator",""))}<p>{esc(e.get("reading",""))}</p></li>'
            uncertainty=f'<p class="remaining"><strong>Remaining uncertainty</strong><br>{esc(row["remaining_uncertainty"])}</p>' if row.get('remaining_uncertainty') else ''
            blocks.append(f'<div class="review-record" id="{esc(rid)}"><div class="review-label">{label} · {esc(row.get("field",""))} · {esc(row.get("comparison_confidence",row.get("confidence","")))}</div><div class="comparison"><div><h4>{old_label}</h4><pre>{left}</pre></div><div><h4>Editorial</h4><pre>{right}</pre></div></div><p>{esc(row.get("rationale",""))}</p>{uncertainty}<a href="{esc(link)}" target="_blank" rel="noopener">Source ↗</a> <span class="control-help">{esc(where)}</span>'+('<ul class="evidence-list">'+evidence+'</ul>' if evidence else '')+f'<details><summary>Full published record · {esc(rid)}</summary><pre>{esc(json.dumps(row,ensure_ascii=False,indent=2))}</pre></details></div>')
        item=allitems.get(target);preview=''
        if item:
            preview=decorate(item.get('stem',item.get('content',item.get('heading',''))))
            if 'stem'in item:preview+='<ol>'+''.join('<li>'+decorate(o)+'</li>' for o in item['options'])+'</ol><p>Editorial key: '+str(item['key'])+'</p>'
            preview='<details class="review-context"><summary>Current editorial context</summary><div lang="ja">'+preview+'</div></details>'
        groups.append(f'<section class="review-group" id="{anchor}" data-kinds="{" ".join(sorted(flags))}"><div class="review-group-heading"><h2>{esc(target or "Paper coverage")}</h2><a href="../{html_path(m["unit"])}#{esc(target or "content")}">Open in paper →</a></div>{preview}{"".join(blocks)}</section>')
    controls='<div class="review-controls"><label>Show <select id="review-filter"><option value="all">All records</option><option value="difference">Principal differences</option><option value="unresolved">Unresolved cases</option><option value="provisional_fix">Provisional fixes</option></select></label><label>Find <input id="review-search" type="search" placeholder="Item, wording, evidence…"></label></div><p id="review-count" class="control-help" role="status"></p>'
    return controls+''.join(groups),mapping
