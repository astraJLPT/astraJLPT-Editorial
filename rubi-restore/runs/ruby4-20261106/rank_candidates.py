"""Replay stored scores and create a broader, explicitly unaudited review queue."""
from common import *
import gzip,math
from collections import Counter,defaultdict
from functools import lru_cache
from ruby_core import Projection,json_hash,hira,KANJI_RE
from ruby2_scope import iter_current
from candidate_policy import review_eligibility

def stream(path):
    with gzip.open(path,'rt',encoding='utf-8') as f:
        for line in f:yield json.loads(line)

def key(r):return r['unit'],r['pointer'],r['a'],r['b'],r['rd']

def frequencies():
    import csv,io,zipfile
    path=next((ROOT/'rubi-restore/data/frequency').rglob('*suw*.zip'))
    pairs=Counter();readings=defaultdict(set)
    with zipfile.ZipFile(path) as z:
        for row in csv.DictReader(io.TextIOWrapper(z.open(z.namelist()[0]),encoding='utf-8-sig'),delimiter='\t'):
            lemma,rd=row['lemma'],hira(row['lForm']);pairs[lemma,rd]+=int(row['frequency']);readings[lemma].add(rd)
    return pairs,readings,ref(path)

def main():
    sys.path.insert(0,str(RUN.parent/'ruby2-20261105'))
    import fit_models as fm
    from reading_resources import dictionary,tokenizer
    tk=dictionary.Dictionary().create();freq,readings,freqref=frequencies()
    @lru_cache(2048)
    def tokens(text):return [(t.begin(),t.end(),t.surface(),t.dictionary_form(),hira(t.reading_form())) for t in tk.tokenize(text,tokenizer.Tokenizer.SplitMode.C)]
    def lookup(r,pj):
        hits=[t for t in tokens(pj.text) if t[0]<=r['a']<r['b']<=t[1]]
        if len(hits)!=1:return dict(state='unknown',reason='no unique whole-token match')
        a,b,s,lemma,rd=hits[0]
        if (a,b)==(r['a'],r['b']) and s==r['base']:rd=r['rd']
        for word in dict.fromkeys([s,lemma]):
            count=freq.get((word,rd))
            if count:
                return dict(state='matched',word=word,reading=rd,count=count,surface=s,lemma=lemma,
                    whole_span=[a,b],match='exact_surface_reading' if word==s else 'exact_lemma_reading')
        return dict(state='unknown',reason='whole-word contextual-reading pair absent; not interpreted as rare',surface=s,lemma=lemma,reading=rd,whole_span=[a,b])
    roster=load(RUN/'paper-roster.json');ix=load(PREV/'ranking-index.json')
    census={r['unit']:r for r in load(RUN.parent/'ruby2-20261105/opportunity-census.json')['units']}
    model=load(PREV/'presence-model.json');index=[];total=Counter()
    for rr in roster:
        u=rr['unit'];doc=load(check(rr['editorial']));fields={f['pointer']:f for f in iter_current(doc)}
        projections={p:Projection(f['value']) for p,f in fields.items()}
        raw=list(stream(check(census[u])));prior={key(r):r for r in stream(check(ix[u]['rank_file']))}
        assert len(raw)==len(prior)
        for r in raw:r['features']['priorgloss']=prior[key(r)]['prior_gloss']
        scores=fm.scored(raw,model)
        existing=load(check(rr['sidecar']))['annotations']
        active={(a['pointer'],a['start'],a['end'],a['reading']):a['annotation_id'] for a in existing}
        rows=[];counts=Counter()
        for r,s in zip(raw,scores):
            old=prior[key(r)];pos,neg=old['analogy_positive_lineages'],old['analogy_negative_lineages']
            expected=round(min(1,max(0,float(s)+.04*(pos-neg)/(2+pos+neg))),10)
            assert expected==old['rank_score'],(u,key(r),expected,old['rank_score'])
            guard,adjustments=review_eligibility(r,fields[r['pointer']],projections[r['pointer']]) if rr['public_class']=='restored' else ('trusted_owner',[])
            current=active.get((r['pointer'],r['a'],r['b'],r['rd']))
            if old['direct'] and not current:guard='direct_evidence_route'
            row={**old,'starting_id':current,'original_shape_guard':old['shape_guard'],'review_guard':guard,'guard_adjustments':adjustments,
                'frequency':lookup(r,projections[r['pointer']]) if not guard else dict(state='not_evaluated'),
                'raw_alignment':r['alignment'],'dictionary_readings':r['features']['dictionary_names'][1],
                'prior_retired_or_firstpass_id':r.get('current_id') if r.get('current_id')!=current else None,
                'review_state':'starting_inference_requires_final_reread' if current else 'not_reviewed'}
            rows.append(row);counts['total']+=1
            counts['starting' if current else guard or 'review_eligible']+=1
        rows.sort(key=lambda r:(-r['rank_score'],*key(r)))
        dest=RUN/'ranked'/f'{u}.jsonl.gz';dest.parent.mkdir(parents=True,exist_ok=True)
        with dest.open('wb') as st,gzip.GzipFile(filename='',fileobj=st,mode='wb',mtime=0,compresslevel=5) as z:
            for r in rows:z.write((json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n').encode())
        index.append(dict(unit=u,public_class=rr['public_class'],counts=counts,file=ref(dest)));total.update(counts)
        if len(index)%20==0:print('Score replay',len(index),flush=True)
    save('research/ranking-index.json',dict(status='scores_reproduced_candidates_require_contextual_review',files=index,counts=total,
        model=ref(PREV/'presence-model.json'),frequency_resource=freqref,policy=ref(RUN/'candidate_policy.py'),
        frequency_policy='Only identical stored rank_score values may use count ascending, matched before unknown, then original unit/pointer/start/end/reading order. Unknown is not rarity. Adoption remains subject to boundary tests.'))
    print('Replayed all candidate scores',dict(total),flush=True)

if __name__=='__main__':main()
