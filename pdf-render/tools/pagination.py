"""Ordered content groups used by the bounded PDF consumer."""
def content_groups(items):
 groups=[];group=[]
 for item in items:
  if 'content' in item and item.get('type')!='example' and group:
   groups.append(group);group=[]
  group.append(item)
 if group:groups.append(group)
 return groups

def reading_start(policy):
 if policy=='independent_passage':return r'\clearpage'
 if policy=='flow':return r'\Needspace{8\baselineskip}'
 raise ValueError('Unknown reading group start policy')
