"""Native covers and compact sequential assembly without blank-page padding."""
import copy
import re
import subprocess
from pathlib import Path
import fitz
from model import BASE, file_hash, write
from cover_native import generate as generate_cover


def parse_anchors(aux):
    return {name: int(page) for name, page in re.findall(r'\\newlabel\{([^}]+)\}\{\{[^}]*\}\{(\d+)\}', Path(aux).read_text(encoding='utf-8', errors='replace'))}


def plan(model, anchors, body_pages):
    booklets = model['layout']['booklets']
    if not booklets:raise ValueError('No declared booklet anchors')
    section_ids = [s['id'] for s in model['document']['sections']]
    ids = [b['booklet_id'] for b in booklets]
    if len(ids) != len(set(ids)):raise ValueError('Duplicate booklet identity')
    for b in booklets:
        if b['insert_before_section_id'] != b['section_ids'][0]:raise ValueError('Cover anchor must precede the first semantic section')
        facts = b['cover']
        if (facts['unit'], facts['level'], facts['booklet_id'], facts['insert_before_section_id']) != (model['unit'], model['unit'][:2], b['booklet_id'], b['insert_before_section_id']):
            raise ValueError('Cover facts do not match booklet identity')
    if [sid for b in booklets for sid in b['section_ids']] != section_ids:
        raise ValueError('Booklet sections must partition the unit in order')
    starts = [anchors[b['insert_before_section_id']] for b in booklets]
    if starts[0] != 1 or starts != sorted(set(starts)):
        raise ValueError('Invalid compiled booklet starts')
    if any(name.startswith('intentional-') for name in anchors):
        raise ValueError('Blank-page anchors are forbidden; rebuild the body under the sequential policy')
    result = []
    for index, booklet in enumerate(booklets):
        for sid in booklet['section_ids']:
            if model['layout']['sections'][sid]['booklet'] != booklet['booklet_id']:
                raise ValueError('Booklet semantic identity mismatch')
        start = starts[index]
        end = starts[index+1]-1 if index+1 < len(starts) else body_pages
        kept = list(range(start, end+1))
        if not kept:raise ValueError('Empty booklet')
        result.append({'booklet': booklet, 'body_pages': kept, 'folio_extent': len(kept), 'body_start': start, 'internal_blank_pages': []})
    if set(range(1, body_pages+1)) != {p for r in result for p in r['body_pages']}:
        raise ValueError('Body page omitted from assembly')
    return result


def compile_cover(model, row, work, environment):
    booklet = row['booklet']
    facts = copy.deepcopy(booklet['cover'])
    facts['displayed_body_folios'] = row['folio_extent']
    facts['rendition']=model.get('rendition',{'variant':'regular'})
    style = model['style']['cover_styles'][facts['style_id']]
    common = model['style']['cover_common']
    publication_kind = facts.get('publication', {}).get('kind')
    year, month = (None, None) if publication_kind in ['workbook', 'sample', 'practice_set'] else (int(model['unit'][-4:]), int(model['unit'][3:5]))
    level = model['unit'][:2]
    if level in ['N4', 'N5'] and publication_kind not in ['workbook', 'sample', 'practice_set']:
        modern = (year, month) >= (2020, 12)
        mins = {'N4': [25,55] if modern else [30,60], 'N5': [20,40] if modern else [25,50]}[level]
        expected = mins[0 if booklet['booklet_id'] == 'vocabulary' else 1]
        if facts['minutes'] != expected:raise ValueError('Cover timing differs from recorded official period rule')
    directory = work / 'covers' / booklet['booklet_id']
    directory.mkdir(parents=True, exist_ok=True)
    tex = generate_cover(facts, style, common, directory / 'cover.tex')
    engine = __import__('package_paths').engine()
    result = subprocess.run([str(engine), '-no-shell-escape', '-interaction=nonstopmode', '-halt-on-error', '-recorder', 'cover.tex'], cwd=directory, env=environment, capture_output=True, timeout=120)
    (directory / 'process.log').write_bytes(result.stdout + result.stderr)
    if result.returncode:raise RuntimeError('Cover compilation failed: ' + str(directory) + '\n' + (result.stdout+result.stderr)[-1800:].decode('utf-8', 'replace'))
    log = (directory / 'cover.log').read_text(encoding='utf-8', errors='replace')
    if re.search(r'Missing character:|Overfull \\[hv]box', log):raise ValueError('Cover glyph/overflow warning: ' + str(directory))
    pdf = directory / 'cover.pdf'
    with fitz.open(pdf) as doc:
        if len(doc) != 1:raise ValueError('Cover must be exactly one page')
        if doc[0].get_text().count('astraJLPT Editorial') != 1:raise ValueError('Missing or duplicated cover mark')
    return pdf, {'booklet_id': booklet['booklet_id'], 'insert_before_section_id': booklet['insert_before_section_id'], 'displayed_body_folios': row['folio_extent'], 'original_count_provenance': facts['original_page_count_provenance'], 'style_id': facts['style_id'], 'minutes': facts['minutes'], 'tex_sha256': file_hash(tex), 'pdf_sha256': file_hash(pdf), 'pdf': pdf.relative_to(BASE).as_posix()}


