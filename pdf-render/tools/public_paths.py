"""Canonical reader IDs and approved publication PDF filenames."""
from unit_identity import canonical_unit, legacy_unit
RENAMED = {
    'N2_workbook_2012':'N2_2012.workbook', 'N4_workbook_2012':'N4_2012.workbook',
    'N5_workbook_2012':'N5_2012.workbook', 'N1_workbook_2018':'N1_2018.workbook',
    'N2_workbook_2018':'N2_2018.workbook', 'N3_workbook_2018':'N3_2018.workbook',
    'N4_workbook_2018':'N4_2018.workbook', 'N5_workbook_2018':'N5_2018.workbook',
}

def stem(unit):
    unit = canonical_unit(unit)
    return RENAMED.get(unit, unit)

def html_path(unit, variant='regular'):
    assert variant in ('regular','norubi')
    return ('papers' if variant=='regular' else 'papers-norubi')+'/'+canonical_unit(unit)+'.html'

def site_pdf(unit, variant='regular'):
    unit = canonical_unit(unit)
    assert variant in ('regular','norubi')
    suffix = '.norubi' if variant=='norubi' and unit in RENAMED else ''
    return ('assets/pdfs' if variant=='regular' else 'assets/pdfs-norubi')+'/'+stem(unit)+suffix+'.pdf'

def renderer_pdf(unit, previous, variant='regular'):
    unit = canonical_unit(unit)
    if unit not in RENAMED:return previous
    return ('output/' if variant=='regular' else 'outputnorubi/')+stem(unit)+('.pdf' if variant=='regular' else '.norubi.pdf')

def approved_transition(unit, before, after):
    return before==after or (unit in RENAMED and after==renderer_pdf(unit,before))

def publication(unit):
    unit = canonical_unit(unit)
    if unit not in RENAMED:return None
    year=int(RENAMED[unit][3:7])
    return {'id':f'JLPT_WORKBOOK_{year}_{unit[:2]}','kind':'workbook','year':year,
            'title':'Official Practice Workbook'+(' Vol. 2' if year==2018 else ''),
            'sitting':None,'level':unit[:2],
            'registry_approval_status':'approved_workbook_typography_20261109',
            'legacy_requested_sitting':{'year':int(legacy_unit(unit)[-4:]),'month':int(legacy_unit(unit)[3:5]),'coverage':'unrecovered'}}
