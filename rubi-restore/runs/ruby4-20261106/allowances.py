"""Composition-adjusted task/section forecasts, with original-level lineage donors."""
from common import *
from collections import Counter,defaultdict
import gzip,math,csv,io
import numpy as np
from ruby_core import Projection,KANJI_RE,json_hash
from ruby2_scope import iter_current

VOCAB={'reading_test','orthography_test','vocabulary','paraphrase','usage'}
GRAMMAR={'grammar','cloze','sentence_composition'}
def family(task):return 'vocabulary' if task in VOCAB else 'grammar' if task in GRAMMAR else 'reading'
def kcount(t):return len(KANJI_RE.findall(t))
def cell(r,grid=True):
    role='heading' if r['role']=='heading' else 'example' if r['role']=='example' else 'passage' if r['role'] in ('passage','notice','table') else 'choice' if r['role']=='option' else 'stem'
    g=r['features']['modern_jlpt'][0];lv=int(r['level'][1]);dif=0 if g<6-lv else 1 if g==6-lv else 2
    return '|'.join([r['task'],role,str(dif) if grid else '*','common' if r['features']['suw'][0]<3.4 else 'less_common'])

def build_cells():
    roster={r['unit']:r for r in load(RUN/'paper-roster.json')}
    previous={r['unit']:r for r in load(RUN.parent/'ruby2-20261105/opportunity-census.json')['units']}
    allcells={};rows=[];note_rows=[]
    for u,rr in roster.items():
        doc=load(check(rr['editorial']));ov=load(check(rr['sidecar']))
        sec={s['id']:dict(kanji=0,source_covered=0,source_groups=0,current_inferred_covered=0,current_inferred_groups=0,
                         task=doc['layout']['sections'][s['id']]['task'],part=s['part'],cells=defaultdict(lambda:[0,0,0])) for s in doc['sections']}
        fields={f['pointer']:f for f in iter_current(doc)}
        candidate_cells={}
        with gzip.open(check(previous[u]),'rt',encoding='utf-8') as f:
            for line in f:
                r=json.loads(line);field=fields[r['pointer']]
                assert json_hash(field['value'])==r['hash'],(u,r['pointer'])
                for p in range(r['a'],r['b']):candidate_cells.setdefault((r['pointer'],p),cell(r))
        byann=defaultdict(list)
        for a in ov['annotations']:byann[a['pointer']].append(a)
        for ptr,f in fields.items():
            p=Projection(f['value']);st=sec[f['section']]
            observed={a for g in p.ruby for a in range(g['start'],g['end']) if kcount(p.text[a])}
            starts={g['start'] for g in p.ruby}
            added={a for g in byann[ptr] for a in range(g['start'],g['end']) if kcount(p.text[a])}
            assert not observed&added
            st['source_groups']+=len(p.ruby);st['current_inferred_groups']+=len(byann[ptr]);st['current_inferred_covered']+=len(added)
            note=doc['layout']['items'].get(f['owner'],{}).get('notes') if f['slot']=='content' else None
            diagnostic=Counter()
            for pos,ch in enumerate(p.text):
                if not kcount(ch):continue
                key=candidate_cells.get((ptr,pos),'|'.join([f['task'],'heading' if f['role']=='heading' else 'example' if f['role']=='example' else 'passage' if f['role'] in ('passage','notice','table') else 'choice' if f['role']=='option' else 'stem','U','U']))
                z=st['cells'][key];z[0]+=1;z[1]+=int(pos in observed);z[2]+=int(pos in starts)
                st['kanji']+=1;st['source_covered']+=int(pos in observed)
                area='note' if note and note['start']<=pos<note['end'] else 'remainder'
                diagnostic[area+'_kanji']+=1;diagnostic[area+'_source_covered']+=int(pos in observed)
            if note:note_rows.append(dict(unit=u,item=f['owner'],level=rr['original_level'],era=rr['era'],public_class=rr['public_class'],**diagnostic))
        for sid,st in sec.items():
            rows.append(dict(unit=u,section=sid,level=rr['original_level'],era=rr['era'],year=int(u[-4:]),public_class=rr['public_class'],lineage=previous[u]['lineage'],
                **{k:v for k,v in st.items() if k!='cells'},family=family(st['task'])))
        allcells[u]={sid:dict(st['cells']) for sid,st in sec.items()}
    save('coverage/cells.json',allcells);save('coverage/before-sections.json',rows);save('coverage/note-diagnostics.json',note_rows)
    return allcells,rows

