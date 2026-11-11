"""Exact presentation bindings for inline cloze labels; no global bracket rewrite."""
import html
import re
from bs4 import BeautifulSoup, NavigableString, Tag
from model import Projection, digest

TOKEN = re.compile(r'【\s*([0-9０-９]+)\s*】|\[\s*([0-9０-９]+)\s*\]|（\s*([0-9０-９]+)\s*）|\(\s*([0-9０-９]+)\s*\)|\s*([0-9０-９]+)\s*')


def exact_inline_atoms(soup,text):
    """Find one exact sibling run, treating every complete ruby as one atom."""
    matches=[]
    for parent in [soup,*soup.find_all(True)]:
        if parent.name in ('ruby','rt','rp') or parent.find_parent(['ruby','rt','rp']):continue
        atoms=[]
        for child in parent.children:
            if isinstance(child,NavigableString):atoms.extend((c,NavigableString(c)) for c in str(child))
            elif isinstance(child,Tag) and child.name=='ruby':atoms.append((Projection({'html':str(child)}).text,child))
            else:atoms.append(('\0',child))
        joined=''.join(a for a,n in atoms);pos=joined.find(text)
        if pos<0:continue
        if joined.count(text)!=1:raise ValueError('Ambiguous exact inline context')
        offsets=[0]
        for a,n in atoms:offsets.append(offsets[-1]+len(a))
        if pos not in offsets or pos+len(text) not in offsets:
            raise ValueError('Exact inline context would split ruby')
        matches.append((parent,atoms,offsets,pos))
    if len(matches)!=1:raise ValueError('Exact inline context must match one intact sibling run')
    return matches[0]


