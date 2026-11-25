"""Source-based Old written booklet covers and bounded missing-cover notices."""
import re
import subprocess

import fitz

from assemble import parse_anchors
from historical_era import UNITS, entry
from model import ROOT, BASE, read, write, file_hash
from richtex import text_tex

PROFILE = ROOT / 'pdf-render/schema/historical-1991-2009/shared/title-page.json'

# Reviewed H24/H25 omissions remain separate from missing unscored examples.
# These are bounded cover disclosures, not a general partial-paper fallback.
PARTIAL_COVER_DISCLOSURES = {
    'N4_12_2009': ((30, 7, 40), [
        '文字・語彙の第11～15問、第33～35問、第39～40問は未収録です。',
        '冒頭の指示文2件は暫定です。原本の冒頭例題は未回収です。']),
    'N3_2006': ((52, 7, 43), [
        '文字・語彙の第21・26・27問は未収録です。原番号を保持しています。',
        '読解・文法の第48～50問は二次資料に基づく暫定復元です。']),
    'N4_2006': ((39, 7, 40), [
        '文字・語彙の第24問は選択肢の原形を確認できず、未収録です。原番号を保持しています。']),
    'N1_2002': ((65, 23, 36), [
        '採点対象の全124問を収録しています。文字・語彙の問題IVの例題1件は未回収です。']),
    'N3_2002': ((48, 7, 43), [
        '文字・語彙の第22・24・26・28・30・33・35問は未収録です。原番号を保持しています。',
        '採点対象外の例題6件は未回収です。']),
    'N4_2002': ((36, 7, 40), [
        '文字・語彙の第19・22・23・24問は未収録です。原番号を保持しています。',
        '採点対象外の例題5件は未回収です。']),
    'N3_2000': ((50, 7, 43), [
        '文字・語彙の第21・22・23・25・31問は未収録です。原番号を保持しています。',
        '読解・文法の全50問は別の資料から収録しています。']),
    'N4_2000': ((39, 7, 40), [
        '文字・語彙の第21問は未収録です。原番号と回収済みの例題5件を保持しています。']),
}
UNGRADED_COVER_DISCLOSURES = {
    'N1_12_2009': (['reading-q008'], '読解の第8問は採点対象外です。'),
    'N2_2004': (['vocab-q044'], '文字・語彙の第44問は取消問題で、採点対象外です。'),
}


def facts(model):
    unit = model['unit']
    if unit not in UNITS or model.get('exam', {}).get('generation') != 'historical-1991-2009':
        raise ValueError('Historical title page requires an admitted historical paper')
    admitted = entry(unit)
    identity = model['public_output']
    if identity['historical_level'] != admitted['historical_level'] or identity['sitting'] != admitted['sitting']:
        raise ValueError('Historical title identity differs from admission')
    counts = {'vocabulary': 0, 'reading': 0, 'grammar': 0}
    ungraded = []
    for section in model['document']['sections']:
        task = model['tasks'][section['id']]
        kind = 'vocabulary' if section['part'] == 'vocab' else 'grammar' if task == 'grammar' else 'reading'
        for item in section['items']:
            if 'stem' in item:
                counts[kind] += 1
                if item['key'] is None:
                    ungraded.append(item['id'])
    if sum(counts.values()) != model['preservation']['question_count']:
        raise ValueError('Cover counts differ from current editorial')
    partial = model['coverage'] == 'partial_available_written'
    if partial != bool(admitted.get('partial_recovery')):
        raise ValueError('Cover must disclose the admitted partial recovery')
    notes = []
    if partial:
        from historical_era import coverage_warning
        coverage_warning(model)  # Exact retained IDs and worked-example count.
        reviewed = PARTIAL_COVER_DISCLOSURES.get(unit)
        if reviewed is None or tuple(counts.values()) != reviewed[0]:
            raise ValueError('Unreviewed historical partial-cover counts')
        notes.extend(reviewed[1])
    if ungraded:
        reviewed = UNGRADED_COVER_DISCLOSURES.get(unit)
        if reviewed is None or ungraded != reviewed[0]:
            raise ValueError('Unreviewed ungraded historical question')
        notes.append(reviewed[1])
    if unit == 'N3_2009':
        notes.append('12月実施の帰属は公式日程に基づきます。')
    return {'unit': unit, 'year': admitted['sitting']['year'], 'month': admitted['sitting']['month'],
            'historical_level': admitted['historical_level'], 'counts': counts,
            'coverage': model['coverage'], 'partial': partial, 'coverage_notes': notes,
            'editorial_sha256': model['input']['editorial_sha256'],
            'source_authentication_claim': False, 'original_cover_claim': False}


def plan(model,anchors,body_pages):
    from historical_booklets import validate
    booklets=validate(model)
    if not booklets:raise ValueError('Old complete editions require explicit written booklet covers')
    starts=[anchors[b['insert_before_section_id']]for b in booklets]
    if starts[0]!=1 or starts!=sorted(set(starts)) or starts[-1]>body_pages:
        raise ValueError('Invalid native Old booklet starts')
    if any(k.startswith('intentional-')for k in anchors):raise ValueError('Blank padding is forbidden')
    rows=[]
    for index,b in enumerate(booklets):
        start=starts[index];end=starts[index+1]-1 if index+1<len(starts)else body_pages
        if any(not start<=anchors[sid]<=end for sid in b['section_ids']):raise ValueError('Section crosses its booklet range')
        rows.append(dict(booklet=b,body_start=start,body_end=end,folio_extent=end-start+1))
    return rows


