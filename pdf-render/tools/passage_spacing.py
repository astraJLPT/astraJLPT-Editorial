"""Presentation-only punctuation glue for explicitly spaced beginner passages."""
import html,re
from model import Projection


def prepare(value, gap_em):
    if isinstance(gap_em,bool)or not isinstance(gap_em,(int,float))or not 0<=gap_em<=2:
        raise ValueError('Invalid passage punctuation gap')
    if not gap_em:return value,[]
    raw=value['html']if isinstance(value,dict)else html.escape(value).replace('\n','<br/>')
    if 'data-passage-punctuation-gap' in raw:return value,[]
    p=Projection({'html':raw});insertions=[];offsets=[]
    # Only these sentence/phrase marks are eligible. A closing quote, explicit
    # space, hard paragraph/line boundary, or numbered-label punctuation blocks it.
    for i,ch in enumerate(p.text[:-1]):
        if ch not in '。、' or not re.fullmatch(r'[ぁ-んァ-ヶー一-龥々A-Za-z0-9０-９]',p.text[i+1]):continue
        if not p.mapping[i] or not p.mapping[i+1]:continue
        end=p.mapping[i][1]
        # The projection must not conceal a hard break between the two bases.
        between=raw[end:p.mapping[i+1][0]]
        if re.search(r'<\s*(?:br|/?p|/?div|/?section|/?li|/?t[rdh])\b',between,re.I):continue
        if re.search(r'data-(?:authored-word-gap|passage-punctuation-gap)',between):continue
        insertions.append((end,'<span data-passage-punctuation-gap="'+str(gap_em)+'"></span>'));offsets.append(i)
    if not insertions:return value,[]
    for pos,span in reversed(insertions):raw=raw[:pos]+span+raw[pos:]
    result={'html':raw}
    if Projection(result).text!=p.text:raise ValueError('Punctuation spacing changed protected text')
    return result,offsets