def forecast(cells,rows,grid,paper_ranges=None):
    meta={r['unit']:r for r in rows};byunit=defaultdict(list)
    for r in rows:byunit[r['unit']].append(r)
    # The p10 exclusion has no exhaustive field map in this full-paper corpus.
    # Keep its descriptive census, but do not infer authorization for its cells.
    donors={u for u,r in meta.items() if r['public_class'] in ('base','workbook','sample') and u!='N2_07_2018'}
    agg={}
    for u,sections in cells.items():
        a=defaultdict(lambda:np.zeros(3))
        for vv in sections.values():
            for key,v in vv.items():
                parts=key.split('|')
                if not grid:parts[2]='*'
                a['|'.join(parts)]+=v
        agg[u]=a
    result=[]
    for u,rs in byunit.items():
        m=meta[u];total=sum(r['kanji'] for r in rs)
        near=sorted(v for v in donors if v!=u and meta[v]['lineage']!=m['lineage'] and meta[v]['era']==m['era'] and meta[v]['level']==m['level'])
        assert near,(u,'no same-era level donors')
        multiplicity=Counter(meta[v]['lineage'] for v in near)
        w=np.array([math.exp(-abs(meta[v]['year']-m['year'])/11-abs(math.log((sum(r['kanji'] for r in byunit[v])+1)/(total+1)))/2)/multiplicity[meta[v]['lineage']] for v in near]);w/=w.sum()
        predictions=[]
        for r in rs:
            targets=defaultdict(lambda:np.zeros(3))
            for key,z in cells[u][r['section']].items():
                parts=key.split('|')
                if not grid:parts[2]='*'
                targets['|'.join(parts)]+=z
            vals=[];support=0
            for i,v in enumerate(near):
                d=agg[v];overall=sum(d.values(),np.zeros(3));expected=0
                for key,z in targets.items():
                    task,role,_,_=key.split('|');n=z[0]
                    taskparent=sum((a for k,a in d.items() if k.split('|')[0]==task),np.zeros(3))
                    familyp=sum((a for k,a in d.items() if family(k.split('|')[0])==family(task)),np.zeros(3))
                    roleparent=sum((a for k,a in d.items() if k.split('|')[:2]==[task,role]),np.zeros(3))
                    broad=(overall[1]+.5)/(overall[0]+1)
                    fr=(familyp[1]+8*broad)/(familyp[0]+8)
                    tr=(taskparent[1]+12*fr)/(taskparent[0]+12)
                    pr=(roleparent[1]+16*tr)/(roleparent[0]+16)
                    exact=d.get(key,np.zeros(3));rate=(exact[1]+6*pr)/(exact[0]+6)
                    expected+=n*rate
                    support+=n*w[i]*bool(exact[0])
                vals.append(expected)
            predictions.append(vals)
            ex=float(w@np.array(vals));groups=defaultdict(list)
            for i,v in enumerate(near):groups[meta[v]['lineage']].append(i)
            cluster=np.array([np.average(np.array(vals)[ii],weights=w[ii]) for ii in groups.values()]);ww=np.array([w[ii].sum() for ii in groups.values()]);ww/=ww.sum()
            seed=int(hashlib.sha256((u+r['section']+str(grid)).encode()).hexdigest()[:8],16)
            rng=np.random.default_rng(seed);n=len(cluster)
            sim=cluster[rng.choice(n,2400,p=ww)]+rng.multinomial(n,ww,2400)@cluster/n-ex+rng.normal(0,math.sqrt(max(ex,1)),2400)
            lo,hi=np.quantile(np.clip(sim,0,r['kanji']),[.025,.975]).round().astype(int)
            result.append(dict(**r,current_covered=r['source_covered']+r['current_inferred_covered'],expected_covered=round(ex,4),
                expected_range=[int(lo),int(hi)],donors=near,donor_lineages=len(groups),weighted_cell_support=round(support/max(r['kanji'],1),5)))
        if paper_ranges is not None:
            # Use one donor lineage for the full composition draw, so section
            # uncertainty is correlated rather than summed as independent.
            totals=np.sum(np.array(predictions),axis=0);ex=float(w@totals)
            cluster=np.array([np.average(totals[ii],weights=w[ii]) for ii in groups.values()])
            ww=np.array([w[ii].sum() for ii in groups.values()]);ww/=ww.sum();n=len(cluster)
            seed=int(hashlib.sha256((u+'paper'+str(grid)).encode()).hexdigest()[:8],16)
            rng=np.random.default_rng(seed)
            sim=cluster[rng.choice(n,2400,p=ww)]+rng.multinomial(n,ww,2400)@cluster/n-ex+rng.normal(0,math.sqrt(max(ex,1)),2400)
            lo,hi=np.quantile(np.clip(sim,0,total),[.025,.975]).round().astype(int)
            paper_ranges.append(dict(unit=u,expected_covered=round(ex,4),expected_range=[int(lo),int(hi)],donor_lineages=n,
                method='Same-lineage full-paper composition predictions; 2400 descriptive lineage/count draws, not a calibrated predictive confidence interval.'))
    return result

