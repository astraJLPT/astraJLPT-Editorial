"""Native components explicitly encoded in inspected historical HTML."""
import base64,hashlib,json,re
from bs4 import Tag,BeautifulSoup
from model import digest,Projection
from presentation import source_binding

def prepare(value,binding,unit):
    if digest(value)!=binding['content_sha256']or not isinstance(value,dict):raise ValueError('Stale historical component binding')
    source_binding(unit,binding['evidence'])
    soup=BeautifulSoup(value['html'],'html.parser');before=soup.get_text();kind=binding['kind']
    if 'figure_width_fraction'in binding and kind!='clock_pair':raise ValueError('Figure-pair width on another component')
    if 'bracketed_body_scope'in binding and(kind!='clock_pair'or binding['bracketed_body_scope']!='passage_only'):raise ValueError('Invalid bracketed clock-passage scope')
    if 'note_group_left_width_fraction'in binding and kind!='illustrated_note_group':raise ValueError('Note-group width on another component')
    note_keys={'note_arrangement','note_image_width_fraction','note_label_width_em'}
    if note_keys.intersection(binding)and kind!='illustrated_note_group'and(kind!='illustrated_notes'or binding.get('note_arrangement')!='after_label'or binding.get('compact_glossary')):
        raise ValueError('Conflicting after-label illustration controls')
    if kind=='clock_pair':
        tables=soup.find_all('table')
        if len(tables)!=1:raise ValueError('Clock pair requires one source table')
        tables[0]['data-historical-figure-pair']='true'
        width=binding.get('figure_width_fraction',.68)
        if type(width)not in [int,float]or not .3<=width<=1:raise ValueError('Invalid source-bound figure-pair width')
        tables[0]['data-historical-figure-width']=str(width)
        if 'pair_panel_width_fraction' in binding:
            p,g=binding['pair_panel_width_fraction'],binding['pair_gap_fraction']
            if not .3<=p<=.45 or not 0<=g<=.1 or 2*p+g>1:raise ValueError('Invalid clock-group geometry')
            tables[0]['data-historical-pair-panel-width']=str(p);tables[0]['data-historical-pair-gap']=str(g)
        if binding.get('bracketed_body_scope')=='passage_only':
            roots=[n for n in soup.children if isinstance(n,Tag)]
            body=roots[1:7];brackets=[n for n in body if n.has_attr('data-historical-bracket-label')]
            if (not roots or roots[0]is not tables[0]or len(body)!=6
                or [n.name for n in body]!=['div','div','div','p','div','p']
                or [n.get('data-historical-bracket-label')for n in brackets]!=list('ABCD')
                or any(n.attrs for n in [body[3],body[5]])or len(roots)<9
                or roots[7].name!='p'or not re.fullmatch(r'（.+による）',Projection({'html':str(roots[7])}).text.strip())
                or roots[8].name!='p'or not roots[8].get_text().startswith('（注1）')):
                raise ValueError('Clock passage requires its exact figure/body/citation/note relationship')
            group=soup.new_tag('div',attrs={'data-historical-letter-bracket-body':'true'});body[0].insert_before(group)
            for node in body:group.append(node.extract())
    elif kind=='table_chart':
        chart_width=binding.get('chart_width_fraction',1)
        if isinstance(chart_width,bool) or not isinstance(chart_width,(int,float)) or not .5<=chart_width<=1:
            raise ValueError('Invalid source-bound chart width')
        tables=soup.find_all('table');images=soup.find_all('img')
        if len(tables)!=1 or len(images)!=1:raise ValueError('Table/chart pair needs one table and one figure')
        table=tables[0];left_caption=table.find_previous_sibling();fig=images[0].find_parent('p');right_caption=fig.find_previous_sibling();citation=fig.find_next_sibling()
        if left_caption is None or not left_caption.get_text().startswith('表')or right_caption is None or not right_caption.get_text().startswith('図')or citation is None or not citation.get_text().startswith('（図'):
            raise ValueError('Table/chart captions or attribution changed')
        group=soup.new_tag('div',attrs={'data-historical-table-chart':'true','data-historical-chart-width':str(chart_width)});left=soup.new_tag('div');right=soup.new_tag('div')
        left_caption.insert_before(group);group.append(left);group.append(right)
        for n in [left_caption,table]:left.append(n.extract())
        for n in [right_caption,fig,citation]:right.append(n.extract())
        if binding.get('bold_caption_markers'):
            from bs4 import NavigableString
            for cap in [left_caption,right_caption]:
                first=next((n for n in cap.descendants if isinstance(n,NavigableString)),None)
                if first is None or str(first)[0] not in '表図':raise ValueError('Caption marker is not the exact first character')
                marker=soup.new_tag('span',attrs={'data-historical-caption-marker':'true'});marker.string=str(first)[0]
                first.replace_with(marker,NavigableString(str(first)[1:]))
        if binding.get('percentage_align')=='right':group['data-historical-percentage-align']='right'
    elif kind=='three_slot_ordering':
        frames=soup.select('div[data-historical-framed-document="single"]')
        flows=soup.select('div[data-historical-order-flow="vertical"]')
        alternatives=soup.select('div[data-historical-labeled-frame]')
        if (len(frames)!=2 or len(flows)!=1 or len(alternatives)!=3
            or [n['data-historical-labeled-frame']for n in alternatives]!=list('ABC')
            or frames[0].find_next_sibling()is not flows[0]
            or flows[0].find_next_sibling()is not frames[1]
            or frames[1].get_text(strip=True)!='これが物価である。'
            or order_flow_values(flows[0])!=[x for c in 'アイウ'for x in ['⬇','（　'+c+'　）']]+['⬇']):
            raise ValueError('Three-slot ordering requires the complete initial/slots/conclusion/ABC relationship')
        frames[0]['data-historical-frame-role']='passage'
        flows[0]['data-historical-compact-sequence']='true'
        for n in alternatives:n['data-historical-frame-role']='alternative'
    elif kind=='illustrated_note_group':
        images=soup.find_all('img');width=binding.get('note_image_width_fraction')
        left_width=binding.get('note_group_left_width_fraction')
        if len(images)!=1 or type(width)not in [int,float]or not (.2 if left_width is not None else .35)<=width<=.55:raise ValueError('Invalid beside-group illustration')
        if left_width is not None and(type(left_width)not in [int,float]or not .3<=left_width<=.6 or left_width+width>.98):raise ValueError('Invalid beside-group note width')
        figure=images[0].find_parent('p');notes=[];p=figure.find_previous_sibling()
        for number in [3,2,1]:
            if p is None or p.name!='p'or p.find('img')or not p.get_text().startswith('（注'+str(number)+'）'):raise ValueError('Beside-group illustration requires its three consecutive notes')
            notes.insert(0,p);p=p.find_previous_sibling()
        group=soup.new_tag('div',attrs={'data-historical-note-group':'true','data-historical-note-image-width':str(width)})
        if left_width is not None:group['data-historical-note-left-width']=str(left_width)
        notes[0].insert_before(group)
        for p in [*notes,figure]:group.append(p.extract())
    elif kind=='illustrated_notes':
        ps=[p for p in soup.find_all('p')if p.find('img')and p.get_text().startswith('（注')]
        if not 1<=len(ps)<=2:raise ValueError('Illustrated notes require one or two labeled source note paragraphs')
        if len(ps)==2 and ps[0].find_next_sibling()!=ps[1]:raise ValueError('Paired illustrations must be adjacent notes')
        if binding.get('compact_glossary'):
            if len(ps)!=1:raise ValueError('Compact glossary needs one illustrated middle definition')
            previous,following=ps[0].find_previous_sibling(),ps[0].find_next_sibling()
            if any(n is None or n.name!='p' or n.find('img') or not n.get_text().startswith('（注') for n in [previous,following]):
                raise ValueError('Compact illustrated glossary needs exact adjacent note definitions')
            group=soup.new_tag('div',attrs={'data-historical-glossary-triplet':'true'});previous.insert_before(group)
            for p in [previous,ps[0],following]:group.append(p.extract())
        elif binding.get('note_arrangement')=='after_label':
            if len(ps)!=1 or ps[0].get_text(strip=True)!='（注）':
                raise ValueError('After-label illustration needs one exact label-only note')
            width=binding.get('note_image_width_fraction');label_width=binding.get('note_label_width_em')
            if type(width)not in [int,float]or not .2<=width<=.6 or type(label_width)not in [int,float]or not 1.5<=label_width<=4:
                raise ValueError('Invalid source-bound note illustration dimensions')
            group=soup.new_tag('div',attrs={'data-historical-after-label-illustration':'true','data-historical-note-image-width':str(width),'data-historical-note-label-width':str(label_width)})
            ps[0].insert_before(group);group.append(ps[0].extract())
        else:
            if binding.get('note_arrangement')is not None:raise ValueError('Unknown note illustration arrangement')
            group=soup.new_tag('div',attrs={'data-historical-illustrated-notes':'true'});ps[0].insert_before(group)
            if 'paired_image_fraction' in binding:
                if not .2<=binding['paired_image_fraction']<=.42:raise ValueError('Invalid paired note image size')
                group['data-historical-note-image-fraction']=str(binding['paired_image_fraction'])
            for p in ps:group.append(p.extract())
    else:raise ValueError('Unknown historical component binding')
    if before!=soup.get_text():raise ValueError('Historical component preparation changed native text')
    return {'html':str(soup)}

