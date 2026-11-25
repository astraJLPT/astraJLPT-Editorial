"""Same-case source observation join and paper-cluster uncertainty. No model sees final labels during fitting."""
from study_inputs import *
from ruby2_baseline import load_baseline
import numpy as np
SEED=20261105;REPS=2000
def safe_phase(phase):
    if phase=='final':
        fr=J(RR/'development-freeze.json');assert fr['status']=='sealed_before_final_labels' and fr['source_sampling_sha256']==H(RR/'source-sampling-v1.json')
def windows(phase):
    safe_phase(phase);inp=J(RR/f'{phase}-printed-observations.json');assert inp['status']=='complete'
    freeze={x['unit']:x for x in J(PR/'editorial-freeze.json')['owners']};cens={x['unit']:x for x in J(RR/'opportunity-census.json')['units']}
    rows=[];golds=[];exclude=collections.Counter();keys=set();vv=collections.defaultdict(list)
    for s in inp['rows']:vv[s['unit']].append(s)
    for u,wins in vv.items():
        o=freeze[u];p=ROOT/o['editorial_path'];assert H(p)==o['editorial_sha256']
        doc=J(p);fields={f['pointer']:f for f in iter_current(doc)}
        byptr={w['pointer']:w for w in wins};assert len(byptr)==len(wins)
        accepted_sids=set();truth={}
        for w in wins:
            f=fields[w['pointer']];pj=Projection(f['value']);assert json_hash(f['value'])==w['field_sha256'] and pj.text[w['checked_start']:w['checked_end']]==w['checked_base']
            assert (phase=='final')==(w['split']=='final')
            for i,g in enumerate(w['groups']):
                if protect(f,pj,g['start'],g['end']):exclude['printed_protected']+=1;continue
                assert pj.text[g['start']:g['end']]==g['base']
                z={'gid':w['sid']+':'+str(i),'sid':w['sid'],'unit':u,'lineage':w['lineage'],'era':w['era'],'orig':w['original_level'],'level':w['comparison_level'],'task':w['task'],'role':w['role'],'family':w['source_family'],'split':w['split'],'strength':w['strength'],'base':g['base'],'printed':g['reading'],'a':g['start'],'b':g['end'],'num':bool(reading_check(pj.text,g['start'],g['end'])),'current_id':None}
                truth[z['gid']]=z;golds.append(z)
        cs=cens[u];cp=ROOT/cs['path'];assert H(cp)==cs['sha256']
        for row in jsonrows(cp):
            w=byptr.get(row['pointer'])
            if not w or row['a']<w['checked_start'] or row['b']>w['checked_end']:continue
            assert not row['duplicate'] and not row['uncertain'] and row['hash']==w['field_sha256']
            if row['protected'] or any(row['a']<b and row['b']>a for a,b in w['masked_spans']):exclude['protected_or_unclear_span']+=1;continue
            matches=[g for g in truth.values() if g['sid']==w['sid'] and row['a']<g['b'] and row['b']>g['a']]
            eq=[g for g in matches if (g['a'],g['b'])==(row['a'],row['b'])]
            if w['strength']=='weak' and not eq:exclude['weak_missing_or_partial_never_negative']+=1;continue
            row.update(sid=w['sid'],strength=w['strength'],family=w['source_family'],gids=[g['gid'] for g in matches],exact=eq[0]['gid'] if eq else None,printed=eq[0]['printed'] if eq else None,y=(1 if eq else -1 if matches else 0))
            # Only independent field/context occurrences. Identical lexical expressions in distinct
            # sentences are not deduplicated as if they were the same printed item.
            key=(u,row['owner'],row['slot'],row['a'],row['b']);assert key not in keys;keys.add(key)
            if row['current_id']:
                for g in matches:g['current_id']=row['current_id']
            rows.append(row)
    bl,score=load_baseline();qq=score(bl,[r['baseline'] for r in rows]) if rows else []
    thresh=J(ROOT/'rubi-restore/runs/first-pass-20261009/threshold_selection.json')['thresholds']
    for r,x in zip(rows,qq):
        r['baseline_score']=x['score'];r['baseline_accepted']=not (r['baseline']['protected'] or x['reason']) and x['score']>=thresh[r['level']]
    return rows,golds,dict(exclude)
