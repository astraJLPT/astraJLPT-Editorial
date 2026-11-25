"""Repeatable bounded local LuaLaTeX renderer; no corpus mutation."""
import argparse,copy,json,os,re,subprocess,sys,hashlib,shutil,time
from pathlib import Path
from bs4 import BeautifulSoup
from model import BASE,ROOT,CAL,compose,read,write,digest,file_hash,Projection
from notice import render_notice
from pagination import reading_start
from presentation import task_tabs, source_binding
from wakachi import spaced_task
from richtex import heading_word_glue,RichTeX,remove_number,escape,text_tex,context_frames,OPEN_PAREN_TEX,CLOSE_PAREN_TEX,literal_parens
from numeral_roles import token as numeric_token,literal_digits,exceptions as numeral_exceptions

def environment():
 env=os.environ.copy();env['ASTRAJLPT_ROOT']=ROOT.as_posix();runtime=BASE/'runtime';bin_=__import__('package_paths').engine().parent
 env['PATH']=str(bin_)+os.pathsep+env['PATH']
 for var,rel in [('TEXMFVAR','texmf-var'),('TEXMFCONFIG','texmf-config'),('TEXMFHOME','texmf-home'),('TEXMFCACHE','texmf-var'),('TEMP','tmp'),('TMP','tmp')]:
  p=runtime/rel;p.mkdir(parents=True,exist_ok=True);env[var]=str(p)
 env['SOURCE_DATE_EPOCH']='1791504000';env['FORCE_SOURCE_DATE']='1';env['TZ']='UTC';return env

def running_prefix_tex(value):
 return r'\RunningSeparator{}'.join(text_tex(p.strip())for p in re.split(r'\s*[-−ｰー]\s*',value))