def image_at_width(conv,node,width,block=True):
    key=hashlib.sha256(base64.b64decode(node['src'].split(',',1)[1])).hexdigest()
    original=conv.embedded_image_styles[key]
    if original['role']!='illustration':raise ValueError('Native panel requires an illustration')
    conv.embedded_image_styles[key]={**original,'width_fraction':width}
    try:
        tex=conv.node(node,'body')
        if not block:
            # The enclosing source component owns paragraph glue and alignment.
            prefix=r'\par\addvspace{8pt}\noindent';suffix=r'\par\addvspace{8pt}'
            if not tex.startswith(prefix)or not tex.endswith(suffix):raise ValueError('Illustration emitter contract changed')
            tex=tex[len(prefix):-len(suffix)]
        return tex
    finally:conv.embedded_image_styles[key]=original

def render(conv,node,context):
    if any(node is consumed for consumed in getattr(conv,'consumed_historical_nodes',[])):return ''
    attrs={k:v for k,v in node.attrs.items()if k.startswith('data-historical-')}
    if attrs and not getattr(conv,'source_target_markers',False):
        raise ValueError('Historical component outside historical edition')
    if not getattr(conv,'source_target_markers',False):return None
    # Two labels attached to the same first character belong side by side.
    # Leave later notes, vertical passages and other reference forms unchanged.
    leading=next((c for c in node.children if str(c).strip()),None)
    if (node.name=='u' and re.fullmatch(r'[①-⑳]',node.get('data-reference-label',''))
        and not getattr(conv,'active_vertical_body',False) and isinstance(leading,Tag)
        and leading.name=='span' and set(leading.attrs)=={'data-note-label'}
        and re.fullmatch(r'（注[1-9][0-9]*）',leading['data-note-label'])):
        label=node['data-reference-label'];note=leading['data-note-label'];plain=Projection({'html':str(node)}).text
        head=''.join(conv.node(x,context)for x in leading.children)
        tail=''.join(conv.node(c,context)for c in node.children if c is not leading)
        body=head+tail
        conv.features.append(dict(kind='underline_reference',label=label,text=plain))
        conv.features.append(dict(kind='layout_symbol',text=note,basis='Source-supported note label explicitly encoded in the canonical data-note-label attribute'))
        conv.features.append(dict(kind='historical_shared_reference_note_anchor',reference=label,note=note,text=plain,canonical_changed=False))
        # Preserve the ordinary note's 6.5pt role and reserve its depth so
        # ruby on the following line cannot occupy the same vertical space.
        clearance=node.get('data-reference-clearance','1.5')
        note_tex=r'{\fontsize{6.5}{7}\selectfont '+conv.text(note)+'}'
        target=r'\UnderlinedReference['+clearance+']{'+conv.text(label)+note_tex+'}{'+body+'}'
        from richtex import bounded_word
        if len(plain)<=6 and bounded_word(plain)and not node.find(['br','p','div','table','img']):
            conv.features.append(dict(kind='historical_bounded_reference',label=label,text=plain,limit=6))
            return r'\mbox{'+target+'}'
        # The lexical term was already atomic in AnnotatedTerm. Bind both
        # labels to that same term and allow the remaining underline to wrap.
        conv.features.append(dict(kind='historical_bound_reference_start',label=label,text=plain,first_cluster=Projection({'html':leading.decode_contents()}).text,shared_note=True,canonical_changed=False))
        return r'\mbox{\UnderlinedReference['+clearance+']{'+conv.text(label)+note_tex+'}{'+head+'}}'+(r'\underLine{'+tail+'}'if tail else'')
    if (node.name=='u' and re.fullmatch(r'[①-⑳]',node.get('data-reference-label',''))
        and context=='body' and not getattr(conv,'active_vertical_body',False)
        and not node.find(['br','p','div','table','img'])):
        plain=Projection({'html':str(node)}).text
        if len(plain)>6 and plain and not plain[0].isspace():
            from example_layout import slice_inline
            raw=node.decode_contents();projection=Projection({'html':raw})
            cut=next((r['end'] for r in projection.ruby if r['start']==0),1)
            head=conv.value({'html':slice_inline(raw,0,cut)},context)
            tail=conv.value({'html':slice_inline(raw,cut,len(plain))},context)
            label=node['data-reference-label'];clearance=node.get('data-reference-clearance')
            conv.features.append(dict(kind='underline_reference',label=label,text=plain,**({'clearance_below_pt':float(clearance)}if clearance is not None else{})))
            conv.features.append(dict(kind='historical_bound_reference_start',label=label,text=plain,first_cluster=plain[:cut],shared_note=False,canonical_changed=False))
            target=r'\UnderlinedReference'+('['+clearance+']'if clearance is not None else'')+'{'+conv.text(label)+'}{'+head+'}'
            return r'\mbox{'+target+'}'+r'\underLine{'+tail+'}'
    from historical_spatial import render as render_spatial
    spatial=render_spatial(conv,node,context)
    if spatial is not None:return spatial
    if 'data-historical-caption-marker' in attrs:
        if node.get_text() not in ['表','図'] or node.find():raise ValueError('Invalid separate caption marker')
        conv.features.append(dict(kind='historical_gothic_caption_marker',text=node.get_text()))
        return r'{\HistoricalQuestionJapanese '+conv.text(node.get_text())+'}'
    def children():return ''.join(conv.node(c,context)for c in node.children)
    if 'data-historical-letter-bracket-body'in attrs:
        metrics=getattr(conv,'historical_letter_brackets',None)
        if node.name!='div'or attrs!={'data-historical-letter-bracket-body':'true'}or context!='body'or not metrics:
            raise ValueError('Bracketed passage body lacks its family metrics')
        labels=[n['data-historical-bracket-label']for n in node.select('[data-historical-bracket-label]')]
        if labels!=list('ABCD')or node.find('table')or node.select('[data-historical-text-role]'):
            raise ValueError('Bracketed passage scope contains figures or terminal roles')
        inset=metrics['body_inset_em']
        conv.features.append(dict(kind='historical_letter_bracket_body_scope',left_inset_em=inset,figures_and_notes_outside=True,canonical_changed=False))
        return (r'\par\begingroup\advance\leftskip by '+str(inset)+r'em\relax\advance\linewidth by -'+str(inset)+r'em\relax '
                +children()+r'\par\endgroup')
    if 'data-historical-display-keep-end' in attrs:
        if attrs!={'data-historical-display-keep-end':'true'} or node.get_text() or node.find():
            raise ValueError('Invalid display keep marker')
        from historical_complex import DISPLAY_KEEP_END
        return DISPLAY_KEEP_END
    if 'data-historical-answer-slot' in attrs:
        from historical_inline_atoms import render as render_atom
        return render_atom(conv,node)
    if 'data-historical-text-role' in attrs:
        from historical_prose import render as render_prose
        return render_prose(conv,node,context)
    if 'data-historical-note-group'in attrs:
        ps=node.find_all('p',recursive=False);width=float(attrs['data-historical-note-image-width'])
        if len(ps)!=4 or len(ps[-1].find_all('img'))!=1 or any(p.find('img')for p in ps[:3]):raise ValueError('Altered illustrated note group')
        left=''.join(conv.node(p,context)for p in ps[:3]);right=image_at_width(conv,ps[-1].img,1,block=False)
        left_width=float(attrs.get('data-historical-note-left-width',.98-width))
        gap=r'\hspace{.02\linewidth}'if 'data-historical-note-left-width'in attrs else r'\hfill'
        conv.features.append(dict(kind='historical_illustrated_note_group',notes=3,image_width_fraction=width,left_width_fraction=left_width,source_order_preserved=True))
        return (r'\par\noindent\begin{minipage}{\linewidth}\noindent\begin{minipage}[t]{'+str(left_width)+r'\linewidth}\vspace{0pt}\parindent=0pt '+left
            +r'\end{minipage}'+gap+r'\begin{minipage}[t]{'+str(width)+r'\linewidth}\vspace{0pt}'+right+r'\end{minipage}\end{minipage}\par\addvspace{7pt}')
    if 'data-historical-glossary-triplet' in attrs:
        ps=node.find_all('p',recursive=False)
        if len(ps)!=3 or len(ps[1].find_all('img'))!=1:raise ValueError('Invalid illustrated glossary triplet')
        prefix=''.join(conv.node(c,'body')for c in ps[1].children if getattr(c,'name',None)!='img')
        graphic=image_at_width(conv,ps[1].img,1)
        conv.features.append({'kind':'historical_compact_illustrated_glossary','notes':3,'image_bytes_preserved':True,'native_definition_order_preserved':True})
        return r'\HistoricalGlossaryTriplet{'+conv.node(ps[0],context)+'}{'+prefix+'}{'+graphic+'}{'+conv.node(ps[2],context)+'}'
    if 'data-historical-figure-pair'in attrs:
        rows=node.find_all('tr');cells=[r.find_all(['th','td'],recursive=False)for r in rows]
        if len(cells)!=2 or any(len(r)!=2 for r in cells)or any(len(c.find_all('img'))!=1 for c in cells[1]):raise ValueError('Invalid two-figure panel')
        panels=[];width=float(attrs['data-historical-figure-width'])
        panel_width=attrs.get('data-historical-pair-panel-width','.47')
        if not .3<=width<=1:raise ValueError('Invalid native figure-pair width')
        for header,cell in zip(cells[0],cells[1]):
            head=''.join(conv.node(c,'body')for c in header.children)
            panels.append(r'\begin{minipage}[t]{'+panel_width+r'\linewidth}\centering '+head+r'\par '+image_at_width(conv,cell.img,width)+r'\end{minipage}')
        conv.features.append({'kind':'historical_native_figure_pair','panels':2,'outer_grid':False,'figure_width_fraction':width,'caption_alignment':'first_baseline'})
        if 'data-historical-pair-gap' in attrs:
            gap=attrs['data-historical-pair-gap']
            return r'\par\noindent\makebox[\linewidth][c]{'+(r'\hspace{'+gap+r'\linewidth}').join(panels)+r'}\par\addvspace{8pt}'
        return r'\par\noindent '+r'\hfill '.join(panels)+r'\par\addvspace{8pt}'
    if 'data-historical-after-label-illustration'in attrs:
        ps=node.find_all('p',recursive=False)
        if len(ps)!=1 or len(ps[0].find_all('img'))!=1 or ps[0].get_text(strip=True)!='（注）':raise ValueError('Invalid after-label illustration')
        width=float(attrs['data-historical-note-image-width']);label_width=float(attrs['data-historical-note-label-width'])
        if not .2<=width<=.6 or not 1.5<=label_width<=4:raise ValueError('Invalid native note dimensions')
        img=ps[0].img;label=''.join(conv.node(c,'body')for c in ps[0].children if c is not img)
        graphic=image_at_width(conv,img,width,block=False)
        inset=getattr(conv,'historical_note_left_inset_em',0)
        if type(inset)not in [int,float]or not 0<=inset<=3:raise ValueError('Invalid after-label note inset')
        offset=r'\hspace{'+str(inset)+r'em}'if inset else''
        conv.features.append({'kind':'historical_after_label_illustration','image_width_fraction':width,'label_width_em':label_width,'left_inset_em':inset,'image_bytes_preserved':True})
        return (r'\par\noindent\begin{minipage}{\linewidth}\noindent'+offset+r'\makebox['+str(label_width)+r'em][l]{'+label+r'}\raisebox{\dimexpr\ht\strutbox-\height\relax}{'+graphic+r'}\par\end{minipage}\par\addvspace{7pt}')
    if 'data-historical-table-chart'in attrs:
        cols=node.find_all('div',recursive=False)
        if len(cols)!=2 or not cols[0].find('table')or len(cols[1].find_all('img'))!=1:raise ValueError('Invalid table/chart columns')
        previous_tables=conv.table_styles
        if attrs.get('data-historical-percentage-align')=='right':
            index=str(conv.table_index)
            conv.table_styles={**previous_tables,index:{**previous_tables.get(index,{}),'column_alignments':['left','right']}}
        try:left=''.join(conv.node(c,'body')for c in cols[0].children)
        finally:conv.table_styles=previous_tables
        img=cols[1].img;key=hashlib.sha256(base64.b64decode(img['src'].split(',',1)[1])).hexdigest();old=conv.embedded_image_styles[key]
        chart_width=float(attrs.get('data-historical-chart-width',1))
        if not .5<=chart_width<=1:raise ValueError('Invalid native chart width')
        conv.embedded_image_styles[key]={**old,'width_fraction':chart_width}
        try:right=''.join(conv.node(c,'body')for c in cols[1].children)
        finally:conv.embedded_image_styles[key]=old
        conv.features.append({'kind':'historical_native_table_chart','left_fraction':.38,'right_fraction':.58,'chart_width_fraction':chart_width,'table_native':True})
        return r'\par\noindent\begin{minipage}[t]{.38\linewidth}\vspace{0pt}\setlength\parindent{0pt}'+left+r'\end{minipage}\hfill\begin{minipage}[t]{.58\linewidth}\vspace{0pt}\setlength\parindent{0pt}'+right+r'\end{minipage}\par\addvspace{8pt}'
    if 'data-historical-illustrated-notes'in attrs:
        ps=node.find_all('p',recursive=False);panels=[]
        for p in ps:
            if len(p.find_all('img'))!=1:raise ValueError('Illustrated note must contain exactly one image')
            img=p.img;prefix=''.join(conv.node(c,'body')for c in p.children if c is not img)
            if 'data-historical-note-image-fraction' in attrs:
                graphic=image_at_width(conv,img,float(attrs['data-historical-note-image-fraction']),block=False)
                panels.append(r'\begin{minipage}[t]{.48\linewidth}\vspace{0pt}\fontsize{\NoteSize}{\NoteBaseline}\selectfont\noindent\rule{0pt}{1.6em}\makebox[6.4em][l]{'+prefix+r'}\raisebox{\dimexpr .7em-\height\relax}{'+graphic+r'}\par\end{minipage}')
            else:
                graphic=image_at_width(conv,img,1)
                panels.append(r'\begin{minipage}[t]{'+('.48'if len(ps)==2 else'1')+r'\linewidth}\vspace{0pt}\noindent\begin{minipage}[t]{.53\linewidth}'+prefix+r'\end{minipage}\hfill\begin{minipage}[t]{'+('.42'if len(ps)==2 else'.34')+r'\linewidth}\vspace{0pt}'+graphic+r'\end{minipage}\end{minipage}')
        conv.features.append({'kind':'historical_native_illustrated_notes','count':len(ps)})
        from historical_prose import with_numbered_note_inset
        return with_numbered_note_inset(conv,r'\par\noindent '+r'\hfill '.join(panels)+r'\par\addvspace{7pt}')
    if node.name=='p'and node.get_text(strip=True)in 'ABCD'and len(node.get_text(strip=True))==1:
        nxt=node.find_next_sibling()
        if nxt is not None and nxt.get('data-historical-framed-document')=='single':
            # Canonical adjacent label/frame nodes are one source component.
            # Hold object references so a later soup cannot reuse their ids.
            if not hasattr(conv,'consumed_historical_nodes'):conv.consumed_historical_nodes=[]
            conv.consumed_historical_nodes.append(nxt)
            label=node.get_text(strip=True)
            body=''.join(conv.node(c,context)for c in nxt.children)
            conv.features.append({'kind':'historical_native_labeled_frame','label':label,'rule':'solid','label_outside':True})
            tex=r'\HistoricalLabeledFrame{'+conv.text(label)+r'}{solid}{'+body+'}'
            if nxt.get('data-historical-frame-role')=='alternative':
                conv.features.append({'kind':'historical_frame_variant','variant':'alternative','first_line_indent_em':0})
                tex=r'{\HistoricalAlternativeFrameStyle '+tex+'}'
            return tex
    if 'data-historical-framed-document'in attrs:
        if attrs['data-historical-framed-document']!='single':raise ValueError('Unknown historical frame')
        if 'data-historical-insertion-height'in attrs:
            height=float(attrs['data-historical-insertion-height'])
            if node.get_text(strip=True)!='ウ' or not 2.8<=height<=4.5:raise ValueError('Invalid standalone insertion rectangle')
            conv.features.append(dict(kind='historical_standalone_insertion',label='ウ',height_em=height))
            tex=r'\par\addvspace{7pt}{\setlength\fboxsep{0pt}\setlength\fboxrule{.5pt}\noindent\fbox{\parbox[c]['+str(height)+r'em][c]{\dimexpr\linewidth-2\fboxrule\relax}{\centering '+conv.text('ウ')+r'}}\par}\addvspace{7pt}'
            if 'data-historical-slot-inset'in attrs:
                inset=float(attrs['data-historical-slot-inset'])
                if not 0<=inset<=3:raise ValueError('Invalid standalone slot inset')
                tex=tex.replace(r'\noindent\fbox{',r'\noindent\hspace*{'+str(inset)+r'em}\fbox{',1).replace(r'\linewidth-2\fboxrule',r'\linewidth-'+str(inset)+r'em-2\fboxrule',1)
                conv.features.append(dict(kind='historical_standalone_slot_geometry',label='ウ',inset_em=inset,canonical_changed=False))
            return tex
        conv.features.append({'kind':'historical_native_frame','rule':'solid','outside_labels_and_trailer':True})
        if attrs.get('data-historical-frame-role')=='passage':
            following=node.find_next_sibling()
            if following is not None and 'data-historical-order-gap'in following.attrs and 'data-historical-frame-width'in attrs:
                expected=order_flow_values(following)
                if not hasattr(conv,'consumed_historical_nodes'):conv.consumed_historical_nodes=[]
                conv.consumed_historical_nodes.append(following)
                return render_source_connected_frame(conv,node,following,children(),expected)
            if following is not None and following.get('data-historical-compact-sequence')=='true':
                expected=order_flow_values(following)
                if not hasattr(conv,'consumed_historical_nodes'):conv.consumed_historical_nodes=[]
                conv.consumed_historical_nodes.append(following)
                conv.features.append({'kind':'historical_frame_variant','variant':'passage','first_line_indent_em':1})
                conv.features.append({'kind':'historical_native_order_flow','slots':[x[2]for x in expected if x!='⬇'],'arrows':expected.count('⬇'),
                    'orientation':'vertical','first_arrow':'native_vector_attached_to_frame_south',
                    'attachment_gap_pt':0,'attachment_independent_of_following_clearance':True})
                # The first arrow is drawn in the frame's coordinate system. The
                # remaining canonical slots/arrows follow once in original order.
                rest=''.join(conv.text(t)+r'\par\nobreak 'for t in expected[1:])
                return r'{\HistoricalPassageFrameStyle \HistoricalConnectedFrame{solid}{'+children()+'}{'+rest+'}}'
        tex=r'\HistoricalFramed{solid}{'+children()+'}'
        if attrs.get('data-historical-frame-role')=='passage':
            conv.features.append({'kind':'historical_frame_variant','variant':'passage','first_line_indent_em':1})
            indent=(r'\renewcommand\HistoricalFrameIndent{'+attrs['data-historical-frame-first-line-indent-em']+'em}')if 'data-historical-frame-first-line-indent-em'in attrs else ''
            tex=r'{\HistoricalPassageFrameStyle '+indent+tex+'}'
        if 'data-historical-frame-width'in attrs:
            width=float(attrs['data-historical-frame-width']);inset=float(attrs['data-historical-frame-inset'])
            if not .35<=width<=.9 or not 0<=inset<=5:raise ValueError('Invalid compact frame geometry')
            conv.features.append(dict(kind='historical_source_frame_geometry',width_fraction=width,inset_em=inset,canonical_changed=False))
            # Retain the frame's ordinary vertical paragraph flow. A nested
            # minipage swallowed its trailing clearance before following prose.
            spacing=''
            for key,macro in [('padding-y-pt','HistoricalFrameYPadding'),('before-pt','HistoricalFrameBefore'),('first-line-indent-em','HistoricalFrameIndent')]:
                if 'data-historical-frame-'+key in attrs:
                    value=float(attrs['data-historical-frame-'+key])
                    if not 0<=value<=30:raise ValueError('Invalid native source frame spacing')
                    spacing+='\\renewcommand\\'+macro+'{'+str(value)+('em'if key=='first-line-indent-em'else'pt')+'}'
                    conv.features[-1][key.replace('-','_')]=value
            tex=(r'\par\begingroup'+spacing+r'\advance\leftskip by '+str(inset)+r'em\relax\setlength\linewidth{'+str(width)+r'\linewidth}'
                 +tex+r'\par\endgroup')
        return tex
    if 'data-historical-labeled-frame'in attrs:
        label=attrs['data-historical-labeled-frame'];style=attrs.get('data-historical-border-style')
        if label not in list('ABCD')or style not in ['solid','dashed']:raise ValueError('Invalid historical labeled frame')
        if 'data-historical-order-frame'in attrs:
            return render_source_order_frame(conv,node,label,style,children())
        conv.features.append({'kind':'historical_native_labeled_frame','label':label,'rule':style,'label_outside':True})
        tex=r'\HistoricalLabeledFrame{'+conv.text(label)+'}{'+style+'}{'+children()+'}'
        if attrs.get('data-historical-frame-role')=='alternative':
            conv.features.append({'kind':'historical_frame_variant','variant':'alternative','first_line_indent_em':0})
            tex=r'{\HistoricalAlternativeFrameStyle '+tex+'}'
        if 'data-historical-fragment-width' in attrs:
            tex=r'{\renewcommand\HistoricalFragmentWidth{'+attrs['data-historical-fragment-width']+'}'+tex+'}'
        return tex
    if 'data-historical-bracket-label'in attrs:
        label=attrs['data-historical-bracket-label']
        if label in ['〔1〕','〔2〕']:
            parts=[n for n in node.children if isinstance(n,Tag)]
            if (node.name!='div' or len(parts)!=1 or parts[0].name!='p'
                or node.find(['img','table','div']) or not parts[0].get_text(strip=True)
                or set(attrs)!={'data-historical-bracket-label'}):
                raise ValueError('Numbered source bracket requires one complete prose paragraph')
            conv.features.append({'kind':'historical_native_numbered_bracket','label':label,'label_in_spine_gap':True})
            return r'\HistoricalNumberedBracket{'+conv.text(label)+'}{'+children()+'}'
        if label not in list('ABCD'):raise ValueError('Unknown historical bracket label')
        if getattr(conv,'historical_letter_brackets',None):
            return render_aligned_letter_bracket(conv,label,children())
        conv.features.append({'kind':'historical_native_bracket','label':label,'label_outside':True})
        return r'\HistoricalBracket{'+conv.text(label)+'}{'+children()+'}'
    if 'data-historical-order-flow'in attrs:
        expected=order_flow_values(node)
        conv.features.append({'kind':'historical_native_order_flow','slots':[x[2]for x in expected if x!='⬇'],'arrows':expected.count('⬇'),'orientation':'vertical'})
        if attrs.get('data-historical-compact-sequence')=='true':
            return r'\HistoricalOrderSequence{'+''.join(conv.text(t)+r'\par\nobreak 'for t in expected)+'}'
        gap=attrs.get('data-historical-order-gap')
        if gap is None:
            return r'\par{\centering\setlength\parindent{0pt}'+''.join(conv.text(t)+r'\par\nobreak\vspace{2pt}'for t in expected)+r'\par}\vspace{6pt}'
        gap=float(gap)
        if not 0<=gap<=18 or expected!=['⬇','（\u3000ア\u3000）','⬇','（\u3000イ\u3000）','⬇','（\u3000ウ\u3000）','⬇']:raise ValueError('Invalid source order rhythm')
        conv.features.append(dict(kind='historical_source_order_rhythm',gap_pt=gap,slots=['ア','イ','ウ'],arrows=4,canonical_changed=False))
        return r'\par{\centering\setlength\parindent{0pt}'+''.join(conv.text(t)+r'\par\nobreak\vspace{'+str(gap)+r'pt}'for t in expected)+r'\par}\vspace{6pt}'
    if 'data-historical-continuation-slot'in attrs:
        label=attrs['data-historical-continuation-slot'];parts=[n for n in node.children if isinstance(n,Tag)]
        if label not in list('アイウエ')or len(parts)!=2 or parts[0].name!='p'or parts[1].get('data-historical-framed-blank')!=label or parts[1].get_text()!=label:
            raise ValueError('Invalid stepped continuation slot')
        prose=''.join(conv.node(c,context)for c in parts[0].children)
        conv.features.append({'kind':'historical_native_continuation_slot','label':label,'step':'after_actual_last_prose_line'})
        tex=r'\HistoricalContinuationSlot{'+prose+'}{'+conv.text(label)+'}'
        if 'data-historical-slot-bottom' in attrs:
            tex=r'{\renewcommand\HistoricalSlotBottom{'+attrs['data-historical-slot-bottom']+'em}'+tex+'}'
        if 'data-historical-slot-geometry'in attrs:
            geometry=json.loads(attrs['data-historical-slot-geometry']);inset=geometry['inset_em'];indent=geometry['first_line_indent_em']
            if set(geometry)-{'inset_em','first_line_indent_em','before_pt'}or not {'inset_em','first_line_indent_em'}<=set(geometry)or type(inset)not in [int,float]or not 0<=inset<=3 or type(indent)not in [int,float]or not 0<=indent<=2:
                raise ValueError('Invalid native continuation-slot geometry')
            if type(geometry.get('before_pt',0))not in [int,float]or not 0<=geometry.get('before_pt',0)<=30:raise ValueError('Invalid slot introduction clearance')
            tex=tex.replace(r'\HistoricalContinuationSlot{',r'\HistoricalContinuationSlot{\setlength\parindent{'+str(indent)+r'em}',1)
            tex=r'\par\begingroup\advance\leftskip by '+str(inset)+r'em\relax\advance\linewidth by -'+str(inset)+r'em\relax '+tex+r'\par\endgroup'
            if geometry.get('before_pt'):tex=r'\par\addvspace{'+str(geometry['before_pt'])+r'pt}'+tex
            conv.features.append(dict(kind='historical_continuation_slot_geometry',label=label,**geometry,canonical_changed=False))
        return tex
    if 'data-historical-framed-blank'in attrs:
        raise ValueError('Continuation blank must be consumed by its prose-slot component')
    if attrs and set(attrs)-{'data-historical-option-table','data-historical-fixed-column'}:
        raise ValueError('Unconsumed historical component attributes: '+str(attrs))
    return None