def prepare_inline(value, binding, source_value=None):
    """Apply exact, bounded presentation roles without altering stored content/ruby."""
    source = value if source_value is None else source_value
    if digest(source) != binding['content_sha256']:
        raise ValueError('Stale inline presentation binding')
    before, current = Projection(source), Projection(value)
    ruby_signature = lambda p: [(r['base'], r['reading']) for r in p.ruby]
    if ''.join(before.text.split()) != ''.join(current.text.split()) or ruby_signature(before) != ruby_signature(current):
        raise ValueError('Prior presentation changed protected text or ruby')
    if set(binding)<= {'content_sha256','evidence','literal_identifiers'} and binding.get('literal_identifiers'):
        for spec in binding['literal_identifiers']:
            pattern=r'(?<![A-Za-z0-9])'+re.escape(spec['text'])+r'(?![A-Za-z0-9])'
            if len(re.findall(pattern,current.text))!=spec['occurrences']:raise ValueError('Literal identifier count changed')
        return value
    if 'soft_line_break_offsets' in binding:
        if digest(value) != digest(source):
            raise ValueError('Soft field breaks require the exact untransformed bound field')
        value = prepare_soft_question_breaks(value, {
            'stem_sha256': binding['content_sha256'],
            'break_offsets': binding['soft_line_break_offsets'],
        })
    raw = value['html'] if isinstance(value, dict) else html.escape(value).replace('\n', '<span data-authored-plain-break="line">\n</span>')
    soup = BeautifulSoup(raw, 'html.parser')
    for url in binding.get('breakable_urls', []):
        if not re.fullmatch(r'https?://[A-Za-z0-9:/?=&._%#~+\-]+', url):
            raise ValueError('Citation URL must retain one exact safe ASCII URL')
        matches = [n for n in soup.descendants if isinstance(n, NavigableString)
                   and n.parent.name not in ['rt', 'rp'] and url in str(n)]
        if len(matches) != 1 or str(matches[0]).count(url) != 1:
            raise ValueError('Breakable URL must occur once in an existing text run')
        n = matches[0]
        before, after = str(n).split(url)
        displayed=url
        # Angle brackets belong to the URL atom, never to the previous line.
        for opening,closing in [('<','>'),('〈','〉'),('《','》')]:
            if before.endswith(opening) and after.startswith(closing):
                before,after=before[:-1],after[1:]
                displayed=opening+url+closing
                break
        span = soup.new_tag('span')
        span['data-citation-url'] = 'breakable'
        span.string = displayed
        # Keep a complete acquisition-date attribution together at a citation
        # boundary. This applies only inside the already exact-bound URL field.
        tail=re.match(r'^(\s*\d{4}年\s*\d{1,2}月\s*\d{1,2}日取得による[）)])(.*)$',after,re.S)
        if tail:
            attribution=soup.new_tag('span');attribution['data-citation-attribution']='kept'
            attribution.string=tail.group(1)
            n.replace_with(NavigableString(before),span,attribution,NavigableString(tail.group(2)))
        else:n.replace_with(NavigableString(before), span, NavigableString(after))
        parent=span.parent
        if (parent.name in ['p','div'] and not parent.find(['p','div','table','section'])
            and re.fullmatch(r'[（(].*[）)]',Projection({'html':str(parent)}).text.strip(),re.S)):
            parent['data-native-url-citation']='true'
    for box in binding.get('inline_boxes', []):
        text, count = box['text'], box.get('occurrences', 1)
        if not 1 <= len(text) <= 20 or type(count) is not int or not 1 <= count <= 10:
            raise ValueError('Invalid exact inline label box')
        matches = [n for n in soup.find_all('span') if 'border:' in n.get('style', '')
                   and Projection({'html': str(n)}).text == text]
        if len(matches) != count or any(n.find(['p', 'div', 'table', 'br', 'section']) for n in matches):
            raise ValueError('Inline label box needs exact existing inline bordered spans')
        for n in matches:
            n['data-native-inline-box'] = 'label'
            if 'padding_pt' in box:
                if not 0<=box['padding_pt']<=3:raise ValueError('Invalid inline box padding')
                n['data-inline-box-padding-pt']=str(box['padding_pt'])
    for alignment in binding.get('alignments', []):
        if alignment['align'] not in ['left','center','right']:raise ValueError('Invalid exact block alignment')
        matches=[n for n in soup.find_all(['p','div','center'])if Projection({'html':str(n)}).text.strip()==alignment['text'] and not n.find(['p','div','center'])]
        if len(matches)!=1:raise ValueError('Alignment must select one existing complete block')
        matches[0]['style']='text-align:'+alignment['align']
        if 'right_inset_em' in alignment:
            inset=alignment['right_inset_em']
            if alignment['align']!='right' or isinstance(inset,bool) or not 0<=inset<=3:raise ValueError('Right inset requires bounded right alignment')
            matches[0]['data-right-inset-em']=str(inset)
    for edit in binding.get('spaces', []):
        before, after = edit['before'], edit['after']
        if before == after or before.replace(' ', '') != after.replace(' ', ''):
            raise ValueError('Inline space edit may only alter ASCII spaces')
        found = [n for n in soup.descendants if isinstance(n, NavigableString) and n.parent.name not in ['rt', 'rp'] and before in str(n)]
        if len(found) != 1 or str(found[0]).count(before) != 1:
            raise ValueError('Inline space edit must select one complete existing run')
        found[0].replace_with(str(found[0]).replace(before, after, 1))
    clusters=binding.get('kept_star_clusters',[])
    if len(clusters)!=len(set(clusters)):raise ValueError('Duplicate bound STAR cluster')
    for cluster in clusters:
        if not re.fullmatch(r'[_★](?:[ \t\u3000]+[_★]){3}',cluster)or cluster.count('_')!=3 or cluster.count('★')!=1:
            raise ValueError('Bound STAR cluster requires four literal slots and one star')
        matches=[n for n in soup.descendants if isinstance(n,NavigableString)and not n.find_parent(['ruby','rt','rp'])and cluster in str(n)]
        if len(matches)==1 and str(matches[0]).count(cluster)==1:
            node=matches[0];left,right=str(node).split(cluster)
            span=soup.new_tag('span');span['data-kept-star-cluster']='true';span.string=cluster
            node.replace_with(NavigableString(left),span,NavigableString(right))
        else:
            # Some audited fields underline the STAR as its own inline node.
            # Permit only that exact atom and its adjacent literal text runs.
            candidates=[]
            for star in soup.find_all('u'):
                if star.string is None or not re.fullmatch(r'[ \t\u3000]*★[ \t\u3000]*',str(star.string)) or star.find(True) or star.find_parent(['ruby','rt','rp']):continue
                a,b=star.previous_sibling,star.next_sibling
                left=str(a) if isinstance(a,NavigableString) else ''
                right=str(b) if isinstance(b,NavigableString) else ''
                combined=left+str(star.string)+right;start=combined.find(cluster)
                if start>=0 and combined.count(cluster)==1 and start<=len(left) and start+len(cluster)>=len(left)+len(star.string):
                    candidates.append((star,a,b,left,right,start))
            if len(candidates)!=1 or Projection({'html':str(soup)}).text.count(cluster)!=1:
                raise ValueError('Bound STAR cluster must match one intact text run or underlined STAR atom')
            star,a,b,left,right,start=candidates[0];end=start+len(cluster)
            span=soup.new_tag('span');span['data-kept-star-cluster']='true'
            span.append(NavigableString(left[start:]));span.append(BeautifulSoup(str(star),'html.parser').u)
            span.append(NavigableString(right[:end-len(left)-len(star.string)]))
            if isinstance(a,NavigableString):a.replace_with(NavigableString(left[:start]))
            if isinstance(b,NavigableString):b.replace_with(NavigableString(right[end-len(left)-len(star.string):]))
            star.replace_with(span)
    ranges=binding.get('kept_date_ranges',[])
    selectors=binding.get('kept_choice_selectors',[])
    for group in selectors:
        if not isinstance(group,str)or not re.fullmatch(r'1[ \u3000]+2[ \u3000]+3[ \u3000]+4[ \u3000]*から',group)or len(group)>20:
            raise ValueError('Exact choice selector requires spaced1–4 followed byから')
    for group in binding.get('groups', [])+ranges+selectors:
        is_range=group in ranges
        is_selector=group in selectors
        if is_range and not re.fullmatch(r'\d{1,2}月\d{1,2}日[（(][月火水木金土日][）)][～〜]\d{1,2}日[（(][月火水木金土日][）)]',group):raise ValueError('Invalid exact date range')
        if not is_selector and (not 2 <= len(group) <= (40 if is_range else 12) or any(x.isspace() for x in group)):
            raise ValueError('Bounded inline group must contain 2–12 unspaced base characters')
        matches=[]
        for parent in [soup, *soup.find_all(True)]:
            if parent.name in ['ruby', 'rt', 'rp'] or parent.find_parent(['ruby', 'rt', 'rp']):continue
            atoms=[]
            for child in parent.children:
                if isinstance(child, NavigableString):atoms.extend((c, NavigableString(c)) for c in str(child))
                elif isinstance(child, Tag) and child.name=='ruby':atoms.append((Projection({'html':str(child)}).text, child))
                else:atoms.append(('\0',child))
            joined=''.join(a for a,n in atoms);pos=joined.find(group)
            if pos<0:continue
            if joined.count(group)!=1:raise ValueError('Ambiguous bounded inline group')
            offsets=[0]
            for a,n in atoms:offsets.append(offsets[-1]+len(a))
            if pos not in offsets or pos+len(group) not in offsets:raise ValueError('Bounded group would split ruby')
            matches.append((parent,atoms,offsets.index(pos),offsets.index(pos+len(group))))
        if len(matches)!=1:raise ValueError('Bounded group must match once across intact inline nodes: '+group)
        parent,atoms,start,end=matches[0];parent.clear()
        span=soup.new_tag('span');span['data-bounded-word']='exact-choice-selector'if is_selector else'exact-date-range'if is_range else'exact-source-group'
        for idx,(a,n) in enumerate(atoms):
            if idx==start:parent.append(span)
            (span if start<=idx<end else parent).append(n)
    if binding.get('measured_gaps') and (binding.get('groups') or ranges):
        # Grouping splits neighboring text into character atoms. Rejoin only
        # adjacent text nodes before exact gap matching; never cross markup.
        soup.smooth()
    for gap in binding.get('measured_gaps',[]):
        text,prefix,width=gap['text'],gap['after'],gap['width_em']
        if not text.startswith(prefix)or not 0<len(prefix)<len(text)or isinstance(width,bool)or not 0<width<=3:
            raise ValueError('Invalid source-bound measured gap')
        parent,atoms,offsets,pos=exact_inline_atoms(soup,text)
        boundary=pos+len(prefix)
        if boundary not in offsets:raise ValueError('Measured gap would split ruby')
        at=offsets.index(boundary)
        marker=soup.new_tag('span');marker['data-inline-gap-em']=str(width)
        parent.clear()
        for index,(base,node) in enumerate(atoms):
            if index==at:parent.append(marker)
            parent.append(node)
    if binding.get('range_tokens'):
        from range_tokens import prepare
        prepare(soup,binding['range_tokens'])
    if binding.get('document_bullet_lines'):
        from document_bullets import prepare
        prepare(soup,binding['document_bullet_lines'])
    if binding.get('ascii_question_marks'):
        soup.smooth()
    for text in binding.get('ascii_question_marks',[]):
        if not isinstance(text,str) or not 2<=len(text)<=12 or text.count('?')!=1 or not text.endswith('?'):
            raise ValueError('Question mark presentation needs an exact short context ending in ASCII question mark')
        parent,atoms,offsets,pos=exact_inline_atoms(soup,text)
        boundary=pos+len(text)-1
        if boundary not in offsets:raise ValueError('Question mark presentation would split ruby')
        at=offsets.index(boundary)
        if atoms[at][0]!='?' or not isinstance(atoms[at][1],NavigableString):
            raise ValueError('Question mark must be an existing plain punctuation atom')
        mark=soup.new_tag('span');mark['data-ascii-question-mark']='fullwidth-glyph';mark.string='?'
        parent.clear()
        for index,(base,node) in enumerate(atoms):parent.append(mark if index==at else node)
    if binding.get('breadcrumbs') or binding.get('literal_identifiers'):
        from inline_text_roles import prepare as prepare_text_roles
        prepare_text_roles(soup,binding)
    result={'html':str(soup)}
    if binding.get('paragraphs'):
        from paragraph_layout import prepare
        result=prepare(result,binding['paragraphs'])
    old,new=Projection(value),Projection(result)
    if ''.join(old.text.split())!=''.join(new.text.split()):raise ValueError('Inline presentation changed protected text')
    signature=lambda p:[(r['base'],r['reading'])for r in p.ruby]
    if signature(old)!=signature(new):raise ValueError('Inline presentation changed ruby')
    return result


