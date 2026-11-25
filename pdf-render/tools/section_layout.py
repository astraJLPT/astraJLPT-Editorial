"""Observed presentation of existing semantic reading-passage sections."""
import re,html
from bs4 import BeautifulSoup,Tag,NavigableString
from model import Projection

def render_section(conv,node,context,style):
 if 'frame_rule'in style and style['frame_style']!='box':raise ValueError('Section frame rules require box frame mechanism')
 children=[n for n in node.children if not isinstance(n,NavigableString) or n.strip()]
 if any(isinstance(n,Tag) and any(n.has_attr(key) for key in ('data-literal-identifier','data-breadcrumb-separator','data-japanese-label-colon','data-japanese-label-space')) for n in children):
  children=flow_lines(children)
 if 'list_layout'in style:
  roots=[n for n in children if isinstance(n,Tag)and n.name=='ul']
  if len(roots)!=1:raise ValueError('Section list layout requires exactly one immediate unordered list')
 title='';parts=[];line_styles=style.get('line_styles',[]);used=[]
 first_indent=style.get('first_paragraph_indent_em')
 if first_indent is not None and (isinstance(first_indent,bool)or not isinstance(first_indent,(int,float))or not 0<=first_indent<=2):
  raise ValueError('Invalid first paragraph indent')
 first_indent_used=False
 metadata_rows={}
 if 'metadata_rows' in style:
  from section_metadata import collect as collect_metadata
  metadata_rows=collect_metadata(children,style['metadata_rows'],line_styles)
 label_indexes=[];label_pairs=[]
 if 'label_value_list' in style:
  from label_values import collect as collect_labels
  label_indexes,label_pairs=collect_labels(children,style['label_value_list'])
 for child_index,child in enumerate(children):
  if child_index in metadata_rows:
   if child_index in label_indexes:raise ValueError('Section metadata conflicts with a bracket-label list')
   from section_metadata import render as render_metadata
   parts.append(render_metadata(conv,child,metadata_rows[child_index],style['metadata_rows']))
   continue
  if child_index in label_indexes:
   if child_index==label_indexes[0]:
    from label_values import render as render_labels
    parts.append(render_labels(conv,label_pairs,style['label_value_list'],context))
   continue
  plain=Projection({'html':str(child)}).text.strip()
  matches=[(idx,line)for idx,line in enumerate(line_styles)if plain==line['text']]
  if len(matches)>1:raise ValueError('Duplicate observed document line style')
  if matches:
   idx,line=matches[0];used.append(idx)
   if line.get('label_column'):
    from notice_layout import body_nodes_tex
    parts.append(body_nodes_tex(conv,[child],[line]));continue
   if line.get('attached_bar'):
    child=BeautifulSoup(str(child),'html.parser').find()
    for underline in list(child.find_all('u')):underline.unwrap()
   body=''.join(conv.node(n,context)for n in child.children)if isinstance(child,Tag)else conv.node(child,context)
   if line.get('inset_frame'):
    panel=line['inset_frame']
    if not isinstance(child,Tag)or child.name!='div' or child.find(['div','table','section']):raise ValueError('Inset frame requires one exact simple child div')
    if set(panel)!={'radius_pt','padding_pt'} or any(isinstance(v,bool)or not isinstance(v,(int,float))or not 0<=v<=24 for v in panel.values()):raise ValueError('Invalid section inset geometry')
    body=r'\NoticeInsetPanel{'+str(panel['radius_pt'])+'}{'+str(panel['padding_pt'])+'}{'+body+'}'
    conv.features.append({'kind':'observed_section_inset_frame','text':plain,'geometry':panel})
   if line.get('attached_bar') and 'line_sizes_pt' not in line:
    from title_ribbons import render as ribbon
    body=ribbon(conv,body,line['attached_bar'],line['align'],line['font_pt'],style.get('padding_pt',12),line.get('slant',0))
   if line.get('font_family')=='heading':body=r'{\sffamily\gtfamily '+(r'\addjfontfeatures{FakeSlant='+str(line['slant'])+'}'if line.get('slant')else'')+body+'}'
   if 'letter_space_em'in line:
    if not isinstance(child,Tag)and isinstance(child,NavigableString):pass
    elif isinstance(child,Tag)and child.find('ruby'):raise ValueError('Tracked title cannot split ruby')
    if not 2<=len(plain)<=12 or any(c.isspace()for c in plain):raise ValueError('Tracked title requires one short plain label')
    body=(r'\hspace{'+str(line['letter_space_em'])+'em}').join(conv.text(c)for c in plain)
   if 'line_sizes_pt'in line:
    from notice_layout import html_lines
    raw=child.decode_contents()if isinstance(child,Tag)else str(child);chunks=html_lines(raw)
    if len(chunks)!=len(line['line_sizes_pt']):raise ValueError('Observed section line sizes must match complete lines')
    matcher=type(conv)(conv.assets,source_base=conv.source_base,word_space_em=conv.word_space_em)
    matcher.numeric_role=getattr(conv,'numeric_role',None)
    matcher.literal_identifiers=getattr(conv,'literal_identifiers',set())
    arrow=line.get('native_down_arrow')
    if arrow:
     required={'line','width_pt','height_pt','shaft_width_pt','head_height_pt'}
     if (set(arrow)!=required or type(arrow['line'])is not int or not 0<=arrow['line']<len(chunks)
         or Projection({'html':chunks[arrow['line']]}).text.strip()!='↓'):
      raise ValueError('Native down arrow requires one exact whole existing arrow line')
     dims=[arrow[k]for k in ['width_pt','height_pt','shaft_width_pt','head_height_pt']]
     if (any(isinstance(v,bool)or not isinstance(v,(int,float))or not 1<=v<=30 for v in dims)
         or not dims[2]<dims[0] or not dims[3]<dims[1]):
      raise ValueError('Invalid native down-arrow geometry')
     conv.features.append({'kind':'native_down_arrow','canonical_glyph':'↓','geometry':arrow})
    pieces=[]
    for index,(part,sz)in enumerate(zip(chunks,line['line_sizes_pt'])):
     content=(r'\NativeDownArrow'+''.join('{'+str(arrow[k])+'}'for k in ['width_pt','height_pt','shaft_width_pt','head_height_pt'])
              if arrow and index==arrow['line']else matcher.value({'html':part},context))
     if line.get('attached_bar') and index==line['attached_bar'].get('line_index',0):
      from title_ribbons import render as ribbon
      content=r'\raggedright '+ribbon(conv,content,line['attached_bar'],'left',sz,style.get('padding_pt',12))
     pieces.append(r'{\fontsize{'+str(sz)+'}{'+str(line.get('baseline_pt',sz*1.5))+r'}\selectfont '+content+r'\par}')
    body=''.join(pieces)
   elif 'native_down_arrow'in line:raise ValueError('Native down arrow needs explicit complete line sizes')
   if 'font_pt'in line:body=r'{\fontsize{'+str(line['font_pt'])+'}{'+str(line.get('baseline_pt',line['font_pt']*1.5))+r'}\selectfont '+body+'}'
   align={'left':r'\raggedright ','center':r'\centering ','right':r'\raggedleft '}[line['align']]
   if 'right_inset_em' in line:
    inset=line['right_inset_em']
    if (line['align']!='right' or isinstance(inset,bool)
        or not isinstance(inset,(int,float)) or not 0<=inset<=3):
     raise ValueError('Section right inset requires a right-aligned complete line and 0–3em')
    align+=r'\rightskip='+str(inset)+r'em\relax '
    conv.features.append({'kind':'observed_section_right_inset','text':plain,'right_inset_em':inset})
   rhythm=r'\baselineskip='+str(line['baseline_pt'])+r'pt\relax 'if 'baseline_pt'in line else ''
   indent=r'\hspace*{'+str(line.get('indent_em',0))+'em}'if line.get('indent_em')else ''
   ending=r'\vspace{'+str(line.get('after_pt',0))+'pt}'
   if 'rule_after_pt' in line:
    weight=line['rule_after_pt']
    if isinstance(weight,bool) or not isinstance(weight,(int,float)) or not .1<=weight<=2:
     raise ValueError('Invalid exact document-line rule')
    ending=r'\par\nobreak\hrule height '+str(weight)+r'pt\relax\nobreak '+ending
    conv.features.append({'kind':'observed_section_line_rule','text':plain,'width_pt':weight})
   parts.append(r'\par\addvspace{'+str(line.get('before_pt',0))+r'pt}{'+rhythm+align+r'\noindent '+indent+body+r'\par}'+ending)
  elif isinstance(child,Tag) and child.name in ['h1','h2','h3','h4'] and style.get('title_placement')!='preserve':
   if title:raise ValueError('Multiple section titles require a collected layout')
   title=''.join(conv.node(n,context) for n in child.children)
  elif isinstance(child,Tag) and 'passage-author' in child.get('class',[]):
   body=''.join(conv.node(n,context) for n in child.children)
   if style.get('author_latin_role')=='document':body=r'{\DocumentLatin '+body+'}'
   parts.append(r'\par\addvspace{'+str(style.get('author_before_pt',0))+r'pt}{\raggedleft '+body+r'\par}\vspace{'+str(style.get('author_after_pt',0))+'pt}')
  elif isinstance(child,Tag)and child.name=='ul'and 'list_layout'in style:
   from section_lists import render as render_list
   parts.append(render_list(conv,child,context,style['list_layout']))
  else:
   paragraph=conv.node(child,context)
   if first_indent is not None and not first_indent_used and isinstance(child,Tag)and child.name=='p':
    # mdframed suppresses the first automatic indent. Bind a presentation
    # dimension to this first body paragraph without inserting source spaces.
    if (Projection({'html':str(child)}).text.startswith('　')
        or child.find(attrs={'data-canonical-paragraph-indent':True})):
     raise ValueError('First paragraph already owns its canonical indent')
    paragraph,count=re.subn(r'^\s*\\Para\s*',lambda _:r'\Para \noindent\hspace*{'+str(first_indent)+'em}',paragraph,count=1)
    if count!=1:raise ValueError('First paragraph indent requires a plain body paragraph')
    first_indent_used=True
    conv.features.append({'kind':'section_first_paragraph_indent','indent_em':first_indent,'text':plain})
   parts.append(paragraph)
   if len(parts)==1 and not title and style.get('lead_gap_pt'):parts.append(r'\par\vspace{'+str(style['lead_gap_pt'])+'pt}')
 if sorted(used)!=list(range(len(line_styles))):
  missing=[line['text']for idx,line in enumerate(line_styles)if used.count(idx)!=1]
  raise ValueError('Observed document line must match exactly one complete node: '+repr(missing))
 if first_indent is not None and not first_indent_used:raise ValueError('First paragraph indent did not reach a body paragraph')
 align=r'\centering ' if style.get('title_align','center')=='center' else r'\raggedright '
 titletex=r'{\par'+align+title+r'\par}\vspace{'+str(style.get('title_after_pt',8))+'pt}' if title else ''
 before=''
 if style.get('title_placement','inside_frame')=='before_frame':before=titletex;titletex=''
 pad=style.get('padding_pt',12)
 body=r'{\setlength\parindent{'+str(style.get('paragraph_indent_em',1))+r'em}'+titletex+''.join(parts)+r'\par}'
 if getattr(conv,'passage_word_flow',False):body=r'{\rightskip=0pt plus 1fil\relax '+body+'}'
 if style.get('font_role','body')=='letter':body=r'{\PreserveDocumentDigitstrue\LetterLatin\LetterJapanese '+body+'}'
 elif style.get('font_role','body')=='memo':body=r'{\PreserveDocumentDigitstrue\MemoLatin\MemoJapanese '+body+'}'
 elif style.get('font_role','body')!='body':raise ValueError('Unknown document font role')
 if 'ruby_intergap_em' in style:
  gap=style['ruby_intergap_em']
  if isinstance(gap,bool) or not isinstance(gap,(int,float)) or not 0<=gap<=.2:raise ValueError('Invalid document ruby gap')
  body=r'{\ltjsetruby{intergap='+str(gap)+'}'+body+'}'
 # Font-box metrics can leave detached ink even with zero added intergap.
 # Apply only to this exact bound document; frozen readings are untouched.
 ruby_metrics=[]
 for key,texkey,lo,hi in [('ruby_base_height_em','ybaseheight',.65,1.1),('ruby_size_ratio','size',.35,.6)]:
  if key in style:
   value=style[key]
   if isinstance(value,bool) or not isinstance(value,(int,float)) or not lo<=value<=hi:raise ValueError('Invalid document ruby metric: '+key)
   ruby_metrics.append(texkey+'='+str(value))
 if ruby_metrics:body=r'{\ltjsetruby{'+','.join(ruby_metrics)+'}'+body+'}'
 if style['frame_style']=='pinned_corners':frame=r'\PinnedNotice{'+str(pad)+'}{'+body+'}'
 if style['frame_style']=='pinned_corners'and 'pins'in style:
  from notice_pins import decorate
  frame=decorate(frame,style['pins'])

 if style['frame_style']=='folded_corner':
  frame=r'\FoldedMemo{'+str(pad)+'}{'+body+'}'
  for key,macro in [('frame_top_pt','FoldTopPadding'),('frame_bottom_pt','FoldBottomPadding')]:
   if key in style:frame='{\\renewcommand\\'+macro+'[1]{'+str(style[key])+'pt}'+frame+'}'
  if 'fold_size_pdf_pt'in style:
   fold=style['fold_size_pdf_pt'];frame=r'{\renewcommand\FoldCornerScaleX{'+str(fold['width']/33)+r'}\renewcommand\FoldCornerScaleY{'+str(fold['height']/21)+'}'+frame+'}'
  if 'frame_rule_pt'in style:frame=r'{\renewcommand\FoldRuleWidth{'+str(style['frame_rule_pt'])+'}'+frame+'}'
 elif style['frame_style']=='box':
  from rules import frame_options
  rule=','+frame_options(style['frame_rule']) if 'frame_rule'in style else ''
  # The pinned mdframed method does not paint its inner/outer-width options.
  # Emit a pair of native horizontal rules for this explicit document variant.
  if style.get('frame_rule',{}).get('style')=='double':
   spec=style['frame_rule']
   if set(spec.get('edges',[]))!={'top','bottom'}:raise ValueError('Semantic double frame requires exact horizontal edges')
   weight=str(spec.get('width_pt',.4));gap=str(spec.get('double_gap_pt',1.2))
   double=r'\par\hrule height '+weight+r'pt\kern'+gap+r'pt\hrule height '+weight+r'pt\relax '
   body=double+r'\nobreak\vspace{'+str(pad)+'pt}'+body+r'\par\nobreak\vspace{'+str(pad)+'pt}'+double
   rule=','+frame_options({'style':'none'})
  frame=r'\begin{NoticeFrame}[innerleftmargin='+str(pad)+'pt,innerrightmargin='+str(pad)+'pt,innertopmargin='+str(style.get('frame_top_pt',pad))+'pt,innerbottommargin='+str(style.get('frame_bottom_pt',pad))+'pt'+rule+']'+body+r'\end{NoticeFrame}'
 elif style['frame_style']=='cloze':
  frame=r'\begin{ClozeFrame}'+body+r'\end{ClozeFrame}'
  geometry={}
  for key,macro in [('frame_top_pt','ClozeFrameTop'),('frame_bottom_pt','ClozeFrameBottom')]:
   if key in style:
    value=style[key]
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not 0<=value<=40:
     raise ValueError('Invalid cloze frame padding')
    geometry[key]=value
    frame='{\\renewcommand\\'+macro+'{'+str(value)+'pt}'+frame+'}'
  if geometry:conv.features.append({'kind':'cloze_frame_padding','geometry':geometry,'projection':Projection({'html':str(node)}).text})
 elif style['frame_style']!='pinned_corners':raise ValueError('Unsupported semantic section frame')
 if 'body_pt'in style:frame=r'{\fontsize{'+str(style['body_pt'])+'}{'+str(style['baseline_pt'])+r'}\selectfont '+frame+'}'
 conv.features.append({'kind':'observed_semantic_section','frame_style':style['frame_style'],'label':node.get('aria-label'),'projection':Projection({'html':str(node)}).text})
 if 'width_fraction'in style:
  frame=r'\noindent\makebox[\linewidth][c]{\begin{minipage}{'+str(style['width_fraction'])+r'\linewidth}'+frame+r'\end{minipage}}\par'
 return r'\ObservedSection{\par\vspace{'+str(style.get('before_pt',0))+'pt}'+before+r'{\setlength\parindent{'+str(style.get('paragraph_indent_em',1))+r'em}'+frame+'}}'