def order_flow_values(node):
    ps=node.find_all('p',recursive=False)
    if node.get('data-historical-order-flow')!='vertical'or len(ps)not in(7,8):raise ValueError('Invalid historical ordering flow')
    expected=([text for letter in 'アイウ'for text in ['⬇','（　'+letter+'　）']]+['⬇']if len(ps)==7 else
              [text for letter in 'アイウエ'for text in ['⬇','（　'+letter+'　）']])
    if [p.get_text()for p in ps]!=expected:raise ValueError('Historical ordering sequence differs from its canonical arrows/slots')
    return expected


def letter_bracket_parameters(value,style):
    params=style.get('historical_typography',{}).get('letter_brackets')
    if params is None:return None
    limits={'body_inset_em':(2,4),'spine_inset_em':(.5,2.5),'cap_inset_em':(0,1),'label_inset_em':(1,3.5),'before_pt':(0,20),'after_pt':(0,20)}
    if not isinstance(params,dict)or set(params)!=set(limits)or any(type(params[k])not in [int,float]or not lo<=params[k]<=hi for k,(lo,hi)in limits.items()):raise ValueError('Invalid letter bracket metrics')
    if not params['cap_inset_em']<params['spine_inset_em']<params['label_inset_em']<params['body_inset_em']:raise ValueError('Letter bracket margin order is invalid')
    if not isinstance(value,dict):return None
    nodes=BeautifulSoup(value['html'],'html.parser').select('[data-historical-bracket-label]')
    labels=[n['data-historical-bracket-label']for n in nodes]
    if not labels:return None
    if labels!=list('ABCD'):raise ValueError('Letter bracket family needs one ordered A-D passage')
    return params


