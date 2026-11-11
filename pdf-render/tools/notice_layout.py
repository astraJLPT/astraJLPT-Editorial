"""Hash-bound notice reflow helpers; original HTML is never edited."""
import html,re
from bs4 import BeautifulSoup,Tag,NavigableString
from model import Projection,digest
from section_layout import flow_lines


def meaningful(nodes):
 return [n for n in nodes if not (isinstance(n,NavigableString)and not n.strip()) and not (isinstance(n,Tag)and n.name=='br')]


def panel_heading(node):
 """Read the first content line, excluding non-content HTML whitespace."""
 return next((line.strip() for line in Projection({'html':str(node)}).text.splitlines() if line.strip()),'')


def notice_nodes(value,style):
 soup=BeautifulSoup(value['html'],'html.parser');nodes=list(soup.children)
 if style.get('content_selector')=='outer_div':
  roots=[n for n in soup.children if not isinstance(n,NavigableString)or n.strip()]
  if len(roots)!=1 or not isinstance(roots[0],Tag)or roots[0].name!='div':raise ValueError('Outer notice selector requires one complete root div')
  nodes=list(roots[0].children)
 elif style.get('content_selector')in ['single_section','single_div']:
  tag='section'if style['content_selector']=='single_section'else'div'
  regions=soup.find_all(tag)
  if len(regions)!=1:raise ValueError('Styled notice requires exactly one section')
  outside=BeautifulSoup(str(soup),'html.parser');outside.find(tag).decompose()
  if Projection({'html':str(outside)}).text.strip():raise ValueError('Notice section has outside content')
  nodes=list(regions[0].children)
 if style.get('flow_lines'):
  nodes=flow_lines(nodes)
  nodes=[n for n in nodes if Projection({'html':str(n)}).text.strip()]
  for n in nodes:
   if isinstance(n,Tag)and n.name=='div' and n.find('table') and not style.get('inset_panels'):
    for br in list(n.find_all('br',recursive=False)):br.decompose()
 return nodes


def group_flow_panels(nodes,panels):
 """Wrap declared complete consecutive nodes without changing table/text order."""
 specs=panels.get('ranges',[]);titles=panels['titles']
 if len(specs)!=len(titles) or not specs or len(set(titles))!=len(titles):
  raise ValueError('Flow panels need one unique title and range per panel')
 before=Projection({'html':''.join(map(str,nodes))});ranges=[]
 for title,spec in zip(titles,specs):
  if set(spec)!={'end_node_sha256'}:raise ValueError('Invalid flow panel range')
  starts=[i for i,n in enumerate(nodes)if Projection({'html':str(n)}).text.strip()==title]
  ends=[i for i,n in enumerate(nodes)if digest({'html':str(n)})==spec['end_node_sha256']]
  if len(starts)!=1 or len(ends)!=1 or starts[0]>=ends[0]:
   raise ValueError('Flow panel requires unique complete title and later end node')
  a,b=starts[0],ends[0]
  if nodes[a].name not in ['p','center','h1','h2','h3']or nodes[a].find(['table','div','section','br']):
   raise ValueError('Flow panel title must be one simple complete line')
  for n in nodes[a:b+1]:
   if not isinstance(n,Tag)or n.name not in ['p','center','h1','h2','h3','table']:
    raise ValueError('Flow panel requires complete simple lines or native tables')
   if n.find(['div','section'])or (n.name!='table'and n.find('table'))or (n.name=='table'and n.find('table')):
    raise ValueError('Nested flow panel content is unsupported')
  if ranges and a<=ranges[-1][1]:raise ValueError('Flow panels overlap or reverse order')
  ranges.append((a,b))
 out=[];selected=[];cursor=0
 for a,b in ranges:
  out.extend(nodes[cursor:a]);panel=BeautifulSoup('<div></div>','html.parser').div
  for n in nodes[a:b+1]:panel.append(n)
  out.append(panel);selected.append(panel);cursor=b+1
 out.extend(nodes[cursor:])
 after=Projection({'html':''.join(map(str,out))})
 if ''.join(before.text.split())!=''.join(after.text.split())or [(r['base'],r['reading'])for r in before.ruby]!=[(r['base'],r['reading'])for r in after.ruby]:
  raise ValueError('Flow panels changed text or ruby')
 return out,selected