def split_paragraph_lines(nodes):
 """Expose authored explicit lines inside paragraphs for exact line roles."""
 out=[]
 for node in nodes:
  if not isinstance(node,Tag) or node.name!='p' or not node.find('br',recursive=False):
   out.append(node);continue
  chunks=[[]]
  for child in list(node.children):
   if isinstance(child,Tag) and child.name=='br':chunks.append([])
   else:chunks[-1].append(child)
  for chunk in chunks:
   if not Projection({'html':''.join(map(str,chunk))}).text.strip():continue
   p=BeautifulSoup('<p></p>','html.parser').p
   p.attrs=dict(node.attrs)
   for child in chunk:p.append(child.extract())
   out.append(p)
 return out


def flow_lines(nodes):
 """Group existing inline runs at explicit breaks, keeping ruby and markup intact."""
 out=[];inline=[]
 def flush():
  if not inline:return
  p=BeautifulSoup('<p></p>','html.parser').p
  for n in inline:p.append(n)
  out.append(p);inline.clear()
 def emit(nodes):
  for n in list(nodes):
   if isinstance(n,Tag)and (n.name=='br'or n.has_attr('data-authored-plain-break')):
    flush()
    # html.parser can nest later content in a mixed <br>/<br/> sequence.
    # A break is only a boundary; its parsed children still belong to the flow.
    if n.name=='br' and n.contents:emit(list(n.contents))
   elif isinstance(n,Tag)and n.name in ['p','div','center','h1','h2','h3','h4','table','section']:
    flush();out.append(n)
   else:inline.append(n)
 emit(nodes)
 flush();return out