def allocate(rows):
    by=defaultdict(list)
    for r in rows:by[r['unit']].append(r)
    papers=[]
    for u,rs in by.items():
        expected=sum(r['expected_covered'] for r in rs);current=sum(r['current_covered'] for r in rs)
        cap=max(0,math.floor(expected+.5)-current) if rs[0]['public_class']=='restored' else 0
        deficits=[max(0,r['expected_covered']-r['current_covered']) for r in rs]
        denom=sum(deficits);alloc=[cap*d/denom if denom else 0 for d in deficits]
        floors=[math.floor(a) for a in alloc]
        order=sorted(range(len(rs)),key=lambda i:(-(alloc[i]-floors[i]),rs[i]['section']))
        for i in order[:cap-sum(floors)]:floors[i]+=1
        for r,a in zip(rs,floors):r['additional_allowance']=a
        papers.append(dict(unit=u,level=rs[0]['level'],era=rs[0]['era'],public_class=rs[0]['public_class'],
            kanji=sum(r['kanji'] for r in rs),source_covered=sum(r['source_covered'] for r in rs),current_covered=current,
            expected_covered=round(expected,2),additional_allowance=cap,section_allowance=sum(floors)))
        assert sum(floors)==cap
    return papers

def main():
    cells,rows=build_cells()
    for grid in (True,False):
        result=forecast(cells,rows,grid);papers=allocate(result);name='with-grid' if grid else 'without-grid'
        save('coverage/'+name+'-sections.json',result);save('coverage/'+name+'-papers.json',papers)
        grouped=defaultdict(Counter)
        for r in papers:
            if r['public_class']=='restored':grouped[r['level']].update({k:r[k] for k in ('kanji','current_covered','expected_covered','additional_allowance')})
        print(name,{k:dict(v) for k,v in grouped.items()},flush=True)
    save('coverage/method.json',dict(status='research_estimates_not_final_selection',
        method='Original-level/era donor rates; task then task/role then difficulty/frequency cells; shrinkage 8/12/16/6; year and written-volume weights, inverse lineage multiplicity; 2400 deterministic descriptive range draws.',
        denominator='All authored kanji occurrences, union of observed source coverage; source and 719 current inferences count toward targets.',
        exclusions={'N2_07_2018':'Excluded from full-paper donor estimation because its excluded physical page 10 lacks an exhaustive field map in this corpus. Included only in descriptive base census. Pages 2-9,11-29 remain authorized for exact observation research.'},
        rounding='Nearest whole covered-kanji paper target (half up), subtract existing. Reconcile positive section deficits proportionally under the cap, largest remainders in section-id order. No transfer after contextual rejections; whole spans only.',
        note_roles='Diagnostic only pending R6; no automatic note boost.',
        scope='Density is reading-support guidance, not evidence of exact printing or psychometric equivalence.'))

if __name__=='__main__':main()
