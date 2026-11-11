"""Optional, hash-bound notice presentation; accepted rich values stay unchanged."""
import hashlib,re,math,html,copy
from pathlib import Path
from bs4 import BeautifulSoup,Tag,NavigableString
from model import digest,Projection
from notice_layout import notice_nodes,html_lines,body_nodes_tex,panel_heading


def render_notice(conv,value,style,level_root,original_value=None):
 allowed={'content_sha256','body_pt','baseline_pt','word_space_em','paragraph_skip_pt','frame_padding_pt','title','contact','asset','indent_hierarchy','body_width_fraction','intro_word_space_em','table_word_space_em','wave_separators','intro_align','emphasis_terms','flow_lines','content_selector','line_styles','intro_line_count','intro_bold','frame_top_pt','frame_bottom_pt','inset_panels','frame_rule','list_indent_em','latin_role'}
 allowed.update(['ruby_intergap_em','intro_break_before','collapse_paragraph_boundaries','page_frame'])
 allowed.add('colon_fields')
 allowed.add('page_segments')
 allowed.add('segments_same_page')
 allowed.add('list_continuations')
 allowed.add('page_flow')
 allowed.add('table_row_breaks')
 if set(style)-allowed:raise ValueError('Unknown notice style property')
 if digest(value if original_value is None else original_value)!=style['content_sha256']:raise ValueError('Stale notice content binding')
 if not isinstance(value,dict):raise ValueError('Notice region styles require rich HTML')
 if 'table_row_breaks' in style:
  from notice_table_pages import render_table_pages
  return render_table_pages(conv,value,style,level_root,render_notice)
 if 'page_segments' in style:
  from notice_layout import split_notice_pages
  segments=split_notice_pages(value,style)
  parts=[]
  for fragment,segment in segments:
   child=copy.deepcopy(style);child.pop('page_segments');child.pop('content_selector',None);child.pop('segments_same_page',None)
   child.update(content_sha256=digest(fragment),flow_lines=False,title=segment['title'],contact=segment['contact'])
   for key in ['content_selector','line_styles']:
    if key in segment:child[key]=copy.deepcopy(segment[key])
   parts.append(render_notice(conv,fragment,child,level_root))
  conv.features.append({'kind':'notice_page_segments','content_sha256':style['content_sha256'],'start_texts':[s['start_text'] for v,s in segments]})
  if style.get('segments_same_page'):
   conv.features.append({'kind':'notice_segments_same_page','segments':len(parts),'content_sha256':style['content_sha256']})
   return r'\SamePageNotices{'+r'\par\vspace{6pt}'.join(parts)+'}'
  return r'\clearpage'.join(parts)
 for key in ['body_pt','baseline_pt','frame_padding_pt']:
  if not isinstance(style[key],(int,float)) or style[key]<=0:raise ValueError('Invalid notice dimension')
 title_style=style['title'];contact_style=style['contact']
 if title_style['selector']not in ['leading_region','leading_nodes','none']:raise ValueError('Unsupported notice title selector')
 soup=BeautifulSoup(value['html'],'html.parser')
 nodes=notice_nodes(value,style) if style.get('flow_lines')or style.get('content_selector') else [n for n in soup.children if not isinstance(n,NavigableString) or n.strip()]
 if not nodes:raise ValueError('Empty styled notice')
 if len(nodes)==1 and isinstance(nodes[0],Tag) and nodes[0].name=='section':
  nodes=[n for n in nodes[0].children if not isinstance(n,NavigableString) or n.strip()]
 title=[]
 if title_style['selector']=='none':
  if title_style['line_sizes_pt']:raise ValueError('Untitled notice cannot have title dimensions')
  title_html=''
 elif title_style['selector']=='leading_nodes':
  count=title_style['node_count']
  if not 0<count<len(nodes):raise ValueError('Invalid leading notice node count')
  title_html=''.join(map(str,nodes[:count]));nodes=nodes[count:]
 elif isinstance(nodes[0],Tag) and nodes[0].name in ['center','p','h1','h2','h3']:
  title_html=nodes.pop(0).decode_contents()
 else:
  while nodes and not (isinstance(nodes[0],Tag) and nodes[0].name in ['p','div','table']):title.append(nodes.pop(0))
  title_html=''.join(map(str,title))
 if title_style.get('plain_prefix'):
  prefix=title_style['plain_prefix'];fragment=BeautifulSoup(title_html,'html.parser');first=next((n for n in fragment.descendants if isinstance(n,NavigableString)and n.strip()),None)
  if first is None or first.parent.name in ['ruby','rt','rp']or not str(first).startswith(prefix):raise ValueError('Notice prefix must match the complete leading plain title')
  first.replace_with(str(first)[len(prefix):]);intro=BeautifulSoup('<p></p>','html.parser').p
  for n in list(fragment.contents):intro.append(n)
  if not Projection({'html':str(intro)}).text.strip():raise ValueError('Notice prefix has no remaining intro')
  nodes.insert(0,intro);title_html=html.escape(prefix)
 if not title_html and title_style['selector']!='none':raise ValueError('Missing notice title')
 contact=[]
 if contact_style['selector']=='none':pass
 elif contact_style['selector']=='last_paragraph':
  if not nodes or not isinstance(nodes[-1],Tag) or nodes[-1].name not in ['p','div']:raise ValueError('Missing terminal notice contact paragraph')
  contact=[nodes.pop()]
 elif contact_style['selector']=='marker_suffix':
  marker=contact_style['marker']
  found=[i for i,n in enumerate(nodes) if Projection({'html':str(n)}).text.strip()==marker]
  if len(found)!=1:raise ValueError('Notice contact marker must select one complete node')
  contact=nodes[found[0]:];nodes=nodes[:found[0]]
 elif contact_style['selector']=='last_panel_suffix':
  from notice_layout import split_nested_contact
  nodes,contact=split_nested_contact(nodes,contact_style['marker'])
 else:raise ValueError('Unsupported notice contact selector')
 if contact and not any(x in Projection({'html':''.join(map(str,contact))}).text for x in ['電話','〒','@','https://','http://']):raise ValueError('Notice contact role is not supported by content')
 asset=style.get('asset');asset_tex=None
 if asset:
  if asset['role']!='decorative' or asset['placement'] not in ['intro_right','contact_left','title_right','title_left','table_right']:raise ValueError('Invalid notice asset role')
  if not 0<asset['width_fraction']<.6:raise ValueError('Invalid decorative asset width')
  root=Path(level_root).resolve();path=(root/asset['path']).resolve()
  if not path.is_relative_to(root) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=asset['sha256']:raise ValueError('Missing or stale notice asset')
  asset_tex=r'\includegraphics[width=\linewidth]{'+path.as_posix()+'}'
  conv.features.append({'kind':'decorative_asset','path':path.as_posix(),'sha256':asset['sha256'],'role':'decorative','placement':asset['placement']})
 if asset and asset['placement']=='table_right':
  if 'table_index'not in asset or 'table_width_fraction'not in asset or asset['table_index']>=len(soup.find_all('table'))or asset['table_width_fraction']+asset['width_fraction']>.98:raise ValueError('Table artwork requires an existing table and disjoint widths')
  conv.notice_table_asset={**asset,'absolute_path':path.as_posix()}
 width=style.get('body_width_fraction',1)
 if not .7<=width<=1:raise ValueError('Invalid notice body width')
 saved=conv.word_space_em;conv.word_space_em=style.get('word_space_em',saved);conv.notice_cell_word_space_em=style.get('table_word_space_em',conv.word_space_em)
 try:
  clean=lambda t:re.sub(r'^(?:(?:\\Para|\\NoticeLine)\s*)+|(?:(?:\\Para|\\NoticeLine)\s*)+$','',t).strip()
  if title_style.get('structured_lines')or title_style.get('attached_bar'):
   raw_lines=html_lines(title_html,title_style.get('break_before'))
   if title_style.get('attached_bar'):
    idx=title_style['attached_bar']['line_index']
    if not 0<=idx<len(raw_lines):raise ValueError('Attached title bar line changed')
    fragment=BeautifulSoup(raw_lines[idx],'html.parser')
    for underline in list(fragment.find_all('u')):underline.unwrap()
    raw_lines[idx]=str(fragment)
   title_lines=[clean(conv.value({'html':line},'notice'))for line in raw_lines]
  else:
   title_tex=clean(conv.value({'html':title_html},'notice'))
   title_lines=[clean(x) for x in re.split(r'\\NoticeLine|\\Para',title_tex) if clean(x)]
  if len(title_lines)!=len(title_style['line_sizes_pt']):raise ValueError('Notice title line count changed')
  aligns=title_style.get('line_alignments',['center']*len(title_lines))
  if len(aligns)!=len(title_lines) or any(x not in ['left','center','right']for x in aligns):raise ValueError('Invalid notice title alignment')
  families=title_style.get('line_font_families',['heading']*len(title_lines))
  if len(families)!=len(title_lines)or any(x not in ['heading','body','notice_heading']for x in families):raise ValueError('Invalid title font roles')
  slants=title_style.get('line_slants',[0]*len(title_lines))
  if len(slants)!=len(title_lines)or any(isinstance(x,bool)or not isinstance(x,(int,float))or not 0<=x<=.3 for x in slants):raise ValueError('Invalid title slant')
  title_parts=[]
  for idx,(line,sz,align)in enumerate(zip(title_lines,title_style['line_sizes_pt'],aligns)):
   line_gaps=title_style.get('line_before_pt',[0]*len(title_lines))
   if len(line_gaps)!=len(title_lines)or any(type(x)not in [int,float]or not 0<=x<=24 for x in line_gaps):raise ValueError('Invalid title line gaps')
   if line_gaps[idx]:title_parts.append(r'\vspace{'+str(line_gaps[idx])+'pt}')
   bar=title_style.get('attached_bar')
   if bar and idx==bar['line_index']:
    if width!=1 or bar['edge']!=align or bar['edge']not in ['left','right']:raise ValueError('Attached bar must meet an aligned full-width notice edge')
    from title_ribbons import render as ribbon
    line=ribbon(conv,line,bar,align,sz,style['frame_padding_pt'],slants[idx],idx)
   face=r'\rmfamily\mcfamily 'if families[idx]=='body'else r'\NoticeHeadingJapanese 'if families[idx]=='notice_heading'else r'\sffamily\gtfamily '
   if slants[idx]:face+=r'\addjfontfeatures{FakeSlant='+str(slants[idx])+'}'
   title_parts.append('{'+face+({'left':r'\raggedright ','center':r'\centering ','right':r'\raggedleft '}[align])+r'\fontsize{'+str(sz)+'}{'+str(sz*title_style.get('leading_ratio',1.3))+r'}\selectfont '+line+r'\par}')
  title_tex=r'\par\vspace{'+str(title_style['before_pt'])+r'pt}{\sffamily\gtfamily '+''.join(title_parts)+r'}\vspace{'+str(title_style['after_pt'])+'pt}'
  if title_style['selector']=='none':title_tex=''

  if asset and asset['placement'] in ['title_right','title_left']:
   left=asset['placement']=='title_left'
   inset=asset.get('left_inset_pt' if left else 'right_inset_pt',0)
   if not 0<=inset<=60:raise ValueError('Invalid title artwork inset')
   drop=r'\dimexpr-\height-'+str(asset.get('raise_pt',0))+r'pt\relax'if asset.get('vertical_alignment')=='top'else '-'+str(asset.get('raise_pt',0))+'pt'
   offset=str(inset)+'pt' if left else r'\dimexpr '+str(1-asset['width_fraction'])+r'\linewidth-'+str(inset)+r'pt\relax'
   title_tex=r'\noindent\makebox[0pt][l]{\hspace{'+offset+r'}\raisebox{'+drop+r'}[0pt][0pt]{\includegraphics[width='+str(asset['width_fraction'])+r'\linewidth]{'+path.as_posix()+'}}}'+title_tex

  if title_style.get('shape')=='arch':
   raw=Projection({'html':title_html}).text.strip()
   if len(title_lines)!=1 or '<ruby' in title_html or not 3<=len(raw)<=30:raise ValueError('Arched title requires one plain short title')
   size=title_style['line_sizes_pt'][0];rise=title_style['arch_rise_pt'];sweep=title_style['arch_sweep_degrees'];glyphs=[]
   for index,ch in enumerate(raw):
    t=(2*index/(len(raw)-1))-1;angle=-t*sweep/2;up=rise*(1-t*t)
    glyphs.append(r'\raisebox{'+str(round(up,3))+r'pt}{\rotatebox{'+str(round(angle,3))+'}{'+conv.text(ch)+'}}')
   title_tex=r'\par\vspace{'+str(title_style['before_pt'])+r'pt}{\centering\sffamily\gtfamily\fontsize{'+str(size)+'}{'+str(size*1.3)+r'}\selectfont '+''.join(glyphs)+r'\par}\vspace{'+str(title_style['after_pt'])+'pt}'
   conv.features.append({'kind':'arched_title','text':raw,'rise_pt':rise,'sweep_degrees':sweep})
  if title_style.get('shape') in ['box','opposite_round_box']:
   title_width=title_style.get('box_width_fraction',.8)
   if not .5<=title_width<=1:raise ValueError('Invalid boxed notice title width')
   pad=title_style.get('box_padding_pt',2)
   if not 0<=pad<=20:raise ValueError('Invalid boxed title padding')
   if title_style['shape']=='opposite_round_box':
    radius=title_style.get('box_radius_pt',6)
    if not 0<radius<=15:raise ValueError('Invalid title corner radius')
    framed=r'{\let\NoticePanelStroke\NoticeOppositePanelStroke\NoticeInsetPanel{'+str(radius)+'}{'+str(pad)+'}{'+title_tex+'}}'
   else:
    outer_rule=style.get('frame_rule',{})
    # A declared title box must not inherit hidden edges from its enclosing
    # notice. Preserve existing TeX when the enclosing frame has all edges.
    edges=',topline=true,bottomline=true,leftline=true,rightline=true'if outer_rule.get('style')=='none'or set(outer_rule.get('edges',['top','bottom','left','right']))!={'top','bottom','left','right'}else''
    framed=r'\begin{NoticeFrame}[nobreak=true,skipabove=0pt,skipbelow=0pt,innertopmargin='+str(pad)+r'pt,innerbottommargin='+str(pad)+'pt'+edges+']'+title_tex+r'\end{NoticeFrame}'
   title_tex=r'\par{\centering\begin{minipage}{'+str(title_width)+r'\linewidth}'+framed+r'\end{minipage}\par}\vspace{6pt}'
  contact_html=''.join(map(str,contact))
  if 'break_before'in contact_style:contact_html='<br/>'.join(html_lines(contact_html,contact_style['break_before']))
  contact_tex=clean(conv.value({'html':contact_html},'notice'))
  if contact_style.get('segments'):
   from contact_lines import render as render_contact
   contact_tex=render_contact(conv,contact_html,contact_style)
  if 'telephone'in contact_style:
   phone=contact_style['telephone'];scale=contact_style['phone_dash_scale']
   if not re.fullmatch(r'[0-9]+(?:-[0-9]+){2}',phone)or contact_tex.count(phone)!=1 or not 1<=scale<=2:raise ValueError('Invalid exact telephone presentation')
   contact_tex=contact_tex.replace(phone,phone.replace('-',r'\scalebox{'+str(scale)+r'}[1]{-}'),1)
  if contact_style['flow']=='postal_two_lines':
   ls=[clean(x) for x in re.split(r'\\NoticeLine|\\Para',contact_tex) if clean(x)]
   if not ls[-1].startswith('〒'):raise ValueError('Postal contact flow requires terminal address')
   contact_tex=r'\hspace{.3em}'.join(ls[:-1])+r'\NoticeLine '+ls[-1]
  elif contact_style['flow']=='join_last_two_lines':
   ls=[clean(x)for x in re.split(r'\\NoticeLine|\\Para',contact_tex)if clean(x)]
   if len(ls)<3 or not ls[-2].startswith('電話')or not ls[-1].startswith('ホームページ'):raise ValueError('Joined contact requires terminal phone and website lines')
   contact_tex=r'\NoticeLine '.join(ls[:-2]+[ls[-2]+r'\hspace{1em}'+ls[-1]])
  elif contact_style['flow']!='preserve':raise ValueError('Unsupported contact flow')
  if 'baseline_pt'in contact_style:
   pitch=contact_style['baseline_pt']
   if isinstance(pitch,bool)or not isinstance(pitch,(int,float))or not 8<=pitch<=30:raise ValueError('Invalid contact baseline')
   contact_tex=r'\fontsize{'+str(style['body_pt'])+'}{'+str(pitch)+r'}\selectfont '+contact_tex
  if 'email_phone_separator_width_em'in contact_style:
   separator_width=contact_style['email_phone_separator_width_em']
   if isinstance(separator_width,bool)or not .5<=separator_width<=1.5 or contact_tex.count('/')!=1 or '@'not in contact_tex or 'telephone'not in contact_style:raise ValueError('Invalid email/phone separator width')
   contact_tex=contact_tex.replace('/',r'\makebox['+str(separator_width)+r'em][c]{/}')
  contact_tex='{'+({'left':r'\raggedright ','right':r'\raggedleft '}[contact_style.get('align','right')])+contact_tex+r'\par}'
  if 'rule_before_pt'in contact_style:
   weight=contact_style['rule_before_pt']
   if not contact or isinstance(weight,bool)or not isinstance(weight,(int,float))or not .1<=weight<=2:
    raise ValueError('Contact separator requires an existing contact and bounded single rule')
   contact_tex=r'\par\hrule height '+str(weight)+r'pt\relax\nobreak\vspace{5pt}'+contact_tex
   conv.features.append({'kind':'notice_contact_rule','width_pt':weight,'contact_text':Projection({'html':contact_html}).text})
  intro_tex=''
  if asset and asset['placement']=='intro_right':
   while nodes and isinstance(nodes[0],Tag) and nodes[0].name=='br':nodes.pop(0)
   count=style.get('intro_line_count',1)
   if len(nodes)<count or any(not isinstance(n,Tag)or n.name not in ['p','center']for n in nodes[:count]):raise ValueError('Intro artwork requires existing leading intro paragraphs')
   intro_nodes=nodes[:count];nodes=nodes[count:]
   conv.keep_spaced_words=True;body_space=conv.word_space_em;conv.word_space_em=style.get('intro_word_space_em',body_space)
   try:
    intro_html=''.join(map(str,intro_nodes))
    if 'intro_break_before' in style:intro_html='<br/>'.join(html_lines(intro_html,style['intro_break_before']))
    intro=clean(conv.value({'html':intro_html},'notice'))
   finally:conv.keep_spaced_words=False;conv.word_space_em=body_space
   if style.get('intro_bold'):intro=r'{\sffamily\gtfamily\bfseries '+intro+'}'
   w=asset['width_fraction']
   intro_tex=r'\par\noindent\begin{minipage}[t]{'+str(1-w-.03)+r'\linewidth}\vspace{0pt}\raggedright '+intro+r'\par\end{minipage}\hfill\begin{minipage}[t]{'+str(w)+r'\linewidth}\vspace{0pt}\vspace{-'+str(asset.get('raise_pt',0))+r'pt}'+asset_tex+r'\end{minipage}\par\vspace{8pt}'
  if style.get('wave_separators'):
   tables=[i for i,n in enumerate(nodes) if isinstance(n,Tag) and n.find('table')]
   if len(tables)!=1:raise ValueError('Wave bands require one table wrapper')
   pos=tables[0];nodes.insert(pos,BeautifulSoup('<hr/>','html.parser').hr);nodes.insert(pos+2,BeautifulSoup('<hr/>','html.parser').hr);nodes.append(BeautifulSoup('<hr/>','html.parser').hr)
  if style.get('intro_align')=='center':
   if not nodes or not isinstance(nodes[0],Tag) or nodes[0].name!='p':raise ValueError('Centered intro requires the leading body paragraph')
   nodes[0]['style']='text-align:center'
  panels=style.get('inset_panels')
  if panels:
   selector=panels.get('selector','table_divs')
   if set(panels)&{'title_align','title_rule_pt'}and 'title_font_pt'not in panels:raise ValueError('Inset title geometry requires an explicit title size')
   if selector not in ['table_divs','bordered_divs','titled_divs','flow_ranges']:raise ValueError('Unknown inset panel selector')
   if selector=='flow_ranges':
    if not style.get('flow_lines')or 'title_font_pt'not in panels:raise ValueError('Flow panels require explicit lines and title size')
    from notice_layout import group_flow_panels
    nodes,selected=group_flow_panels(nodes,panels)
   else:
    if 'ranges'in panels:raise ValueError('Panel ranges require flow range selector')
    selected=[n for n in nodes if isinstance(n,Tag)and n.name=='div'and (n.find('table')if selector=='table_divs'else 'border:'in n.get('style','')if selector=='bordered_divs'else True)]
   if len(selected)!=len(panels['titles']):raise ValueError('Inset notice panel count changed')
   if selector=='titled_divs'and len(set(panels['titles']))!=len(panels['titles']):raise ValueError('Duplicate inset notice panel title')
   if 'line_styles'in panels and (selector not in ['titled_divs','flow_ranges']or 'title_font_pt'not in panels or len(panels['line_styles'])!=len(selected)):raise ValueError('Panel line styles require one exact titled entry per panel and an explicit title size')
   for idx,(node,title)in enumerate(zip(selected,panels['titles'])):
    if not title or panel_heading(node)!=title:raise ValueError('Inset notice panel title changed')
    if selector=='titled_divs':
     from section_layout import flow_lines
     if node.find(['div','section','table']):raise ValueError('Titled notice panel requires simple existing lines')
     children=flow_lines(list(node.children));node.clear()
     for child in children:node.append(child)
    node['data-notice-inset-panel']=str(idx)
   conv.notice_inset_panels=panels
  conv.keep_spaced_words=conv.word_space_em>0
  if style.get('colon_fields'):
   from notice_fields import prepare as prepare_fields
   nodes=prepare_fields(nodes,style['colon_fields']);conv.notice_fields=style['colon_fields']
  conv.notice_list_indent=style.get('list_indent_em')
  conv.notice_list_continuations=style.get('list_continuations',[])
  conv.notice_list_continuations_used=[]
  if conv.notice_list_continuations and conv.notice_list_indent is None:raise ValueError('List continuations require an explicit native list indent')
  try:body_tex=clean(body_nodes_tex(conv,nodes,style['line_styles']))if 'line_styles'in style else clean(conv.value({'html':''.join(map(str,nodes))},'notice'))
  finally:conv.keep_spaced_words=False
  if sorted(conv.notice_list_continuations_used)!=list(range(len(conv.notice_list_continuations))):raise ValueError('List continuation must match one complete existing list item')
  if style.get('collapse_paragraph_boundaries'):
   # Match value()'s normal rich-paragraph normalization when individual
   # source-bound lines are emitted through body_nodes_tex instead.
   body_tex=re.sub(r'(?:\s*\\Para\s*){2,}',lambda m:r'\Para ',body_tex)
  if style.get('wave_separators'):body_tex=body_tex.replace(r'\par\smallskip\hrule\smallskip',r'\WaveRule{}')
  for emphasis in style.get('emphasis_terms',[]):
   # Match the exact rich fragment, including already frozen ruby wrappers.
   # Plain-text re-emission cannot find a decorated term and must not drop ruby.
   ep=Projection({'html':''.join(map(str,nodes))});term=emphasis['text']
   if ep.text.count(term)!=1:raise ValueError('Emphasis must select one exact base-text term')
   a=ep.text.index(term);b=a+len(term)
   if any(r['start']<a<r['end']or r['start']<b<r['end']for r in ep.ruby):raise ValueError('Emphasis boundary splits ruby')
   ra,rb=ep.mapping[a][0],ep.mapping[b-1][1]
   for r in ep.ruby:
    if r['start']==a:ra=ep.raw.rfind('<ruby',0,ra+1)
    if r['end']==b:rb=ep.raw.find('</ruby>',rb)+7
   fragment={'html':ep.raw[ra:rb]}
   if Projection(fragment).text!=term:raise ValueError('Emphasis crosses unsupported markup')
   feature_count=len(conv.features);keep=conv.keep_spaced_words;conv.keep_spaced_words=False
   try:token=conv.value(fragment,'notice')
   finally:conv.keep_spaced_words=keep;del conv.features[feature_count:]
   if body_tex.count(token)!=1:
    # Bound body lines may keep complete existing spaced/ruby words. Reproduce
    # that exact alternate emitter state, never strip markup or match fuzzily.
    feature_count=len(conv.features);conv.keep_spaced_words=conv.word_space_em>0
    try:token=conv.value(fragment,'notice')
    finally:conv.keep_spaced_words=keep;del conv.features[feature_count:]
   if body_tex.count(token)!=1:raise ValueError('Emphasis must select exactly one body term')
   gaps=[emphasis.get(k,0)for k in ['before_em','after_em']]
   if any(isinstance(v,bool)or not isinstance(v,(int,float))or not 0<=v<=1.5 for v in gaps):raise ValueError('Invalid emphasis boundary space')
   body_tex=body_tex.replace(token,r'\hspace{'+str(gaps[0])+r'em}{\bfseries\fontsize{'+str(emphasis['font_pt'])+'}{'+str(emphasis['font_pt']*1.4)+r'}\selectfont '+token+r'}\hspace{'+str(gaps[1])+'em}',1)
  if style.get('indent_hierarchy'):
   pieces=re.split(r'(\\Para|\\NoticeLine)',body_tex);formatted=[]
   for piece in pieces:
    if not piece.strip():continue
    if piece in [r'\Para',r'\NoticeLine']:formatted.append(piece);continue
    if re.match(r'^\{\\bfseries [A-Z][.．]',piece.strip()):indent=0
    elif piece.lstrip().startswith(('【','<','〈','①','②','③','④')):indent=.8
    else:indent=1.8
    hang='.6em' if piece.lstrip().startswith(('・','※')) else '0pt'
    formatted.append(r'{\leftskip='+str(indent)+r'em\hangindent='+hang+r'\hangafter=1 '+piece+r'\par}')
   body_tex=''.join(formatted)
  if asset and asset['placement']=='contact_left':
   w=asset['width_fraction'];inset=asset.get('left_inset_pt',0);raise_pt=contact_style.get('raise_pt',0)
   if not 0<=inset<=30 or not 0<=raise_pt<=30:raise ValueError('Invalid contact alignment')
   text=r'\begin{minipage}[b]{'+str(1-w-.03)+r'\linewidth}'+contact_tex+r'\end{minipage}'
   if raise_pt:text=r'\raisebox{'+str(raise_pt)+'pt}{'+text+'}'
   contact_tex=r'\par\noindent'+(r'\hspace*{'+str(inset)+'pt}'if inset else'')+r'\begin{minipage}[b]{'+str(w)+r'\linewidth}'+asset_tex+r'\end{minipage}\hfill'+text+r'\par'
  if r'\AuthoredWordGap{' in body_tex:
   # Authored word groups carry their own finite gaps. Stretching the remaining
   # Japanese glue to justify a line creates conspicuous gaps inside a group.
   body_tex=r'{\rightskip=0pt plus 1fil\relax '+body_tex+r'\par}'
   conv.features.append({'kind':'grouped_notice_ragged_right','content_sha256':style['content_sha256'],'basis':'explicit authored word boundaries'})
  p=style['frame_padding_pt']
  from rules import frame_options
  frame_rule_options=','+frame_options(style['frame_rule']) if 'frame_rule'in style else ''
  result=r'{\fontsize{'+str(style['body_pt'])+'}{'+str(style['baseline_pt'])+r'}\selectfont\setlength\parindent{0pt}\setlength\parskip{0pt}\renewcommand\Para{\par\addvspace{'+str(style['paragraph_skip_pt'])+r'pt}\noindent}\WholeNotice{innerleftmargin='+str(p)+'pt,innerrightmargin='+str(p)+'pt,innertopmargin='+str(style.get('frame_top_pt',p))+'pt,innerbottommargin='+str(style.get('frame_bottom_pt',p))+'pt'+frame_rule_options+'}{'+r'\noindent\hfil\begin{minipage}{'+str(width)+r'\linewidth}'+title_tex+intro_tex+body_tex+r'\par\vspace{'+str(contact_style['before_pt'])+'pt}'+contact_tex+r'\end{minipage}\hfil}}'
  if style.get('page_flow'):
   if style['page_flow']!='whole_or_continue' or width!=1 or 'page_frame'in style:raise ValueError('Native notice continuation requires the complete full-width document')
   content=title_tex+intro_tex+body_tex+r'\par\vspace{'+str(contact_style['before_pt'])+'pt}'+contact_tex
   result=(r'{\fontsize{'+str(style['body_pt'])+'}{'+str(style['baseline_pt'])+r'}\selectfont\setlength\parindent{0pt}\setlength\parskip{0pt}\renewcommand\Para{\par\addvspace{'+str(style['paragraph_skip_pt'])+r'pt}\noindent}\FlowingNotice{innerleftmargin='+str(p)+'pt,innerrightmargin='+str(p)+'pt,innertopmargin='+str(style.get('frame_top_pt',p))+'pt,innerbottommargin='+str(style.get('frame_bottom_pt',p))+'pt'+frame_rule_options+'}{'+content+'}}')
   conv.features.append({'kind':'native_whole_notice_continuation','policy':'keep_whole_when_it_fits_otherwise_native_frame_flow'})
  if 'page_frame' in style:
   if width!=1:raise ValueError('Registered notice uses its explicit inner frame width')
   from registered_notice import render as registered_frame
   content=r'\fontsize{'+str(style['body_pt'])+'}{'+str(style['baseline_pt'])+r'}\selectfont\setlength\parindent{0pt}\setlength\parskip{0pt}\renewcommand\Para{\par\addvspace{'+str(style['paragraph_skip_pt'])+r'pt}\noindent}'+title_tex+intro_tex+body_tex+r'\par\vspace{'+str(contact_style['before_pt'])+'pt}'+contact_tex
   result=registered_frame(content,style)
  if style.get('latin_role')=='document':result=r'{\DocumentLatin '+result+'}'
  if 'ruby_intergap_em' in style:
   gap=style['ruby_intergap_em']
   if isinstance(gap,bool) or not isinstance(gap,(int,float)) or not 0<=gap<=.2:raise ValueError('Invalid notice ruby gap')
   result=r'{\ltjsetruby{intergap='+str(gap)+'}'+result+'}'
  conv.features.append({'kind':'notice_regions','content_sha256':style['content_sha256'],'title_lines':len(title_lines),'contact_selector':contact_style['selector'],'asset':bool(asset)})
  return result
 finally:
  conv.word_space_em=saved
  conv.notice_table_asset=None
  conv.notice_inset_panels=None
  conv.notice_list_indent=None
  conv.notice_list_continuations=[]
  conv.notice_list_continuations_used=[]
