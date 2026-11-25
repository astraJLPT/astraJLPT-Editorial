"""Exact Old paragraph roles, with preserved canonical wording and ruby."""
import re
from bs4 import BeautifulSoup
from model import Projection, digest
from presentation import source_binding

ROLES = {'citation','note','numbered_introduction','document_headline','source_annotation','question_instruction','labeled_paragraph','embedded_query'}


def split_deferred_figure(source_value, figure, binding, unit):
    """Keep exact source prose roles when a graph moves after its question."""
    # Validate every role against the original before partitioning its display.
    prepare(source_value, binding, unit)
    paragraphs = {Projection({'html': str(p)}).text.strip()
                  for p in BeautifulSoup(figure['html'], 'html.parser').find_all('p')}
    figure_roles = [r for r in binding['paragraphs'] if r['text'] in paragraphs]
    body_roles = [r for r in binding['paragraphs'] if r['text'] not in paragraphs]
    if figure_roles:
        figure = prepare(figure, {**binding, 'content_sha256': digest(figure),
                                 'paragraphs': figure_roles}, unit)
    return {**binding, 'paragraphs': body_roles}, figure


def question_citations(model):
    """Bind a separate attribution to its immediately preceding image choices."""
    result={}
    for section in model['document']['sections']:
        for index,item in enumerate(section['items']):
            binding=model['layout']['items'][item['id']].get('historical_prose',{})
            link=binding.get('after_question')
            if link is None:continue
            if model['schema_version']!='4.1.0' or model.get('exam',{}).get('generation')!='historical-1991-2009':
                raise ValueError('Question citation requires the Old written contract')
            if model['layout']['sections'][section['id']]['task']!='reading' or item.get('type')!='passage' or index==0:
                raise ValueError('Question citation must follow a reading question')
            previous=section['items'][index-1]
            if set(link)!={'item_id','options_sha256'} or previous['id']!=link['item_id'] or 'stem'not in previous or digest(previous.get('options'))!=link['options_sha256']:
                raise ValueError('Stale question citation relationship')
            options=previous.get('options',[])
            if len(options)!=4 or any(not isinstance(v,dict) or len(BeautifulSoup(v.get('html',''),'html.parser').find_all('img'))!=1 for v in options):
                raise ValueError('Question citation requires four image choices')
            if digest(item.get('content'))!=binding['content_sha256'] or not isinstance(item.get('content'),dict) or binding.get('frame_sequence'):
                raise ValueError('Stale question citation content')
            specs=binding['paragraphs'];soup=BeautifulSoup(item['content']['html'],'html.parser')
            if len(specs)!=1 or specs[0]['role']!='citation' or len(soup.find_all('p'))!=1 or soup.find(['img','table']) or Projection(item['content']).text.strip()!=specs[0]['text']:
                raise ValueError('Attached attribution must be one complete citation paragraph')
            # Also exercise the exact attribution syntax and source authority.
            prepare(item['content'],binding,model['unit'])
            result[item['id']]=dict(previous_question=previous['id'],options_sha256=link['options_sha256'],content_sha256=binding['content_sha256'])
    return result


