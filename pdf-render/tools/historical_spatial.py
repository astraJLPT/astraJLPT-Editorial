"""Source-bound Old paragraph geometry, sentence blanks and observed word gaps."""
import json,re
from bs4 import BeautifulSoup
from model import Projection,digest
from presentation import source_binding


def collect(model):
    result={}
    for section in model['document']['sections']:
        for item in section['items']:
            bindings=model['layout']['items'][item['id']].get('historical_spatial',{})
            for slot,b in bindings.items():
                if model.get('exam',{}).get('generation')!='historical-1991-2009':raise ValueError('Old spatial role outside Old')
                value=item['options'][int(slot.split('/')[1])] if slot.startswith('options/') else item[slot]
                if digest(value)!=b['content_sha256']:raise ValueError('Stale historical spatial field')
                source_binding(model['unit'],b['evidence'])
                key=item['id']+('/'+slot if slot.startswith('options/') else '')
                if key in result:raise ValueError('Ambiguous historical spatial target')
                result[key]=(b,value,slot)
    return result


def prepare(value,binding,original,slot):
    if digest(original)!=binding['content_sha256']:raise ValueError('Stale historical spatial input')
    before=Projection(value)
    soup=BeautifulSoup(value['html'],'html.parser') if isinstance(value,dict) else None
    if binding.get('paragraphs') or binding.get('sentence_blank') or binding.get('sequence') or binding.get('frames') or binding.get('ordering_sequence'):
        if soup is None:raise ValueError('Spatial structure requires canonical HTML')
    frame_specs=binding.get('frames',[])
    if frame_specs:
        original_frames=BeautifulSoup(original['html'],'html.parser').select('[data-historical-framed-document="single"]')
        frames=soup.select('[data-historical-framed-document="single"]');seen=set()
        for spec in frame_specs:
            required={'index','count','frame_sha256','width_fraction','inset_em'}
            if not required<=set(spec) or set(spec)-required-{'padding_y_pt','before_pt','first_line_indent_em'}:raise ValueError('Unknown frame geometry')
            for key in ['padding_y_pt','before_pt']:
                if key in spec and(type(spec[key])not in [int,float]or not 0<=spec[key]<=30):raise ValueError('Invalid source-bound frame spacing')
            if 'first_line_indent_em'in spec and(type(spec['first_line_indent_em'])not in [int,float]or not 0<=spec['first_line_indent_em']<=2):raise ValueError('Invalid source frame first-line indent')
            index=spec['index'];width=spec['width_fraction'];inset=spec['inset_em']
            if (type(index)is not int or index in seen or type(spec['count'])is not int
                    or len(frames)!=len(original_frames)or len(frames)!=spec['count']or not 0<=index<len(frames)
                    or type(width)not in [int,float]or not .35<=width<=.9
                    or type(inset)not in [int,float]or not 0<=inset<=5
                    or digest({'html':str(original_frames[index])})!=spec['frame_sha256']):
                raise ValueError('Stale or invalid source-bound frame geometry')
            seen.add(index)
            frames[index]['data-historical-frame-width']=str(width)
            frames[index]['data-historical-frame-inset']=str(inset)
            for key in ['padding_y_pt','before_pt','first_line_indent_em']:
                if key in spec:frames[index]['data-historical-frame-'+key.replace('_','-')]=str(spec[key])
    if binding.get('ordering_sequence'):
        b=binding['ordering_sequence']
        limits={'fragment_width_fraction':(.7,.9),'label_width_em':(1,2),'inset_em':(0,4),'flow_gap_pt':(0,18),'first_before_pt':(0,60),'next_before_pt':(0,60),'padding_x_pt':(4,18),'padding_y_pt':(0,12)}
        if set(b)!=set(limits)or any(type(b[k])not in [int,float]or not lo<=b[k]<=hi for k,(lo,hi)in limits.items()):raise ValueError('Invalid three-slot ordering geometry')
        alternatives=soup.select('[data-historical-labeled-frame]');flow=soup.select('[data-historical-order-flow="vertical"]')
        from historical_nodes import order_flow_values
        if [n['data-historical-labeled-frame']for n in alternatives]!=list('ABC')or len(flow)!=1:raise ValueError('Ordering requires exactly A-C and one flow')
        values=order_flow_values(flow[0])
        if values!=['⬇','（\u3000ア\u3000）','⬇','（\u3000イ\u3000）','⬇','（\u3000ウ\u3000）','⬇']:raise ValueError('Ordering slots/arrows changed')
        flow[0].attrs.pop('data-historical-compact-sequence',None)
        flow[0]['data-historical-order-gap']=str(b['flow_gap_pt'])
        for index,node in enumerate(alternatives):
            node['data-historical-order-frame']=json.dumps(dict(b,first=index==0))
    for spec in binding.get('paragraphs',[]):
        hits=[p for p in soup.find_all('p') if Projection({'html':str(p)}).text.strip()==spec['text']]
        if len(hits)!=1:raise ValueError('Spatial paragraph needs one complete exact paragraph')
        options={k:v for k,v in spec.items() if k!='text'}
        if set(options)-{'inset_em','before_pt','after_pt','font','align','first_line_outdent_em','first_line_indent_em'}:raise ValueError('Unknown paragraph geometry')
        if type(options.get('inset_em',0))not in [int,float]or not 0<=options.get('inset_em',0)<=4 or any(type(options.get(k,0))not in [int,float]or not 0<=options.get(k,0)<=30 for k in ['before_pt','after_pt']):raise ValueError('Invalid paragraph spacing')
        indent=options.get('first_line_indent_em',0)
        if type(indent)not in [int,float]or not 0<=indent<=2 or (indent and options.get('first_line_outdent_em',0)):raise ValueError('Invalid source paragraph first-line indent')
        outdent=options.get('first_line_outdent_em',0)
        if type(outdent)not in [int,float]or not 0<=outdent<=options.get('inset_em',0):raise ValueError('Invalid source paragraph first-line outdent')
        if options.get('font') not in [None,'instruction'] or options.get('align','left') not in ['left','center','right']:raise ValueError('Unknown spatial type/alignment')
        if options.get('font')=='instruction':
            for n in hits[0].find_all(['b','strong']):n.unwrap()
        hits[0]['data-historical-spatial-paragraph']=json.dumps(options)
    if binding.get('sequence'):
        b=binding['sequence'];frames=soup.select('[data-historical-labeled-frame]');slots=soup.select('[data-historical-continuation-slot]')
        standalone=soup.select('[data-historical-framed-document="single"]')
        mixed=(len(slots)==3 and [n['data-historical-continuation-slot']for n in slots]==list('アイエ') and len(standalone)==1 and standalone[0].get_text(strip=True)=='ウ')
        solid=(not slots and len(standalone)==4 and [n.get_text(strip=True)for n in standalone]==list('アイウエ'))
        if (len(frames)!=4 or [n['data-historical-labeled-frame']for n in frames]!=list('ABCD')
            or not .75<=b['fragment_width_fraction']<=.9
            or (solid and(set(b)!={'fragment_width_fraction'}or any(n.get('data-historical-border-style')!='dashed'for n in frames)))
            or (not solid and(not(len(slots)==4 or mixed)or not 1.5<=b['slot_bottom_em']<=4))):
            raise ValueError('Invalid bound four-fragment sequence')
        geometry=b.get('fragment_geometry')
        if geometry is not None:
            limits={'label_width_em':(1,2),'inset_em':(0,4),'first_before_pt':(0,60),'next_before_pt':(0,60),'padding_x_pt':(4,18),'padding_y_pt':(0,12),'last_after_pt':(0,30)}
            if (solid or (not mixed and [n['data-historical-continuation-slot']for n in slots]!=list('アイウエ'))
                or any(n.get('data-historical-border-style')!='dashed'for n in frames)
                or not isinstance(geometry,dict)or set(geometry)-set(limits)or set(limits)-{'last_after_pt'}-set(geometry)
                or any(type(geometry[k])not in [int,float]or not lo<=geometry[k]<=hi for k,(lo,hi)in limits.items()if k in geometry)):
                raise ValueError('Invalid four-slot alternative frame geometry')
            for index,node in enumerate(frames):
                node['data-historical-order-frame']=json.dumps(dict(geometry,fragment_width_fraction=b['fragment_width_fraction'],first=index==0,last=index==len(frames)-1,sequence_kind='mixed_continuation_and_standalone_slot'if mixed else'four_continuation_slots'))
        slot_geometry=b.get('slot_geometry')
        if slot_geometry is not None:
            if (solid or (not mixed and [n['data-historical-continuation-slot']for n in slots]!=list('アイウエ'))
                or not isinstance(slot_geometry,dict)or set(slot_geometry)-{'inset_em','first_line_indent_em','first_before_pt'}or not {'inset_em','first_line_indent_em'}<=set(slot_geometry)
                or type(slot_geometry['inset_em'])not in [int,float]or not 0<=slot_geometry['inset_em']<=3
                or not isinstance(slot_geometry['first_line_indent_em'],list)or len(slot_geometry['first_line_indent_em'])!=len(slots)
                or any(type(v)not in [int,float]or not 0<=v<=2 for v in slot_geometry['first_line_indent_em'])
                or type(slot_geometry.get('first_before_pt',0))not in [int,float]or not 0<=slot_geometry.get('first_before_pt',0)<=30):
                raise ValueError('Invalid four-slot passage geometry')
            for index,(node,indent)in enumerate(zip(slots,slot_geometry['first_line_indent_em'])):
                params=dict(inset_em=slot_geometry['inset_em'],first_line_indent_em=indent)
                if index==0 and 'first_before_pt'in slot_geometry:params['before_pt']=slot_geometry['first_before_pt']
                node['data-historical-slot-geometry']=json.dumps(params)
            if mixed:standalone[0]['data-historical-slot-inset']=str(slot_geometry['inset_em'])
        for n in frames:n['data-historical-fragment-width']=str(b['fragment_width_fraction'])
        for n in slots:n['data-historical-slot-bottom']=str(b['slot_bottom_em'])
        if 'standalone_height_em'in b:
            if not mixed or not 2.8<=b['standalone_height_em']<=4.5:raise ValueError('Invalid standalone insertion height')
            standalone[0]['data-historical-insertion-height']=str(b['standalone_height_em'])
    blank=binding.get('sentence_blank')
    if blank:
        if not 5<=blank['width_em']<=8 or not .6<=blank['height_em']<=1.2:raise ValueError('Invalid sentence blank dimensions')
        hits=[n for n in soup.find_all('span') if 'border:' in n.get('style','') and n.get_text()==blank['text']]
        if len(hits)!=blank['occurrences'] or blank['text'].strip() or any(n.find() for n in hits):raise ValueError('Linked blank requires exact existing empty bordered span')
        for n in hits:n['data-historical-sentence-blank']=json.dumps(blank)
    if soup is not None:value={'html':str(soup)}
    groups=binding.get('word_groups',[])
    if groups:
        p=Projection(original);offsets=[b['offset'] for b in groups]
        if offsets!=sorted(set(offsets)):raise ValueError('Repeated/unordered Old word boundary')
        for b in groups:
            n=b['offset']
            if not 0<n<len(p.text) or p.text[n-1].isspace() or p.text[n].isspace() or any(r['start']<n<r['end'] for r in p.ruby):raise ValueError('Old boundary splits ruby or duplicates a space')
            if p.text[max(0,n-12):n]!=b['left'] or p.text[n:n+12]!=b['right']:raise ValueError('Stale Old word-boundary anchor')
        from word_groups import prepare as prepare_groups
        value=prepare_groups(value,original,dict(rendered_sha256=digest(original),slot=slot,boundaries=groups))
        value={'html':value['html'].replace('data-authored-word-gap=','data-historical-word-gap=')}
    after=Projection(value)
    if before.text!=after.text or before.ruby!=after.ruby:raise ValueError('Spatial roles changed canonical text/ruby')
    return value


