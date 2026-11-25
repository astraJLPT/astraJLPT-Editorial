"""Keep explicit old-format target groups together without inferring associations."""
import re
from bs4 import BeautifulSoup
from model import Projection,digest
from presentation import source_binding

def validate_heading_range(section, task, labels):
    """A preserved old-format range must describe exactly its following choices."""
    if section.get('part')!='vocab' or task not in ('vocabulary','usage'):
        raise ValueError('Invalid historical heading range family')
    try:
        first,last=map(int,labels)
        numbers=[int(q['id'].split('q')[-1])for q in section['items']if 'stem'in q]
    except (ValueError,TypeError):
        raise ValueError('Invalid historical heading range labels')
    if first>=last or numbers!=list(range(first,last+1)):
        raise ValueError('Historical heading range differs from question sequence')

def collect(model):
    if model.get('exam',{}).get('generation')!='historical-1991-2009':return {},set()
    starts={};ends=set()
    for section in model['document']['sections']:
        if section['part']!='vocab':continue
        items=section['items']
        for n,item in enumerate(items):
            if not isinstance(item.get('content'),dict):continue
            inferred=model['layout'].get('historical_numbering',{}).get('contexts',{}).get(item['id'])
            if inferred and inferred.get('mode')=='bound_underlines':
                from historical_numbering import bound_context_nodes
                bound_context_nodes(item['content'],inferred)
                following=[]
                for q in items[n+1:]:
                    if 'stem'not in q:break
                    following.append(q)
                qids=[r['question_id']for r in inferred['references']]
                if not qids:
                    if following:raise ValueError('Unbound inferred target questions')
                    continue
                if qids!=[q['id']for q in following]:raise ValueError('Inferred target group differs from following questions')
                for ref,q in zip(inferred['references'],following):
                    if (ref['source_label']!=model['layout']['items'][q['id']]['printed_label']['value']
                        or ref['target_text']!=Projection(q['stem']).text):raise ValueError('Stale inferred group target')
                starts[item['id']]=qids;ends.add(qids[-1]);continue
            refs=BeautifulSoup(item['content']['html'],'html.parser').select('u[data-reference-label], span[data-reference-parenthesized="true"]')
            if not refs:continue
            following=[]
            for q in items[n+1:]:
                if 'stem'not in q:break
                following.append(q)
            # The approved N2 1994 agriculture context has seven literal targets.
            # Every target still has to match exactly one following stem/label.
            if len(following)!=len(refs) or not 1<=len(refs)<=7:raise ValueError(f"Historical group target/question count mismatch: {model['unit']} {item['id']}; {len(refs)} targets/{len(following)} questions")
            for ref,q in zip(refs,following):
                number=model['layout']['items'][q['id']]['printed_label']['value']
                targets=ref.select('[data-reference-target="true"]')
                if len(targets)>1:raise ValueError('Historical group target is ambiguous')
                target=targets[0]if targets else ref
                label=ref.get('data-reference-label','')
                if re.fullmatch(r'（[1-9][0-9]*）',label):label=label[1:-1]
                if label!=number or Projection({'html':target.decode_contents()}).text!=Projection(q['stem']).text:raise ValueError('Historical group target/label mismatch')
            starts[item['id']]=[q['id'] for q in following];ends.add(following[-1]['id'])
    bound={iid for iid,meta in model['layout']['items'].items()if meta.get('historical_target_dialogue')}
    if bound-set(starts):raise ValueError('Target dialogue must belong to an actual Old vocabulary target group')
    return starts,ends


def target_dialogue_turns(item,binding,unit):
    """Every aligned turn is an exact complete quoted canonical line."""
    if digest(item['content'])!=binding.get('content_sha256'):
        raise ValueError('Stale historical target dialogue')
    source_binding(unit,binding['evidence'])
    text=Projection(item['content']).text
    prefix=re.match(r'^((?:問|とい)[1-9][0-9]*)([ \u3000]+|・)',text)
    if not prefix:raise ValueError('Target dialogue requires its existing group label')
    turns=text[prefix.end():].splitlines()
    if (not 2<=len(turns)<=4 or turns!=binding.get('turns')
            or any(not re.fullmatch(r'「[^\n]+」',t)for t in turns)):
        raise ValueError('Target dialogue must bind every exact quoted turn in order')
    return turns


def prose_tex(conv,item,tex,binding=None,unit=None):
    """A validated target group's existing leading label owns its hanging prose."""
    match=re.match(r'^((?:問|とい)[1-9][0-9]*)([ \u3000]+|・)',Projection(item['content']).text)
    turns=None
    if binding:
        if not getattr(conv,'source_target_markers',False):raise ValueError('Target dialogue outside Old rendering')
        turns=target_dialogue_turns(item,binding,unit)
    if not match:return tex
    prefix=conv.text(match[0])
    initial=r'\Para ' if tex.startswith(r'\Para ') else ''
    if not tex[len(initial):].startswith(prefix):
        raise ValueError('Historical target-group label emission differs from its canonical prefix')
    body=tex[len(initial)+len(prefix):]
    kana=match[1].startswith('とい')
    conv.features.append(dict(kind='historical_target_group_label',target=item['id'],label=match[1],
        label_width_em=4 if kana else 3,continuation_indent_em=3 if kana else 2,canonical_changed=False))
    from historical_typography import question_tex
    # Some secondary witnesses print a middle dot after the group number.
    # Keep that printed punctuation, while the target-group component owns
    # spacing; a vocabulary group is not a reading-passage label.
    separator=conv.text(match[2]) if match[2]=='・' else ''
    label=question_tex(match[1],'vocabulary')+separator
    if turns:
        fragments=body.split(r'\Para ')
        if len(fragments)!=len(turns)or any(not s.strip()for s in fragments):
            raise ValueError('Target dialogue lost its exact native paragraph boundaries')
        tex=''.join(r'\HistoricalTargetGroupProse{'+(label if n==0 else '')+'}{'+part+'}'for n,part in enumerate(fragments))
        conv.features.append(dict(kind='historical_target_dialogue',target=item['id'],turns=turns,content_sha256=binding['content_sha256'],turn_start_indent_em=4 if kana else 3,continuation_indent_em=3 if kana else 2,canonical_changed=False))
    else:tex=r'\HistoricalTargetGroupProse{'+label+'}{'+body+'}'
    if kana:
        tex=(r'{\renewcommand\HistoricalTargetGroupLabelWidth{4em}'
             r'\renewcommand\HistoricalTargetGroupIndent{3em}'+tex+'}')
    return tex
