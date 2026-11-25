"""Source-bound answer-slot punctuation; ordinary quotes/references stay literal."""
import re,html,json
from pathlib import Path
from functools import lru_cache
from bs4 import BeautifulSoup, NavigableString
from model import Projection, digest, ROOT
from presentation import source_binding

ROLES={'corner_answer_slot','parenthesized_answer_slot','boxed_parenthesized_answer_slot','bracket_answer_slot','tortoise_answer_slot','compact_reference_range','kana_answer_slot','dialogue_phrase_answer_line'}


KANA_PROFILE_PATH=ROOT/'pdf-render/config/historical-kana-slot-profiles.json'


@lru_cache(maxsize=1)
def kana_profiles():
    data=json.loads(KANA_PROFILE_PATH.read_text('utf8'))
    profiles=data.get('profiles',{})
    if data.get('version')!=1 or set(profiles)!={'compact','medium','wide'}:
        raise ValueError('Invalid historical kana-slot profiles')
    for spec in profiles.values():
        width=spec.get('inner_width_em')
        if set(spec)!={'inner_width_em'} or type(width)not in [int,float] or not 1.5<=width<=8:
            raise ValueError('Invalid historical kana-slot profile width')
    return profiles


def kana_parenthesis(soup,spec):
    """Bind one plain authored strong kana and its exact adjacent punctuation."""
    text=spec['text'];font=spec.get('kana_font');width=spec.get('kana_width')
    if font not in ['gothic','body'] or width not in kana_profiles() or set(spec)-{'role','text','occurrences','kana_font','kana_width'}:
        raise ValueError('Invalid source-bound kana-slot style')
    found=0
    for label in list(soup.find_all(['b','strong'])):
        if label.find_parent(attrs={'data-historical-answer-slot':True}) or label.find_parent(['ruby','rt','rp']):continue
        previous,following=label.previous_sibling,label.next_sibling
        if not isinstance(previous,NavigableString) or not isinstance(following,NavigableString):continue
        left=re.search(r'（[ \u3000]*$',str(previous));right=re.match(r'[ \u3000]*）',str(following))
        if not left or not right or left[0]+label.get_text()+right[0]!=text:continue
        if label.attrs or label.find() or not re.fullmatch('[アイウエ]',label.get_text()):
            raise ValueError('Kana slot must retain one plain strong kana')
        wrapper=soup.new_tag('span',attrs={'data-historical-answer-slot':'kana_answer_slot',
            'data-historical-kana-font':font,'data-historical-kana-width':width})
        wrapper.string=text
        previous.replace_with(NavigableString(str(previous)[:left.start()]))
        following.replace_with(NavigableString(str(following)[right.end():]))
        label.replace_with(wrapper);found+=1
    return found


def boxed_parenthesis(soup,text,width=None):
    """Keep an existing numeric box; optionally bind a measured slot width."""
    if width is not None and(type(width)not in[int,float]or not 1.5<=width<=8):raise ValueError('Invalid source-bound boxed slot width')
    found=0
    for box in list(soup.select('span[data-native-inline-box="label"]')):
        if box.find_parent(attrs={'data-historical-answer-slot':True}):continue
        previous,following=box.previous_sibling,box.next_sibling
        if not isinstance(previous,NavigableString) or not isinstance(following,NavigableString):continue
        left=re.search(r'[（(][ \u3000]+$',str(previous))
        right=re.match(r'[ \u3000]+[）)]',str(following))
        if not left or not right or left[0]+box.get_text()+right[0]!=text:continue
        if not re.fullmatch(r'[0-9]{1,3}',box.get_text()) or any(n.name not in ['b','strong'] or n.attrs for n in box.find_all(True)):
            raise ValueError('Boxed parenthesis must retain one plain numeric inline box')
        wrapper=soup.new_tag('span',attrs={'data-historical-answer-slot':'boxed_parenthesized_answer_slot'})
        if width is not None:wrapper['data-historical-slot-width']=str(width)
        previous.replace_with(NavigableString(str(previous)[:left.start()]))
        following.replace_with(NavigableString(str(following)[right.end():]))
        box.replace_with(wrapper)
        wrapper.append(NavigableString(left[0]));wrapper.append(box);wrapper.append(NavigableString(right[0]))
        found+=1
    return found