def prepare_sections(value,style):
 """Select a source-bound region from existing paragraphs; never change the model."""
 if style.get('unbordered_composition_divs') and style.get('selector')!='composition_pairs':raise ValueError('Unbordered composition selection requires explicit pair semantics')
 if style.get('split_paragraph_lines') and style.get('selector')not in ['single_section','single_div']:raise ValueError('Explicit paragraph lines require one selected document section')
 if isinstance(value,str):value={'html':html.escape(value).replace('\n','<br/>')}
 if style.get('paragraph_break_before'):
  soup=BeautifulSoup(value['html'],'html.parser')
  for token in style['paragraph_break_before']:
   matches=[n for n in soup.descendants if isinstance(n,NavigableString)and n.parent.name not in ['rt','rp']and token in str(n)]
   if len(matches)!=1 or str(matches[0]).count(token)!=1:raise ValueError('Paragraph break must match one accepted text span')
   n=matches[0]
   if n.parent.has_attr('data-cloze-label'):
    # Cloze preparation runs first. Its entire span is an atomic box, so a
    # break inserted among its children would be silently discarded at render.
    atom=n.parent
    if str(n)!=token or len(atom.contents)!=1:raise ValueError('Paragraph break must precede one complete cloze atom')
    atom.insert_before(soup.new_tag('br'))
   else:
    a,b=str(n).split(token);n.replace_with(NavigableString(a),soup.new_tag('br'),NavigableString(token+b))
  prepared={'html':str(soup)}
  if ''.join(Projection(prepared).text.split())!=''.join(Projection(value).text.split()):raise ValueError('Paragraph role changed content')
  value=prepared
 if style.get('selector','existing_sections')=='existing_sections':return value
 soup=BeautifulSoup(value['html'],'html.parser');nodes=[n for n in soup.children if not isinstance(n,NavigableString) or n.strip()]
 if style['selector']=='composition_pairs':
  labels=[n for n in nodes if isinstance(n,Tag)and n.name=='p'and re.match(r'^[（(][12][）)].+',Projection({'html':str(n)}).text)]
  if len(labels)!=style['section_count']:raise ValueError('Composition pair labels changed')
  for label in labels:
   frame=label.find_next_sibling()
   if frame is None or frame.name!='div'or ('border'not in frame.get('style','') and not style.get('unbordered_composition_divs')):raise ValueError('Composition label must precede its exact existing frame')
   frame.name='section';frame['class']=['reading-passage'];label.name='h3';frame.insert(0,label.extract())
  result={'html':str(soup)}
  if Projection(result).text!=Projection(value).text or Projection(result).ruby!=Projection(value).ruby:raise ValueError('Composition section selection changed text/ruby')
  return result
 if style['selector']=='whole_content':
  region=BeautifulSoup('<section class="reading-passage"></section>','html.parser').section
  for n in flow_lines(nodes):region.append(n)
  result={'html':str(region)}
 elif style['selector']in ['single_section','single_div','single_outer_div']:
  regions=soup.find_all('section' if style['selector']=='single_section' else 'div')
  if style['selector']=='single_outer_div':regions=[n for n in regions if n.parent is soup]
  if len(regions)!=1:raise ValueError('Observed single section or div changed')
  regions[0].name='section'
  regions[0]['class']=list(dict.fromkeys(regions[0].get('class',[])+['reading-passage']))
  if 'external_title'in style:
   if style['selector']!='single_outer_div' or style.get('title_placement')!='before_frame':raise ValueError('External title requires one outer frame and before-frame placement')
   title=regions[0].find_previous_sibling()
   if (title is None or title.name!='p' or title.find(['p','div','table','br'])
       or Projection({'html':str(title)}).text.strip()!=style['external_title']):raise ValueError('External title must match the complete preceding paragraph')
   title.name='h3';regions[0].insert(0,title.extract())
  if style.get('split_paragraph_lines'):
   children=split_paragraph_lines(list(regions[0].children))
   regions[0].clear()
   for child in children:regions[0].append(child)
  if style.get('flow_lines'):
   children=flow_lines(list(regions[0].children));regions[0].clear()
   for child in children:regions[0].append(child)
  result={'html':str(soup)}
 elif style['selector']=='after_intro_text':
  if len(nodes)==1 and isinstance(nodes[0],Tag) and nodes[0].name=='div':nodes=[n for n in nodes[0].children if not isinstance(n,NavigableString)or n.strip()]
  nodes=flow_lines(nodes)
  found=[idx for idx,n in enumerate(nodes)if Projection({'html':str(n)}).text.strip()==style['intro_text']]
  if len(found)!=1:raise ValueError('Observed intro must match one complete node')
  pos=found[0]+1;prefix=nodes[:pos];tail=nodes[pos:]
  while tail and isinstance(tail[0],Tag)and tail[0].name=='br':tail.pop(0)
  if not tail:raise ValueError('Observed intro has no document body')
  if style.get('unwrap_existing_frame'):
   if len(tail)!=1 or not isinstance(tail[0],Tag) or tail[0].name!='div' or 'border'not in tail[0].get('style',''):
    raise ValueError('Frame unwrapping requires one exact existing bordered div')
   tail=list(tail[0].children)
  region=BeautifulSoup('<section class="reading-passage"></section>','html.parser').section
  for n in tail:region.append(n)
  result={'html':''.join(map(str,prefix))+str(region)}
 else:result=None
 if result is not None:
  plain=lambda v:''.join(Projection(v).text.split())
  if plain(result)!=plain(value):raise ValueError('Source-bound region lost or changed content')
  return result
 if not nodes or nodes[0].name!='p':raise ValueError('Observed intro requires a leading paragraph')
 first=nodes.pop(0);region=BeautifulSoup('<section class="reading-passage"></section>','html.parser').section
 if style['selector']=='after_intro_lines':
  chunks=[[]]
  for n in list(first.children):
   if isinstance(n,Tag) and n.name=='br':chunks.append([])
   else:chunks[-1].append(n)
  count=style['intro_line_count']
  if len(chunks)!=count+1:raise ValueError('Observed intro line count changed')
  first.clear()
  for idx,part in enumerate(chunks[:count]):
   if idx:first.append(BeautifulSoup('<br/>','html.parser').br)
   for n in part:first.append(n)
  title=BeautifulSoup('<h3></h3>','html.parser').h3
  for n in chunks[-1]:title.append(n)
  region.append(title)
 elif style['selector']!='after_first_paragraph':raise ValueError('Unknown observed section selector')
 for n in nodes:region.append(n)
 if style.get('last_paragraph_author'):
  tail=region.find_all('p',recursive=False)
  if not tail:raise ValueError('Missing source-bound signature paragraph')
  tail[-1]['class']=['passage-author']
 result={'html':str(first)+str(region)}
 plain=lambda v:''.join(Projection(v).text.split())
 if plain(result)!=plain(value):raise ValueError('Source-bound region lost or changed content')
 return result


