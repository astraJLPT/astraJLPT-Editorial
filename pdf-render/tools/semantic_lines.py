"""Exact authored line boundaries over balanced inline markup."""
from collections import Counter
from model import Projection
from example_layout import slice_inline


def split_before(fragments, prefixes):
    if len(prefixes) != len(set(prefixes)):
        raise ValueError('Duplicate semantic line prefix')
    out = list(fragments)
    for prefix in prefixes:
        if not prefix or '\n' in prefix:
            raise ValueError('Invalid semantic line prefix')
        hits = [(n, p.text.index(prefix)) for n, raw in enumerate(out)
                if (p := Projection({'html': raw})).text.count(prefix) == 1]
        total = sum(Projection({'html': raw}).text.count(prefix) for raw in out)
        if total != 1 or len(hits) != 1:
            raise ValueError('Semantic line prefix must select one exact span')
        n, offset = hits[0]
        raw = out[n]; p = Projection({'html': raw})
        if not p.text[:offset].strip():
            continue
        left = slice_inline(raw, 0, offset)
        right = slice_inline(raw, offset, len(p.text))
        out[n:n+1] = [left, right]
    compact = lambda xs: ''.join(''.join(Projection({'html': x}).text.split()) for x in xs)
    ruby = lambda xs: Counter((r['base'], r['reading']) for x in xs
                             for r in Projection({'html': x}).ruby)
    if compact(out) != compact(fragments) or ruby(out) != ruby(fragments):
        raise ValueError('Semantic line split changed text or ruby')
    return out