def render_aligned_letter_bracket(conv,label,body):
    p=conv.historical_letter_brackets
    cap=str(p['cap_inset_em']);spine=str(p['spine_inset_em']);offset=str(p['label_inset_em'])
    conv.features.append(dict(kind='historical_native_bracket',label=label,label_outside=True,body_aligned=True,**p))
    return (r'\par\addvspace{'+str(p['before_pt'])+r'pt}\noindent'
        +r'\sbox\HistoricalComponentBox{\begin{minipage}{\linewidth}\setlength\parindent{1em}'+body+r'\par\end{minipage}}'
        +r'\begin{tikzpicture}[baseline=(body.base)]'
        +r'\node[inner sep=0pt,outer sep=0pt,anchor=north west](body)at(0,0){\usebox\HistoricalComponentBox};'
        +r'\draw[line width=.5pt]([xshift=-'+cap+r'em]body.north west)--([xshift=-'+spine+r'em]body.north west)--([xshift=-'+spine+r'em]body.south west)--([xshift=-'+cap+r'em]body.south west);'
        +r'\node[anchor=east,inner sep=0pt]at([xshift=-'+offset+r'em]body.west){'+conv.text(label)+r'};'
        +r'\pgfresetboundingbox\path[use as bounding box](body.north west)rectangle(body.south east);'
        +r'\end{tikzpicture}\par\addvspace{'+str(p['after_pt'])+r'pt}')


