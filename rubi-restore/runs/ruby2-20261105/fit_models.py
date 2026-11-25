"""Frozen-split ridge logistic presence comparisons; no final label access.
Presence scores are ranking scores, never a certification of a reading or of original printing."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
from study_eval import *
from scipy.special import expit
from scipy.optimize import minimize
from scipy.stats import rankdata
TGRID=(.35,.50,.60,.70,.75,.80,.85,.90,.95,.97,.99)
def design(rows,families):
    if not rows:return np.empty((0,0))
    def vec(r):
        v=[]
        for f in families:
            q=r['features'][f];v+=q
            if f not in ('core','era'):v+=[float(q[0])*(int(r['level'][1])-3)]
        return v
    return np.asarray([vec(r) for r in rows],dtype=float)
def fit(rows,families,weak=0,modern=False):
    fitrows=[r for r in rows if r['split']=='train' and r['y']>=0 and (r['strength']=='strong' or weak) and (not modern or r['era']=='modern-2010')]
    cc=collections.Counter(r['lineage'] for r in fitrows);w=np.array([(1 if r['strength']=='strong' else weak)/cc[r['lineage']] for r in fitrows]);w*=len(fitrows)/sum(w)
    X=design(fitrows,families);mu=np.average(X,axis=0,weights=w);sig=np.sqrt(np.average((X-mu)**2,axis=0,weights=w));sig[sig<.12]=1
    X=np.clip((X-mu)/sig,-8,8);X=np.column_stack((np.ones(len(X)),X));y=np.array([r['y'] for r in fitrows]);l2=2.5
    def loss(b):
        z=X@b;v=(w*(np.logaddexp(0,z)-y*z)).sum()+l2*(b[1:]@b[1:])/2;g=X.T@(w*(expit(z)-y));g[1:]+=l2*b[1:];return v,g
    opt=minimize(loss,np.zeros(X.shape[1]),jac=True,method='L-BFGS-B',options={'maxiter':450,'ftol':1e-10})
    if not opt.success:raise ValueError(opt.message)
    return {'families':list(families),'weak_weight':weak,'modern_training_only':modern,'ridge':l2,'mu':mu.tolist(),'scale':sig.tolist(),'coef':opt.x.tolist(),'training_opportunities':len(y),'training_lineages':len(cc),'feature_columns':X.shape[1]-1}
def scored(rows,model):
    if not rows:return np.asarray([])
    X=np.clip((design(rows,model['families'])-model['mu'])/model['scale'],-8,8);b=np.array(model['coef']);return expit(b[0]+X@b[1:])
def ranking(rows,scores):
    y=np.array([bool(r['gids']) for r in rows]);scores=np.asarray(scores);order=np.argsort(-scores,kind='stable');hit=y[order];p=sum(y);n=len(y)-p
    return {'presence_auc':float((rankdata(scores)[y].sum()-p*(p+1)/2)/(p*n)) if p and n else None,'presence_average_precision':float(((np.cumsum(hit)/np.arange(1,len(y)+1))*hit).sum()/p) if p else None}
def tune(rows,golds,sc):
    trials=[]
    for t in TGRID:
        ann=predict(rows,'model',sc,t);stats=describe(rows,golds,ann);stats['threshold']=t;stats['accepted_lineages']=len({r['lineage'] for r,rd in ann});trials.append(stats)
    support=[s for s in trials if s['accepted']>=15 and s['accepted_lineages']>=3];viable=[s for s in support if s['joint_precision']>=.95]
    if viable:best=max(viable,key=lambda s:(s['joint'], -s['harmful'],s['joint_precision']))
    elif support:best=max(support,key=lambda s:(s['joint_precision'],-s['harmful'],s['joint']))
    else:best=max(trials,key=lambda s:(s['joint_precision'] or 0,s['joint']))
    return {'chosen':best,'meets_development_target':bool(viable),'trials':trials,'fixed_070':next(s for s in trials if s['threshold']==.70),'ranking':ranking(rows,sc)}
def experiments():
    if (RR/'development-freeze.json').exists():raise ValueError('Development is sealed')
    r,g,mask=windows('development');tr=[x for x in r if x['split']=='train'];de=[x for x in r if x['split']=='development'];gg=[x for x in g if x['split']=='development'];seen={x['base'] for x in tr if x['strength']=='strong'}
    fs=list(FAMILIES);base=['core','era'];extra=fs[2:]
    specs={'modern_retrained_core':(['core'],True),'pooled_core':(['core'],False),'era_core':(base,False),'pooled_all':([f for f in fs if f!='era'],False),'era_all':(fs,False)}
    specs.update({'add_'+f:(base+[f],False) for f in extra});specs.update({'drop_'+f:([j for j in fs if j!=f],False) for f in extra})
    models={};summ={};baseline=predict(de,'first_pass')
    for name,(fam,modern) in specs.items():
        m=fit(tr,fam,0,modern);sc=scored(de,m);t=tune(de,gg,sc);m['threshold']=t['chosen']['threshold'];models[name]=m;summ[name]=t
    # Same data and same thresholds. Prefer a smaller family on exact ties and require actual support.
    pool=[n for n in models if not n.startswith('drop_')];ok=[n for n in pool if summ[n]['meets_development_target']]
    if ok:key=lambda n:(summ[n]['chosen']['joint'],-summ[n]['chosen']['harmful'],-models[n]['feature_columns'])
    else:key=lambda n:(summ[n]['chosen']['joint_precision'] or 0,-summ[n]['chosen']['harmful'],summ[n]['chosen']['joint'],-models[n]['feature_columns'])
    win=max(ok or pool,key=key);strong_name=win
    for wt in (.10,.25):
        n=f'{win}_weak_{wt:.2f}';m=fit(tr,models[win]['families'],wt,models[win]['modern_training_only']);sc=scored(de,m);t=tune(de,gg,sc);m['threshold']=t['chosen']['threshold'];summ[n]=t;models[n]=m
    for n in [k for k in models if '_weak_' in k]:
        s,b=summ[n]['chosen'],summ[win]['chosen']
        if summ[n]['meets_development_target'] and s['joint_precision']>=(b['joint_precision'] or 0) and s['joint']>b['joint'] and s['harmful']<=b['harmful']:win=n
    m=models[win];sc=scored(de,m);pred=predict(de,'model',sc,m['threshold']);wd=RR/'development-models';wd.mkdir(exist_ok=True)
    for n,v in models.items():save(wd/(n+'.json'),v)
    info={'phase':'development only; no final labels read','seed':SEED,'fit':'L2 logistic, per-lineage total weight equal for strong papers, weak lineage total 0/.1/.25; fixed penalty 2.5. Same tokenization and contextual reading correction across presence ablations. Scores not calibrated.','selection':'Lowest-error supported operating point targeting >=95% joint precision, >=15 accepted and >=3 contributing lineages. Among eligible experiments prefer greatest joint coverage, then fewer harmful additions, then smaller design. Without an eligible operating point, highest descriptive precision with support; do not authorize expansion on that result. Leave-one-family-out tests are diagnostics, not selected via multiple searches.','counts':{'strong_train':sum(x['strength']=='strong' for x in tr),'weak_positive_train':sum(x['strength']=='weak' for x in tr),'development':len(de),'development_gold':len(gg),'mask':mask},'strong_choice':strong_name,'choice':win,'target_met':summ[win]['meets_development_target'],'model_path':(wd/(win+'.json')).relative_to(ROOT).as_posix(),'model_sha256':H(wd/(win+'.json')),'joint_threshold':m['threshold'],'corpus_sha256':H(RR/'development-printed-observations.json'),'census_sha256':H(RR/'opportunity-census.json'),'experiments':summ,'first_pass':strata(de,gg,baseline,seen),'candidate':strata(de,gg,pred,seen),'paired':paired(de,gg,baseline,pred),'weak_support':'All usable weak labels come from one train-only N5 retype, positive-only. Absence, conflicting attachments and duplicate lineages cannot supply weak negatives.'}
    save(RR/'development-experiments.json',info)
    # Per-family evidence/report negative results using both common 0.70 point and threshold-independent ranks.
    effects={}
    for n in extra:
        a,b=summ['add_'+n],summ['era_core'];c,d=summ['era_all'],summ['drop_'+n]
        effects[n]={'add_presence_auc_delta':a['ranking']['presence_auc']-b['ranking']['presence_auc'],'add_average_precision_delta':a['ranking']['presence_average_precision']-b['ranking']['presence_average_precision'],'add_fixed070_joint_delta':a['fixed_070']['joint']-b['fixed_070']['joint'],'add_fixed070_harmful_delta':a['fixed_070']['harmful']-b['fixed_070']['harmful'],'drop_average_precision_loss':c['ranking']['presence_average_precision']-d['ranking']['presence_average_precision'],'limited_interpretation':'One shared development panel; overlapping resources are not independent sources. Reporting paired effects, not a causal estimate or a printing rule.'}
    save(RR/'feature-effects.json',effects)
    wr=[{'sid':x['sid'],'base':x['base'],'predicted_reading':rd,'printed':x['printed'],'overlapping_printed_group_ids':x['gids'],'context':x.get('context'),'lineage':x['lineage']} for x,rd in pred if not x['exact'] or rd!=x['printed']]
    save(RR/'development-errors.json',wr);print('Selected',win,m['threshold'],{k:summ[win]['chosen'][k] for k in ('accepted','joint','harmful','joint_recall')},'strong',strong_name,flush=True)
if __name__=='__main__':experiments()

