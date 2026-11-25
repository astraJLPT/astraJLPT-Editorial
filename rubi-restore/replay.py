"""Replay frozen ranking and allowance/context decisions without acquiring data."""
from pathlib import Path
import collections,gzip,hashlib,json,os,sys
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import numpy as np
from scipy.special import expit
ROOT=Path(__file__).resolve().parent.parent
RUN=ROOT/'rubi-restore/runs/ruby4-20261106'
sys.path[:0]=[str(RUN),str(ROOT/'rubi-restore/tools'),str(ROOT/'pdf-render/tools')]
from simulate_selection import identity
from replay_contextual_selection import replay

def raw(path):
    path=Path(path)
    if not path.exists():path=path.with_name(path.name+'.gz')
    data=path.read_bytes()
    return gzip.decompress(data) if path.suffix=='.gz' else data
def load(path):return json.loads(raw(path))
def checked(binding):
    data=raw(ROOT/binding['path'])
    if hashlib.sha256(data).hexdigest()!=binding['sha256']:raise ValueError('Frozen input changed: '+binding['path'])
    return json.loads(data)
def main():
    manifest=load(ROOT/'rubi-restore/datasets/manifest.json')
    for binding in manifest['files']:
        if hashlib.sha256((ROOT/binding['path']).read_bytes()).hexdigest()!=binding['sha256']:raise ValueError('Packaged research file changed: '+binding['path'])
    scorer=load(ROOT/'rubi-restore/runs/ruby3-20261105/presence-model.json')
    freeze=load(RUN/'policy-freeze-v3.json')
    papers={r['unit']:r for r in checked(freeze['allocations']['papers'])}
    sections=collections.defaultdict(list)
    for row in checked(freeze['allocations']['sections']):sections[row['unit']].append(row)
    ledger=load(RUN/'selection/final-v3/final-context-ledger.json')
    decisions={r['final_context_verdict']['proposal_id']:r['final_context_verdict'] for r in ledger}
    for row in load(RUN/'selection/final-v3/final-effective-rejections.json'):decisions[row['proposal_id']]=row
    for row in load(RUN/'selection/final-v3/final-historical-suitable-not-selected.json'):
        verdict=row['final_verdict']
        if verdict:decisions.setdefault(row['proposal_id'],verdict)
    starting=collections.defaultdict(list)
    for row in load(RUN/'selection/final-v3/final-starting-reconciliation.json'):
        unit,pointer,digest,a,b,base,reading=row['binding']
        starting[unit].append({'pointer':pointer,'start':a,'end':b,'base':base,'reading':reading,'annotation_id':row['annotation_id']})
    extras=collections.defaultdict(list)
    for group in ['corrections','final-corrections-001','r8-corrections-001','r8-corrections-002']:
        receipt=load(RUN/'selection'/group/'score-reconciliation.json')
        for row in checked(receipt['ranked']):extras[row['unit']].append(row)
    expected=load(RUN/'selection/final-v3/final-selected.json')
    expected_new={identity(r) for r in expected if not r['starting_id']}
    selected=[];total=0;unreviewed=[]
    for index,binding in enumerate(manifest['features']):
        path=ROOT/binding['path']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=binding['sha256']:raise ValueError('Frozen feature projection changed')
        features=load(path);ranked_bytes=(ROOT/binding['ranked_path']).read_bytes()
        if hashlib.sha256(ranked_bytes).hexdigest()!=features['ranked_sha256']:raise ValueError('Ranked row order changed')
        rows=[json.loads(line) for line in gzip.decompress(ranked_bytes).splitlines()]
        X=np.clip((np.asarray(features['vectors'],dtype=float)-scorer['mu'])/scorer['scale'],-8,8)
        coefficients=np.asarray(scorer['coef']);scores=expit(coefficients[0]+X@coefficients[1:])
        for row,score in zip(rows,scores):
            pos,neg=row['analogy_positive_lineages'],row['analogy_negative_lineages']
            adjusted=round(min(1,max(0,float(score)+.04*(pos-neg)/(2+pos+neg))),10)
            if adjusted!=row['rank_score']:raise ValueError('Frozen score differs: '+identity(row))
        unit=binding['unit'];total+=len(rows)
        if papers[unit]['additional_allowance'] or starting[unit]:
            kept,remaining,cap,skipped,rejected=replay(rows+extras[unit],sections[unit],papers[unit],starting[unit],decisions)
            selected.extend(identity(r) for r in kept)
            unreviewed.extend(identity(r) for r in kept if identity(r) not in decisions)
        if (index+1)%50==0:print('Replayed',index+1,'owners',flush=True)
    actual=set(selected)
    if actual!=expected_new or unreviewed:
        raise ValueError(json.dumps({'missing':sorted(expected_new-actual)[:15],'extra':sorted(actual-expected_new)[:15],'unreviewed':unreviewed[:15]}))
    from release_contract import checked_owner,contract
    annotation_count=0
    for unit in contract()['owners']:
        row=checked_owner(unit);sidecar=load(ROOT/row['selection']['sidecar']['path'])
        from ruby_release_policy import validate_derivative_overlay
        validate_derivative_overlay(sidecar);annotation_count+=len(sidecar['annotations'])
    result={'owners':len(manifest['features']),'candidate_scores_reproduced':total,'new_selections_reproduced':len(actual),'starting_annotations':sum(map(len,starting.values())),'final_pass4_groups':len(expected),'installed_final_annotations':annotation_count,'unreviewed_selected':len(unreviewed),'result':'pass'}
    print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
