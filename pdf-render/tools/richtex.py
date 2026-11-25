"""Conservative rich-HTML to LuaTeX-ja translation with explicit unsupported failures."""
import re, math, base64, hashlib, copy, html
from pathlib import Path
from wakachi import bind_groups,short_group
from bs4 import BeautifulSoup, NavigableString, Tag
from model import Projection
from numeral_roles import render as numeric_text, token as numeric_token, literal_digits
ESC={'►':r'{\SymbolFont\ltjalchar"25BA\relax}','\\':r'\textbackslash{}','{':r'\{','}':r'\}','#':r'\#','$':r'\$','%':r'\%','&':r'\&','_':r'\_','^':r'\textasciicircum{}','~':r'\textasciitilde{}'}
ESC['⚫']=r'{\SymbolFont\ltjalchar"26AB\relax}'
# Canonical symbols and retained Chinese administrative characters must remain
# native Unicode. These finite glyph routes are not a text substitution.
for _char in '✙➀➁':ESC[_char]=r'{\SymbolFont\ltjalchar"'+format(ord(_char),'X')+r'\relax}'
for _char in '试题':ESC[_char]=r'{\RetainedChineseFace\ltjalchar"'+format(ord(_char),'X')+r'\relax}'
# Preserve ASCII characters and select their glyph at native emission time.
# This is deliberately not a () -> fullwidth text normalization.
ESC['(']=r'\AsciiParen{(}'
ESC[')']=r'\AsciiParen{)}'
OPEN_PAREN_TEX = r'(?:（|\(|\\AsciiParen\{\(\})'
CLOSE_PAREN_TEX = r'(?:）|\)|\\AsciiParen\{\)\})'
HISTORICAL_NUMBERED_PAREN = re.compile(r'(?:（[ \u3000\t]{0,3}[①-⑳A-Za-zＡ-Ｚａ-ｚ][ \u3000\t]{0,3}）|\([ \u3000\t]{0,3}[①-⑳A-Za-zＡ-Ｚａ-ｚ][ \u3000\t]{0,3}\))')

def literal_parens(tex):
 return tex.replace(r'\AsciiParen{(}','(').replace(r'\AsciiParen{)}',')')
def escape(s):return ''.join(ESC.get(c,c) for c in s)

def bounded_word(text):
 # Existing space/typed boundaries own membership. Quotes attach to their
 # short word group; they do not turn the whole quoted sentence into a box.
 return bool(re.fullmatch(r'[「『（]?[ぁ-んァ-ヶー一-龥々。、？！]{1,12}[」』）]?',text))

def text_tex(s,inline=True):
 s=s.replace('\r\n','\n').replace('\r','\n')
 # Keep ordinary source spaces; soft HTML line endings use natural TeX wrapping.
 s=re.sub(r'[\t\n]+',' ',s) if inline else s
 tokens=re.split(r'((?<![A-Za-z0-9])_+(?![A-Za-z0-9])|＿+|★|[（(][ \u3000\t]+[）)])',s)
 out=[]
 for t in tokens:
  if not t:continue
  if re.fullmatch(r'_+|＿+',t):out.append(r'\Slot{}')
  elif t=='★':out.append(r'\StarSlot{}' if len(re.findall(r'_+|＿+',s))>=3 else '★')
  elif re.fullmatch(r'[（(][ \u3000\t]+[）)]',t):out.append(r'\BlankParens{}')
  else:out.append(escape(t))
 return ''.join(out)
def remove_number(value, prefix_binding=None):
 if prefix_binding:
  from model import digest
  prefix=prefix_binding['prefix']
  if not re.fullmatch(r'[0-9０-９]{1,3}',prefix) or digest(value)!=prefix_binding['stem_sha256']:
   raise ValueError('Stale exact question prefix binding')
  if not Projection(value).text.startswith(prefix):raise ValueError('Question prefix is not at the field start')
  if isinstance(value,str):return prefix,value[len(prefix):]
  soup=BeautifulSoup(value['html'],'html.parser')
  first=next(n for n in soup.descendants if isinstance(n,NavigableString) and n.strip() and n.parent.name not in ['rt','rp'])
  if not str(first).startswith(prefix):raise ValueError('Question prefix crosses markup')
  first.replace_with(str(first)[len(prefix):])
  return prefix,{'html':str(soup)}
 pattern=r'^\s*(?:(?:[（(【\[]\s*)?([0-9０-９]{1,3})\s*[）)】\].．:：]\s*|([0-9０-９]{1,3})(?:\s+|$))'
 if isinstance(value,str):
  m=re.match(pattern,value)
  return ((m.group(1)or m.group(2)),value[m.end():]) if m else (None,value)
 # Ruby can end the first text node after a quantity (e.g. 10<ruby>年...).
 # A text-node end is not the end of the question's complete base text.
 if not re.match(pattern,Projection(value).text):return None,value
 soup=BeautifulSoup(value['html'],'html.parser')
 for n in soup.descendants:
  if isinstance(n,NavigableString) and n.strip() and n.parent.name not in ['rt','rp']:
   m=re.match(pattern,str(n))
   if m:
    number=m.group(1)or m.group(2);n.replace_with(str(n)[m.end():]);return number,{'html':str(soup)}
   break
 return None,value

def heading_word_glue(body):
    """Keep the JFM cell width in a line and discard its space at a wrap."""
    if '　' not in body:
        return body
    depth = 0

    def convert(match):
        nonlocal depth
        token = match[0]
        if token == '{':
            depth += 1
        elif token == '}':
            depth -= 1
        elif depth == 0 and token.startswith('　'):
            return rf'\hskip {len(token)}\zw\relax '
        return token

    # Braced arguments include ruled samples, ruby and protected choice groups.
    return re.sub(r'\\[{}\\]|[{}]|　+', convert, body)


def unbox_adjacent_commas(tex):
    """Let LuaTeX-ja space a word-final comma against the following inline text."""
    from renditions import balanced

    # Kinsoku keeps the comma with the preceding word. Outside its box the JFM
    # can choose the advance for kana, kanji, numerals or a bracket.
    following = re.compile(
        r'(?:\\allowbreak\{\})?(?:[\w「『（【」』）】]|\\(?:mbox|ruby|underLine|makebox)\b)'
    )
    edits = []
    for box in re.finditer(r'\\mbox\{', tex):
        word, end = balanced(tex, box.end() - 1)
        if word.endswith('、') and following.match(tex, end):
            if word == '、':
                edits.append((box.start(), end, '、'))
            else:
                edits.append((end - 2, end, '}、'))

    parts = []
    start = 0
    for at, end, replacement in sorted(edits):
        parts.extend((tex[start:at], replacement))
        start = end
    parts.append(tex[start:])
    return ''.join(parts)


def bind_ruby_word_groups(soup):
 """Keep bounded existing Japanese space groups across inline ruby markup."""
 def visit(parent):
  original=list(parent.children)
  for child in original:
   if isinstance(child,Tag) and child.name not in ['ruby','rt','rp'] and not child.has_attr('data-bounded-word'):
    visit(child)
  parts=[];word=[]
  def flush():
   if not word:return
   raw=''.join(str(x) if isinstance(x,Tag) else html.escape(str(x)) for x in word)
   text=Projection({'html':raw}).text
   if any(isinstance(x,Tag) and x.name=='ruby' for x in word) and bounded_word(text):
    group=soup.new_tag('span');group['data-bounded-word']='ruby-space-group'
    for x in word:group.append(x)
    parts.append(group)
   else:parts.extend(word)
   word.clear()
  for child in original:
   if isinstance(child,NavigableString):
    for piece in re.split(r'([ \u3000\t\r\n]+|[、。？！][」』）]?)',str(child)):
     if not piece:continue
     if piece.isspace():flush();parts.append(NavigableString(piece))
     elif re.fullmatch(r'[、。？！][」』）]?',piece):word.append(NavigableString(piece));flush()
     else:word.append(NavigableString(piece))
   elif child.name=='ruby':word.append(child)
   else:flush();parts.append(child)
  flush();parent.clear()
  for child in parts:parent.append(child)
 visit(soup)
 # Preserve text-node context for four-slot STAR recognition and blank padding.
 soup.smooth()
 return soup

