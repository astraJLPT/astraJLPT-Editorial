"""Exact Old printed-document frame roles, independent of handwritten memos."""
import json,re,unicodedata
from bs4 import BeautifulSoup
from model import Projection,digest
from presentation import source_binding


def metric(value,lo,hi,label):
    if type(value)not in [int,float] or not lo<=value<=hi:raise ValueError('Invalid historical '+label)
    return value


def prepare(value,binding,unit,source_value):
    if digest(source_value)!=binding['content_sha256']:raise ValueError('Stale historical framed paragraphs')
    source_binding(unit,binding['evidence'])
    before=Projection(value);soup=BeautifulSoup(value['html'],'html.parser')
    frames=[d for d in soup.find_all('div')if 'border'in d.get('style','')]
    if len(frames)!=1:raise ValueError('Historical paragraphs require one complete frame')
    paragraphs=frames[0].find_all('p',recursive=False);seen=set()
    for spec in binding['paragraphs']:
        index=spec['index'];role=spec['role']
        if type(index)is not int or not 0<=index<len(paragraphs) or index in seen or role not in ['title','list','note']:raise ValueError('Invalid historical framed paragraph role')
        seen.add(index);p=paragraphs[index]
        if role=='title' and not re.search(r'text-align\s*:\s*center',p.get('style','')):raise ValueError('Bound title is not a centered source paragraph')
        if role=='list':
            marker=spec.get('marker');metric(spec.get('hanging_em'),.5,3,'list hanging inset')
            if not isinstance(marker,str) or len(marker)!=1 or not p.get_text().startswith(marker+' '):raise ValueError('Stale historical list marker')
        elif 'marker'in spec or 'hanging_em'in spec:raise ValueError('List fields on a non-list paragraph')
        for key in ['before_pt','after_pt']:
            if key in spec:metric(spec[key],0,72,'framed paragraph gap')
        p['data-historical-frame-paragraph']=json.dumps(spec,ensure_ascii=False,sort_keys=True)
    after=Projection({'html':str(soup)})
    if before.text!=after.text or before.ruby!=after.ruby:raise ValueError('Historical frame changed protected content')
    return {'html':str(soup)}


def render_paragraph(conv,node,context):
    if not getattr(conv,'source_target_markers',False) or node.name!='p':raise ValueError('Invalid historical framed paragraph consumer')
    spec=json.loads(node['data-historical-frame-paragraph']);role=spec['role']
    if role not in ['title','list','note']:raise ValueError('Invalid historical paragraph role')
    before=metric(spec.get('before_pt',0),0,72,'framed paragraph gap');after=metric(spec.get('after_pt',0),0,72,'framed paragraph gap')
    setup=r'\parindent=0pt\relax\noindent '
    if role=='title':setup=r'\centering '+setup
    if role=='list':
        if not node.get_text().startswith(spec['marker']+' '):raise ValueError('Historical list marker changed')
        hang=metric(spec['hanging_em'],.5,3,'list hanging inset');setup=r'\hangindent='+str(hang)+r'em\hangafter=1'+setup
    body=''.join(conv.node(child,context)for child in node.children)
    conv.features.append(dict(kind='historical_frame_paragraph',**spec,canonical_changed=False))
    return r'\par\vspace{'+str(before)+r'pt}{'+setup+body+r'\par}\vspace{'+str(after)+r'pt}'


def native_rectangle(tex):
    """Read the one solid native frame, preserving every nested TeX group."""
    marker=r'\HistoricalFramed{solid}{'
    if tex.count(marker)!=1:raise ValueError('Labeled notice requires one complete native rectangle')
    prefix,tail=tex.split(marker);depth=1;index=0
    while index<len(tail):
        char=tail[index]
        if char=='\\':
            index+=2;continue
        if char=='{':depth+=1
        elif char=='}':
            depth-=1
            if depth==0:return prefix,tail[:index],tail[index+1:]
        index+=1
    raise ValueError('Unclosed native rectangle')