def prepare_soft_question_breaks(value, binding):
    """Remove witnessed literal line endings, including after frozen ruby wraps."""
    if digest(value) != binding['stem_sha256']:
        raise ValueError('Stale soft question break binding')
    projection=Projection(value)
    text=projection.text
    offsets = binding['break_offsets']
    if not offsets or len(set(offsets)) != len(offsets):
        raise ValueError('Soft question break offsets must be nonempty and unique')
    for offset in offsets:
        if (type(offset) is not int or not 0 < offset < len(text) - 1
                or text[offset] != '\n'):
            raise ValueError('Soft question break must be one literal interior newline')
        japanese_pair = re.fullmatch(r'[ぁ-んァ-ヶー一-龥々]{2}', text[offset - 1] + text[offset + 1])
        # A literal wrap after a comma is allowed only by this exact authored
        # field/offset binding. Scene endings and speaker boundaries still fail.
        comma_continuation = (text[offset-1] in '、,' and
                              re.fullmatch(r'[ぁ-んァ-ヶー一-龥々0-9０-９]', text[offset+1]))
        slots = re.search(r'([_★](?:[ \t]+[_★])*)[ \t]*$', text[:offset])
        slot_continuation = (slots and slots[1].count('_') == 3 and slots[1].count('★') == 1
                             and re.fullmatch(r'[ぁ-んァ-ヶー一-龥々]', text[offset + 1]))
        if not japanese_pair and not slot_continuation and not comma_continuation:
            raise ValueError('Soft question break requires a bound Japanese/comma continuation or complete four-slot STAR cluster')
        if projection.overlaps_ruby(offset,offset+1):
            raise ValueError('Soft break cannot split a ruby base')
    if isinstance(value,str):
        result=''.join(c for n,c in enumerate(value) if n not in set(offsets))
    else:
        raw=projection.raw
        spans=[projection.raw_span(n,n+1)for n in offsets]
        if any(raw[a:b]!='\n' for a,b in spans):
            raise ValueError('Soft break must be literal newline, not structural HTML')
        for a,b in sorted(spans,reverse=True):raw=raw[:a]+raw[b:]
        result={'html':raw}
    after=Projection(result)
    if after.text != ''.join(c for n,c in enumerate(text) if n not in set(offsets)):
        raise ValueError('Soft question break changed protected text')
    signature=lambda p:[(r['start'],r['end'],r['base'],r['reading'])for r in p.ruby]
    expected=[(r['start']-sum(n<r['start']for n in offsets),r['end']-sum(n<r['end']for n in offsets),r['base'],r['reading'])for r in projection.ruby]
    if signature(after)!=expected:raise ValueError('Soft break changed ruby association')
    return result


