"""Current v4 written editorial + optional ruby sidecar + defaults -> PDF model."""
from pathlib import Path
import copy, hashlib, json, re, sys, collections
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'pdf-render'
V3=ROOT/'pdf-render/schema'
sys.path.insert(0,str(ROOT/'rubi-restore/tools'))
from ruby_core import Projection, iter_fields, file_hash, field_role
from current_editorial import editorial_path, payload, resolve_defaults, value_at
from current_ruby import apply_current_overlay
from ruby_release_policy import is_current, is_expanded
CAL=[f'N{i}_07_2025' for i in range(1,6)]
RELEASE=ROOT/'rubi-restore/releases/rubi-first-pass-20261009-v1'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):
 p=Path(p);assert p.resolve().is_relative_to(BASE.resolve()) or p.resolve().is_relative_to(V3.resolve());p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def digest(d):return hashlib.sha256(json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def resolve_slot(explicit, suppressed, template, enabled):
 # Presence is separate from truthiness; an explicit empty value wins.
 if suppressed:return None,'suppressed'
 if explicit is not None:return copy.deepcopy(explicit),'editorial'
 if enabled and template is not None:return copy.deepcopy(template),'profile_default'
 return None,'unavailable'
def task_of(unit,s):
 h=Projection(s['heading']).text.replace(' ','').replace('　','')
 if '右のページ' in h:return 'information_retrieval'
 task=field_role(unit[:2],s,'heading')[0]
 if task=='star':return 'sentence_composition'
 if ('ぶんしょうのいみ' in h or '文章の意味' in h) and re.search(r'\d|[０-９]',h):return 'cloze'
 if task=='reading':
  if re.search(r'[AＡ].*[BＢ]',h):return 'paired_reading'
  return 'reading'
 return task

def merge_defaults(defaults,override):
 """Recursive object override. Lists/scalars replace; false/empty/null remain explicit."""
 out=copy.deepcopy(defaults)
 for key,value in override.items():
  out[key]=merge_defaults(out[key],value) if isinstance(value,dict) and isinstance(out.get(key),dict) else copy.deepcopy(value)
 return out


def compose(unit,mode='auto',component='written',variant='regular'):
 from unit_identity import canonical_unit,legacy_unit
 unit=canonical_unit(unit)
 if component!='written':raise ValueError('This release package generates written components only')
 from era_registry import for_editorial,for_unit
 for_unit(unit).admit(unit)
 from release_contract import checked_owner
 checked_owner(unit)
 path=editorial_path(unit);staged=read(path)
 if staged['schema_version']!='4.1.0' or staged['unit']!=unit:raise ValueError('Unsupported current schema version or unit')
 from star_answers import validate_document
 validate_document(staged)
 star_answers={q['id']:copy.deepcopy(q['star']) for s in staged['sections'] for q in s['items'] if 'star' in q}
 era=for_editorial(staged);era.validate_identity(staged)
 ref=staged['defaults'];profile_path=resolve_defaults(path,staged)
 profile=read(profile_path)
 if (profile['profile_id'],profile['revision'])!=(ref['profile_id'],ref['revision']):raise ValueError('Defaults identity/revision mismatch')
 if profile['applicability']!={'exam_generation':staged['exam']['generation'],'historical_level':staged['exam']['historical_level']}:raise ValueError('Historical profile mismatch')
 from style_resolver import resolve as resolve_style
 style,shared_identity,selected_variants=resolve_style(profile_path,profile,staged)
 era.validate_style(staged,style)
 raw=payload(staged);binding={'path':path.relative_to(ROOT).as_posix(),'sha256':file_hash(path),'semantic_sha256':digest(raw)}
 if any('data-rubi-origin' in str(f['value']) for f in iter_fields(raw)):raise ValueError('Project-restored ruby must remain in its separate sidecar')
 rref=staged['provenance'].get('ruby_overlay');doc=copy.deepcopy(raw);overlay=None
 auto=mode=='auto';active=None
 if auto:
  from ruby2_selection import selected
  active=selected(unit,path)
  if active and (not rref or rref.get('release_id')!=active[0]):raise ValueError('Missing or mixed current ruby release selection')
  mode='restored' if rref else 'base'
 if mode=='restored':
  if not rref:raise ValueError('No bound ruby overlay; explicitly select base')
  op=path.parent/rref['path']
  if op.resolve()!=path.with_name('ruby_'+unit+'.json').resolve() or not op.is_file():raise ValueError('Missing or invalid selected ruby sidecar')
  overlay=read(op)
  if overlay['release_id']!=rref['release_id']:raise ValueError('Selected ruby release identity differs')
  from ruby2_selection import selected
  active=selected(unit,path,op)
  if active and overlay['release_id']!=active[0]:raise ValueError('Mixed active written ruby release')
  if is_current(overlay['release_id']) and not active:raise ValueError('Current sidecar has no sealed active selection')
  if is_expanded(overlay['release_id']):
   public=era.identity(unit,staged['provenance']['source_witness'],active[1]['render_edition'])
   retained_workbook_ruby=(active[0]=='rubi-typography-20261109-v1' and unit=='N2_workbook_2018' and public['class']=='workbook' and len(overlay['annotations'])==6)
   if Path(public['complete_path']).name!=active[1]['public_filename'] or (public['class']!='restored' and overlay['annotations'] and not retained_workbook_ruby):
    raise ValueError('Inferred expansion conflicts with public PDF identity')
 elif mode!='base':raise ValueError('Unknown rendering edition')
 doc=apply_current_overlay(raw,overlay,scope_document=staged,expected_release=rref['release_id']) if overlay else copy.deepcopy(raw)
 if auto and active:
  mode=active[1]['render_edition']
  if mode=='base' and overlay['annotations'] and not is_expanded(active[0]):raise ValueError('Base edition cannot discard selected annotations')
 rendition=raw
 before={f['pointer']:f for f in iter_fields(rendition)};after={f['pointer']:f for f in iter_fields(doc)}
 assert before.keys()==after.keys()
 original_groups=0;result_groups=0;fields=[]
 for pointer,f in before.items():
  a=Projection(f['value']);b=Projection(after[pointer]['value']);assert a.text==b.text,(unit,pointer)
  sig=lambda p:collections.Counter((r['start'],r['end'],r['base'],r['reading'])for r in p.ruby)
  assert not sig(a)-sig(b);original_groups+=len(a.ruby);result_groups+=len(b.ruby)
  fields.append({**{k:v for k,v in f.items()if k!='value'},'base_projection_sha256':hashlib.sha256(a.text.encode()).hexdigest(),'content_sha256':digest(f['value']),'authoring_content_sha256':digest(value_at(staged,pointer)),'source_plain_text':isinstance(f['value'],str),'origin':'editorial_with_project_rubi_restore' if 'data-rubi-origin' in str(after[pointer]['value']) else 'editorial'})
 from current_bindings import maps as rendition_maps,select as select_bindings
 rendition_bindings=rendition_maps(raw,doc,style.get('question_groups',[]))
 meta=select_bindings(staged['layout'],rendition_bindings)
 style=select_bindings(style,rendition_bindings)
 tasks={};directions={};origins={};assumptions=[];requests=[]
 for si,section in enumerate(doc['sections']):
  sm=meta['sections'][section['id']];tasks[section['id']]=sm['task']
  for ii,item in enumerate(section['items']):
   im=meta['items'][item['id']];origins[item['id']]={'origin':'editorial','pointer':f'/sections/{si}/items/{ii}'}
   if 'content' in item:
    w=im['writing_mode'];value=w['value'];chosen=style['unknown_direction_fallback'] if value=='unknown' else value
    if value not in ['horizontal-tb','vertical-rl','unknown']:raise ValueError('Unsupported writing mode')
    directions[item['id']]={'evidence_value':value,'render_value':chosen,'basis':w['basis'],'source':w.get('evidence')}
    if value=='unknown':
     assumptions.append({'unit':unit,'item_id':item['id'],'fact':'writing_mode','evidence_state':'unknown','chosen_render_value':chosen,'choice_basis':w.get('fallback_basis','level_defaults'),'historical_claim':False})
     requests.append({'request_id':unit+':'+item['id']+':writing-mode','unit':unit,'item_id':item['id'],'pointer':f'/layout/items/{item["id"]}/writing_mode','missing_fact':'original block writing direction','priority':'P1','source':staged['provenance']['source_witness'],'status':'open','collector_rule':'One credible vertical witness is positive inferred evidence. Horizontal retypes alone do not establish original horizontal direction.'})
  slot=sm.get('example_default')
  if slot is not None and slot is not False and not any(i.get('type')=='example' for i in section['items']):
   template=profile['exam_defaults']['templates'][slot];years=template['applicability']['observed_years']
   if int(legacy_unit(unit)[-4:]) not in years:raise ValueError('Template historical applicability requires explicit review')
   tid='profile:'+template['template_id'];item={'id':tid,'type':'example','content':copy.deepcopy(template['content'])}
   if template.get('options')is not None:item['options']=template['options']
   if template.get('key')is not None:item['key']=template['key']
   section['items'].insert(0,item);origins[tid]={'origin':'profile_default','template_id':template['template_id'],'profile_id':profile['profile_id'],'profile_revision':profile['revision']}
   directions[tid]={'evidence_value':'unknown','render_value':'horizontal-tb','basis':'profile_default'}
   meta['items'][tid]={'example_variant':'star_worked'}
   assumptions.append({'unit':unit,'item_id':tid,'kind':'exam_default','evidence_state':'original_example_unrecovered','chosen_render_value':template['template_id'],'historical_claim':False})
 for field in fields:field['task']=tasks[field['section']]
 info={'unit':unit,'editorial_path':path.relative_to(ROOT).as_posix(),'editorial_sha256':file_hash(path),**staged['provenance']['source_witness']}
 model={'model_version':3,'schema_version':staged['schema_version'],'scope':era.scope_binding(),'unit':unit,'edition':mode,'coverage':staged['exam']['coverage'],'partial_warning':None,'input':info,'canonical_editorial':raw,'document':doc,'layout':meta,'style':style,'tasks':tasks,'directions':directions,'origins':origins,'field_manifest':fields,
 'canonical_current':{'binding':binding,'semantic_sha256':digest(raw)},
 'star_answers':star_answers,
 'ruby_release':{'id':rref['release_id'],'processing_status':overlay['processing_status'],'overlay_path':op.relative_to(ROOT).as_posix(),'overlay_sha256':file_hash(op),'annotations':overlay['annotations']}if overlay else None,
 'profile':{'id':profile['profile_id'],'revision':profile['revision'],'path':profile_path.relative_to(ROOT).as_posix(),'sha256':file_hash(profile_path),'shared_defaults':shared_identity,'selected_variants':selected_variants},
 'preservation':{'canonical_sha256':binding['sha256'],'current_editorial_semantic_sha256':digest(raw),'question_count':sum('stem'in i for s in raw['sections']for i in s['items']),'existing_ruby_groups':original_groups,'project_ruby_groups':result_groups-original_groups,'all_fields_base_projection_equal':True,'rendition_ruby_base_projection_equal':True,'ids_order_keys_explanations_preserved':True},'metadata_requests':requests,'render_assumptions':assumptions}
 era.finish_model(model,staged)
 if 'publication_identity' in staged['provenance']:
  model['publication']=copy.deepcopy(staged['provenance']['publication_identity'])
 from public_output import identity
 model['public_output']=identity(unit,info,mode)
 if model['public_output']['class']=='workbook':
  expected=model['public_output']['publication']
  if model.get('publication',{}).get('kind')!='workbook' or model['publication'].get('year')!=expected['year']:
   raise ValueError('Workbook cover identity differs from the publication registry')
 from instruction_selectors import resolve as resolve_selectors
 resolve_selectors(model)
 from workbook_typography import resolve as resolve_workbook_typography
 resolve_workbook_typography(model)
 from renditions import select as select_rendition
 select_rendition(model,variant)
 return model


def __getattr__(name):
 if name in {"PILOT", "UNITS", "ENTRIES", "SCOPE_PATH", "SCOPE"}:
  import render_scope
  return getattr(render_scope,name)
 raise AttributeError(name)


# Retain the legacy wildcard-import API without loading an era's scope merely
# by importing the neutral compositor.
__all__ = [name for name in globals() if not name.startswith('_')] + ['PILOT', 'UNITS', 'ENTRIES', 'SCOPE_PATH', 'SCOPE']
