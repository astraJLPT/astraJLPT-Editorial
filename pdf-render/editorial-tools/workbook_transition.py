"""Replay the exact validated style digest transitions, not old handoff archives."""
import copy
from release_contract import owner
def rebind_style(unit,style):
 result=copy.deepcopy(style);rows=owner(unit)['style_rebindings']
 for row in rows:
  keys=row['pointer'].strip('/').split('/');node=result
  for key in keys[:-1]:node=node[int(key)] if isinstance(node,list) else node[key]
  key=int(keys[-1]) if isinstance(node,list) else keys[-1]
  if node[key]!=row['before']:raise ValueError('Stale approved typography transition')
  node[key]=row['after']
 return result,copy.deepcopy(rows)
