"""Projection-bound reconstruction of a flattened, unscored STAR solution."""
import html, re, hashlib
from collections import Counter
from bs4 import BeautifulSoup, NavigableString
from model import Projection
from notice_layout import html_lines


def slice_inline(raw, start, end):
    """Slice base code points while retaining complete ruby and inline wrappers."""
    projection=Projection({'html':raw})
    if not 0<=start<end<=len(projection.text):raise ValueError('Invalid inline span')
    if any(r['start']<p<r['end'] for r in projection.ruby for p in [start,end]):
        raise ValueError('Inline span splits ruby')
    cursor=0
    def visit(node):
        nonlocal cursor
        if isinstance(node,NavigableString):
            a=cursor;cursor+=len(str(node))
            return html.escape(str(node)[max(start-a,0):max(min(end-a,len(str(node))),0)]) if a<end and cursor>start else ''
        if node.name=='ruby':
            a=cursor;cursor+=len(Projection({'html':str(node)}).text)
            return str(node) if start<=a and cursor<=end else ''
        if node.name in ['br','p','div','table','rt','rp']:raise ValueError('Expected one inline fragment')
        children=''.join(visit(c)for c in node.children)
        if not children:return ''
        clone=BeautifulSoup(str(node),'html.parser').find();clone.clear()
        for child in list(BeautifulSoup(children,'html.parser').contents):clone.append(child)
        return str(clone)
    result=''.join(visit(n)for n in BeautifulSoup(raw,'html.parser').contents)
    if Projection({'html':result}).text!=projection.text[start:end]:raise ValueError('Inline span changed text')
    return result


def numbered_table_choices(table):
    """Read an existing one-row choice table without losing labels or ruby."""
    rows=table.find_all('tr')
    cells=rows[0].find_all(['td','th'],recursive=False)if len(rows)==1 else []
    if len(cells)!=4 or table.find('caption') or len(table.find_all('table')) or any(c.has_attr('rowspan')or c.has_attr('colspan')or c.find(['p','div','br','table'])for c in cells):
        raise ValueError('Choice table requires four unspanned inline cells')
    choices=[];numbers=[]
    for cell in cells:
        raw=cell.decode_contents();p=Projection({'html':raw})
        match=re.fullmatch(r'\s*([1-4])\s+(\S.*)',p.text,re.S)
        if not match:raise ValueError('Choice table requires four numbered fragments')
        numbers.append(match[1])
        choices.append({'number':int(match[1]),'raw':raw,'value':{'html':slice_inline(raw,match.start(2),len(p.text))}})
    if sorted(numbers)!=list('1234'):raise ValueError('Choice table requires four unique numbers')
    return choices


def prepare_inline_solution(value, layout):
    raw=html.escape(value).replace('\n','<br/>')if isinstance(value,str)else value['html']
    lines=html_lines(raw);spec=layout['inline_solution'];index=spec['line']
    if not 0<=index<len(lines):raise ValueError('Unknown inline solution line')
    p=Projection({'html':lines[index]});a,b=spec['prefix_end'],spec['suffix_start'];cells=spec['choices']
    if not 0<a<b<len(p.text)or len(cells)!=4 or not 0<=spec['star_index']<4:raise ValueError('Invalid inline solution geometry')
    previous=a;choices=[];discard=''
    for cell in cells:
        x,y=cell['start'],cell['end']
        if not previous<=x<y<=b:raise ValueError('Overlapping inline choices')
        discard+=p.text[previous:x];previous=y;choices.append(slice_inline(lines[index],x,y))
    discard+=p.text[previous:b]
    if re.sub(r'[\s［］★]','',discard) or discard.count('★')!=1:raise ValueError('Inline solution would discard protected text')
    numbers=[re.fullmatch(r'([1-4])\s+\S.*',Projection({'html':v}).text)for v in choices]
    if not all(numbers)or sorted(n[1]for n in numbers)!=list('1234'):raise ValueError('Inline solution needs four unique numbered choices')
    star_offset=p.text.index('★',a,b)
    c=cells[spec['star_index']]
    if not (cells[spec['star_index']-1]['end']if spec['star_index']else a)<=star_offset<c['start']:raise ValueError('Star differs from authored slot')
    first=[slice_inline(lines[index],0,a),*['★'if j==spec['star_index']else'_'for j in range(4)],slice_inline(lines[index],b,len(p.text))]
    table='<table>'+''.join('<tr>'+''.join('<td>'+v+'</td>'for v in row)+'</tr>'for row in [first,['',*choices,'']])+'</table>'
    out=[]
    for j,line in enumerate(lines):
        if j==index:out.append(table);continue
        splits=[r for r in layout.get('line_splits',[])if r['line']==j]
        if len(splits)>1:raise ValueError('Duplicate example line split')
        offsets=[0,*splits[0]['offsets'],len(Projection({'html':line}).text)]if splits else None
        if offsets:
            if offsets!=sorted(set(offsets)):raise ValueError('Invalid example line split')
            out.extend('<p>'+slice_inline(line,x,y)+'</p>'for x,y in zip(offsets,offsets[1:]))
        else:out.append('<p>'+line+'</p>')
    result={'html':''.join(out)}
    signature=lambda v:[(r['base'],r['reading'])for r in Projection(v).ruby]
    if signature(value)!=signature(result):raise ValueError('Inline solution changed ruby')
    return result