def validate_native_cover(pdf):
    """Inspect unfiltered glyph traces: text extraction omits off-page glyphs."""
    with fitz.open(pdf) as doc:
        if len(doc)!=1 or doc[0].get_text().count('astraJLPT Editorial')!=1:
            raise ValueError('Old cover must be one native page with one editorial watermark')
        page=doc[0];limit=page.rect+(-.2,-.2,.2,.2);bad=[]
        for span in page.get_texttrace():
            for code,glyph,origin,bbox in span['chars']:
                if chr(code).isspace():continue
                if not limit.contains(fitz.Rect(bbox)):
                    bad.append(dict(character=chr(code),bbox=list(bbox)))
        if bad:raise ValueError('Old cover native glyph extends beyond page: '+str(bad))
        return dict(method='unfiltered_native_glyph_trace',glyphs_inside_page=True)


def compile_cover(model,row,work,environment):
    from historical_cover_native import generate
    from historical_cover_reconstruction import resolve
    b=row['booklet'];cover=b['cover'];profile=read(PROFILE)
    if profile['profile_id']!='historical-written-source-covers' or profile['historical_appearance_claim']is not False:
        raise ValueError('Old cover profile is not the source-based bounded contract')
    directory=work/'covers'/b['booklet_id'];directory.mkdir(parents=True,exist_ok=True)
    data=facts(model)
    rendered,reconstruction=resolve(cover,data,row['folio_extent'])
    if reconstruction:
        data['coverage_notes']=data['coverage_notes']+[
            '原本の表紙は未回収です。この表紙の様式・配点・時間は同級の参考資料から推定した編集版です。']
    tex=generate(rendered,profile,model['style']['cover_common'],data,row['folio_extent'],directory/'cover.tex')
    from renditions import emit_tex
    tex.write_text(emit_tex(tex.read_text('utf-8'),model,'cover:'+b['booklet_id']),encoding='utf-8')
    engine=__import__('package_paths').engine()
    cp=subprocess.run([str(engine),'-no-shell-escape','-interaction=nonstopmode','-halt-on-error','-file-line-error','-recorder','cover.tex'],
        cwd=directory,env=environment,capture_output=True,timeout=120)
    (directory/'compile.txt').write_bytes(cp.stdout+cp.stderr)
    if cp.returncode:raise RuntimeError((cp.stdout+cp.stderr)[-4000:].decode('utf-8','replace'))
    log=(directory/'cover.log').read_text('utf-8',errors='replace')
    if re.search(r'Missing character:|Overfull \\[hv]box|undefined',log,re.I):raise ValueError('Old cover has glyph, overflow or font warnings: '+str(directory))
    pdf=directory/'cover.pdf'
    bounds=validate_native_cover(pdf)
    return pdf,dict(booklet_id=b['booklet_id'],status=rendered['status'],source_cover_status=cover['status'],style_id=rendered['style_id'],source=cover.get('source'),reconstruction=reconstruction,
        visible_disclosures=data['coverage_notes'],
        source_body_page_count=cover.get('printed',{}).get('source_body_pages'),actual_body_page_count=row['folio_extent'],
        pdf_sha256=file_hash(pdf),tex_sha256=file_hash(tex),pdf=pdf.relative_to(BASE).as_posix(),native_bounds=bounds,
        original_page_count_policy='source_wording_preserved_actual_restoration_count_disclosed_separately')


def assemble(model,body_path,target,work,environment):
    anchors=parse_anchors(work/'paper.aux');pages=[];covers=[];mapping={};toc=[]
    with fitz.open(body_path)as body:
        rows=plan(model,anchors,len(body));out=fitz.open()
        for row in rows:
            b=row['booklet'];bid=b['booklet_id'];pdf,record=compile_cover(model,row,work,environment)
            with fitz.open(pdf)as front:out.insert_pdf(front)
            new_cover=len(out);record['final_pdf_page']=new_cover;covers.append(record)
            pages.append(dict(pdf_page=new_cover,kind='source_cover'if b['cover']['status']=='source_transcribed'else'reconstructed_cover',booklet_id=bid))
            toc.append([1,('文字・語彙'if bid=='vocabulary'else'読解・文法')+' — '+('source cover'if b['cover']['status']=='source_transcribed'else'inferred 1999-style cover'),new_cover])
            out.insert_pdf(body,from_page=row['body_start']-1,to_page=row['body_end']-1,final=0)
            for p in range(row['body_start'],row['body_end']+1):
                final=new_cover+p-row['body_start']+1;mapping[p]=final
                pages.append(dict(pdf_page=final,kind='body',booklet_id=bid,body_pdf_page=p,body_folio=p-row['body_start']+1))
        if sorted(mapping)!=list(range(1,len(body)+1)):raise ValueError('Old assembly omitted or duplicated a body page')
        final_anchors={k:mapping[p]for k,p in anchors.items()if p in mapping}
        out.set_toc(toc)
        out.set_metadata({'title':model['public_output']['public_title'],'author':'astraJLPT Editorial',
          'subject':model.get('partial_warning')or'Old JLPT written edition with source-transcribed or inferred covers and retained uncertainty.'})
        out.save(target,garbage=4,deflate=True,no_new_id=True,use_objstms=1);out.close()
    record=dict(unit=model['unit'],status='assembled_pending_visual_review',page_count=len(pages),cover_pages=len(covers),body_pages=len(mapping),
      body_input_sha256=file_hash(body_path),output_sha256=file_hash(target),covers=covers,facts=facts(model),
      profile=dict(path=PROFILE.relative_to(ROOT).as_posix(),sha256=file_hash(PROFILE)),anchors=final_anchors,pages=pages,
      blank_policy='none',size_bytes=target.stat().st_size,size_target_bytes=1500000,native_body_copy=True,
      count_policy='source_count_verbatim_and_separate_actual_booklet_extent',body_copy='contiguous_ranges_shared_source_map')
    write(work/'assembly.json',record)
    return record
