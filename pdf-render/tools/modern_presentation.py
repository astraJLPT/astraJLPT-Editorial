"""Source-bound optional presentation facts, independent of accepted content."""
import re
from render_scope import ENTRIES
from model import ROOT, file_hash

def source_binding(unit, evidence):
    if evidence.get('kind') == 'current_semantic_role_v2':
        from canonical_presentation import verify
        return verify(unit, evidence)
    entry = ENTRIES[unit]
    # Exact registered alternate witnesses retain their own independent page
    # partition. Selecting one never grants access to a mixed principal page.
    if entry.get('presentation_witnesses'):
        matches=[w for w in entry['presentation_witnesses'] if evidence.get('source_path')==w['source_path'] and evidence.get('source_sha256')==w['source_sha256']]
        if len(matches)!=1:raise ValueError('Presentation witness is not an admitted exact witness')
        witness=matches[0];pages=evidence.get('physical_pages',[])
        if evidence.get('state')!='inferred' or evidence.get('historical_claim') is not False or not evidence.get('region'):
            raise ValueError('Unverified witness requires an explicit inferred region')
        if not pages or len(pages)!=len(set(pages)):raise ValueError('Missing or duplicate witness pages')
        for page in pages:
            if page in witness['permitted_written_physical_pages']:continue
            regions=[r for r in witness.get('region_limits',[])if r['physical_page']==page]
            clips=[r for r in evidence.get('region_clips',[])if r.get('physical_page')==page]
            if len(regions)!=1 or len(clips)!=1:raise ValueError('Presentation witness uses an unapproved whole page')
            a=regions[0]['clip_pdf_points'];b=clips[0].get('clip_pdf_points',[])
            if len(b)!=4 or not all(isinstance(x,(int,float))and not isinstance(x,bool)for x in b) or not (a[0]<=b[0]<b[2]<=a[2] and a[1]<=b[1]<b[3]<=a[3]):raise ValueError('Presentation clip exceeds its exact written region')
        if not __import__('release_contract').verify_source(witness['source_path'],witness['source_sha256']):raise ValueError('Stale presentation witness')
        return
    if not entry.get('source_path') or evidence.get('source_path') != entry['source_path'] or evidence.get('source_sha256') != entry['source_sha256']:
        raise ValueError('Presentation witness is not the approved exact source')
    pages = evidence.get('physical_pages', [])
    permitted=entry.get('approved_written_physical_pages',[])
    if entry.get('presentation_source_role'):
        if evidence.get('state')!='inferred' or evidence.get('historical_claim') is not False or not evidence.get('region'):
            raise ValueError('Unverified/workbook structural evidence requires explicit inferred basis and region')
        permitted=entry['permitted_written_physical_pages']
    if not pages or any(p not in permitted for p in pages):
        raise ValueError('Presentation witness uses an unapproved page')
    if not __import__('release_contract').verify_source(entry['source_path'],evidence['source_sha256']):
        raise ValueError('Stale presentation witness')