def prepare_soft_content_breaks(value, binding):
    """Reuse the strict single-newline guard for a selected plain passage."""
    return prepare_soft_question_breaks(value, {
        'stem_sha256': binding['content_sha256'],
        'break_offsets': binding['break_offsets'],
    })


def cloze_label(token):
    display=cloze_display(token)
    return display.split('-')[0] if display is not None else None


def cloze_display(token):
    # Retained letter suffixes distinguish multiple slots sharing one question.
    normalized=token.strip().translate(str.maketrans('０１２３４５６７８９［］','0123456789[]'))
    bracket_suffix=re.fullmatch(r'\[\s*([0-9]{1,3}-[a-z])\s*\]',normalized)
    if bracket_suffix:return bracket_suffix[1]
    suffix=re.fullmatch(r'([0-9]{1,3}-[a-z])',normalized)
    if suffix:return suffix[1]
    closing=re.fullmatch(r'([0-9]{1,3})[）)]',normalized)
    if closing:return closing[1]
    match = TOKEN.fullmatch(normalized)
    if not match:
        return None
    return next(g for g in match.groups() if g is not None).translate(str.maketrans('０１２３４５６７８９', '0123456789'))


def prepare_clozes(value, binding, questions, source_value=None):
    source=value if source_value is None else source_value
    if digest(source) != binding['content_sha256']:
        raise ValueError('Stale inline cloze content binding')
    if source_value is not None:
        old,new=Projection(source),Projection(value)
        ruby=lambda p:[(r['base'],r['reading'])for r in p.ruby]
        if ''.join(old.text.split())!=''.join(new.text.split())or ruby(old)!=ruby(new):
            raise ValueError('Cloze presentation changed source text or ruby')
    raw = value['html'] if isinstance(value, dict) else html.escape(value).replace('\n', '<span data-authored-plain-break="line">\n</span>')
    soup = BeautifulSoup(raw, 'html.parser')
    seen_tokens=set()
    for marker in binding['markers']:
        token, label, qid = (marker[k] for k in ['token', 'label', 'question_id'])
        if token in seen_tokens:raise ValueError('Duplicate cloze token binding')
        seen_tokens.add(token)
        if cloze_label(token) != label:
            raise ValueError('Invalid inline cloze token')
        if questions.get(qid) != label:
            raise ValueError('Cloze label does not match its question association')
        found = [n for n in soup.descendants if isinstance(n, NavigableString) and n.parent.name not in ['rt', 'rp'] and token in str(n)]
        occurrences=marker.get('occurrences',1)
        if type(occurrences)is not int or not 1<=occurrences<=10:raise ValueError('Invalid exact cloze occurrence count')
        if sum(str(n).count(token)for n in found)!=occurrences:
            raise ValueError('Inline cloze token occurrence count differs from binding')
        display=marker.get('display_label',label)
        if cloze_display(token)!=display:raise ValueError('Cloze display label must preserve the existing slot label')
        for n in found:
            pieces=str(n).split(token);replacement=[];spans=[]
            for index,piece in enumerate(pieces):
                if index:
                    span=soup.new_tag('span');span['data-cloze-label']=label;span['data-cloze-display']=display;span.string=token
                    spans.append(span);replacement.append(span)
                replacement.append(NavigableString(piece))
            n.replace_with(*replacement)
            if binding.get('replace_inline_box_wrappers'):
                for span in spans:
                    parent=span.parent
                    if parent.name=='span' and 'border' in parent.get('style','') and Projection({'html':str(parent)}).text.strip()==token.strip():parent.unwrap()
    result = {'html': str(soup)}
    if ''.join(Projection(result).text.split()) != ''.join(Projection(value).text.split()):
        raise ValueError('Inline cloze presentation changed protected text')
    return result