class RichTeX:
 def __init__(self,assets,source_base=None,word_space_em=0):self.assets=Path(assets);self.source_base=source_base;self.features=[];self.table_styles={};self.table_index=0;self.word_space_em=word_space_em
 def question(self,value,target,associated=False):
  gap=getattr(self,'question_table_before_pt',None)
  if gap is not None:
   if isinstance(gap,bool) or not isinstance(gap,(int,float)) or not 0<=gap<=30:raise ValueError('Invalid question-table clearance')
   from question_displays import prepare
   value=prepare(value,target,associated)
  return self.value(value)
 def text(self,value):
  # Slot padding owns its gap. Literal word spaces must not add a second gap,
  # and splitting at spaces must not destroy STAR's four-slot context.
  if not value.strip() and '\n' in value:return ''
  pattern=r'((?<![A-Za-z0-9])_+(?![A-Za-z0-9])|＿+|★|[（(][ \u3000\t]+[）)])'
  if getattr(self,'source_target_markers',False):
   # Old source quantities may touch a blank (2____). Consume the entire run;
   # rejecting its first underscore used to split it into two answer slots.
   pattern=r'((?<![A-Za-z_])_+(?![A-Za-z_])|＿+|★|[（(][ \u3000\t]+[）)])'
  numbered=HISTORICAL_NUMBERED_PAREN if getattr(self,'source_target_markers',False) else None
  if numbered:pattern=pattern[:-1]+'|'+numbered.pattern+')'
  pieces=re.split(pattern,value);star=len(re.findall(r'_+|＿+',value))>=3
  out=[]
  for k,piece in enumerate(pieces):
   if k%2:
    if numbered and numbered.fullmatch(piece):
     out.append(r'\mbox{'+escape(piece[0])+self.text(piece[1:-1])+escape(piece[-1])+'}')
     self.features.append({'kind':'historical_numbered_parenthesis','text':piece,'basis':'Existing short matched parentheses and single circled or Latin-letter target, kept on one line'})
    else:out.append(r'\BlankParens{}' if re.fullmatch(r'[（(][ \u3000\t]+[）)]',piece) else r'\StarSlot{}' if piece=='★' and star else '★' if piece=='★' else r'\Slot{}')
   else:
    if k and not (numbered and numbered.fullmatch(pieces[k-1])):piece=piece.lstrip(' ')
    if k+1<len(pieces) and not (numbered and numbered.fullmatch(pieces[k+1])):piece=piece.rstrip(' ')
    def content(x):
     identifiers=getattr(self,'literal_identifiers',set())
     render=lambda text:numeric_text(text,getattr(self,'numeric_role',None),text_tex)
     if not identifiers or '-'not in x:return render(x)
     pattern=r'(?<![A-Za-z0-9])(?:'+'|'.join(re.escape(t)for t in sorted(identifiers,key=len,reverse=True))+r')(?![A-Za-z0-9])'
     cursor=0;parts=[]
     for match in re.finditer(pattern,x):
      parts.append(render(x[cursor:match.start()]));token=match[0]
      pieces=re.split(r'([①-⑳])',token)
      parts.append(r'\mbox{'+''.join(render(p) if re.fullmatch(r'[①-⑳]',p) else r'{\ContactLatin '+escape(p)+'}' for p in pieces if p)+'}')
      self.features.append({'kind':'literal_identifier','text':token,'font_role':'contact_latin'});cursor=match.end()
     parts.append(render(x[cursor:]));return ''.join(parts)
    if not self.word_space_em:out.append(content(piece));continue
    chunks=re.split(r'([ \u3000]+|(?<=[、。？！])(?![」』）]))',piece)
    def word(x,internal):
     if x and x.isspace() and '\n'not in x:
      # Use discardable glue for lexical gaps. A fixed slot or worked table
      # owns its own padding and still receives the original source character.
      if (x=='　' and internal and getattr(self,'modern_wakachi',False)
          and getattr(self,'keep_spaced_words',False) and not getattr(self,'passage_word_flow',False)):
       return r'\hskip 1\zw\relax '
      if '\u3000'in x and getattr(self,'passage_word_flow',False):
       # Preserve in-line advance, discarding separators at wrapped line starts.
       width=x.count('\u3000')+sum(c!='\u3000'for c in x)*self.word_space_em
       self.features.append({'kind':'discardable_fullwidth_word_gap','width_em':width})
       return r'\hskip '+str(width)+r'em\relax '
      return content(x) if '\u3000' in x else r'\hskip '+str(self.word_space_em)+r'em\relax '
     t=content(x)
     if getattr(self,'keep_spaced_words',False) and (bounded_word(x) or
             getattr(self,'modern_wakachi',False) and short_group(x)):
      self.features.append({'kind':'bounded_spaced_word','text':x,'basis':'Existing text-node word group, at most 12 characters; no inserted source line break'})
      return r'\mbox{'+t+'}'+(r'\allowbreak{}' if getattr(self,'passage_word_flow',False) and x[-1] in '、。？！' else '')
     return t
    out.append(''.join(word(x,0 < j < len(chunks)-1 and chunks[j-1] and chunks[j+1]) for j,x in enumerate(chunks)))
  return ''.join(out)
 def pedagogical_groups(self,node,context):
  """Prefer existing space boundaries inside a tested N5 phrase, preserving ruby."""
  import html
  groups=[];current=[]
  def flush():
   if current:groups.append(('word',''.join(current)));current.clear()
  for child in node.children:
   if isinstance(child,NavigableString):
    for piece in re.split(r'([ \u3000]+)',str(child)):
     if piece and re.fullmatch(r'[ \u3000]+',piece):flush();groups.append(('space',piece))
     else:current.append(html.escape(piece))
   else:current.append(str(child))
  flush();out=[]
  for kind,raw in groups:
   if kind=='space':out.append(self.text(raw));continue
   text=Projection({'html':raw}).text;tex=self.value({'html':raw},context)
   out.append(r'\mbox{'+tex+'}' if 1<=len(text)<=12 and '\n'not in text else tex)
  self.features.append({'kind':'pedagogical_phrase_breaks','text':Projection({'html':str(node)}).text,'basis':'Existing space groups only; maximum 12 base characters; ruby nodes remain intact'})
  return ''.join(out)
 def value(self,value,context='body'):
  if context!='heading' and getattr(self,'workbook_font_spans',None):
   from workbook_typography import prepare as prepare_workbook_fonts
   value=prepare_workbook_fonts(value,self.workbook_font_spans)
  if context=='heading' and getattr(self,'approved_administrative_numerals',False) and isinstance(value,str):
   value={'html':html.escape(value)}
  from label_separators import prepare as label_separators
  value,separators=label_separators(value,presentation=False)
  if separators:self.features.append({'kind':'japanese_label_separators','context':context,'separators':separators,'canonical_changed':False})
  if getattr(self,'answer_blank_roles',None) is not None:
   from answer_blanks import prepare as prepare_blanks
   role='heading' if context=='heading' else 'example' if getattr(self,'in_example',False) else 'body'
   settings={**getattr(self,'answer_blank_base',{}),**self.answer_blank_roles.get(role,{})}
   value,records=prepare_blanks(value,role,settings,historical_underline_samples=getattr(self,'source_target_markers',False))
   self.features.extend(records)
  spaced_flow=self.word_space_em and (getattr(self,'passage_word_flow',False) or getattr(self,'keep_spaced_words',False) or getattr(self,'in_example',False))
  if spaced_flow and context in ['body','email','cell','option','example']:
   from passage_spacing import prepare
   value,offsets=prepare(value,getattr(self,'punctuation_after_em',0))
   if offsets:self.features.append({'kind':'passage_punctuation_spacing','context':context,'punctuation_after_em':self.punctuation_after_em,'projection_offsets':offsets,'word_space_em':self.word_space_em})
  policy=getattr(self,'word_space_policy','preserve')
  from word_spacing import POLICIES, continuous_japanese
  if policy not in POLICIES:raise ValueError('Unknown word-space presentation policy')
  if policy=='continuous_japanese' and context in ['body','option','email']:
   protected=[s['text']for s in (getattr(self,'section_style',None)or{}).get('line_styles',[])]
   value,removed=continuous_japanese(value,protected)
   if removed:self.features.append({'kind':'continuous_japanese_spacing','context':context,'removed_single_spaces':len(removed),'boundaries':removed})
  if isinstance(value,str):
   if context in ['heading','option']:
    tex=self.text(value)
    return re.sub(r'\\Slot\{\}\s*★\s*\\Slot\{\}',lambda m:r'\StarSlot{}',tex) if context=='heading'else tex
   if context=='email':
    pieces=re.split(r'(\n+)',value);return ''.join((r'\Para ' if len(x)>1 else r'\EmailLine ') if x.startswith('\n') else self.text(x) for x in pieces)
   return r'\Para '.join(self.text(x) for x in re.split(r'\n+',value) if x.strip())
  soup=BeautifulSoup(value['html'],'html.parser')
  if soup.select('span[data-inline-omission-after]'):
   from paragraph_layout import join_inline_omissions
   join_inline_omissions(soup)
  if self.word_space_em and getattr(self,'keep_spaced_words',False):
   if getattr(self,'modern_wakachi',False):bind_groups(soup,web=False)
   else:bind_ruby_word_groups(soup)
  # Duplicate serialized example options are handled upstream only with exact equality.
  s=''.join(self.node(n,context) for n in soup.children)
  s=re.sub(r'(?:\s*\\Para\s*){2,}',lambda m:r'\Para ',s)
  if context=='notice':s=re.sub(r'(?:\s*\\NoticeLine\s*){2,}',lambda m:r'\Para ',s)
  if context=='email':s=re.sub(r'(?:\s*\\EmailLine\s*){2,}',lambda m:r'\Para ',s)
  if context=='heading':s=re.sub(r'\\Slot\{\}\s*★\s*\\Slot\{\}',lambda m:r'\StarSlot{}',s)
  return s.strip()
 def heading(self,value):
  soup=BeautifulSoup(value if isinstance(value,str) else value['html'],'html.parser')
  # Serialized scan/retype line endings are soft in an administrative heading.
  # Explicit cloze annotation converts plain newlines to <br>; retaining those
  # breaks after native boxes widen the line can strand a two-character line.
  for br in soup.find_all('br'):br.replace_with(' ')
  for br in soup.select('span[data-authored-plain-break]'):br.replace_with(' ')
  if not getattr(self,'source_target_markers',False):
   from instruction_selectors import prepare as prepare_selectors
   prepare_selectors(soup)
  boundary=getattr(self,'heading_selector_boundary',False)
  if not isinstance(boundary,bool):raise ValueError('Heading selector boundary must be boolean')
  suffix_break=getattr(self,'heading_selector_suffix_break',False)
  if type(suffix_break)is not bool or (suffix_break and not getattr(self,'source_target_markers',False)):
   raise ValueError('Invalid Old heading selector suffix break')
  from instruction_spacing import prepare as separate_instructions
  sentence_boundaries=separate_instructions(soup)
  if sentence_boundaries:self.features.append({'kind':'instruction_sentence_boundary','projection_offsets':sentence_boundaries,'gap_em':.5,'canonical_changed':False})
  if boundary:
   # A bounded administrative selector role, never general punctuation spacing.
   for node in list(soup.descendants):
    if not isinstance(node,NavigableString) or node.parent.name in ['rt','rp']:continue
    raw=str(node);changed=re.sub(r'。(?=[1１]\s*・\s*[2２]\s*・\s*[3３]\s*・\s*[4４][ \u3000]*から)', '。 ',raw)
    if changed!=raw:
     node.replace_with(changed);self.features.append({'kind':'heading_selector_boundary','before':raw,'after':changed,'scope':'exact four-choice selector after sentence punctuation'})
  if getattr(self,'keep_spaced_words',False) or boundary or getattr(self,'source_target_markers',False):
   # A beginner instruction's four-choice selector is one bounded group.
   # Keep its last numeral off a new line without freezing the sentence.
   for node in list(soup.descendants):
    if not isinstance(node,NavigableString)or node.parent.name in ['rt','rp'] or node.parent.has_attr('data-bounded-word') or node.parent.has_attr('data-choice-selector'):continue
    match=re.search(r'[1１]\s*・\s*[2２]\s*・\s*[3３]\s*・\s*[4４][ \u3000]*から',str(node))
    selector_kind='heading-choice-selector'
    if not match and getattr(self,'source_target_markers',False):
     match=re.search(r'(?<![0-9０-９])[1１][ \u3000]*[2２][ \u3000]*[3３][ \u3000]*[4４][ \u3000]*から',str(node))
     selector_kind='heading-undotted-choice-selector'
    if match:
     raw=str(node);span=soup.new_tag('span');span['data-bounded-word']=selector_kind;span.string=match[0]
     node.replace_with(NavigableString(raw[:match.start()]),span,NavigableString(raw[match.end():]))
  def finish(body):
   # Paragraph wrappers around an HTML instruction are its container, not a
   # request to detach the extracted problem label from the first line.
   # Preserve internal paragraph boundaries and all native inline markup.
   body=re.sub(r'^(?:\\Para\s*)+|(?:\s*\\Para)+$', '',body)
   gap=getattr(self,'heading_choice_gap_em',0)
   if gap or getattr(self,'source_target_markers',False):
    separator=r'\hspace{'+str(gap/2)+r'em}・\hspace{'+str(gap/2)+'em}' if gap else '・'
    # Unbounded selectors (e.g. followed by の) retain their instruction face
    # and receive only the calibrated Old horizontal digit width. Bounded
    # selectors keep their separately chosen face through HistoricalSelectorDigit.
    def selector_digits(match):
     digits=match.groups()
     if getattr(self,'source_target_markers',False):
      digits=[r'\HistoricalInstructionDigit{'+d+'}' for d in digits]
     return separator.join(digits)
    body=re.sub(r'([1１])\s*・\s*([2２])\s*・\s*([3３])\s*・\s*([4４])',selector_digits,body)
   body=re.sub(r'選びなさい。|えらびなさい。|えらんで|ください。|いちばん|最もよい|あります|答えは|いい|から',lambda m:r'\mbox{'+m[0]+'}',body)
   body=re.sub(r'(?<![０-９])([１-４])(?![０-９])',lambda m:r'\HeadingChoiceNumber{'+m[1]+'}',body)
   body=re.sub(r'(?<![0-9])((?:4|\\HeadingChoiceNumber\{４\}))(?=\\mbox\{から\})',lambda m:m[1]+r'\hspace{.3em}',body)
   # Keep the selector's final numeral with its short suffix, preserving the
   # existing ASCII/fullwidth spacing and role-specific numeral rendering.
   body=re.sub(r'(?<![0-9])(?:4|\\HeadingChoiceNumber\{４\})(?:[ \u3000]|\\hskip [0-9.]+em\\relax |\\hspace\{[0-9.]+em\})*\\mbox\{(?:から|\\mbox\{から\})\}',lambda m:r'\mbox{'+m[0]+'}',body)
   return body.replace(r'\underLine{★}',r'\StarSlot{}').replace('★',r'\StarSlot{}')
  for n in soup.descendants:
   if not isinstance(n,NavigableString) or not n.strip() or n.parent.name in ['rt','rp']:continue
   numeral=r'(?:[0-9０-９]{1,2}|[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ])' if getattr(self,'source_target_markers',False) else r'[0-9０-９]{1,2}'
   match=re.match(r'^\s*(問題|もんだい)\s*('+numeral+r')[.:：．]?\s*',str(n))
   if not match:break
   number=text_tex(match[2])
   if getattr(self,'approved_administrative_numerals',False):
    number=r'{\AdministrativeNumerals '+match[2].translate(str.maketrans('０１２３４５６７８９','0123456789'))+'}'
   label=text_tex(match[1])+r'\hspace{.25em}'+number
   n.replace_with(str(n)[match.end():])
   body=self.value({'html':str(soup)},'heading')
   return r'\HeadingLabel{'+label+'}'+finish(body)
  # A prefixed heading (e.g. 文法 問題1) still uses instruction wrapping.
  return finish(self.value({'html':str(soup)},'heading'))
 def node(self,n,context):
  if isinstance(n,NavigableString):
   raw=str(n)
   if context=='heading' and getattr(self,'approved_administrative_numerals',False):
    return ''.join(r'{\AdministrativeNumerals '+p.translate(str.maketrans('０１２３４５６７８９','0123456789'))+'}' if re.fullmatch(r'[0-9０-９]+',p) else self.text(p) for p in re.split(r'([0-9０-９]+)',raw))
   if context=='email'and '\n'in raw and raw.strip():
    return ''.join((r'\Para 'if len(x)>1 else r'\EmailLine ')if x.startswith('\n')else self.text(x)for x in re.split(r'(\n+)',raw))
   return self.text(raw)
  if not isinstance(n,Tag):return ''
  tag=n.name
  if tag=='span' and n.has_attr('data-wakachi-wide-gap'):
   return r'\hskip 1em\relax ' if getattr(self,'passage_word_flow',False) else r'\hskip 1\zw\relax '
  if tag=='span' and n.has_attr('data-workbook-font'):
   from workbook_typography import macro
   name=macro(n['data-workbook-font'])
   previous=getattr(self,'numeric_role',None);self.numeric_role=None
   try:body=''.join(self.node(x,context) for x in n.children)
   finally:self.numeric_role=previous
   self.features.append({'kind':'approved_workbook_font','font_id':n['data-workbook-font'],'text':Projection({'html':str(n)}).text})
   return '{\\'+name+'Latin\\'+name+'Japanese\\mdseries '+body+'}'
  if tag=='span' and n.has_attr('data-choice-selector'):
   if context!='heading' or n.attrs!={'data-choice-selector':'four'}:raise ValueError('Instruction selector used outside its role')
   from instruction_selectors import tex as selector_tex
   return selector_tex(self,n)
  if tag=='span' and n.has_attr('data-japanese-label-colon'):
   if set(n.attrs)!={'data-japanese-label-colon'} or n.get('data-japanese-label-colon') not in ('definition','group','metadata','label') or n.get_text() not in (':','：') or n.find():raise ValueError('Invalid Japanese label separator')
   return r'\NoteDefinitionColon{}'
  if tag=='span' and n.has_attr('data-japanese-label-space'):
   if n.attrs!={'data-japanese-label-space':'true'} or n.find() or not re.fullmatch(r'[ \u3000]+',n.get_text()):raise ValueError('Invalid Japanese label whitespace')
   return ''
  if tag=='span' and n.has_attr('data-note-definition-colon'):
   if n.attrs!={'data-note-definition-colon':'true'} or n.get_text()!='：' or n.find():raise ValueError('Invalid prepared note definition separator')
   return r'\NoteDefinitionColon{}'
  if n.has_attr('data-historical-frame-paragraph'):
   from historical_document_frame import render_paragraph
   return render_paragraph(self,n,context)
  if tag=='p' and n.has_attr('data-historical-inline-body'):
   if not getattr(self,'source_target_markers',False) or n.attrs!={'data-historical-inline-body':'continued-paragraph'} or context!='body':raise ValueError('Invalid historical inline body paragraph')
   body=''.join(self.node(x,context) for x in n.children)
   inset=getattr(self,'historical_passage_left_inset_em',0)
   if type(inset)not in [int,float]or not 0<=inset<=4:raise ValueError('Invalid historical inline paragraph inset')
   return r'\Para {\leftskip='+str(1+inset)+r'em\relax\parindent=1em\indent '+body+r'\par}\Para '
  if getattr(self,'source_target_markers',False) or any(k.startswith('data-historical-')for k in n.attrs):
   from historical_nodes import render as render_historical_node
   native=render_historical_node(self,n,context)
   if native is not None:return native
  if n.has_attr('data-instruction-boundary'):
   if n.contents or n['data-instruction-boundary']!='sentence':raise ValueError('Invalid instruction boundary')
   return r'\hskip .5em plus .15em minus .1em\relax '
  if n.has_attr('data-cloze-panel'):
   from cloze_panels import render as render_cloze_panel
   return render_cloze_panel(self,n,context)
  if n.has_attr('data-canonical-paragraph-indent'):
   if n['data-canonical-paragraph-indent']!='one-em' or n.get_text()!='　' or n.find():raise ValueError('Invalid canonical paragraph indent marker')
   self.features.append({'kind':'canonical_paragraph_indent_once','context':context,'preserved_character':'U+3000'})
   return r'\noindent '+self.text('　')
  if n.has_attr('data-email-paragraph-padding'):
   if n['data-email-paragraph-padding']!='zero' or n.get_text()!='　' or n.find():raise ValueError('Invalid email paragraph padding')
   self.features.append({'kind':'email_padding_consumer','canonical_character':'U+3000','first_line_indent_em':0})
   return r'\noindent '
  if n.has_attr('data-notice-fields'):
   from notice_fields import render
   return render(self,n,self.notice_fields)
  if n.has_attr('data-embedded-document'):
   from embedded_documents import render
   return render(self,n,self.embedded_document_binding,self.memo_defaults)
  if n.has_attr('data-fullwidth-bracket'):
   if n.string not in ('「','」'):raise ValueError('Invalid fullwidth corner bracket')
   return r'{\addjfontfeatures{RawFeature={-palt}}'+str(n.string)+'}'
  if n.has_attr('data-inline-gap-em'):
   gap=float(n['data-inline-gap-em'])
   if n.contents or not 0<gap<=3:raise ValueError('Invalid measured inline gap')
   self.features.append({'kind':'measured_inline_gap','width_em':gap})
   return r'\hspace{'+str(gap)+'em}'
  if tag=='span'and n.has_attr('data-authored-plain-break'):
   if n.get_text()!='\n' or n.find():raise ValueError('Invalid preserved plain line break')
   return ' 'if context in ['option','heading']else r'\EmailLine 'if context=='email'else r'\Para '
  if tag in ['rt','rp','script','style']:return ''
  if tag=='span' and re.search(r'(?:^|;)\s*(?:-webkit-)?text-emphasis(?:-style|-position)?\s*:',n.get('style','')):
   from text_emphasis import render
   return render(self,n)
  if tag=='ruby':
   rts=n.find_all('rt',recursive=False);assert len(rts)==1,'Unsupported multi-rt ruby'
   base=''.join(self.node(x,context) for x in n.children if not isinstance(x,Tag)or x.name not in ['rt','rp'])
   reading=text_tex(rts[0].get_text());self.features.append({'kind':'ruby','origin':n.get('data-rubi-origin','editorial'),'id':n.get('data-rubi-id'),'base':Projection({'html':str(n)}).text,'reading':rts[0].get_text()})
   return r'\ruby{'+base+'}{'+reading+'}'
  if tag=='br':
   if n.has_attr('data-vertical-soft-break'):
    if n['data-vertical-soft-break']!='true' or not getattr(self,'active_vertical_flow',False) or n.contents:
     raise ValueError('Soft vertical break used outside its bound body')
    self.features.append({'kind':'vertical_joined_line_wrap','basis':'exact authored HTML break index'})
    return ''
   # HTML serializers can leave children inside a void br; never discard them.
   return (r'\NoticeLine ' if context=='notice' else r'\EmailLine ' if context=='email' else r'\Para ' if context not in ['heading','option'] else r'\linebreak[2] ')+''.join(self.node(x,context) for x in n.children)
  if tag=='hr':return r'\par\smallskip\hrule\smallskip '
  if tag=='table' and n.has_attr('data-native-chart'):
   from historical_figures import pies
   return pies(n,self)
  if tag=='table':return self.table(n,context)
  if tag=='img':
   src=n.get('src','');assert src.startswith('data:image/'),'External asset needs explicit registered resolver'
   header,data=src.split(',',1);b=base64.b64decode(data);suffix='png' if 'png' in header else 'jpg';p=self.assets/(hashlib.sha256(b).hexdigest()+'.'+suffix);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
   selected=getattr(self,'embedded_image_styles',{}).get(hashlib.sha256(b).hexdigest())
   if getattr(self,'source_target_markers',False) and getattr(self,'historical_artworks',{}):
    from historical_artwork import render as render_old_artwork
    native=render_old_artwork(self,hashlib.sha256(b).hexdigest(),selected)
    if native is not None:return native
   if getattr(self,'source_target_markers',False) and getattr(self,'historical_native_diagrams',{}):
    from historical_diagrams import render as render_native_old_diagram
    native=render_native_old_diagram(self,hashlib.sha256(b).hexdigest(),selected)
    if native is not None:return native
   if getattr(self,'source_target_markers',False) and getattr(self,'historical_source_pixels',{}):
    from historical_source_pixels import render as render_source_pixels
    replacement=render_source_pixels(self,hashlib.sha256(b).hexdigest(),selected)
    if replacement is not None:return replacement
   if selected:
    from embedded_images import render
    self.features.append({'kind':'embedded_image','sha256':hashlib.sha256(b).hexdigest(),'alt':n.get('alt'),'path':str(p),'presentation':selected})
    return render(p,selected)
   self.features.append({'kind':'glyph_asset','sha256':hashlib.sha256(b).hexdigest(),'alt':n.get('alt'),'path':str(p),'height_em':1.05,'basis':'unselected legacy glyph fallback'})
   return r'\raisebox{-.12em}{\includegraphics[height=1.05em]{'+p.as_posix()+'}}'
  if tag not in ['u','s','del','b','strong','em','i','p','div','span','center','h1','h2','h3','h4','ul','ol','li','sup','sub','a','small','font','section','blockquote']:
   raise ValueError('Unsupported meaningful HTML tag: '+tag)
  if tag=='span'and n.has_attr('data-cloze-label'):
   label=n['data-cloze-label']
   from inline_layout import cloze_label
   if cloze_label(n.get_text())!=label:raise ValueError('Source-bound cloze marker changed')
   display=n.get('data-cloze-display',label)
   from inline_layout import cloze_display
   if cloze_display(n.get_text())!=display:raise ValueError('Source-bound cloze display changed')
   self.features.append({'kind':'observed_cloze_marker','label':label,'display':display})
   return r'\Cloze{'+display+'}'
  if tag=='ul'and n.has_attr('data-native-decision-tree'):
   binding=getattr(self,'decision_tree_style',None)
   if not binding or n['data-native-decision-tree']!='binary_chain':raise ValueError('Missing native decision-tree binding')
   from decision_trees import render as render_decision_tree
   return render_decision_tree(self,n,binding)
  if tag=='span'and n.has_attr('data-authored-word-gap'):
   identity=n['data-authored-word-gap']
   if n.contents or not re.fullmatch('[0-9a-f]{20}',identity):raise ValueError('Invalid authored group marker')
   width=self.word_space_em
   if isinstance(width,bool)or not isinstance(width,(int,float))or not 0<width<=2:raise ValueError('Authored group requires positive effective role width')
   self.features.append({'kind':'authored_word_group_gap','id':identity,'word_space_em':width,'context':context})
   return r'\AuthoredWordGap{'+str(width)+'}{'+identity+'}'
  if tag=='span'and n.has_attr('data-paragraph-role'):
   from paragraph_layout import render
   return render(self,n,context)
  if tag=='span'and n.has_attr('data-document-bullet'):
   notice_cell=context=='cell'and getattr(self,'native_notice_cell',False)
   if context!='notice'and not notice_cell:raise ValueError('A document list role cannot affect questions or answer marks')
   from document_bullets import present
   plain=Projection({'html':str(n)}).text.strip()
   body=''.join(self.node(x,context)for x in n.children).lstrip()
   body,hang=present(self,plain,body,n['data-document-bullet'],'notice_cell'if notice_cell else'notice')
   return r'\par{\parindent=0pt\hangindent='+str(hang)+r'em\hangafter=1\noindent '+body+r'\par}'
  if tag=='span'and n.has_attr('data-ascii-question-mark'):
   if n['data-ascii-question-mark']!='fullwidth-glyph' or n.find() or n.get_text()!='?':
    raise ValueError('Invalid ASCII question-mark glyph role')
   self.features.append({'kind':'ascii_question_mark_presentation','codepoint':'U+003F',
                         'feature':'fwid','pdf_actual_text':'U+003F','canonical_changed':False})
   return (r'\pdfextension literal direct{/Span << /ActualText <FEFF003F> >> BDC}'
           r'{\addfontfeatures{RawFeature=+fwid}?}\pdfextension literal direct{EMC}')
  if tag=='span'and n.has_attr('data-kept-star-cluster'):
   value=n.get_text()
   markup=n.find_all(True)
   valid_markup=not markup or (len(markup)==1 and markup[0].name=='u' and markup[0].string is not None and re.fullmatch(r'[ \t\u3000]*★[ \t\u3000]*',str(markup[0].string)))
   if n['data-kept-star-cluster']!='true'or not valid_markup or not re.fullmatch(r'[_★](?:[ \t\u3000]+[_★]){3}',value)or value.count('_')!=3 or value.count('★')!=1:
    raise ValueError('Invalid bound four-slot STAR cluster')
   self.features.append({'kind':'kept_star_cluster','text':value,'star_position':value.split().index('★')+1})
   return r'\mbox{'+self.text(value)+'}'
  if tag=='span'and n.has_attr('data-answer-blank'):
   from answer_blanks import EMPTY, COMPACT, ROLES
   text=n.get_text().strip(' ')
   valid=COMPACT.fullmatch(text) if n.get('data-blank-kind')=='compact-question' else EMPTY.fullmatch(text)
   if n['data-answer-blank'] not in ROLES or not valid or n.find() or n.get('data-blank-kind') not in [None,'compact-question']:
    raise ValueError('Stale or malformed answer bracket marker')
   dimensions=[float(n[k])for k in ['data-blank-inner','data-blank-left','data-blank-right']]
   if not 0<=dimensions[0]<=5 or any(not 0<=d<=2 for d in dimensions[1:]):raise ValueError('Invalid answer bracket marker')
   return r'\ContextBlank'+''.join('{'+str(d)+'}'for d in dimensions)
  if tag=='span'and n.has_attr('data-blank-padding'):
   if n['data-blank-padding']!='ascii' or n.find() or not re.fullmatch(' +',n.get_text()):raise ValueError('Invalid bracket padding marker')
   return ''
  if tag=='span'and n.get('data-bounded-word')=='heading-undotted-choice-selector':
   text=Projection({'html':str(n)}).text
   match=re.fullmatch(r'[1１]([ \u3000]*)[2２]([ \u3000]*)[3３]([ \u3000]*)[4４]([ \u3000]*)から',text)
   if not getattr(self,'source_target_markers',False) or context!='heading' or n.find() or not match:
    raise ValueError('Invalid Old undotted instruction selector')
   parts=[]
   for index,digit in enumerate('1234'):
    parts.append(r'\HistoricalSelectorDigit{'+digit+'}')
    separator=match[index+1]
    parts.append(self.text(separator) if separator else r'\hspace{'+('.5'if index<3 else'.3')+'em}')
   self.features.append(dict(kind='historical_instruction_selector',text=text,variant='undotted',canonical_changed=False))
   return r'\mbox{'+''.join(parts)+r'\mbox{から}}'
  if tag=='span'and n.get('data-bounded-word')in ['ruby-space-group','exact-source-group','heading-choice-selector','exact-date-range','exact-choice-selector']:
   if n['data-bounded-word']=='heading-choice-selector' and getattr(self,'source_target_markers',False):
    text=Projection({'html':str(n)}).text
    if n.find() or not re.fullmatch(r'[1１]\s*・\s*[2２]\s*・\s*[3３]\s*・\s*[4４][ \u3000]*から',text):raise ValueError('Invalid Old instruction selector')
    gap=getattr(self,'heading_choice_gap_em',0)
    sep=r'\hspace{'+str(gap/2)+r'em}・\hspace{'+str(gap/2)+'em}'if gap else '・'
    digits=sep.join(r'\HistoricalSelectorDigit{'+d+'}'for d in '1234')
    suffix=re.search(r'([ \u3000]*)から$',text)[1]
    self.features.append(dict(kind='historical_instruction_selector',text=text,canonical_changed=False))
    if getattr(self,'heading_selector_suffix_break',False):
     self.features.append(dict(kind='historical_heading_selector_suffix_break',text=text,canonical_changed=False))
     return r'\mbox{'+digits+r'}\allowbreak'+(self.text(suffix)if suffix else r'\hspace{.3em}')+'から'
    return r'\mbox{'+digits+(self.text(suffix)if suffix else r'\hspace{.3em}')+r'\mbox{から}}'
   if n['data-bounded-word']=='exact-choice-selector'and (len(Projection({'html':str(n)}).text)>20 or not re.fullmatch(r'1[ \u3000]+2[ \u3000]+3[ \u3000]+4[ \u3000]*から',Projection({'html':str(n)}).text)):
    raise ValueError('Invalid native exact choice selector')
   saved=getattr(self,'keep_spaced_words',False);self.keep_spaced_words=False
   try:body=''.join(self.node(x,context) for x in n.children)
   finally:self.keep_spaced_words=saved
   self.features.append({'kind':'bounded_date_range'if n.get('data-bounded-word')=='exact-date-range'else'bounded_spaced_word','text':Projection({'html':str(n)}).text,'basis':'Exact authored range across intact ruby'if n.get('data-bounded-word')=='exact-date-range'else'Existing space group across intact ruby markup, at most 12 base characters'})
   text=Projection({'html':str(n)}).text
   return r'\mbox{'+body+'}'+(r'\allowbreak{}' if getattr(self,'passage_word_flow',False) and text and text[-1] in '、。？！' else '')
  if tag=='span'and n.has_attr('data-range-token'):
   from range_tokens import render
   return render(self,n,context)
  if n.has_attr('data-passage-punctuation-gap'):
   gap=float(n['data-passage-punctuation-gap'])
   if not 0<gap<=2 or list(n.children):raise ValueError('Invalid punctuation-gap marker')
   return r'\hskip '+str(gap)+r'em\relax '
  if n.has_attr('data-passage-introduction'):
   role=n['data-passage-introduction']
   if role not in ['passage','document']:raise ValueError('Unknown passage introduction role')
   return ('\\DocumentIntroduction{' if role=='document' else '\\PassageIntroduction{')+''.join(self.node(x,context)for x in n.children)+'}'
  if tag=='u' and len(n.contents)==1 and isinstance(n.contents[0],Tag) and n.contents[0].has_attr('data-cloze-label'):
   return self.node(n.contents[0],context)
  if tag=='div'and n.has_attr('data-notice-inset-panel'):
   panel=getattr(self,'notice_inset_panels',None)
   if not panel:raise ValueError('Missing inset notice panel binding')
   if 'title_font_pt'in panel:
    children=[c for c in n.children if not isinstance(c,NavigableString)or c.strip()]
    title_tags=['p','center','h1','h2','h3']if panel.get('selector')in ['titled_divs','flow_ranges']else['p']
    if not children or not isinstance(children[0],Tag)or children[0].name not in title_tags:raise ValueError('Inset title needs an existing leading paragraph')
    title=children[0];size=panel['title_font_pt']
    if isinstance(size,bool)or not isinstance(size,(int,float))or not 10<=size<=24:raise ValueError('Invalid inset title size')
    titletex=self.value({'html':title.decode_contents()},'notice')
    if 'line_styles'in panel:
     from notice_layout import body_nodes_tex
     bodytex=body_nodes_tex(self,children[1:],panel['line_styles'][int(n['data-notice-inset-panel'])])
    else:bodytex=self.value({'html':''.join(map(str,children[1:]))},'notice')
    align=panel.get('title_align','center')
    if align not in ['left','center','right']:raise ValueError('Invalid inset title alignment')
    alignment={'left':r'\raggedright','center':r'\centering','right':r'\raggedleft'}[align]
    divider=''
    if 'title_rule_pt'in panel:
     weight=panel['title_rule_pt']
     if isinstance(weight,bool)or not isinstance(weight,(int,float))or not .1<=weight<=2:raise ValueError('Invalid inset title rule')
     divider=r'\par\nobreak\hrule height '+str(weight)+r'pt\relax\nobreak '
    body=r'{'+alignment+r'\fontsize{'+str(size)+'}{'+str(size*1.5)+r'}\selectfont '+titletex+r'\par}'+divider+r'\vspace{4pt}'+bodytex
   else:body=self.value({'html':n.decode_contents()},'notice')
   from notice_layout import panel_heading
   self.features.append({'kind':'notice_inset_panel','title':panel_heading(n)})
   return r'\par\addvspace{'+str(panel['gap_pt'])+r'pt}\NoticeInsetPanel{'+str(panel['radius_pt'])+'}{'+str(panel['padding_pt'])+'}{'+body+r'}\par\vspace{'+str(panel['gap_pt'])+'pt}'
  if tag=='section' and 'reading-passage' in n.get('class',[]) and getattr(self,'section_style',None):
   from section_layout import render_section
   return render_section(self,n,context,self.section_style)
  if tag=='span'and n.has_attr('data-paired-label-source'):
   from paired_labels import label_value
   source,display=n['data-paired-label-source'],n.get('data-paired-label-display')
   if n.find() or n.get_text()!=source or display not in ['A','B'] or label_value(source)!=display:
    raise ValueError('Invalid exact paired label display')
   self.features.append({'kind':'paired_label_display','source_label':source,'display_label':display,'canonical_delimiters_preserved':True})
   return r'\Para '+display+r'\Para '
  if n.has_attr('data-paired-label'):
   label=n['data-paired-label']
   if label not in ['A','B']or Projection({'html':str(n)}).text.strip()!=label:raise ValueError('Invalid paired label role')
   return r'\Para '+label+r'\Para '
  if n.get('data-paired-outside-citation')=='true':
   body=''.join(self.node(x,context)for x in n.children)
   self.features.append({'kind':'paired_external_citation','text':Projection({'html':str(n)}).text})
   return r'\PairedCitationStart{}{\raggedleft '+body+r'\par}\PairedCitationEnd{}'
  if tag=='span'and n.get('data-breadcrumb-separator')=='true':
   if n.get_text()!='>' or n.find():raise ValueError('Invalid breadcrumb separator')
   self.features.append({'kind':'breadcrumb_separator','character':'>','font_role':'breadcrumb_latin','side_gap_em':.35})
   return r'\nobreak\hspace{.35em}{\BreadcrumbLatin\char62}\hspace{.35em}\allowbreak{}'
  if tag=='span'and n.get('data-literal-identifier')=='true':
   text=n.get_text()
   if n.find() or not re.fullmatch(r'[0-9A-Za-z①-⑳-]+',text):raise ValueError('Invalid native identifier')
   parts=re.split(r'([①-⑳])',text)
   body=''.join(self.text(p) if re.fullmatch(r'[①-⑳]',p) else r'{\ContactLatin '+escape(p)+'}' for p in parts if p)
   self.features.append({'kind':'literal_identifier','text':text,'font_role':'contact_latin'})
   return r'\mbox{'+body+'}'
  if tag=='span'and n.get('data-native-inline-box')=='label':
   label=Projection({'html':str(n)}).text
   if getattr(self,'historical_inline_number_box_role',None)=='main_question' and re.fullmatch(r'[1-9][0-9]{0,2}',label):
    if not getattr(self,'source_target_markers',False) or any(x.name not in ['b','strong'] or x.attrs for x in n.find_all(True)):
     raise ValueError('Invalid historical numeric inline box')
    self.features.append(dict(kind='native_inline_label_box',text=label))
    self.features.append(dict(kind='historical_inline_number_box',text=label,font_role='boxed_numeral',geometry_role='main_question',canonical_changed=False))
    return r'\QNumber{'+label+'}'
   body=''.join(self.node(x,context)for x in n.children)
   if r'\Para'in body or r'\begin{'in body:raise ValueError('Block content cannot become an inline box')
   self.features.append({'kind':'native_inline_label_box','text':Projection({'html':str(n)}).text})
   if n.has_attr('data-inline-box-padding-pt'):
    padding=float(n['data-inline-box-padding-pt'])
    if not 0<=padding<=3:raise ValueError('Invalid inline box padding')
    return r'{\setlength\fboxsep{'+str(padding)+r'pt}\fbox{'+body+'}}'
   return r'\NativeInlineLabel{'+body+'}'
  if n.get('data-native-url-citation')=='true':
   if tag not in ['p','div'] or not n.find('span',attrs={'data-citation-url':'breakable'}):raise ValueError('Invalid URL citation block')
   body=''.join(self.node(c,context) for c in n.children)
   align=r'\raggedleft ' if re.search(r'text-align\s*:\s*right',n.get('style','')) else r'\raggedright '
   return r'\Para {'+align+body+r'\par}'
  if tag=='span'and n.get('data-citation-url')=='breakable':
   value=n.get_text()
   bracketed=any(value.startswith(a) and value.endswith(b) for a,b in [('<','>'),('〈','〉'),('《','》')])
   raw=value[1:-1] if bracketed else value
   if n.find()or not re.fullmatch(r'https?://[A-Za-z0-9:/?=&._%#~+\-]+',raw):raise ValueError('Invalid citation URL marker')
   self.features.append({'kind':'breakable_literal_citation_url','text':raw,'wrap_policy':'whole_if_fits_else_url_components'})
   head,rest=re.match(r'^(https?://[^/?]+)(.*)$',raw).groups()
   chunks=[head]+[x for x in re.split(r'(?<=[/?&=])',rest) if x]
   if bracketed:chunks[0]=value[0]+chunks[0];chunks[-1]+=value[-1]
   fallback=r'\allowbreak{}'.join(r'\mbox{'+self.text(c)+'}' for c in chunks)
   # Measure in the actual font and current frame width. Long URLs may break
   # at path/query boundaries; a fitting URL and its filename stay intact.
   return (r'\allowbreak{}\begingroup\setbox0=\hbox{'+self.text(value)+
           r'}\ifdim\wd0>\linewidth '+fallback+r'\else\box0\fi\endgroup\allowbreak{}')
  if tag=='span'and n.get('data-citation-attribution')=='kept':
   value=n.get_text()
   if n.find() or not re.fullmatch(r'\s*\d{4}年\s*\d{1,2}月\s*\d{1,2}日取得による[）)]',value):raise ValueError('Invalid citation attribution')
   return r'\allowbreak{}\mbox{'+self.text(value)+'}'
  if tag=='span'and n.has_attr('data-css-underlined-reference'):
   children=[x for x in n.children if isinstance(x,Tag)]
   if len(children)!=2 or children[0].name!='u' or children[1].get_text()!=n['data-css-underlined-reference']:raise ValueError('Invalid prepared CSS underline reference')
   body=''.join(self.node(x,context)for x in children[0].children)
   label=n['data-css-underlined-reference'];clearance=n.get('data-reference-clearance')
   self.features.append({'kind':'underline_reference','label':label,'text':Projection({'html':str(children[0])}).text,'source_placement':'css_below'})
   return r'\UnderlinedReference'+('['+clearance+']'if clearance is not None else'')+'{'+self.text(label)+'}{'+body+'}'
  body=self.pedagogical_groups(n,context) if tag=='u'and getattr(self,'underlined_word_groups',False)and re.search(r'[ \u3000]',Projection({'html':str(n)}).text) else ''.join(self.node(x,context) for x in n.children)
  if n.has_attr('data-right-inset-em'):
   inset=float(n['data-right-inset-em'])
   if not 0<=inset<=3 or 'right' not in n.get('style',''):raise ValueError('Invalid right-aligned inset')
   body+=r'\hspace*{'+str(inset)+'em}'
   self.features.append({'kind':'soft_right_inset','text':Projection({'html':str(n)}).text,'inset_em':inset})
  if tag=='span' and n.has_attr('data-note-label'):
   label=n['data-note-label'];label_tex=text_tex(label)
   if getattr(self,'source_target_markers',False):self.features.append({'kind':'layout_symbol','text':label,'basis':'Source-supported note label explicitly encoded in the canonical data-note-label attribute'})
   if getattr(self,'active_vertical_body',False):
    label_tex=re.sub(r'[0-9０-９]+',lambda m:r'\VerticalNoteDigit{'+m[0]+'}',label_tex)
    if re.search(r'[0-9０-９]',label):self.features.append({'kind':'upright_vertical_note_digits','label':label,'font_role':'annotation','scope':'inline note label only'})
    if getattr(self,'source_target_markers',False):
     self.features.append({'kind':'historical_vertical_note_side','side':'right','label':label})
     return r'\HistoricalVerticalNote{'+body+'}{'+label_tex+'}'
   return r'\AnnotatedTerm{'+body+'}{'+label_tex+'}'
  style=n.get('style','')
  if tag=='span' and (n.has_attr('data-extra-underline') or n.has_attr('data-double-underline')):
   if not getattr(self,'source_target_markers',False):raise ValueError('Historical underline outside historical edition')
   extra=n.get('data-extra-underline')=='true';double=n.get('data-double-underline')=='true'
   if extra==double:raise ValueError('Ambiguous historical underline marker')
   self.features.append({'kind':'historical_extra_underline' if extra else 'historical_double_underline','text':Projection({'html':str(n)}).text})
   return ('\\HistoricalExtraUnderline{' if extra else '\\HistoricalDoubleUnderline{')+body+'}'
  if tag=='span' and n.get('data-reference-parenthesized')=='true':
   if not getattr(self,'source_target_markers',False):raise ValueError('Historical parenthetical reference outside historical edition')
   label=n.get('data-reference-label','');position=n.get('data-reference-position','before')
   if not re.fullmatch(r'[1-9][0-9]*',label)or position not in ['before','after']or n.get('data-reference-boxed'):
    raise ValueError('Invalid historical parenthetical reference')
   self.features.append({'kind':'historical_parenthetical_reference','label':label,'position':position,'text':Projection({'html':str(n)}).text})
   marker=r'\HistoricalCompactNumber{'+label+'}'
   return body+r'\nobreak{}'+marker if position=='after'else marker+r'\nobreak{}'+body
  if tag=='u' and n.get('data-reference-label'):
   label=n['data-reference-label'];plain=Projection({'html':str(n)}).text
   self.features.append({'kind':'underline_reference','label':label,'text':plain})
   clearance=n.get('data-reference-clearance')
   if clearance is not None:self.features[-1]['clearance_below_pt']=float(clearance)
   if n.get('data-reference-boxed')=='true':
    if not getattr(self,'source_target_markers',False):raise ValueError('Historical boxed reference outside historical edition')
    self.features[-1]['boxed']=True
    if not re.fullmatch(r'[1-9][0-9]*',label):raise ValueError('Historical boxed ID must be a plain positive integer')
    target=r'\HistoricalBoxedReference{'+label+'}{'+self.text(label)+'}{'+body+'}'
   elif getattr(self,'source_target_markers',False) and getattr(self,'active_vertical_body',False):
    self.features.append({'kind':'historical_vertical_reference_side','label':label,'side':'right','ordinary_ruby_unchanged':True})
    target=r'\HistoricalVerticalReference{'+self.text(label)+'}{'+body+'}'
   elif getattr(self,'source_target_markers',False) and re.fullmatch(r'（[1-9][0-9]*）',label) and clearance is None:
    target=r'\HistoricalTargetReference{\HistoricalCompactNumber{'+label[1:-1]+'}}{'+body+'}'
   else:target=r'\UnderlinedReference'+('['+clearance+']'if clearance is not None else'')+'{'+self.text(label)+'}{'+body+'}'
   # A zero-width reference label can otherwise remain on the preceding line.
   # Keep only short explicit Japanese targets together; long reading spans
   # and targets containing structural breaks retain normal paragraph flow.
   if getattr(self,'source_target_markers',False) and len(plain)<=6 and bounded_word(plain) and not n.find(['br','p','div','table','img']):
    self.features.append({'kind':'historical_bounded_reference','label':label,'text':plain,'limit':6})
    return r'\mbox{'+target+'}'
   return target
  if tag=='u' and (context in ['example','heading'] or getattr(self,'scored_star',False)) and Projection({'html':str(n)}).text.strip()=='★':
   self.features.append({'kind':'underline','text':Projection({'html':str(n)}).text})
   return r'\StarSlot{}'
  if tag=='u' or 'text-decoration' in style and 'underline' in style:
   self.features.append({'kind':'underline','text':Projection({'html':str(n)}).text});body=r'\Slot{}'if context=='heading'and not Projection({'html':str(n)}).text.strip()else (r'\HistoricalVerticalUnderline{' if getattr(self,'source_target_markers',False) and getattr(self,'active_vertical_body',False) else r'\underLine{')+body+'}'
   if getattr(self,'source_target_markers',False) and context!='heading' and re.fullmatch(r'[ \u3000\t]+',Projection({'html':str(n)}).text) and not n.find():
    # A whitespace-only underlined answer field is one native blank. Keep
    # its authored width, but never divide that blank over two text lines.
    if getattr(self,'historical_phrase_answer_line',False) is True:
     body=r'\Slot{}'
     self.features.append({'kind':'historical_phrase_underlined_blank','text':Projection({'html':str(n)}).text,'width_role':'bound_section_phrase_answer_line','canonical_changed':False})
    else:body=r'\mbox{'+body+'}'
    self.features.append({'kind':'historical_atomic_underlined_blank','text':Projection({'html':str(n)}).text,'canonical_changed':False})
   historical_prefix=getattr(self,'source_target_markers',False) and context=='body' and not getattr(self,'active_vertical_body',False)
   if tag=='u' and (getattr(self,'passage_word_flow',False) or historical_prefix) and isinstance(n.previous_sibling,NavigableString) and re.search(r'[①-⑳]\s*$',str(n.previous_sibling)):
    # Preserve an existing prefix reference's association without moving it
    # beneath the underline. Only short Japanese targets stay whole;
    # longer spans retain normal paragraph flow.
    plain=Projection({'html':str(n)}).text
    short_target=historical_prefix and len(plain)<=12 and bounded_word(plain) and not n.find(['br','p','div','table','img'])
    if short_target:body=r'\mbox{'+body+'}'
    body=r'\nobreak{}'+body
    if historical_prefix:
     self.features.append({'kind':'historical_bound_prefix_reference','label':re.search(r'([①-⑳])\s*$',str(n.previous_sibling))[1],'text':plain,'scope':'horizontal_body','short_target_kept':bool(short_target),'short_target_limit':12,'canonical_changed':False})
   # An unspaced final particle belongs to the preceding pedagogical group.
   # Keep the underline's exact scope while preventing a lone ka/ne/yo line.
   if tag=='u'and getattr(self,'underlined_word_groups',False)and isinstance(n.next_sibling,NavigableString)and re.match(r'^[かねよ][。？！?!]',str(n.next_sibling)):
    body+=r'\nobreak{}'
  elif tag in ['s','del'] or 'line-through' in style:
   self.features.append({'kind':'strikethrough','text':Projection({'html':str(n)}).text});body=r'\strikeThrough{'+body+'}'
  elif tag in ['b','strong']:body=r'{\bfseries '+body+'}'
  elif tag in ['em','i']:body=r'{\itshape '+body+'}'
  elif tag=='sup':body=r'\textsuperscript{'+body+'}'
  elif tag=='sub':body=r'\textsubscript{'+body+'}'
  elif tag=='li':
   marker='・' if n.parent.name=='ul' else ''
   literal_marker=n.get('data-literal-list-marker')
   if literal_marker is not None and literal_marker!=marker:raise ValueError('Literal list marker differs from native unordered marker')
   if marker:self.features.append({'kind':'literal_list_marker' if literal_marker else 'layout_symbol','text':marker,'basis':'existing literal marker retained by native list' if literal_marker else 'unordered HTML list marker'})
   if context=='notice'and getattr(self,'notice_list_continuations',None):
    plain=Projection({'html':str(n)}).text.strip()
    selected=[(index,spec)for index,spec in enumerate(self.notice_list_continuations)if spec['text']==plain]
    if len(selected)>1:raise ValueError('Duplicate notice list continuation')
    if selected:
     index,spec=selected[0];prefix=spec['prefix'];lines=plain.splitlines()
     if set(spec)!={'text','prefix'}or len(lines)!=2 or not 1<=len(prefix)<=30 or not lines[0].startswith(prefix)or len(lines[0])<=len(prefix)or n.find(['ruby','ul','ol'])or body.count(r'\NoticeLine ')!=1:raise ValueError('List continuation requires two exact plain lines and a proper first-line prefix')
     following=lines[0][len(prefix)]
     measure=(r'\settowidth\NoticeLineIndent{'+self.text(prefix+following)+r'}'
              r'\settowidth\NoticePrefixTail{'+self.text(following)+r'}'
              r'\addtolength\NoticeLineIndent{-\NoticePrefixTail}')
     # The converter's delimiter after the control word was previously ignored
     # by TeX. Consume it here so inserting a dimension does not print a space.
     body=measure+body.replace(r'\NoticeLine ',r'\NoticeLine\hspace*{\NoticeLineIndent}',1)
     self.notice_list_continuations_used.append(index)
     self.features.append({'kind':'notice_list_continuation','text':plain,'prefix':prefix,'basis':'exact existing prefix with following-character boundary measurement'})
   if context=='notice'and getattr(self,'notice_list_indent',None)is not None:
    body=r'\par{\leftskip='+str(self.notice_list_indent)+r'em\parindent=0pt\noindent\llap{'+marker+r'\hspace{.2em}}'+body+r'\par}'
   else:body=r'\Para '+marker+body
  if tag=='center' or 'text-align:center' in style or 'text-align: center' in style:
   body=r'\Para {\centering '+body+r'\par}\Para '
  elif 'text-align:right' in style or 'text-align: right' in style:
   body=r'\Para {\raggedleft '+body+r'\par}\Para '
  elif tag in ['p','div','h1','h2','h3','h4','blockquote']:
   if tag.startswith('h')and tag[1:].isdigit():body=r'{\bfseries '+body+'}'
   body=r'\Para '+body+r'\Para '
  if 'border-top:' in style and 'border-bottom:' in style:
   body=r'\Para\begin{RuleFrame}'+body+r'\end{RuleFrame}\Para '
  elif 'border:' in style or 'border :' in style:
   body=r'\Para\begin{NoticeFrame}'+body+r'\end{NoticeFrame}\Para '
  return body

 def answer_cell(self,raw):
  plain=Projection({'html':raw}).text.strip()
  if re.fullmatch(r'[（(](?:例|れい)[）)]',plain):
   # The native AnswerLine already owns the cell border. A clipped legacy
   # span around the label must not become a nested paragraph-mode frame.
   soup=BeautifulSoup(raw,'html.parser')
   for span in soup.find_all('span'):
    if 'border:'in span.get('style','')and Projection({'html':str(span)}).text.strip()==plain:
     span.unwrap();self.features.append({'kind':'answer_label_border_owned_by_native_strip','text':plain})
   raw=str(soup)
   return r'\AnswerExampleLabel{'+self.value({'html':raw},'option')+'}'
  if plain in '①②③④' and len(plain)==1:
   return r'\AnswerBubble{'+str('①②③④'.index(plain)+1)+'}'
  if plain in '❶❷❸❹' and len(plain)==1:
   return r'\AnswerBubbleFilledNumber{'+str('❶❷❸❹'.index(plain)+1)+'}'
  if plain=='●':return r'\AnswerBubbleFilled{}'
  return self.value({'html':raw},'option')

 def example(self,value,variant,options=None,options_vertical=False):
  """Recognize structural HTML paragraph/table components, never replace their text."""
  structure=getattr(self,'example_layout',None)
  if structure:
   if 'answer_line_pair'in structure and not getattr(self,'source_target_markers',False):
    raise ValueError('Historical answer line pair outside Old JLPT')
   from example_layout import prepare
   value=prepare(value,structure)
   self.features.append({'kind':'restored_example_structure','layout':structure})
  if isinstance(value,str):value={'html':html.escape(value).replace('\n','<br/>')}
  soup=BeautifulSoup(value['html'],'html.parser');parts=[];buf=[]
  choice_lists=[];choice_tables=[];table_values={}
  if options:
   for node in soup.find_all('ol'):
    children=[x for x in node.children if not isinstance(x,NavigableString)or x.strip()]
    if len(children)!=len(options)or any(not isinstance(x,Tag)or x.name!='li'for x in children):continue
    pairs=[(Projection({'html':x.decode_contents()}),Projection(v))for x,v in zip(children,options)]
    if all(a.text==b.text and a.ruby==b.ruby for a,b in pairs):choice_lists.append(node)
   from example_layout import numbered_table_choices
   for node in soup.find_all('table'):
    try:choices=numbered_table_choices(node)
    except ValueError:continue
    pairs=[(Projection(c['value']),Projection(v))for c,v in zip(choices,options)]
    if len(options)==4 and [c['number']for c in choices]==[1,2,3,4]and all(a.text==b.text and a.ruby==b.ruby for a,b in pairs):
     choice_tables.append(node);table_values[id(node)]=[c['value']for c in choices]
  if len(choice_lists)+len(choice_tables)>1:raise ValueError('Example has multiple matching choice lists or tables')
  def flush():
   if ''.join(buf).strip():parts.append(('text',''.join(buf)))
   buf.clear()
  def walk(n):
   if isinstance(n,NavigableString):
    # Plain newlines in an unwrapped rich value carry the original example breaks.
    for j,piece in enumerate(str(n).split('\n')):
     if j:flush()
     buf.append(piece)
   elif any(n is x for x in choice_lists):flush();parts.append(('choice_list',n))
   elif any(n is x for x in choice_tables):flush();parts.append(('choice_table',n))
   elif n.name=='div' and n.get('data-historical-framed-document')=='single' and getattr(self,'source_target_markers',False):
    flush();parts.append(('historical_frame',n))
   elif n.name=='table':flush();parts.append(('table',n))
   elif n.name in ['br','p','div'] or (n.name=='span'and n.has_attr('data-authored-plain-break')):
    flush()
    for c in n.children:walk(c)
    flush()
   else:buf.append(str(n))
  for n in soup.children:walk(n)
  flush();out=[];answer_label='';star=variant=='star_worked';skip=set()
  historical_example=bool(getattr(self,'source_target_markers',False) and not star)
  framed_example=getattr(self,'historical_example_frame',None)
  if framed_example and not historical_example:raise ValueError('Framed example arrangement requires ordinary Old example')
  frame_used=0;frame_question_used=0
  # The old Level3 source also prints a kana/kanji mixed answer-sheet label.
  # Match its base text without replacing the retained ruby or widening Modern.
  answer_names=r'解答用紙|かいとうようし'+(r'|かいとう用紙' if historical_example else '')
  choices_seen=False;explanation_seen=False
  if star and parts and parts[0][0]=='text':
   lead=re.match(r'^([（(].*?[）)])\s*(.+)$',parts[0][1],re.S)
   if lead and re.sub(r'\s','',Projection({'html':lead[1]}).text)in ['（問題例）','(問題例)']:
    parts[:1]=[('text',lead[1]),('text',lead[2])]
  # Choices belong before the answer demonstration. A solution table is never
  # evidence that the independent choice row has already been printed.
  boundary=next((j for j,(k,v)in enumerate(parts)if k=='table' or re.search(r'解答のしかた|解答の仕方|答え方|こたえかた|'+answer_names,re.sub(r'\s','',Projection({'html':str(v)}).text))),len(parts))
  prefix='\n'.join(Projection({'html':str(v)}).text for k,v in parts[:boundary])
  listed=any(k in ['choice_list','choice_table']for k,v in parts[:boundary])
  if (choice_lists or choice_tables)and not listed:raise ValueError('Example choice list or table must precede the answer demonstration')
  embedded=listed or bool(options)and all(re.search(r'(?<!\d)'+str(n+1)+r'\s*'+re.escape(Projection(v).text.strip()),prefix)for n,v in enumerate(options))
  self.example_options_embedded=embedded
  target_row=getattr(self,'historical_example_target_row',None)
  example_grid=getattr(self,'historical_example_options',None)
  if example_grid and (not historical_example or not options or (embedded and not listed) or target_row):
   raise ValueError('Conflicting historical example choice-grid parser structure')
  if target_row:
   index=target_row['target_part']
   merged=target_row.get('source_shape')=='merged_prompt_target_embedded_choices'
   if (not historical_example or not options or (embedded and not merged) or index>=boundary
       or index>=len(parts) or parts[index][0]!='text'):
    raise ValueError('Conflicting historical example target/choice parser structure')
   if merged:
    if not listed or len(parts)!=4 or index!=1 or parts[2][0]!='choice_list':
     raise ValueError('Merged historical example must own one embedded choice list')
    skip.add(2)
  choice_gap=getattr(self,'historical_example_choices_before_pt',0)
  if type(choice_gap)not in [int,float] or not 0<=choice_gap<=30:
   raise ValueError('Invalid historical example choice clearance')
  if choice_gap and (not historical_example or star):
   raise ValueError('Historical example choice clearance outside ordinary Old example')
  choice_gap_emitted=False
  def spaced_choices(tex):
   nonlocal choice_gap_emitted
   if not choice_gap or choice_gap_emitted:return tex
   choice_gap_emitted=True
   self.features.append(dict(kind='historical_example_choice_clearance',
     target=getattr(self,'historical_example_target_id',None),before_pt=choice_gap,canonical_changed=False))
   return r'\par\vspace{'+str(choice_gap)+r'pt}\noindent '+tex
  def choices_tex(choices):
   values=[self.value(v,'option')for v in choices]
   if example_grid:
    from historical_layout import options_tex as grid_tex
    self.features.append(dict(kind='historical_example_option_grid',target=self.historical_example_target_id,
      columns=example_grid['columns'],left_indent_em=example_grid.get('left_indent_em',0),options_sha256=example_grid['options_sha256'],canonical_changed=False))
    grid=grid_tex(self,{'id':self.historical_example_target_id,'options':choices},
      {'kind':'grid','columns':example_grid['columns'],'source_numbered':False},values,row_gap_pt=0)
    if example_grid.get('width_fraction',1)!=1:
     fraction=example_grid['width_fraction']
     grid=r'\begin{minipage}[t]{'+str(fraction)+r'\linewidth}\vspace{0pt}'+grid+r'\par\end{minipage}'
     self.features.append(dict(kind='historical_example_option_measure',target=self.historical_example_target_id,width_fraction=fraction,canonical_changed=False))
    return spaced_choices(r'\HistoricalExampleChoices{'+str(example_grid.get('left_indent_em',0))+'em}{'+grid+'}')
   label=lambda n:r'\ExampleChoiceNumber{'+str(n)+'}' if getattr(self,'example_choice_numerals',False) else str(n)
   return spaced_choices((r'\OptionsVertical'+''.join('{'+v+'}'for v in values))if options_vertical else r'\ExampleChoices'+''.join('{'+label(j+1)+r'\hspace{.4em}'+v+'}'for j,v in enumerate(values)))
  choice_tex=''
  if options and not embedded and not target_row:
   choice_tex=choices_tex(options)
   self.features.append({'kind':'example_separate_choices','count':len(options),'before_demonstration':boundary<len(parts)})
  for pi,(kind,obj) in enumerate(parts):
   if pi==boundary and choice_tex:out.append(choice_tex)
   if pi in skip:continue
   if kind=='historical_frame':
    if not historical_example or obj.find(['table','img']):raise ValueError('Old example frame requires its complete native text notice')
    if framed_example:raise ValueError('Bound example frame was not adjacent to its complete label')
    out.append(self.node(obj,'example'))
    self.features.append(dict(kind='historical_example_framed_notice',canonical_changed=False))
    continue
   if target_row and pi==target_row['target_part']:
    from historical_example_rows import render as render_example_row
    out.append(render_example_row(self,self.historical_example_target_id,str(obj),options,target_row))
    choices_seen=True
    continue
   if kind=='choice_list':
    out.append(choices_tex([{'html':x.decode_contents()}for x in obj.find_all('li',recursive=False)]))
    choices_seen=True
    self.features.append({'kind':'example_ordered_choices','count':len(options),'metadata_duplicate_suppressed':True})
    continue
   if kind=='choice_table':
    out.append(choices_tex(table_values[id(obj)]))
    choices_seen=True
    self.features.append({'kind':'example_table_choices','count':len(options),'metadata_duplicate_suppressed':True})
    continue
   plain=Projection({'html':str(obj)}).text.strip()
   if kind=='text' and re.fullmatch(r'[（(](?:'+answer_names+r')[）)]',re.sub(r'\s','',plain)):
    answer_label=self.value({'html':obj},'option');continue
   if kind=='table':
    rows=obj.find_all('tr');cells=rows[0].find_all(['td','th'],recursive=False) if rows else []
    if len(rows)==1:
     cap=obj.find('caption')
     if cap:answer_label=self.value({'html':cap.decode_contents()},'option')
     content=[c.decode_contents()for c in cells]
     if content and re.search(answer_names,Projection({'html':content[0]}).text):answer_label=self.value({'html':content.pop(0)},'option')
     if len(content)==2:
      # Legacy HTML stores all four printed bubbles in a single cell.
      tokens=re.findall(r'[①②③④❶❷❸❹●]',Projection({'html':content[1]}).text)
      if len(tokens)==4:content=content[:1]+tokens
     if len(content)==5:
      out.append(r'\AnswerLine{'+answer_label+'}{'+r' & '.join(self.answer_cell(c)for c in content)+'}')
      answer_label='';continue
    if star and len(rows)>1:
     # A following dialogue turn continues the worked solution. The source
     # N5 witness confirms this grouping; accepted table/text values stay intact.
     tail=[]
     for j in range(pi+1,len(parts)):
      k,v=parts[j]
      if k!='text' or not re.match(r'^[A-ZＡ-Ｚ]\s*[「｢]',Projection({'html':v}).text.strip()):break
      tail.append(v);skip.add(j)
     if tail:
      obj=copy.deepcopy(obj);columns=sum(int(c.get('colspan',1))for c in obj.find('tr').find_all(['td','th'],recursive=False))
      holder=obj.find('tbody')or obj
      for value in tail:
       tr=soup.new_tag('tr');td=soup.new_tag('td',colspan=str(columns))
       for child in list(BeautifulSoup(value,'html.parser').contents):td.append(child)
       tr.append(td);holder.append(tr)
      self.features.append({'kind':'example_solution_dialogue','following_turns':len(tail),'basis':'explicit dialogue continuation; shared component'})
    table_tex=self.table(obj,'star_solution' if star else 'example')
    out.append(r'{\StarWorkedFont '+table_tex+r'\par}' if star else table_tex);continue
   # A flattened answer demonstration is still an unscored answer row.
   inline_answer=re.fullmatch(r'([（(]解答用紙の例[：:])\s*([①②③④❶❷❸❹●\s]+)([）)])',plain)
   if inline_answer:
    from example_layout import slice_inline
    tokens=re.findall(r'[①②③④❶❷❸❹●]',inline_answer[2])
    if len(tokens)!=4:raise ValueError('Inline answer demonstration needs four existing bubbles')
    offset=len(Projection({'html':str(obj)}).text)-len(Projection({'html':str(obj)}).text.lstrip())
    label=self.value({'html':slice_inline(str(obj),offset+inline_answer.start(1),offset+inline_answer.end(1))},'option')
    framed=bool(structure and structure.get('inline_answer_frame'))
    if framed:
     out.append(r'\InlineAnswerLine{'+label+'}{'+' & '.join(self.answer_cell(x)for x in tokens)+'}{'+self.text(inline_answer[3])+'}')
    else:
     out.append(label+r'\hspace{.4em}'+r'\hspace{.3em}'.join(self.answer_cell(x)for x in tokens)+self.text(inline_answer[3])+r'\par')
    self.features.append({'kind':'inline_answer_demonstration','bubbles':4,'framed':framed,'basis':'Retained parenthetical caption; native answer glyphs without invented answer label'})
    continue
   answer=re.fullmatch(r'([（(](?:'+answer_names+r')[）)])\s*([（(](?:例|れい)[）)])\s*([①②③④❶❷❸❹●\s]+)',plain)
   if answer:
    tokens=re.findall(r'[①②③④❶❷❸❹●]',answer[3])
    if len(tokens)!=4:raise ValueError('Answer demonstration needs four existing bubbles')
    from example_layout import slice_inline
    offset=len(Projection({'html':str(obj)}).text)-len(Projection({'html':str(obj)}).text.lstrip())
    label_raw=[slice_inline(str(obj),offset+answer.start(k),offset+answer.end(k))for k in [1,2]]
    labels=[self.value({'html':label_raw[0]},'option'),self.answer_cell(label_raw[1])]
    out.append(r'\AnswerLine{'+labels[0]+'}{'+labels[1]+' & '+' & '.join(self.answer_cell(x)for x in tokens)+'}')
    continue
   # A caption and its bubble row may be separate HTML paragraphs or plain
   # lines. Consume the same native strip as the combined/table variants.
   separate_answer=re.fullmatch(r'([（(](?:例|れい)[）)])\s*([①②③④❶❷❸❹●\s]+)',plain)
   if answer_label and separate_answer:
    tokens=re.findall(r'[①②③④❶❷❸❹●]',separate_answer[2])
    if len(tokens)!=4:raise ValueError('Separate answer demonstration needs four existing bubbles')
    from example_layout import slice_inline
    offset=len(Projection({'html':str(obj)}).text)-len(Projection({'html':str(obj)}).text.lstrip())
    label=slice_inline(str(obj),offset+separate_answer.start(1),offset+separate_answer.end(1))
    out.append(r'\AnswerLine{'+answer_label+'}{'+self.answer_cell(label)+' & '+' & '.join(self.answer_cell(x)for x in tokens)+'}')
    self.features.append({'kind':'paragraph_answer_strip','bubbles':4,'selected_positions':[j+1 for j,x in enumerate(tokens)if x in '❶❷❸❹●']})
    answer_label='';continue
   tx=None
   # Numbered options already exist in the accepted content. Reflow, do not add.
   starts=list(re.finditer(r'(?<!\S)([1-4])[)）]?\s+',obj))
   if len(starts)==4 and sorted(m[1]for m in starts)==list('1234'):
    rendered=[]
    for k,m in enumerate(starts):
     end=starts[k+1].start() if k+1<len(starts) else len(obj)
     # The row supplies its own column gaps; only spaces inside a choice belong to it.
     x=obj[m.start():end].rstrip()
     if structure and structure.get('bare_choice_labels'):
      x=re.sub(r'^([1-4])[)）]\s+',r'\1 ',x,count=1)
     opt=self.value({'html':x},'option')
     if getattr(self,'example_choice_numerals',False):opt=re.sub('^('+numeric_token('[1-4]')+')',lambda m:r'\ExampleChoiceNumber{'+literal_digits(m[1])+'}',opt,count=1)
     rendered.append(opt)
    tx=r'\ExampleChoices'+''.join('{'+x+'}'for x in rendered)
    # value() above was only used for structure; avoid double feature counts.
    # Features are a layout audit, not the content coverage input.
   instruction_star=False
   if star and kind=='text':
    from star_instruction import prepare as prepare_star_instruction
    obj,instruction_star=prepare_star_instruction(str(obj))
   if tx is None:tx=self.value({'html':obj},'option'if instruction_star else'example')
   if historical_example:
    label=re.match(r'^[（(](?:例|れい)[）)]',plain)
    is_choice=bool(re.match(r'^[1-4]\s+',plain)) or tx.startswith(r'\ExampleChoices')
    if label:
     from example_layout import slice_inline
     raw_plain=Projection({'html':str(obj)}).text
     offset=len(raw_plain)-len(raw_plain.lstrip())
     labeltex=self.value({'html':slice_inline(str(obj),offset,offset+label.end())},'option')
     rest=self.value({'html':slice_inline(str(obj),offset+label.end(),len(raw_plain))},'example')if offset+label.end()<len(raw_plain)else''
     if framed_example:
      if rest or pi+1>=len(parts) or parts[pi+1][0]!='historical_frame':raise ValueError('Framed example requires a standalone label immediately before its notice')
      from historical_example_frame import render as render_example_frame
      tx=render_example_frame(self,labeltex,parts[pi+1][1],framed_example)
      skip.add(pi+1);frame_used+=1
     else:
      prompt_macro=r'\HistoricalHangingExamplePrompt'if getattr(self,'historical_example_prompt_hanging',False)else r'\HistoricalExamplePrompt'
      tx=prompt_macro+'{'+labeltex+'}{'+rest+'}'
      if example_grid and 'prompt_label_indent_em'in example_grid:
       inset=example_grid['prompt_label_indent_em']
       tx=r'{\leftskip='+str(inset)+r'em\relax '+tx+'}'
       self.features.append(dict(kind='historical_options_example_prompt_inset',target=self.historical_example_target_id,inset_em=inset,canonical_changed=False))
      if prompt_macro==r'\HistoricalHangingExamplePrompt':self.features.append(dict(kind='historical_example_prompt_hanging',target=getattr(self,'historical_example_target_id',None),canonical_changed=False))
      self.features.append({'kind':'historical_example_prompt','label':label[0],'canonical_changed':False})
    elif choices_seen and not is_choice and pi<boundary:
     tx=(r'\HistoricalExampleExplanationStart{}' if not explanation_seen else '')+r'\HistoricalExampleExplanation{'+tx+'}'
     explanation_seen=True
     self.features.append({'kind':'historical_example_explanation','text':plain,'canonical_changed':False})
    if is_choice:
     tx=spaced_choices(tx)
     choices_seen=True
    if framed_example and plain.startswith(framed_example['question_prefix']):
     tx=r'\noindent\hspace*{'+str(framed_example['question_indent_em'])+'em}'+tx
     frame_question_used+=1
   # Embedded vertical choices are a separate path from four-choice rows.
   # Dot-numbered STAR instructions and digits inside a sentence are excluded.
   if getattr(self,'example_choice_numerals',False) and kind=='text' and re.match(r'^[1-4]\s+',plain) and len(starts)==1:
    tx=re.sub('^('+numeric_token('[1-4]')+r')(?=\s|\\hskip)',lambda m:r'\ExampleChoiceNumber{'+literal_digits(m[1])+'}',tx,count=1)
   label_gap=getattr(self,'example_label_gap_em',None)
   if label_gap is not None and re.match(r'^[（(]れい[）)]',plain):
    # An exact administrative example label is separate from word glue.
    tx=re.sub(r'^('+OPEN_PAREN_TEX+'れい'+CLOSE_PAREN_TEX+r')(?:\s|\\hskip [0-9.]+em\\relax )*',lambda m:m[1]+r'\hspace{'+str(label_gap)+'em}',tx,count=1)
   if instruction_star:self.features.append({'kind':'administrative_star_symbol','text':plain,'preserved_exercise_slots':True})
   if star and (re.match(r'^[12][.．]',plain) or re.fullmatch(r'[（(](?:問題例|もんだいれい|解答のしかた|解答の仕方|答え方|こたえかた)[）)]',re.sub(r'\s','',plain))):
    tx=r'{\ExampleInstructionFont '+tx+r'}'
   if star and re.search(r'解答のしかた|解答の仕方|答え方|こたえかた',re.sub(r'\s','',plain)):
    tx=r'\vspace{\StarSolutionBefore}'+tx
   if star and pi>0 and not any(k=='table' for k,v in parts[:pi]) and not re.search(r'解答|答え方|こたえかた',plain) and not re.match(r'^1[.．]',plain) and not tx.startswith(r'\ExampleChoices'):
    tx=r'\noindent\hspace*{\ExampleStemIndent}'+tx
   out.append(tx+r'\par')
  if choice_tex and boundary==len(parts):out.append(choice_tex)
  if answer_label:out.append(answer_label+r'\par')
  if framed_example and (frame_used,frame_question_used)!=(1,1):raise ValueError('Framed example roles were not consumed exactly once')
  return '\n'.join(out)

 def split_notes(self,value,notes):
  proj=Projection(value)
  if hashlib.sha256(proj.text.encode()).hexdigest()!=notes['projection_sha256']:raise ValueError('Stale note range')
  start=notes['start'];end=notes['end']
  if end!=len(proj.text) or not proj.mapping[start]:raise ValueError('Unsupported note range')
  rawpos=proj.mapping[start][0]
  if any(r['start']<start<r['end']for r in proj.ruby):raise ValueError('Note range splits ruby')
  raw=proj.raw
  if isinstance(value,dict) and getattr(self,'source_target_markers',False):
   # A source-bound Old paragraph role must stay with its paragraph. Cutting
   # after its opening <p> leaves an empty note inside a vertical frame and
   # strips the first exterior definition's role. Move only an immediately
   # preceding complete paragraph opener, preserving the same Projection.
   opening=re.search(r'<p\b[^>]*>$',raw[:rawpos])
   if opening and 'data-historical-text-role' in opening[0]:
    cut=opening.start()
    left={'html':raw[:cut]};right={'html':raw[cut:]}
    if Projection(left).text!=proj.text[:start] or Projection(right).text!=proj.text[start:]:
     raise ValueError('Historical note paragraph split changed its projection')
    return left,right
  if isinstance(value,str):before=raw[:rawpos];after=raw[rawpos:]
  else:before={'html':raw[:rawpos]};after={'html':raw[rawpos:]}
  return before,after

 def note_markers(self,before,after,anchors=None):
  """Use exact preceding definitions or explicit validated term/marker spans."""
  bp=Projection(before);ap=Projection(after)
  from note_definitions import terms_in_confirmed_cluster
  definitions=terms_in_confirmed_cluster(ap.text)
  replacements=[];bound={};used=set()
  for a in anchors or []:
   ts,te,ms,me=(a[k] for k in ['term_start','term_end','marker_start','marker_end'])
   between=bp.text[te:ms] if te<=ms else bp.text[me:ts] if me<=ts else None
   adjacent=between is not None and not between.strip()
   if 'intervening_text'in a:
    declared=a['intervening_text']
    if not isinstance(declared,str) or not 1<=len(declared)<=20 or '\n'in declared or '注'in declared or between!=declared:raise ValueError('Stale or unsafe exact note intervening text')
    adjacent=True
   if not (0<=ts<te<=len(bp.text) and 0<=ms<me<=len(bp.text) and adjacent) or bp.text[ts:te]!=a['term'] or bp.text[ms:me]!=a['marker']:raise ValueError('Stale inline note anchor')
   if ms in bound:raise ValueError('Duplicate inline note anchor')
   bound[ms]=a
  for marker in re.finditer(r'[（(]注\s*([0-9０-９]*(?:・[0-9０-９]+)*)[）)]',bp.text):
   anchor=bound.get(marker.start())
   labels=marker[1].split('・')
   if len(labels)>1:
    # Combined references need an explicit reviewed lexical span. Never infer
    # whether the longer definition term should absorb its shorter neighbour.
    if not anchor:continue
    if not 2<=len(labels)<=4 or len(set(labels))!=len(labels)or any(not label for label in labels):raise ValueError('Invalid combined note labels')
   if anchor and any(label not in definitions for label in labels):raise ValueError('Inline anchor has no note definition')
   if anchor:
    if anchor['marker_end']!=marker.end():raise ValueError('Stale inline note anchor')
    start,end=anchor['term_start'],anchor['term_end'];term=anchor['term']
   else:
    term=definitions.get(marker[1]);prefix=bp.text[:marker.start()].rstrip()
    if not term or not prefix.endswith(term):continue
    start=len(prefix)-len(term);end=len(prefix)
   crossing=[n for n,r in enumerate(bp.ruby) if any(r['start']<p<r['end'] for p in (start,end))]
   if crossing and isinstance(before,dict):
    ruby_nodes=BeautifulSoup(before['html'],'html.parser').find_all('ruby')
    if len(ruby_nodes)!=len(bp.ruby):raise ValueError('Note reference ruby structure changed')
    if all(ruby_nodes[n].get('data-rubi-origin')=='project_rubi_restore' and ruby_nodes[n].get('data-rubi-id') for n in crossing):
     # A suffix note (e.g. …証) can be shorter than a selected whole-word
     # reading. Keep the exact original marker beside that word; neither split
     # its ruby nor silently enlarge the bound lexical note anchor.
     self.features.append({'kind':'inline_note_reference_preserved','label':marker[0],'term':term,
      'term_start':start,'term_end':end,'marker_start':marker.start(),'marker_end':marker.end(),
      'ruby_ids':[ruby_nodes[n]['data-rubi-id'] for n in crossing],
      'basis':'Exact original reference retained because its lexical boundary is inside intact project ruby'})
     if anchor:used.add(marker.start())
     continue
   replacements.append({'term_start':start,'term_end':end,'term':term,
                        'marker_start':marker.start(),'marker_end':marker.end(),'marker':marker[0]})
   if anchor:used.add(marker.start())
   self.features.append({'kind':'inline_note_anchor','label':marker[0],'term':term,'basis':'observed projection-bound term span' if anchor else 'exact preceding term matches bound note definition'})
  if set(bound)!=used:raise ValueError('Unused inline note anchor')
  from note_markup import annotate
  return annotate(before,replacements,preserve_reference_containers=bool(getattr(self,'source_target_markers',False)))

 def with_notes(self,value,notes,context='body',underline_references=None):
  before,after=self.split_notes(value,notes)
  if notes.get('restored_anchors'):
   from passage_roles import restore_note_links
   before=restore_note_links(before,after,notes['restored_anchors'])
   for a in notes['restored_anchors']:self.features.append({'kind':'layout_symbol','text':a['label'],'basis':'restored link to existing note definition','term':a['term']})
  before=self.note_markers(before,after,notes.get('inline_anchors'))
  if underline_references:
   from section_layout import prepare_underline_references
   before=prepare_underline_references(before,underline_references)
  note_tex=self.notes_tex(after,notes.get('separate_definitions',False))
  body_tex=self.value(before,context)
  if notes.get('keep_marker_unbroken'):body_tex=self.unbroken_note_markers(body_tex)
  # Source-bound Old definitions already own their spacing and hanging
  # geometry. Do not add the generic minipage and NoteBefore a second time.
  # Vertical notes use vertical(); exterior framed notes retain their wrapper.
  if getattr(self,'source_target_markers',False) and context=='body' and not notes.get('frame_placement') and isinstance(after,dict):
   tail=BeautifulSoup(after['html'],'html.parser')
   roots=[n for n in tail.contents if str(n).strip()]
   if roots and all(isinstance(n,Tag) and n.name=='p' and n.get('data-historical-text-role')=='note' for n in roots):
    if notes.get('separate_definitions'):raise ValueError('Historical definition paragraphs already own their boundaries')
    self.features.append(dict(kind='historical_bound_note_tail',definitions=len(roots),generic_wrapper=False,canonical_changed=False))
    return body_tex+note_tex
  return body_tex+r'\begin{ReadingNotes}'+note_tex+r'\end{ReadingNotes}'

 def notes_tex(self,after,separate=False):
  """The same definition labels/colons serve horizontal and vertical bodies."""
  from note_definitions import presentation
  if isinstance(after,str) and not separate:
   # Preserve the established plain-field paragraph policy before adding the
   # semantic separator spans turns the field into rich HTML.
   after='\n'.join(x for x in re.split(r'\n+',after) if x.strip())
  after,_=presentation(after,separate)
  note_tex=self.value(after,'notes')
  note_tex=re.sub(OPEN_PAREN_TEX+r'[ \u3000]*注\s*('+numeric_token()+'|)'+r'[ \u3000]*'+CLOSE_PAREN_TEX,lambda m:r'\NoteDefinitionLabel{'+('注'+(r'\hspace{.16em}'+literal_digits(m[1])if m[1]else''))+'}',note_tex)
  return note_tex

 def unbroken_note_markers(self,tex):
  def wrap(m):
   self.features.append({'kind':'unbroken_note_marker','label':m[0],'basis':'selected note role; literal label kept as one typographic unit'})
   return r'\mbox{'+m[0]+'}'
  return re.sub(OPEN_PAREN_TEX+r'注\s*(?:'+numeric_token()+'|)'+CLOSE_PAREN_TEX,wrap,tex)

 def vertical(self,value,notes=None,flow=None,header=None,introduction=None,paired_style=None,paired_label=None):
  original_value=value
  if paired_label and (header or flow or introduction):raise ValueError('A standalone paired label cannot combine with another vertical prefix')
  if introduction and (flow or header):raise ValueError('Vertical introduction cannot combine with a flow or paired header')
  if header:
   from model import digest
   prefix=header['prefix']
   if not isinstance(value,str) or digest(value)!=header['content_sha256']:
    raise ValueError('Stale or unsupported vertical header binding')
   if not re.fullmatch(r'[ABＡＢ]\n[^\n]+\n\n',prefix) or not value.startswith(prefix):
    raise ValueError('Vertical header must bind an exact leading paired label and title')
   if flow:raise ValueError('Plain vertical header cannot use HTML flow')
  if flow:
   from vertical_flow import prepare
   value=prepare(value,flow)
  before,after=self.split_notes(value,notes) if notes else (value,None)
  if after is not None:before=self.note_markers(before,after,notes.get('inline_anchors'))
  if header:
   if not isinstance(before,str) or not before.startswith(prefix):raise ValueError('Vertical header changed during note preparation')
   body=before[len(prefix):]
   label,title=prefix.strip().split('\n')
   from paired_passages import parameters
   paired=parameters(paired_style)
   label_identity=label.translate(str.maketrans('ＡＢ','AB'))
   gap=paired['first_label_before_pt'] if label_identity=='A'else paired['next_label_before_pt']
   prefix_tex=r'{\PairedLabelLatin '+text_tex(label)+r'}\hspace{.6em}'+text_tex(title)
   header_before=(r'\clearpage'if label_identity in paired['new_page_before_labels']else
                  r'\par'+(r'\addvspace{'if label_identity=='A'else r'\vspace{')+str(gap)+'pt}')
   self.features.append({'kind':'vertical_horizontal_header','label':label,'title':title,'content_sha256':header['content_sha256'],'label_font_role':'paired_label','before_pt':0 if label_identity in paired['new_page_before_labels']else gap})
  elif paired_label:
   from model import digest
   from paired_passages import parameters
   label=paired_label['label']
   if label not in ['A','B'] or digest(value)!=paired_label['content_sha256'] or not isinstance(value,dict):
    raise ValueError('Stale or unsupported vertical paired label')
   soup=BeautifulSoup(before['html'],'html.parser')
   first=next((n for n in soup.contents if not isinstance(n,NavigableString) or n.strip()),None)
   if not isinstance(first,Tag) or first.name!='p' or first.get_text()!=label or first.find(True):
    raise ValueError('Vertical paired label must be an exact standalone first paragraph')
   first.decompose();body={'html':str(soup)}
   paired=parameters(paired_style)
   gap=paired['first_label_before_pt'] if label=='A' else paired['next_label_before_pt']
   prefix_tex=r'{\PairedLabelLatin '+text_tex(label)+'}'
   header_before=(r'\clearpage' if label in paired['new_page_before_labels'] else r'\par\addvspace{'+str(gap)+'pt}')
   self.features.append({'kind':'vertical_paired_label','label':label,'content_sha256':paired_label['content_sha256']})
  else:
   prefix=Projection(before).text.split('\n')[0].strip()
   number,body=remove_number(before)
   if number is None:raise ValueError('Vertical block requires an explicit leading label')
   prefix_tex=text_tex(prefix)
  intro_tex=''
  if introduction:
   from passage_roles import detach_vertical_introduction,introduction_tex
   intro,body=detach_vertical_introduction(body,introduction)
   intro_tex=introduction_tex(self,original_value,self.value(intro),introduction,notes).strip()
   self.features.append({'kind':'vertical_horizontal_introduction','text':introduction['text'],'projection_sha256':introduction['projection_sha256']})
  if isinstance(body,dict):
   soup=BeautifulSoup(body['html'],'html.parser')
   for wrapper in list(soup.find_all(['center','div'])):wrapper.unwrap()
   body={'html':str(soup)}
  saved_flow=getattr(self,'active_vertical_flow',False)
  saved_vertical=getattr(self,'active_vertical_body',False)
  self.active_vertical_flow=bool(flow)
  self.active_vertical_body=True
  try:tex=self.value(body)
  finally:self.active_vertical_flow=saved_flow;self.active_vertical_body=saved_vertical
  if notes and notes.get('keep_marker_unbroken'):tex=self.unbroken_note_markers(tex)
  tex=re.sub(r'^(?:\s*\\Para\s*)+|(?:\s*\\Para\s*)+$','',tex)
  result=(r'\VerticalIntroducedBlock{'+prefix_tex+'}{'+intro_tex+'}{'+tex+'}' if introduction
          else r'\VerticalBlock{'+prefix_tex+'}{'+tex+'}')
  if header or paired_label:result=header_before+result
  if after is not None:result+=r'\begin{ReadingNotes}'+self.notes_tex(after,notes.get('separate_definitions',False))+r'\end{ReadingNotes}'
  return result

 def table(self,t,context):
  artwork=getattr(self,'notice_table_asset',None)
  if artwork and context=='notice'and artwork['table_index']==self.table_index:
   self.notice_table_asset=None
   try:table=self.table(t,context)
   finally:self.notice_table_asset=artwork
   self.features.append({'kind':'table_side_artwork','semantic_table_index':artwork['table_index']})
   return r'\Para \noindent\begin{minipage}[b]{'+str(artwork['table_width_fraction'])+r'\linewidth}'+table+r'\end{minipage}\hfill\begin{minipage}[b]{'+str(artwork['width_fraction'])+r'\linewidth}\includegraphics[width=\linewidth]{'+artwork['absolute_path']+r'}\end{minipage}\Para '
  presentation=self.table_styles.get(str(self.table_index),{});self.table_index+=1
  allowed={'rule_style','width_fraction','align','column_weights','row_sep_pt','column_groups','group_gap_fraction','cell_flow','discount_pt','column_sep_pt','stub_align','column_alignments','vertical_cells','diagonal_header','panel_padding_pt','panel_radius_pt','panel_gap_pt','panel_title_pt','header_gray','rules','body_pt','baseline_pt','before_pt','after_pt','header_align','cell_styles','circled_bullet_gap_em','vertical_align','date_cells','row_separations','left_inset_pt'}
  allowed.update(['top_gap_pt','panel_lines','caption_style'])
  allowed.add('approved_duration')
  if set(presentation)-allowed:raise ValueError('Unknown table style property')
  if presentation.get('rule_style','grid') not in ['grid','row_groups','bands_with_stub','outer_box']:raise ValueError('Unsupported table rule style')
  if presentation.get('align','left') not in ['left','center']:raise ValueError('Unsupported table alignment')
  if not 0<presentation.get('width_fraction',1)<=1:raise ValueError('Invalid table width')
  rows=t.find_all('tr',recursive=False)
  if not rows:rows=[r for r in t.find_all('tr') if r.find_parent('table') is t]
  grid={};ncols=0
  for ri,row in enumerate(rows):
   ci=0
   for cell in row.find_all(['td','th'],recursive=False):
    while (ri,ci) in grid:ci+=1
    rs=int(cell.get('rowspan',1));cs=int(cell.get('colspan',1))
    grid[ri,ci]=(cell,rs,cs)
    for a in range(rs):
     for b in range(cs):
      if a or b:grid[ri+a,ci+b]=None
    ci+=cs;ncols=max(ncols,ci)
  if not ncols:return ''
  if 'column_groups' in presentation:
   groups=presentation['column_groups']
   if len(groups)<2 or [c for group in groups for c in group]!=list(range(ncols)):raise ValueError('Column groups must partition the semantic table in order')
   if any(v and (v[1]!=1 or v[2]!=1) for v in grid.values()):raise ValueError('Parallel grids do not accept spanning cells')
   gap=presentation.get('group_gap_fraction',.04)
   if not 0<=gap<=.15:raise ValueError('Invalid parallel table gap')
   width=presentation.get('width_fraction',1);part=(1-gap*(len(groups)-1))/len(groups)
   saved_styles=self.table_styles;saved_index=self.table_index;parts=[]
   try:
    for group in groups:
     nested=BeautifulSoup('<table></table>','html.parser').table
     for r in range(len(rows)):
      row=BeautifulSoup('<tr></tr>','html.parser').tr
      for c in group:row.append(BeautifulSoup(str(grid[r,c][0]),'html.parser').find(['td','th']))
      nested.append(row)
     child={k:v for k,v in presentation.items() if k not in ['column_groups','group_gap_fraction','column_weights','column_alignments']}
     child['width_fraction']=1;child['align']='left'
     if 'column_weights'in presentation:child['column_weights']=[presentation['column_weights'][c]for c in group]
     if 'column_alignments'in presentation:child['column_alignments']=[presentation['column_alignments'][c]for c in group]
     self.table_styles={str(saved_index):child};self.table_index=saved_index
     tex=self.table(nested,context)
     parts.append(r'\begin{minipage}[t]{'+str(part)+r'\linewidth}'+tex+r'\end{minipage}')
   finally:self.table_styles=saved_styles;self.table_index=saved_index
   self.features.append({'kind':'parallel_table','semantic_columns':ncols,'column_groups':groups,'semantic_table_index':saved_index-1})
   return r'\Para {\centering\begin{minipage}{'+str(width)+r'\linewidth}'+r'\hfill'.join(parts)+r'\end{minipage}\par}\Para '
  self.features.append({'kind':'table','rows':len(rows),'columns':ncols,'spans':[(r,c,v[1],v[2]) for (r,c),v in grid.items() if v and (v[1]>1 or v[2]>1)]})
  if presentation.get('cell_flow')=='transit_routes':
   from transit_routes import render
   return render(self,rows,grid,ncols,presentation)
  if presentation.get('cell_flow')=='contact_list':
   if ncols!=2 or any(v and (v[1]!=1 or v[2]!=1)for v in grid.values()):raise ValueError('Contact list requires two nonspanning semantic columns')
   lines=[]
   for r in range(len(rows)):
    a,b=(grid[r,c][0]for c in range(2))
    label=''.join(self.node(n,'cell')for n in a.children);value=''.join(self.node(n,'cell')for n in b.children)
    lines.append(r'\noindent {\bfseries '+label+r'}\hspace{1em}'+value+r'\par')
   self.features.append({'kind':'contact_list','semantic_rows':len(rows),'semantic_columns':2})
   return r'\Para \begin{NoticeFrame}[nobreak=true,skipabove=0pt,skipbelow=0pt,innertopmargin=3pt,innerbottommargin=3pt]'+''.join(lines)+r'\end{NoticeFrame}\Para '
  if presentation.get('cell_flow')=='notice_panels':
   if ncols!=2 or any(v and (v[1]!=1 or v[2]!=1)for v in grid.values()):raise ValueError('Notice panels require two nonspanning semantic columns')
   from section_layout import flow_lines
   panel_rows=[];panel_lines_used=[]
   for r in range(len(rows)):
    panels=[]
    for c in range(2):
     cell=copy.deepcopy(grid[r,c][0])
     for textnode in list(cell.find_all(string=True)):
      if textnode.parent.name not in ['rt','rp']and '　'in textnode:textnode.replace_with(str(textnode).replace('　',' '))
     nodes=flow_lines(list(cell.children));nodes=[n for n in nodes if Projection({'html':str(n)}).text.strip()]
     if not nodes or nodes[0].name!='center' or nodes[-1].name!='div':raise ValueError('Notice panel requires a leading title and trailing contact')
     title=nodes.pop(0);contact=nodes.pop();size=presentation.get('panel_title_pt',13)
     titletex=self.value({'html':title.decode_contents()},'notice');contacttex=self.value({'html':contact.decode_contents()},'notice')
     bodyparts=[]
     for n in nodes:
      plain=Projection({'html':str(n)}).text.strip();fragment={'html':n.decode_contents()}
      selected=[(idx,x)for idx,x in enumerate(presentation.get('panel_lines',[]))if x['row']==r and x['column']==c and x['text']==plain]
      if len(selected)>1:raise ValueError('Duplicate notice panel line')
      if selected:
       idx,entry=selected[0]
       panel_lines_used.append(idx)
       if entry.get('keep_words'):
        from inline_layout import prepare_inline
        from model import digest
        fragment=prepare_inline(fragment,{'content_sha256':digest(fragment),'groups':entry['keep_words']})
      if selected and 'continuation_before' in selected[0][1]:
       idx,entry=selected[0]
       from semantic_lines import split_before
       prefix=entry['continuation_before']
       if plain.count(prefix)!=1 or not prefix.startswith('③') or not plain.startswith('【見学時間】'):raise ValueError('Invalid exact notice time continuation')
       chunks=split_before([fragment['html']],[prefix])
       if len(chunks)!=2:raise ValueError('Notice time continuation must have two lines')
       label='【見学時間】'
       first=self.value({'html':chunks[0]},'notice');second=self.value({'html':chunks[1]},'notice')
       if not first.startswith(label):raise ValueError('Notice time label changed')
       # A measured native label box aligns the continuation under ①, even
       # when the label face/size or its canonical separator space changes.
       leading=first[len(label):];gap=r'\hspace{.35em}'
       bodyparts.append(r'{\noindent '+label+gap+leading.lstrip()+r'\par\noindent\hphantom{'+label+'}'+gap+second+r'\par}')
       continue
      part=self.value(fragment,'notice')
      count_label='【見学できる人の数】'
      if plain.startswith(count_label):part=part.replace(count_label,count_label+r'\par\noindent\hspace{1em}',1)
      elif not plain.startswith('【'):part=r'\hspace{1em}'+part
      bodyparts.append(r'{\hangindent=1em\hangafter=1\noindent '+part+r'\par}')
     body=''.join(bodyparts)
     panels.append(r'{\centering\fontsize{'+str(size)+'}{'+str(size*1.4)+r'}\selectfont '+titletex+r'\par}\vspace{6pt}'+body+r'\par\vfill\vspace{5pt}{\raggedleft '+contacttex+r'\par}')
    panel_rows.append(r'\NoticePanelRow{'+str(presentation.get('panel_gap_pt',10))+'}{'+str(presentation.get('panel_radius_pt',12))+'}{'+str(presentation.get('panel_padding_pt',9))+'}{'+panels[0]+'}{'+panels[1]+'}')
   self.features.append({'kind':'notice_panels','rows':len(rows),'columns':2})
   if sorted(panel_lines_used)!=list(range(len(presentation.get('panel_lines',[])))):raise ValueError('Unused notice panel line')
   return r'\Para '+(r'\par\vspace{'+str(presentation.get('panel_gap_pt',10))+r'pt}').join(panel_rows)+r'\Para '
  # Content-derived proportions; semantic table data never flattened to images.
  weights=[1.0]*ncols
  for (r,c),v in grid.items():
   if v and v[2]==1:
    txt=Projection({'html':str(v[0])}).text.strip();width=max((len(x) for x in txt.splitlines()),default=1)
    weights[c]=max(weights[c],min(12,math.sqrt(max(1,width))))
  if 'column_weights' in presentation:
   weights=presentation['column_weights']
   if len(weights)!=ncols or any(w<=0 for w in weights):raise ValueError('Table column weights mismatch')
  isexample=context in ['example','star_solution'];answer=context=='example' and len(rows)==1
  star=context=='star_solution'
  saved_word_space=self.word_space_em
  if star:self.word_space_em=getattr(self,'star_cell_word_space_em',self.word_space_em)
  elif context=='notice':self.word_space_em=getattr(self,'notice_cell_word_space_em',self.word_space_em)
  if star:
   first=Projection({'html':str(grid[0,0][0])}).text.strip();last=Projection({'html':str(grid[0,ncols-1][0])}).text.strip()
   weights=[max(4,len(first)+2)]+[5.5]*(ncols-2)+[max(4,len(last)+1)]
   if len(rows)==1:
    # A solved sentence has words and choice labels in one row, rather than
    # the separate blank/answer rows of a worked STAR diagram.
    weights=[max(2.5,.6+sum(.3 if ch.isspace() else .5 if ch.isascii() else 1 for ch in Projection({'html':str(grid[0,c][0])}).text.strip())) for c in range(ncols)]
  if answer:weights=[2]+[1]*(ncols-1)
  aligns=presentation.get('column_alignments',['center'if idx==0 and presentation.get('stub_align')=='center'else'left'for idx in range(ncols)])
  if len(aligns)!=ncols or any(x not in ['left','center','right']for x in aligns):raise ValueError('Table column alignments mismatch')
  spec=' '.join(f'X[{w:.3f},{("r" if idx==0 else "l" if idx==ncols-1 else "c") if star else {"left":"l","center":"c","right":"r"}[aligns[idx]]}]' for idx,w in enumerate(weights))
  unbroken_edges=star and t.get('data-star-unbroken-edges')=='true'
  if unbroken_edges:
   if ncols!=6 or len(rows)<2 or max(len(first),len(last))>12 or any(grid.get((r,0))is None or grid[r,0][1:]!=(1,6)for r in range(2,len(rows))):raise ValueError('Unbroken STAR edges require short six-column sentence fragments and spanning support rows')
   # Natural-width sentence edges leave the four native slots equal widths.
   # This avoids splitting あります into unrelated vertical fragments.
   spec='Q[r] '+' '.join('X[1,c]'for _ in range(4))+' Q[l]'
   if t.get('data-star-keep-choices')=='true':
    spec='Q[r,leftsep=21pt] '+' '.join('X[1,c]'for _ in range(4))+' Q[l,rightsep=21pt]'
  settings='width=\\linewidth,hspan=minimal,colspec={'+spec+'},colsep=3pt,rowsep=4pt,cells={valign=m},hline{1,Z}={.45pt}'
  if presentation.get('vertical_align'):
   if presentation['vertical_align']!='top':raise ValueError('Unsupported table vertical alignment')
   settings+=',cells={valign=t}'
  if not isexample:
   if 'rules' in presentation:
    from rules import table_settings
    settings=settings.replace(',hline{1,Z}={.45pt}','')
    rule_settings=table_settings(presentation['rules'],len(rows),ncols)
    self.features.append({'kind':'table_rules','table_index':self.table_index-1,'rules':presentation['rules']})
   else:rule_settings=None
   settings+=',colsep='+str(presentation.get('column_sep_pt',3))+'pt,width='+str(presentation.get('width_fraction',1))+r'\linewidth,rowsep='+str(presentation.get('row_sep_pt',4))+'pt'
   if rule_settings is not None:settings+=rule_settings
   elif presentation.get('rule_style')=='bands_with_stub':settings+=',hlines={.58pt},vline{2}={.58pt}'
   elif presentation.get('rule_style')=='outer_box':settings+=',vline{1,Z}={.58pt}'
   elif presentation.get('rule_style')=='row_groups':
    starts=[r+1 for (r,c),v in grid.items() if v and v[0].get('scope')=='rowgroup']
    if not starts:raise ValueError('Row-group rules require explicit rowgroup headers')
    settings+=',hline{'+','.join(map(str,sorted(set(starts+[len(rows)+1]))))+'}={.58pt}'
   else:settings+=',hlines={.58pt},vlines={.58pt}'
  elif answer:settings+=',vlines={.35pt}'
  else:settings+=',hline{1,Z}={.35pt},vline{1,Z}={.35pt}'
  table_font=''
  if not isexample and (context!='notice' or 'baseline_pt'in presentation) and hasattr(self,'table_baseline_pt'):
   sz=presentation.get('body_pt',self.table_body_pt);leading=presentation.get('baseline_pt',self.table_baseline_pt)
   settings+=',cells={font=\\fontsize{'+str(sz)+'}{'+str(leading)+r'}\selectfont}'
   # tabularray captures the surrounding strut before applying cells.font.
   # Set the same font outside it so compact tables do not inherit body leading.
   table_font=r'\fontsize{'+str(sz)+'}{'+str(leading)+r'}\selectfont '
  if 'header_gray'in presentation:
   gray=presentation['header_gray']
   if isexample or not 0<=gray<=1 or any(v and v[0].name!='th'for (r,c),v in grid.items()if r==0):raise ValueError('Shaded header requires an explicit semantic header row')
   settings+=',row{1}={bg=black!'+str(round((1-gray)*100,3))+'}'
  if star:settings+=',width=\\StarBoxWidth\\linewidth,rowsep=\\StarRowSep,cells={font=\\fontsize{\\BodySize}{\\StarRowBaseline}\\selectfont},row{1}={abovesep=\\StarBoxPadding,belowsep=\\StarSlotBelow},row{Z}={belowsep=\\StarBottomPadding}'
  if star and len(rows)>2:settings+=',row{3}={abovesep=\\StarDialogueBefore}'
  if star and t.get('data-star-keep-choices')=='true':settings+=',column{1}={leftsep=21pt},column{Z}={rightsep=21pt}'
  if 'header_align'in presentation:
   if presentation['header_align']!='center':raise ValueError('Unsupported table header alignment')
   settings+=',row{1}={halign=c}'
  seen_rows=set()
  for entry in presentation.get('row_separations',[]):
   row=entry['row']
   if isinstance(row,bool)or not isinstance(row,int)or not 0<=row<len(rows)or row in seen_rows:raise ValueError('Invalid or duplicate table row separation')
   seen_rows.add(row)
   if any(isinstance(entry[k],bool)or not isinstance(entry[k],(int,float))or not 0<=entry[k]<=20 for k in ['above_pt','below_pt']):raise ValueError('Invalid row separation dimension')
   settings+=',row{'+str(row+1)+'}={abovesep='+str(entry['above_pt'])+'pt,belowsep='+str(entry['below_pt'])+'pt}'
  out=[];vertical_used=[];styled_used=[];date_used=[];star_measured_cells={}
  for r in range(len(rows)):
   cells=[]
   for c in range(ncols):
    v=grid.get((r,c))
    if not v:cells.append('');continue
    cell,rs,cs=v
    bound=[(idx,entry)for idx,entry in enumerate(presentation.get('cell_styles',[]))if entry['row']==r and entry['column']==c]
    if len(bound)>1:raise ValueError('Duplicate table cell style')
    from table_roles import alignment as cell_alignment
    align_role=None
    if not isexample:
     semantic_alignment,align_role=cell_alignment(cell,Projection({'html':str(cell)}).text,r,c,presentation,aligns[c],bound[0][1]if bound else None,
        getattr(self,'table_header_align','center'),getattr(self,'table_mark_align','center'))
     if semantic_alignment not in ['left','center','right']:raise ValueError('Invalid semantic table alignment')
     settings+=',cell{'+str(r+1)+'}{'+str(c+1)+'}={halign='+{'left':'l','center':'c','right':'r'}[semantic_alignment]+'}'
     self.features.append({'kind':'semantic_table_alignment','table_index':self.table_index-1,'row':r,'column':c,'rowspan':rs,'colspan':cs,'role':align_role,'alignment':semantic_alignment})
    children=cell.children
    if bound and bound[0][1].get('keep_words'):
     entry=bound[0][1];plain=Projection({'html':str(cell)}).text.strip()
     if plain!=entry['text']:raise ValueError('Stale table cell style')
     for word in entry['keep_words']:
      if plain.count(word)!=1:raise ValueError('Bounded table word must occur once in its exact cell')
     from inline_layout import prepare_inline
     from model import digest
     fragment={'html':cell.decode_contents()}
     grouped=prepare_inline(fragment,{'content_sha256':digest(fragment),'groups':entry['keep_words']})
     children=BeautifulSoup(grouped['html'],'html.parser').children
    child_list=list(children);cell_parts=[]
    # Bound line-role cells are emitted below from their exact rich fragments.
    # Do not first render and discard the same glyphs with default line roles.
    for child_index,n in enumerate([] if bound and 'line_indents_em' in bound[0][1] else child_list):
     if bound and bound[0][1].get('keep_words') and isinstance(n,Tag) and n.has_attr('data-bounded-word') and child_index:
      preceding=Projection({'html':''.join(map(str,child_list[:child_index]))}).text.rstrip()
      if preceding.endswith(('、','，',',','；',';','／','/')):
       # Adjacent native boxes otherwise suppress the legal break after a
       # list separator. Keep the separator attached to the previous date.
       cell_parts.append(r'\allowbreak{}')
       self.features.append({'kind':'kept_table_separator_break','row':r,'column':c})
     saved_notice_cell=getattr(self,'native_notice_cell',False)
     self.native_notice_cell=context=='notice'
     try:cell_parts.append(self.node(n,'cell'))
     finally:self.native_notice_cell=saved_notice_cell
    body=''.join(cell_parts).strip()
    body=re.sub(r'^(?:\\Para\s*)+|(?:\\Para\s*)+$','',body)
    body=body.replace(r'\Para ',r'\par ') # Cell line breaks must not inherit surrounding notice paragraph glue.
    if bound:
     idx,entry=bound[0];plain=Projection({'html':str(cell)}).text.strip()
     if plain!=entry['text']:raise ValueError('Stale table cell style')
     if 'align' in entry:
      alignment={'left':'l','center':'c','right':'r'}.get(entry['align'])
      if alignment is None:raise ValueError('Unknown bound cell alignment')
      settings+=',cell{'+str(r+1)+'}{'+str(c+1)+'}={halign='+alignment+'}'
     if 'background_gray' in entry:
      gray=entry['background_gray']
      if isexample or cell.name!='th' or isinstance(gray,bool)or not isinstance(gray,(int,float))or not 0<=gray<=1:raise ValueError('Local fill requires an exact semantic header cell')
      settings+=',cell{'+str(r+1)+'}{'+str(c+1)+'}={bg=black!'+str(round((1-gray)*100,3))+'}'
      self.features.append({'kind':'bound_header_fill','row':r,'column':c,'gray':gray})
     if 'vertical_align' in entry:
      if isexample or entry['vertical_align']!='top':raise ValueError('Unsupported bound cell vertical alignment')
      settings+=',cell{'+str(r+1)+'}{'+str(c+1)+'}={valign=t}'
     if 'line_indents_em'in entry:
      from notice_layout import html_lines
      chunks=html_lines(cell.decode_contents(),entry.get('break_before'));indents=entry['line_indents_em']
      if len(chunks)!=len(indents):raise ValueError('Table cell line count changed')
      hanging=entry.get('line_hanging_em',[0]*len(chunks));families=entry.get('line_font_families',['body']*len(chunks));spaces=entry.get('line_before_pt',[0]*len(chunks))
      if any(len(x)!=len(chunks)for x in [hanging,families,spaces]):raise ValueError('Table cell line role count changed')
      if set(families)-{'body','notice_body','heading'}:raise ValueError('Unknown bound cell line font')
      parts=[]
      for line_index,(chunk,indent,hang,family,before) in enumerate(zip(chunks,indents,hanging,families,spaces)):
       if entry.get('normalize_line_starts'):
        fragment=BeautifulSoup(chunk,'html.parser')
        for node in list(fragment.descendants):
         if not isinstance(node,NavigableString)or node.parent.name in ['rt','rp']:continue
         raw=str(node);node.replace_with(raw.lstrip(' \u3000\t'))
         if raw.strip(' \u3000\t'):break
        chunk=str(fragment)
       face={'notice_body':r'\NoticeBodyJapanese ','heading':r'\sffamily\gtfamily ','body':''}[family]
       if family=='heading':self.features.append({'kind':'bound_cell_line_heading','row':r,'column':c,'text':Projection({'html':chunk}).text.strip()})
       # Initial strut must not become an empty line in the measurement pass.
       gap=(r'\ifhmode\else\addvspace{'+str(before)+r'pt}\fi')if parts else''
       column=entry.get('line_label_column')
       if column and line_index in [column['start_line'],*column['continuation_lines']]:
        from example_layout import slice_inline
        text=Projection({'html':chunk}).text;label=column['label'];width=column['width_em'];start=len(text)-len(text.lstrip())
        if line_index==column['start_line']:
         if not text[start:].startswith(label):raise ValueError('Cell label column changed')
         labeltex=self.value({'html':slice_inline(chunk,start,start+len(label))},'cell')
         content=r'\makebox['+str(width)+r'em][l]{'+labeltex+'}'+self.value({'html':slice_inline(chunk,start+len(label),len(text))},'cell')
        else:content=r'\hspace*{'+str(width)+'em}'+self.value({'html':chunk},'cell')
        indent=0;hang=width
       else:content=self.value({'html':chunk},'cell')
       parts.append(gap+'{'+face+r'\advance\leftskip by '+str(indent)+r'em\relax\hangindent='+str(hang)+r'em\hangafter=1\noindent '+content+r'\par}')
      body=''.join(parts)
     elif any(k in entry for k in ['line_hanging_em','line_font_families','line_before_pt']):raise ValueError('Cell line roles require explicit line indents')
     if any(k in entry for k in ['normalize_line_starts','break_before']) and 'line_indents_em'not in entry:raise ValueError('Line-start presentation requires bound line indents')
     if entry.get('keep_time_ranges'):
      time_pattern=r'[0-9０-９]{1,2}[:：][0-9０-９]{2}[～〜\-][0-9０-９]{1,2}[:：][0-9０-９]{2}'
      if not re.search(time_pattern,plain):raise ValueError('Time-range role has no existing range')
      for match in re.finditer(time_pattern,plain):
       fragment=self.text(match[0])
       if body.count(fragment)!=1:raise ValueError('Time range must reach one native table span')
       body=body.replace(fragment,r'\mbox{'+fragment+'}',1)
     if entry.get('aligned_duration'):
      match=re.fullmatch(r'(?:(\d+)分)?(\d+)秒',plain)
      if not match or cell.find('ruby'):raise ValueError('Duration columns require unchanged plain minute/second values')
      minute=match[1]or'';second=match[2]
      body=r'\mbox{\makebox[.7em][r]{'+self.text(minute)+r'}\makebox[1em][c]{'+('分'if minute else'')+r'}\makebox[1.2em][r]{'+self.text(second)+r'}\makebox[1em][c]{秒}}'
      self.features.append({'kind':'aligned_duration','row':r,'column':c,'text':plain})
     if entry.get('aligned_money'):
      match=re.fullmatch(r'([0-9]+(?:,[0-9]{3})*)\s*円',plain)
      if not match or cell.find('ruby'):raise ValueError('Money columns require an exact plain amount and 円')
      width=entry.get('amount_width_em',3)
      if isinstance(width,bool)or not isinstance(width,(int,float))or not 1<=width<=8:raise ValueError('Invalid money column width')
      body=r'\mbox{\makebox['+str(width)+r'em][r]{'+self.text(match[1])+r'}\hspace{.12em}円}'
      self.features.append({'kind':'aligned_money','table_index':self.table_index-1,'row':r,'column':c,'text':plain,'amount_width_em':width})
     for word in entry.get('keep_words',[]):
      self.features.append({'kind':'kept_table_word','row':r,'column':c,'text':word})
     if 'document_bullet'in entry:
      if isexample or context!='notice':raise ValueError('Document bullet cannot affect an answer strip or ordinary table')
      from document_bullets import present
      body,hang=present(self,plain,body,entry['document_bullet'],'notice_cell')
      body=r'{\hangindent='+str(hang)+r'em\hangafter=1 '+body+r'\par}'
     if 'body_pt'in entry or 'baseline_pt'in entry:
      if not all(k in entry and not isinstance(entry[k],bool)and isinstance(entry[k],(int,float))and 6<=entry[k]<=36 for k in ['body_pt','baseline_pt']):raise ValueError('Cell font and baseline must be specified together')
      settings+=',cell{'+str(r+1)+'}{'+str(c+1)+'}={font=\\fontsize{'+str(entry['body_pt'])+'}{'+str(entry['baseline_pt'])+r'}\selectfont}'
     if 'ruby_intergap_em'in entry:
      gap=entry['ruby_intergap_em']
      if isinstance(gap,bool)or not isinstance(gap,(int,float))or not 0<=gap<=.3 or not cell.find('ruby'):raise ValueError('Invalid bound cell ruby clearance')
      body=r'{\ltjsetruby{intergap='+str(gap)+'}'+body+'}'
     styled_used.append(idx)
    dates=[(idx,x)for idx,x in enumerate(presentation.get('date_cells',[]))if x['row']==r and x['column']==c]
    if len(dates)>1 or (dates and bound):raise ValueError('Duplicate or conflicting date cell style')
    if dates:
     from table_dates import anchored_dates
     idx,binding=dates[0];body=anchored_dates(self,cell,binding);date_used.append(idx)
    if presentation.get('circled_bullet_gap_em'):
     body=re.sub(r'([①②③④⑤⑥])(?=[^\s])',lambda m:m[1]+r'\hspace{'+str(presentation['circled_bullet_gap_em'])+'em}',body)
    if presentation.get('cell_flow')=='sale_prices' and c>0:
     if len(cell.find_all(['s','del']))!=1 or body.count('⇒')!=1:raise ValueError('Sale cell requires one old price and one literal discount arrow')
     old,new=body.split('⇒')
     body=old+r'\par {\fontsize{'+str(presentation['discount_pt'])+'}{'+str(presentation['discount_pt']*1.4)+r'}\selectfont ⇒'+new+r'\par}'

    vertical=[(idx,x)for idx,x in enumerate(presentation.get('vertical_cells',[]))if x['row']==r and x['column']==c]
    if len(vertical)>1:raise ValueError('Duplicate vertical table cell')
    if vertical:
     idx,vstyle=vertical[0];plain=Projection({'html':str(cell)}).text.strip()
     if plain!=vstyle['text']or cell.find('ruby')or not re.fullmatch(r'[ぁ-んァ-ヶ一-龥]{2,8}',plain):raise ValueError('Vertical cell must match a short existing plain label')
     body=r'\par '.join(self.text(ch)for ch in plain);vertical_used.append(idx)
    if presentation.get('diagonal_header')and r==0 and c==0:
     from notice_layout import html_lines
     pieces=html_lines(cell.decode_contents())
     if len(pieces)!=2 or cs<2:raise ValueError('Diagonal header requires two existing labels in a spanning first cell')
     # Width follows the selected table/column geometry, including colspan padding.
     frac=presentation.get('width_fraction',1)*sum(weights[:cs])/sum(weights);sep=presentation.get('column_sep_pt',3)
     correction=2*sep*(ncols*sum(weights[:cs])/sum(weights)-(cs-1))
     dim=r'\linewidth'
     matcher=type(self)(self.assets,source_base=self.source_base,word_space_em=self.word_space_em)
     top,bottom=(matcher.value({'html':p},'cell')for p in pieces)
     body=r'\NoticeDiagonalHeader{'+dim+'}{'+top+'}{'+bottom+'}{'+str(sep)+'pt}'
     self.features.append({'kind':'diagonal_header','semantic_row':r,'semantic_column':c,'colspan':cs})

    if isexample and not answer and not (star and len(rows)==1):
     # A cell containing only an underlined STAR is one blank, not an
     # underline around a second native blank (which creates stray strokes).
     if re.fullmatch(r'\s*★\s*',Projection({'html':str(cell)}).text) and cell.find('u'):
      body=r'\StarSlot{}'
     else:body=body.replace('★',r'\StarSlot{}')
     if star:body=body.replace(r'\Slot{}',r'\WideSlot{}').replace(r'\StarSlot{}',r'\WideStarSlot{}')
    if star and cs==ncols and r>1:
     if re.match(r'^[A-ZＡ-Ｚ]\s*[「｢]',Projection({'html':str(cell)}).text.strip()):
      body=r'{\StarSupportingFont '+body+'}'
      self.features.append({'kind':'star_supporting_dialogue','row':r,'font_role':'regular_body','text':Projection({'html':str(cell)}).text})
     if t.get('data-star-keep-choices')!='true':body=r'\hspace*{1.5em}'+body
    if star:
     # Converted beginner word-space glue after the label already represents
     # the same separator. Consume it before adding the one numeral gutter;
     # leave word-space glue inside the answer unchanged.
     body=re.sub(r'^(★(?:\s|\\hskip [0-9.]+em\\relax\s*)*)?('+numeric_token('[1-4]')+r')(?:\s|\\hskip [0-9.]+em\\relax\s*)*',lambda m:(m[1]or'')+r'{\ChoiceNumerals '+literal_digits(m[2])+r'}\hspace{.3em}',body)
     if unbroken_edges and r<2 and c in [0,ncols-1]:body=r'\mbox{'+body+'}'
     if t.get('data-star-keep-choices')=='true' and r==1 and c in [1,2,3,4]:body=r'\mbox{'+body+'}'
     if t.get('data-star-keep-choices')=='true' and ((r==0 and c in [0,ncols-1]) or (r==1 and c in [1,2,3,4])):
      star_measured_cells[r,c]=body
     if len(rows)==1:
      body=r'\mbox{'+body+'}'
      self.features.append({'kind':'single_row_star_solution_cell','column':c,'text':Projection({'html':str(cell)}).text.strip()})
    span=(r'\SetCell[r='+str(rs)+',c='+str(cs)+(']{l,t}' if presentation.get('rule_style')=='row_groups' and cell.get('scope')=='rowgroup' else ']{l}') if rs>1 or cs>1 else '')
    if span and 'column_alignments'in presentation:span=span.replace(']{l}',']{'+{'left':'l','center':'c','right':'r'}[aligns[c]]+'}')
    if span and bound and 'align' in bound[0][1]:
     span=re.sub(r'\]\{[lcr]\}',']{'+{'left':'l','center':'c','right':'r'}[bound[0][1]['align']]+'}',span)
    if span and not isexample:
     valign=',t'if presentation.get('vertical_align')=='top' or (bound and bound[0][1].get('vertical_align')=='top')else''
     span=r'\SetCell[r='+str(rs)+',c='+str(cs)+']{'+{'left':'l','center':'c','right':'r'}[semantic_alignment]+valign+'}'
    if presentation.get('rule_style')=='row_groups' and cell.get('scope')=='rowgroup':span='' # visual label sits in the first row; semantic rowspan remains in the model/audit
    if star and r==0 and rs>1 and cs==1 and c in [0,ncols-1]:
     # The semantic span relates the sentence to both solution rows. Its ink
     # belongs beside the blanks, so retain left alignment in the first row.
     span=r'\SetCell{l}'
     self.features.append({'kind':'star_flank_first_visual_row','semantic_rowspan':rs,'column':c})
    # No automatic bold on all table headers: accepted source typography is restrained.
    cells.append(span+'{'+body+'}')
   out.append(' & '.join(cells)+r' \\')
  if sorted(vertical_used)!=list(range(len(presentation.get('vertical_cells',[])))):raise ValueError('Unused vertical table cell')
  if sorted(styled_used)!=list(range(len(presentation.get('cell_styles',[])))):raise ValueError('Unused table cell style')
  if sorted(date_used)!=list(range(len(presentation.get('date_cells',[])))):raise ValueError('Unused date cell style')
  self.word_space_em=saved_word_space
  cap=t.find('caption',recursive=False);caption=self.value({'html':cap.decode_contents()},'body') if cap else ''
  prefix=r'\Para '+caption+r'\Para ' if cap else r'\Para '
  if not isexample and (context!='notice' or 'before_pt' in presentation):prefix=r'\Para \vspace{'+str(presentation.get('before_pt',0 if context=='notice' else 6))+r'pt}\noindent '+caption
  question_owner=t.get('data-question-display-owner')
  if question_owner and context=='body' and not isexample:
   owns_gap=any(k in presentation for k in ['before_pt','top_gap_pt','caption_style'])
   if not owns_gap:
    prefix=r'\Para \vspace{'+str(self.question_table_before_pt)+r'pt}\noindent '+caption
   self.features.append({'kind':'question_table_clearance','target':question_owner,
      'gap_owner':'explicit_table_presentation' if owns_gap else 'era_question_boundary',
      'before_pt':presentation.get('before_pt',presentation.get('top_gap_pt',presentation.get('caption_style',{}).get('before_pt',0))) if owns_gap else self.question_table_before_pt,
      'canonical_changed':False})
  if 'top_gap_pt'in presentation:
   gap=presentation['top_gap_pt']
   if isexample or 'before_pt'in presentation or isinstance(gap,bool)or not isinstance(gap,(int,float))or not 0<=gap<=30:raise ValueError('Invalid table top gap')
   prefix=r'\par\vspace{'+str(gap)+r'pt}\noindent '+caption
  if 'caption_style' in presentation:
   bound=presentation['caption_style']
   if isexample or not cap or Projection({'html':cap.decode_contents()}).text.strip()!=bound['text']:
    raise ValueError('Native table caption requires its exact existing caption')
   if set(bound)-{'text','align','font_pt','baseline_pt','before_pt','after_pt','boxed','font_family'}:
    raise ValueError('Unknown native caption property')
   if bound.get('font_family','body')not in ['body','heading']:raise ValueError('Unknown native caption font role')
   if bound.get('font_family')=='heading':caption=r'{\sffamily\gtfamily\bfseries '+caption+'}'
   title=r'{\fontsize{'+str(bound['font_pt'])+'}{'+str(bound['baseline_pt'])+r'}\selectfont '+caption+'}'
   if bound.get('boxed'):title=r'{\setlength\fboxsep{6pt}\setlength\fboxrule{.5pt}\fbox{'+title+'}}'
   alignment={'left':r'\raggedright ','center':r'\centering ','right':r'\raggedleft '}[bound['align']]
   prefix=r'\par\vspace{'+str(bound.get('before_pt',0))+r'pt}{'+alignment+r'\noindent '+title+r'\par}\nobreak\vspace{'+str(bound.get('after_pt',6))+r'pt}\noindent '
   self.features.append({'kind':'native_table_caption','text':bound['text'],'align':bound['align'],'boxed':bool(bound.get('boxed'))})
  if answer:return prefix+r'{\begin{minipage}{.53\linewidth}\begin{tblr}{'+settings+'}\n'+'\n'.join(out)+r'\end{tblr}\end{minipage}}\Para '
  if not star and presentation.get('align')=='center':prefix+=r'{\centering '
  if 'left_inset_pt'in presentation:
   inset=presentation['left_inset_pt']
   if isexample or presentation.get('align')=='center' or isinstance(inset,bool)or not isinstance(inset,(int,float))or not 0<=inset<=40:raise ValueError('Invalid table left inset')
   prefix+=r'\hspace*{'+str(inset)+'pt}'
  if star:
   prefix+=r'\vspace{\StarFrameBefore}{\StarTableAlignment '
   if t.get('data-star-keep-choices')=='true':
    order=[(0,0),(0,ncols-1),*( (1,c) for c in [1,2,3,4])]
    if set(star_measured_cells)!=set(order):raise ValueError('Missing measured STAR fragment')
    prefix+=r'\MeasureStarSolution'+''.join('{'+star_measured_cells[k]+'}'for k in order)
    settings=settings.replace(r'width=\StarBoxWidth\linewidth',r'width=\StarEffectiveWidth')
    self.features.append({'kind':'measured_star_solution_width','equal_middle_columns':4,
      'minimum_basis':'Native widths of both sentence edges and widest numbered choice or star glyph, with existing 21pt outer insets and 3pt column padding.',
      'declared_width_is_minimum':True,'maximum':'current linewidth'})
  table_tex=r'\begin{tblr}{'+settings+'}\n'+'\n'.join(out)+r'\end{tblr}'
  if table_font:table_tex='{'+table_font+table_tex+'}'
  if not isexample and 'after_pt'in presentation:
   # End the table paragraph before exterior glue. Para ends with noindent;
   # putting vspace after it creates a spurious empty line at the next par.
   close=r'\par}'if presentation.get('align')=='center'else r'\par'
   return prefix+table_tex+close+r'\vspace{'+str(presentation['after_pt'])+r'pt}\Para '
  after=r'\vspace{'+str(presentation.get('after_pt',0 if context=='notice' else 6))+'pt}' if not isexample and (context!='notice' or 'after_pt' in presentation) else ''
  return prefix+table_tex+(r'\par}\vspace{\StarSolutionAfter}' if star else (r'\par}\Para ' if presentation.get('align')=='center' else r'\Para ')+after)