def email_paragraph_tex(conv,value,starts_with):
 """Select an existing complete email line by its base text, preserving inline ruby."""
 if isinstance(value,str):
  # Resolve the source prefix against the complete field so a terminal label
  # colon has the same presentation role here and in the emitted paragraph.
  from label_separators import prepare as prepare_labels
  prepared,_=prepare_labels(starts_with,presentation=False,source_context=value)
  return conv.value(prepared,'email')
 soup=BeautifulSoup(value['html'],'html.parser')
 nodes=[n for n in soup.children if not isinstance(n,NavigableString)or n.strip()]
 def unwrap(nodes):
  for n in nodes:
   if isinstance(n,Tag)and n.name in ['div','section']:yield from unwrap(n.children)
   else:yield n
 nodes=list(unwrap(nodes))
 lines=flow_lines(nodes);matches=[n for n in lines if Projection({'html':str(n)}).text.strip().startswith(starts_with)]
 if len(matches)!=1:raise ValueError('Email spacing must select exactly one existing paragraph')
 n=matches[0];matcher=type(conv)(conv.assets,source_base=conv.source_base,word_space_em=conv.word_space_em)
 matcher.word_space_policy=getattr(conv,'word_space_policy','preserve')
 matcher.keep_spaced_words=getattr(conv,'keep_spaced_words',False)
 matcher.passage_word_flow=getattr(conv,'passage_word_flow',False)
 matcher.numeric_role=getattr(conv,'numeric_role',None)
 result=matcher.value({'html':n.decode_contents()},'email')
 return re.sub(r'^(?:\\(?:EmailLine|Para)\s*)+|(?:\s*\\(?:EmailLine|Para))+$','',result).strip()