def render_source_order_frame(conv,node,label,rule,body):
    p=json.loads(node['data-historical-order-frame'])
    before=p['first_before_pt']if p['first']else p['next_before_pt']
    after=(r'\par\addvspace{'+str(p['last_after_pt'])+r'pt}')if p.get('last')and p.get('last_after_pt')else''
    width=p['fragment_width_fraction'];reserve=p['label_width_em'];x=p['padding_x_pt'];y=p['padding_y_pt']
    conv.features.append(dict(kind='historical_source_order_frame',label=label,rule=rule,**p,canonical_changed=False))
    # Its complete source-bound box includes the label reserve and measured padding.
    content_width=r'\dimexpr '+str(width)+r'\linewidth-'+str(reserve)+r'em-'+str(2*x+.5)+r'pt\relax'
    return (r'\par\addvspace{'+str(before)+r'pt}\begingroup\advance\leftskip by '+str(p['inset_em'])+r'em\relax\noindent'
        +r'\begin{minipage}[t]{'+str(reserve)+r'em}\vspace{'+str(y)+r'pt}'+conv.text(label)+r'\end{minipage}'
        +r'\begin{tikzpicture}[baseline=(frame.north)]\node[draw,line width=.5pt,'+rule+r',inner xsep='+str(x)+r'pt,inner ysep='+str(y)+r'pt,outer sep=0pt](frame){'
        +r'\begin{minipage}{'+content_width+r'}\setlength\parindent{0pt}'+body+r'\par\end{minipage}};\end{tikzpicture}\par\endgroup'+after)