def predict(rows,kind,scores=None,threshold=None):
    if kind=='first_pass':return [(r,r['prior_reading_candidate']) for r in rows if r['baseline_accepted']]
    if kind=='deployed':return [(r,r['current_rd']) for r in rows if r['current_id']]
    return [(r,r['rd']) for r,x in zip(rows,scores) if not r['guard'] and x>=threshold]
MET=('opportunities','gold','accepted','overlap','exact_spans','joint','distinct_presence_hits','distinct_joint_hits','generator_exact_hits','harmful','span_errors','reading_errors')
def counts(rows,gold,pred):
    seen={g['gid'] for g in gold};p=[(r,rd) for r,rd in pred];hits=set();joints=set();generated={r['exact'] for r in rows if r['exact']}
    over=exact=joint=0
    for r,rd in p:
        ids=set(r['gids'])&seen;hits|=ids;over+=bool(ids);eq=r['exact'] in seen;exact+=eq;j=eq and rd==r['printed'];joint+=j
        if j:joints.add(r['exact'])
    return [len(rows),len(seen),len(p),over,exact,joint,len(hits),len(joints),len(generated&seen),len(p)-over,over-exact,exact-joint]
RAT={'presence_precision':(3,2),'presence_recall':(6,1),'span_given_presence':(4,3),'reading_given_exact_span':(5,4),'joint_precision':(5,2),'joint_recall':(7,1),'generator_exact_recall':(8,1),'harmful_per_opportunity':(9,0),'coverage':(2,0)}
def describe(rows,gold,pred,ci=False):
    c=counts(rows,gold,pred);d=dict(zip(MET,c));d.update({k:c[a]/c[b] if c[b] else None for k,(a,b) in RAT.items()});lin=sorted({r['lineage'] for r in rows+gold});d['lineages']=len(lin);d['support']='cluster_interval' if len(lin)>=3 else 'descriptive_only_fewer_than_three_lineages'
    if ci and len(lin)>=3:
        by=[counts([r for r in rows if r['lineage']==l],[g for g in gold if g['lineage']==l],[(r,rt) for r,rt in pred if r['lineage']==l]) for l in lin]
        take=np.random.default_rng(SEED).integers(0,len(lin),(REPS,len(lin)));a=np.asarray(by)[take].sum(axis=1)
        d['cluster_ci95']={k:[round(float(v),5) for v in np.quantile(a[a[:,j]>0,i]/a[a[:,j]>0,j],[.025,.975])] if np.count_nonzero(a[:,j])>=REPS*.5 else None for k,(i,j) in RAT.items()}
    return d
def strata(rows,gold,pred,seen,ci=True):
    for r in rows+gold:r['lexical']='seen_train_base' if r['base'] in seen else 'unseen_train_base';r['counter_slice']='number_or_counter' if r['num'] else 'other';r['status_slice']='existing_inference' if r['current_id'] else 'no_existing_inference'
    out={'all':describe(rows,gold,pred,ci)}
    for k in ('era','orig','level','task','role','family','counter_slice','status_slice','lexical'):
        out[k]={v:describe([r for r in rows if r[k]==v],[g for g in gold if g[k]==v],[(r,rd) for r,rd in pred if r[k]==v],ci) for v in sorted({r[k] for r in rows+gold})}
    return out
def paired(rows,gold,first,second):
    lin=sorted({r['lineage'] for r in rows+gold})
    if len(lin)<3:return {'lineages':len(lin),'support':'descriptive_only'}
    def per(p):return np.array([counts([r for r in rows if r['lineage']==l],[g for g in gold if g['lineage']==l],[(r,rt) for r,rt in p if r['lineage']==l]) for l in lin])
    take=np.random.default_rng(SEED).integers(0,len(lin),(REPS,len(lin)));a,b=per(first)[take].sum(axis=1),per(second)[take].sum(axis=1)
    out={}
    for k,(i,j) in RAT.items():
        m=(a[:,j]>0)&(b[:,j]>0)
        if m.sum()>=REPS*.5:out[k]={'delta_ci95':[round(float(v),5) for v in np.quantile(b[m,i]/b[m,j]-a[m,i]/a[m,j],[.025,.975])],'valid_draws':int(m.sum())}
    return {'lineages':len(lin),'direction':'second minus first; paired draws of whole lineages','metrics':out}

