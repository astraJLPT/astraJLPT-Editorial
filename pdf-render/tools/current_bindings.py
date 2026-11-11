"""Derive rendition hashes from current editorial fields, never history.

Authored layout hashes bind to editorial-only values. Applying optional ruby
changes serialization, so consumers receive hashes of that selected rendition.
Evidence and canonical field hashes continue to bind to the editorial itself.
"""
import copy
from collections import defaultdict
from bs4 import BeautifulSoup
from current_editorial import digest
from ruby_core import Projection,iter_fields


def maps(source, target, bound_question_groups=()):
    before={f['pointer']:f for f in iter_fields(source)}
    after={f['pointer']:f for f in iter_fields(target)}
    if before.keys()!=after.keys():raise ValueError('Rendition field identities changed')
    buckets=defaultdict(lambda:defaultdict(set))
    def add(owner,slot,a,b,node=False):
        for key in (None,owner,owner+'/'+slot):buckets[('node:'+str(key)) if node else key][a].add(b)
    for pointer,a in before.items():
        b=after[pointer]
        if (a['owner'],a['slot'])!=(b['owner'],b['slot']):raise ValueError('Rendition owner changed')
        add(a['owner'],a['slot'],digest(a['value']),digest(b['value']))
        if a['value']==b['value']:continue
        if not isinstance(a['value'],dict) or not isinstance(b['value'],dict):continue
        def tags(value):
            soup=BeautifulSoup(value['html'],'html.parser')
            return [n for n in soup.find_all() if not n.get('data-rubi-origin')
                    and not (n.name in ('rt','rp') and n.parent.get('data-rubi-origin'))]
        aa,bb=tags(a['value']),tags(b['value'])
        if len(aa)!=len(bb) or [n.name for n in aa]!=[n.name for n in bb]:
            raise ValueError('Ruby changed editorial element structure')
        for an,bn in zip(aa,bb):add(a['owner'],a['slot'],digest({'html':str(an)}),digest({'html':str(bn)}),True)
    # Old inferred numbering binds the entire ordered option list as well as
    # each stem. This digest is private to its question, even if two questions
    # have identical authored choices but different selected reading help.
    def choices(doc):
        return {i['id']:i['options'] for s in doc['sections'] for i in s['items'] if 'options' in i}
    aa,bb=choices(source),choices(target)
    if aa.keys()!=bb.keys():raise ValueError('Rendition choice owners changed')
    for owner,opts in aa.items():
        if opts!=bb[owner]:
            if (len(opts)!=len(bb[owner]) or any(
                    Projection(a).text!=Projection(b).text for a,b in zip(opts,bb[owner]))):
                raise ValueError('Rendition choice text or order changed')
            buckets['options-list:'+owner][digest(opts)].add(digest(bb[owner]))
    # Source-observed Old context keeps also bind the complete consecutive
    # question objects. Ruby changes their serialization, even when every
    # question, key and base text is preserved. Keep these maps owner-local;
    # the consumer still checks the exact question IDs and source evidence.
    def question_groups(doc):
        groups={}
        for section in doc['sections']:
            items=section['items']
            for index,item in enumerate(items):
                if 'content' not in item:continue
                following=[]
                for question in items[index+1:]:
                    if 'stem' not in question:break
                    following.append(question)
                if following:groups[item['id']]=following
        return groups
    aa,bb=question_groups(source),question_groups(target)
    if aa.keys()!=bb.keys():raise ValueError('Rendition context question owners changed')
    for owner,questions in aa.items():
        changed=bb[owner]
        if [q['id'] for q in questions]!=[q['id'] for q in changed]:
            raise ValueError('Rendition context question order changed')
        for a,b in zip(questions,changed):
            fixed=lambda q:{k:v for k,v in q.items() if k not in ('stem','options')}
            if fixed(a)!=fixed(b) or Projection(a['stem']).text!=Projection(b['stem']).text:
                raise ValueError('Rendition context question content or metadata changed')
        # An attached dialogue query can bind a proper initial subset. Its
        # consumer validates the exact consecutive answer labels and count.
        for count in range(1,len(questions)+1):
            buckets['questions-list:'+owner][digest(questions[:count])].add(digest(changed[:count]))
    # Phrase answer-line measures bind an entire grammatical section. Preserve
    # all its metadata and base text before rebinding that aggregate hash.
    def plain_section(section):
        result=copy.deepcopy(section)
        result['heading']=Projection(result['heading']).text
        for item in result['items']:
            for slot in ('stem','content'):
                if slot in item:item[slot]=Projection(item[slot]).text
            if 'options' in item:item['options']=[Projection(v).text for v in item['options']]
        return result
    if len(source['sections'])!=len(target['sections']):raise ValueError('Rendition section count changed')
    for a,b in zip(source['sections'],target['sections']):
        if plain_section(a)!=plain_section(b):raise ValueError('Rendition section content or metadata changed')
        buckets['section:'+a['id']][digest(a)].add(digest(b))
    # Modern spacing groups may start partway through a passage's questions.
    # Map only the explicitly bound contiguous IDs, never arbitrary object
    # hashes or a similarly worded question elsewhere in the paper.
    def bound_questions(doc,ids):
        matches=[]
        for section in doc['sections']:
            items=section['items'];positions=[n for n,i in enumerate(items) if i['id'] in ids]
            if not positions:continue
            if matches or len(positions)!=len(ids) or positions!=list(range(positions[0],positions[0]+len(ids))):
                raise ValueError('Rendition question group must be contiguous in one section')
            matches=[items[n] for n in positions]
        if [q['id'] for q in matches]!=ids or any('stem' not in q for q in matches):
            raise ValueError('Rendition question group identity changed')
        return matches
    for group in bound_question_groups:
        ids=group['items']
        if not isinstance(ids,list) or len(ids)<2 or len(ids)!=len(set(ids)):
            raise ValueError('Invalid rendition question group IDs')
        a,b=bound_questions(source,ids),bound_questions(target,ids)
        buckets['question-group:'+digest(ids)][digest(a)].add(digest(b))
    return {owner:{key:next(iter(values)) for key,values in rows.items() if len(values)==1}
            for owner,rows in buckets.items()}