def dialogue_phrase(soup,spec):
    """Select one reply blank while leaving an identical query sample unchanged."""
    if set(spec)!={'role','text','occurrences','paragraph_text','inner_width_em'}:
        raise ValueError('Dialogue phrase requires one exact paragraph and width')
    token=spec['text'];text=spec['paragraph_text'];width=spec['inner_width_em']
    if (type(spec['occurrences'])is not int or spec['occurrences']!=1
            or not re.fullmatch(r'_+|＿+',token) or not isinstance(text,str)
            or not re.fullmatch(r'[^「」\n]{1,12}「[^「」\n]+」',text)
            or re.findall(r'(?<![A-Za-z_])_+(?![A-Za-z_])|＿+',text)!=[token]
            or type(width)not in[int,float]or not 4<=width<=10):
        raise ValueError('Invalid exact dialogue phrase answer line')
    hits=[p for p in soup.find_all('p')if Projection({'html':str(p)}).text.strip()==text]
    if len(hits)!=1 or hits[0].find(['p','div','img','table','br']):
        raise ValueError('Dialogue phrase requires one complete paragraph')
    nodes=[n for n in hits[0].descendants if isinstance(n,NavigableString)and token in str(n)]
    if (len(nodes)!=1 or str(nodes[0]).count(token)!=1
            or nodes[0].find_parent(['ruby','rt','rp','u'])
            or nodes[0].find_parent(attrs={'data-historical-answer-slot':True})
            or nodes[0].find_parent(attrs={'data-historical-text-role':True})):
        raise ValueError('Dialogue phrase blank has ambiguous or nested markup')
    node=nodes[0];left,right=str(node).split(token)
    wrapper=soup.new_tag('span',attrs={'data-historical-answer-slot':'dialogue_phrase_answer_line',
                                    'data-historical-slot-width':str(width)})
    wrapper.string=token;node.replace_with(NavigableString(left),wrapper,NavigableString(right))


