"""Allowance-bound review proposals and exact-score frequency boundary test."""
from common import *
import gzip
from collections import Counter,defaultdict
from ruby_core import KANJI_RE

def kcount(s):return len(KANJI_RE.findall(s))
def identity(r):return 'rr4-'+hashlib.sha256('|'.join(map(str,[r['unit'],r['pointer'],r['a'],r['b'],r['rd']])).encode()).hexdigest()[:20]
def fallback(r):return r['unit'],r['pointer'],r['a'],r['b'],r['rd']
def order(r,frequency):
    f=r['frequency'];tie=(0,f['count']) if f['state']=='matched' else (1,0)
    return (-r['rank_score'],*(tie if frequency else ()),*fallback(r))

def select(rows,sections,paper,starting,frequency):
    used=defaultdict(list)
    for a in starting:used[a['pointer']].append((a['start'],a['end']))
    remaining={r['section']:r['additional_allowance'] for r in sections}
    cap=paper['additional_allowance'];accepted=[];rejected=Counter()
    for r in sorted(rows,key=lambda r:order(r,frequency)):
        if r['starting_id']:continue
        if r['review_guard']:rejected[r['review_guard'].split(':')[0]]+=1;continue
        cost=kcount(r['base']);s=r['section']
        if any(a<r['b'] and b>r['a'] for a,b in used[r['pointer']]):rejected['overlap']+=1;continue
        if cost>remaining[s] or cost>cap:rejected['allowance']+=1;continue
        used[r['pointer']].append((r['a'],r['b']));remaining[s]-=cost;cap-=cost
        accepted.append(dict(**r,proposal_id=identity(r),covered_kanji=cost,proposal_state='requires_full_context_review',
            final_tie_inputs=list(order(r,frequency)[1:])))
    return accepted,remaining,rejected

def main():
    roster={r['unit']:r for r in load(RUN/'paper-roster.json')}
    papers={r['unit']:r for r in load(RUN/'coverage/with-grid-papers.json')}
    ss=defaultdict(list)
    for r in load(RUN/'coverage/with-grid-sections.json'):ss[r['unit']].append(r)
    selections={False:[],True:[]};summaries={False:[],True:[]};swaps=[]
    for item in load(RUN/'research/ranking-index.json')['files']:
        u=item['unit']
        if roster[u]['public_class']!='restored':continue
        with gzip.open(check(item['file']),'rt',encoding='utf-8') as f:rows=[json.loads(line) for line in f]
        starting=load(check(roster[u]['sidecar']))['annotations']
        result={}
        for freq in (False,True):
            kept,gaps,skipped=select(rows,ss[u],papers[u],starting,freq)
            result[freq]={r['proposal_id']:r for r in kept}
            selections[freq]+=kept
            summaries[freq].append(dict(unit=u,level=papers[u]['level'],era=papers[u]['era'],allowance=papers[u]['additional_allowance'],
                new_groups=len(kept),additional_covered=sum(r['covered_kanji'] for r in kept),section_gaps=gaps,skipped=skipped))
        for aid in sorted(result[False].keys()^result[True].keys()):
            r=result[False].get(aid) or result[True][aid]
            same=[q for q in rows if q['rank_score']==r['rank_score'] and not q['review_guard']]
            swaps.append(dict(**r,policy='original' if aid in result[False] else 'frequency',exact_score_tie_size=len(same)))
    for freq in (False,True):
        name='frequency' if freq else 'original'
        save('research/proposals-'+name+'.json',selections[freq])
        save('research/simulation-'+name+'.json',summaries[freq])
        counts=defaultdict(Counter)
        for r in summaries[freq]:counts[r['level']].update({k:r[k] for k in ('allowance','new_groups','additional_covered')})
        print(name,{k:dict(v) for k,v in counts.items()},flush=True)
    save('research/frequency-boundary-swaps.json',swaps)
    print('Exact-score boundary differences',len(swaps),'proposals; papers',len({r['unit'] for r in swaps}),flush=True)

if __name__=='__main__':main()