def prepare_structured_solution(value, layout):
    """Keep existing solution atoms while exposing their native table roles."""
    if not isinstance(value, dict):
        raise ValueError('Structured solution requires rich content')
    soup=BeautifulSoup(value['html'],'html.parser')
    if 'solution_table' in layout:
        index=layout['solution_table']['index'];tables=soup.find_all('table')
        if type(index)is not int or not 0<=index<len(tables):raise ValueError('Unknown native solution table')
        table=tables[index];rows=table.find_all('tr')
        cells=[r.find_all(['td','th'],recursive=False)for r in rows]
        if len(rows)<2 or any(len(r)!=6 or any(c.has_attr('rowspan')or c.has_attr('colspan')for c in r)for r in cells[:2]):raise ValueError('Native solution needs two six-cell rows')
        marks=[Projection({'html':str(c)}).text.strip()for c in cells[0][1:5]]
        normalize=layout['solution_table'].get('normalize_slot_strokes',False)
        if not isinstance(normalize,bool):raise ValueError('Invalid native solution stroke role')
        if normalize:
            marks=['_'if re.fullmatch(r'_+',mark)else mark for mark in marks]
        numbers=[re.match(r'^([1-4])\s+',Projection({'html':str(c)}).text.strip())for c in cells[1][1:5]]
        # A recovered example may use an outline star. Preserve that literal
        # glyph while applying the same unbroken six-cell solution geometry.
        if marks.count('_')!=3 or sum(mark in ['★','☆']for mark in marks)!=1 or not all(numbers)or sorted(m[1]for m in numbers)!=list('1234'):raise ValueError('Native solution needs four slots and four numbered choices')
        if any(len(r)!=1 or r[0].get('colspan')!='6' or r[0].has_attr('rowspan')for r in cells[2:]):raise ValueError('Native solution tails must span all six columns')
        table['data-star-unbroken-edges']='true';table['data-star-keep-choices']='true'
        if normalize:
            # Existing underline runs are one slot. Native geometry owns their
            # strokes; an administrative padded STAR must not leave a remnant.
            for node in soup.find_all('u'):
                if not node.find(True)and node.get_text().strip()=='★':node.unwrap()
        result={'html':str(soup)}
        if Projection(result).text!=Projection(value).text or Projection(result).ruby!=Projection(value).ruby:raise ValueError('Native solution geometry changed text/ruby')
        return result
    elif 'single_row_solution' in layout:
        index=layout['single_row_solution']['index'];tables=soup.find_all('table')
        if type(index)is not int or not 0<=index<len(tables):raise ValueError('Unknown single-row solution')
        region=tables[index];rows=region.find_all('tr');cells=rows[0].find_all(['td','th'],recursive=False)if rows else []
        if len(rows)!=1 or len(cells)!=6 or any(c.has_attr('rowspan')or c.has_attr('colspan')for c in cells):
            raise ValueError('Single-row solution requires six unspanned cells')
        first=[cells[0].decode_contents()];second=[''];numbers=[];stars=0
        for cell in cells[1:5]:
            raw=cell.decode_contents();p=Projection({'html':raw});m=re.fullmatch(r'\s*(★\s*)?([1-4])\s+\S.*',p.text,re.S)
            if not m:raise ValueError('Single-row solution needs numbered fragments')
            first.append('★'if m[1]else'_');stars+=bool(m[1]);numbers.append(m[2])
            start=p.text.index(m[2]);second.append(slice_inline(raw,start,len(p.text)))
        if stars!=1 or sorted(numbers)!=list('1234'):raise ValueError('Single-row solution requires one star and four unique choices')
        first.append(cells[-1].decode_contents());second.append('')
        replacement=BeautifulSoup('<table data-star-unbroken-edges="true">'+''.join('<tr>'+''.join('<td>'+c+'</td>'for c in row)+'</tr>'for row in [first,second])+'</table>','html.parser').table
        region.replace_with(replacement)
    elif 'flex_solution' in layout:
        candidates=[d for d in soup.find_all('div') if re.search(r'display\s*:\s*flex(?:;|$)',d.get('style',''))]
        index=layout['flex_solution']['index']
        if type(index) is not int or not 0<=index<len(candidates):
            raise ValueError('Unknown flex solution')
        region=candidates[index]
        spans=region.find_all('span',recursive=False)
        if len(spans)!=6 or len(region.find_all(recursive=False))!=6:
            raise ValueError('Flex solution requires prefix, four slots and suffix')
        first=[spans[0].decode_contents()];second=[''];marks=[];numbers=[]
        for span in spans[1:5]:
            slots=span.find_all('span',recursive=False)
            if len(slots)!=1 or slots[0].find(True):
                raise ValueError('Flex slot must be one literal marker')
            slot=slots[0];mark=slot.get_text().strip()
            if mark not in ['', '★']:
                raise ValueError('Unknown flex slot marker')
            marks.append(mark);slot.extract()
            choice=span.decode_contents().strip()
            match=re.match(r'^([1-4])\s+',choice)
            if not match:raise ValueError('Flex solution choice is not numbered')
            numbers.append(match[1]);first.append(mark or '_');second.append(choice)
        if marks.count('★')!=1 or sorted(numbers)!=list('1234'):
            raise ValueError('Flex solution requires one star and four unique choices')
        first.append(spans[-1].decode_contents());second.append('')
        table=BeautifulSoup('<table>'+''.join('<tr>'+''.join('<td>'+c+'</td>' for c in row)+'</tr>' for row in [first,second])+'</table>','html.parser').table
        region.replace_with(table)
    elif 'table_tail' in layout:
        tables=soup.find_all('table');index=layout['table_tail']['index']
        if type(index) is not int or not 0<=index<len(tables):raise ValueError('Unknown solution table')
        rows=tables[index].find_all('tr')
        if len(rows)!=2:raise ValueError('Solution tail requires two rows')
        cells=[r.find_all(['td','th'],recursive=False) for r in rows]
        if any(len(r)!=5 or any(c.has_attr('colspan') or c.has_attr('rowspan') for c in r) for r in cells):
            raise ValueError('Solution tail requires an unspanned five-column table')
        tail=cells[0][-1]
        raw=tail.decode_contents();match=re.fullmatch(r'_(.+)',raw,re.S)
        if not match or '<' in raw:raise ValueError('Solution tail must follow one literal slot')
        if [c.get_text().strip() for c in cells[0][1:4]].count('★')!=1:
            raise ValueError('Solution tail requires an existing starred slot')
        tail.clear();tail.append('_')
        extra=soup.new_tag('td');extra.append(match[1]);rows[0].append(extra)
        rows[1].append(soup.new_tag('td'))
        compact=lambda x:re.sub(r'\s+','',Projection(x).text)
        if compact(value)!=compact({'html':str(soup)}):raise ValueError('Solution tail changed text')
    else:raise ValueError('Unknown structured solution')
    result={'html':str(soup)}
    ruby=lambda v:[(r['base'],r['reading']) for r in Projection(v).ruby]
    if ruby(value)!=ruby(result):raise ValueError('Structured solution changed ruby order')
    return result