def split_nested_contact(nodes,marker):
 """Lift a declared complete terminal contact suffix out of the last panel."""
 if not isinstance(marker,str)or not marker.strip():raise ValueError('Nested contact requires an exact nonempty marker')
 if not nodes or not isinstance(nodes[-1],Tag)or nodes[-1].name!='div':raise ValueError('Nested contact requires a terminal div panel')
 before=Projection({'html':''.join(map(str,nodes))})
 panel=nodes[-1]
 if panel.find(['div','table','section']):raise ValueError('Nested contact panel must contain simple lines')
 children=meaningful(flow_lines(list(panel.children)))
 matches=[i for i,n in enumerate(children)if Projection({'html':str(n)}).text.strip()==marker]
 if len(matches)!=1 or matches[0]==0:raise ValueError('Nested contact must select one complete suffix after panel content')
 at=matches[0];contact=children[at:];panel.clear()
 for n in children[:at]:panel.append(n)
 after=Projection({'html':''.join(map(str,nodes+contact))})
 if ''.join(before.text.split())!=''.join(after.text.split())or [(r['base'],r['reading'])for r in before.ruby]!=[(r['base'],r['reading'])for r in after.ruby]:raise ValueError('Nested contact changed content or ruby')
 return nodes,contact


def split_notice_pages(value,style):
 """Only explicitly authored whole-node boundaries may divide a notice."""
 segments=style['page_segments']
 if not style.get('flow_lines') or not 2<=len(segments)<=4:
  raise ValueError('Notice pages require two to four explicitly authored flow segments')
 if set(style)&{'page_frame','asset','inset_panels','line_styles','colon_fields','emphasis_terms'}:
  raise ValueError('Notice page segments conflict with whole-notice geometry or selectors')
 nodes=notice_nodes(value,style);starts=[]
 for segment in segments:
  if not {'start_text','title','contact'}<=set(segment)or set(segment)-{'start_text','title','contact','content_selector','line_styles'}:raise ValueError('Invalid notice page segment')
  if 'content_selector'in segment and segment['content_selector']!='outer_div':raise ValueError('Segment selector must name one complete outer div')
  found=[n for n,x in enumerate(nodes)if Projection({'html':str(x)}).text.strip()==segment['start_text']]
  if len(found)!=1:raise ValueError('Notice page must begin at one exact complete node')
  starts.append(found[0])
 if starts[0]!=0 or starts!=sorted(set(starts)):
  raise ValueError('Notice pages must preserve the complete original node order')
 stops=starts[1:]+[len(nodes)]
 return [({'html':''.join(map(str,nodes[a:b]))},s)for a,b,s in zip(starts,stops,segments)]


