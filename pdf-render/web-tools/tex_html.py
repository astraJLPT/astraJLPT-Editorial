"""Modern rich-text presentation using the renderer's bound roles and dimensions.

Canonical characters stay in the DOM. Furniture that TeX draws (slots, boxes,
empty brackets) keeps its source text separately from its visual representation.
No editorial, schema, or renderer file is written by this adapter.
"""
import html
import re
from bs4 import BeautifulSoup, NavigableString, Tag
from model import Projection
from answer_blanks import prepare as prepare_blanks
from inline_layout import prepare_inline, prepare_clozes
from instruction_spacing import prepare as instruction_boundaries
from richtex import remove_number
from wakachi import bind_groups, classes, spaced_task


def source_html(value):
    return value['html'] if isinstance(value,dict) else html.escape(value).replace('\n','<br>')


def label_only_stem(value, label, task):
    """Mirror TeX's consumption of a cloze stem that is only its printed label.

    The caller retains canonical markup for text checks and the radio-group
    accessible name. This never hides a prompt containing actual question text.
    """
    if task != 'cloze':
        return False
    number, remainder = remove_number(value)
    return number == str(label) and not Projection(remainder).text.strip()


def span(soup, cls, text=None, **attrs):
    node=soup.new_tag('span',attrs={'class':cls,**attrs})
    if cls in ('tex-word-space','mixed-word-space','authored-word-gap'):node['data-preserved-space']='true'
    if text is not None:
        if text.isspace() and len(text)>1:
            # html.parser collapses an all-ASCII whitespace-only text node
            # when a later bound consumer reparses it. Keep each source space
            # explicit without changing the parent atom's single width owner.
            for ch in text:
                part=soup.new_tag('span',attrs={'data-preserved-space':'true'});part.string=ch;node.append(part)
        else:node.string=text
    return node


def visual_atom(soup,node,cls,display):
    original=node.decode_contents()
    node.clear();node['class']=cls
    src=span(soup,'source-literal sr-only')
    src.append(BeautifulSoup(original,'html.parser'))
    node.append(src);node.append(span(soup,'visual-only',display,**{'aria-hidden':'true'}))


def keep_blank_punctuation(blank):
    """Keep closing punctuation on the blank's line and in its reading order."""
    tail = blank.next_sibling
    padding = []
    while isinstance(tail, Tag) and tail.get('data-blank-padding') == 'ascii':
        padding.append(tail)
        tail = tail.next_sibling
    if not isinstance(tail, NavigableString):
        return
    marks = re.match(r'[、。，．,.！？!?：:；;）)\]］｝」』｣】〉》〕〗〙〛]+', tail)
    if not marks:
        return
    for space in padding:
        blank.append(space.extract())
    blank.append(marks[0])
    if marks.end() < len(tail):
        tail.replace_with(tail[marks.end():])
    else:
        tail.extract()


def native_ascii_space(m,context,target,node):
    """Resolve the explicit ASCII glue; it replaces automatic script glue."""
    if (context == 'example' and node.parent.name == 'span'
            and node.parent.parent.has_attr('data-ordinary-choice-row')
            and node.find_previous_sibling() is None
            and node.get_text() in ('1', '2', '3', '4')):
        # The native ordinary choice row sets a .4em skip after its label.
        return .4, 'example_choice_label'
    style=m['style'];owner=(target or '').split('/')[0]
    if '_web_space_tasks' not in m:
        m['_web_space_tasks']={k:m['tasks'][s['id']] for s in m['document']['sections']
                              for k in [s['id'],*[i['id'] for i in s['items']]]}
    task=m['_web_space_tasks'].get(owner)
    effective={**style,**style.get('task_overrides',{}).get(task,{})}
    block=style.get('block_styles',{}).get(owner,{})
    key='heading_word_space_em' if context=='heading' else 'word_space_em'
    width=block.get(key,effective.get(key,0))
    if context=='example':
        ex=style.get('examples',{});width=ex.get('ordinary_word_space_em',ex.get('word_space_em',width))
    if node.find_parent('table') and 'table_word_space_em' in block:width=block['table_word_space_em']
    role='instruction_latin' if context=='heading' else 'body_latin'
    notice=owner in style.get('block_styles',{}) or any(i['id']==owner and i.get('type')=='notice' for s in m['document']['sections'] for i in s['items'])
    if notice and 'notice_latin' in style['font_roles']:role='notice_latin'
    embedded=style.get('embedded_documents',{}).get(owner,{})
    if node.find_parent(attrs={'data-embedded-document':True}) and embedded.get('role')=='memo' and embedded.get('presentation')!='typed_box':role='memo'
    section=style.get('section_styles',{}).get(owner,{})
    document_role=m.get('layout',{}).get('items',{}).get(owner,{}).get('document_role',{}).get('role')
    if node.find_parent('section',class_='reading-passage') and (section.get('font_role')=='memo' or document_role=='memo'):role='memo'
    from font_geometry import role_metrics
    spec=style['font_roles'][role]
    if width:return float(width)*(spec.get('scale',1) if role=='memo' else 1),'authored_word_glue'
    return role_metrics(m,role,' ')['advance']*spec.get('scale',1),role