def prepare_ordered_solution(value,layout):
    """Keep the solved sentence and give its separate order line four columns."""
    raw=value['html']if isinstance(value,dict)else html.escape(value).replace('\n','<br/>')
    lines=html_lines(raw);s=layout['ordered_solution'];p,a,b=(s[k]for k in ['prompt_line','solved_line','choices_line'])
    if not 0<=p<a<b<len(lines)or b!=a+1:raise ValueError('Ordered solution needs prompt and adjacent solution/order lines')
    prompt=Projection({'html':lines[p]}).text
    prompt=re.sub(r'^[（(]問題例[）)]','',prompt).strip();parts=re.split(r'(_|★)',prompt)
    if len(parts)!=9 or parts[1::2].count('★')!=1 or parts[1::2].count('_')!=3 or any(x.strip()for x in parts[2:7:2]):raise ValueError('Ordered solution needs four prompt slots')
    plain=Projection({'html':lines[b]}).text;marks=list(re.finditer(r'(?<!\S)([1-4])\s+',plain))
    if len(marks)!=4 or sorted(m[1]for m in marks)!=list('1234')or plain[:marks[0].start()].strip():raise ValueError('Ordered solution needs unique numbered choices')
    choices=[slice_inline(lines[b],m.start(),marks[j+1].start()if j<3 else len(plain)).strip()for j,m in enumerate(marks)]
    words=[re.sub(r'^[1-4]\s+','',Projection({'html':v}).text).strip()for v in choices]
    compact=lambda v:re.sub(r'\s+','',v)
    if compact(Projection({'html':lines[a]}).text)!=compact(parts[0]+''.join(words)+parts[-1]):raise ValueError('Solution sentence and ordered fragments disagree')
    star=parts[1::2].index('★')
    if int(marks[star][1])!=s['selected_choice']:raise ValueError('Selected answer differs from starred fragment')
    table='<table>'+''.join('<tr>'+''.join('<td>'+c+'</td>'for c in row)+'</tr>'for row in [['',*parts[1::2],''],['',*choices,'']])+'</table>'
    out=[]
    for j,line in enumerate(lines):
        out.append(table if j==b else line if BeautifulSoup(line,'html.parser').find('table')else'<p>'+line+'</p>')
    result={'html':''.join(out)}
    if [(r['base'],r['reading'])for r in Projection(value).ruby]!=[(r['base'],r['reading'])for r in Projection(result).ruby]:raise ValueError('Ordered solution changed ruby')
    return result