def html_lines(raw,break_before=None,*,preserve_underlined_blanks=False,preserve_historical_word_gaps=False):
 """Split explicit lines before TeX conversion, retaining balanced inline markup."""
 soup=BeautifulSoup(raw,'html.parser')
 if break_before:
  found=[n for n in soup.descendants if isinstance(n,NavigableString)and n.parent.name not in ['rt','rp']and break_before in str(n)]
  if len(found)!=1 or str(found[0]).count(break_before)!=1:raise ValueError('Notice title break must match one text span')
  n=found[0];a,b=str(n).split(break_before);last=NavigableString(a);n.replace_with(last)
  br=soup.new_tag('br');last.insert_after(br);br.insert_after(NavigableString(break_before+b))
 def pieces(n):
  if isinstance(n,NavigableString):return [html.escape(str(n))]
  if not isinstance(n,Tag):return ['']
  if n.name=='br':return ['','']
  if n.name=='span'and n.has_attr('data-authored-plain-break'):return ['','']
  if n.name=='ruby':return [str(n)]
  if n.name=='span'and n.has_attr('data-authored-word-gap'):return [str(n)]
  if n.name=='span'and n.has_attr('data-japanese-label-space'):return [str(n)]
  if n.name=='span'and n.has_attr('data-preserved-space'):return [str(n)]
  # Source-bound Old gaps have no text but must survive semantic line splitting.
  # Keep the opt-in separate from underlined answer blanks and Modern output.
  if preserve_historical_word_gaps and n.name=='span'and n.has_attr('data-historical-word-gap'):return [str(n)]
  result=['']
  for child in n.children:
   p=pieces(child);result[-1]+=p[0];result.extend(p[1:])
  if n.name in ['p','div','center','h1','h2','h3','h4']:return ['']+result+['']
  if n.name=='[document]':return result
  attrs=''.join(' '+k+'="'+html.escape(' '.join(v)if isinstance(v,list)else str(v),quote=True)+'"'for k,v in n.attrs.items())
  # An Old answer field can contain only spaces. Its underline is meaningful
  # even though its text projection has no visible characters. Keep this opt-in
  # so Modern and unrelated consumers retain their established emissions.
  blank=n.name=='u' or 'underline' in n.get('style','')
  return ['<'+n.name+attrs+'>'+x+'</'+n.name+'>' if x.strip() or (preserve_underlined_blanks and blank and x) else '' for x in result]
 return [x for x in pieces(soup)if Projection({'html':x}).text.strip()]