def prepare(value, binding, unit, source_value=None):
    original=value if source_value is None else source_value
    if digest(original)!=binding['content_sha256'] or not isinstance(value,dict):
        raise ValueError('Stale historical prose binding')
    source_binding(unit,binding['evidence'])
    before=Projection(value);soup=BeautifulSoup(value['html'],'html.parser')
    seen=set()
    for spec in binding['paragraphs']:
        role,text=spec['role'],spec['text']
        if role not in ROLES or (role,text) in seen:raise ValueError('Invalid/duplicate historical paragraph role')
        seen.add((role,text))
        hits=[n for n in soup.find_all('p') if Projection({'html':str(n)}).text.strip()==text]
        if len(hits)!=1:raise ValueError(f'Historical role needs one exact complete paragraph: {unit}/{role}/{text!r}, found {len(hits)}')
        # Some source attributions end immediately after the book title.
        # They still require an exact, source-bound complete paragraph.
        citation=(re.fullmatch(r'[（(].+(?:による|より)[。.]?[）)]',text)
                  or re.fullmatch(r'[（(][^（(\n]+『[^』\n]+』[）)]',text))
        if 'citation_variant' in spec or 'publisher' in spec:
            # A printed publisher is an attribution ending, not permission to
            # append an unprinted 「による」. Require the declared literal
            # publisher and one source-bound complete author/title paragraph.
            publisher=spec.get('publisher','')
            title_ending=(re.fullmatch(r'[（(][^（(『』\n]+『[^』\n]+』'+re.escape(publisher)+r'[）)]',text)
                          or re.fullmatch(r'[（(]参考：[^（(「」\n]+「[^「」\n]+」「[^「」\n]+」'+re.escape(publisher)+r'[）)]',text))
            if (role!='citation' or spec.get('citation_variant')!='publisher_ending'
                    or not re.fullmatch(r'[一-龯々ぁ-ゖァ-ヺー・A-Za-z0-9]{1,30}',publisher)
                    or not title_ending):
                raise ValueError('Invalid exact publisher-ending citation')
            citation=True
        if role=='citation' and not citation:
            raise ValueError('Historical citation must retain its exact attribution')
        if role=='note' and not re.match(r'^[（(]注[0-9０-９]*[）)].+[:：]',text):
            raise ValueError('Historical definition must have its source label, term and colon')
        if role=='numbered_introduction' and not re.fullmatch(r'[（(][0-9０-９]+[）)].+[。．]',text):
            raise ValueError('Historical introduction needs its numbered source sentence')
        if role=='document_headline' and (hits[0].get('data-document-headline')!='true' or not hits[0].find_parent('div',attrs={'data-historical-framed-document':'single'})):
            raise ValueError('Historical headline needs its explicit source document role')
        if role=='source_annotation' and not text.startswith('＊印以下の文は、'):
            raise ValueError('Historical source annotation needs its exact asterisk notice')
        if role=='question_instruction':
            if (not re.fullmatch(r'◎ここまで読んで、次の問[1-9][0-9]*から問[1-9][0-9]*に答えなさい。',text)
                    or hits[0]!=soup.find_all('p')[-1] or hits[0].find_parent('div')
                    or spec.get('page_boundary')!='source_question_group_start'):
                raise ValueError('Question-group instruction requires its exact terminal source paragraph')
        if role=='labeled_paragraph':
            label=spec.get('margin_label','')
            parts=[n for n in hits[0].contents if str(n).strip()]
            if (not re.fullmatch(r'第[1-9]段落',label) or spec.get('margin_bracket')!='angled_caps'
                    or not text.startswith(label) or len(text)<=len(label)
                    or not parts or getattr(parts[0],'name',None)!='span'
                    or parts[0].attrs!={'data-historical-margin-label':'true'}
                    or parts[0].find() or parts[0].get_text()!=label
                    or len(hits[0].select('span[data-historical-margin-label]'))!=1):
                raise ValueError('Labeled source paragraph needs its exact leading label and bracket')
            hits[0]['data-historical-margin-label']=label
            hits[0]['data-historical-margin-bracket']='angled_caps'
        elif 'margin_label'in spec or 'margin_bracket'in spec:
            raise ValueError('Margin label belongs only to an exact labeled paragraph')
        if role=='embedded_query':
            if (not text.startswith('【しつもん】') or len(text)<=6
                    or hits[0]!=soup.find_all('p')[-1] or hits[0].attrs
                    or hits[0].find(['img','table','br','p','div'])):
                raise ValueError('Embedded query requires its complete terminal plain paragraph')
            # Keep this role inside the paragraph so dialogue line extraction
            # retains it while discarding paragraph wrappers.
            wrapper=soup.new_tag('span',attrs={'data-historical-text-role':role})
            for child in list(hits[0].contents):wrapper.append(child.extract())
            hits[0].append(wrapper)
        else:
            hits[0]['data-historical-text-role']=role
        if 'definition_arrangement' in spec:
            if role!='note' or spec['definition_arrangement']not in ['description_next_line','continuation_at_term']:
                raise ValueError('Only an exact source definition may place its description on the next line')
            hits[0]['data-historical-definition-arrangement']=spec['definition_arrangement']
        if 'inset_em'in spec:
            if role!='source_annotation'or type(spec['inset_em'])not in [int,float]or not 0<=spec['inset_em']<=2:raise ValueError('Only a source annotation may select a bounded inset')
            hits[0]['data-historical-inset']=str(spec['inset_em'])
        if 'page_boundary'in spec:
            expected={'note':'source_note_continuation','question_instruction':'source_question_group_start'}.get(role)
            if spec['page_boundary']!=expected or len(binding['evidence']['physical_pages'])<2:raise ValueError('A semantic source boundary needs its exact multi-page source binding')
            hits[0]['data-historical-page-boundary']=expected
        if 'font_pt' in spec:
            if role!='citation' or not 8<=spec['font_pt']<=12 or not spec['font_pt']<=spec.get('baseline_pt',0)<=20:
                raise ValueError('Only a citation may use an explicitly calibrated compact type size')
            hits[0]['data-historical-font-pt']=str(spec['font_pt'])
            hits[0]['data-historical-baseline-pt']=str(spec['baseline_pt'])
        if 'following_notes_may_break'in spec:
            if role!='citation'or type(spec['following_notes_may_break'])is not bool:
                raise ValueError('Only an exact citation can release its following note keep')
            if spec['following_notes_may_break']:hits[0]['data-historical-following-notes-may-break']='true'
    if binding.get('frame_sequence'):
        frames=soup.select('div[data-historical-framed-document="single"]')
        sequence=soup.select('div[data-historical-order-flow="vertical"]')
        if len(frames)!=5 or len(sequence)!=1:raise ValueError('Expected one initial and four alternative source frames')
        for n,node in enumerate(frames):node['data-historical-frame-role']='passage' if n==0 else 'alternative'
        sequence[0]['data-historical-compact-sequence']='true'
    after=Projection({'html':str(soup)})
    if before.text!=after.text or before.ruby!=after.ruby:raise ValueError('Historical role changed content/ruby')
    return {'html':str(soup)}



