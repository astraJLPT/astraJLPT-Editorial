"""Deterministic local website adapter for the current Modern PDF model.

Run using ../pdf-render/runtime/venv/Scripts/python.exe -B tools/build.py.
Only writes inside astraJLPT. The audited editorial and renderer are read-only.
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import collections, copy as copy_module, hashlib, html, json, re

HUB = Path(__file__).resolve().parents[2]
SITE = HUB/'astraJLPT'
WEB = HUB/'pdf-render'
sys.path.insert(0, str(HUB / 'pdf-render/tools'))
import model
from ruby_core import KANJI_RE
from richtex import RichTeX, remove_number
from example_layout import slice_inline
from tex_html import source_html
from passage_roles import restore_note_links
from document_roles import resolve as resolve_document_role
from bs4 import BeautifulSoup, NavigableString
import fitz
from reader_contract import resolve_metrics, PRESETS, physical_items, validate_pdf_source
from tex_html import render_inline, render_heading, render_section_heading, label_only_stem, prepare_bound_inline
from semantic_html import (render_dialogue, prepare_semantic_value, mark_introduction,
                           wrap_tail, paired_frames, email_frame,
                           present_tables, prepare_table_values, has_printed_options, audit_layout, add_style, pt, gap)
from settings_ui import settings as settings_markup, MARKS
from review_ui import registers as review_registers
from theme_colors import prepare as prepare_themes, theme_css
from size_report import measure_site
from collection import UNITS, CONFIG, ENTRIES, PATH as COLLECTION_PATH, release_for, date_info, domains, validate_identity
from public_paths import RENAMED,html_path,site_pdf,stem as public_stem
from web_star import star_data

VENDOR = WEB / 'web-vendor/design-lab'
INPUTS = {}
GENERATED = []

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def track(p):
    p = Path(p).resolve()
    INPUTS[p.as_posix()] = sha(p)
    return p
def read(p): return json.loads(track(p).read_text(encoding='utf-8-sig'))
def esc(v): return html.escape(str(v), quote=True)
def safe_json(v): return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':')).replace('<', '\\u003c')
def write(name, data):
    p = (SITE / name).resolve()
    assert p.is_relative_to(SITE.resolve())
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, bytes): p.write_bytes(data)
    else: p.write_text(data, encoding='utf-8', newline='\n')
    GENERATED.append(name)
    return p
def copy(source, target): return write(target, track(source).read_bytes())
def compose(unit):
    m=model.compose(unit,mode='auto',component='written')
    validate_identity(unit,m)
    return m

def raw(v): return v['html'] if isinstance(v, dict) else esc(v).replace('\n','<br>')
def plain(v): return model.Projection(v).text

def ruby_diagnostics(m):
    """Report coverage: covered / all authored kanji occurrences, using the active release.

    Matches ruby3-20261105/final-report.md's all-written density definition.
    """
    kanji = annotated = 0
    for field in model.iter_fields(m['canonical_editorial']):
        projection = model.Projection(field['value'])
        kanji += len(KANJI_RE.findall(projection.text))
        annotated += sum(len(KANJI_RE.findall(r['base'])) for r in projection.ruby if r['reading'].strip())
    annotations = m['ruby_release']['annotations'] if m['ruby_release'] else []
    annotated += sum(len(KANJI_RE.findall(a['base'])) for a in annotations)
    return {'original': m['preservation']['existing_ruby_groups'],
            'restored': m['preservation']['project_ruby_groups'],
            'kanji': kanji, 'annotated_kanji': annotated}
def clean(v):
    soup = BeautifulSoup(raw(v), 'html.parser')
    allowed = {'p','div','section','center','caption','br','hr','u','ruby','rt','rp','h1','h2','h3','h4','table','thead','tbody','tr','th','td','ul','ol','li','strong','b','em','i','small','sup','sub','span','a'}
    for tag in soup.find_all():
        if tag.name not in allowed: raise ValueError('Unsupported content element: '+tag.name)
        for attr in list(tag.attrs):
            if attr not in {'colspan','rowspan','data-rubi-origin','data-rubi-id','data-note-label','data-note-term','data-note-definition','data-note-definition-colon','lang'}: del tag[attr]
    return str(soup)

def decorate(v, cloze=False):
    soup = BeautifulSoup(clean(v), 'html.parser')
    for t in list(soup.find_all(string=True)):
        if t.parent.name in {'rt','rp'}: continue
        pieces = re.split(r'(_(?:\s+_)*|★|\[\d+\])', str(t))
        if len(pieces)==1: continue
        out = []
        for piece in pieces:
            if piece == '★' or piece.startswith('_'):
                for x in re.findall(r'_|★',piece):
                    s=soup.new_tag('span',attrs={'class':'star-slot' if x=='★' else 'answer-slot'})
                    glyph=soup.new_tag('span',attrs={'class':'slot-glyph star-glyph' if x=='★' else 'slot-glyph'});glyph.string=x;s.append(glyph)
                    out.append(s)
            elif re.fullmatch(r'\[\d+\]',piece):
                s=soup.new_tag('span',attrs={'class':'cloze-slot'});s.string=piece;out.append(s)
            else:out.append(NavigableString(piece))
        for n in out: t.insert_before(n)
        t.extract()
    return str(soup)

def review_markup(value,m):
    # Review context can include canonical picture choices. Use the same
    # validated shared-asset projection as the paper, not data-URL copies.
    if isinstance(value,dict) and BeautifulSoup(value['html'],'html.parser').find('img'):
        return render_inline(value,m)
    return decorate(value)

def ptvars(style):
    keys=['body_pt','baseline_pt','passage_body_pt','passage_baseline_pt','question_gap_pt','heading_pt','heading_baseline_pt','option_baseline_pt','note_pt','note_baseline_pt','note_before_pt','note_after_pt','notice_body_pt','notice_baseline_pt','paragraph_skip_pt','heading_after_pt','passage_after_pt','section_before_pt','block_before_pt','intro_after_pt','example_padding_pt','option_row_gap_pt','option_indent_em','option_label_gap_em','question_indent_em','question_label_pt']
    keys+=['heading_label_pt','heading_label_gap_em','heading_choice_gap_em','heading_slot_side_em','heading_continuation_pullback_em','question_continuation_indent_em','option_grid_width_fraction','option_reserve_em','option_continuation_pullback_em','slot_width_em','cloze_clearance_em','mixed_script_gap_em','paragraph_indent_em']
    keys+=['dialogue_quote_gap_em','dialogue_continuation_pullback_em','star_raise_em','word_space_em','heading_word_space_em','heading_horizontal_scale']
    values=['--'+k.replace('_','-')+':'+str(style[k]) for k in keys if k in style]
    for side in ['left','right','top','bottom']:
        if 'margins_mm'in style:values.append('--margin-'+side+':'+str(style['margins_mm'][side]*96/25.4)+'px')
    for key,value in style.get('question_box',{}).items():values.append('--question-box-'+key.replace('_','-')+':'+str(value))
    for key,value in style.get('cloze_box',{}).items():values.append('--cloze-box-'+key.replace('_','-')+':'+str(value))
    if 'cloze_box' in style:
        box=style['cloze_box'];rule=box.get('rule_pt',.4)
        if 'rule_pt' not in box:values.append('--cloze-box-rule-pt:'+str(rule))
        # TeX reserves 75% ascent / 25% depth inside 1.7pt padding and the rule.
        depth=(box['height_pt']-3.4-2*rule)*.25+1.7+rule
        values.append('--cloze-box-depth-pt:'+str(depth))
    choice=style.get('font_roles',{}).get('choice_numeral')
    if choice:
        values+=['--choice-scale:'+str(choice.get('horizontal_scale',1)),"--choice-features:"+(','.join("'"+f+"'"for f in choice.get('features',[])) or 'normal')]
    bubble=style.get('font_roles',{}).get('answer_bubble_numeral')
    if bubble:
        values+=['--bubble-scale:'+str(bubble.get('horizontal_scale',1)),"--bubble-features:"+(','.join("'"+f+"'"for f in bubble.get('features',[])) or 'normal')]
    return ';'.join(values)

def prepare_block(m, item, task):
    if not m.get('_web_combined_notice'):
        from notice_documents import collect
        if '_web_notice_documents' not in m:m['_web_notice_documents']=collect(m)
        group=next((g for g in m['_web_notice_documents'].values() if any(i['id']==item['id'] for i in g['items'])),None)
        if group:
            lead=group['items'][0]['id']
            if item['id']!=lead:return f'<div id="{item["id"]}" class="source-block grouped-source-anchor" data-document-lead="{lead}"></div>'
            # Collect validates every original member/direction/hash. This local
            # presentation view mirrors the native combined-notice emitter.
            view={**m,'style':copy_module.deepcopy(m['style']),'_web_combined_notice':True}
            view['workbook_typography']=copy_module.deepcopy(m.get('workbook_typography',{}))
            local=view['workbook_typography'].get('local',{})
            members={i['id']for i in group['items']}
            for row in local.get('spans',[]):
                if row['target']in members:row['target']=lead
            view['style']['block_styles'][lead]={**group['style'],'content_sha256':model.digest(group['value'])}
            view['style'].setdefault('table_styles',{})[lead]=group['table_styles']
            return prepare_block(view,{**item,'content':group['value']},task)
    bid=item['id'];meta=m['layout']['items'][bid];value=item['content'];style=m['style']
    from historical_html import block_value
    value=block_value(m,item)
    context='example' if item.get('type')=='example' else 'body'
    if meta.get('paired_label_presentation'):
        from paired_labels import prepare as prepare_paired_label
        value=prepare_paired_label(value,meta['paired_label_presentation'],item['content'])
    if meta.get('paragraph_indent_ownership'):
        from paragraph_indent_ownership import prepare as prepare_indent_ownership
        value=prepare_indent_ownership(value,meta['paragraph_indent_ownership'])
    if meta.get('vertical_flow'):
        from vertical_flow import prepare as prepare_vertical_flow
        value=prepare_vertical_flow(value,meta['vertical_flow'])
    if meta.get('soft_line_breaks'):
        from inline_layout import prepare_soft_content_breaks
        value=prepare_soft_content_breaks(value,meta['soft_line_breaks'])
    value=prepare_bound_inline(value,m,context,bid,item['content'])
    from context_html import tables as context_tables
    transferred=context_tables(m)[0].get(bid)
    if transferred:
        from question_tables import detach
        value,_=detach(value,transferred['binding'])
        if transferred['standalone']:return f'<div id="{bid}" class="source-block transferred-table-anchor" data-table-question="{transferred["question_id"]}"></div>'
        style={**style,'table_styles':{**style.get('table_styles',{}),bid:{}}}
    for key,module_name in [('decision_tree','decision_trees'),('table_captions','table_captions'),('cloze_panel_headers','cloze_panels'),('paired_structure','paired_structure')]:
        if meta.get(key):
            from importlib import import_module
            value=import_module(module_name).prepare(value,meta[key],item['content'])
    notice_style=style.get('block_styles',{}).get(bid,{})
    if notice_style.get('inset_panels',{}).get('selector')=='flow_ranges':
        from notice_layout import group_flow_panels,notice_nodes,meaningful
        nodes,panels=group_flow_panels(meaningful(notice_nodes(value,notice_style)),notice_style['inset_panels'])
        for index,panel in enumerate(panels):panel['data-notice-inset-panel']=str(index)
        value={'html':''.join(map(str,nodes))}
    if any(f['owner']==bid and f['slot']=='content' and f.get('source_plain_text') for f in m['field_manifest']) and isinstance(value,dict):
        from plain_rich_breaks import prepare as preserve_plain_breaks
        value=preserve_plain_breaks(value)
    if meta.get('shared_note_anchors'):
        from shared_note_anchors import prepare as prepare_shared_notes
        value=prepare_shared_notes(RichTeX(SITE/'work/assets'),m,item,value,meta['shared_note_anchors'])
    notes=''
    if meta.get('notes'):
        conv=RichTeX(SITE/'work/assets')
        before, after=conv.split_notes(value,meta['notes'])
        if meta['notes'].get('restored_anchors'): before=restore_note_links(before,after,meta['notes']['restored_anchors'])
        before=conv.note_markers(before,after,meta['notes'].get('inline_anchors'))
        value=before
        from note_definitions import presentation as prepare_notes
        after,_=prepare_notes(after,meta['notes'].get('separate_definitions',False))
        notes='<div class="reading-notes">'+clean(after)+'</div>'
    document_role,section_style=resolve_document_role(item,meta,task,style,style.get('section_styles',{}).get(bid))
    if document_role and document_role['role']=='email' and not meta.get('structured_document'):
        from email_family import prepare_padding
        value,_=prepare_padding(value)
    value=prepare_semantic_value(value,m,meta,bid,item['content'])
    if section_style:
        from section_html import prepare as prepare_section
        value=prepare_section(value,item['content'],section_style)
    value=prepare_table_values(value,style,bid)
    if meta.get('historical_reading_dialogue'):
        from historical_html import reading_dialogue
        markup=reading_dialogue(value,m,meta['historical_reading_dialogue'],item['content'])
    else:markup=render_inline(value,m,context,font_target=bid)
    soup=BeautifulSoup(markup,'html.parser')
    # Classify structural lines without rewriting their contents.
    for p in soup.find_all(['p','h3','h4'],recursive=False):
        txt=plain({'html':str(p)}).strip()
        if re.fullmatch(r'[（(][0-9０-９]+[）)]',txt):p['class']=['passage-label']
    mark_introduction(soup,item['content'],meta,style)
    if meta.get('paragraph_breaks'):
        from document_html import paragraph_breaks
        paragraph_breaks(soup,item['content'],meta['paragraph_breaks'])
    if meta.get('document_lines'):
        from document_html import present_lines
        present_lines(soup,item['content'],meta['document_lines'])
    if meta.get('document_fields'):
        from document_html import present_fields
        present_fields(soup,item['content'],meta['document_fields'])
    role=document_role['role'] if document_role else ''
    bs=style.get('block_styles',{}).get(bid,{})
    isnotice=bool(bs) or (item.get('type')=='notice' and bid.startswith('reading-') and role!='email')
    classes=['source-block',item.get('type','passage')]
    if task in ('reading','paired_reading','cloze') and item.get('type')!='example':classes.append('paragraph-flow')
    if role:classes.append('document-'+role)
    if item.get('type')=='example':
        classes.append('worked-example')
        if not style['examples'].get('ordinary_rules',True):classes.append('example-without-rules')
    # Block typography and table geometry follow the resolved PDF settings.
    custom=ptvars(m['web_metrics']['items'].get(bid,{}))+';'
    for k in ['body_pt','baseline_pt','paragraph_skip_pt','frame_padding_pt']:
        if k in bs:custom+='--block-'+k.replace('_','-')+':'+str(bs[k])+';'
    if 'word_space_em' in bs:custom+='--word-space-em:'+str(bs['word_space_em'])+';'
    if bs.get('title'):
        from notice_html import present as present_notice
        present_notice(soup,item['content'],bs,m)
    if meta.get('decision_tree'):
        from diagram_html import present_decision
        present_decision(soup,m,meta['decision_tree'])
    present_tables(soup,style,bid,'example' if item.get('type')=='example' else 'notice' if isnotice else 'body',bool(meta.get('example_layout')))
    if 'table_word_space_em' in bs:
        for table in soup.find_all('table'):table['style']+='--word-space-em:'+str(bs['table_word_space_em'])+';'
    frame_style=style.get('content_frames',{}).get(bid,'box')
    mode=meta.get('writing_mode',{})
    mode=mode.get('value',mode.get('mode','horizontal')) if isinstance(mode,dict) else mode
    if mode in ('vertical','vertical-rl'):
        from historical_html import enabled
        if enabled(m):
            from historical_flow_html import vertical
            vertical(soup,m,item,meta)
        else:
            from frame_html import vertical
            vertical(soup,item['content'],meta,style)
        classes.append('vertical-passage')
    elif section_style:
        from section_html import present as present_sections
        section_typography={**style,**style.get('task_overrides',{}).get(task,{})} if section_style.get('font_role')=='memo' else style
        present_sections(soup,section_style,section_typography,native_glyph_scale=m['web_metrics'].get('japanese_glyph_scale',1))
    elif task=='paired_reading':
        classes.append('paired-passage');paired_frames(soup,style,frame_style)
    elif role=='email' and not meta.get('horizontal_frame') and not meta.get('cloze_panel_headers'):
        email_frame(soup,item['content'],style,bid,m)
    elif bs.get('page_segments'):
        pass # Each bound document already owns its native frame.
    elif task=='cloze' and frame_style=='none':
        # An explicit source override removes the frame and its dimensions.
        # Keep any alignment on the captured container and all prose roles.
        for frame in soup.select('.source-native-frame'):
            frame['class']=[c for c in frame.get('class',[]) if c!='source-native-frame']
            frame.attrs.pop('data-native-frame',None)
    elif meta.get('cloze_panel_headers'):
        for panel in soup.select('[data-cloze-panel]'):
            children=panel.find_all(recursive=False)
            if len(children)!=3:raise ValueError('Cloze panel lost its label, introduction or frame')
            children[0]['class']=['passage-label'];children[1]['class']=['context-intro']
            add_style(children[1],text_indent='0',margin_bottom='0')
            frame=children[2];frame['class']=['cloze-frame'];frame.attrs.pop('data-native-frame',None)
            add_style(frame,padding=f'{pt(20)} {pt(8)} {pt(8)}',border=f'{pt(style.get("cloze_frame_rule_pt",.6))} solid currentColor',margin_top=gap(9),margin_bottom=gap(7))
            # The native panel changes NoticeFrame to ClozeFrame while keeping
            # its zero-indented correspondence paragraphs.
            for paragraph in frame.find_all('p',recursive=False):add_style(paragraph,text_indent='0')
    elif task=='cloze' or isnotice or meta.get('horizontal_frame'):
        if meta.get('horizontal_frame'):
            frames=soup.select('[data-native-frame]')
            if len(frames)>1:raise ValueError('Horizontal geometry needs one source rectangle')
            if frames:
                frame=frames[0];frame['class']=[c for c in frame.get('class',[]) if c!='source-native-frame']+['notice-frame']
                frame.attrs.pop('data-native-frame',None)
                from section_layout import flow_lines
                lines=flow_lines(list(frame.contents));frame.clear()
                for line in lines:frame.append(line)
            else:frame=wrap_tail(soup,'notice-frame')
            if role=='email':add_style(frame,font_size='inherit',line_height='inherit')
        else:frame=wrap_tail(soup,'cloze-frame' if task=='cloze' else 'notice-frame')
        default_rule=style.get('cloze_frame_rule_pt',.6) if task=='cloze' else .45
        if document_role:default_rule=document_role['parameters'].get('frame_rule_pt',default_rule)
        rule=bs.get('frame_rule',{'style':'single','width_pt':default_rule})
        from table_html import rule_css
        add_style(frame,border=rule_css(rule))
        if rule['style']=='single':add_style(frame,border_width=pt(rule['width_pt']))
        if task=='cloze':
            # ClozeFrameBox uses an outward nominal-em margin, 8pt side
            # padding, and distinct top/bottom padding (components.tex).
            add_style(frame,padding_left=pt(8),padding_right=pt(8),
                      padding_top=pt(bs.get('frame_top_pt',20)),
                      padding_bottom=pt(bs.get('frame_bottom_pt',8)))
        for side,key in [('top','frame_top_pt'),('bottom','frame_bottom_pt')]:
            if key in bs:add_style(frame,**{'padding_'+side:pt(bs[key])})
        if bs.get('title'):
            from notice_html import frame_geometry
            frame_geometry(frame,bs,m)
        for ul in frame.find_all(['ul','ol']):
            add_style(ul,padding_left=f'calc(var(--nominal-em) * {bs.get("list_indent_em",1.5)})')
    if meta.get('horizontal_frame'):
        from frame_html import horizontal
        horizontal(soup,item['content'],meta['horizontal_frame'])
    # Examples that already carry printed options do not acquire duplicate choices.
    if item.get('type')=='example':
        from example_html import source_options
        source_options(soup,item,style,task)
    opts=''
    if item.get('options') and not has_printed_options(value,item['options']):
        opts='<div class="example-options">'+''.join(f'<span><span class="example-choice-number"><span>{n}</span></span>　{render_inline(o,m,"example",bid+"/options/"+str(n-1))}</span>'for n,o in enumerate(item['options'],1))+'</div>'
        choices=BeautifulSoup(opts,'html.parser').div
        if task in ('usage','paraphrase'):choices['style']='grid-template-columns:1fr'
        answer=next((p for p in soup.find_all(['p','div'],recursive=False) if re.search('かいとう|解答',plain({'html':str(p)}))),None)
        if answer:answer.insert_before(choices)
        else:soup.append(choices)
        opts=''
    if item.get('type')=='example':
        from example_html import present as present_example
        custom+=present_example(soup,style,meta,task)+';'
        if item.get('options') and has_printed_options(value,item['options']):
            from example_html import bind_printed_options
            bind_printed_options(soup,item,m)
    if item.get('type')=='example' and meta.get('example_layout'):
        if re.sub(r'\s+','',plain(value))!=re.sub(r'\s+','',plain(item['content'])):
            # A source-bound worked diagram can move fragments into rows. Keep
            # its linear canonical reading and independently verify the diagram.
            canonical='<div class="source-literal sr-only">'+clean(item['content'])+'</div>'
            soup=BeautifulSoup(canonical+'<div class="example-rendered visual-only" aria-hidden="true">'+str(soup)+'</div>','html.parser')
    for n in soup.select('[data-note-label]'):
        label=n['data-note-label'];n['class']=[*n.get('class',[]),'annotated-term']
        base=soup.new_tag('span',attrs={'class':'annotation-base'})
        for child in list(n.contents):base.append(child.extract())
        n.append(base);note=soup.new_tag('span',attrs={'class':'annotation-label'});note.string=label;n.append(note)
    from historical_html import present_block,state as old_state,block_geometry
    present_block(soup,m,item)
    custom+=block_geometry(m,item,task)
    old=old_state(m)
    if old and old['numbering'] and bid in old['numbering']['contexts'] and plain(value)!=plain(item['content']):
        soup=BeautifulSoup('<div class="source-literal sr-only">'+source_html(item['content'])+'</div><div class="visual-only" aria-hidden="true">'+str(soup)+'</div>','html.parser')
    return f'<div id="{bid}" class="{" ".join(classes)}" style="{custom}" data-source-id="{bid}">{soup}{opts}{notes}</div>'

def question(m,q,task,orders):
    qid=q['id'];label=m['layout']['items'][qid]['printed_label'];label=label.get('text',label.get('value',label)) if isinstance(label,dict) else label
    if isinstance(label,dict):raise ValueError('Unsupported printed label '+str(label))
    binding=m['layout']['items'][qid].get('dialogue')
    bound=prepare_bound_inline(q['stem'],m,'question',qid)
    from memo_html import prepare as prepare_embedded_document
    bound=prepare_embedded_document(bound,m,q)
    label_spec=m['layout']['items'][qid]['printed_label']
    source_prefix=label_spec.get('source_prefix') if isinstance(label_spec,dict) else None
    if source_prefix:
        remove_number(q['stem'],source_prefix)
        # The exact prefix hash binds the canonical field before inline roles.
        number,value=remove_number(bound,{**source_prefix,'stem_sha256':model.digest(bound)})
    else:
        from historical_html import leading_content
        number,value=(None,bound) if leading_content(m,q) or m['layout']['items'][qid].get('historical_answer_list') else remove_number(bound)
    if number is not None and str(number)!=str(label):raise ValueError('Printed label differs from stem prefix: '+qid)
    from historical_html import remove_inferred_prefix,question_label as old_question_label
    value=remove_inferred_prefix(value,m,q)
    prefix=''
    if plain(bound)!=plain(value):
        original=plain(bound);remaining=re.sub(r'\s+','',plain(value));compact=re.sub(r'\s+','',original)
        if not compact.endswith(remaining):raise ValueError('Question prefix removal changed content: '+qid)
        count=len(compact)-len(remaining);length=0
        while count and length<len(original):
            if not original[length].isspace():count-=1
            length+=1
        while length<len(original) and original[length].isspace():length+=1
        prefix='<span class="source-literal sr-only">'+esc(original[:length])+'</span>'
    if 'question_table_before_pt' in m['style']:
        from question_displays import prepare as prepare_question_displays
        value=prepare_question_displays(value,qid)
    if m['style'].get('table_styles',{}).get(qid):value=prepare_table_values(value,m['style'],qid)
    stem=render_dialogue(value,m,binding,None) if binding else render_inline(value,m,'question',font_target=qid)
    stem=prefix+stem
    if '<table' in stem:
        stem=BeautifulSoup(stem,'html.parser');present_tables(stem,m['style'],qid);stem=str(stem)
    if qid in m['style'].get('embedded_documents',{}):
        from memo_html import present as present_embedded_document
        soup=BeautifulSoup(stem,'html.parser');present_embedded_document(soup,m,q);stem=str(soup)
    stem_class='question-content'
    if binding:stem_class+=' dialogue-content'
    label_attrs=' aria-hidden="true"' if prefix else ''
    coalesced=m['style'].get('coalesced_cloze_labels',{}).get(qid)
    if coalesced and (coalesced['stem_sha256']!=model.digest(q['stem']) or coalesced['label']!=str(label)):
        raise ValueError('Stale coalesced cloze label: '+qid)
    if coalesced or label_only_stem(q['stem'],label,task):
        stem='<span class="source-literal sr-only">'+stem+'</span>'
        stem_class+=' label-only'
        label_attrs=' aria-hidden="true"'
    columns=1 if task in {'reading','paired_reading','information_retrieval','usage'} else 4
    opts=[]
    gradable=q.get('key') in (1,2,3,4)
    availability='' if gradable else ' disabled aria-describedby="ungraded-'+qid+'"'
    for n,o in enumerate(q['options'],1):
        rid=qid+'-'+str(n);correct=str(n==q['key']).lower()
        option=render_inline(o,m,"option",qid+"/options/"+str(n-1))
        if m['layout']['items'][qid].get('option_money_columns'):
            from table_html import option_money
            option=option_money(option,q['options'],m['layout']['items'][qid]['option_money_columns'],n-1)
        opts.append(f'<div class="option-item"><input class="answer-radio" type="radio" name="{qid}" id="{rid}" value="{n}" data-correct="{correct}"{availability}><label class="option" for="{rid}"><span class="option-number">{n}</span><span class="option-text">{option}</span><span class="option-feedback" aria-hidden="true"></span><span class="sr-only result-text result-correct">Correct</span><span class="sr-only result-text result-wrong">Incorrect; try again</span></label></div>')
    order=orders.get(m['unit']+':'+qid);reveal='<aside class="star-solution" aria-label="STAR answer order">'+' → '.join(map(str,order['order']))+'</aside>'if order and order['order'] else '<span class="star-unavailable control-help">Full STAR order under review.</span>' if order else ''
    ungraded='' if gradable else f'<p id="ungraded-{qid}" class="control-help ungraded-note">Answer key unavailable; this question is not graded.</p>'
    from context_html import question_table
    table=question_table(m,qid)
    label,kind=old_question_label(m,q,label)
    markup=f'<article id="{qid}" class="question" style="{ptvars(m["web_metrics"]["items"][qid])}" data-question-id="{qid}" data-key="{q["key"]}" data-gradable="{str(gradable).lower()}" data-native-cols="{columns}"><span class="margin-answer" aria-hidden="true"></span><div class="q-stem"><span class="question-no"{label_attrs}>{esc(label)}</span><div class="{stem_class}" id="stem-{qid}">{stem}</div></div>{table}<div class="options-grid" role="radiogroup" aria-labelledby="stem-{qid}" style="--option-columns:{columns}">{"".join(opts)}</div>{ungraded}{reveal}<span class="answer-announcement sr-only" role="status"></span></article>'
    from historical_html import present_question,figure
    return present_question(markup,m,q,task,kind)+figure(m,qid)

def paper(m,orders):
    parts=[];nav=[];questions=[];current=''
    for s in m['document']['sections']:
        if not s['items'] and not plain(s['heading']).strip():
            parts.append(f'<section id="{s["id"]}" class="source-empty-section" hidden><h2 class="section-heading"></h2></section>')
            continue
        task=m['tasks'][s['id']];domain='reading'if task in {'reading','paired_reading','information_retrieval'} else 'grammar'if task in {'grammar','sentence_composition','cloze'}else 'vocab'
        if domain!=current:nav.append((s['id'],{'vocab':'語彙','grammar':'文法','reading':'読解'}[domain]));current=domain
        style=model.merge_defaults(m['style'],m['style']['task_overrides'].get(task,{}))
        style.update(m['web_metrics']['sections'][s['id']])
        section=[f'<section id="{s["id"]}" class="exam-section" data-task="{task}" style="{ptvars(style)}">{render_section_heading(s["heading"],m,s["id"])}']
        for it in physical_items(s,task):
            if 'stem'in it:section.append(question(m,it,task,orders));questions.append({'id':it['id'],'key':it['key'],'binding':model.digest(it)})
            else:section.append(prepare_block(m,it,task))
        section.append('</section>')
        from historical_flow_html import group_figures
        parts.append(group_figures(''.join(section),m))
    from reader_contract import preserve_answer_bindings
    questions=preserve_answer_bindings(m,questions)
    from label_separators import emit_html as emit_label_separators
    markup=emit_label_separators(''.join(parts))
    from renditions import variant,html_without_ruby
    if variant(m)=='norubi':
        markup,count=html_without_ruby(markup)
        m.setdefault('rendition_emissions',[]).append({'component':'html_body','removed_ruby_groups':count})
        from image_html import project_rendition
        markup=project_rendition(markup,m)
    return markup,nav,questions


def shell(title,body,themes,prefix='',reader=False,data=None,nav='',catalog=False,font_stylesheet='assets/fonts.css'):
    attrs='class="reader-page"'if reader else 'class="catalog-page"'
    header_settings='' if reader else settings_markup(themes,labelled=catalog)
    result=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="dark light"><title>{esc(title)} · astraJLPT</title><link rel="icon" href="{prefix}assets/favicon.png" type="image/png"><link rel="stylesheet" href="{prefix}{font_stylesheet}"><link rel="stylesheet" href="{prefix}assets/themes.css"><noscript><link rel="stylesheet" href="{prefix}assets/themes-no-script.css"></noscript><link rel="stylesheet" href="{prefix}assets/answer-marking.css"><link rel="stylesheet" href="{prefix}assets/site.css"></head><body data-theme="astraJLPT_dark" {attrs}><a class="skip-link" href="#content">Skip to content</a><header class="topbar" id="page-top" tabindex="-1"><a class="wordmark" id="brand" href="{prefix}index.html">astra<span>JLPT</span></a>{nav}{header_settings}</header>{body}<footer class="site-footer"><button class="boar-unlock js-only" id="boar" aria-label="Toggle developer mode and older chapters" aria-pressed="false"><img src="{prefix}assets/boar.png" alt="" width="66" height="44"></button><span class="developer-only">Developer mode</span></footer><div id="toast" role="status" class="toast" hidden></div><script id="page-data" type="application/json">{safe_json(data or {})}</script><script id="theme-data" src="{prefix}assets/theme-data.js" defer></script><script src="{prefix}assets/app.js" defer></script></body></html>'''
    result=result.replace('</head>','<link rel="stylesheet" href="'+prefix+'assets/pdf-typography.css"></head>')
    if not catalog:
        result=re.sub(r'<button class="boar-unlock.*?</button>','',result)
        result=re.sub(r'<link rel="icon"[^>]+>','<link rel="icon" href="data:,">',result)
    from web_assets import version_resources
    return version_resources(result)

def font_assets(models):
    from fontTools import subset
    from fontTools.ttLib import TTFont
    text=''.join(json.dumps(m['document'],ensure_ascii=False) for m in models)+'注0123456789（）１２３４例答正しい★_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    from image_html import artwork
    text+=''.join(a.get('text','')for m in models for a in artwork(m).values())
    specs={};profiles={};unit_profiles={};registry={};subset_targets={};derivations={}
    cachepath=SITE/'work/font-subsets.json'
    cache=json.loads(cachepath.read_text()) if cachepath.exists() else {}
    charsha=hashlib.sha256(''.join(sorted(set(text))).encode()).hexdigest()
    for m in models:
        from font_profiles import role_specs,logical_font_target,font_face
        styles=m['style'];roles=role_specs(m)
        bindings={};source_bindings={}
        for name,spec in roles.items():
            p=Path(spec.get('path',styles['fonts'].get(spec.get('source',''),'')))
            p=__import__('package_paths').resource(p)
            track(p);digest=sha(p);key=(digest,spec.get('font_index',0))
            if spec.get('sha256') and spec['sha256']!=digest:raise ValueError('Font binding changed: '+name)
            source_target=logical_font_target(digest,key[1])
            if key not in specs:
                target=source_target+'2';dst=SITE/target
                cachekey=digest+':'+str(key[1])+':'+charsha+':all-layout-woff2-v1'
                if not(dst.exists() and cache.get(cachekey)==sha(dst)):
                    f=TTFont(p,fontNumber=key[1],recalcTimestamp=False)
                    options=subset.Options();options.flavor='woff2';options.layout_features=['*'];options.recalc_timestamp=False
                    sub=subset.Subsetter(options=options);sub.populate(text=text);sub.subset(f);f.flavor='woff2'
                    dst.parent.mkdir(parents=True,exist_ok=True);f.save(dst);cache[cachekey]=sha(dst)
                subset_sha=sha(dst)
                derived={'source_sha256':digest,'font_index':key[1],'subset_sha256':subset_sha}
                canonical=subset_targets.get(subset_sha,target)
                if canonical!=target:
                    # Both exact source binaries have independently produced
                    # identical bytes. Share only that derived web payload;
                    # retain each source identity and the role's source path.
                    if dst.read_bytes()!=(SITE/canonical).read_bytes():raise ValueError('Font subset hash collision')
                    previous=json.loads((SITE/'build-manifest.json').read_text('utf8'))
                    if target in previous['outputs']:raise ValueError('Previously published duplicate font needs explicit migration: '+target)
                    if dst.resolve().parent!=(SITE/'assets/fonts').resolve():raise ValueError('Font cleanup path escaped assets/fonts')
                    dst.unlink()
                    registry[canonical]['derived_sources'].append(derived)
                else:
                    GENERATED.append(target);subset_targets[subset_sha]=target
                    registry[target]={'source_sha256':digest,'font_index':key[1],'derived_sources':[derived]}
                specs[key]=canonical
            bindings[name]=specs[key]
            source_bindings[name]=source_target
        # Keep existing profile identities stable while deduplicating payloads.
        signature=safe_json(source_bindings)
        if signature not in profiles:
            target='assets/fonts.css' if not profiles else 'assets/fonts-'+hashlib.sha256(signature.encode()).hexdigest()[:16]+'.css'
            profiles[signature]=(target,bindings)
        unit_profiles[m['unit']]=profiles[signature][0]
        derivations[profiles[signature][0]]=source_bindings
    # The settings font is bundled separately; never substitute PDF paper faces.
    from fontTools.varLib.instancer import instantiateVariableFont
    ui_font=TTFont(track(__import__('package_paths').resource('astraJLPT/vendor/roboto-mono/RobotoMono.ttf')),recalcTimestamp=False)
    instantiateVariableFont(ui_font,{'wght':400},inplace=True)
    ui_font.flavor='woff2'
    target='assets/fonts/RobotoMono-Regular.woff2'
    ui_font.save(SITE/target);GENERATED.append(target)
    copy(WEB/'web-vendor/roboto-mono/OFL.txt','assets/fonts/RobotoMono-OFL.txt')
    for target,bindings in profiles.values():
        rules=[font_face(name,font,SITE) for name,font in bindings.items()]
        rules.append(font_face('Roboto Mono','assets/fonts/RobotoMono-Regular.woff2',SITE))
        write(target,'\n'.join(rules))
    write('data/font-assets.json',json.dumps({'fonts':registry,'profiles':{target:bindings for target,bindings in profiles.values()},'profile_source_targets':derivations,'units':unit_profiles},ensure_ascii=False,indent=2)+'\n')
    cachepath.write_text(json.dumps(cache,sort_keys=True),encoding='utf8')
    return unit_profiles

def reviews(m,entry,themes,font_stylesheet,assessment):
    unit=m['unit'];root=HUB/'editorial-json'/unit[:2]/unit;date=date_info(unit)
    counts={kind:sum(bool(l.strip()) for l in track(root/f'{kind}_{unit}.jsonl').read_text(encoding='utf-8-sig').splitlines()) for kind in ['unresolved_cases','principal_differences']}
    from review_sources import bundle
    target,source_links=bundle(m,HUB,copy,sha)
    rows={kind:[json.loads(l)for l in track(root/f'{kind}_{unit}.jsonl').read_text(encoding='utf-8-sig').splitlines()if l.strip()] for kind in ['unresolved_cases','principal_differences']}
    content,m['web_review']=review_registers(m,rows,'../'+target,lambda value:review_markup(value,m),source_links)
    statuses=collections.Counter(r['status'] for r in rows['unresolved_cases'])
    source_list='<ul>'+''.join(f'<li><a href="{esc(link)}">{esc(key.replace("_"," "))} source</a></li>' for key,link in source_links.items() if key!='default' and '/' not in key)+'</ul>'
    score=assessment['index'] if assessment['index'] is not None else 'Unassessed'
    breakdown=(f'<p>Evidence base {assessment["evidence_base"]} + source concerns {assessment["concern_points"]} = {score}. Concerns are uncapped; browsing order uses evidence tier before concern points.</p>' if assessment['index'] is not None else '<p>No matching completed assessment for the selected source.</p>')
    history='<details><summary>Assessment evidence and original source scores</summary><pre>'+esc(json.dumps(assessment,ensure_ascii=False,indent=2))+'</pre></details>'
    body=f'<main id="content" class="review-page"><div class="review-content"><a href="../levels/{date['catalog_level']}.html">← {date['level']} papers</a><h1>{date['level']} · {date['sitting']}</h1><p>Uncertainty index: <strong>{score}</strong> · {counts["principal_differences"]} differences · {statuses["unresolved"]} unresolved · {statuses["provisional_fix"]} provisional fixes</p>{breakdown}<p>This is an editorial evidence assessment, not a probability, an error rate or a practice score.</p>{history}<a href="../{target}" target="_blank" rel="noopener">Open principal source ↗</a>{source_list}{content}</div></main>'
    write(f'reviews/{unit}.html',shell('Developer review · '+unit,body,themes,'../',data={'review':True},font_stylesheet=font_stylesheet));return counts

def paper_navigation(unit,date,variant='regular'):
    from source_links import official_link
    if variant not in ('regular','norubi'):raise ValueError('Unknown reader variant')
    directory='pdfs-norubi' if variant=='norubi' else 'pdfs'
    label=' <span class="rendition-label">· no rubi</span>' if variant=='norubi' else ''
    return ('<div class="paper-nav"><a href="../levels/'+date['catalog_level']+'.html">← '+date['level']+' papers</a><span>'
            +date['level']+' <span class="muted">/</span> '+date['sitting']+label+'</span>'
            +f'<a href="../{site_pdf(unit,variant)}" target="_blank" rel="noopener">PDF ↗</a>'
            +(official_link(unit) if unit in RENAMED else '')+f'<a class="developer-only" href="../reviews/{unit}.html">Review</a></div>')

def main():
    from rebuild import main as rebuild
    rebuild()
if __name__=='__main__':main()