def prepare(value,binding,unit,source_value=None):
    if digest(value if source_value is None else source_value)!=binding['content_sha256']:
        raise ValueError('Stale historical inline-atom binding')
    source_binding(unit,binding['evidence'])
    if not isinstance(value,(dict,str)):raise ValueError('Historical inline atoms require an exact text field')
    before=Projection(value);soup=BeautifulSoup(html.escape(value)if isinstance(value,str)else value['html'],'html.parser');soup.smooth();seen=set()
    for spec in binding['atoms']:
        role,text,count=spec['role'],spec['text'],spec['occurrences']
        if role=='dialogue_phrase_answer_line':
            key=(role,spec.get('paragraph_text'))
            if key in seen:raise ValueError('Duplicate dialogue phrase paragraph')
            dialogue_phrase(soup,spec);seen.add(key);continue
        if 'paragraph_text'in spec:raise ValueError('Paragraph selection belongs only to a dialogue phrase')
        pattern={'kana_answer_slot':r'（[ \u3000]*[アイウエ][ \u3000]*）',
                 'corner_answer_slot':r'「[ \u3000]+[A-C][ \u3000]+」',
                 'bracket_answer_slot':r'［[ \u3000]+(?:[①-⑳][ \u3000]+)?］',
                 'parenthesized_answer_slot':r'[（(](?:[ \u3000]+[A-Da-d①-⑳][ \u3000]+|[ \u3000]+)[）)]',
                 'boxed_parenthesized_answer_slot':r'(?:（[ \u3000]+[0-9]{1,3}[ \u3000]+）|\([ \u3000]+[0-9]{1,3}[ \u3000]+\))',
                 'tortoise_answer_slot':r'〔[ \u3000]+[a-z①-⑳][ \u3000]+〕',
                 'compact_reference_range':r'（[a-z]）～（[a-z]）'}.get(role,'(?!)')
        if role not in ROLES or text in seen or not re.fullmatch(pattern,text) or type(count)is not int or count<1:
            raise ValueError('Invalid historical answer-slot atom')
        if role=='parenthesized_answer_slot'and not text[1:-1].strip()and 'inner_width_em'not in spec:
            raise ValueError('Empty source parenthesis requires an explicit width')
        seen.add(text);found=0
        if role=='kana_answer_slot':
            if kana_parenthesis(soup,spec)!=count:raise ValueError('Kana answer-slot count or markup boundary changed')
            continue
        if 'kana_font'in spec or 'kana_width'in spec:raise ValueError('Kana style on a non-kana atom')
        if role=='boxed_parenthesized_answer_slot':
            if boxed_parenthesis(soup,text,spec.get('inner_width_em'))!=count:raise ValueError('Boxed answer-slot count or markup boundary changed')
            continue
        for node in list(soup.descendants):
            if not isinstance(node,NavigableString) or node.find_parent(['rt','rp','ruby']) or text not in str(node):continue
            pieces=str(node).split(text);replacement=[]
            for n,part in enumerate(pieces):
                if n:
                    span=soup.new_tag('span',attrs={'data-historical-answer-slot':role})
                    if role=='bracket_answer_slot':
                        width=spec.get('inner_width_em')
                        minimum=3 if not text[1:-1].strip() else 8
                        if type(width) not in [int,float] or not minimum<=width<=13:raise ValueError('Invalid source-bound bracketed sentence blank')
                        span['data-historical-slot-width']=str(width)
                    elif 'inner_width_em'in spec:
                        width=spec['inner_width_em']
                        if role!='parenthesized_answer_slot' or type(width)not in [int,float] or not 1.5<=width<=8:raise ValueError('Invalid source-bound parenthesized slot width')
                        span['data-historical-slot-width']=str(width)
                    if 'after_gap_em'in spec:
                        gap=spec['after_gap_em']
                        if role!='parenthesized_answer_slot' or type(gap)not in [int,float] or not 0<=gap<=2:raise ValueError('Invalid source-bound parenthesized slot after gap')
                        span['data-historical-slot-after']=str(gap)
                    span.string=text;replacement.append(span);found+=1
                replacement.append(NavigableString(part))
            node.replace_with(*replacement)
        if found!=count:raise ValueError('Historical answer-slot count or text boundary changed')
    after=Projection({'html':str(soup)})
    if before.text!=after.text or before.ruby!=after.ruby:raise ValueError('Historical atom changed protected content')
    return {'html':str(soup)}