def render(conv,node,context):
    if node.has_attr('data-historical-word-gap'):
        ident=node['data-historical-word-gap']
        if node.contents or not re.fullmatch(r'h21-[a-f0-9]{16}',ident):raise ValueError('Invalid source word gap')
        conv.features.append(dict(kind='historical_source_word_gap',id=ident,width_em=conv.word_space_em))
        return r'\HistoricalSourceWordGap{'+str(conv.word_space_em)+'}{'+ident+'}'
    if node.has_attr('data-historical-sentence-blank'):
        b=json.loads(node['data-historical-sentence-blank'])
        if node.get_text()!=b['text'] or node.find():raise ValueError('Altered sentence blank')
        conv.features.append(dict(kind='historical_sentence_blank',**b))
        return r'\HistoricalSentenceBlank{'+str(b['width_em'])+'}{'+str(b['height_em'])+'}'
    if node.has_attr('data-historical-spatial-paragraph'):
        b=json.loads(node['data-historical-spatial-paragraph']);body=''.join(conv.node(c,context) for c in node.children)
        align={'left':r'\raggedright','center':r'\centering','right':r'\raggedleft'}[b.get('align','left')]
        font=r'\InstructionLatin\InstructionJapanese ' if b.get('font')=='instruction' else ''
        conv.features.append(dict(kind='historical_spatial_paragraph',text=Projection({'html':str(node)}).text,**b))
        lead=r'\hspace*{-'+str(b['first_line_outdent_em'])+'em}' if b.get('first_line_outdent_em',0)else ''
        if b.get('first_line_indent_em',0):lead=r'\hspace*{'+str(b['first_line_indent_em'])+'em}'
        return (r'\par\addvspace{'+str(b.get('before_pt',0))+r'pt}{'+font+align+r'\parindent=0pt\advance\leftskip by '+str(b.get('inset_em',0))+r'em\relax\noindent '+lead+body+r'\par}\nobreak\addvspace{'+str(b.get('after_pt',0))+r'pt}')
    return None


def verify(tex,bindings):
    expected=[b['id'] for binding,_,_ in bindings.values() for b in binding.get('word_groups',[])]
    used=re.findall(r'\\HistoricalSourceWordGap\{[^{}]+\}\{(h21-[a-f0-9]{16})\}',tex)
    if sorted(expected)!=sorted(used) or len(used)!=len(set(used)):raise ValueError('Unused/repeated source-bound Old word gaps')
    return dict(fields=len(bindings),word_boundaries=len(used),all_consumed_once=True)
