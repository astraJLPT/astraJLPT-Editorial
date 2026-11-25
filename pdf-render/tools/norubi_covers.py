"""Exact native cover span removal, independent of font size heuristics."""
import hashlib,json
from pathlib import Path
from functools import lru_cache

@lru_cache(maxsize=1)
def policy():
    return json.loads((Path(__file__).resolve().parents[1]/'config/norubi-cover-spans.json').read_text('utf-8'))

def spans(native):
    digest=hashlib.sha256(json.dumps(native,sort_keys=True).encode()).hexdigest()
    row=policy()['families'].get(digest)
    if row is None:raise ValueError('No reviewed no-rubi cover-span binding for '+digest)
    removed=set()
    for record in row['reading_spans']:
        i=record['index']
        if native['spans'][i]!=record['span']:raise ValueError('Stale no-rubi cover span')
        removed.add(i)
    return [s for i,s in enumerate(native['spans']) if i not in removed],sorted(removed)