def select(settings, bindings):
    """Rewrite only active consumer hash leaves; unknown/stale hashes fail later."""
    def walk(value,owner=None,key=None):
        if key in ('evidence','basis','source','provenance'):return copy.deepcopy(value)
        if isinstance(value,dict):
            owner=value.get('item_id',value.get('owner_id',owner))
            if 'owner_id' in value and 'slot' in value:owner=value['owner_id']+'/'+value['slot']
            if key=='question_groups' and 'items' in value:
                owner='question-group:'+digest(value['items'])
            return {k:walk(v,k if k in bindings and k is not None else owner,k) for k,v in value.items()}
        if isinstance(value,list):return [walk(v,owner,key) for v in value]
        if (isinstance(value,str) and key and key.endswith('sha256')
                and key not in ('canonical_sha256','value_sha256','projection_sha256')):
            if key=='options_sha256':
                return bindings.get('options-list:'+str(owner),{}).get(value,value)
            if key=='questions_sha256':
                return bindings.get('questions-list:'+str(owner),{}).get(value,value)
            if key=='section_sha256':
                return bindings.get('section:'+str(owner),{}).get(value,value)
            if key=='content_sha256' and str(owner).startswith('question-group:'):
                return bindings.get(owner,{}).get(value,value)
            node='_node_' in key or key in ('table_sha256','list_sha256')
            local='node:'+str(owner) if node else owner;global_='node:None' if node else None
            return bindings.get(local,{}).get(value,bindings.get(global_,{}).get(value,value))
        return value
    return walk(settings)