def attach_trailing_caption(value,spec):
    """Move only an explicitly bound answer caption into its existing table."""
    soup=BeautifulSoup(value['html'],'html.parser');tables=soup.find_all('table');index=spec['index']
    if not 0<=index<len(tables):raise ValueError('Unknown answer table')
    table=tables[index];following=table.find_next_sibling()
    if not following or following.name!='p' or re.sub(r'\s','',Projection({'html':str(following)}).text)not in ['（解答用紙）','(解答用紙)']or table.find('caption'):
        raise ValueError('Expected exact following answer-sheet caption')
    cells=table.find_all(['td','th']);text=Projection({'html':str(table)}).text
    if len(table.find_all('tr'))!=1 or len(cells)!=5 or len(re.findall(r'[①②③④❶❷❸❹●]',text))!=4:raise ValueError('Caption target is not an answer demonstration')
    cap=soup.new_tag('caption')
    for child in list(following.contents):cap.append(child)
    following.decompose();table.insert(0,cap);result={'html':str(soup)}
    identity=lambda v:Counter((r['base'],r['reading'])for r in Projection(v).ruby)
    if identity(value)!=identity(result):raise ValueError('Answer caption changed ruby associations')
    return result

def projection_sha(value):
    return hashlib.sha256(Projection(value).text.encode()).hexdigest()