def labeled_box(conv,tex,value,binding,item_id):
    keys={'content_sha256','kind','font_role','label','label_width_em','width_fraction','rule_pt','padding_pt','top_padding_pt','bottom_padding_pt','evidence'}
    if set(binding)!=keys or binding['font_role']!='body':raise ValueError('Invalid labeled notice fields')
    label=binding['label'];plain=Projection(value).text
    if not isinstance(label,str) or not re.fullmatch(r'[（(][1-9][0-9]*[）)]',label) or not plain.startswith(label) or plain.count(label)!=1:
        raise ValueError('Labeled notice requires one exact leading passage label')
    width=metric(binding['label_width_em'],1.5,4,'notice label width')
    fraction=metric(binding['width_fraction'],.5,.9,'notice frame width')
    rule=metric(binding['rule_pt'],.3,1.5,'notice rule')
    pad=metric(binding['padding_pt'],4,20,'notice horizontal padding')
    top=metric(binding['top_padding_pt'],4,30,'notice top padding')
    bottom=metric(binding['bottom_padding_pt'],4,30,'notice bottom padding')
    begin,end=r'\begin{NoticeFrame}',r'\end{NoticeFrame}'
    native_frame=r'\HistoricalFramed{'in tex
    if native_frame:
        soup=BeautifulSoup(value['html'],'html.parser')
        frames=soup.select('[data-historical-framed-document="single"]')
        if len(frames)!=1 or begin in tex or end in tex:raise ValueError('Conflicting native labeled rectangle')
        prefix,body,suffix=native_rectangle(tex)
        body=r'\setlength\parindent{1em}'+body
    else:
        if tex.count(begin)!=1 or tex.count(end)!=1:raise ValueError('Labeled notice requires one complete native rectangle')
        prefix,body=tex.split(begin);body,suffix=body.split(end)
    match=re.fullmatch(r'\s*\\HistoricalInlinePassageLabel\{([^{}]+)\}\s*',prefix)
    if not match or unicodedata.normalize('NFKC',match[1])!=unicodedata.normalize('NFKC',label):
        raise ValueError('Labeled notice lost its bound inline label')
    if suffix.strip() or body.lstrip().startswith('['):raise ValueError('Labeled notice has conflicting frame geometry or exterior content')
    options=('nobreak=true,skipabove=0pt,skipbelow=0pt,linewidth='+str(rule)+'pt,innerleftmargin='+str(pad)
             +'pt,innerrightmargin='+str(pad)+'pt,innertopmargin='+str(top)+'pt,innerbottommargin='+str(bottom)+'pt')
    conv.features.append(dict(kind='historical_document_frame',target=item_id,frame='label_beside_box',label=label,
        label_width_em=width,width_fraction=fraction,font_role='body',content_sha256=binding['content_sha256'],canonical_changed=False))
    return (r'\par\noindent\begin{minipage}[t]{'+str(width)+r'em}\vspace{0pt}\noindent{\PassageNumerals '+match[1]
            +r'}\end{minipage}%'+ '\n'+r'\begin{minipage}[t]{'+str(fraction)+r'\linewidth}\vspace{0pt}'
            +begin+'['+options+']'+body+end+r'\end{minipage}\par')


def wrap(conv,tex,value,binding,unit,item_id):
    if digest(value)!=binding['content_sha256']:
        raise ValueError('Stale historical document frame')
    source_binding(unit,binding['evidence'])
    if binding['kind']=='label_beside_box':return labeled_box(conv,tex,value,binding,item_id)
    if binding['kind']not in ['folded_corner','curved_folded_corner','pinned_folded_corner'] or binding['font_role']not in ['instruction','body']:
        raise ValueError('Unsupported historical printed document frame')
    for key,lo,hi in [('rule_pt',.3,1.5),('padding_pt',4,20)]:
        n=binding[key]
        if isinstance(n,bool)or not isinstance(n,(int,float))or not lo<=n<=hi:
            raise ValueError('Invalid historical document frame metric')
    soup=BeautifulSoup(value['html'],'html.parser')
    frames=[d for d in soup.find_all('div')if 'border' in d.get('style','')]
    begin,end=r'\begin{NoticeFrame}',r'\end{NoticeFrame}'
    if len(frames)!=1 or tex.count(begin)!=1 or tex.count(end)!=1:
        raise ValueError('Historical document frame requires one complete source frame')
    prefix,body=tex.split(begin);body,suffix=body.split(end)
    conv.features.append(dict(kind='historical_document_frame',target=item_id,frame=binding['kind'],font_role=binding['font_role'],content_sha256=binding['content_sha256'],canonical_changed=False))
    if binding['kind']!='folded_corner':
        width=metric(binding['fold_width_pt'],10,80,'fold width');height=metric(binding['fold_height_pt'],8,60,'fold height')
        top=metric(binding['top_padding_pt'],4,60,'frame top padding');bottom=metric(binding['bottom_padding_pt'],4,80,'frame bottom padding')
        if bottom<height+4:raise ValueError('Historical folded corner lacks content clearance')
        pins=binding['kind']=='pinned_folded_corner'
        conv.features[-1].update(pin_positions=['top_left','top_right','bottom_left']if pins else[],fold_width_pt=width,fold_height_pt=height)
        if 'before_pt'in binding:
            before=metric(binding['before_pt'],0,72,'frame entry gap')
            prefix+=r'\par\vspace{'+str(before)+'pt}'
            conv.features[-1]['before_pt']=before
        if 'width_fraction'in binding:
            fraction=metric(binding['width_fraction'],.5,1,'frame width fraction')
            prefix+=r'\par\noindent\hfill\begin{minipage}{'+str(fraction)+r'\linewidth}'
            suffix=r'\end{minipage}\hfill\par'+suffix
            conv.features[-1]['width_fraction']=fraction
        face=r'\InstructionLatin\InstructionJapanese 'if binding['font_role']=='instruction'else ''
        return (prefix+r'{\renewcommand\FoldRuleWidth{'+str(binding['rule_pt'])+r'}\renewcommand\FoldCornerScaleX{'+str(width/33)
            +r'}\renewcommand\FoldCornerScaleY{'+str(height/21)+r'}\renewcommand\HistoricalNoticeTopPadding{'+str(top)
            +r'pt}\renewcommand\HistoricalNoticeBottomPadding{'+str(bottom)+r'pt}\HistoricalFoldedNotice{'+str(binding['padding_pt'])
            +'}{'+('1'if pins else'0')+'}{'+face+body+'}}'+suffix)
    if binding['font_role']!='instruction' or any(k in binding for k in ['before_pt','width_fraction']):raise ValueError('Legacy folded frame requires unchanged instruction geometry')
    return (prefix+r'{\renewcommand\FoldRuleWidth{'+str(binding['rule_pt'])+r'}\FoldedMemo{'+str(binding['padding_pt'])
            +r'}{\InstructionLatin\InstructionJapanese '+body+'}}'+suffix)