def prepare_heading_boxes(value,m,target,source):
    """Consume the native modern range binding without editing canonical text."""
    from historical_html import enabled
    bound=m['style'].get('heading_number_boxes',{}).get(target)
    if not bound or enabled(m):return value
    from model import digest
    from presentation import source_binding
    source_binding(m['unit'],bound['evidence'])
    if digest(source)!=bound['content_sha256']:
        raise ValueError('Stale heading range binding')
    if m['tasks'].get(target)!='cloze':raise ValueError('Heading boxes require a cloze section')
    first,last=bound['labels']
    def number(label):
        digit=re.escape(label)
        return r'(?:\[\s*'+digit+r'\s*\]|［\s*'+digit+r'\s*］|[（(]\s*'+digit+r'\s*[）)]|'+digit+')'
    pattern=re.compile(r'(?<![0-9０-９])('+number(first)+r')(\s*から\s*)('+number(last)+r')(?![0-9０-９])')
    soup=BeautifulSoup(source_html(value),'html.parser')
    hits=[(node,match) for node in soup.find_all(string=True)
          if not any(p.name in ('ruby','rt','rp') or p.has_attr('data-cloze-label') for p in node.parents)
          for match in pattern.finditer(str(node))]
    if len(hits)!=1:raise ValueError('Heading range must occur exactly once in an intact text run')
    node,match=hits[0];raw=str(node);parts=[NavigableString(raw[:match.start()])]
    for group,label in ((1,first),(3,last)):
        if group==3:parts.append(NavigableString(match[2]))
        box=span(soup,'',match[group],**{'data-cloze-label':label,'data-cloze-display':label})
        parts.append(box)
    parts.append(NavigableString(raw[match.end():]));node.replace_with(*parts)
    result={'html':str(soup)}
    a,b=Projection(value),Projection(result)
    if a.text!=b.text or a.ruby!=b.ruby:raise ValueError('Heading boxes changed source text/ruby')
    return result


def prepare_bound_inline(value,m,context='body',target=None,source_value=None):
    """Resolve whole-field bindings before a semantic layout splits the field."""
    style=m['style']
    original=value if source_value is None else source_value
    if context=='heading' and target:value=prepare_heading_boxes(value,m,target,original)
    if target:
        from historical_html import prepare_field
        value=prepare_field(value,m,target)
    bound=style.get('inline_presentations',{}).get(target+'/heading' if context=='heading' and target else target)
    if bound:value=prepare_inline(value,bound,original)
    cloze=style.get('inline_cloze_boxes',{}).get(target)
    if cloze:
        numbers={i['id']:m['layout']['items'][i['id']]['printed_label']['value']
                 for s in m['document']['sections'] if m['tasks'][s['id']]=='cloze'
                 for i in s['items'] if 'stem'in i}
        value=prepare_clozes(value,cloze,numbers,source_value)
    if target and m['layout'].get('word_groups') is not None:
        from word_groups import validate, prepare
        from model import iter_fields
        if '_web_groups' not in m:
            m['_web_groups']=validate(m)
            m['_web_group_sources']={f['owner']+'/'+f['slot']:f['value'] for f in iter_fields(m['document'])}
        slot=target if '/options/' in target else target+('/heading' if context=='heading' else '/stem' if context=='question' else '/content')
        if slot in m['_web_groups']:
            value=prepare(value,m['_web_group_sources'][slot],m['_web_groups'][slot])
    return value