def prepare_answer_line_pair(value, spec):
    """Bind existing bubbles and their adjacent caption to a native answer row."""
    if not isinstance(value, dict):
        raise ValueError('Answer line pair requires rich content')
    soup = BeautifulSoup(value['html'], 'html.parser')
    nodes = [n for n in soup.contents if not isinstance(n, NavigableString) or n.strip()]
    a, b = spec['bubble_part'], spec['caption_part']
    if (type(a) is not int or type(b) is not int or b != a + 1
            or not 0 <= a < b < len(nodes)
            or any(getattr(nodes[n], 'name', None) != 'p' for n in [a, b])):
        raise ValueError('Answer line pair requires adjacent complete paragraphs')
    raw = nodes[a].decode_contents()
    text = Projection({'html': raw}).text
    match = re.fullmatch(r'\s*([（(](?:例|れい)[）)])\s*([①②③④❶❷❸❹●\s]+)', text)
    caption = nodes[b].decode_contents()
    if not match or re.sub(r'\s', '', Projection({'html': caption}).text) not in ['（解答用紙）', '(解答用紙)']:
        raise ValueError('Answer line pair lacks exact label, bubbles or caption')
    tokens = list(re.finditer(r'[①②③④❶❷❸❹●]', text))
    if len(tokens) != 4:
        raise ValueError('Answer line pair requires four existing bubbles')
    for n, token in enumerate(tokens, 1):
        if token[0] != '●' and token[0] not in ['①②③④'[n-1], '❶❷❸❹'[n-1]]:
            raise ValueError('Answer line pair has inconsistent bubble order')
    cells = [slice_inline(raw, match.start(1), match.end(1))]
    cells.extend(slice_inline(raw, t.start(), t.end()) for t in tokens)
    table = BeautifulSoup('<table><caption>' + caption + '</caption><tr>'
        + ''.join('<td>' + c + '</td>' for c in cells) + '</tr></table>', 'html.parser').table
    nodes[a].replace_with(table)
    nodes[b].decompose()
    result = {'html': str(soup)}
    ruby = lambda v: Counter((r['base'], r['reading']) for r in Projection(v).ruby)
    compact = lambda v: Counter(re.sub(r'\s', '', Projection(v).text))
    if ruby(value) != ruby(result) or compact(value) != compact(result):
        raise ValueError('Answer line pair changed retained text or ruby')
    return result

def prepare_stacked_cells(value, spec):
    """Expose four existing marker/fragment cells as a two-row worked diagram."""
    if not isinstance(value,dict):raise ValueError('Stacked cells require rich content')
    soup=BeautifulSoup(value['html'],'html.parser');tables=soup.find_all('table')
    index=spec['index'];line_index=spec['prompt_line']
    if type(index)is not int or not 0<=index<len(tables):raise ValueError('Unknown stacked solution table')
    region=tables[index];rows=region.find_all('tr');cells=rows[0].find_all(['td','th'],recursive=False)if len(rows)==1 else []
    if len(cells)!=6 or any(c.has_attr('rowspan')or c.has_attr('colspan')for c in cells):
        raise ValueError('Stacked solution needs six unspanned cells')
    if any(c.find(['p','div','br','table'])for c in [cells[0],cells[-1]]):
        raise ValueError('Stacked solution edges must be inline')
    marks=[];choices=[];numbers=[]
    for cell in cells[1:5]:
        if cell.find(['p','div','table'])or len(cell.find_all('br'))!=1:
            raise ValueError('Stacked solution needs one explicit marker/choice break')
        lines=html_lines(cell.decode_contents())
        if len(lines)!=2:raise ValueError('Stacked solution needs exactly two cell lines')
        marker=BeautifulSoup(lines[0],'html.parser')
        if marker.find(True):raise ValueError('Stacked slot marker must be literal')
        text=marker.get_text().strip()
        if not re.fullmatch(r'_+|_*★_*',text):raise ValueError('Invalid stacked slot marker')
        marks.append('★'if '★'in text else'_')
        p=Projection({'html':lines[1]});number=re.match(r'^\s*([1-4])\s+\S',p.text)
        if not number:raise ValueError('Stacked solution needs numbered fragments')
        numbers.append(number[1]);choices.append(lines[1])
    if marks.count('★')!=1 or sorted(numbers)!=list('1234'):
        raise ValueError('Stacked solution requires one star and four unique choices')
    lines=html_lines(value['html'])
    if type(line_index)is not int or not 0<=line_index<len(lines):raise ValueError('Unknown stacked prompt line')
    raw=lines[line_index];p=Projection({'html':raw})
    tokens=list(re.finditer(r'_+★_+|_+|★',p.text))
    if len(tokens)!=4 or ['★'if '★'in t[0]else'_'for t in tokens]!=marks or any(p.text[a.end():b.start()].strip()for a,b in zip(tokens,tokens[1:])):
        raise ValueError('Stacked prompt and solution must have the same four slots')
    if tokens[0].start()==0 or tokens[-1].end()==len(p.text):raise ValueError('Stacked prompt requires both sentence edges')
    holders=[n for n in soup.find_all('p')if not n.find(['p','div','br','table'])and Projection({'html':n.decode_contents()}).text==p.text]
    if len(holders)!=1 or holders[0].find_parent('table')or region not in holders[0].find_all_next('table'):
        raise ValueError('Stacked prompt must be one complete preceding paragraph')
    prefix=slice_inline(raw,0,tokens[0].start());suffix=slice_inline(raw,tokens[-1].end(),len(p.text))
    if re.sub(r'\s','',Projection({'html':prefix}).text)!=re.sub(r'\s','',Projection({'html':cells[0].decode_contents()}).text)or re.sub(r'\s','',Projection({'html':suffix}).text)!=re.sub(r'\s','',Projection({'html':cells[-1].decode_contents()}).text):
        raise ValueError('Stacked prompt and solution sentence edges disagree')
    # Only display strokes become native geometry; words and ruby stay intact.
    holders[0].replace_with(BeautifulSoup('<p>'+prefix+' '.join(marks)+suffix+'</p>','html.parser').p)
    first=[cells[0].decode_contents(),*marks,cells[-1].decode_contents()];second=['',*choices,'']
    replacement=BeautifulSoup('<table data-star-unbroken-edges="true" data-star-keep-choices="true">'+''.join('<tr>'+''.join('<td>'+x+'</td>'for x in row)+'</tr>'for row in [first,second])+'</table>','html.parser').table
    region.replace_with(replacement)
    # In this bound example the administrative STAR is one native symbol;
    # unwrap its literal underline so padded spaces cannot leave stray strokes.
    for node in soup.find_all('u'):
        if not node.find(True)and node.get_text().strip()=='★':node.unwrap()
    result={'html':str(soup)}
    # Row traversal moves the sentence suffix before the numbered fragments;
    # intact ruby nodes preserve their text, readings and original identities.
    rubies=lambda v:Counter(str(n)for n in BeautifulSoup(v['html'],'html.parser').find_all('ruby'))
    if rubies(value)!=rubies(result):raise ValueError('Stacked solution changed ruby identities')
    return result