def body_nodes_tex(conv,nodes,styles):
 used=[];parts=[]
 for n in nodes:
  plain=Projection({'html':str(n)}).text.strip();matches=[(idx,s)for idx,s in enumerate(styles)if s['text']==plain]
  if len(matches)>1:raise ValueError('Duplicate notice line style')
  if not matches:
   parts.append(conv.value({'html':str(n)},'notice')if getattr(conv,'workbook_group_spans',False)else conv.node(n,'notice'))
   continue
  idx,s=matches[0];used.append(idx)
  raw=n.decode_contents()if isinstance(n,Tag)else str(n)
  if s.get('line_breaks_before'):
   for token in s['line_breaks_before']:
    raw='<br/>'.join(html_lines(raw,token))
  if s.get('label_column'):
   from example_layout import slice_inline
   spec=s['label_column'];label=spec['label'];width=spec['width_em'];gap=spec.get('gap_em',.5)
   text=Projection({'html':raw}).text;start=len(text)-len(text.lstrip())
   if not text[start:].startswith(label) or not 1<=width<=14 or not 0<=gap<width:raise ValueError('Invalid exact notice label column')
   end=start+len(label);value_start=end
   while value_start<len(text) and text[value_start].isspace():value_start+=1
   if value_start==len(text):raise ValueError('Label column requires an existing value')
   labeltex=conv.value({'html':slice_inline(raw,start,end)},'notice')
   value=conv.value({'html':slice_inline(raw,value_start,len(text))},'notice')
   alignment=spec.get('align','left')
   if alignment not in ['left','right']:raise ValueError('Invalid label alignment')
   body=r'\makebox['+str(width-gap)+'em]['+('l'if alignment=='left'else'r')+']{'+labeltex+r'}\hspace{'+str(gap)+'em}'+value
   conv.features.append({'kind':'notice_label_column','label':label,'width_em':width,'gap_em':gap})
  elif s.get('inline_list'):
   from example_layout import slice_inline
   markers=s['inline_list']['markers'];text=Projection({'html':raw}).text
   positions=[text.index(m) if text.count(m)==1 else -1 for m in markers]
   if not markers or positions!=sorted(set(positions)) or text[:positions[0]].strip():raise ValueError('Inline list must cover exact ordered markers')
   parts_inline=[]
   for index,(a,b) in enumerate(zip(positions,positions[1:]+[len(text)])):
    fragment=conv.value({'html':slice_inline(raw,a,b)},'notice')
    parts_inline.append(r'\mbox{'+fragment+'}')
   body=(r'\hskip .8em plus .1em\relax ').join(parts_inline)
  elif s.get('time_columns'):
   # Column boundaries use existing circled labels; all six label/value pairs
   # stay in their accepted row order, with fixed native column alignment.
   pairs=re.findall(r'([①②③④⑤⑥])\s*([0-9]{1,2}:[0-9]{2}～[0-9]{1,2}:[0-9]{2})',plain)
   if [a for a,b in pairs]!=['①','④','②','⑤','③','⑥'] or re.sub(r'\s','',plain)!=''.join(a+b for a,b in pairs):raise ValueError('Time columns require exactly the six unchanged pairs')
   gap=s.get('time_label_gap_em',.3);tracking=s.get('time_letterspace',0);colsep=s.get('time_column_sep_pt',5)
   if not 0<=gap<=1 or not 0<=tracking<=10 or not 0<=colsep<=20:raise ValueError('Invalid time pair spacing')
   def pair(label,value):
    number=conv.text(value)
    if tracking:number=r'{\addfontfeatures{LetterSpace='+str(tracking)+'}'+number+'}'
    return r'\mbox{'+conv.text(label)+r'\hspace{'+str(gap)+'em}'+number+'}'
   rows=[pair(a,b)+' & '+pair(c,d)+r' \\'for (a,b),(c,d)in zip(pairs[::2],pairs[1::2])]
   alignment=s.get('time_columns_align','left')
   if alignment not in ['left','center']:raise ValueError('Invalid time column alignment')
   a='c'if alignment=='center'else'l'
   body=r'\begin{tblr}{width=\linewidth,colspec={X['+a+'] X['+a+r']},colsep='+str(colsep)+r'pt,rowsep=1pt}'+''.join(rows)+r'\end{tblr}'
  elif s.get('label_width_em'):
   label=s['label'];soup=BeautifulSoup(raw,'html.parser')
   first=next((x for x in soup.descendants if isinstance(x,NavigableString)and x.strip()),None)
   if first is None or str(first)!=label:raise ValueError('Notice label must be one complete existing leading node')
   first.replace_with('');value=conv.value({'html':str(soup)},'notice').lstrip()
   labeltex=r'\hfill '.join(conv.text(ch)for ch in label)
   face=r'\NoticeLabelJapanese 'if s.get('label_font_family')=='notice_label'else r'\NoticeBodyJapanese '
   body=r'\makebox['+str(s['label_width_em']-.7)+r'em][s]{{'+face+labeltex+r'}}\hspace{.7em}'+value
  elif s.get('boxed_label'):
   from example_layout import slice_inline
   label=s['boxed_label'];soup=BeautifulSoup(raw,'html.parser')
   first=next((x for x in soup.descendants if isinstance(x,NavigableString)and x.strip()),None)
   if first is not None and not first.find_parent(['ruby','rt','rp']) and str(first).startswith(label):
    # Keep the established unannotated label's exact native typography.
    first.replace_with(str(first)[len(label):]);body=r'{\setlength\fboxsep{1pt}\fbox{'+conv.text(label)+'}}'+conv.value({'html':str(soup)},'notice')
   else:
    text=Projection({'html':raw}).text;start=len(text)-len(text.lstrip())
    if not text[start:].startswith(label):raise ValueError('Boxed notice label must be leading existing text')
    end=start+len(label)
    labeltex=conv.value({'html':slice_inline(raw,start,end)},'notice')
    remainder=(slice_inline(raw,0,start) if start else '')+(slice_inline(raw,end,len(text)) if end<len(text) else '')
    body=r'{\setlength\fboxsep{1pt}\fbox{'+labeltex+'}}'+conv.value({'html':remainder},'notice')
  elif s.get('break_before'):
   chunks=html_lines(raw,s['break_before'])
   if len(chunks)!=2:raise ValueError('Notice continuation break must create exactly two rich lines')
   body=r'\linebreak{}'.join(conv.value({'html':chunk},'notice') for chunk in chunks)
  elif s.get('split_lines'):
   chunks=html_lines(raw);indents=s.get('line_indents_em',[0]*len(chunks))
   if len(indents)!=len(chunks):raise ValueError('Notice line indent count changed')
   body=''.join(r'{\advance\leftskip by '+str(indent)+r'em\relax\hangindent='+str(s.get('hanging_em',0))+r'em\hangafter=1 '+conv.value({'html':chunk},'notice')+r'\par}'for chunk,indent in zip(chunks,indents))
  else:body=conv.value({'html':raw},'notice')
  if s.get('line_breaks_before'):body=body.replace(r'\NoticeLine',r'\linebreak{}')
  if 'numeric_padding_em'in s:
   gap=s['numeric_padding_em']
   if isinstance(gap,bool)or not 0<=gap<=.4 or not re.search(r'[0-9]',plain):raise ValueError('Invalid notice numeric padding')
   # Numeric padding applies only to plain body runs, never TeX dimensions.
   if s.get('label_width_em'):
    if re.search(r'\\(?:fontsize|hspace|scalebox|raisebox|makebox|ruby)\b',value):raise ValueError('Numeric padding requires a plain bound value')
    value=re.sub(r'[0-9]+',lambda m:r'\hspace{'+str(gap)+'em}'+m[0]+r'\hspace{'+str(gap)+'em}',value)
    body=r'\makebox['+str(s['label_width_em']-.7)+r'em][s]{{'+face+labeltex+r'}}\hspace{.7em}'+value
   else:raise ValueError('Numeric padding requires a bound label/value line')
  if s.get('fullwidth_parentheses'):
   if not s.get('label_width_em')or '('not in plain or ')'not in plain:raise ValueError('Parenthesis spacing requires a bound label/value line')
   body=body.replace(r'\AsciiParen{(}',r'\makebox[1em][c]{\AsciiParen{(}}').replace(r'\AsciiParen{)}',r'\makebox[1em][c]{\AsciiParen{)}}')
  if 'marker' in s:
   marker=s['marker']
   if marker!={'character':'▶','kind':'notched_arrowhead'} or not plain.startswith('▶') or body.count('▶')!=1:raise ValueError('Notched marker requires one exact existing leading triangle')
   body=body.replace('▶',r'\NoticeNotchedArrow{}',1)
   conv.features.append({'kind':'notice_marker_presentation','text':plain,'canonical_marker':'▶','presentation':'native_notched_arrowhead'})
  if s.get('bullet_scale'):
   if not plain.startswith('●') or body.count('●')!=1:raise ValueError('Bullet role must select one existing leading circle')
   body=body.replace('●',r'\raisebox{.1em}{\scalebox{'+str(s['bullet_scale'])+r'}{●}}\hspace{.3em}',1)
  bullet_hang=None
  if 'document_bullet' in s:
   if any(k in s for k in ['bullet_scale','hanging_em','hanging_prefix','marker']):raise ValueError('Conflicting document bullet controls')
   from document_bullets import present
   body,bullet_hang=present(conv,plain,body,s['document_bullet'],'notice')
  if s.get('angular_delimiters'):
   if not plain.startswith('〈')or not plain.endswith('〉')or plain.count('〈')!=1 or plain.count('〉')!=1:raise ValueError('Angular role requires one decorative heading pair')
   body=body.replace('〈',r'\textless{}').replace('〉',r'\textgreater{}')
  if s.get('font_family')=='heading':body=r'{\sffamily\gtfamily '+body+'}'
  if s.get('font_family')=='notice_body':body=r'{\NoticeBodyJapanese '+body+'}'
  if s.get('font_family')=='notice_heading':body=r'{\NoticeHeadingJapanese '+body+'}'
  if s.get('font_family')=='notice_label':body=r'{\NoticeLabelJapanese '+body+'}'
  if s.get('period_spacing'):
   if not re.fullmatch(r'期間:[0-9]+月[0-9]+日~[0-9]+月[0-9]+日',plain):raise ValueError('Period spacing requires the exact existing date interval')
   body=body.replace(':',r'\hspace{.45em}:\hspace{.5em}',1).replace(r'\textasciitilde{}',r'\hspace{.2em}\textasciitilde{}\hspace{.2em}')
  if s.get('bold'):body=r'{\bfseries '+body+'}'
  if s.get('underline'):body=r'\underLine{'+body+'}'
  if 'font_pt'in s:body=r'{\fontsize{'+str(s['font_pt'])+'}{'+str(s.get('baseline_pt',s['font_pt']*1.4))+r'}\selectfont '+body+'}'
  align={'left':r'\raggedright ','center':r'\centering ','right':r'\raggedleft '}[s.get('align','left')]
  if 'offset_x_pt'in s:
   offset=s['offset_x_pt']
   if isinstance(offset,bool)or not isinstance(offset,(int,float))or not -12<=offset<=12:raise ValueError('Invalid notice line offset')
   align+=r'\advance\leftskip by '+str(offset)+r'pt\advance\rightskip by '+str(-offset)+r'pt '
  indent=s.get('indent_em',0)
  measured=''
  if s.get('indent_like_prefix'):
   measured=r'\settowidth\NoticeLineIndent{'+conv.text(s['indent_like_prefix'])+r'}\advance\leftskip by \NoticeLineIndent\relax '
  hanging=r'\hangindent='+str(s.get('hanging_em',0))+r'em\hangafter=1 '
  if s.get('label_column'):hanging=r'\hangindent='+str(s['label_column']['width_em'])+r'em\hangafter=1 '
  if bullet_hang is not None:hanging=r'\hangindent='+str(bullet_hang)+r'em\hangafter=1 '
  if 'hanging_prefix' in s:
   prefix=s['hanging_prefix']
   if not prefix or not plain.startswith(prefix) or len(prefix)>4:raise ValueError('Hanging prefix must match the existing leading label')
   if 'hanging_em' in s:raise ValueError('Choose measured prefix or explicit hanging, not both')
   following=plain[len(prefix):len(prefix)+1]
   if not following:raise ValueError('Hanging prefix needs following text')
   # LuaTeX-ja removes a punctuation boundary at a box end. Measure with the
   # actual following character, then subtract that character's own advance.
   # Measuring the isolated dot loses .25em in the sports notice's JFM.
   hanging=(r'\settowidth\NoticeLineIndent{'+conv.text(prefix+following)+r'}'
            r'\settowidth\NoticePrefixTail{'+conv.text(following)+r'}'
            r'\addtolength\NoticeLineIndent{-\NoticePrefixTail}'
            r'\hangindent=\NoticeLineIndent\hangafter=1 ')
  body=r'{'+align+r'\advance\leftskip by '+str(indent)+r'em\relax '+measured+hanging+r'\noindent '+(r'\hspace*{'+str(s['first_indent_em'])+'em}'if s.get('first_indent_em')else'')+body+r'\par}'
  if s.get('box'):
   width=s.get('width_fraction',1);placement=r'\noindent\hspace*{'+str(s['box_indent_em'])+'em}'if 'box_indent_em'in s else r'\centering '
   padding=s.get('box_padding_pt',3)
   body='{'+placement+r'\begin{minipage}{'+str(width)+r'\linewidth}\begin{NoticeFrame}[nobreak=true,skipabove=0pt,skipbelow=0pt,innertopmargin='+str(padding)+'pt,innerbottommargin='+str(padding)+'pt]'+body+r'\end{NoticeFrame}\end{minipage}\par}'
  parts.append(r'\par\addvspace{'+str(s.get('before_pt',0))+'pt}'+body+r'\vspace{'+str(s.get('after_pt',0))+'pt}')
 if sorted(used)!=list(range(len(styles))):raise ValueError('Notice line styles must select each complete node once')
 return ''.join(parts)