def render_source_connected_frame(conv,node,flow,body,expected):
    width=float(node['data-historical-frame-width']);inset=float(node['data-historical-frame-inset'])
    gap=float(flow['data-historical-order-gap']);indent=float(node['data-historical-frame-first-line-indent-em'])
    if not .35<=width<=.9 or not 0<=inset<=5 or not 0<=gap<=18 or not 0<=indent<=2:raise ValueError('Invalid bound connected-frame geometry')
    if expected!=['⬇','（\u3000ア\u3000）','⬇','（\u3000イ\u3000）','⬇','（\u3000ウ\u3000）','⬇']:raise ValueError('Unexpected source-connected ordering sequence')
    conv.features.append(dict(kind='historical_source_connected_order',width_fraction=width,inset_em=inset,first_line_indent_em=indent,gap_pt=gap,slots=['ア','イ','ウ'],arrows=4,first_arrow_attached=True,flow_at_text_center=True,canonical_changed=False))
    offset=r'\dimexpr '+str((1-width)/2)+r'\linewidth-'+str(inset)+r'em\relax'
    rest=''.join(conv.text(t)+r'\par\nobreak\vspace{'+str(gap)+r'pt}'for t in expected[1:])
    return (r'\par\addvspace{7pt}\begingroup\advance\leftskip by '+str(inset)+r'em\relax\noindent'
        +r'\begin{tikzpicture}\node[draw,line width=.9pt,solid,inner xsep=8pt,inner ysep=6pt,outer sep=0pt](frame){'
        +r'\begin{minipage}{\dimexpr '+str(width)+r'\linewidth-17pt\relax}\setlength\parindent{'+str(indent)+r'em}'+body+r'\par\end{minipage}};'
        +r'\begin{scope}[shift={([xshift='+offset+r']frame.south)}]'
        +r'\fill(-2pt,0)--(2pt,0)--(2pt,-5.8pt)--(4pt,-5.8pt)--(0,-10pt)--(-4pt,-5.8pt)--(-2pt,-5.8pt)--cycle;\end{scope}'
        +r'\end{tikzpicture}\par\endgroup\nobreak\nointerlineskip\vspace{3pt}'
        +r'{\centering\setlength\parindent{0pt}'+rest+r'\par}\vspace{6pt}')