def render_inline(value,m,context='body',target=None,*,font_target=None):
    style=m['style']; role='heading' if context=='heading' else 'example' if context=='example' else 'body'
    value=prepare_bound_inline(value,m,context,target)
    if context!='heading':
        from workbook_typography import prepare as prepare_workbook_fonts
        owner=(target or font_target or '').split('/')[0]
        value=prepare_workbook_fonts(value,[r for r in m.get('workbook_typography',{}).get('local',{}).get('spans',[]) if r['target']==owner])
    from label_separators import prepare as label_separators
    value,_=label_separators(value,presentation=False)
    dimensions={'inner_width_em':style.get('blank_inner_width_em',2.8),
                'side_space_em':style.get('blank_side_space_em',.45),
                'digit_side_space_em':style.get('blank_digit_side_space_em',.45),
                'punctuation_side_space_em':0,
                **style.get('answer_blank_roles',{}).get(role,{})}
    from historical_html import enabled as old_enabled
    value,_=prepare_blanks(value,role,dimensions,compact_question=context=='question',historical_underline_samples=old_enabled(m))
    soup=BeautifulSoup(source_html(value),'html.parser')
    for table in soup.select('table[data-ordinary-choice-row]'):
        grid = soup.new_tag('div', attrs={'class': 'example-native-options', 'data-ordinary-choice-row': 'true'})
        for cell in table.find_all('td'):
            cell.name = 'span'
            grid.append(cell.extract())
        table.replace_with(grid)
    for marker in soup.select('[data-inline-gap-em]'):
        marker['style'] = f'display:inline-block;width:{float(marker["data-inline-gap-em"]):g}em;height:0'
    for bracket in soup.select('[data-fullwidth-bracket]'):
        bracket['style'] = 'font-feature-settings:"palt" 0;text-spacing-trim:space-all'
    for padding in soup.select('[data-email-paragraph-padding]'):
        if padding['data-email-paragraph-padding']!='zero':raise ValueError('Unsupported email paragraph padding')
        # Preserve the canonical space without adding ink, indent or line depth.
        padding['style']='display:inline-block;width:0;height:0;overflow:hidden;'
    from image_html import present as present_images
    present_images(soup,m)
    # Editorial HTML can carry capture-time page colors and pixel dimensions.
    # The composed native roles own those surfaces; retain semantic alignment
    # and the existence of an unbound rectangle, using shared reader geometry.
    for node in soup.select('[style]'):
        if 'var(--' in node['style']:continue
        if node.name not in ('div','section','p','center','h1','h2','h3','h4','table','tr','td','th','hr'):continue
        props=dict(part.split(':',1) for part in node['style'].split(';') if ':' in part)
        props={k.strip():v.strip() for k,v in props.items()}
        if node.name in ('div','section') and any(k.startswith('border') for k in props):
            node['data-native-frame']='rules' if 'border-top' in props and 'border' not in props else 'box'
            node['class']=[*node.get('class',[]),'source-native-frame']
        kept={k:v for k,v in props.items() if k in ('text-align','border-collapse','overflow-x')}
        node['style']=''.join(k+':'+v+';' for k,v in kept.items())
    from historical_html import enabled as old_enabled
    if context=='heading' and not old_enabled(m):
        from selector_html import present as present_selectors
        present_selectors(soup,m)
        if style.get('approved_administrative_numerals'):
            for node in list(soup.find_all(string=True)):
                if any(p.name in ('rt','rp') or p.has_attr('data-choice-selector') for p in node.parents):continue
                pieces=re.split(r'([0-9０-９]+)',str(node))
                if len(pieces)>1:node.replace_with(*[span(soup,'instruction-digit',part,**{'data-instruction-digit':'instruction'}) if j%2 else NavigableString(part) for j,part in enumerate(pieces) if part])
    if context=='heading' and old_enabled(m):
        # The native Old selector role applies to the bounded ...から form.
        # Other four-choice runs retain the instruction face and their own
        # horizontal digit width. Mark before splitting Latin/Japanese text.
        old=old_enabled(m)
        for node in list(soup.find_all(string=True)):
            if node.parent.name in ('rt','rp'):continue
            pattern=r'[1１]\s*・\s*[2２]\s*・\s*[3３]\s*・\s*[4４]'
            if old:pattern+='|(?<![0-9０-９])[1１][ \u3000]*[2２][ \u3000]*[3３][ \u3000]*[4４](?=[ \u3000]*から)'
            raw=str(node);parts=[];end=0
            for match in re.finditer(pattern,raw):
                parts.append(NavigableString(raw[end:match.start()]))
                suffix=re.match(r'[ \u3000]*から',raw[match.end():])
                bounded=bool(suffix)
                suffix_break=old and bounded and style.get('heading_selector_suffix_break',False) and '・' in match[0]
                group=span(soup,'heading-selector' if old and bounded and not suffix_break else 'instruction-number-sequence')
                digits=span(soup,'heading-selector') if suffix_break else group
                dotted='・' in match[0]
                pieces=re.split(r'([1-4１-４])',match[0])
                for j,part in enumerate(pieces):
                    if not part:continue
                    if re.fullmatch(r'[1-4１-４]',part):
                        digit=span(soup,'instruction-digit',part,**{'data-instruction-digit':'selector' if bounded else 'instruction'})
                        if not old and bounded and suffix[0]=='から' and part in '4４':digit['data-selector-last-gap']='true'
                        digits.append(digit)
                        if old and bounded and not dotted and part not in '4４' and not pieces[j+1]:
                            digits.append(span(soup,'instruction-digit-gap',style='display:inline-block;width:calc(var(--nominal-em) * .5)'))
                    elif dotted:
                        # Native selector separators consume source whitespace.
                        for token in re.split(r'([ \u3000]+)',part):
                            if token:digits.append(span(soup,'source-literal sr-only',token) if token.isspace() else NavigableString(token))
                    else:digits.append(NavigableString(part))
                if suffix_break:group.append(digits)
                if old and bounded:
                    if suffix_break:group.append(soup.new_tag('wbr'))
                    if suffix[0]=='から':group.append(span(soup,'instruction-digit-gap',style='display:inline-block;width:calc(var(--nominal-em) * .3)'))
                    group.append(NavigableString(suffix[0]))
                parts.append(group);end=match.end()+(len(suffix[0]) if old and bounded else 0)
            if parts:
                parts.append(NavigableString(raw[end:]));node.replace_with(*parts)
    for node in soup.select('[data-cloze-label]'):
        display=node.get('data-cloze-display',node['data-cloze-label'])
        visual_atom(soup,node,'cloze-slot',display)
    for node in soup.select('[data-answer-blank]'):
        node['style']=';'.join('--blank-'+key+':'+node['data-blank-'+key] for key in ['inner','left','right'])
        visual_atom(soup,node,'context-blank','')
        visual=node.select_one('.visual-only');visual.append(span(soup,'blank-open','（'));visual.append(span(soup,'blank-inner'));visual.append(span(soup,'blank-close','）'))
        keep_blank_punctuation(node)
    for node in soup.select('[data-blank-padding]'):node['class']='source-literal sr-only'
    for node in soup.select('[data-instruction-boundary]'):node['class']='instruction-boundary'
    for node in soup.select('[data-authored-word-gap]'):node['class']='authored-word-gap'
    for node in soup.select('[data-paired-label-display]'):
        visual_atom(soup,node,'paired-source-label',node['data-paired-label-display'])
    # RichTeX also draws an empty underlined element as a ruled answer slot.
    # N3's instructions use this representation instead of underscore text.
    for node in soup.select('u'):
        if not node.get_text().strip():
            node.name='span';node['class']='answer-slot'
            node.append(span(soup,'slot-glyph visual-only','\u200b',**{'aria-hidden':'true'}))
    # RichTeX.text treats each contiguous underscore run as one ruled slot.
    for node in list(soup.find_all(string=True)):
        if any(p.name in ['rt','rp'] or set(p.get('class',[]))&{'source-literal','visual-only'} for p in node.parents):continue
        # RichTeX owns ASCII padding beside ruled slots. Retain the source
        # spaces without adding word glue on top of the slot's two side gaps.
        raw=str(node)
        atoms=r'(?<![A-Za-z0-9])_+(?![A-Za-z0-9])|＿+|★'
        if old_enabled(m):
            # Match RichTeX's historical quantity rule: 2____ has one whole
            # answer line, whereas underscores adjoining letters are literal.
            atoms=r'(?<![A-Za-z_])_+(?![A-Za-z_])|＿+|★'
        raw_parts=re.split('('+atoms+')',raw)
        for j in range(0,len(raw_parts),2):
            part=raw_parts[j];left=len(part)-len(part.lstrip(' ')) if j else 0
            right=len(part)-len(part.rstrip(' ')) if j+1<len(raw_parts) else 0
            if left or right:
                # Keep whitespace in its original position, including runs
                # between adjacent slots (which must only be consumed once).
                if left+right>len(part):left=len(part);right=0
                raw_parts[j]=(' ' * left,part[left:len(part)-right if right else None],' ' * right)
        pieces=[]
        latin=r'[A-Za-z0-9_][A-Za-z0-9_.,:/@%+\-]*'
        for j,part in enumerate(raw_parts):
            if isinstance(part,tuple):
                before,middle,after=part
                if before:pieces.append(span(soup,'source-literal sr-only',before))
                pieces.extend(re.split('('+latin+r'|[()])',middle))
                if after:pieces.append(span(soup,'source-literal sr-only',after))
            elif j%2:
                # Only the original context-sensitive match denotes a slot.
                # A later Latin split must not turn an address's literal _
                # into a new slot after losing its neighboring characters.
                slot=span(soup,'star-slot' if part=='★' else 'answer-slot')
                slot.append(span(soup,'slot-glyph star-glyph' if part=='★' else 'slot-glyph',part));pieces.append(slot)
            else:pieces.extend(re.split('('+latin+r'|[()])',part))
        if len(pieces)==1:continue
        nodes=[]
        for piece in pieces:
            if not piece:continue
            if not isinstance(piece,str):nodes.append(piece);continue
            if piece in ['(',')']:nodes.append(span(soup,'ascii-parenthesis tex-latin',piece))
            elif re.fullmatch(latin,piece):
                nodes.append(span(soup,'tex-latin',piece))
            else:nodes.append(NavigableString(piece))
        node.replace_with(*nodes)
    # Latin/Japanese boundary glue belongs to the nominal TeX em, not the
    # reduced Japanese glyph em. Do not add it around punctuation or slots.
    jp=r'[\u3040-\u30ff\u3400-\u9fff々]'
    def adjacent(node,direction):
        other=getattr(node,direction+'_sibling');spaces=[]
        while isinstance(other,NavigableString) and not str(other).strip(' \u3000'):
            spaces.append(other);other=getattr(other,direction+'_sibling')
        if isinstance(other,NavigableString):
            raw=str(other)
            match=re.search(r'[ \u3000]+$',raw) if direction=='previous' else re.match(r'^[ \u3000]+',raw)
            if match:
                space=NavigableString(match[0]);content=NavigableString(raw[:match.start()] if direction=='previous' else raw[match.end():])
                other.replace_with(*([content,space] if direction=='previous' else [space,content]))
                spaces.append(space);other=content
        text=Projection({'html':str(other)}).text if other is not None else ''
        return text,spaces,other
    for node in soup.select('.tex-latin'):
        for direction,edge,cls in [('previous','before','mixed-before'),('next','after','mixed-after')]:
            text,spaces,other=adjacent(node,direction)
            if not (re.search(jp+'$',text) if edge=='before' else re.match(jp,text)):continue
            if spaces:
                # Explicit ASCII whitespace has a font space (or authored
                # pedagogical glue), even when Japanese word-space is zero.
                # It replaces automatic script glue; never add both.
                raw=''.join(map(str,reversed(spaces) if direction=='previous' else spaces))
                marker=span(soup,'mixed-word-space',raw)
                marker['style']='--source-wide-spaces:'+str(raw.count('\u3000'))+';'
                if '\u3000' not in raw:
                    width,space_role=native_ascii_space(m,context,font_target or target,node)
                    marker['style']+=f'--source-space-width:calc(1em / var(--glyph-scale) * {width});'
                    marker['data-native-space-role']=space_role
                    marker['data-native-space-em']=str(width)
                spaces[0].replace_with(marker)
                for space in spaces[1:]:space.extract()
            elif other is not None:
                node['class'].append(cls)
    if style.get('word_space_em',0):
        for node in list(soup.find_all(string=True)):
            if any(p.name in ('rt','rp') or p.has_attr('data-japanese-label-space') or set(p.get('class',[]))&{'source-literal','visual-only','answer-slot','star-slot','mixed-word-space'} for p in node.parents):continue
            pieces=re.split(r'([ \u3000]+)',str(node))
            if len(pieces)<2:continue
            nodes=[]
            for piece in pieces:
                if not piece:continue
                if re.fullmatch(r'[ \u3000]+',piece):
                    gap=span(soup,'tex-word-space',piece)
                    if '\u3000' in piece:gap['style']='width:calc(var(--nominal-em) * '+str(piece.count('\u3000'))+' + var(--nominal-em) * var(--word-space-em,0) * '+str(piece.count(' '))+')'
                    nodes.append(gap)
                else:nodes.append(NavigableString(piece))
            node.replace_with(*nodes)
    from font_html import present as present_fonts
    present_fonts(soup,m,context,font_target or target)
    from historical_html import present_inline
    present_inline(soup,m)
    from workbook_typography import html_fonts
    html_fonts(soup)
    if context!='heading' and m.get('modern_wakachi'):
        bind_groups(soup,web=True)
        for gap in soup.select('.tex-word-space,.mixed-word-space,.authored-word-gap'):
            if gap.previous_sibling is None or gap.next_sibling is None:
                continue
            raw=gap.get_text()
            if raw not in ('',' ','　') or gap.find_parent(['rt','rp']):
                continue
            gap['class']=[*classes(gap),'wakachi-wide-gap' if raw=='　' else 'wakachi-gap']
            if raw == ' ' and gap.has_attr('data-native-space-em'):
                # A discardable separator uses font-size:0. Its own em has zero advance.
                width = gap['data-native-space-em']
                gap['style'] = f'--source-space-width:calc(var(--nominal-em) * {width});'
    return str(soup)


