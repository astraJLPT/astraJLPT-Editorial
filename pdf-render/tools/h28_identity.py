"""Explicit H28 publication identities; a publication year never implies an era."""
SAMPLES = {f'N{n}_sample_2009': {'id': f'JLPT_SAMPLE_2009_N{n}', 'level': f'N{n}',
           'year': 2009, 'questions': count} for n, count in enumerate([34, 31, 29, 26, 21], 1)}
PRACTICE = {
    'N1_set_2011_2012': {'title': 'N1 — expanded practice set (2011/2012 sources)', 'year': 2011,
                   'questions': 72, 'subtitle': 'Expanded practice set', 'sources': '2011/2012 sources'},
    'N3_set_2011_2012': {'title': 'N3 — attributed July 2011 set', 'year': 2011,
                   'questions': 74, 'subtitle': 'Attributed July 2011 set', 'sources': 'Includes all 72 scored questions of the 2012 workbook'},
}


def validate_publication(unit, publication):
    kind = publication.get('kind')
    if kind == 'sample':
        spec = SAMPLES.get(unit)
        if not spec or (publication.get('id'), publication.get('year'), publication.get('sitting')) != (spec['id'], 2009, None):
            raise ValueError('Sample must identify the exact 2009 publication without a sitting')
        if publication.get('title') != f'2009 {spec["level"]} Official Sample Questions — revised 2010 JLPT':
            raise ValueError('Sample title differs from the agreed publication identity')
    elif kind == 'practice_set':
        spec = PRACTICE.get(unit)
        if not spec or publication.get('id') != unit or publication.get('year') != spec['year'] or publication.get('title') != spec['title']:
            raise ValueError('Outside the exact H28 practice identity')
        if publication.get('sitting') is not None:
            raise ValueError('Practice collection must not assert a complete historical sitting')
    else:
        raise ValueError('Not an H28 publication identity')
    return spec
