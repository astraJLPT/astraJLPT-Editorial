"""Consume explicit LLM-authored boundaries. No tokenizer or inference at build."""
import hashlib,html,re
from model import Projection,digest,iter_fields

def applicable(model):
    if model['unit'][:2]not in ['N4','N5']:return {}
    out={}
    for f in iter_fields(model['document']):
        task=model['tasks'][f['section']]
        if model['unit'][:2]=='N4' and task in ['reading','paired_reading','information_retrieval']:continue
        out[f['owner']+'/'+f['slot']]=f
    return out

def validate(model):
    fields=applicable(model);records=model['layout'].get('word_groups')
    authoring={f['owner']+'/'+f['slot']:f.get('authoring_content_sha256') for f in model.get('field_manifest',[])}
    # Earlier frozen fixtures may lack H11's complete inventory.
    if records is None:
        if model['schema_version'] in ['3.6.0','3.7.0'] and fields:raise ValueError('Missing authored group inventory')
        return {}
    if not isinstance(records,list):raise ValueError('Invalid authored group records')
    result={}
    for r in records:
        target=r['owner_id']+'/'+r['slot'];f=fields.get(target)
        if target in result or not f:raise ValueError('Duplicate or inapplicable authored group target')
        p=Projection(f['value'])
        if r['unit']!=model['unit'] or r['pointer']!=f['pointer'] or r['section_id']!=f['section'] or r['task']!=model['tasks'][f['section']]:raise ValueError('Wrong authored group identity')
        if digest(f['value'])!=r['rendered_sha256']or hashlib.sha256(p.text.encode()).hexdigest()!=r['projection_sha256']:raise ValueError('Stale authored group field/projection')
        if authoring.get(target) and authoring[target]!=r['canonical_sha256']:raise ValueError('Stale authored group canonical field')
        if r['basis']not in ['declared_llm_restoration','retain_audited_groups','atomic_or_structural']or not r['rationale']:raise ValueError('Missing group authoring decision')
        offsets=[b['offset']for b in r['boundaries']]
        if offsets!=sorted(set(offsets)):raise ValueError('Duplicate/unordered authored boundary')
        for b in r['boundaries']:
            n=b['offset']
            if type(n)is not int or not 0<n<len(p.text)or p.text[n-1].isspace()or p.text[n].isspace():raise ValueError('Boundary duplicates existing or structural separator')
            if any(x['start']<n<x['end']for x in p.ruby):raise ValueError('Word group splits ruby')
            if p.text[max(0,n-12):n]!=b['left']or p.text[n:n+12]!=b['right']:raise ValueError('Stale word group anchor')
            if not p.mapping[n-1]or not p.mapping[n]:raise ValueError('Boundary crosses structural node')
        result[target]=r
    if set(result)!=set(fields):raise ValueError('Unbound applicable word-group fields')
    return result

def prepare(value,original,record):
    """Map checked presentation transforms; substantive text must be identical."""
    if not record['boundaries']:return value
    before=Projection(original);after=Projection(value)
    if digest(original)!=record['rendered_sha256']:raise ValueError('Group source binding changed')
    # Only an already-consumed printed question prefix may disappear.
    a=before.text;b=after.text;prefix=0
    if record['slot']=='stem' and not ''.join(a.split())==''.join(b.split()):
        m=re.match(r'^\s*(?:[（(【\[]?[0-9０-９]{1,3}\s*[）)】\].．:：]\s*|[0-9０-９]{1,3}\s*)',a)
        if not m:raise ValueError('Unmapped question prefix')
        prefix=m.end();a=a[prefix:]
    left=[(i,c)for i,c in enumerate(a)if not c.isspace()];right=[(i,c)for i,c in enumerate(b)if not c.isspace()]
    if [c for i,c in left]!=[c for i,c in right]:raise ValueError('Presentation changed substantive grouping text')
    mapping={i+prefix:j for (i,c),(j,d)in zip(left,right)}
    raw=after.raw if after.is_html else html.escape(after.raw,quote=False).replace('\n','<span data-authored-plain-break="line">\n</span>')
    p=Projection({'html':raw});inserts=[]
    for boundary in record['boundaries']:
        n=boundary['offset'];end=mapping.get(n-1);start=mapping.get(n)
        if end is None or start!=end+1:raise ValueError('Authored group lost or duplicated by presentation')
        if any(r['start']<start<r['end']for r in p.ruby):raise ValueError('Presentation boundary splits ruby')
        pos=p.mapping[start][0]
        for r in p.ruby:
            if r['start']==start:pos=raw.rfind('<ruby',0,pos+1)
        # Put glue outside adjacent underline/bold wrappers whenever they open
        # at this exact boundary; the zero-width marker never changes text.
        prev=p.mapping[end][1];between=raw[prev:pos]
        opens=list(re.finditer(r'<(?:u|b|strong|span)\b[^>]*>',between))
        if opens:pos=prev+opens[0].start()
        inserts.append((pos,'<span data-authored-word-gap="'+boundary['id']+'"></span>'))
    for pos,marker in sorted(inserts,reverse=True):raw=raw[:pos]+marker+raw[pos:]
    out={'html':raw}
    if Projection(out).text!=after.text or Projection(out).ruby!=after.ruby:raise ValueError('Grouping changed base/ruby projection')
    return out

def verify_consumed(tex,records,sources,embedded_options):
    emitted={}
    for width,bid in re.findall(r'\\AuthoredWordGap\{([0-9.]+)\}\{([0-9a-f]{20})\}',tex):emitted.setdefault(bid,[]).append(float(width))
    expected={b['id']for r in records.values()for b in r['boundaries']};used=set();rows=[]
    if set(emitted)-expected:raise ValueError('Unknown emitted authored boundary')
    for target,r in records.items():
        mapped=[]
        for b in r['boundaries']:
            bid=b['id'];alias=None
            if bid not in emitted and target in embedded_options:
                content_target=r['owner_id']+'/content';content=Projection(sources[content_target]).text;option=Projection(sources[target]).text
                if content.count(option)!=1:raise ValueError('Ambiguous embedded group choice')
                offset=content.index(option)+b['offset']
                matches=[x for x in records[content_target]['boundaries']if x['offset']==offset]
                if len(matches)!=1:raise ValueError('Suppressed option group lacks identical embedded declaration')
                alias=matches[0]['id'];bid=alias
            if len(emitted.get(bid,[]))!=1:raise ValueError('Unused or repeated authored group: '+target+' / '+str(b['offset']))
            used.add(bid);mapped.append({'id':b['id'],'emitted_id':bid,'alias':alias,'word_space_em':emitted[bid][0]})
        rows.append({'target':target,'task':r['task'],'role':r['role'],'basis':r['basis'],'boundaries':mapped,'actual_consumer':'native AuthoredWordGap'if mapped else'existing spacing / atomic structure retained'})
    if used!=set(emitted):raise ValueError('Unaccounted emitted group')
    return rows