def render(conv,node):
    if getattr(conv,'source_target_markers',False) and node.get('data-historical-answer-slot')=='boxed_parenthesized_answer_slot':
        boxes=node.select('span[data-native-inline-box="label"]')
        if len(boxes)!=1 or not re.fullmatch(r'(?:（[ \u3000]+[0-9]{1,3}[ \u3000]+）|\([ \u3000]+[0-9]{1,3}[ \u3000]+\))',node.get_text()):
            raise ValueError('Invalid boxed answer-slot consumer')
        conv.features.append(dict(kind='historical_answer_slot',role='boxed_parenthesized_answer_slot',text=node.get_text(),preserved_inline_box=True,canonical_changed=False))
        if node.has_attr('data-historical-slot-width'):
            width=float(node['data-historical-slot-width'])
            if not 1.5<=width<=8:raise ValueError('Invalid bound boxed slot consumer')
            conv.features[-1]['inner_width_em']=width
            text=node.get_text();label=conv.node(boxes[0],'body')
            return (r'{\renewcommand\HistoricalSlotOuterGap{0pt}\renewcommand\HistoricalSlotInnerWidth{'+node['data-historical-slot-width']
                +r'em}\HistoricalMarkedAnswerSlot{'+conv.text(text[0])+'}{'+label+'}{'+conv.text(text[-1])+'}}')
        return r'\mbox{'+''.join(conv.node(child,'body')for child in node.children)+'}'
    if not getattr(conv,'source_target_markers',False) or node.find() or node['data-historical-answer-slot']not in ROLES:
        raise ValueError('Invalid historical answer-slot consumer')
    text=node.get_text();role=node['data-historical-answer-slot'];middle=text[1:-1].strip()
    conv.features.append(dict(kind='historical_answer_slot',role=role,text=text,canonical_changed=False))
    if role=='dialogue_phrase_answer_line':
        width=float(node.get('data-historical-slot-width','nan'))
        if not re.fullmatch(r'_+|＿+',text)or not 4<=width<=10:
            raise ValueError('Invalid dialogue phrase consumer')
        conv.features[-1]['inner_width_em']=width
        return r'{\renewcommand\SlotWidth{'+node['data-historical-slot-width']+r'em}\Slot{}}'
    if role=='kana_answer_slot':
        font=node.get('data-historical-kana-font');profile=node.get('data-historical-kana-width')
        if not re.fullmatch(r'（[ \u3000]*[アイウエ][ \u3000]*）',text) or font not in ['gothic','body'] or profile not in kana_profiles():
            raise ValueError('Invalid historical kana-slot consumer')
        width=kana_profiles()[profile]['inner_width_em']
        conv.features[-1].update(kana_font=font,kana_width=profile,inner_width_em=width)
        label=(r'{\gtfamily\mdseries 'if font=='gothic'else r'{\mcfamily\mdseries ')+middle+'}'
        return (r'{\renewcommand\HistoricalSlotOuterGap{0pt}\renewcommand\HistoricalSlotInnerWidth{'+str(width)
            +r'em}\HistoricalMarkedAnswerSlot{'+conv.text(text[0])+'}{'+label+'}{'+conv.text(text[-1])+'}}')
    if role=='compact_reference_range':
        match=re.fullmatch(r'（([a-z])）～（([a-z])）',text)
        if not match:raise ValueError('Compact range changed')
        return (r'\HistoricalCompactReference{（}{'+match[1]+r'}{）}\hspace{.08em}～\hspace{.08em}'
                r'\HistoricalCompactReference{（}{'+match[2]+r'}{）}\hspace{.2em}')
    if role=='bracket_answer_slot':
        return conv.text(text[0])+r'\makebox['+node['data-historical-slot-width']+r'em][c]{'+conv.text(middle)+'}'+conv.text(text[-1])
    macro='HistoricalCornerAnswerSlot' if role=='corner_answer_slot' else 'HistoricalMarkedAnswerSlot'
    tex='\\'+macro+'{'+conv.text(text[0])+'}{'+conv.text(middle)+'}{'+conv.text(text[-1])+'}'
    if node.has_attr('data-historical-slot-after'):
        gap=float(node['data-historical-slot-after'])
        if role!='parenthesized_answer_slot' or not 0<=gap<=2:raise ValueError('Invalid bound parenthesized slot after-gap consumer')
        conv.features[-1]['after_gap_em']=gap
        tex=r'\hspace{\HistoricalSlotOuterGap}{\renewcommand\HistoricalSlotOuterGap{0pt}'+tex+r'}\hspace{'+node['data-historical-slot-after']+'em}'
    if node.has_attr('data-historical-slot-width'):
        width=float(node['data-historical-slot-width'])
        if role!='parenthesized_answer_slot' or not 1.5<=width<=8:raise ValueError('Invalid bound parenthesized slot consumer')
        conv.features[-1]['inner_width_em']=width
        tex=r'{\renewcommand\HistoricalSlotInnerWidth{'+node['data-historical-slot-width']+'em}'+tex+'}'
    return tex