def embedded_query_gaps(model):
    """Apply family spacing only between consecutive complete query contexts."""
    params=model['style'].get('historical_typography',{}).get('embedded_query',{})
    if 'question_gap_pt'not in params:return {}
    gap=params['question_gap_pt']
    if (model.get('exam',{}).get('generation')!='historical-1991-2009'
            or type(gap)not in[int,float]or not 0<=gap<=60):
        raise ValueError('Invalid Old embedded-query context gap')
    result={}
    for section in model['document']['sections']:
        if model['layout']['sections'][section['id']]['task']!='reading':continue
        previous=False
        for item in section['items']:
            binding=model['layout']['items'][item['id']].get('historical_stem_prose',{})
            current='stem'in item and any(r['role']=='embedded_query'for r in binding.get('paragraphs',[]))
            if current and previous:result[item['id']]=gap
            previous=current
    return result


def render(conv,node,context):
    role=node['data-historical-text-role']
    if role not in ROLES or not getattr(conv,'source_target_markers',False):
        raise ValueError('Invalid historical paragraph role consumer')
    from example_layout import slice_inline
    raw=node.decode_contents();plain=Projection({'html':raw}).text
    value=lambda a,b:conv.value({'html':slice_inline(raw,a,b)},'option')if a<b else''
    conv.features.append(dict(kind='historical_paragraph_role',role=role,text=plain,canonical_changed=False))
    if role=='embedded_query':
        params=getattr(conv,'historical_embedded_query',None)
        limits={'left_inset_em':(0,4),'width_em':(5,9),'continuation_pullback_em':(.5,1.5),'before_pt':(0,30)}
        if (node.name!='span' or not plain.startswith('【しつもん】') or not isinstance(params,dict)
                or not set(limits)<=set(params) or set(params)-set(limits)-{'label_font_role','question_gap_pt'}
                or params.get('label_font_role','body')not in ['body','task_label']
                or ('question_gap_pt'in params and(type(params['question_gap_pt'])not in[int,float]or not 0<=params['question_gap_pt']<=60))
                or any(type(params[k])not in [int,float]or not a<=params[k]<=b for k,(a,b)in limits.items())):
            raise ValueError('Embedded query lacks valid family geometry')
        start=len('【しつもん】')
        while start<len(plain)and plain[start].isspace():start+=1
        body=conv.value({'html':slice_inline(raw,start,len(plain))},'body')
        first=params['left_inset_em']+params['width_em'];continuation=first-params['continuation_pullback_em']
        label_font=(r'\TaskLabelLatin\TaskLabelJapanese\bfseries 'if params.get('label_font_role','body')=='task_label'else r'\rmfamily\mcfamily\mdseries ')
        conv.features.append(dict(kind='historical_embedded_query',label='【しつもん】',**params,canonical_changed=False))
        # Reset the parent question's hanging state; reserve the label only on
        # this first query line, and return one moji on continuations.
        return (r'\par\vspace{'+str(params['before_pt'])+r'pt}\begingroup'
                r'\hangindent=0pt\hangafter=1\leftskip='+str(continuation)+r'em\relax'
                r'\parindent='+str(params['continuation_pullback_em'])+r'em\relax'
                r'\rightskip=0pt plus 1fil\relax\indent\llap{\makebox['+str(params['width_em'])
                +r'em][l]{{'+label_font+r'【しつもん】}}}'+body+r'\par\endgroup')
    if role=='labeled_paragraph':
        label=node.get('data-historical-margin-label','')
        if not re.fullmatch(r'第[1-9]段落',label)or node.get('data-historical-margin-bracket')!='angled_caps':
            raise ValueError('Labeled source paragraph lost its bracket/label')
        content=BeautifulSoup(raw,'html.parser')
        first=content.find('span',attrs={'data-historical-margin-label':'true'})
        if first is None or first.get_text()!=label:raise ValueError('Missing canonical paragraph label')
        first.extract()
        body=conv.value({'html':str(content)},'body')
        vertical=r'\\'.join(conv.text(ch)for ch in label)
        conv.features.append(dict(kind='historical_margin_bracket',label=label,bracket='angled_caps',canonical_changed=False))
        # The source has a straight spine with sloping caps, not a curly
        # answer brace. Draw around the naturally measured paragraph box.
        return (r'\par\noindent\begin{tikzpicture}[baseline=(body.north)]'
            +r'\node[anchor=north west,inner sep=0pt,outer sep=0pt,text width=\dimexpr\linewidth-3em\relax,align=left](body)at(3em,0){\hspace*{1em}'+body+r'};'
            +r'\draw[line width=.5pt]([xshift=-.4em]body.north west)--([xshift=-.8em,yshift=-.3em]body.north west)--([xshift=-.8em,yshift=.3em]body.south west)--([xshift=-.4em]body.south west);'
            +r'\node[anchor=east,inner sep=0pt,font=\TaskLabelLatin\TaskLabelJapanese\bfseries\fontsize{10}{11}\selectfont]at([xshift=-1.2em]body.west){\shortstack{'+vertical+r'}};'
            +r'\end{tikzpicture}\par\addvspace{7pt}')
    if role=='question_instruction':
        if node.get('data-historical-page-boundary')!='source_question_group_start':
            raise ValueError('Question-group instruction lost its semantic boundary')
        body=''.join(conv.node(c,'option')for c in node.children)
        conv.features.append(dict(kind='historical_question_group_start',text=plain,canonical_changed=False))
        return r'\par\newpage\noindent '+body+r'\par\nobreak\addvspace{8pt}'
    if role in {'document_headline','source_annotation'}:
        # Preserve inline glyph images and ruby; text-only slicing would drop
        # the clockmaker's four-stroke Roman numeral in the source annotation.
        body=''.join(conv.node(c,'option')for c in node.children)
        macro='HistoricalDocumentHeadline'if role=='document_headline'else'HistoricalSourceAnnotation'
        if role=='document_headline':body=body.replace(r'\linebreak[2]',r'\hfil\break')
        tex='\\'+macro+'{'+body+'}'
        if node.has_attr('data-historical-inset'):
            inset=node['data-historical-inset'];tex=r'{\advance\leftskip by '+inset+r'em\relax\advance\linewidth by -'+inset+r'em\relax '+tex+'}'
        return tex
    if role=='citation':
        macro='HistoricalCitationWithNoteBreak'if node.get('data-historical-following-notes-may-break')=='true'else'HistoricalCitation'
        tex='\\'+macro+'{'+value(0,len(plain))+'}'
        params=getattr(conv,'historical_citation_metrics',None)
        origin='family'
        if node.has_attr('data-historical-font-pt'):
            params=dict(font_pt=float(node['data-historical-font-pt']),baseline_pt=float(node['data-historical-baseline-pt']))
            origin='source_bound'
        if params is not None:
            if (not isinstance(params,dict) or set(params)!={'font_pt','baseline_pt'}
                    or any(type(v)not in [int,float]for v in params.values())
                    or not 8<=params['font_pt']<=12 or not params['font_pt']<=params['baseline_pt']<=20):
                raise ValueError('Invalid historical citation metrics')
            # Preserve exact pre-existing source-bound TeX number spelling.
            font=node['data-historical-font-pt']if origin=='source_bound'else str(params['font_pt'])
            leading=node['data-historical-baseline-pt']if origin=='source_bound'else str(params['baseline_pt'])
            tex=r'{\fontsize{'+font+'}{'+leading+r'}\selectfont '+tex+'}'
            conv.features.append(dict(kind='historical_citation_metrics',origin=origin,**params,canonical_changed=False))
        return tex
    if role=='numbered_introduction':
        match=re.match(r'^[（(][0-9０-９]+[）)]',plain)
        return r'\HistoricalNumberedIntroduction{'+value(0,match.end())+'}{'+value(match.end(),len(plain))+'}'
    match=re.match(r'^([（(]注[0-9０-９]*[）)])(.*?[:：])(.*)$',plain,re.S)
    if not match:raise ValueError('Historical note definition changed')
    # Label typography owns its visible spaces; the exact canonical label remains
    # recorded, and the term/ruby/colon and description are emitted intact.
    number=re.fullmatch(r'[（(]注([0-9０-９]*)[）)]',match[1])[1]
    label=r'\HistoricalDefinitionLabel{'+conv.text(number)+'}'
    # The colon is presentation furniture in this exact Old definition role.
    # Preserve the canonical glyph and all term/ruby and description content.
    term=value(match.start(2),match.end(2)-1)
    boundary=r'\par\newpage 'if node.has_attr('data-historical-page-boundary')else''
    if boundary:conv.features.append(dict(kind='historical_note_source_continuation',text=plain))
    if node.get('data-historical-definition-arrangement')=='continuation_at_term':
        # The first description follows its term on the same line. Subsequent
        # lines align at the term, retaining every ruby and literal character.
        description=value(match.start(3),match.end(3))
        tex=(r'\par{\fontsize{\NoteSize}{\NoteBaseline}\selectfont'
             r'\setlength\parindent{0pt}\hangindent=3.6em\hangafter=1'
             r'\noindent\makebox[3.6em][l]{'+label+'}'+term
             +r'\HistoricalDefinitionColon{}\hspace{.2em}'+description+r'\par}')
        conv.features.append(dict(kind='historical_definition_term_continuation',text=plain,canonical_changed=False))
        return boundary+with_numbered_note_inset(conv,tex)
    macro='HistoricalDefinition'
    if node.get('data-historical-definition-arrangement')=='description_next_line':
        macro='HistoricalLongDefinition'
        conv.features.append(dict(kind='historical_definition_next_line',text=plain,continuation_anchor='term_start'))
    tex='\\'+macro+'{'+label+'}{'+term+r'\HistoricalDefinitionColon{}}{'+value(match.start(3),match.end(3))+'}'
    return boundary+with_numbered_note_inset(conv,tex)


def with_numbered_note_inset(conv,tex):
    inset=getattr(conv,'historical_note_left_inset_em',0)
    if type(inset)not in [int,float]or not 0<=inset<=3:raise ValueError('Invalid numbered-context note inset')
    if not inset:return tex
    if not getattr(conv,'source_target_markers',False):raise ValueError('Numbered-context notes require Old source roles')
    conv.features.append(dict(kind='historical_numbered_context_note_inset',left_inset_em=inset,canonical_changed=False))
    return r'\par\begingroup\advance\leftskip by '+str(inset)+r'em\relax\advance\linewidth by -'+str(inset)+r'em\relax '+tex+r'\par\endgroup'
