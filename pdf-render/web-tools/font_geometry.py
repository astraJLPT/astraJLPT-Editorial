"""Pinned font glyph metrics for native numeral geometry, never PDF tracing."""
from functools import lru_cache
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen


@lru_cache(maxsize=None)
def glyph_metrics(path, index, features, text):
    with TTFont(path, fontNumber=index) as font:
        cmap = font.getBestCmap()
        glyphs = font.getGlyphSet()
        names = [cmap[ord(c)] for c in text]
        if 'GSUB' in font:
            table = font['GSUB'].table
            for record in table.FeatureList.FeatureRecord:
                if record.FeatureTag not in features:
                    continue
                for lookup_index in record.Feature.LookupListIndex:
                    lookup = table.LookupList.Lookup[lookup_index]
                    for subtable in lookup.SubTable:
                        mapping = getattr(subtable, 'mapping', None)
                        if mapping:
                            names = [mapping.get(name, name) for name in names]
        bounds = []
        for name in names:
            pen = BoundsPen(glyphs)
            glyphs[name].draw(pen)
            if pen.bounds:
                bounds.append(pen.bounds)
        em = font['head'].unitsPerEm
        return {
            'advance': sum(font['hmtx'][name][0] for name in names) / em,
            'top': max((b[3] for b in bounds), default=0) / em,
            'bottom': min((b[1] for b in bounds), default=0) / em,
        }


def role_metrics(model, role, text):
    style = model['style']
    spec = style['font_roles'][role]
    path = Path(spec.get('path', style['fonts'].get(spec.get('source', ''), '')))
    path=__import__('package_paths').resource(path)
    return glyph_metrics(str(path), spec.get('font_index', 0), tuple(spec.get('features', [])), text)