def prepare_ordinary_choices(value, indexes):
    """Expose four existing complete numbered lines as one native choice row."""
    raw = html.escape(value).replace('\n','<br/>') if isinstance(value,str) else value['html']
    lines = html_lines(raw)
    if (not isinstance(indexes,list) or len(indexes)!=4
            or any(type(n)is not int for n in indexes)
            or indexes!=list(range(indexes[0],indexes[0]+4))
            or not 0<=indexes[0]<=indexes[-1]<len(lines)):
        raise ValueError('Ordinary choices require four consecutive complete lines')
    chosen=[lines[n] for n in indexes]
    table='<table><tr>'+''.join('<td>'+line+'</td>' for line in chosen)+'</tr></table>'
    choices=numbered_table_choices(BeautifulSoup(table,'html.parser').table)
    if [c['number'] for c in choices]!=[1,2,3,4]:
        raise ValueError('Ordinary choice lines must retain order1–4')
    out=[]
    for n,line in enumerate(lines):
        if n==indexes[0]:out.append(table)
        elif n in indexes:continue
        else:out.append(line if BeautifulSoup(line,'html.parser').find('table') else '<p>'+line+'</p>')
    result={'html':''.join(out)}
    if re.sub(r'\s','',Projection(value).text)!=re.sub(r'\s','',Projection(result).text):
        raise ValueError('Ordinary choice row changed text')
    ruby=lambda v:Counter(str(n)for n in BeautifulSoup(v['html']if isinstance(v,dict)else html.escape(v),'html.parser').find_all('ruby'))
    if ruby(value)!=ruby(result):raise ValueError('Ordinary choice row changed ruby identities')
    return result