def assemble(model, body_path, target, work, environment):
    anchors = parse_anchors(work / 'paper.aux')
    body = fitz.open(body_path)
    body_count = len(body)
    planned = plan(model, anchors, body_count)
    output = fitz.open()
    pages, covers, old_to_new = [], [], {}

    for row in planned:
        bid = row['booklet']['booklet_id']
        cover, record = compile_cover(model, row, work, environment)
        with fitz.open(cover) as front:output.insert_pdf(front)
        pages.append({'pdf_page': len(output), 'kind': 'cover', 'booklet_id': bid})
        record['final_pdf_page'] = len(output)
        covers.append(record)
        # Copy each body range together and retain the source-object map between
        # booklets. Never rasterize native text, tables, images or covers.
        first_new = len(output) + 1
        output.insert_pdf(body, from_page=row['body_pages'][0]-1, to_page=row['body_pages'][-1]-1, final=0)
        for original_page in row['body_pages']:
            new_page = first_new + original_page - row['body_start']
            old_to_new[original_page] = new_page
            pages.append({'pdf_page': new_page, 'kind': 'body', 'booklet_id': bid, 'body_pdf_page': original_page, 'body_folio': original_page-row['body_start']+1})
    final_anchors = {name: old_to_new[page] for name, page in anchors.items() if page in old_to_new}
    for relation in model['render_coverage']['physical_layout_overrides']:
        section = next(s for s in model['document']['sections'] if s['id'] == relation['section_id'])
        from question_tables import validate_pages
        validate_pages(model, section, final_anchors)
    from public_output import identity
    public_title = identity(model['unit'], model['input'], model['edition'])['public_title']
    suffix = ' - PARTIAL practice editorial edition' if model['coverage'] == 'partial_available_written' else ' - complete written editorial edition'
    output.set_metadata({'title': public_title + suffix, 'author': 'astraJLPT Editorial', 'subject': model.get('partial_warning') or 'Native reconstructed covers and protected JLPT practice content'})
    # Level 4 deduplicates identical font/image streams as well as dictionaries.
    # Level 3 left duplicate embedded font streams after the old per-page copy.
    output.save(target, garbage=4, deflate=True, no_new_id=True, use_objstms=1)
    output.close()
    body.close()
    report = {'unit': model['unit'], 'status': 'assembled_pending_visual_review', 'page_count': len(pages), 'body_input_sha256': file_hash(body_path), 'output_sha256': file_hash(target), 'covers': covers, 'pages': pages, 'anchors': final_anchors, 'count_policy': model['style']['cover_common']['count_policy'], 'blank_policy': 'none', 'size_bytes': target.stat().st_size, 'size_target_bytes': 1500000, 'compression': {'garbage': 4, 'deflate': True, 'use_objstms': 1, 'body_copy': 'contiguous_ranges_shared_source_map', 'rasterization': False}, 'removed_legacy_booklet_parity_pages': []}
    write(work / 'assembly.json', report)
    return report