def context_frames(tex,task,frame_style='box',explicit=False,paired_style=None,notes_outside=False):
 """Frame existing content boundaries; allow a recorded per-item style override."""
 if notes_outside:
  begin,end=r'\begin{ReadingNotes}',r'\end{ReadingNotes}'
  if task!='reading' or tex.count(begin)!=1 or tex.count(end)!=1:
   raise ValueError('Exterior reading notes require one complete bound cluster')
  body,tail=tex.split(begin)
  notes,after=tail.split(end)
  if not body.strip() or not notes.strip() or re.sub(r'\\(?:Para|EmailLine)\s*','',after).strip():
   raise ValueError('Exterior reading notes must be the complete document tail')
  framed,rule=context_frames(body,task,frame_style,explicit,paired_style)
  return framed+r'\Para '+begin+notes+end,rule+'_bound_notes_outside'
 start,end=r'\ExteriorCitationStart{}',r'\ExteriorCitationEnd{}'
 if start in tex or end in tex:
  if task not in ['cloze','paired_reading'] or r'\ObservedSection{' in tex:
   raise ValueError('Exterior citation requires a cloze or paired context frame')
  body,marker,notes=tex.partition(r'\begin{ReadingNotes}')
  body=re.sub(r'(?:\s*\\Para\s*)+$','',body).strip()
  if body.count(start)!=1 or body.count(end)!=1 or not body.endswith(end):
   raise ValueError('Exterior citation must be the complete passage tail before notes')
  body,citation=body[:-len(end)].split(start)
  if not body.strip():raise ValueError('Exterior citation requires a preceding passage')
  framed,rule=context_frames(body,task,frame_style,explicit,paired_style)
  return framed+citation+(r'\Para '+marker+notes if marker else ''),rule+'_bound_citation_outside'
 if r'\ObservedSection{' in tex:return tex,'source_bound_semantic_sections'
 if r'\KeepClozePanel{' in tex:return tex,'source_bound_cloze_panel_headers'
 if frame_style not in ['box','horizontal_rules','none']:raise ValueError('Unsupported context frame style: '+str(frame_style))
 # Semantic paired roles must run before generic HTML border early returns.
 # A source-bound note cluster is outside the paired bodies in every encoding.
 if task=='paired_reading':
  from paired_passages import render as paired_render
  body,marker,notes=tex.partition(r'\begin{ReadingNotes}')
  framed,rule=paired_render(body,frame_style,paired_style)
  return (framed+r'\Para '+marker+notes,rule+'_notes_outside')if marker else(framed,rule)
 env='RuleFrame'if frame_style=='horizontal_rules'else 'ClozeFrame' if task=='cloze' and frame_style=='box' else 'PairedFrame'if task=='paired_reading'else 'NoticeFrame'
 def frame(body):
  if frame_style=='none':return body
  if env=='ClozeFrame':
   first=re.sub(r'^(?:\s*\\Para\s*)+','',body)
   # A centered title or right-aligned author is already an explicit local
   # line role. Its following paragraph receives the normal paragraph indent.
   # An ordinary first body paragraph needs the same indent in either encoding.
   if not first.startswith((r'{\centering ',r'{\raggedleft ',r'\begin{center}',r'\begin{flushright}')):
    body=r'\hspace*{1em}'+first
  return r'\begin{'+env+'}'+body+r'\end{'+env+'}'
 if r'\begin{RuleFrame}' in tex:return tex,'explicit_html_horizontal_rules'
 if r'\begin{NoticeFrame}' in tex:
  if frame_style=='none':tex=tex.replace(r'\begin{NoticeFrame}','').replace(r'\end{NoticeFrame}','')
  elif frame_style=='horizontal_rules':tex=tex.replace('NoticeFrame','RuleFrame')
  elif task=='cloze':
   tex=re.sub(r'\\begin\{NoticeFrame\}(.*?)\\end\{NoticeFrame\}',lambda m:frame(m[1]),tex,flags=re.S)
   tex=re.sub('('+OPEN_PAREN_TEX+numeric_token(r'[0-9０-９]{1,2}')+CLOSE_PAREN_TEX+r')\\Para\s*(\\begin\{ClozeFrame\}.*?\\end\{ClozeFrame\})',lambda m:r'\KeepComposition{'+literal_digits(m[1])+'}{'+m[2]+'}',tex,flags=re.S)
  return tex,'explicit_html_border'
 # A bound note cluster is a separate role from paired passage bodies.
 # Keep the note outside the final frame, retaining its original sequence.
 if task in ['paired_reading','cloze'] and r'\begin{ReadingNotes}'in tex:
  body,notes=tex.split(r'\begin{ReadingNotes}',1)
  framed,rule=context_frames(body,task,frame_style)
  return framed+r'\Para \begin{ReadingNotes}'+notes,rule+'_notes_outside'
 parts=[x.strip() for x in tex.split(r'\Para') if x.strip()]
 if task=='cloze':
  intros=[n for n,x in enumerate(parts)if x.startswith((r'\PassageIntroduction{',r'\DocumentIntroduction{'))]
  if intros:
   if len(intros)!=1:raise ValueError('Cloze context has multiple introductions')
   n=intros[0]
   if n+1==len(parts):raise ValueError('Cloze introduction needs following content')
   remainder=r'\Para '.join(parts[n+1:])
   # Preserve multiple composition labels/frames after a bound shared lead.
   if len([x for x in parts[n+1:] if re.match('^'+OPEN_PAREN_TEX+numeric_token('[１２12]')+CLOSE_PAREN_TEX+r'.*さくぶん',x)])>1:
    framed,subrule=context_frames(remainder,task,frame_style,explicit)
   else:framed=frame(remainder)
   return r'\Para '.join(parts[:n+1])+r'\Para '+framed,'bound_cloze_intro_outside_frame'
  labels=[n for n,x in enumerate(parts) if re.match('^'+OPEN_PAREN_TEX+numeric_token('[１２12]')+CLOSE_PAREN_TEX+r'.*さくぶん',x)]
  if len(labels)>1:
   out=parts[:labels[0]]
   for k,start in enumerate(labels):
    stop=labels[k+1] if k+1<len(labels) else len(parts)
    out += [r'\KeepComposition{'+parts[start]+'}{'+frame(r'\Para '.join(parts[start+1:stop]))+'}']
   return r'\Para '.join(out),'explicit_composition_labels_separate_frames'
  if len(parts)>1 and re.search(r'作文|文章|さくぶん',parts[0]):
   return parts[0]+r'\Para '+frame(r'\Para '.join(parts[1:])),'cloze_intro_outside_frame'
  return frame(tex),'cloze_context_frame'
 if task=='reading':
  intros=[n for n,x in enumerate(parts[:3])if x.startswith((r'\PassageIntroduction{',r'\DocumentIntroduction{'))]
  if intros:
   if len(intros)!=1:raise ValueError('Reading context has multiple introductions')
   n=intros[0]
   if parts[n].startswith(r'\DocumentIntroduction{')or explicit:
    return r'\Para '.join(parts[:n+1])+r'\Para '+frame(r'\Para '.join(parts[n+1:])),'bound_document_intro_then_frame'
   return tex,'bound_passage_introduction'
  for n,x in enumerate(parts[:3]):
   plain=re.sub(r'\\ruby\{([^{}]*)\}\{[^{}]*\}',r'\1',x).replace(' ','')
   intro=re.search(r'(?:メール|手紙)(?:である|です)。$|お知らせ(?:である|です|が.{0,30}あります)。$|紙.{0,40}見ました。$',plain)
   if intro and len(plain)<180 and n+1<len(parts):
    return r'\Para '.join(parts[:n+1])+r'\Para '+frame(r'\Para '.join(parts[n+1:])),'document_intro_then_frame'
 if explicit and task=='reading':
  prefix=[]
  if parts and re.fullmatch(OPEN_PAREN_TEX+numeric_token()+CLOSE_PAREN_TEX,parts[0]):prefix=[literal_digits(parts.pop(0))]
  return r'\Para '.join(prefix+[frame(r'\Para '.join(parts))]),'source_override_frame_after_optional_label'
 return tex,None
