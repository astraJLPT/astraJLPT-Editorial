"""Source-bound Old reading dialogues with speech-aligned continuations."""
import copy,hashlib,re
from bs4 import BeautifulSoup
from model import Projection,digest
from presentation import source_binding
from dialogue import candidates,lines,render as render_dialogue

def prepare(value,binding,unit,source_value=None):
    source=value if source_value is None else source_value
    if not isinstance(value,dict)or digest(source)!=binding['content_sha256']:
        raise ValueError('Stale historical reading dialogue')
    source_binding(unit,binding['evidence'])
    if Projection(value).text!=Projection(source).text or Projection(value).ruby!=Projection(source).ruby:
        raise ValueError('Historical dialogue presentation changed source projection')
    prepared=copy.deepcopy(value);label=binding.get('opening_label')
    if label:
        if not re.fullmatch(r'（[1-9]）',label):raise ValueError('Invalid historical dialogue opening label')
        soup=BeautifulSoup(prepared['html'],'html.parser');first=soup.find('p')
        text=Projection({'html':first.decode_contents()}).text
        if not text.startswith(label):raise ValueError('Changed dialogue opening label')
        from example_layout import slice_inline
        inner=BeautifulSoup(slice_inline(first.decode_contents(),len(label),len(text)),'html.parser')
        first.clear()
        for n in list(inner.contents):first.append(n.extract())
        prepared={'html':str(soup)}
        if Projection(prepared).text!=Projection(value).text[len(label):]:raise ValueError('Opening label split changed dialogue text')
    separator=binding.get('turn_separator')
    if separator not in [None,'colon']:raise ValueError('Unknown historical dialogue separator')
    found=candidates(prepared,named_colon=separator=='colon')
    if found!=binding['turns']:raise ValueError('Historical dialogue must bind every exact source speaker/turn')
    scenes=binding.get('scene_lines',[]);raw=lines(prepared)
    if set(scenes)|{t['line']for t in found}!=set(range(len(raw))):raise ValueError('Unclassified historical dialogue paragraph')
    for index in scenes:
        if type(index)is not int or not 0<=index<len(raw) or not re.fullmatch(r'（.+）',Projection({'html':raw[index]}).text):
            raise ValueError('Dialogue scene needs its exact parenthetical paragraph')
    return prepared

def render(conv,value,binding,unit,source_value=None,*,left_inset_em=0):
    if type(left_inset_em)not in [int,float]or not 0<=left_inset_em<=4:raise ValueError('Invalid historical dialogue inset')
    if not getattr(conv,'source_target_markers',False):raise ValueError('Old reading dialogue outside historical edition')
    prepared=prepare(value,binding,unit,source_value)
    structure=dict(projection_sha256=hashlib.sha256(Projection(prepared).text.encode()).hexdigest(),turns=binding['turns'],state='observed',speaker_align='left')
    tex=render_dialogue(conv,prepared,structure,scene_lines=binding.get('scene_lines',[]),named_colon=binding.get('turn_separator')=='colon')
    label=binding.get('opening_label')
    if label:
        tex=tex.replace(r'\DialogueTurn{',r'\HistoricalDialogueOpeningLabel{'+conv.text(label)+r'}\DialogueTurn{',1)
    conv.features.append(dict(kind='historical_reading_dialogue',content_sha256=binding['content_sha256'],turn_count=len(binding['turns']),scene_lines=binding.get('scene_lines',[]),opening_label=label,canonical_changed=False))
    inset=(2.5 if label else 0)+left_inset_em
    return r'\HistoricalReadingDialogue{'+str(inset)+'}{'+tex+'}'
