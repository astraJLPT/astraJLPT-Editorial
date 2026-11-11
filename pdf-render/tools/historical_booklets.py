"""Old written-cover identity and exact existing admission authority."""
from bs4 import BeautifulSoup
from reference_approvals import REGISTRY,approved_reference,sha,registry_sha
from historical_era import entry,GENERATION

BOOKLETS=('vocabulary','reading_grammar')

def text(value):
    if not isinstance(value,dict)or set(value)!={'html'}:raise ValueError('Cover text must be explicit rich text')
    soup=BeautifulSoup(value['html'],'html.parser')
    for rt in soup.find_all('rt'):rt.decompose()
    return soup.get_text()

def validate(staged):
    if staged['exam']['generation']!=GENERATION:raise ValueError('Old covers cannot be consumed by another era')
    booklets=staged['layout'].get('historical_booklets')
    if booklets is None:return None
    admitted=entry(staged['unit']);sections=staged.get('sections',staged.get('document',{}).get('sections'))
    if [b['booklet_id']for b in booklets]!=list(BOOKLETS):raise ValueError('Old written covers require the two exact written booklets')
    if [sid for b in booklets for sid in b['section_ids']]!=[s['id']for s in sections]:
        raise ValueError('Historical booklets must partition current sections exactly in order')
    for index,b in enumerate(booklets):
        if not b['section_ids']or b['insert_before_section_id']!=b['section_ids'][0]:raise ValueError('Invalid historical cover insertion anchor')
        if any(staged['layout']['sections'][sid]['booklet']!=b['booklet_id']for sid in b['section_ids']):raise ValueError('Historical booklet section mismatch')
        c=b['cover']
        if c['unit']!=staged['unit']or c['historical_level']!=admitted['historical_level']or c['booklet_id']!=b['booklet_id']:
            raise ValueError('Cover identity differs from the existing Old admission')
        if c['status']=='unavailable':
            if admitted.get('section_covers')or c['style_id']!='unwitnessed' or 'printed'in c or 'source'in c:
                raise ValueError('Unwitnessed cover cannot invent source facts or conceal an admitted cover')
            if c['admission_source']!={k:admitted[k]for k in ['source_path','source_sha256']}:
                raise ValueError('Cover absence record differs from current admission')
            if not c['reason']:raise ValueError('Missing cover needs a bounded disclosure')
            continue
        if c['status']!='source_transcribed':raise ValueError('Unknown Old cover status')
        e=c['source'];p=c['printed'];approved=approved_reference(admitted)
        if approved is None or e['source_path']!=admitted['source_path']or e['source_sha256']!=admitted['source_sha256']:
            raise ValueError('Cover witness does not have exact approved source authority')
        if (e['physical_pages']!=[admitted['section_covers'][index]]or
            not set(e['physical_pages'])<=set(approved['approved_physical_pages'])or
            e['reference_id']!=approved['reference_id']or e['approval_registry_sha256']!=registry_sha()or
            e['subject']!='written_booklet_cover'or e['historical_claim']is not False or not e['region']):
            raise ValueError('Cover page is outside its exact existing written-cover authority')
        year=str(admitted['sitting']['year'])
        if p['year_text']not in [year,year+'−2']or p['level_number']!=int(admitted['historical_level'][0]):raise ValueError('Printed cover identity mismatch')
        if c['style_id'] not in {f'four_instruction_L{p["level_number"]}',f'{p["family"]}_L{p["level_number"]}'}:
            raise ValueError('Cover style family differs from its declared observation')
        expected=4 if p['family']in {'four_instruction','bilingual_four_instruction'} else 5
        if [r['number']for r in p['instructions']]!=list(range(1,expected+1)):raise ValueError('Incomplete source cover instructions')
        if any(type(p[k])is not int or p[k]<1 for k in ['score','minutes','source_body_pages']):raise ValueError('Invalid source cover numeric fact')
        early=p['family']in {'japanese_five_instruction','bilingual_five_instruction'}
        if str(p['source_body_pages'])not in text(p['instructions'][4 if early else 3]['japanese']):raise ValueError('Printed source page count was changed')
        japanese_only=p['family']in {'four_instruction','japanese_five_instruction'}
        if not japanese_only and any(r['english']is None for r in p['instructions']):raise ValueError('Bilingual cover lost an English instruction')
        if japanese_only and any(r['english']is not None for r in p['instructions']):raise ValueError('Japanese-only cover gained invented English instructions')
        if early:
            from historical_cover_1991 import validate_printed
            validate_printed(c)
        elif any(k in p for k in ['digit_specimen','identity_fields']):raise ValueError('Early identity grid requires its observed cover family')
        if not early:
            from historical_cover_fields import validate as validate_fields
            validate_fields(c)
        if 'english_field_labels_observed'in p:
            if type(p['english_field_labels_observed'])is not bool:
                raise ValueError('English field-label observation must be boolean')
            if p['english_field_labels_observed']is False and any(k in p['labels']for k in ['registration_english','name_english']):
                raise ValueError('Absent English field labels cannot contain English label text')
        for key in ['registration_english','name_english']:
            if key in p['labels']and(not isinstance(p['labels'][key],str)or not 1<=len(p['labels'][key])<=80):raise ValueError('Invalid source-transcribed cover field label')
    return booklets