def generate(model,work):
 if model.get('selected_component','written')!='written':raise ValueError('Select the listening renderer for a listening component')
 unit=model['unit'];level=unit[:2];style=model['style'];doc=model['document'];conv=RichTeX(work/'assets',word_space_em=style.get('word_space_em',0))
 from era_registry import for_unit
 era=for_unit(unit);source_targets=era.SOURCE_TARGET_MARKERS
 conv.source_target_markers=source_targets
 conv.approved_administrative_numerals=style.get('approved_administrative_numerals',False)
 conv.workbook_font_spans=[]
 conv.historical_inline_number_box_role=style.get('historical_typography',{}).get('inline_number_box_role')
 if conv.historical_inline_number_box_role is not None and (not source_targets or conv.historical_inline_number_box_role!='main_question'):
  raise ValueError('Invalid historical inline number-box role')
 conv.question_table_before_pt=style.get('question_table_before_pt')
 historical_group_starts,historical_group_ends=era.target_groups(model)
 historical_labels,historical_options,historical_breaks={},{},set()
 historical_graph_contexts,historical_graph_questions,deferred_graph_tex={},{},{}
 historical_target_rows={};historical_example_rows={};historical_example_options={};historical_example_frames={};historical_question_stems={}
 historical_context_starts,historical_context_ends={},set()
 historical_answer_lists={}
 historical_label_answers={}
 historical_inline_dialogue_questions={}
 historical_side_figures,historical_side_questions,deferred_side_figures={},{},{}
 historical_question_citations={}
 historical_passage_starts,historical_question_boundaries={},{}
 historical_grammar_section_gaps={}
 if source_targets:
  from historical_dialogue_questions import collect as collect_inline_dialogue_questions
  historical_inline_dialogue_questions=collect_inline_dialogue_questions(model)
  from historical_figure_question import collect as collect_side_figures
  historical_side_figures,historical_side_questions=collect_side_figures(model)
  from historical_page_relationships import collect as collect_old_page_relationships
  historical_passage_starts,historical_question_boundaries=collect_old_page_relationships(model)
  from historical_prose import question_citations
  historical_question_citations=question_citations(model)
  from historical_diagrams import collect as collect_native_old_diagrams
  conv.historical_native_diagrams=collect_native_old_diagrams(model)
  from historical_artwork import collect as collect_old_artwork
  conv.historical_artworks=collect_old_artwork(model)
  from historical_source_pixels import collect as collect_source_pixels
  conv.historical_source_pixels=collect_source_pixels(model)
  from historical_spatial import collect as collect_old_spatial
  old_spatial=collect_old_spatial(model)
  from historical_numbering import collect as collect_old_numbering
  old_numbering=collect_old_numbering(model)
  from historical_metrics import parameters as historical_metric_parameters
  historical_metrics=historical_metric_parameters(style)
  conv.historical_option_label_width_em=historical_metrics['option_label_width_em']
  conv.historical_example_target_before_pt=historical_metrics['example_target_before_pt']
  conv.historical_example_target_after_pt=historical_metrics['example_target_after_pt']
  from historical_layout import collect as collect_historical_layout
  historical_labels,historical_options,historical_breaks=collect_historical_layout(model)
  from historical_layout import grammar_two_column_section_gaps
  historical_grammar_section_gaps=grammar_two_column_section_gaps(model)
  from historical_layout import collect_stems as collect_historical_stems
  historical_question_stems=collect_historical_stems(model)
  from historical_answer_lists import collect as collect_answer_lists
  historical_answer_lists=collect_answer_lists(model)
  from historical_label_answers import collect as collect_label_answers
  historical_label_answers=collect_label_answers(model)
  from historical_complex import collect_graphs
  historical_graph_contexts,historical_graph_questions=collect_graphs(model)
  from historical_target_rows import collect as collect_target_rows
  historical_target_rows=collect_target_rows(model)
  from historical_example_rows import collect as collect_example_rows
  historical_example_rows=collect_example_rows(model)
  from historical_example_rows import collect_options as collect_example_options
  historical_example_options=collect_example_options(model)
  from historical_example_frame import collect as collect_example_frames
  historical_example_frames=collect_example_frames(model)
  from historical_context_keep import collect as collect_context_keeps
  historical_context_starts,historical_context_ends=collect_context_keeps(model)
  conv.historical_embedded_query=style.get('historical_typography',{}).get('embedded_query')
  conv.historical_citation_metrics=style.get('historical_typography',{}).get('citation')
 from historical_prose import embedded_query_gaps
 embedded_query_context_gaps=embedded_query_gaps(model)if source_targets else{}
 from word_groups import validate as validate_groups, prepare as prepare_groups
 from model import iter_fields
 group_records=validate_groups(model)
 number_exceptions=numeral_exceptions(model)
 embedded_documents=style.get('embedded_documents',{})
 if set(embedded_documents)-{i['id']for s in doc['sections']for i in s['items']if 'stem'in i}:raise ValueError('Unknown embedded document stem')
 conv.memo_defaults=style.get('document_roles',{}).get('memo')
 conv.memo_typography=style.get('memo_typography',{})
 conv.email_first_line_indent_em=style.get('email_family',{}).get('first_line_indent_em',0)
 def number_role(target,role):
  chosen=number_exceptions.get(target,{}).get('role',role)
  return chosen if chosen in style.get('font_roles',{}) else None
 group_sources={f['owner']+'/'+f['slot']:f['value']for f in iter_fields(doc)}
 plain_sources={f['owner']+'/'+f['slot']for f in model['field_manifest']if f.get('source_plain_text')}
 embedded_group_options=set()
 def grouped(value,owner,slot):
  target=owner+'/'+slot
  return prepare_groups(value,group_sources[target],group_records[target]) if target in group_records else value
 # Preserve the accepted intermediate PDF metadata through the ID migration.
 from unit_identity import legacy_unit
 public_title=(str(model['publication']['year'])+' '+level+' '+model['publication']['title'] if (model.get('publication')or{}).get('kind')=='workbook' else legacy_unit(unit))
 if source_targets:public_title=model['public_output']['public_title']
 from embedded_images import configure
 conv.embedded_image_styles=configure(doc,style.get('embedded_image_styles',{}))
 from example_policy import validate as validate_examples
 validate_examples(style['examples'])
 conv.underlined_word_groups=style.get('underlined_word_groups',False)
 from document_bullets import DEFAULTS as DOCUMENT_BULLETS
 conv.document_bullets=style.get('document_bullets',DOCUMENT_BULLETS)
 conv.notice_title_ribbon_overhang_em=style.get('notice_title_ribbon_overhang_em',1.4)
 from paragraph_layout import DEFAULTS as PARAGRAPH_ROLES
 conv.paragraph_roles=style.get('paragraph_roles',PARAGRAPH_ROLES)
 conv.answer_blank_base={'inner_width_em':style.get('blank_inner_width_em',2.8),'side_space_em':style.get('blank_side_space_em',.45),'digit_side_space_em':style.get('blank_digit_side_space_em',.45),'punctuation_side_space_em':0}
 conv.answer_blank_roles=style.get('answer_blank_roles',{'heading':{'inner_width_em':2.6,'side_space_em':.35,'digit_side_space_em':.35}})
 frame_overrides=style.get('content_frames',{});table_overrides=style.get('table_styles',{})
 block_styles=style.get('block_styles',{});section_styles=style.get('section_styles',{});heading_boxes=style.get('heading_number_boxes',{})
 heading_intros=style.get('heading_introductions',{})
 if not isinstance(heading_intros,dict) or set(heading_intros)-{s['id'] for s in doc['sections']}:raise ValueError('Unknown heading introduction target')
 booklet_titles=style.get('booklet_titles',{})
 if not isinstance(booklet_titles,dict)or set(booklet_titles)-{s['id']for s in doc['sections']}:raise ValueError('Unknown booklet title target')
 from question_tables import collect as collect_question_tables
 context_tables,question_tables=collect_question_tables(model)
 from context_introductions import collect as collect_context_introductions
 context_introductions=collect_context_introductions(model)
 from notice_documents import collect as collect_notice_documents
 notice_documents=collect_notice_documents(model)
 for association in notice_documents.values():
  source_binding(unit,association['binding']['evidence'])
  if any(i['id']+'/content' in group_records for i in association['items']):raise ValueError('Notice document conflicts with per-field word groups')
 for association in context_tables.values():source_binding(unit,association['binding']['evidence'])
 transferred_tables=set();detached_tables=set()
 from model import merge_defaults
 from email_family import headers as resolve_email_headers
 email_headers=resolve_email_headers(model)
 # A/B stored as adjacent items is one paired group. The B role owns its gap;
 # do not also add the generic passage-after gap at the serialization boundary.
 paired_continues=set()
 for section in doc['sections']:
  if model['layout']['sections'][section['id']]['task']!='paired_reading':continue
  for first,second in zip(section['items'],section['items'][1:]):
   if all('content'in item and item['type']!='example' and item['id']not in section_styles for item in [first,second]) and re.match(r'^\s*[AＡ](?:\s|$)',Projection(first['content']).text) and re.match(r'^\s*[BＢ](?:\s|$)',Projection(second['content']).text):paired_continues.add(first['id'])
 inline_clozes=style.get('inline_cloze_boxes',{})
 cloze_sources={s['id']:s['heading']for s in doc['sections']}
 cloze_sources.update({i['id']:i.get('content',i.get('stem'))for s in doc['sections']for i in s['items']})
 inline_presentations=style.get('inline_presentations',{})
 consumers=[]
 pending_document_question_gap=None
 from passage_boundaries import resolve as resolve_boundaries, question_groups
 group_starts,group_ends,group_members=question_groups(model)
 group_gaps={qid:g['question_gap_pt']for g in group_starts.values()for qid in g['items']}
 inline_targets={i['id'] for section in doc['sections'] for i in section['items']}
 inline_targets.update(i['id']+'/options/'+str(n) for section in doc['sections'] for i in section['items'] for n in range(len(i.get('options',[]))))
 inline_targets.update(section['id']+'/heading' for section in doc['sections'])
 if not isinstance(inline_presentations,dict) or set(inline_presentations)-inline_targets:raise ValueError('Unknown inline presentation field target')
 def inline_value(value,key,source_value=None):
  if source_targets and old_numbering and key in old_numbering['contexts']:
   from historical_numbering import context_value as inferred_context
   value=inferred_context(value,old_numbering['contexts'][key])
   conv.features.append({'kind':'historical_inferred_target_numbers','target':key,'binding':old_numbering['contexts'][key]})
  if key in inline_presentations:
   from inline_layout import prepare_inline
   binding=inline_presentations[key];source_binding(unit,binding['evidence'])
   conv.features.append({'kind':'bound_inline_presentation','target':key,'binding':binding})
   value=prepare_inline(value,binding,source_value)
  if source_targets and key in old_spatial:
   from historical_spatial import prepare as prepare_old_spatial
   binding,original,slot=old_spatial[key]
   value=prepare_old_spatial(value,binding,original,slot)
  return value
 cloze_questions={i['id']:model['layout']['items'][i['id']]['printed_label']['value'] for s in doc['sections'] if model['layout']['sections'][s['id']]['task']=='cloze' for i in s['items'] if 'stem'in i}
 def cloze_value(value,key):
  if key not in inline_clozes:return value
  from inline_layout import prepare_clozes
  conv.features.append({'kind':'bound_inline_cloze_boxes','target':key,'binding':inline_clozes[key]})
  return prepare_clozes(value,inline_clozes[key],cloze_questions,cloze_sources[key])
 block_ids={i['id']for section in doc['sections']for i in section['items']if 'content'in i}
 boundaries=style.get('passage_boundaries',{})
 if not isinstance(boundaries,dict) or set(boundaries)-block_ids:raise ValueError('Unknown passage boundary target')
 if not isinstance(section_styles,dict) or set(section_styles)-block_ids:raise ValueError('Unknown section style target')
 if not isinstance(email_headers,dict) or set(email_headers)-block_ids:raise ValueError('Unknown email header target')
 if not isinstance(block_styles,dict) or set(block_styles)-block_ids:raise ValueError('Unknown block style override target')
 if not isinstance(frame_overrides,dict) or set(frame_overrides)-block_ids:raise ValueError('Unknown content frame override target')
 if not isinstance(table_overrides,dict) or set(table_overrides)-{i['id']for section in doc['sections']for i in section['items']}:raise ValueError('Unknown table style override target')
 font=__import__('package_paths').resource(style['fonts']['body']);bold=__import__('package_paths').resource(style['fonts']['bold']);localfonts=BASE/'runtime/fonts';localfonts.mkdir(exist_ok=True)
 for original in [font,bold]:
  target=localfonts/original.name
  if not target.exists() or file_hash(target)!=file_hash(original):shutil.copyfile(original,target)
 size=style['body_pt'];baseline=style['baseline_pt'];m=style['margins_mm']
 pullback=style.get('option_continuation_pullback_em',1)
 if isinstance(pullback,bool) or not isinstance(pullback,(int,float)) or not 0<=pullback<=1.5:raise ValueError('Invalid option continuation pullback')
 conv.literal_identifiers={s['text'] for b in style.get('inline_presentations',{}).values() for s in b.get('literal_identifiers',[])}
 conv.table_body_pt=style.get('table_body_pt',size);conv.table_baseline_pt=style.get('table_baseline_pt',size*1.4)
 conv.table_header_align=style['table_header_align'];conv.table_mark_align=style['table_mark_align']
 headingfont=__import__('package_paths').resource(style['fonts']['heading']);dashfont=__import__('package_paths').resource(style['fonts']['footer_dashes'])
 def macro(name,value):return chr(92)+'newcommand'+chr(92)+name+'{'+str(value)+'}'
 lines=[r'\documentclass[12pt,a4paper]{article}',r'\input{'+(BASE/'tex/components.tex').as_posix()+'}',
  r'\newcommand\AuthoredWordGap[2]{\hskip#1em\relax}',
  r'\geometry{a4paper,headsep=34pt,footskip='+str(style.get('footer_skip_pt',30))+'pt,left='+str(m['left'])+'mm,right='+str(m['right'])+'mm,top='+str(m['top'])+'mm,bottom='+str(m['bottom'])+'mm}',
  r'\setmainfont{TeX Gyre Termes}',r'\setsansfont{TeX Gyre Heros}',
  r'\setmainjfont[Path={'+localfonts.as_posix()+'/},BoldFont={'+bold.name+'}]{'+font.name+'}',
  r'\setsansjfont[Path={'+headingfont.parent.as_posix()+'/}'+(',FontIndex=0'if headingfont.suffix.lower()=='.ttc'else'')+']{'+headingfont.name+'}',
  r'\newjfontfamily\FooterDash[Path={'+dashfont.parent.as_posix()+'/}]{'+dashfont.name+'}',r'\newfontfamily\FooterNumerals{'+style['fonts']['footer_numerals']+'}',r'\ltjsetruby{size='+str(style['ruby_ratio'])+'}',macro('VerticalExtent',str(style['vertical_extent_em'])),macro('VerticalAfter',str(style.get('vertical_after_pt',0))+'pt'),macro('VerticalBodySize',style.get('vertical_body_pt',size)),macro('VerticalFrameOffset',str(style.get('vertical_frame_offset_em',0))+'em'),macro('VerticalPitch',style.get('vertical_column_pitch_em',1.8)),macro('VerticalPadding',str(style.get('vertical_frame_padding_em',.25))+'em'),
  macro('SlotWidth',str(style.get('slot_width_em',2.7))+'em'),macro('EmailParagraphSkip',str(style.get('email_paragraph_skip_pt',baseline))+'pt'),macro('HeadingSize',style.get('heading_pt',size)),macro('HeadingBaseline',style.get('heading_baseline_pt',baseline)),macro('HeadingLabelSize',style.get('heading_label_pt',r'\HeadingSize')),macro('HeadingSlotSide',str(style.get('heading_slot_side_em',.4))+'em'),macro('HeadingLabelGap',str(style.get('heading_label_gap_em',1.5))+'em'),macro('QuestionGap',str(style['question_gap_pt'])+'pt'),macro('OptionBaseline',style['option_baseline_pt']),macro('QuestionLabelSize',style['question_label_pt']),macro('QuestionLabelPadding',str(style.get('question_label_padding_pt',1))+'pt'),macro('QuestionIndent',str(style.get('question_indent_em',2.1))+'em'),macro('OptionIndent',str(style.get('option_indent_em',2.1))+'em'),macro('OptionLabelGap',str(style.get('option_label_gap_em',.65))+'em'),macro('OptionGridWidth',style.get('option_grid_width_fraction',1)),macro('OptionReserve',str(style['option_reserve_em'])+'em'),
  macro('NoteSize',style['note_pt']),macro('NoteBaseline',style['note_baseline_pt']),macro('NoteBefore',str(style['note_before_pt'])+'pt'),macro('NoteAfter',str(style['note_after_pt'])+'pt'),
  macro('ExampleChoiceIndent',str(style['examples'].get('choice_indent_em',1.8))+'em'),macro('ExampleStemIndent',str(style['examples'].get('stem_indent_em',0))+'em'),macro('StarBodySize',style['examples'].get('body_pt',size)),macro('StarSolutionBefore',str(style['examples']['star_solution_before_pt'])+'pt'),macro('StarSolutionAfter',str(style['examples']['star_solution_after_pt'])+'pt'),macro('StarBoxPadding',str(style['examples']['star_box_padding_pt'])+'pt'),
  macro('AnswerOffset',str(style['examples'].get('answer_offset_em',0))+'em'),macro('AnswerBefore',str(style['examples'].get('answer_before_pt',0))+'pt'),macro('StarSlotBelow',str(style['examples'].get('star_slot_below_pt',style['examples']['star_row_sep_pt']))+'pt'),macro('StarDialogueBefore',str(style['examples'].get('star_dialogue_before_pt',style['examples']['star_row_sep_pt']))+'pt'),macro('StarBottomPadding',str(style['examples'].get('star_bottom_padding_pt',style['examples']['star_box_padding_pt']))+'pt'),macro('StarBoxWidth',style['examples']['star_box_width_fraction']),macro('StarBoxAlign',style['examples']['star_box_align']),macro('StarRowBaseline',style['examples']['star_row_baseline_pt']),macro('StarRowSep',str(style['examples']['star_row_sep_pt'])+'pt'),macro('BodySize',size),macro('AnswerBaseline',style['examples']['answer_baseline_pt']),macro('AnswerColsep',str(style['examples']['answer_colsep_pt'])+'pt'),
  r'\fancyfoot[C]{{\fontsize{'+str(style['footer']['dash_pt'])+r'}{16}\selectfont\FooterDash ―}\hspace{'+str(style['footer']['gap_em'])+r'em}{\FooterNumerals\bfseries\fontsize{'+str(style['footer']['number_pt'])+r'}{16}\selectfont\scalebox{1}['+str(style['footer'].get('number_vertical_scale',1))+r']{\BookletPage}}\hspace{'+str(style['footer']['gap_em'])+r'em}{\fontsize{'+str(style['footer']['dash_pt'])+r'}{16}\selectfont\FooterDash ―}}',
  r'\hypersetup{pdftitle={'+escape(public_title+' - available written paper')+'},pdfauthor={astraJLPT project},pdfsubject={'+escape(model['edition']+' practice rendition from staged schema-v3; not a source facsimile')+'}}',
  r'\begin{document}',r'\fontsize{'+str(size)+'}{'+str(baseline)+r'}\selectfont',r'\setlength\parskip{'+str(style['paragraph_skip_pt'])+'pt}']
 if source_targets:
  lines.insert(lines.index(r'\begin{document}'),r'\input{'+era.EXTRA_TEX.as_posix()+'}')
  if any(b['art']['kind']=='recycling_pies' for b in conv.historical_artworks.values()):
   from historical_artwork import pattern_tex
   lines.insert(lines.index(r'\begin{document}'),pattern_tex())
 if 'heading_continuation_pullback_em' in style:
  heading_pullback=style['heading_continuation_pullback_em']
  if isinstance(heading_pullback,bool) or not isinstance(heading_pullback,(int,float)) or not 0<=heading_pullback<=1.5:
   raise ValueError('Invalid instruction continuation pullback')
  lines.insert(lines.index(r'\begin{document}'),r'\renewcommand\HeadingContinuationPullback{'+str(heading_pullback)+'em}')
 if any(p.get('cell_flow')=='transit_routes' for tables in table_overrides.values() for p in tables.values())or any(i.get('decision_tree')for i in model['layout']['items'].values()):
  lines.insert(lines.index(r'\begin{document}'),r'\usepackage{tikz}')
 if any('page_frame'in b for b in style.get('block_styles',{}).values()):
  lines.insert(lines.index(r'\begin{document}'),r'\newsavebox\RegisteredNoticeFrame')
 if 'cloze_box'in style:
  box=style['cloze_box'];rule=box.get('rule_pt',.4);inner=box['height_pt']-3.4-2*rule
  if not 20<=box['width_pt']<=60 or not 12<=box['height_pt']<=30 or not 8<=box['font_pt']<=16:raise ValueError('Invalid cloze box geometry')
  lines.append(r'\renewcommand\Cloze[1]{\leavevmode\hbox{\hspace{\ClozeClearance}{\setlength\fboxsep{1.7pt}\setlength\fboxrule{'+str(rule)+r'pt}\fbox{\makebox[\dimexpr '+str(box['width_pt'])+r'pt-2\fboxsep-2\fboxrule\relax]{\raisebox{0pt}['+str(inner*.75)+'pt]['+str(inner*.25)+r'pt]{\BoxNumerals\fontsize{'+str(box['font_pt'])+'}{'+str(box['font_pt'])+r'}\selectfont #1}}}}\hspace{\ClozeClearance}}}')
 # Independent geometry; no font-dependent square fallback in revised profiles.
 if 'font_roles' in style:
  from font_roles import declarations
  font_lines,font_identities=declarations(style)
  idx=lines.index(r'\begin{document}');lines[idx:idx]=font_lines
  model['font_roles']=font_identities
  if style.get('workbook_native_2012_furniture'):
   lines=[line.replace(r'{\BookletPage}',r'{\WorkbookFolio}') if line.startswith(r'\fancyfoot[C]') else line for line in lines]
  if source_targets:
   from historical_typography import declarations as historical_type_declarations
   old_lines,old_identities=historical_type_declarations(style)
   lines[lines.index(r'\begin{document}'):lines.index(r'\begin{document}')]=old_lines
   model['font_roles'].extend(old_identities)
  lines[idx:idx]=[macro('OptionRowGap',str(style.get('option_row_gap_pt',3))+'pt'),macro('StarRaise',str(style.get('star_raise_em',.15))+'em'),macro('ClozeClearance',str(style.get('cloze_clearance_em',.28))+'em'),macro('BlankInnerWidth',str(style.get('blank_inner_width_em',2.8))+'em'),macro('BlankSideSpace',str(style.get('blank_side_space_em',.45))+'em')]
  lines.insert(lines.index(r'\begin{document}'),macro('ClozeFrameRule',str(style.get('cloze_frame_rule_pt',.6))+'pt'))
  for key,name,default in [('passage_intro_after_pt','PassageIntroAfter',23),('document_intro_after_pt','DocumentIntroAfter',6),('heading_after_pt','HeadingAfter',6)]:lines.insert(lines.index(r'\begin{document}'),macro(name,str(style.get(key,default))+'pt'))
  for key,name,default in [('underline_drop_ex','UnderlineDrop',.45),('underline_thickness_ex','UnderlineThickness',.1),('reference_drop_ex','ReferenceDrop',2.0)]:lines.insert(lines.index(r'\begin{document}'),macro(name,str(style.get(key,default))+'ex'))
  if style.get('passage_label_parentheses','japanese')=='latin':
   lines.insert(lines.index(r'\begin{document}'),r'\renewcommand\InstructionPassageNumber[1]{{\rmfamily\mcfamily\PassageNumerals \AsciiParen{(}#1\AsciiParen{)}}}')
  lines.insert(lines.index(r'\begin{document}'),r'\ltjsetparameter{xkanjiskip='+str(style.get('mixed_script_gap_em',0))+r'em plus .04em minus 0pt}')
 if style['examples'].get('font_family')=='body':
  lines.insert(lines.index(r'\begin{document}'),r'\renewcommand\ExampleInstructionFont{\rmfamily\mcfamily\mdseries}\renewcommand\StarWorkedFont{\rmfamily\mcfamily\bfseries}')
 qb=style.get('question_box',{'width_pt':17,'height_pt':11.5,'rule_pt':.4})
 if not .75<=style.get('heading_horizontal_scale',1)<=1.1:raise ValueError('Invalid instruction horizontal scale')
 for name,value in [('HeadingHorizontalScale',str(style.get('heading_horizontal_scale',1))),('HeadingWidthMultiplier',str(round(1/style.get('heading_horizontal_scale',1),8))),('QuestionBoxWidth',str(qb['width_pt'])+'pt'),('QuestionBoxHeight',str(qb['height_pt'])+'pt'),('QuestionBoxRule',str(qb['rule_pt'])+'pt'),('QuestionContinuationIndent',str(style.get('question_continuation_indent_em',1.5))+'em'),('DialogueQuoteGap',str(style.get('dialogue_quote_gap_em',.4))+'em'),('DialogueContinuationPullback',str(style.get('dialogue_continuation_pullback_em',.5))+'em'),('StarFrameBefore',str(style['examples'].get('star_frame_before_pt',9))+'pt'),('CompositionBefore',str(style.get('composition_before_pt',20))+'pt'),('AnswerBubbleWidth',str(style['examples'].get('bubble_width_em',.62))+'em'),('AnswerBubbleHeight',str(style['examples'].get('bubble_height_em',.92))+'em')]:
  lines.insert(lines.index(r'\begin{document}'),macro(name,value))
 glyph_size=style['examples'].get('bubble_glyph_size_em',.7)
 for key,name,default,suffix in [('answer_label_width_em','AnswerLabelWidth',2.8,'em'),('answer_label_ruby_base_height_em','AnswerLabelRubyBaseHeight',.8,'')]:
  lines.insert(lines.index(r'\begin{document}'),macro(name,str(style['examples'].get(key,default))+suffix))
 if isinstance(glyph_size,bool) or not isinstance(glyph_size,(int,float)) or not .5<=glyph_size<=1:raise ValueError('Invalid answer bubble glyph size')
 lines.insert(lines.index(r'\begin{document}'),r'\renewcommand\AnswerBubbleGlyphSize{'+str(glyph_size)+'em}')
 emitted=[];number_log=[];layouts=[];suppressed_options=[];coalesced_labels=[];context_layouts=[]
 lines.insert(lines.index(r'\begin{document}'),macro('OptionContinuationPullback',str(pullback)+'em'))
 coalescing=style.get('coalesced_cloze_labels',{})
 question_ids={i['id']for section in doc['sections']for i in section['items']if 'stem'in i}
 soft_breaks=style.get('soft_question_breaks',{})
 if not isinstance(soft_breaks,dict)or set(soft_breaks)-question_ids:raise ValueError('Unknown soft question break target')
 if set(soft_breaks)&(set(coalescing)|set(inline_clozes)):raise ValueError('Conflicting question presentation bindings')
 joined_next={}
 for section in doc['sections']:
  for n,item in enumerate(section['items']):
   im=model['layout']['items'][item['id']];previous=im.get('example_layout',{}).get('continues')
   if not previous:continue
   if n==0 or section['items'][n-1]['id']!=previous or item['type']!='example' or section['items'][n-1]['type']!='example' or im.get('example_variant')!='star_worked':raise ValueError('Example continuation must join adjacent STAR example items')
   joined_next[previous]=item['id']

 if not isinstance(coalescing,dict)or set(coalescing)-question_ids:raise ValueError('Unknown coalesced cloze label target')
 def emit_question(i,task):
  nonlocal pending_document_question_gap
  vertical=task in ['reading','paired_reading','information_retrieval','usage'] or (level in ['N4','N5'] and task=='paraphrase')
  command=r'\OptionsVertical' if vertical else r'\Options'
  nr=model['layout']['items'][i['id']]['printed_label'];num=nr['value']
  source_stem=inline_value(i['stem'],i['id'])
  stem_prose=model['layout']['items'][i['id']].get('historical_stem_prose')
  if stem_prose:
   if not source_targets:raise ValueError('Historical stem prose outside Old JLPT')
   from historical_prose import prepare as prepare_historical_prose
   binding={**stem_prose,'content_sha256':stem_prose['stem_sha256']}
   del binding['stem_sha256']
   source_stem=prepare_historical_prose(source_stem,binding,unit,i['stem'])
  atom_binding=model['layout']['items'][i['id']].get('historical_inline_atoms')
  if atom_binding:
   if not source_targets:raise ValueError('Historical question atoms outside Old JLPT')
   from historical_inline_atoms import prepare as prepare_historical_atoms
   source_stem=prepare_historical_atoms(source_stem,atom_binding,unit,i['stem'])
  conv.embedded_document_binding=None
  if i['id'] in embedded_documents:
   from embedded_documents import prepare as prepare_embedded
   binding=embedded_documents[i['id']];source_binding(unit,binding['evidence'])
   source_stem=prepare_embedded(source_stem,binding,i['stem']);conv.embedded_document_binding=binding
  if i['id'] in soft_breaks:
   if model['layout']['items'][i['id']].get('dialogue') or nr.get('source_prefix'):raise ValueError('Soft question breaks cannot alter a dialogue or bound number prefix')
   from inline_layout import prepare_soft_question_breaks
   binding=soft_breaks[i['id']];source_binding(unit,binding['evidence'])
   source_stem=prepare_soft_question_breaks(source_stem,binding)
   conv.features.append({'kind':'bound_soft_question_breaks','target':i['id'],'binding':binding})
  leading=nr.get('leading_content')
  if leading:
   if not source_targets or nr.get('source_prefix') or digest(i['stem'])!=leading.get('stem_sha256') or not Projection(source_stem).text.startswith(leading.get('text','')) or not re.match(r'^[0-9]+\s+\S',leading.get('text','')):
    raise ValueError('Stale or invalid historical leading content binding')
   source_binding(unit,leading['evidence'])
   original,stem=None,source_stem
   conv.features.append({'kind':'historical_leading_content_number','target':i['id'],'text':leading['text'],'basis':'Exact source-bound quantity belongs to the stem, not its separate question label'})
  elif i['id']in historical_answer_lists:
   # This source-bound prompt's local (1)/(2)/(3) is distinct from the
   # answer number printed beside the options. Preserve the whole prompt.
   original,stem=None,source_stem
  else:original,stem=remove_number(source_stem,nr.get('source_prefix'))
  if original is not None and original!=num:raise ValueError('Explicit label differs from staged metadata')
  if any(key in historical_options.get(i['id'],{})for key in ('braced_prefix','braced_suffix')):
   from historical_layout import braced_stem
   stem=braced_stem(i,historical_options[i['id']],stem)
  if source_targets and old_numbering:
   from historical_numbering import stem_value as inferred_stem
   inferred=old_numbering['questions'][i['id']]
   stem=inferred_stem(stem,inferred)
   conv.features.append({'kind':'historical_inferred_numbering','target':i['id'],
    **{key:value for key,value in inferred.items()if key!='kind'},'label_kind':inferred['kind'],'canonical_changed':False})
  if original is not None and isinstance(stem,dict) and not Projection(stem).text.strip() and '<img' not in stem['html']:
   # The number has moved to the native question label. Its emptied HTML
   # border is not a second answer field and must not become a page-wide frame.
   stem=''
   conv.features.append({'kind':'consumed_number_only_stem','target':i['id'],'label':num})
  if i['id']in coalescing:
   bound=coalescing[i['id']];source_binding(unit,bound['evidence'])
   if task!='cloze'or digest(i['stem'])!=bound['stem_sha256']or bound['label']!=num:raise ValueError('Stale or invalid coalesced cloze binding')
   if not isinstance(i['stem'],str)or not re.fullmatch(r'\s*'+re.escape(num)+r'(?:\s+|[.．]\s*)【'+re.escape(num)+r'】\s*',i['stem']):raise ValueError('Coalescing requires exactly two copies of one label and no stem text')
   stem='';coalesced_labels.append({'item_id':i['id'],'label':num,'stem_sha256':bound['stem_sha256'],'evidence':bound['evidence']})
  elif i['id']in inline_clozes:
   # A leading number is furniture; preserve the exact original binding first.
   bound_stem=cloze_value(i['stem'],i['id'])
   _,stem=remove_number(bound_stem)
  number_log.append({'item_id':i['id'],'source_label':num,'label_basis':'explicit_stem_prefix' if original else nr['basis']})
  gap=style['task_overrides'].get(task,{}).get('question_gap_pt',style['usage_question_gap_pt'] if task=='usage'else style['question_gap_pt'])
  if source_targets and task=='vocabulary' and 'vocabulary_blank_question_gap_pt'in style:
   blank_gap=style['vocabulary_blank_question_gap_pt']
   if type(blank_gap)not in [int,float]or not 0<=blank_gap<=30:raise ValueError('Invalid Old vocabulary blank question gap')
   has_blank=bool(re.search(r'_{2,}|＿{2,}',Projection(stem).text))
   if not has_blank and isinstance(stem,dict) and 'html'in stem:
    # The same Old blank may be authored as underscores or a whitespace-only
    # underline. Apply its role's existing spacing equally to both forms.
    has_blank=any(not node.find() and re.fullmatch(r'[ \u3000\t]+',node.get_text())
                  for node in BeautifulSoup(stem['html'],'html.parser').find_all('u'))
   if has_blank:
    gap=blank_gap
    conv.features.append(dict(kind='historical_vocabulary_blank_spacing',target=i['id'],question_gap_pt=gap,canonical_changed=False))
  if source_targets and task=='vocabulary' and 'vocabulary_vertical_question_gap_pt'in style:
   vertical_gap=style['vocabulary_vertical_question_gap_pt']
   if type(vertical_gap)not in [int,float]or not 0<=vertical_gap<=30:raise ValueError('Invalid Old vertical vocabulary question gap')
   if historical_options.get(i['id'],{}).get('columns')==1:
    gap=vertical_gap
    conv.features.append(dict(kind='historical_vocabulary_vertical_spacing',target=i['id'],question_gap_pt=gap,canonical_changed=False))
  if i['id']in embedded_query_context_gaps:
   gap=embedded_query_context_gaps[i['id']]
   conv.features.append(dict(kind='historical_embedded_query_context_gap',target=i['id'],question_gap_pt=gap,canonical_changed=False))
  if i['id']in historical_grammar_section_gaps:
   binding=historical_grammar_section_gaps[i['id']];gap=binding['question_gap_pt']
   conv.features.append(dict(kind='historical_two_column_grammar_section_spacing',target=i['id'],**binding,canonical_changed=False))
  gap=group_gaps.get(i['id'],gap)
  if pending_document_question_gap is not None:gap=pending_document_question_gap
  pending_document_question_gap=None
  conv.table_styles=table_overrides.get(i['id'],{});conv.table_index=0
  structure=model['layout']['items'][i['id']].get('dialogue')
  if not structure and i['id']+'/stem' in plain_sources and isinstance(stem,dict):
   # Frozen ruby can turn an originally plain stem into HTML. Preserve its
   # intentional breaks after exact authored OCR-wrap removal. Native HTML
   # formatting whitespace and separately bound dialogue turns are excluded.
   from plain_rich_breaks import prepare as preserve_plain_breaks
   stem=preserve_plain_breaks(stem)
   conv.features.append({'kind':'source_plain_question_breaks','target':i['id']})
  saved_keep=getattr(conv,'keep_spaced_words',False)
  conv.keep_spaced_words=style.get('question_word_groups',False)
  stem=grouped(stem,i['id'],'stem')
  feature_start=len(conv.features)
  saved_numeral=getattr(conv,'numeric_role',None)
  saved_scored_star=getattr(conv,'scored_star',False)
  saved_phrase_blank=getattr(conv,'historical_phrase_answer_line',False)
  conv.historical_phrase_answer_line=bool(source_targets and phrase)
  conv.scored_star=task=='sentence_composition'
  conv.numeric_role=number_role(i['id']+'/stem','body_numeral')
  try:
   # Scored stems have answer slots even when transcription left no interior
   # whitespace. Keep this inference out of prose, URLs, options and headings.
   from answer_blanks import COMPACT, prepare as prepare_question_blanks
   dialogue_source=stem
   if COMPACT.search(Projection(stem).text):
    stem,blank_records=prepare_question_blanks(stem,'body',{**conv.answer_blank_base,**conv.answer_blank_roles.get('body',{})},compact_question=True)
    conv.features.extend({**r,'target':i['id']}for r in blank_records)
   if structure:
    if i['id']in historical_inline_dialogue_questions:
     from historical_dialogue_questions import prepare as prepare_inline_dialogue
     stem=prepare_inline_dialogue(stem,historical_inline_dialogue_questions[i['id']],i['stem'])
    from dialogue import render as render_dialogue
    turn_style=style.get('reading_dialogue_turns')if source_targets and task=='reading'else None
    stem_tex=render_dialogue(conv,stem,structure,dialogue_source,turn_style=turn_style)
   else:stem_tex=conv.question(stem,i['id'])
   question_display=any(f['kind']=='question_table_clearance' and f['target']==i['id'] for f in conv.features[feature_start:])
   if source_targets or conv.embedded_document_binding or question_display or re.match(r'^(?:\s*\\Para\s*)+\\SceneParagraph\{',stem_tex):
    # A bound opening scene or selected memo may follow an HTML paragraph break.
    # Keep the native question number beside that opening content.
    cleaned=re.sub(r'^(?:\s*\\Para\s*)+','',stem_tex)
    if question_display and cleaned!=stem_tex:
     conv.features.append({'kind':'question_display_opening_paragraph','target':i['id'],'canonical_changed':False,'reason':'The native number shares the first prose line; retain subsequent paragraph/table boundaries'})
    stem_tex=cleaned
   from intake_roles import reached
   question_roles=reached(model['layout']['items'][i['id']],stem_tex)
  finally:conv.keep_spaced_words=saved_keep;conv.numeric_role=saved_numeral;conv.scored_star=saved_scored_star;conv.historical_phrase_answer_line=saved_phrase_blank
  if source_targets and phrase and i['id']in phrase.get('question_widths',{}):
   width=phrase['question_widths'][i['id']]
   stem_tex=r'{\renewcommand\SlotWidth{'+str(width)+'em}'+stem_tex+'}'
   conv.features.append(dict(kind='historical_source_phrase_answer_line',target=i['id'],width_em=width,canonical_changed=False))
  if any(f['kind'] in ['pedagogical_phrase_breaks','bounded_spaced_word','kept_star_cluster'] for f in conv.features[feature_start:]):
   stem_tex=r'\rightskip=0pt plus 1fil\relax '+stem_tex
  table_count=len(BeautifulSoup(stem['html'],'html.parser').find_all('table'))if isinstance(stem,dict)else 0
  if any(not str(k).isdigit()or int(k)>=table_count for k in conv.table_styles):raise ValueError('Unknown question table index')
  conv.table_styles={};conv.table_index=0
  if i['id'] in question_tables:
   association=question_tables[i['id']];cid=association['context_id']
   if cid in transferred_tables:raise ValueError('Question table rendered twice')
   saved_numeral=conv.numeric_role
   conv.table_styles=table_overrides.get(cid,{});conv.numeric_role=number_role(cid+'/content','notice_numeral')
   try:
    table_tex=conv.question(association['table'],i['id'],associated=bool(Projection(stem).text.strip()))
    if association['standalone']:
     from content_extent import mark as mark_content_extent
     table_tex=mark_content_extent(r'\hypertarget{'+cid+r'}{}\label{'+cid+'}'+table_tex,cid)
     emitted.append(cid);detached_tables.add(cid)
     conv.features.append({'kind':'standalone_question_table_consumed','context_id':cid,'question_id':i['id'],'table_sha256':association['binding']['table_sha256']})
    stem_tex+=r'\par\nobreak '+table_tex
   finally:conv.table_styles={};conv.table_index=0;conv.numeric_role=saved_numeral
   transferred_tables.add(cid)
   conv.features.append({'kind':'question_table_association','context_id':cid,'question_id':i['id'],'table_sha256':association['binding']['table_sha256'],'placement':'after_stem_before_options','canonical_changed':False})
  conv.keep_spaced_words=style.get('option_word_groups',False)
  try:
   option_parts=[]
   columns=model['layout']['items'][i['id']].get('option_money_columns')
   column_rows=None
   if columns:
    from option_columns import render as render_money_options
    column_rows=render_money_options(conv,i['options'],columns,[number_role(i['id']+'/options/'+str(n),'option_content_numeral')for n in range(4)])
   for n,x in enumerate(i['options']):
    conv.numeric_role=number_role(i['id']+'/options/'+str(n),'option_content_numeral')
    historical_binding=historical_options.get(i['id'],{})
    if historical_binding.get('kind')in ['shared_header_table','chronology']or historical_binding.get('source_numbered'):
     option_parts.append('{}');continue
    option_parts.append('{'+(column_rows[n]if column_rows else conv.value(grouped(inline_value(x,i['id']+'/options/'+str(n)),i['id'],'options/'+str(n)),'option'))+'}')
   options_tex=''.join(option_parts)
  finally:conv.keep_spaced_words=saved_keep;conv.numeric_role=saved_numeral
  label_setup='';display_num=num;option_tex=command+options_tex
  if i['id']in historical_labels:
   from historical_layout import question_label
   display_num,label_setup=question_label(historical_labels[i['id']],num,style)
   conv.features.append({'kind':'historical_question_label','target':i['id'],'display':display_num,'source_number':num})
  elif source_targets and old_numbering:
   from historical_layout import question_label
   inferred=old_numbering['questions'][i['id']]
   if inferred['kind']=='boxed':display_num=inferred['display_number']
   else:display_num,label_setup=question_label(inferred['kind'],inferred['display_number'],style)
  if i['id']in historical_options:
   from historical_layout import options_tex as render_historical_options
   row_gap=None
   if i['id']in historical_target_rows:
    from historical_target_rows import parameters as target_row_parameters
    row_settings=target_row_parameters(style,task)
    row_gap=row_settings['choice_row_gap_pt']
   option_tex=render_historical_options(conv,i,historical_options[i['id']],[p[1:-1]for p in option_parts],row_gap_pt=row_gap)
  emitted.append(i['id'])
  question_measure={k:style['task_overrides'].get(task,{})[k] for k in ['question_right_inset_em','question_ragged_right'] if k in style['task_overrides'].get(task,{})}
  if question_measure:
   if not source_targets or set(question_measure)!={'question_right_inset_em','question_ragged_right'}:
    raise ValueError('Question measure requires paired Old task parameters')
   inset=question_measure['question_right_inset_em'];ragged=question_measure['question_ragged_right']
   if type(inset)not in [int,float]or not 0<=inset<=6 or type(ragged)is not bool:
    raise ValueError('Invalid Old question measure')
   if ragged:stem_tex=r'\rightskip=0pt plus1fil\relax '+stem_tex
  if i['id']in historical_question_stems:
   stem_tex=r'\HistoricalQuestionProse{'+stem_tex+'}'
   conv.features.append(dict(kind='historical_question_prose',target=i['id'],font_role='instruction',stem_sha256=digest(i['stem']),canonical_changed=False))
  if i['id']in historical_question_boundaries:
   from historical_page_relationships import split_question
   lines.append(split_question(i['id'],label_setup,text_tex(display_num),stem_tex,option_tex,gap))
   conv.features.append(dict(kind='historical_options_next_page',target=i['id'],binding=historical_question_boundaries[i['id']],canonical_changed=False))
  elif historical_options.get(i['id'],{}).get('source_four_panel_page'):
   lines.append('{'+label_setup+r'\par\addvspace{'+str(gap)+r'pt}\hypertarget{'+i['id']+r'}{}\label{'+i['id']+r'}\QuestionStem{'+text_tex(display_num)+'}{'+stem_tex+r'}\par\clearpage\label{options-'+i['id']+'}'+option_tex+'}')
  elif historical_options.get(i['id'],{}).get('allow_image_option_breaks'):
   lines.append('{'+label_setup+r'\par\addvspace{'+str(gap)+r'pt}\QuestionFlow{'+i['id']+'}{'+text_tex(display_num)+'}{'+stem_tex+'}{'+option_tex+'}}')
   conv.features.append(dict(kind='historical_image_option_flow',target=i['id'],options_sha256=digest(i['options']),options=4,source_numbered=True,breaks='between_intact_panels',forced_page_breaks=False,canonical_changed=False))
  elif i['id']in historical_inline_dialogue_questions:
   from historical_dialogue_questions import render as render_inline_dialogue_question
   lines.append(render_inline_dialogue_question(conv,i,historical_inline_dialogue_questions[i['id']],stem_tex,option_tex,gap))
  elif i['id']in historical_label_answers:
   from historical_label_answers import render as render_label_answer
   lines.append(render_label_answer(conv,i,historical_label_answers[i['id']],option_tex,gap))
  elif i['id']in historical_answer_lists:
   from historical_answer_lists import render as render_answer_list
   lines.append(render_answer_list(conv,i,historical_answer_lists[i['id']],display_num,stem_tex,option_tex,gap))
  elif i['id']in historical_target_rows:
   from historical_target_rows import render as render_target_row
   target_label=text_tex(display_num)
   if i['id']not in historical_labels and (not(source_targets and old_numbering)or old_numbering['questions'][i['id']]['kind']=='boxed'):target_label=r'\QNumber{'+target_label+'}'
   lines.append(render_target_row(conv,i,historical_target_rows[i['id']],target_label,stem_tex,option_tex,row_settings))
  else:lines.append('{'+label_setup+r'\renewcommand\QuestionGap{'+str(gap)+r'pt}\Question{'+i['id']+'}{'+text_tex(display_num)+'}{'+stem_tex+'}{'+option_tex+'}}')
  if question_measure:
   if r'\Question{'+i['id']+'}'not in lines[-1]:raise ValueError('Question measure requires an ordinary whole-question block')
   lines[-1]=r'\par{\advance\linewidth by -'+str(float(inset))+r'em\relax\hsize=\linewidth '+lines[-1]+r'\par}'
   conv.features.append(dict(kind='historical_question_measure',target=i['id'],task=task,**question_measure,canonical_changed=False))
  consumers.append({'target':i['id'],'task':task,'role':'question','word_space_em':conv.word_space_em,'word_space_policy':conv.word_space_policy,'option_path':command,'numeral_role':'choice_numeral','stem_numeral_role':'boxed_numeral','tex_sha256':digest(lines[-1]),'question_gap_pt':gap,'bindings':question_roles})
  if i['id']in historical_side_questions:
   from historical_figure_question import render as render_side_figure
   cid=historical_side_questions[i['id']]
   if cid not in deferred_side_figures:raise ValueError('Beside-question figure not emitted first')
   lines[-1]=render_side_figure(conv,cid,historical_side_figures[cid],deferred_side_figures.pop(cid),lines[-1])
  if i['id']in historical_graph_questions:
   cid=historical_graph_questions[i['id']]
   if cid not in deferred_graph_tex:raise ValueError('Historical graph not detached before its question')
   figure_tex=deferred_graph_tex.pop(cid)
   if historical_graph_contexts[cid].get('page_break_before_figure',False):
    lines[-1]+=r'\par\clearpage\noindent\begin{minipage}{\linewidth}'+figure_tex+r'\par\end{minipage}\par'
   else:
    lines[-1]=r'\par\noindent\begin{minipage}{\linewidth}'+lines[-1]+r'\par\addvspace{8pt}'+figure_tex+r'\par\end{minipage}\par'
   conv.features.append({'kind':'historical_graph_after_question','context':cid,'question':i['id'],'canonical_changed':False})
 def emit_block(i,task,notice=False):
  nonlocal pending_document_question_gap
  pending_document_question_gap=section_styles.get(i['id'],{}).get('following_question_gap_pt')
  boundary=resolve_boundaries(model,i,task)
  if 'following_question_gap_pt'in boundary:pending_document_question_gap=boundary['following_question_gap_pt']
  # Bounded pedagogical words also apply inside beginner cloze/readings.
  # Restore converter state even when a special native document returns early.
  saved_keep=getattr(conv,'keep_spaced_words',False)
  saved_workbook_spans=conv.workbook_font_spans
  conv.workbook_font_spans=[r for r in model.get('workbook_typography',{}).get('local',{}).get('spans',[]) if r['target']==i['id']]
  saved_flow=getattr(conv,'passage_word_flow',False)
  saved_numeral=getattr(conv,'numeric_role',None)
  saved_word_space=conv.word_space_em
  saved_punctuation=getattr(conv,'punctuation_after_em',0)
  prose_metrics={}
  if source_targets and task in ['reading','cloze'] and i['type']!='example':
   for key,attribute in [('passage_word_space_em','word_space_em'),('passage_punctuation_after_em','punctuation_after_em')]:
    if key in style:
     value=style[key]
     if type(value)not in [int,float] or not 0<=value<=2:raise ValueError('Invalid Old passage spacing: '+key)
     setattr(conv,attribute,value);prose_metrics[key]=value
  if prose_metrics:conv.features.append(dict(kind='historical_passage_spacing',target=i['id'],task=task,parameters=prose_metrics,canonical_changed=False))
  is_notice=notice or section_styles.get(i['id'],{}).get('frame_style')=='pinned_corners'
  conv.numeric_role=number_role(i['id']+'/content','notice_numeral' if is_notice else 'body_numeral')
  conv.passage_word_flow=style.get('passage_word_groups',False) and task in style.get('passage_word_group_tasks',['cloze','reading']) and i['type']!='example'
  conv.keep_spaced_words=conv.passage_word_flow or (conv.modern_wakachi and i['type']!='example')
  start=len(lines)
  try:
   result=emit_block_content(i,task,notice)
   if i['type']!='example':
    from content_extent import mark as mark_content_extent
    lines[-1]=mark_content_extent(lines[-1],i['id'])
   # Notice numerals are a separate role from ordinary prose. Explicit inner
   # document/letter faces still take precedence over this semantic default.
   if 'notice_latin' in style.get('font_roles',{}) and (notice or section_styles.get(i['id'],{}).get('frame_style')=='pinned_corners'):
    lines[start:]=[r'{\NoticeLatin '+'\n'.join(lines[start:])+'}']
    consumers.append({'target':i['id'],'task':task,'role':'notice_latin','font':style['font_roles']['notice_latin']})
   from intake_roles import reached
   roles=reached(model['layout']['items'][i['id']], '\n'.join(lines[start:]))
   consumers.append({'target':i['id'],'task':task,'role':'component_activation','bindings':roles})
   if i['id']in historical_side_figures:
    deferred_side_figures[i['id']]='\n'.join(lines[start:]);del lines[start:]
   return result
  finally:
   conv.workbook_font_spans=saved_workbook_spans
   conv.keep_spaced_words=saved_keep;conv.passage_word_flow=saved_flow;conv.numeric_role=saved_numeral
   conv.word_space_em=saved_word_space;conv.punctuation_after_em=saved_punctuation
   consumers.append({'target':i['id'],'task':task,'role':i['type'],'parent_word_space_em':conv.word_space_em,'local_parameters':{k:style.get(k,{}).get(i['id']) for k in ['section_styles','block_styles','table_styles'] if i['id'] in style.get(k,{})},'tex_sha256':digest('\n'.join(lines[start:]))})
 def emit_block_content(i,task,notice=False):
  bid=i['id'];im=model['layout']['items'][bid];emitted.append(bid)
  boundary=resolve_boundaries(model,i,task)
  block_anchor=r'\par\hypertarget{'+bid.replace(':','-')+r'}{}\label{'+bid.replace(':','-')+'}'
  graph_display_keep=bool(historical_graph_contexts.get(bid,{}).get('keep_through_citation_if_fits'))
  sequence_display_keep=im.get('historical_prose',{}).get('keep_sequence_through_citation_if_fits',False)
  if sequence_display_keep and (not source_targets or task!='reading' or bid in historical_graph_contexts or im.get('historical_context_keep')):
   raise ValueError('Source sequence keep outside an independent Old reading structure')
  display_keep=graph_display_keep or sequence_display_keep
  if not display_keep and not im.get('historical_vertical_inset') and not im.get('historical_wrapped_illustration'):lines.append(block_anchor)
  conv.table_styles=table_overrides.get(bid,{});conv.table_index=0
  v=i['content']
  historical_prose_binding=im.get('historical_prose')
  wrapped_illustration=None
  if im.get('historical_wrapped_illustration'):
   if not source_targets or task!='reading' or not im.get('historical_inline_label'):
    raise ValueError('Historical wrapped illustration requires a bound Old inline reading passage')
   from historical_wrapped_illustration import detach as detach_wrapped_illustration
   v,wrapped_illustration=detach_wrapped_illustration(v,im['historical_wrapped_illustration'],unit)
  source_order_graph=bid in historical_graph_contexts and historical_graph_contexts[bid].get('placement')=='source_order'
  if source_order_graph:
   conv.features.append({'kind':'historical_graph_source_order','context':bid,'question':historical_graph_contexts[bid]['question_id'],'canonical_changed':False})
  if bid in historical_graph_contexts and not source_order_graph:
   from historical_complex import detach_graph
   v,figure=detach_graph(v,historical_graph_contexts[bid])
   if im.get('historical_components'):
    from historical_nodes import prepare as prepare_historical_components
    component=im['historical_components']
    if component['kind']!='table_chart' or 'table_chart_sha256' not in historical_graph_contexts[bid]:
     raise ValueError('Deferred historical component must be an exact table/chart group')
    prepare_historical_components(i['content'],component,unit)
    figure=prepare_historical_components(figure,{**component,'content_sha256':digest(figure)},unit)
   if bid in deferred_graph_tex:raise ValueError('Historical graph detached twice')
   if historical_prose_binding:
    from historical_prose import split_deferred_figure
    historical_prose_binding,figure=split_deferred_figure(i['content'],figure,historical_prose_binding,unit)
   deferred_graph_tex[bid]=conv.value(figure)
  if im.get('historical_components') and (bid not in historical_graph_contexts or source_order_graph):
   if not source_targets:raise ValueError('Historical component binding outside historical edition')
   from historical_nodes import prepare as prepare_historical_components
   v=prepare_historical_components(v,im['historical_components'],unit)
  if historical_prose_binding:
   if not source_targets:raise ValueError('Historical prose outside Old JLPT')
   from historical_prose import prepare as prepare_historical_prose
   v=prepare_historical_prose(v,historical_prose_binding,unit,i['content'])
  if im.get('historical_inline_label') and not im.get('historical_reading_dialogue') and not im.get('structured_document'):
   from historical_inline_labels import validate as validate_inline_body,prepare_body_paragraphs
   if task!='reading' or not source_targets:raise ValueError('Historical inline body requires Old reading')
   validate_inline_body(model,i,im['historical_inline_label'])
   v,body_paragraphs=prepare_body_paragraphs(v,im['historical_inline_label']['text'],spatial_paragraphs=[p['text']for p in im.get('historical_spatial',{}).get('content',{}).get('paragraphs',[])])
   if body_paragraphs:conv.features.append(dict(kind='historical_inline_body_inset',target=bid,inset_em=1,first_line_indent_em=1,paragraphs=body_paragraphs,canonical_changed=False))
  if source_targets and task=='reading'and style.get('historical_typography',{}).get('numbered_introduction_body_inset') and not im.get('historical_inline_label'):
   intro=next((p for p in im.get('historical_prose',{}).get('paragraphs',[])if p['role']=='numbered_introduction'),None)
   if intro:
    from historical_inline_labels import prepare_body_paragraphs
    label=re.match(r'^[（(][0-9０-９]+[）)]',intro['text'])[0]
    v,body_paragraphs=prepare_body_paragraphs(v,label,numbered_introduction=True,spatial_paragraphs=[p['text']for p in im.get('historical_spatial',{}).get('content',{}).get('paragraphs',[])])
    if body_paragraphs:conv.features.append(dict(kind='historical_numbered_introduction_body_inset',target=bid,inset_em=1,first_line_indent_em=1,paragraphs=body_paragraphs,canonical_changed=False))
  if im.get('historical_inline_atoms'):
   if not source_targets:raise ValueError('Historical inline atoms outside Old JLPT')
   from historical_inline_atoms import prepare as prepare_historical_atoms
   v=prepare_historical_atoms(v,im['historical_inline_atoms'],unit,i['content'])
  if im.get('historical_document_frame',{}).get('paragraphs'):
   if not source_targets or task!='reading':raise ValueError('Historical framed paragraphs require Old reading')
   from historical_document_frame import prepare as prepare_historical_frame
   v=prepare_historical_frame(v,im['historical_document_frame'],unit,i['content'])
  if graph_display_keep:
   from historical_complex import mark_display_group
   if task!='reading' or not source_order_graph:raise ValueError('Display keep outside an Old reading graph')
   v=mark_display_group(v,historical_graph_contexts[bid],i['content'])
  if sequence_display_keep:
   from historical_complex import mark_sequence_display_group
   v=mark_sequence_display_group(v,historical_prose_binding,i['content'],unit)
  if im.get('paired_label_presentation'):
   if task!='paired_reading' or model['directions'][bid]['render_value']!='horizontal-tb' or im.get('paired_structure'):
    raise ValueError('Paired label display requires one horizontal paired context without a conflicting structure')
   from paired_labels import prepare as prepare_paired_label
   binding=im['paired_label_presentation'];source_binding(unit,binding['evidence'])
   v=prepare_paired_label(v,binding,i['content'])
   consumers.append({'target':bid,'task':task,'role':'paired_label_presentation','source_label':binding['source_label'],'display_label':binding['display_label'],'content_sha256':binding['content_sha256']})
  if im.get('paragraph_indent_ownership'):
   from paragraph_indent_ownership import prepare as prepare_indent_ownership
   binding=im['paragraph_indent_ownership'];source_binding(unit,binding['evidence'])
   if task not in ['reading','paired_reading','cloze'] or model['directions'][bid]['render_value']!='horizontal-tb':raise ValueError('Paragraph indent ownership requires a horizontal prose task')
   v=prepare_indent_ownership(v,binding)
   consumers.append({'target':bid,'task':task,'role':'canonical_paragraph_indent_ownership','offsets':binding['offsets'],'content_sha256':binding['content_sha256']})
  if im.get('soft_line_breaks'):
   from inline_layout import prepare_soft_content_breaks
   binding=im['soft_line_breaks'];source_binding(unit,binding['evidence'])
   v=prepare_soft_content_breaks(v,binding)
   conv.features.append({'kind':'bound_soft_content_breaks','target':bid,'binding':binding})
  v=inline_value(v,bid,i['content'])
  conv.decision_tree_style=im.get('decision_tree')
  if conv.decision_tree_style:
   if not notice:raise ValueError('Decision chart requires an information-retrieval document')
   from decision_trees import prepare as prepare_decision_tree
   binding=conv.decision_tree_style;source_binding(unit,binding['evidence'])
   v=prepare_decision_tree(v,binding,i['content'])
   consumers.append({'target':bid,'task':task,'role':'native_decision_tree','content_sha256':binding['content_sha256'],'list_sha256':binding['list_sha256']})
  if im.get('table_captions'):
   from table_captions import prepare as prepare_table_captions
   binding=im['table_captions'];source_binding(unit,binding['evidence'])
   v=prepare_table_captions(v,binding,i['content'])
   consumers.append({'target':bid,'task':task,'role':'table_caption_ownership','captions':binding['captions'],'content_sha256':binding['content_sha256']})
  if im.get('cloze_panel_headers'):
   if task!='cloze':raise ValueError('Cloze panel headers require a cloze task')
   from cloze_panels import prepare as prepare_cloze_panels
   binding=im['cloze_panel_headers'];source_binding(unit,binding['evidence'])
   v=prepare_cloze_panels(v,binding,i['content'])
   consumers.append({'target':bid,'task':task,'role':'cloze_panel_header_ownership','panels':binding['panels'],'content_sha256':binding['content_sha256']})
  if im.get('paired_structure'):
   if task!='paired_reading':raise ValueError('Paired structure requires a paired-reading task')
   from paired_structure import prepare as prepare_paired_structure
   binding=im['paired_structure'];source_binding(unit,binding['evidence'])
   v=prepare_paired_structure(v,binding,i['content'])
   consumers.append({'target':bid,'task':task,'role':'authored_paired_structure','labels':binding['labels'],'outside_citations':len(binding.get('outside_citations',[])),'content_sha256':binding['content_sha256']})
  if im.get('content_role')=='administrative' and v=='':
   context_layouts.append({'item_id':bid,'kind':'administrative_suppression','basis':'reviewed_editorial_change'});return
  reference_style=style.get('underline_references',{}).get(bid)
  if reference_style:
   source_binding(unit,reference_style['evidence'])
   if digest(i['content'])!=reference_style['content_sha256']or not isinstance(v,dict):raise ValueError('Stale underline reference binding')
   from section_layout import prepare_underline_references
   if 'notes'not in im:v=prepare_underline_references(v,reference_style['markers'])
  from document_roles import resolve as resolve_document_role, wrap as wrap_document_role
  document_role,conv.section_style=resolve_document_role(i,im,task,style,section_styles.get(bid))
  email_role=bool(document_role and document_role['role']=='email')
  if email_role and not im.get('structured_document'):
   from email_family import prepare_padding
   v,offsets=prepare_padding(v)
   if offsets:conv.features.append({'kind':'email_paragraph_padding','target':bid,'offsets':offsets,'indent_em':0,'canonical_changed':False})
  if bid+'/content'in plain_sources and isinstance(v,dict):
   from plain_rich_breaks import prepare as preserve_plain_breaks
   v=preserve_plain_breaks(v)
  if conv.section_style:
   source_binding(unit,conv.section_style['evidence'])
   if digest(i['content'])!=conv.section_style['content_sha256']:raise ValueError('Stale semantic section binding')
   from section_layout import prepare_sections
   v=prepare_sections(cloze_value(v,bid),conv.section_style)
   if 'number_box_labels'in conv.section_style and bid not in inline_clozes:
    if task!='cloze':raise ValueError('Cloze marker boxes require a cloze task')
    from section_layout import prepare_cloze_markers
    v=prepare_cloze_markers(v,conv.section_style['number_box_labels'])
   if len(BeautifulSoup(v['html'],'html.parser').select('section.reading-passage'))!=conv.section_style['section_count']:raise ValueError('Semantic section count changed')

  if not conv.section_style:v=cloze_value(v,bid)
  table_count=len(BeautifulSoup(i['content']['html'],'html.parser').find_all('table')) if isinstance(i['content'],dict) else 0
  if any(not str(k).isdigit() or int(k)>=table_count for k in conv.table_styles):raise ValueError('Unknown table index')
  if task=='cloze':lines.append(r'\vspace{'+str(style.get('cloze_before_pt',0))+r'pt}')
  grouped_v=grouped(v,bid,'content')
  if im.get('shared_note_anchors'):
   if model['directions'][bid]['render_value']!='horizontal-tb':raise ValueError('Shared-note anchors currently require horizontal paired passages')
   from shared_note_anchors import prepare as prepare_shared_notes
   binding=im['shared_note_anchors'];source_binding(unit,binding['evidence'])
   grouped_v=prepare_shared_notes(conv,model,i,grouped_v,binding)
   consumers.append({'target':bid,'task':task,'role':'shared_note_anchors','definitions_item':binding['definitions_item'],'count':len(binding['anchors'])})
  if im.get('horizontal_frame') and (task!='reading' or model['directions'][bid]['render_value']!='horizontal-tb' or conv.section_style or bid in block_styles):
   raise ValueError('Horizontal frame geometry requires the ordinary horizontal reading path')
  if im.get('document_fields') and (task!='reading' or model['directions'][bid]['render_value']!='horizontal-tb' or bid in block_styles):
   raise ValueError('Document fields require a horizontal reading document')
  if im.get('notes',{}).get('frame_placement')=='outside' and (task!='reading' or model['directions'][bid]['render_value']!='horizontal-tb'):
   raise ValueError('Explicit exterior notes require a horizontal reading document')
  if bid in block_styles:
   if not notice:raise ValueError('Notice style used outside information retrieval')
   if bid in context_tables:
    from question_tables import detach as detach_question_table
    grouped_v,table=detach_question_table(grouped_v,context_tables[bid]['binding'])
    if bid in detached_tables:raise ValueError('Question table detached twice')
    detached_tables.add(bid);conv.table_styles={};conv.table_index=0
    conv.features.append({'kind':'question_table_detached_from_notice','context_id':bid,'question_id':context_tables[bid]['question_id'],'table_sha256':context_tables[bid]['binding']['table_sha256']})
   lines.append(render_notice(conv,grouped_v,block_styles[bid],ROOT/'pdf-render/schema'/level,original_value=i['content']));return
  mode=model['directions'][bid]['render_value']
  if mode=='vertical-rl':
   flow=im.get('vertical_flow')
   if flow:source_binding(unit,flow['evidence'])
   header=im.get('vertical_header')
   paired_label=im.get('vertical_paired_label')
   if paired_label:
    if task!='paired_reading':raise ValueError('Vertical paired label requires paired-reading task')
    source_binding(unit,paired_label['evidence'])
   if header:
    if task!='paired_reading':raise ValueError('Vertical paired header requires a paired-reading task')
    source_binding(unit,header['evidence'])
   if im.get('historical_vertical_letter'):
    if not source_targets or flow or header or any(im.get(k)for k in ['notes','introduction','historical_vertical_inset','vertical_frame']):
     raise ValueError('Historical ruled letter conflicts with another vertical structure')
    from historical_vertical_letter import render as render_historical_letter
    vertical_tex=render_historical_letter(conv,grouped_v,im['historical_vertical_letter'],unit,bid)
   elif im.get('historical_vertical_inset'):
    if not source_targets or flow or header or im.get('notes')or im.get('introduction'):
     raise ValueError('Historical vertical inset conflicts with another vertical structure')
    from historical_complex import vertical_tex as render_historical_vertical
    vertical_tex=render_historical_vertical(conv,grouped_v,im['historical_vertical_inset'],unit,block_anchor)
   else:vertical_tex=conv.vertical(grouped_v,im.get('notes'),flow,header,im.get('introduction'),style.get('paired_passages'),paired_label)
   if header:
    from paired_passages import parameters
    consumers.append({'target':bid,'task':task,'role':'vertical_paired_header','parameters':parameters(style.get('paired_passages')),'label':header['prefix'].split('\n')[0],'label_font':style['font_roles']['paired_label'],'content_sha256':header['content_sha256']})
   geometry=im.get('vertical_frame')
   if geometry:
    source_binding(unit,geometry['evidence'])
    if digest(i['content'])!=geometry['content_sha256']:raise ValueError('Stale vertical frame geometry')
    padding=geometry['padding_em']
    if isinstance(padding,bool)or not isinstance(padding,(int,float))or not .25<=padding<=2:raise ValueError('Invalid vertical frame padding')
    vertical_tex=r'{\renewcommand\VerticalPadding{'+str(padding)+'em}'+vertical_tex+'}'
    conv.features.append({'kind':'vertical_frame_geometry','target':bid,'padding_em':padding,'content_sha256':geometry['content_sha256']})
   lines.append(vertical_tex);return
  if im.get('vertical_flow'):raise ValueError('Vertical flow binding requires an explicit vertical body')
  if im.get('vertical_header'):raise ValueError('Vertical header binding requires an explicit vertical body')
  if im.get('vertical_paired_label'):raise ValueError('Vertical paired label requires an explicit vertical body')
  if im.get('historical_vertical_letter'):raise ValueError('Ruled letter requires explicit vertical writing mode')
  if i['type']=='example':
   variant=im.get('example_variant','ordinary');pad=style['examples']['ordinary_padding_pt']
   saved_word_space=conv.word_space_em;conv.word_space_em=style['examples'].get('word_space_em',saved_word_space);conv.star_cell_word_space_em=style['examples'].get('star_cell_word_space_em',conv.word_space_em)
   if variant!='star_worked':conv.word_space_em=style['examples'].get('ordinary_word_space_em',conv.word_space_em)
   ordinary_groups=style['examples'].get('ordinary_word_groups',False)
   if type(ordinary_groups)is not bool:raise ValueError('Ordinary example word grouping must be boolean')
   conv.keep_spaced_words=variant!='star_worked' and (conv.modern_wakachi or bool(source_targets and ordinary_groups))
   conv.passage_word_flow=conv.keep_spaced_words
   conv.example_choice_numerals=style['examples'].get('choice_numeral_role','literal')=='choice'
   conv.example_label_gap_em=style['examples'].get('ordinary_label_gap_em',None) if variant!='star_worked' else None
   choice_indent=style['examples'].get('ordinary_choice_indent_em',style['examples'].get('choice_indent_em',1.8)) if variant!='star_worked' else style['examples'].get('choice_indent_em',1.8)
   structure=im.get('example_layout');continues=structure and structure.get('continues')
   conv.example_layout=structure
   conv.historical_example_target_row=historical_example_rows.get(bid)
   conv.historical_example_target_id=bid
   if conv.historical_example_target_row and 'ordinary_target_label_gap_em'in style['examples']:
    gap=style['examples']['ordinary_target_label_gap_em']
    if type(gap)not in [int,float]or not 0<=gap<=5:raise ValueError('Invalid Old target-example label gap')
    conv.example_label_gap_em=gap
   conv.historical_example_options=historical_example_options.get(bid)
   if conv.historical_example_options:
    from historical_example_rows import resolve_options_geometry
    conv.historical_example_options=resolve_options_geometry(conv.historical_example_options,style['examples'])
   conv.historical_example_frame=historical_example_frames.get(bid)
   prompt_hanging=style['examples'].get('ordinary_prompt_hanging',False)
   if type(prompt_hanging)is not bool or (prompt_hanging and not source_targets):raise ValueError('Invalid Old example prompt continuation policy')
   conv.historical_example_prompt_hanging=prompt_hanging and variant!='star_worked'
   conv.historical_example_choices_before_pt=style['examples'].get('ordinary_choices_before_pt',0) if source_targets and variant!='star_worked' else 0
   before=style['examples']['star_before_pt'] if variant=='star_worked' else style['examples'].get('ordinary_before_pt',10)
   top_pad=pad if variant=='star_worked' else style['examples'].get('ordinary_top_padding_pt',pad)
   example_rules=style['examples'].get('ordinary_rules',True)if variant!='star_worked'else True
   if type(example_rules)is not bool:raise ValueError('Example rule policy must be a boolean')
   if not source_targets and not example_rules:raise ValueError('Unruled ordinary-example policy requires Old JLPT')
   if source_targets and im.get('historical_picture_example'):
    for key in ['ordinary_picture_before_pt','ordinary_picture_top_padding_pt','ordinary_picture_answer_before_pt']:
     if key in style['examples']and(type(style['examples'][key])not in [int,float]or not 0<=style['examples'][key]<=60):raise ValueError('Invalid Old picture-example spacing')
    before=style['examples'].get('ordinary_picture_before_pt',before)
    top_pad=style['examples'].get('ordinary_picture_top_padding_pt',top_pad)
   example_baseline=style['examples'].get('baseline_pt',baseline)
   if source_targets and conv.historical_example_target_row and 'ordinary_target_baseline_pt'in style['examples']:
    example_baseline=style['examples']['ordinary_target_baseline_pt']
    if type(example_baseline)not in [int,float] or not 12<=example_baseline<=60:raise ValueError('Invalid Old target-example baseline')
    if continues:raise ValueError('Target-example leading requires a complete example scope')
    conv.features.append(dict(kind='historical_target_example_baseline',target=bid,baseline_pt=example_baseline,canonical_changed=False))
   task_example_baseline=style['task_overrides'].get(task,{}).get('example_baseline_pt')
   if task_example_baseline is not None:
    if not source_targets or type(task_example_baseline)not in [int,float] or not 12<=task_example_baseline<=60:raise ValueError('Invalid Old task example baseline')
    if continues:raise ValueError('Task example leading requires a complete example scope')
    example_baseline=task_example_baseline
    conv.features.append(dict(kind='historical_task_example_baseline',target=bid,task=task,baseline_pt=example_baseline,canonical_changed=False))
   example_size=style['examples'].get('body_pt',size)
   task_example_size=style['task_overrides'].get(task,{}).get('example_body_pt')
   if task_example_size is not None:
    if not source_targets or type(task_example_size)not in [int,float]or not 9<=task_example_size<=20:raise ValueError('Invalid Old task example body size')
    if continues:raise ValueError('Task example body size requires a complete example scope')
    example_size=task_example_size
    conv.features.append(dict(kind='historical_task_example_body',target=bid,task=task,body_pt=example_size,canonical_changed=False))
   if not continues:lines.append(r'\par\vspace{'+str(before)+r'pt}'+(r'\hrule'if example_rules else'')+r'\vspace{'+str(top_pad)+r'pt}{\renewcommand\ExampleChoiceIndent{'+str(choice_indent)+r'em}\fontsize{'+str(example_size)+'}{'+str(example_baseline)+r'}\selectfont\setlength\parskip{2pt}\setlength\parindent{0pt}\noindent\hspace*{6pt}\begin{minipage}{\dimexpr\linewidth-12pt\relax}')
   if conv.historical_example_target_row and 'ordinary_target_label_gap_em'in style['examples']:
    lines.append(r'\renewcommand\HistoricalExampleLabelGap{'+str(style['examples']['ordinary_target_label_gap_em'])+'em}')
    conv.features.append(dict(kind='historical_target_example_prompt_gap',target=bid,gap_em=style['examples']['ordinary_target_label_gap_em'],canonical_changed=False))
   if conv.historical_example_options:
    geometry=conv.historical_example_options
    if 'prompt_label_gap_em'in geometry:
     lines.append(r'\renewcommand\HistoricalExampleLabelGap{'+str(geometry['prompt_label_gap_em'])+'em}')
     conv.features.append(dict(kind='historical_options_example_prompt_gap',target=bid,gap_em=geometry['prompt_label_gap_em'],canonical_changed=False))
    if 'ordinary_options_answer_indent_em'in style['examples']:
     inset=style['examples']['ordinary_options_answer_indent_em']
     if type(inset)not in [int,float]or not 0<=inset<=10:raise ValueError('Invalid Old option-example answer inset')
     if continues:raise ValueError('Option-example inset requires a complete example scope')
     lines.append(r'\renewcommand\HistoricalExampleAnswerIndent{'+str(inset)+'em}')
     conv.features.append(dict(kind='historical_options_example_answer_inset',target=bid,inset_em=inset,canonical_changed=False))
   if conv.keep_spaced_words:
    lines.append(r'\rightskip=0pt plus 1fil\relax ')
    conv.features.append(dict(kind='historical_example_word_groups',target=bid,canonical_changed=False,basis='Existing bounded space groups with intact ruby; no inserted source line breaks'))
   if im.get('historical_picture_example')and 'ordinary_picture_answer_before_pt'in style['examples']:
    gap=style['examples']['ordinary_picture_answer_before_pt']
    lines.append(r'\renewcommand\AnswerBefore{'+str(gap)+'pt}')
    conv.features.append(dict(kind='historical_picture_example_answer_clearance',target=bid,before_pt=gap,canonical_changed=False))
   target_answer_before=style['examples'].get('ordinary_target_answer_before_pt')
   if target_answer_before is not None:
    if not source_targets or type(target_answer_before)not in [int,float] or not 0<=target_answer_before<=30:raise ValueError('Invalid Old target-example answer clearance')
    if conv.historical_example_target_row:
     if continues:raise ValueError('Target-example answer clearance requires a complete example scope')
     lines.append(r'\renewcommand\AnswerBefore{'+str(target_answer_before)+'pt}')
     conv.features.append(dict(kind='historical_target_example_answer_clearance',target=bid,before_pt=target_answer_before,scope='current example minipage',canonical_changed=False))
   if conv.historical_example_target_row and 'ordinary_target_answer_indent_em'in style['examples']:
    inset=style['examples']['ordinary_target_answer_indent_em']
    if type(inset)not in [int,float]or not 0<=inset<=10:raise ValueError('Invalid Old target-example answer inset')
    if continues:raise ValueError('Target-example inset requires a complete example scope')
    lines.append(r'\renewcommand\HistoricalExampleAnswerIndent{'+str(inset)+'em}')
    conv.features.append(dict(kind='historical_target_example_answer_inset',target=bid,inset_em=inset,canonical_changed=False))
   if structure and 'answer_before_pt'in structure:
    if continues:raise ValueError('Local answer clearance requires a complete example scope')
    gap=structure['answer_before_pt']
    if isinstance(gap,bool)or not isinstance(gap,(int,float))or not 0<=gap<=30:raise ValueError('Invalid per-example answer clearance')
    lines.append(r'\renewcommand\AnswerBefore{'+str(gap)+'pt}')
    consumers.append({'target':bid,'task':task,'role':'example_answer_clearance','before_pt':gap,
        'scope':'current example minipage','inherited_before_pt':style['examples']['answer_before_pt']})
   conv.in_example=True
   try:
    example_options=[grouped(x,bid,'options/'+str(n))for n,x in enumerate(i['options'])]if i.get('options')else None
    if im.get('historical_picture_example'):
     if task!='reading':raise ValueError('Picture example requires its Old reading section')
     from historical_picture_example import render as render_picture_example
     example_tex=render_picture_example(conv,i,im['historical_picture_example'],unit,grouped_v,example_options,im,style)
    else:example_tex=conv.example(grouped_v,variant,example_options,task in ['usage','paraphrase'])
   finally:
    conv.in_example=False
    conv.historical_example_target_row=None
    conv.historical_example_target_id=None
    conv.historical_example_options=None
    conv.historical_example_frame=None
    conv.historical_example_prompt_hanging=False
   lines.append(example_tex)
   consumers.append({'target':bid,'task':task,'role':'example_effective','variant':variant,'parent_word_space_em':saved_word_space,'word_space_em':conv.word_space_em,'star_cell_word_space_em':conv.star_cell_word_space_em if variant=='star_worked' else None,'label_gap_em':conv.example_label_gap_em,'choice_indent_em':choice_indent,'before_pt':before,'top_padding_pt':top_pad,'bottom_padding_pt':pad,'bubble_glyph_size_em':style['examples'].get('bubble_glyph_size_em',.7),'choice_numeral_role':style['examples'].get('choice_numeral_role','literal'),'emitted_macros':{k:example_tex.count(k) for k in [r'\ExampleChoiceNumber',r'\ChoiceNumerals',r'\OptionsVertical',r'\ExampleChoices',r'\AnswerBubble{',r'\AnswerBubbleFilled{}',r'\AnswerBubbleFilledNumber']},'tex_sha256':digest(example_tex)})
   conv.example_layout=None
   if i.get('options') and conv.example_options_embedded:
    suppressed_options.extend(i['options']);embedded_group_options.update(bid+'/options/'+str(n)for n in range(len(i['options'])))
   if source_targets:conv.features.append({'kind':'historical_example_rules','target':bid,'ruled':example_rules})
   if bid not in joined_next:
    after=style['examples'].get('after_pt',10)
    if im.get('historical_picture_example')and 'ordinary_picture_after_pt'in style['examples']:
     after=style['examples']['ordinary_picture_after_pt']
     if type(after)not in [int,float]or not 0<=after<=60:raise ValueError('Invalid Old picture-example after gap')
     conv.features.append(dict(kind='historical_picture_example_after_spacing',target=bid,after_pt=after,canonical_changed=False))
    if source_targets and bid in historical_example_options:
     from historical_example_rows import after_gap
     after,origin=after_gap(style['examples'],historical_example_options[bid],after)
     if origin:conv.features.append(dict(kind='historical_example_after_spacing',target=bid,after_pt=after,origin=origin,columns=historical_example_options[bid]['columns'],canonical_changed=False))
    lines.append(r'\par\end{minipage}}\vspace{'+str(pad)+r'pt}'+(r'\hrule'if example_rules else'')+r'\vspace{'+str(after)+r'pt}')
   conv.word_space_em=saved_word_space;return
  role='email' if frame_overrides.get(bid)=='horizontal_rules' else 'body'
  inset_role='inline_numbered' if im.get('historical_inline_label') or im.get('historical_reading_dialogue',{}).get('opening_label') else 'margin_labeled' if any(p.get('role')=='labeled_paragraph' for p in im.get('historical_prose',{}).get('paragraphs',[])) else None
  from historical_nodes import letter_bracket_parameters
  letter_metrics=letter_bracket_parameters(grouped_v,style)if source_targets and task=='reading'else None
  conv.historical_letter_brackets=letter_metrics
  numbered_context=bool(im.get('historical_inline_label')or any(p['role']=='numbered_introduction'for p in im.get('historical_prose',{}).get('paragraphs',[])))
  note_geometry=style.get('historical_typography',{})
  general_note_inset=note_geometry.get('notes_inset_em',0)
  conv.historical_note_left_inset_em=(note_geometry.get('numbered_context_notes_inset_em',general_note_inset)if numbered_context else general_note_inset)if source_targets and task=='reading'else 0
  passage_insets=style.get('historical_passage_left_inset_em',{})
  if not isinstance(passage_insets,dict)or set(passage_insets)-{'inline_numbered','margin_labeled'}or any(type(v)not in [int,float]or not 0<=v<=4 for v in passage_insets.values())or(passage_insets and not source_targets):raise ValueError('Invalid Old passage role insets')
  passage_left_inset=passage_insets.get(inset_role,0)if task=='reading'else 0
  letter_body_scope=im.get('historical_components',{}).get('bracketed_body_scope')=='passage_only'
  if letter_body_scope and not letter_metrics:raise ValueError('Scoped letter body requires its family metrics')
  if letter_metrics and not letter_body_scope:
   passage_left_inset=letter_metrics['body_inset_em'];inset_role='letter_bracketed'
  conv.historical_passage_left_inset_em=passage_left_inset
  if passage_left_inset:conv.features.append(dict(kind='historical_passage_inset',target=bid,role=inset_role,left_inset_em=passage_left_inset,canonical_changed=False))
  if im.get('historical_reading_dialogue'):
   if not source_targets or task not in ['reading','grammar','cloze'] or im.get('structured_document') or im.get('notes') or im.get('dialogue'):
    raise ValueError('Historical dialogue requires one bound Old reading, grammar or cloze context')
   from historical_reading_dialogue import render as render_historical_reading_dialogue
   tex=render_historical_reading_dialogue(conv,grouped_v,im['historical_reading_dialogue'],unit,i['content'],left_inset_em=passage_left_inset)
  elif im.get('structured_document'):
   if im.get('notes')or im.get('document_lines')or task not in ['reading','paired_reading']:raise ValueError('Conflicting structured document role')
   source_binding(unit,im['structured_document']['evidence'])
   from structured_documents import render as render_structured_document
   tex=render_structured_document(conv,i['content'],im['structured_document'])
  else:tex=conv.with_notes(grouped_v,im['notes'],role,reference_style['markers']if reference_style else None)if 'notes'in im else conv.value(grouped_v,role)
  if im.get('document_lines'):
   source_binding(unit,im['document_lines']['evidence'])
   from document_lines import render as render_document_lines
   tex=render_document_lines(conv,i['content'],tex,im['document_lines'],role,grouped_v)
  if im.get('document_fields'):
   source_binding(unit,im['document_fields']['evidence'])
   if im.get('structured_document'):raise ValueError('Document fields conflict with structured groups')
   from document_fields import render as render_document_fields
   tex=render_document_fields(conv,i['content'],tex,im['document_fields'],role)
  if im.get('paragraph_breaks'):
   from passage_roles import paragraph_breaks_tex
   source_binding(unit,im['paragraph_breaks']['evidence'])
   tex=paragraph_breaks_tex(conv,i['content'],tex,im['paragraph_breaks'])
  if bid in email_headers:
   header=email_headers[bid];source_binding(unit,header['evidence'])
   if digest(i['content'])!=header['content_sha256'] or role!='email':raise ValueError('Stale or unsupported email header binding')
   if 'last_header_line'in header:
    line=header['last_header_line']
    if Projection(v).text.splitlines().count(line)!=1:raise ValueError('Email header must end at one exact source line')
    end=conv.value(line,'option')
    if tex.count(end)!=1:raise ValueError('Ambiguous email header boundary')
    if header.get('rule_set'):
     from document_rules import rule_tex
     separator=r'\par\vspace{'+str(header.get('metadata_to_rule_pt',10))+'pt}'+rule_tex(header['rule_set']['inner'])+r'\vspace{'+str(header.get('rule_to_body_pt',8))+'pt}'
    else:separator=r'\EmailHeaderRule{}'
    tex=tex.replace(end,end+separator,1)
   if header.get('metadata'):
    from paragraph_layout import email_metadata
    tex=email_metadata(conv,v,tex,header['metadata'])
   for gap in header.get('spaced_paragraphs',[]):
    from section_layout import email_paragraph_tex
    start=email_paragraph_tex(conv,v,gap['starts_with'])
    pattern=re.compile(r'(^|\\(?:Para|EmailLine)\s*)'+re.escape(start))
    if len(list(pattern.finditer(tex)))!=1:raise ValueError('Ambiguous email paragraph spacing boundary: '+bid+' / '+gap['starts_with'])
    tex=pattern.sub(lambda m:m[1]+r'\par\addvspace{'+str(gap['before_pt'])+r'pt}\noindent '+start,tex,count=1)
   conv.features.append({'kind':'email_header_rule'if 'last_header_line'in header else 'email_paragraph_spacing','item_id':bid,'content_sha256':header['content_sha256']})
  inline_historical_label=im.get('historical_inline_label')
  if inline_historical_label:
   from historical_inline_labels import validate as validate_inline_label
   if task!='reading':raise ValueError('Historical inline label requires a reading passage')
   validate_inline_label(model,i,inline_historical_label)
  if task=='reading':tex=re.sub(r'^(?:\\Para\s*)?('+OPEN_PAREN_TEX+numeric_token(r'[0-9０-９]{1,2}')+CLOSE_PAREN_TEX+r')(?:\s*\\(?:Para|EmailLine))?\s*',lambda m:m[1]+r'\Para ',tex,count=1)
  if im.get('introduction'):
   from passage_roles import introduction_tex
   tex=introduction_tex(conv,grouped(i['content'],bid,'content'),tex,im['introduction'],im.get('notes'))
  separate_intro=bool(im.get('introduction',{}).get('following_context') or im.get('context_label'))
  if separate_intro:rule='separate_introduction_only'
  else:tex,rule=context_frames(tex,task,frame_overrides.get(bid,'box'),explicit=bid in frame_overrides,paired_style=style.get('paired_passages'),notes_outside=im.get('notes',{}).get('frame_placement')=='outside')
  if im.get('horizontal_frame'):
   from horizontal_frames import apply as horizontal_frame
   source_binding(unit,im['horizontal_frame']['evidence'])
   tex,geometry=horizontal_frame(tex,i['content'],im['horizontal_frame'])
   conv.features.append({'kind':'horizontal_frame_geometry','target':bid,'geometry':geometry,'content_sha256':im['horizontal_frame']['content_sha256']})
   consumers.append({'target':bid,'task':task,'role':'horizontal_frame_geometry','geometry':geometry})
  if task=='paired_reading':
   from paired_passages import parameters
   consumers.append({'target':bid,'task':task,'role':'paired_passages','parameters':parameters(style.get('paired_passages')),'label_font':style.get('font_roles',{}).get('paired_label'),'labels':re.findall(r'\\PairedPassageLabel\{([^{}]+)\}',literal_parens(tex)),'frame_count':tex.count(r'\begin{PairedFrame}'),'frame_style':frame_overrides.get(bid,'box'),'rule':rule,'tex_sha256':digest(tex)})
  if im.get('keep_with_previous'):
   from passage_roles import keep_with_previous_tex
   tex=keep_with_previous_tex(conv,grouped(i['content'],bid,'content'),tex,im['keep_with_previous'])
  if conv.passage_word_flow:
   # Frame environments reset paragraph skips; reapply natural right-edge flow
   # inside the actual content box, after its optional dimensions.
   tex=re.sub(r'\\begin\{(?:ClozeFrame|NoticeFrame)\}(?:\[[^\]]*\])?',lambda m:m[0]+r'\rightskip=0pt plus 1fil\relax ',tex)
  if bid in email_headers and email_headers[bid].get('rule_set'):
   from document_rules import email_frame
   tex=email_frame(tex,email_headers[bid]['rule_set'])
  if document_role:
   tex=wrap_document_role(tex,document_role)
   consumers.append({'target':bid,'task':task,'role':'document_role',**document_role,'tex_sha256':digest(tex)})
  # Normalize a leading passage label before the optional email scope wraps
  # it. Otherwise that wrapper hides the label from the anchored recognizer.
  if task=='reading':
   brackets=str.maketrans('（）','()') if style.get('passage_label_parentheses','japanese')=='latin' else str.maketrans('()','（）')
   def passage_label(match):
    original=literal_parens(literal_digits(match[1]));display=original.translate(brackets)
    if original!=display:conv.features.append({'kind':'parenthesis_display_mapping','context':'existing_passage_label_role','target':bid,'before':original,'display':display,'canonical_changed':False})
    if inline_historical_label:
     conv.features.append({'kind':'historical_inline_passage_label','target':bid,'text':original,'canonical_changed':False})
     return r'\HistoricalInlinePassageLabel{'+text_tex(display)+'}'
    return r'\PassageLabel{'+text_tex(display)+r'}\Para '
   tex=re.sub('^('+OPEN_PAREN_TEX+numeric_token(r'[0-9０-９]{1,2}')+CLOSE_PAREN_TEX+r')\\Para\s*',passage_label,tex,count=1)
   if im.get('context_label'):
    original=im['context_label']['text'];display=original.translate(brackets)
    tex=r'\PassageLabel{'+text_tex(display)+r'}\par\nobreak'
    if original!=display:conv.features.append({'kind':'parenthesis_display_mapping','context':'separate_passage_label_role','target':bid,'before':original,'display':display,'canonical_changed':False})
  if wrapped_illustration is not None:
   from historical_wrapped_illustration import wrap_tex as wrap_illustration_tex
   tex=wrap_illustration_tex(conv,tex,im['historical_wrapped_illustration'],wrapped_illustration,bid,block_anchor)
  if bid in email_headers and 'paragraph_skip_pt'in email_headers[bid]:tex=r'{\renewcommand\EmailParagraphSkip{'+str(email_headers[bid]['paragraph_skip_pt'])+'pt}'+tex+'}'
  if bid in historical_group_starts or (source_targets and old_numbering and bid in old_numbering['contexts']):
   from historical_groups import prose_tex as historical_group_prose
   tex=historical_group_prose(conv,i,tex,im.get('historical_target_dialogue'),unit)
  if im.get('historical_document_frame'):
   if not source_targets or task!='reading':raise ValueError('Historical document frame requires Old reading')
   from historical_document_frame import wrap as wrap_historical_document_frame
   tex=wrap_historical_document_frame(conv,tex,i['content'],im['historical_document_frame'],unit,bid)
  if display_keep:
   from historical_complex import keep_display_tex
   tex=keep_display_tex(tex,block_anchor,bid)
   conv.features.append({'kind':'historical_display_group_keep_if_fits','target':bid,'canonical_changed':False})
  if rule:context_layouts.append({'item_id':bid,'rule':rule,'basis':'deterministic rich-text content cues; shared convention','frame_style':frame_overrides.get(bid,'box'),'style_origin':'editorial_override'if bid in frame_overrides else 'renderer_convention'})
  passage_style=style['task_overrides'].get(task,{})
  passage_size=passage_style.get('passage_body_pt',passage_style.get('body_pt',style.get('passage_body_pt',size)));passage_baseline=passage_style.get('passage_baseline_pt',passage_style.get('baseline_pt',style.get('passage_baseline_pt',baseline)))
  from passage_boundaries import typography as passage_typography
  local_typography=passage_typography(model,i,task)
  if local_typography:
   passage_baseline=local_typography['baseline_pt'];consumers.append({'target':bid,'task':task,'role':'passage_typography',**local_typography})
  paragraph_indent=document_role['parameters']['first_line_indent_em'] if email_role else style['paragraph_indent_em'] if task in ['reading','cloze','paired_reading']else 0
  lines.append(r'{\fontsize{'+str(passage_size)+'}{'+str(passage_baseline)+r'}\selectfont\setlength\parindent{'+str(paragraph_indent)+'em}')
  if passage_left_inset and not im.get('historical_reading_dialogue'):
   lines.append(r'\advance\leftskip by '+str(passage_left_inset)+r'em\relax\advance\linewidth by -'+str(passage_left_inset)+r'em\relax ')
  if source_targets and inline_historical_label and 'inline_passage_label_width_em'in style:
   label_width=style['inline_passage_label_width_em']
   if type(label_width)not in [int,float]or not 1.5<=label_width<=3:raise ValueError('Invalid Old inline passage label width')
   lines.append(r'\renewcommand\HistoricalInlinePassageLabel[1]{\noindent\hangindent=1em\hangafter=1\makebox['+str(label_width)+r'em][l]{{\PassageNumerals #1}}}')
   conv.features.append(dict(kind='historical_inline_label_width',target=bid,width_em=label_width,scope='current reading context',canonical_changed=False))
  if getattr(conv,'keep_spaced_words',False):lines.append(r'\rightskip=0pt plus 1fil\relax ')
  if 'note_before_pt'in passage_style:lines.append(r'\renewcommand\NoteBefore{'+str(passage_style['note_before_pt'])+'pt}')
  if boundary.get('note_keep_with_previous'):lines.append(r'\NoteKeepWithPrevioustrue')
  for key,macro_name in [('note_before_pt','NoteBefore'),('note_after_pt','NoteAfter'),('intro_after_pt','DocumentIntroAfter')]:
   if key in boundary:lines.append('\\renewcommand\\'+macro_name+'{'+str(boundary[key])+'pt}')
  if notice:lines.append(r'\fontsize{'+str(style['notice_body_pt'])+'}{'+str(style['notice_baseline_pt'])+r'}\selectfont\setlength\parskip{2pt}\setlength\parindent{0pt}')
  if notice and frame_overrides.get(bid)!='none' and r'\begin{NoticeFrame}'not in tex:tex=r'\begin{NoticeFrame}'+tex+r'\end{NoticeFrame}'
  default_after=passage_style.get('passage_after_pt',style.get('passage_after_pt',8))
  if source_targets and im.get('historical_reading_dialogue') and 'dialogue_passage_after_pt'in style:
   default_after=style['dialogue_passage_after_pt']
   if type(default_after)not in [int,float]or not 0<=default_after<=72:raise ValueError('Invalid Old dialogue clearance')
   conv.features.append(dict(kind='historical_dialogue_clearance',target=bid,after_pt=default_after,canonical_changed=False))
  after=conv.section_style.get('after_pt',default_after) if conv.section_style else default_after
  if bid in historical_group_starts:after=historical_metrics['target_prose_after_pt']
  after=boundary.get('after_pt',after)
  if boundary:consumers.append({'target':bid,'task':task,'role':'passage_boundary',**boundary})
  lines.append(tex+r'\par}'+('' if bid in paired_continues or separate_intro else r'\vspace{'+str(after)+'pt}'))
 booklet=None
 historical_page_inset=0
 tabs=task_tabs(model)
 if tabs:
  g=tabs['geometry']
  lines.append(r'\ConfigureTaskTabs{'+str(g['width_pt'])+'}{'+str(g['height_pt'])+'}{'+str(g['outer_inset_pt'])+'}{'+str(g['gray'])+'}')
 from running_matter import resolve as resolve_running
 running=resolve_running(model)
 if running:
  if running.get('basis') not in ['observed_prefix_generated_page','inferred_metadata_prefix_generated_page'] or running.get('page_number')!='renderer_booklet':raise ValueError('Unsupported running matter provenance')
  if set(running['booklet_prefixes'])!={s['booklet'] for s in model['layout']['sections'].values()}:raise ValueError('Unknown or missing running booklet')
  lines.append(r'\fancyheadoffset[L,R]{10mm}')
 for si,section in enumerate(doc['sections']):
  pending_document_question_gap=None
  sm=model['layout']['sections'][section['id']];task=sm['task'];items=section['items'];info=task=='information_retrieval'
  conv.modern_wakachi=spaced_task(model,task)
  from section_flow import start_tex
  section_start=start_tex(sm,si,booklet)
  if section_start:lines.append(section_start)
  if sm.get('start_policy')=='flow':consumers.append({'target':section['id'],'task':task,'role':'section_flow','before_pt':sm['flow_before_pt'],'keep_lines':sm['flow_keep_lines'],'basis':sm['flow_basis']})
  if source_targets:
   from historical_section_measures import page_inset,geometry
   inset=page_inset(style,task,sm)
   if inset!=historical_page_inset:
    if sm.get('start_policy','new_page')!='new_page':raise ValueError('Cannot change Old page measure inside flowing section')
    lines.append(geometry(style,inset));historical_page_inset=inset
   if inset:conv.features.append(dict(kind='historical_task_page_measure',target=section['id'],task=task,bottom_inset_mm=inset,footer_baseline_preserved=True,canonical_changed=False))
  if sm['booklet']!=booklet:
   lines.append(r'\BeginBooklet{'+('1'if style['booklet_start']=='recto'else '0')+'}');booklet=sm['booklet']
   if running:
    code=running_prefix_tex(running['booklet_prefixes'][booklet])+r'\RunningSeparator{}\BookletPage'
    running_size=str(style.get('running_pt',7.4));running_font=r'\RunningLatin\RunningJapanese 'if 'font_roles'in style else ''
    lines.append(r'\fancyhead[L]{\ifodd\numexpr\value{page}-\value{bookletstart}+1\relax\else{\fontsize{'+running_size+r'}{10}\selectfont '+running_font+code+r'}\fi}\fancyhead[R]{\ifodd\numexpr\value{page}-\value{bookletstart}+1\relax{\fontsize{'+running_size+r'}{10}\selectfont '+running_font+code+r'}\fi}')
  if tabs:
   group=tabs['task_groups'][task]
   if group is None:lines.append(r'\TaskTabsEnabledfalse')
   else:
    tab=tabs['groups'][group]
    if 'label_parts'in tab:
     label=r'\\[9pt]'.join(r'\TaskTabCharacter{'+text_tex(p['base'])+'}{'+r'\kern.25pt'.join(r'\hbox{'+text_tex(c)+'}'for c in p['reading'])+'}'for p in tab['label_parts'])
    else:label=(r'\\[10pt]' if style.get('workbook_native_2012_furniture') and len(tab['label'])==2 else r'\\').join(text_tex(c) for c in tab['label'])
    lines.append(r'\TaskTabsEnabledtrue\SetTaskTab{'+str(tab['top_pt'])+'}{'+label+'}')
  task_style=style['task_overrides'].get(task,{})
  if source_targets:
   historical_metrics=historical_metric_parameters(style,task)
   if task_style.get('historical_component_metrics'):
    conv.features.append(dict(kind='historical_task_target_metrics',section=section['id'],task=task,metrics=task_style['historical_component_metrics'],canonical_changed=False))
  conv.word_space_policy='preserve'
  conv.word_space_em=task_style.get('heading_word_space_em',style.get('heading_word_space_em',0))
  conv.heading_choice_gap_em=task_style.get('heading_choice_gap_em',style.get('heading_choice_gap_em',0))
  conv.selector_presentation=style.get('instruction_selector')
  saved_keep=getattr(conv,'keep_spaced_words',False)
  conv.keep_spaced_words=conv.modern_wakachi or task_style.get('heading_word_groups',style.get('heading_word_groups',False))
  conv.heading_selector_boundary=style.get('heading_selector_boundary',False)
  conv.heading_selector_suffix_break=task_style.get('heading_selector_suffix_break',style.get('heading_selector_suffix_break',False))
  heading_intro=None;booklet_title=None
  try:
   heading_value=grouped(cloze_value(inline_value(section['heading'],section['id']+'/heading'),section['id']),section['id'],'heading')
   if section['id'] in booklet_titles:
    from booklet_titles import split as split_booklet_title
    title_binding=booklet_titles[section['id']];source_binding(unit,title_binding['evidence'])
    booklet_title,heading_value=split_booklet_title(heading_value,title_binding,section['heading'])
    title_tex=conv.value(booklet_title,'heading')
    conv.features.append({'kind':'booklet_title','section_id':section['id'],'text':title_binding['text'],'canonical_preserved':True})
   if section['id'] in heading_intros:
    from heading_introductions import split as split_heading_intro
    intro_binding=heading_intros[section['id']];source_binding(unit,intro_binding['evidence'])
    heading_value,heading_intro=split_heading_intro(heading_value,intro_binding,section['heading'])
    conv.features.append({'kind':'heading_introduction','section_id':section['id'],'text':intro_binding['text'],'role':intro_binding['role']})
   heading_tex=conv.heading(heading_value)
   consumers.append({'target':section['id'],'task':task,'role':'heading','word_space_em':conv.word_space_em,'word_space_policy':conv.word_space_policy,'numeral_role':'instruction_latin','tex_sha256':digest(heading_tex)})
  finally:
   conv.keep_spaced_words=saved_keep
   conv.heading_selector_suffix_break=False
  inferred_range=old_numbering['ranges'].get(section['id']) if source_targets and old_numbering else None
  if section['id'] in heading_boxes or inferred_range:
   if section['id'] in heading_boxes:
    bound=heading_boxes[section['id']];source_binding(unit,bound['evidence'])
   else:bound={'content_sha256':inferred_range['heading_sha256'],'labels':inferred_range.get('heading_labels',inferred_range['source_labels'])}
   if digest(section['heading'])!=bound['content_sha256']:raise ValueError('Stale or invalid heading range binding')
   if task!='cloze':
    if not source_targets:raise ValueError('Stale or invalid heading range binding')
    if not inferred_range:
     from historical_groups import validate_heading_range
     validate_heading_range(section,task,bound['labels'])
   first,last=bound['labels']
   def label_pattern(x):
    number=re.escape(x)
    if getattr(conv,'approved_administrative_numerals',False):number=r'(?:\{\\AdministrativeNumerals '+number+r'\}|'+number+r')'
    return r'(?:\['+number+r'\]|'+OPEN_PAREN_TEX+number+CLOSE_PAREN_TEX+'|'+number+')'
   range_word=r'(?:から|\\mbox\{から\}|\\mbox\{\\mbox\{から\}\})'
   pattern=label_pattern(first)+r'\s*'+range_word+r'\s*'+label_pattern(last)
   if source_targets:
    gap=r'(?:\s|\\hskip [0-9.]+em\\relax )*'
    pattern=label_pattern(first)+'('+gap+')'+range_word+'('+gap+')'+label_pattern(last)
   if len(re.findall(pattern,heading_tex))!=1:raise ValueError('Heading range must occur exactly once')
   from historical_numbering import heading_range_label
   if inferred_range:
    if inferred_range.get('heading_labels',inferred_range['source_labels'])!=[first,last]:raise ValueError('Inferred heading range differs from source binding')
    a,b=inferred_range['display_labels']
    range_label=lambda label:heading_range_label(conv,label,boxed=inferred_range.get('number_style')=='boxed')
    heading_tex=re.sub(pattern,lambda m:range_label(a)+m[1]+'から'+m[2]+range_label(b),heading_tex)
    conv.features.append({'kind':'historical_inferred_instruction_range','section':section['id'],**inferred_range})
   else:heading_tex=re.sub(pattern,lambda m:heading_range_label(conv,first)+(m[1]if source_targets else'')+'から'+(m[2]if source_targets else'')+heading_range_label(conv,last),heading_tex)
   conv.features.append({'kind':'heading_number_boxes','labels':bound['labels'],'section_id':section['id']})
  heading_tex=re.sub(OPEN_PAREN_TEX+r'(?:\{\\AdministrativeNumerals )?([0-9０-９]{1,2})\}?'+CLOSE_PAREN_TEX,lambda m:r'\InstructionPassageNumber{'+m[1]+'}',heading_tex)
  heading_tex=heading_word_glue(heading_tex)
  heading_after=task_style.get('heading_after_pt',style.get('heading_after_pt',6))
  first_context=next((i for i in items if 'content'in i and i['type']!='example'),None)
  labeled_context=task=='reading' and first_context is not None and re.match(r'^[（(][0-9０-９]{1,2}[）)](?:\s|$)',Projection(first_context['content']).text.strip()) is not None
  if labeled_context:heading_after=task_style.get('heading_after_labeled_pt',heading_after)
  margin_labeled=bool(source_targets and task=='reading' and first_context and any(p['role']=='labeled_paragraph'for p in model['layout']['items'][first_context['id']].get('historical_prose',{}).get('paragraphs',[])))
  if source_targets and task=='reading'and first_context:
   from historical_nodes import letter_bracket_parameters
   margin_labeled=margin_labeled or bool(letter_bracket_parameters(first_context['content'],style))
  if margin_labeled and 'heading_after_margin_labeled_pt'in task_style:
   heading_after=task_style['heading_after_margin_labeled_pt']
   conv.features.append(dict(kind='historical_margin_labeled_heading_gap',target=section['id'],heading_after_pt=heading_after,canonical_changed=False))
  ordinary_example_entry=bool(source_targets and 'ordinary_heading_after_pt'in style['examples'] and items and items[0].get('type')=='example' and model['layout']['items'][items[0]['id']].get('example_variant','ordinary')=='ordinary')
  if ordinary_example_entry:heading_after=style['examples']['ordinary_heading_after_pt']
  if isinstance(heading_after,bool) or not isinstance(heading_after,(int,float)) or not 0<=heading_after<=60:raise ValueError('Invalid task heading gap')
  consumers.append({'target':section['id'],'task':task,'role':'reading_entry_gap' if task in ['reading','paired_reading'] else 'heading_gap','first_content':first_context['id'] if first_context else None,'labeled':labeled_context,'explicit_introduction':bool(first_context and model['layout']['items'][first_context['id']].get('introduction')),'heading_after_pt':heading_after,'owner_key':'heading_after_labeled_pt' if labeled_context and 'heading_after_labeled_pt'in task_style else 'heading_after_pt','passage_intro_after_pt':style.get('passage_intro_after_pt',23),'document_intro_after_pt':style.get('document_intro_after_pt',6)})
  if ordinary_example_entry:consumers[-1]['owner_key']='examples.ordinary_heading_after_pt'
  if booklet_title is not None:
   lines.append(r'{\centering\fontsize{'+str(task_style.get('heading_pt',style.get('heading_pt',size)))+r'}{\HeadingBaseline}\selectfont '+title_tex+r'\par}\nobreak\vspace{'+str(title_binding.get('after_pt',12))+'pt}')
   consumers.append({'target':section['id'],'task':task,'role':'booklet_title','text':title_binding['text'],'after_pt':title_binding.get('after_pt',12),'tex_sha256':digest(title_tex)})
  opening_context_id=items[0]['id'] if items and items[0]['id'] in historical_context_starts else None
  heading_command=r'\HistoricalMeasuredSectionHeading' if opening_context_id else r'\SectionHeading'
  heading_leading=''
  if source_targets and 'heading_baseline_pt'in task_style:
   value=task_style['heading_baseline_pt']
   if type(value)not in [int,float] or not 12<=value<=60:raise ValueError('Invalid Old task heading baseline')
   heading_leading=r'\renewcommand\HeadingBaseline{'+str(value)+'}'
   conv.features.append(dict(kind='historical_task_heading_baseline',target=section['id'],task=task,baseline_pt=value,canonical_changed=False))
  lines.append(r'{'+heading_leading+r'\renewcommand\HeadingAfter{'+str(heading_after)+r'pt}\renewcommand\HeadingSize{'+str(task_style.get('heading_pt',style.get('heading_pt',size)))+'}'+heading_command+'{'+section['id']+'}{'+heading_tex+'}}')
  conv.word_space_em=task_style.get('word_space_em',style.get('word_space_em',0))
  conv.punctuation_after_em=task_style.get('punctuation_after_em',style.get('punctuation_after_em',0))
  conv.word_space_policy=task_style.get('word_space_policy','preserve')
  lines.append(r'{\fontsize{'+str(task_style.get('body_pt',size))+'}{'+str(task_style.get('baseline_pt',baseline))+r'}\selectfont')
  if source_targets:
   from historical_section_measures import phrase_line
   phrase=phrase_line(model,section)
   if phrase:
    lines[-1]+=r'\renewcommand\SlotWidth{'+str(phrase['width_em'])+'em}'
    conv.features.append(dict(kind='historical_phrase_answer_line',target=section['id'],**phrase))
  if 'question_block_origin'in task_style:
   if not source_targets or task_style['question_block_origin']!='first_line':raise ValueError('Invalid Old question block origin')
   # The outer question box can start at its first line; its nested option
   # boxes retain stable zero-height origins and ruby clearance.
   lines[-1]+=r'\patchcmd{\QuestionWhole}{\vspace{0pt}}{}{}{\PackageError{JLPT}{Old question origin changed}{Expected the outer zero-height origin}}'
   lines[-1]+=r'\patchcmd{\QuestionWhole}{\hypertarget{#1}{}\label{#1}\QuestionStem{#2}{#3}}{\QuestionStem{#2}{\hypertarget{#1}{}\label{#1}#3}}{}{\PackageError{JLPT}{Old question anchor changed}{Expected one leading question anchor}}'
   conv.features.append(dict(kind='historical_question_block_origin',target=section['id'],task=task,origin='first_line',inner_option_origins='retained',canonical_changed=False))
  if 'option_baseline_pt'in task_style:
   value=task_style['option_baseline_pt']
   if not source_targets or type(value)not in [int,float] or not 12<=value<=60:raise ValueError('Invalid Old task option baseline')
   lines[-1]+=r'\renewcommand\OptionBaseline{'+str(value)+'}'
   conv.features.append(dict(kind='historical_task_option_baseline',target=section['id'],task=task,baseline_pt=value,canonical_changed=False))
  if heading_intro is not None:
   intro_tex=conv.value(heading_intro,'body')
   intro_macro={'passage':r'\PassageIntroduction{','document':r'\DocumentIntroduction{'}[intro_binding['role']]
   lines.append(intro_macro+intro_tex+'}')
   consumers.append({'target':section['id'],'task':task,'role':'heading_introduction','text':intro_binding['text'],'introduction_role':intro_binding['role'],'tex_sha256':digest(intro_tex)})
  if 'ruby_intergap_em' in task_style:
   gap=task_style['ruby_intergap_em']
   if isinstance(gap,bool) or not isinstance(gap,(int,float)) or not 0<=gap<=.2:raise ValueError('Invalid task ruby gap')
   lines.append(r'\ltjsetruby{intergap='+str(gap)+'}')
  if info:
   qs=[i for i in items if 'stem'in i];bs=[i for i in items if 'content'in i and not context_tables.get(i['id'],{}).get('standalone')]
   for qi,q in enumerate(qs):
    if style.get('keep_question_tail',False) and len(qs)>=2 and qi==len(qs)-2:lines.append(r'\QuestionTailKeep{')
    emit_question(q,task)
   if style.get('keep_question_tail',False) and len(qs)>=2:lines.append('}')
   lines.append(r'\clearpage')
   registered=[b for b in bs if 'page_frame'in block_styles.get(b['id'],{})]
   if registered:
    if len(bs)!=1:raise ValueError('Registered page notice must own the complete information page')
    frame=block_styles[bs[0]['id']]['page_frame']
    lines.append(r'\newgeometry{headsep=34pt,footskip='+str(style.get('footer_skip_pt',30))+'pt,left='+str(m['left'])+'mm,right='+str(m['right'])+'mm,top='+str(m['top'])+'mm,bottom='+str(frame['page_bottom_bp'])+'bp}')
   if section['id'] in notice_documents:
    group=notice_documents[section['id']];members=group['items'];lead=members[0]
    saved_workbook_spans=conv.workbook_font_spans
    conv.workbook_font_spans=[r for r in model.get('workbook_typography',{}).get('local',{}).get('spans',[]) if r['target'] in {i['id']for i in members}]
    conv.workbook_group_spans=bool(conv.workbook_font_spans)
    saved_keep=getattr(conv,'keep_spaced_words',False);saved_flow=getattr(conv,'passage_word_flow',False);saved_numeral=getattr(conv,'numeric_role',None)
    conv.keep_spaced_words=False;conv.passage_word_flow=False
    conv.numeric_role=number_role(lead['id']+'/content','notice_numeral')
    conv.table_styles=group['table_styles'];conv.table_index=0
    try:
     tex=render_notice(conv,group['value'],group['style'],ROOT/'pdf-render/schema'/level,original_value=lead['content'])
    finally:
     conv.keep_spaced_words=saved_keep;conv.passage_word_flow=saved_flow;conv.numeric_role=saved_numeral
     conv.workbook_font_spans=saved_workbook_spans;conv.workbook_group_spans=False
    from content_extent import mark as mark_content_extent
    tex=mark_content_extent(tex,lead['id'])
    tex=tex.replace(r'\label{context-end-'+lead['id']+'}',''.join(r'\label{context-end-'+i['id']+'}'for i in members),1)
    starts=''.join(r'\hypertarget{'+i['id']+r'}{}\label{'+i['id']+'}'for i in members)
    if 'notice_latin'in style.get('font_roles',{}):tex=r'{\NoticeLatin '+tex+'}'
    lines.append(r'\par'+starts+tex)
    emitted.extend(i['id'] for i in members)
    for i in members:
     consumers.append({'target':i['id'],'task':task,'role':'complete_notice_document_member','document_lead':lead['id'],'content_sha256':digest(i['content']),'tex_sha256':digest(tex)})
    conv.features.append({'kind':'notice_document_group','section_id':section['id'],'members':[i['id']for i in members],'combined_content_sha256':digest(group['value']),'canonical_changed':False})
   else:
    for block in bs:
     emit_block(block,task,True)
   if registered:lines.append(r'\restoregeometry')
   physical_order=[]
   for q in qs:
    physical_order.append(q['id'])
    if q['id'] in question_tables and question_tables[q['id']]['standalone']:physical_order.append(question_tables[q['id']]['context_id'])
   physical_order.extend(i['id'] for i in bs)
   layouts.append({'section_id':section['id'],'reason':'sequential information task; original directional wording retained verbatim','serialized_order':[i['id']for i in items],'physical_order':physical_order,'relation':'questions_then_context','facing_enforced':False})
  else:
   seen_context=False;cloze_pending=False;cloze_boundary='next_page';previous_question=False;paired_questions_pending=False
   tail_open=False
   for item_index,item in enumerate(items):
    if 'stem'in item:
     if paired_questions_pending:
      lines.append(r'\clearpage');paired_questions_pending=False
     if item['id']in group_starts:
      lines.append(r'\QuestionGroupKeep{'+item['id']+'}{')
      consumers.append({'target':item['id'],'task':task,'role':'question_group',**group_starts[item['id']]})
     if task=='cloze' and cloze_pending:
      if style.get('cloze_choice_start')!='after_context_group':raise ValueError('Unknown cloze choice policy')
      if cloze_boundary=='next_page':lines.append(r'\clearpage')
      elif cloze_boundary!='flow':raise ValueError('Unknown local cloze question boundary')
      cloze_pending=False
     if item['id']not in group_members and style.get('keep_question_tail',False) and item_index+1<len(items) and 'stem'in items[item_index+1] and (item_index+2==len(items) or 'stem'not in items[item_index+2]):
      lines.append(r'\QuestionTailKeep{');tail_open=True
     emit_question(item,task);previous_question=True
     if item['id']in group_ends:lines.append('}')
     if tail_open and (item_index+1==len(items) or 'stem'not in items[item_index+1]):
      lines.append('}');tail_open=False
     if item['id']in historical_context_ends:lines.append('}')
     if item['id']in historical_group_ends:lines.append(r'\par\end{minipage}\par\addvspace{'+str(historical_metrics['target_group_after_pt'])+'pt}')
    else:
     if item['id']in historical_group_starts:
      lines.append(r'\par\addvspace{'+str(historical_metrics['target_group_before_pt'])+r'pt}\noindent\begin{minipage}{\linewidth}')
      conv.features.append({'kind':'historical_kept_target_group','context':item['id'],'questions':historical_group_starts[item['id']],'basis':'Exact canonical historical reference labels and declared target text match each following question'})
     if item['type']!='example'and task=='reading':
      if item['id']in historical_question_citations:
       lines.append(r'\par\nobreak')
       conv.features.append({'kind':'historical_question_citation','target':item['id'],**historical_question_citations[item['id']]})
      elif item['id'] in context_introductions:
       link=context_introductions[item['id']]
       conv.features.append({'kind':'separate_context_label' if 'label_id' in link else 'separate_context_introduction',**link})
      elif item['id']in historical_passage_starts:
       lines.append(r'\clearpage')
       conv.features.append(dict(kind='historical_independent_passage',target=item['id'],binding=historical_passage_starts[item['id']],canonical_changed=False))
      elif seen_context:
       if source_targets and style['reading_group_start']=='flow':
        context_before=style.get('reading_context_before_pt',14)
        if type(context_before)not in [int,float]or not 0<=context_before<=100:raise ValueError('Invalid Old reading context gap')
        lines.append(r'\par\addvspace{'+str(context_before)+r'pt}')
        if 'reading_context_before_pt'in style:conv.features.append(dict(kind='historical_reading_context_spacing',target=item['id'],before_pt=context_before,canonical_changed=False))
       if historical_context_starts.get(item['id'],{}).get('query_for'):
        conv.features.append(dict(kind='historical_attached_query',target=item['id'],preceding_context=historical_context_starts[item['id']]['query_for'],independent_passage_reservation=False))
       else:
        from historical_context_keep import measured_reservation
        if measured_reservation(style,source_targets,historical_context_starts.get(item['id'])):
         conv.features.append(dict(kind='historical_measured_context_reservation',target=item['id'],independent_passage_reservation=False))
        else:lines.append(reading_start(style['reading_group_start']))
      seen_context=True
     if item['id']in historical_context_starts:
      keep_command=r'\HistoricalOpeningContextKeep' if item['id']==opening_context_id else r'\HistoricalContextKeep'
      lines.append(keep_command+'{'+item['id']+'}{')
      conv.features.append({'kind':'historical_context_keep_if_fits','target':item['id'],'questions':historical_context_starts[item['id']]['questions'],'heading_height_reserved':item['id']==opening_context_id})
     if task=='cloze' and item['type']!='example':
      if previous_question:lines.append(r'\clearpage')
      cloze_pending=True
      cloze_boundary=resolve_boundaries(model,item,task).get('cloze_choices','next_page')
     emit_block(item,task);previous_question=False
     if item['id']in historical_breaks:
      lines.append(r'\clearpage')
      conv.features.append({'kind':'historical_page_break_after','target':item['id'],'basis':'Source-bound preceding-page relationship'})
     if task=='paired_reading'and resolve_boundaries(model,item,task).get('questions_start')=='next_page':paired_questions_pending=True
     if item['type']!='example' and task in ['reading','paired_reading'] and item['id']not in historical_question_citations:lines.append(r'\par\nobreak')
  lines.append('}')
 lines.append(r'\end{document}')
 from word_groups import verify_consumed
 group_consumers=verify_consumed('\n'.join(lines),group_records,group_sources,embedded_group_options)
 if source_targets:
  from historical_spatial import verify as verify_old_spatial
  conv.features.append({'kind':'historical_spatial_consumption',**verify_old_spatial('\n'.join(lines),old_spatial)})
 expected=[i['id']for section in doc['sections']for i in section['items']];assert sorted(emitted)==sorted(expected)and len(emitted)==len(set(emitted))
 if deferred_graph_tex:raise ValueError('Historical graph not emitted after its associated question')
 if deferred_side_figures:raise ValueError('Beside-question figure not consumed exactly once')
 if transferred_tables!=set(context_tables) or detached_tables!=set(context_tables):raise ValueError('Question table transfer was not consumed exactly once')
 model['render_coverage']={'emitted_item_ids':emitted,'all_once':True,'source_numbering':number_log,'physical_layout_overrides':layouts,'features':conv.features,'suppressed_duplicate_options':suppressed_options,'coalesced_cloze_labels':coalesced_labels,'context_layouts':context_layouts,'running_matter':running,'task_edge_tabs':tabs,'grouping_policy':{k:style[k] for k in ['reading_group_start','cloze_choice_start','question_keep']}}
 model['style_sha256']=digest(style);model['fonts']=[{'path':p.as_posix(),'sha256':file_hash(p)}for p in [font,bold,headingfont]]
 # Capture actual emitted values, including code fallbacks, without resolving
 # styles a second time. This record changes evidence only, never page content.
 consumers.append({'target':unit,'task':None,'role':'native_global_parameters',
  'emitted_macros':[{'command':m[0],'name':m[1],'value':m[2]} for m in re.findall(r'\\(newcommand|renewcommand)\\([A-Za-z]+)\{([^{}]*)\}','\n'.join(lines))],
  'font_roles':model.get('font_roles',{}),'body_pt':size,'baseline_pt':baseline,
  'table_body_pt':conv.table_body_pt,'table_baseline_pt':conv.table_baseline_pt,
  'code_fallbacks':{'bubble_glyph_size_em':{'value':glyph_size,'used':'bubble_glyph_size_em' not in style['examples'],'default':.7},
     'table_baseline_pt':{'value':conv.table_baseline_pt,'used':'table_baseline_pt' not in style,'default':size*1.4}},
  'source':'build.py::generate actual macro emission and RichTeX initialization'})
 model['render_coverage']['consumers']=consumers
 model['render_coverage']['authored_word_groups']=group_consumers
 from intake_roles import candidates as intake_candidates
 model['render_coverage']['intake_role_candidates']=intake_candidates(model)
 model['render_assumptions'].append({'unit':unit,'kind':'renderer_convention','evidence_state':'calibrated_profile','chosen_render_value':style['version'],'style_sha256':model['style_sha256'],'choice_basis':'versioned level defaults plus explicit editorial overrides','historical_claim':False})
 from renditions import emit_tex
 from richtex import unbox_adjacent_commas
 return unbox_adjacent_commas(emit_tex('\n'.join(lines)+'\n',model,'body'))