def prepare(value, layout):
    if projection_sha(value) != layout['projection_sha256']:
        raise ValueError('Stale example structure binding')
    for key in ['bare_choice_labels','inline_answer_frame']:
        if key in layout and type(layout[key])is not bool:
            raise ValueError('Example presentation switches require booleans')
    if 'answer_before_pt'in layout:
        gap=layout['answer_before_pt']
        if isinstance(gap,bool)or not isinstance(gap,(int,float))or not 0<=gap<=30:
            raise ValueError('Invalid per-example answer clearance')
    modes=[k for k in ['solution','flex_solution','table_tail','inline_solution','single_row_solution','ordered_solution','solution_table','stacked_cell_solution','ordinary_choice_lines','answer_line_pair'] if k in layout]
    if len(modes)>1:raise ValueError('Conflicting solution layouts')
    if 'trailing_answer_caption'in layout:
        next_layout={k:v for k,v in layout.items()if k!='trailing_answer_caption'}
        result=prepare(value,next_layout)
        return attach_trailing_caption(result,layout['trailing_answer_caption'])
    if 'answer_line_pair'in layout:return prepare_answer_line_pair(value,layout['answer_line_pair'])
    if 'ordinary_choice_lines'in layout:return prepare_ordinary_choices(value,layout['ordinary_choice_lines'])
    if 'ordered_solution'in layout:return prepare_ordered_solution(value,layout)
    if 'stacked_cell_solution'in layout:return prepare_stacked_cells(value,layout['stacked_cell_solution'])
    if 'inline_solution'in layout:return prepare_inline_solution(value,layout)
    if modes and modes[0]!='solution':return prepare_structured_solution(value,layout)
    raw = html.escape(value).replace('\n','<br/>') if isinstance(value,str) else value['html']
    lines = html_lines(raw)
    solution = layout.get('solution')
    if not solution: return value
    a,b = solution['sentence_line'],solution['choices_line']
    if b != a+1 or not 0 <= a < b < len(lines):
        raise ValueError('STAR solution must use adjacent existing lines')
    # Ruby is an atomic node: slots must be literal text outside all markup.
    soup=BeautifulSoup(lines[a],'html.parser')
    if any(re.search(r'[_★]',Projection({'html':str(tag)}).text) for tag in soup.find_all('ruby')):
        raise ValueError('STAR slots cannot divide a ruby group')
    # A retained underlined star is the same slot symbol. The native worked
    # cell supplies its underline; unwrap only this exact one-character role.
    for tag in soup.find_all('u'):
        if tag.get_text()=='★' and not tag.find(True):tag.unwrap()
    pieces=re.split(r'(?<![A-Za-z0-9])(_|★)(?![A-Za-z0-9])',str(soup))
    if len(pieces)!=9 or pieces[1::2].count('★')!=1 or pieces[1::2].count('_')!=3 or any(x.strip()for x in pieces[2:7:2]):
        raise ValueError('STAR sentence must contain four separated slots')
    choice_soup=BeautifulSoup(lines[b],'html.parser')
    choice_nodes=[n for n in choice_soup.contents if not isinstance(n,NavigableString)or n.strip()]
    if choice_soup.find('table'):
        if len(choice_nodes)!=1 or choice_nodes[0].name!='table':raise ValueError('STAR choice line must contain only its table')
        choices=[c['raw']for c in numbered_table_choices(choice_nodes[0])]
    else:
        marks=list(re.finditer(r'(?<!\S)([1-4])\s+',lines[b]))
        if len(marks)!=4 or sorted(m[1]for m in marks)!=list('1234') or lines[b][:marks[0].start()].strip():
            raise ValueError('STAR solution needs each numbered choice exactly once')
        choices=[lines[b][m.start():marks[k+1].start()if k<3 else len(lines[b])].strip()for k,m in enumerate(marks)]
    first=[pieces[0].strip(),*pieces[1::2],pieces[-1].strip()]
    second=['',*choices,'']
    table='<table>'+''.join('<tr>'+''.join('<td>'+c+'</td>'for c in row)+'</tr>'for row in [first,second])+'</table>'
    result={'html':''.join('<p>'+s+'</p>'if k!=a else table for k,s in enumerate(lines)if k!=b)}
    compact=lambda v:re.sub(r'\s+','',Projection(v).text)
    if compact(value)!=compact(result): raise ValueError('STAR reflow altered the existing text sequence')
    before=[(r['base'],r['reading'])for r in Projection(value).ruby]
    after=[(r['base'],r['reading'])for r in Projection(result).ruby]
    if before!=after: raise ValueError('STAR reflow changed ruby')
    return result
