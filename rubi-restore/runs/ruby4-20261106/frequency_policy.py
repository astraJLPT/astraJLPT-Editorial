"""Exact lexical-lemma/reading frequency, never a pronunciation verdict."""
from functools import lru_cache
from ruby_core import hira,KANJI_RE

def lemma_reading(surface,lemma,reading,pos):
    if surface==lemma:return reading,'unchanged_lemma'
    n=0
    while n<min(len(surface),len(lemma)) and surface[n]==lemma[n]:n+=1
    old,new=surface[n:],lemma[n:]
    kana=lambda s:all('ぁ'<=c<='ゖ' or c=='ー' for c in s)
    if not n or not kana(old) or not kana(new):return None,'non_kana_lemma_change'
    if any('変格' in p for p in pos) and KANJI_RE.search(surface):return None,'irregular_kanji_stem'
    if old and not reading.endswith(old):return None,'unmatched_inflection_suffix'
    return (reading[:-len(old)] if old else reading)+new,'checked_kana_suffix_reconstruction'

def make_lookup(tk,tokenizer,pairs):
    @lru_cache(2048)
    def tokens(text):
        return [(t.begin(),t.end(),t.surface(),t.dictionary_form(),hira(t.reading_form()),t.part_of_speech())
            for t in tk.tokenize(text,tokenizer.Tokenizer.SplitMode.C)]
    def lookup(r,projection):
        hits=[t for t in tokens(projection.text) if t[0]<=r['a']<r['b']<=t[1]]
        if len(hits)!=1:return dict(state='unknown',reason='no unique whole-token match')
        a,b,s,lemma,rd,pos=hits[0]
        # A standalone candidate supplies its proposed lexical reading. A
        # subspan must agree with the tokenizer's complete reading; both still
        # require the executing model's subsequent occurrence-level review.
        if (a,b)==(r['a'],r['b']) and s==r['base']:rd=r['rd']
        full,method=lemma_reading(s,lemma,rd,pos)
        data=dict(surface=s,lemma=lemma,token_reading=rd,reading=full,whole_span=[a,b],part_of_speech=pos,match=method)
        count=pairs.get((lemma,full)) if full else None
        if count:return dict(state='matched',word=lemma,count=count,**data)
        return dict(state='unknown',reason='exact reconstructed lemma/reading pair unavailable; unknown is not rare',**data)
    return lookup
