"""Read-only projection of Modern renderer spacing into continuous HTML."""
import collections
import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path
from fontTools.ttLib import TTFont
import fitz
from model import merge_defaults, Projection
from passage_boundaries import resolve, typography, question_groups

PRESETS = {'original': {'line': 100, 'block': 100},
           'standard': {'line': 90, 'block': 75},
           'compact': {'line': 80, 'block': 50}}


def preserve_answer_bindings(m, questions):
    """Reuse installed browser tokens only for the exact accepted question content.

    Legacy tokens hashed import metadata too. The installed shells already own
    those tokens; v4 binds their values and the current semantic questions once
    per rendition, without duplicating a per-question compatibility archive.
    A later content change must explicitly establish new reader bindings.
    """
    from bs4 import BeautifulSoup
    from model import digest
    from package_paths import ROOT
    from public_paths import html_path
    from release_contract import owner
    from renditions import variant
    mode=variant(m);binding=owner(m['unit'])['reader_semantics'][mode]
    semantic=[{k:q[k] for k in ('id','stem','options','key')}
              for s in m['document']['sections']
              for q in physical_items(s,m['tasks'][s['id']]) if 'stem' in q]
    if digest(semantic)!=binding['questions_sha256']:
        raise ValueError('Reader question content changed; review answer-binding migration')
    path=ROOT/'astraJLPT'/html_path(m['unit'],mode)
    saved=json.loads(BeautifulSoup(path.read_text('utf-8'),'html.parser').select_one('#page-data').string)['questions']
    if digest(saved)!=binding['answer_tokens_sha256']:
        raise ValueError('Installed answer tokens changed; review answer-binding migration')
    if [(q['id'],q['key'])for q in saved]!=[(q['id'],q['key'])for q in questions]:
        raise ValueError('Installed answer identities, order or keys changed')
    return [{**q,'binding':old['binding']}for q,old in zip(questions,saved)]


@lru_cache(maxsize=None)
def postscript_name(path, index=0):
    with TTFont(path, fontNumber=index) as font:
        name = font['name'].getDebugName(6)
    if not name: raise ValueError('Bound font has no PostScript identity: ' + str(path))
    return name


def font_name(m, role='body'):
    spec = m['style']['font_roles'].get(role, {'source': role})
    path = Path(spec.get('path', m['style']['fonts'].get(spec.get('source', ''), '')))
    path = __import__('package_paths').resource(path)
    return postscript_name(str(path), spec.get('font_index', 0))


def same_font(pdf_name, source_name):
    return pdf_name.split('+')[-1].replace('-', '').lower() == source_name.replace('-', '').lower()


def validate_pdf_source(m, release, hub, track):
    """Bind calibration to the current composed model and pinned TeX body.

    Shared by the normal website build and optional geometry QA. This performs
    no vector extraction and does not install a second production renderer.
    """
    resolved = json.loads(track(hub / release['resolved']['path']).read_text(encoding='utf-8'))
    if hashlib.sha256((hub / release['resolved']['path']).read_bytes()).hexdigest() != release['resolved']['sha256']:
        raise ValueError('The pinned resolved model has changed: ' + m['unit'])
    if m['edition'] != resolved['edition'] or any(m[key] != resolved[key] for key in ('document', 'style', 'tasks', 'layout')):
        raise ValueError('PDF calibration needs the current document, style and layout: ' + m['unit'])
    from renditions import variant
    if variant(m)!=variant(resolved) or release.get('variant','regular')!=variant(m):
        raise ValueError('PDF calibration rendition differs from the requested paper: '+m['unit'])
    if (hub/'rubi-restore/active_release.json').is_file():
        sel=m.get('ruby_release') or {}
        if (not sel.get('id') or resolved.get('ruby_release')!=sel or release.get('ruby_release_id')!=sel['id'] or
                release['current_editorial']['sha256']!=m['input']['editorial_sha256'] or
                release['selected_ruby']['sha256']!=sel['overlay_sha256']):
            raise ValueError('PDF calibration needs the exact selected editorial and ruby sidecar: '+m['unit'])
        public=dict(m['public_output'],body_path=(hub/release['diagnostic_body']['path']).relative_to(hub/'pdf-render').as_posix())
        if release.get('public_identity')!=public:
            raise ValueError('Written release public identity does not match the composed owner: '+m['unit'])
    # H28-rebuilt modern owners pin the body directly; retained releases also
    # carry a candidate body. Validate every supplied binding, never guess a
    # path or choose an older release when the metadata shape changes.
    bodies = [value for value in (release.get('candidate', {}).get('body'), release.get('diagnostic_body')) if value]
    if not bodies:
        raise ValueError('No pinned TeX body PDF: ' + m['unit'])
    if len({value['sha256'] for value in bodies}) != 1:
        raise ValueError('Conflicting TeX body PDF bindings: ' + m['unit'])
    for value in bodies:
        path = track(hub / value['path'])
        if hashlib.sha256(path.read_bytes()).hexdigest() != value['sha256']:
            raise ValueError('The pinned TeX body PDF has changed: ' + m['unit'])
    return path

def physical_items(section, task):
    """Mirror build.py's information-task placement, not JSON serialization."""
    items=section['items']
    return ([i for i in items if 'stem' in i]+[i for i in items if 'content' in i]) if task=='information_retrieval' else items

