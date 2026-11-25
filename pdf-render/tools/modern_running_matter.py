"""Truthful generated-booklet headers; observed local prefixes remain controls."""
import re

ROMAN={'N1':'I','N2':'II','N3':'III','N4':'IV','N5':'V'}
LABELS={'combined_written':'言・読','vocabulary':'げ（も・ご）','language_knowledge':'言（文）・読'}

def resolve(model):
    style=model['style']
    if style.get('running_matter'):return style['running_matter']
    policy=style.get('running_header_policy')
    if not policy:return None
    if policy!={'enabled':True,'identity':'publication_or_sitting','folio':'generated_booklet','placement':'alternating_outer'}:
        raise ValueError('Unsupported shared running header policy')
    from unit_identity import legacy_unit
    unit=model['unit'];level,month,year=legacy_unit(unit).split('_')
    pub=model.get('publication')or{}
    if pub.get('kind') in ['sample', 'practice_set']:
        from h28_identity import validate_publication
        validate_publication(unit, pub)
        identity = (f"2009 - Sample - {ROMAN[level]}" if pub['kind']=='sample' else
                    f"{'2011/2012' if level=='N1' else '2011'} - Practice - {ROMAN[level]}")
        basis = 'Explicit publication/practice identity; no complete historical-sitting claim.'
    elif pub.get('kind')=='workbook':
        if not isinstance(pub.get('year'),int)or pub.get('sitting')is not None:raise ValueError('Untruthful workbook header identity')
        identity=f"{pub['year']} - WB - {ROMAN[level]}"
        basis='Publication registry workbook year; WB means workbook; legacy owner date is not a sitting claim.'
    else:
        if month not in ['07','12']or not re.fullmatch(r'20\d{2}',year):raise ValueError('Unknown sitting metadata')
        identity=f"{year[-2:]} - {'1'if month=='07'else'2'} - {ROMAN[level]}"
        basis='Year, sitting and level from admitted owner identity; source-like format is an inferred restoration policy.'
    booklets={s['booklet']for s in model['layout']['sections'].values()}
    if booklets-set(LABELS):raise ValueError('Unknown header booklet')
    return {'booklet_prefixes':{b:identity+' - '+LABELS[b]for b in sorted(booklets)},
        'page_number':'renderer_booklet','basis':'inferred_metadata_prefix_generated_page',
        'evidence':{'authority':'pdf-render/handoff_13_cases.md#h13-c25','policy':'shared_running_header_policy','identity_basis':basis,
            'comparisons':['N5_12_2025 existing correct running family','N4_07_2025 approved physical14'],
            'limitation':'Inferred formatting; generated booklet folio; no new source-authentication claim.'}}