HEADING_PHRASES = '選びなさい。|えらびなさい。|えらんで|ください。|いちばん|最もよい|あります|答えは|いい|から'.split('|')
HEADING_PHRASE_PATTERN = re.compile('(' + '|'.join(map(re.escape, HEADING_PHRASES)) + ')')


def heading_flow(soup):
    """Give the browser discardable separators and breaks outside protected groups."""
    protected = ('ruby,rt,rp,u,[data-double-underline],[data-bounded-word],'
                 '.heading-label,.source-literal,.visual-only,.answer-slot,.star-slot,'
                 '.context-blank,.cloze-slot,.heading-selector,.instruction-number-sequence')
    import soupsieve
    blocked = soupsieve.compile(protected)

    for gap in soup.select('.tex-word-space,.mixed-word-space'):
        if any(blocked.match(parent) for parent in gap.parents):
            continue
        raw = gap.get_text()
        if not re.fullmatch(r'[ 　]+', raw):
            continue
        parts = []
        for spaces in re.findall(r' +|　+', raw):
            wide = spaces.startswith('　')
            kind = 'heading-wide-space' if wide else 'heading-word-space'
            part = span(soup, kind, spaces, **{'data-preserved-space':'true'})
            if not wide and gap.has_attr('data-native-space-em'):
                width = gap['data-native-space-em']
                part['style'] = f'--heading-space-width:calc(var(--local-em) * {width})'
                for key in ('data-native-space-em','data-native-space-role'):
                    part[key] = gap[key]
            parts.append(part)
        gap.replace_with(*parts)

    # Work with rendered siblings. An authored space already has a break, and
    # a historical selector can own a separate, intentional break before から.
    def previous(node):
        for sibling in node.previous_siblings:
            if isinstance(sibling, NavigableString):
                if sibling:
                    return str(sibling)
            elif sibling.name in ('br','wbr') or set(sibling.get('class',[])) & {'heading-label','instruction-boundary'}:
                return ''
            else:
                text = sibling.get_text()
                if text:
                    return text
        return ''

    for group in soup.select('.heading-selector,.heading-no-break'):
        if 'heading-selector' in group.get('class',[]):
            if 'instruction-number-sequence' in group.parent.get('class',[]):
                group = group.parent
            if any(blocked.match(parent) for parent in group.parents):
                continue
            left = previous(group)
            if left:
                last = left[-1]
                if (last.isalpha() and not last.isascii()) or last in '、。）」』】〉》］':
                    group.insert_before(soup.new_tag('wbr'))
        elif group.get_text() in HEADING_PHRASES:
            sibling = group.previous_sibling
            if (getattr(sibling, 'name', None) == 'span'
                    and 'heading-no-break' in sibling.get('class',[])
                    and sibling.get_text() in HEADING_PHRASES
                    and not any(blocked.match(parent) or 'heading-no-break' in parent.get('class',[]) for parent in group.parents)):
                group.insert_before(soup.new_tag('wbr'))