def resolve_metrics(m, pdf):
    style=m['style']; sections={}; items={}
    # LuaTeX-ja's Japanese scale is visible in the released PDF. Measure that
    # release, rather than borrowing the design lab's sample font size.
    face=font_name(m)
    with fitz.open(pdf) as doc:
        sizes=collections.Counter(round(s['size'],6) for page in doc
            for b in page.get_text('dict')['blocks'] if 'lines' in b
            for line in b['lines'] for s in line['spans']
            if same_font(s['font'],face) and re.search(r'[\u3040-\u30ff\u4e00-\u9fff]',s['text']))
    expected=style['body_pt']*72/72.27
    candidates=[size for size in sizes if .9 < size/expected < 1.05]
    if not candidates:raise ValueError('No bound body-font size found in PDF: '+m['unit']+' '+face)
    body_bp=min(candidates,key=lambda x:abs(x-expected*.9622))
    scale=body_bp/expected
    groups,_,_=question_groups(m)
    gaps={qid:g['question_gap_pt'] for g in groups.values() for qid in g['items']}
    seen_section=False
    historical=m.get('exam',{}).get('generation')=='historical-1991-2009'
    if historical:
        from historical_page_relationships import collect as page_relationships
        from historical_prose import question_citations
        from context_introductions import collect as context_introductions
        independent,_=page_relationships(m)
        citations=question_citations(m)
        introductions=context_introductions(m)
    for index,section in enumerate(m['document']['sections']):
        task=m['tasks'][section['id']]; local=style.get('task_overrides',{}).get(task,{})
        st=merge_defaults(style,local); meta=m['layout']['sections'][section['id']]
        first=next((i for i in section['items'] if 'content'in i and i['type']!='example'),None)
        labeled=task=='reading' and first and re.match(r'^[（(][0-9０-９]{1,2}[）)](?:\s|$)',Projection(first['content']).text.strip())
        heading=local.get('heading_after_labeled_pt',local.get('heading_after_pt',style.get('heading_after_pt',6))) if labeled else local.get('heading_after_pt',style.get('heading_after_pt',6))
        # Page furniture is not prose. Structural page starts get two source
        # baselines; automatic pagination contributes zero additional space.
        empty=not section['items'] and not Projection(section['heading']).text.strip()
        before=0 if empty or not seen_section else meta.get('flow_before_pt',2*st['baseline_pt'])
        if empty:heading=0
        else:seen_section=True
        sections[section['id']]={'heading_after_pt':heading,'section_before_pt':before}
        pending=None; seen_context=False
        for item in physical_items(section,task):
            iid=item['id']
            if 'stem'in item:
                gap=local.get('question_gap_pt',style['usage_question_gap_pt'] if task=='usage' else style['question_gap_pt'])
                items[iid]={'question_gap_pt':pending if pending is not None else gaps.get(iid,gap)}
                pending=None
            else:
                boundary=resolve(m,item,task); bs=style.get('block_styles',{}).get(iid,{})
                ss=style.get('section_styles',{}).get(iid,{})
                vals={'block_before_pt':0,'passage_after_pt':boundary.get('after_pt',ss.get('after_pt',st.get('passage_after_pt',8)))}
                vals.update({k:boundary[k] for k in ['note_before_pt','note_after_pt'] if k in boundary})
                vals['intro_after_pt']=boundary.get('intro_after_pt',st.get('passage_intro_after_pt',23))
                if task=='reading' and item['type']!='example':
                    if historical and iid in independent:
                        vals['block_before_pt']=2*st['baseline_pt']
                    elif historical and (iid in citations or iid in introductions):
                        pass # The related context owns this boundary, as in TeX.
                    elif seen_context and style['reading_group_start']=='independent_passage':vals['block_before_pt']=2*st['baseline_pt']
                    elif seen_context and historical and style['reading_group_start']=='flow':
                        interval=style.get('reading_context_before_pt',14)
                        if type(interval) not in (int,float) or not 0<=interval<=100:raise ValueError('Invalid Old reading context gap')
                        vals['block_before_pt']=interval
                    seen_context=True
                if task=='cloze':vals['block_before_pt']=st.get('cloze_before_pt',0)
                if task=='information_retrieval':vals['block_before_pt']=2*st['baseline_pt']
                if item['type']=='example':
                    ex=st['examples'];vals.update(block_before_pt=ex.get('star_before_pt',0) if task=='sentence_composition' else 0,passage_after_pt=ex.get('after_pt',10),example_padding_pt=ex.get('ordinary_padding_pt',9))
                vals['passage_baseline_pt']=typography(m,item,task).get('baseline_pt',st.get('passage_baseline_pt',st['baseline_pt']))
                vals.update({k:bs[k] for k in ['paragraph_skip_pt'] if k in bs})
                items[iid]=vals
                pending=boundary.get('following_question_gap_pt',ss.get('following_question_gap_pt'))
    return {'tex_pt_to_css_px':96/72.27,'japanese_glyph_scale':round(scale,8),'measured_body_bp':body_bp,'measured_body_font':face,
            'presets':PRESETS,'sections':sections,'items':items,
            'page_break_policy':{'automatic_extra_pt':0,'structural_start_baselines':2,
                'standalone_notice_baselines':2,
                'description':'Continuous flow omits physical page-end whitespace and headers/footers. A break within the same question sequence adds zero extra space. New sections, independent passages, and a standalone notice after its questions use two source baselines, or an authored flow gap. Paragraphs split across PDF pages remain continuous.'}}