def prepare_underline_references(value,markers):
 """Attach exact accepted markers to their unique underlined phrases."""
 soup=BeautifulSoup(value['html'],'html.parser')
 for marker in markers:
  if marker.get('source_placement')in ['css_below','css_column']:
   before=Projection({'html':str(soup)})
   matches=[]
   for outer in soup.find_all('span'):
    nodes=[n for n in outer.children if not isinstance(n,NavigableString)or n.strip()]
    if not (len(nodes)==2 and all(isinstance(n,Tag)for n in nodes)):continue
    layout=(bool(re.search(r'position\s*:\s*relative',outer.get('style','')))
        and bool(re.search(r'position\s*:\s*absolute',nodes[1].get('style','')))
        and bool(re.search(r'bottom\s*:\s*0(?:[;\s]|$)',nodes[1].get('style',''))))if marker['source_placement']=='css_below'else(
        bool(re.search(r'display\s*:\s*inline-flex',outer.get('style','')))
        and bool(re.search(r'flex-direction\s*:\s*column',outer.get('style',''))))
    if (layout
        and nodes[0].name=='u' and nodes[1].name=='span'
        and not nodes[1].find()
        and Projection({'html':str(nodes[0])}).text==marker['text']
        and nodes[1].get_text()==marker['label']):matches.append(outer)
   if len(matches)!=1:raise ValueError('CSS underline reference requires one exact relative wrapper and below-line label')
   n=matches[0];n['data-css-underlined-reference']=marker['label']
   if 'clearance_below_pt'in marker:
    clearance=marker['clearance_below_pt']
    if isinstance(clearance,bool)or not isinstance(clearance,(int,float))or not 0<=clearance<=12:raise ValueError('Invalid underline reference clearance')
    n['data-reference-clearance']=str(clearance)
   after=Projection({'html':str(soup)})
   if before.text!=after.text or before.ruby!=after.ruby:raise ValueError('CSS underline reference changed text or ruby')
   continue
  if marker.get('source_placement','prefix')!='prefix':raise ValueError('Unknown underline reference source placement')
  matches=[n for n in soup.find_all('u')if Projection({'html':str(n)}).text==marker['text']and isinstance(n.previous_sibling,NavigableString)and str(n.previous_sibling).rstrip().endswith(marker['label'])]
  if len(matches)!=1:raise ValueError('Underline reference must match one adjacent accepted marker and exact phrase')
  n=matches[0];previous=n.previous_sibling;raw=str(previous);pos=raw.rfind(marker['label']);previous.replace_with(raw[:pos]+raw[pos+len(marker['label']):]);n['data-reference-label']=marker['label']
  if 'clearance_below_pt' in marker:
   clearance=marker['clearance_below_pt']
   if isinstance(clearance,bool)or not isinstance(clearance,(int,float))or not 0<=clearance<=12:raise ValueError('Invalid underline reference clearance')
   n['data-reference-clearance']=str(clearance)
 return {'html':str(soup)}


def prepare_cloze_markers(value,labels):
 """Add a presentational box role while preserving every accepted base character."""
 soup=BeautifulSoup(value['html'],'html.parser')
 if len(labels)!=len(set(labels)):raise ValueError('Duplicate source-bound cloze label')
 for label in labels:
  if not re.fullmatch(r'[0-9]+',label):raise ValueError('Invalid source-bound cloze label')
  token='['+label+']';matches=[n for n in soup.descendants if isinstance(n,NavigableString)and n.parent.name not in ['rt','rp']and token in str(n)]
  if len(matches)!=1 or str(matches[0]).count(token)!=1:raise ValueError('Source-bound cloze token must occur once')
  n=matches[0];a,b=str(n).split(token);span=soup.new_tag('span');span['data-cloze-label']=label;span.string=token
  n.replace_with(NavigableString(a),span,NavigableString(b))
 result={'html':str(soup)}
 if Projection(result).text!=Projection(value).text:raise ValueError('Cloze presentation changed accepted projection')
 return result