def render_section_heading(value,m,target):
    """Use the native field splits before measuring a numbered instruction."""
    source=value
    value=prepare_bound_inline(value,m,'heading',target)
    title=intro=None
    titles=m['style'].get('booklet_titles',{})
    introductions=m['style'].get('heading_introductions',{})
    if target in titles:
        from booklet_titles import split
        title,value=split(value,titles[target],source)
    if target in introductions:
        from heading_introductions import split
        value,intro=split(value,introductions[target],source)
    parts=['<header class="source-heading">']
    if title is not None:
        parts.append(f'<div class="booklet-title" style="--booklet-title-after-pt:{titles[target].get("after_pt",12)}">'+render_inline(title,m,'body')+'</div>')
    parts.append('<h2 class="section-heading">'+render_heading(value,m,target,prepared=True)+'</h2>')
    if intro is not None:
        role=introductions[target]['role']
        parts.append(f'<p class="heading-introduction" data-introduction-role="{role}" style="--heading-intro-after-pt:{m["style"].get(role+"_intro_after_pt",23 if role=="passage" else 6)}">'+render_inline(intro,m,'body')+'</p>')
    parts.append('</header>')
    return ''.join(parts)


def render_heading(value,m,target,*,prepared=False):
    # Whole-field hashes/ruby bind before the TeX label consumer runs. Blank
    # neighbour detection must run afterwards: a leading blank has no digit
    # on its left merely because the administrative label ends in a number.
    if not prepared:value=prepare_bound_inline(value,m,'heading',target)
    soup=BeautifulSoup(source_html(value),'html.parser')
    for br in soup.find_all('br'):br.replace_with(' ')
    instruction_boundaries(soup)
    label=None
    for node in soup.find_all(string=True):
        if node.parent.name in ['rt','rp'] or not node.strip():continue
        from historical_html import enabled as old_enabled
        number=r'(?:[0-9０-９]{1,2}|[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ])' if old_enabled(m) else r'[0-9０-９]{1,2}'
        match=re.match(r'^(\s*)(問題|もんだい)(\s*)('+number+r')([.:：．]?\s*)',str(node))
        if match:
            label=(match[2],match[4],match[0])
            node.replace_with(str(node)[match.end():])
        break
    task=m.get('tasks',{}).get(target)
    heading_model={**m,'style':{**m['style'],**m['style'].get('task_overrides',{}).get(task,{})}}
    rendered=BeautifulSoup(render_inline({'html':str(soup)},heading_model,'heading'),'html.parser')
    # RichTeX turns the administrative _★_ sample into one starred rule.
    # Its original three characters remain canonical; scored rows keep all
    # their independent slots and this never supplies a rearrangement order.
    for star in list(rendered.select('.star-slot')):
        def neighbour(direction):
            nodes=[];node=getattr(star,direction)
            while node is not None:
                if isinstance(node,NavigableString) and not node.strip():nodes.append(node)
                elif getattr(node,'name',None)=='span' and 'source-literal' in node.get('class',[]):nodes.append(node)
                else:return node,nodes
                node=getattr(node,direction)
            return None,nodes
        left,before=neighbour('previous_sibling');right,after=neighbour('next_sibling')
        if not all(getattr(n,'name',None)=='span' and 'answer-slot' in n.get('class',[]) for n in (left,right)):continue
        sequence=[left,*reversed(before),star,*after,right]
        raw=''.join(n.get_text() if hasattr(n,'get_text') else str(n) for n in sequence)
        atom=span(rendered,'star-slot');atom.append(span(rendered,'source-literal sr-only',raw));atom.append(span(rendered,'slot-glyph star-glyph visual-only','★',**{'aria-hidden':'true'}))
        star.insert_before(atom)
        for node in sequence:node.extract()
    # An outer paragraph is the instruction container, not a second line or
    # another one-character indent (the same outer \Para consumed by TeX).
    while len([n for n in rendered.contents if getattr(n,'name',None) or str(n).strip()])==1:
        outer=next(n for n in rendered.contents if getattr(n,'name',None) or str(n).strip())
        if getattr(outer,'name',None) not in ('p','div'):break
        outer.unwrap()
    if label:
        lead=span(rendered,'heading-label')
        lead.append(span(rendered,'source-literal sr-only',label[2]))
        visual=span(rendered,'heading-label-visual visual-only',**{'aria-hidden':'true'})
        visual.append(NavigableString(label[0]));visual.append(span(rendered,'heading-number'+(' tex-latin' if label[1].isascii() else ''),label[1]))
        lead.append(visual);rendered.insert(0,lead)
        if m['style'].get('approved_administrative_numerals'):
            visual.select_one('.heading-number')['data-instruction-digit']='task'
            from font_html import heading_digits
            heading_digits(rendered,m,nodes=[visual.select_one('.heading-number')])
    for br in rendered.find_all('br'):br.replace_with(' ')
    for node in list(rendered.find_all(string=True)):
        if any(p.name in ('rt','rp') or set(p.get('class',[]))&{'source-literal','visual-only','heading-label'} for p in node.parents):continue
        pieces=HEADING_PHRASE_PATTERN.split(str(node))
        if len(pieces)>1:node.replace_with(*[span(rendered,'heading-no-break',part) if j%2 else NavigableString(part) for j,part in enumerate(pieces) if part])
    # JFM's middle dot is a half-width cell; each side gets the explicitly
    # authored HeadingChoiceGap/2, as in RichTeX.heading.finish.
    for node in list(rendered.find_all(string=True)):
        if any(set(p.get('class',[]))&{'source-literal','visual-only','answer-slot','heading-label'} for p in node.parents):continue
        pieces=re.split(r'([・、。])',str(node))
        if len(pieces)>1:
            node.replace_with(*[span(rendered,'heading-dot' if p=='・' else 'heading-punctuation',p) if p in '・、。' and p else NavigableString(p) for p in pieces if p])
    for node in rendered.select('.tex-latin'):
        node['class']=[c for c in node['class'] if c not in ['mixed-before','mixed-after']]
        if node.get_text()=='4' and node.next_sibling and str(node.next_sibling).startswith('から'):node['class'].append('selector-last')
    # A half-width inline-block is opaque to the browser's Japanese line
    # breaker. Bind punctuation to its preceding character so a narrow Auto
    # layout cannot start a line with a comma, full stop or choice separator.
    for node in rendered.select('.heading-punctuation,.heading-dot'):
        previous=node.previous_sibling
        group=span(rendered,'heading-no-break')
        if isinstance(previous,NavigableString) and str(previous).strip():
            text=str(previous);previous.replace_with(NavigableString(text[:-1]))
            group.append(NavigableString(text[-1]));node.wrap(group)
        elif getattr(previous,'name',None)=='span' and set(previous.get('class',[])) & {'tex-latin','instruction-digit'}:
            previous.wrap(group);group.append(node.extract())
        if node.string == '、':
            following = node.string.find_next(string=lambda t: t and t.parent.name not in ('rt', 'rp'))
            if following and following[0].isalnum():
                # In running text the comma owns a normal Japanese cell.
                # Keep authored word gaps and adjacent punctuation as composed.
                node.unwrap()
    from historical_html import heading as old_heading
    old_heading(rendered,m,target)
    heading_flow(rendered)
    if spaced_task(m,task):
        bind_groups(rendered,web=True)
    return str(rendered)
