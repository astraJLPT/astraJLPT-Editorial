"""Explicit source-bound historical labels and option arrangements.

This module is called only by the historical dispatcher. No unit-name heuristic,
private audit file or reconstructed legacy payload is a runtime content source.
"""
import base64
import copy
import hashlib
import re
from bs4 import BeautifulSoup
from model import digest, Projection
from presentation import source_binding

LABELS={'parenthesized','question','bracketed_query','bracketed_question','bracketed_shitsumon','bracketed_shitsumon_numbered','circled','query'}

def braced_stem(item,binding,stem=None):
    """Move an exact shared phrase to its source side of four alternatives."""
    sides=[key for key in ('braced_prefix','braced_suffix') if key in binding]
    if len(sides)>1:
        # Both source phrases are distinct final paragraphs: prefix, suffix.
        # Validate each against the original stem hash, then remove in reverse
        # order. Existing one-sided paths retain their validation and emission.
        suffix_binding={k:v for k,v in binding.items()if k!='braced_prefix'}
        prefix_binding={k:v for k,v in binding.items()if k!='braced_suffix'}
        without_suffix=braced_stem(item,suffix_binding,stem)
        return braced_stem(item,prefix_binding,without_suffix)
    side=sides[0]if sides else 'braced_prefix'
    b=binding.get(side)
    if b is None:return item['stem']if stem is None else stem
    width_key='prefix_width_em'if side=='braced_prefix'else'suffix_width_em'
    width=b.get(width_key);text=b.get('text')
    if (binding.get('kind')!='grid'or binding.get('columns')!=1 or binding.get('source_numbered')is not False
        or set(b)-{'text','stem_sha256',width_key,'indent_em','brace_gap_em'} or not {'text','stem_sha256',width_key}<=set(b) or digest(item['stem'])!=b['stem_sha256']
        or not isinstance(text,str)or not text.strip()or len(text)>20
        or isinstance(width,bool)or not isinstance(width,(int,float))or not 3<=width<=14
        or any(k in binding for k in ['paired_fragments','contiguous_strip','column_widths'])):
        raise ValueError('Stale or invalid historical braced prefix')
    for key,high in [('indent_em',5),('brace_gap_em',2)]:
        if key in b and (side!='braced_prefix' or type(b[key])not in (int,float) or not 0<=b[key]<=high):
            raise ValueError('Invalid source-bound shared-prefix spacing')
    value=item['stem']if stem is None else stem
    if not isinstance(value,dict)or set(value)!={'html'}:raise ValueError('Braced prefix requires separate canonical paragraphs')
    soup=BeautifulSoup(value['html'],'html.parser');nodes=[n for n in soup.contents if str(n).strip()]
    if (len(nodes)<2 or any(getattr(n,'name',None)!='p'for n in nodes)
        or any(tag.name not in {'ruby','rt','rp'} or tag.attrs for tag in nodes[-1].find_all())
        or Projection({'html':nodes[-1].decode_contents()}).text!=text):
        raise ValueError('Braced prefix differs from final canonical paragraph')
    nodes[-1].extract()
    return {'html':str(soup)}

def collect_stems(model):
    bindings={iid:m['historical_question_prose']for iid,m in model['layout']['items'].items()if 'historical_question_prose'in m}
    if not bindings:return {}
    if model.get('exam',{}).get('generation')!='historical-1991-2009':
        raise ValueError('Historical question prose outside Old JLPT')
    items={i['id']:i for s in model['document']['sections']for i in s['items']}
    for iid,b in bindings.items():
        if 'stem'not in items[iid]or digest(items[iid]['stem'])!=b['stem_sha256']or b['font_role']!='instruction':
            raise ValueError('Stale or invalid historical question prose role')
        source_binding(model['unit'],b['evidence'])
    return bindings

def collect(model):
    labels={};options={};breaks=set()
    for section in model['document']['sections']:
        default=model['layout']['sections'][section['id']].get('historical_question_label')
        if default:
            source_binding(model['unit'],default['evidence'])
            if default['kind']not in LABELS:raise ValueError('Unknown historical question label')
        for item in section['items']:
            meta=model['layout']['items'][item['id']]
            label=meta.get('historical_question_label',default)
            if 'stem'in item and label:
                source_binding(model['unit'],label['evidence'])
                if label['kind']not in LABELS:raise ValueError('Unknown historical question label')
                labels[item['id']]=label['kind']
            binding=meta.get('historical_options')
            if binding:
                if 'stem'not in item or digest(item['options'])!=binding['options_sha256']:
                    raise ValueError('Stale historical options binding')
                source_binding(model['unit'],binding['evidence'])
                if binding['kind']not in {'grid','shared_header_table','chronology','combination'}:
                    raise ValueError('Unknown historical options kind')
                if binding['kind']=='grid'and(binding.get('columns')not in [1,2,3,4]or type(binding.get('source_numbered'))is not bool):
                    raise ValueError('Invalid historical option grid')
                if any(key in binding for key in ('braced_prefix','braced_suffix')):
                    if model.get('exam',{}).get('generation')!='historical-1991-2009'or any(k in meta for k in ['dialogue','historical_target_row','historical_answer_list','historical_label_answer']):
                        raise ValueError('Conflicting or nonhistorical braced prefix')
                    braced_stem(item,binding)
                if 'allow_image_option_breaks'in binding:
                    allowed={'kind','options_sha256','evidence','columns','source_numbered','multiline','row_gap_pt','panel_width_fraction','allow_image_option_breaks'}
                    conflicts={'dialogue','historical_target_row','historical_answer_list','historical_label_answer','historical_question_boundary','historical_inline_dialogue_question'}
                    if (binding['allow_image_option_breaks']is not True
                        or model.get('exam',{}).get('generation')!='historical-1991-2009'
                        or binding['kind']!='grid'or binding.get('columns')!=1
                        or binding.get('source_numbered')is not True or binding.get('multiline',False)
                        or set(binding)-allowed or conflicts.intersection(meta)
                        or len(item['options'])!=4):
                        raise ValueError('Image-option flow requires four source-numbered single-column image panels')
                    for value in item['options']:
                        if not isinstance(value,dict)or set(value)!={'html'}:
                            raise ValueError('Image-option flow requires image-only canonical choices')
                        soup=BeautifulSoup(value['html'],'html.parser')
                        if len(soup.find_all('img'))!=1 or soup.get_text(strip=True):
                            raise ValueError('Image-option flow cannot duplicate embedded labels or split textual choices')
                options[item['id']]=binding
            boundary=meta.get('historical_page_break_after')
            if boundary:
                if 'content'not in item or digest(item['content'])!=boundary['content_sha256']:
                    raise ValueError('Stale historical passage boundary')
                source_binding(model['unit'],boundary['evidence']);breaks.add(item['id'])
    return labels,options,breaks

def question_label(kind,number,style=None):
    if not re.fullmatch(r'[1-9][0-9]*',number):raise ValueError('Historical local number must be positive')
    if kind=='circled'and int(number)>20:raise ValueError('Historical circled subquestion must be1–20')
    value={'parenthesized':'（'+number+'）','question':'問'+number,
           'bracketed_query':'【問い】','bracketed_question':'【問'+number+'】','bracketed_shitsumon':'【しつもん】','bracketed_shitsumon_numbered':'【しつもん'+number+'】',
           'circled':chr(0x2460+int(number)-1)if kind=='circled'else'', 'query':'問い'}[kind]
    indent='8em'if kind=='bracketed_shitsumon_numbered'else'7em'if kind=='bracketed_shitsumon'else'4.6em'if kind.startswith('bracketed')else'2.8em'
    p=(style or {}).get('historical_typography',{})
    if kind=='parenthesized' and 'parenthesized_indent_em'in p:
        val=p['parenthesized_indent_em']
        if type(val)not in [int,float]or not 1.8<=val<=3:raise ValueError('Invalid parenthesized question indent')
        indent=str(val)+'em'
    from historical_typography import question_tex
    label_tex=(r'{\rmfamily\mcfamily\mdseries\HistoricalCompactNumber{'+number+'}}'
               if kind=='parenthesized'else r'{\HistoricalQuestionJapanese '+value+'}'if kind in {'bracketed_shitsumon','bracketed_shitsumon_numbered','query'}else r'{\rmfamily\mcfamily\mdseries '+value+'}'if kind=='circled'else question_tex(value))
    if kind=='parenthesized' and 'parenthesized_size_pt'in p:
        size=p['parenthesized_size_pt']
        if type(size)not in [int,float]or not 9<=size<=14:raise ValueError('Invalid parenthesized label size')
        label_tex=r'{\fontsize{'+str(size)+'}{'+str(size+2)+r'}\selectfont '+label_tex+'}'
    query_geometry=p.get('query_label')if kind=='query'else p.get('bracketed_query_label')if kind=='bracketed_query'else p.get('bracketed_numbered_query_label')if kind=='bracketed_question'else p.get('shitsumon_label') if kind in {'bracketed_shitsumon','bracketed_shitsumon_numbered'}else None
    query_width_bounds=(2,4)if kind=='query'else(3,5)if kind in {'bracketed_query','bracketed_question'}else(5,9)
    if query_geometry is not None:
        if (not isinstance(query_geometry,dict)or set(query_geometry)!={'left_inset_em','width_em','font'}
            or type(query_geometry['left_inset_em'])not in [int,float]or not 0<=query_geometry['left_inset_em']<=4
            or type(query_geometry['width_em'])not in [int,float]or not query_width_bounds[0]<=query_geometry['width_em']<=query_width_bounds[1]
            or query_geometry['font']not in ['body','heading']):
            raise ValueError('Invalid Old kana query-label geometry')
        left=query_geometry['left_inset_em'];width=query_geometry['width_em']+(1 if kind=='bracketed_shitsumon_numbered'else 0)
        face=r'\rmfamily\mcfamily\mdseries 'if query_geometry['font']=='body'else r'\HistoricalQuestionJapanese '
        label_tex=r'\hspace*{'+str(left)+'em}{'+face+value+'}'
        indent=str(left+width)+'em'
    setup=(r'\renewcommand\QNumber[1]{'+label_tex+'}'
           r'\renewcommand\QuestionIndent{'+indent+'}')
    if kind in {'query','bracketed_query','bracketed_question'}and query_geometry is not None:
        setup+=r'\renewcommand\OptionIndent{'+str((style or {}).get('option_indent_em',2.1)+query_geometry['left_inset_em'])+'em}'
    # Wide kana query labels reserve their own continuation measure. Sources
    # place following lines one moji before the first-line stem, irrespective
    # of the narrower parenthesized-question or option continuation insets.
    pullback=p.get('question_continuation_pullback_em',1 if kind in {'bracketed_shitsumon','bracketed_shitsumon_numbered'}else None)
    if pullback is not None:
        if type(pullback)not in [int,float]or not .5<=pullback<=1.5:raise ValueError('Invalid Old question continuation offset')
        setup+=r'\renewcommand\QuestionContinuationIndent{\dimexpr\QuestionIndent-'+str(pullback)+r'em\relax}'
    return value,setup

def aligned_pair_options(conv,item,binding,converted):
    """Align two literal, optionally ruby-bearing cells without converting twice."""
    b=binding['aligned_pairs'];keys=b.get('keys');width=b.get('first_column_width_em')
    if (binding.get('kind')!='grid' or binding.get('columns')!=1 or binding.get('source_numbered')is not False
        or set(b)!={'keys','first_column_width_em'} or not isinstance(keys,list)or len(keys)!=2
        or len(set(keys))!=2 or any(not isinstance(k,str)or not re.fullmatch(r'[一-龯ぁ-んァ-ヶA-Za-z]{1,6}',k)for k in keys)
        or type(width)not in [int,float]or not 5<=width<=16 or len(converted)!=4
        or any(k in binding for k in ['paired_fragments','multiline','image_panels','source_four_panel_page','contiguous_strip','braced_prefix','braced_suffix','text_horizontal_scales'])):
        raise ValueError('Invalid bound paired columns')
    out=[]
    for value,tex in zip(item['options'],converted):
        if isinstance(value,dict):
            if set(value)!={'html'}:raise ValueError('Paired columns require plain or inline ruby text')
            soup=BeautifulSoup(value['html'],'html.parser')
            if any(n.name not in ['ruby','rt','rp']or n.attrs for n in soup.find_all()):
                raise ValueError('Paired columns cannot contain block or styled content')
        elif not isinstance(value,str):raise ValueError('Paired columns require literal text')
        parts=Projection(value).text.split('　');cells=tex.split('　')
        if (len(parts)!=2 or len(cells)!=2 or len(parts[0])>width
            or any(not p.startswith(k+'：')or not p[len(k)+1:]or re.search(r'\s|：',p[len(k)+1:])for k,p in zip(keys,parts))
            or any(not t.startswith((conv.text(k+'：'),conv.text(k)+r'\NoteDefinitionColon{}'))for k,t in zip(keys,cells))):
            raise ValueError('Paired keys, delimiter or converted cells differ from binding')
        # The exact canonical cells and delimiters were checked above. Both
        # bound Japanese labels use the shared separator display at emission.
        cells=[(conv.text(k)+r'\NoteDefinitionColon{}'+t[len(conv.text(k+'：')):])
               if t.startswith(conv.text(k+'：')) else t for k,t in zip(keys,cells)]
        out.append(r'\makebox['+str(width)+r'em][l]{'+cells[0]+'}'+cells[1])
    conv.features.append(dict(kind='historical_aligned_pair_columns',target=item['id'],keys=keys,first_column_width_em=width,canonical_changed=False))
    return out

def options_tex(conv,item,binding,converted,row_gap_pt=None):
    kind=binding['kind'];values=item['options']
    conv.features.append({'kind':'historical_options','target':item['id'],
        'arrangement':kind,'options_sha256':digest(values),'columns':binding.get('columns'),
        'source_numbered':binding.get('source_numbered',False),'canonical_changed':False})
    scales=binding.get('text_horizontal_scales',{})
    if scales:
        if (kind!='grid' or binding.get('source_numbered')is not False or binding.get('columns')not in [2,3,4]
                or binding.get('multiline') or not isinstance(scales,dict)):
            raise ValueError('Choice width exception requires a textual multicolumn grid')
        converted=list(converted)
        for number,scale in scales.items():
            if number not in {'1','2','3','4'} or type(scale)not in [int,float] or not .8<=scale<1:
                raise ValueError('Invalid source-bound choice horizontal scale')
            index=int(number)-1;value=values[index]
            if not isinstance(value,str) or not value.strip() or '\n'in value or '\r'in value:
                raise ValueError('Choice width exception requires exact single-line text')
            converted[index]=r'\scalebox{'+str(scale)+r'}[1]{'+converted[index]+'}'
            conv.features.append(dict(kind='historical_choice_width_exception',target=item['id'],choice=int(number),text=value,horizontal_scale=scale,vertical_scale=1,canonical_changed=False))
    if kind=='grid':
        if 'aligned_pairs'in binding:converted=aligned_pair_options(conv,item,binding,converted)
        columns=binding['columns'];numbered=binding['source_numbered'];parts=[]
        if binding.get('image_panels'):
            if numbered or columns not in [1,2,4] or any(k in binding for k in ['paired_fragments','contiguous_strip','braced_prefix','braced_suffix','source_four_panel_page']):
                raise ValueError('Image-panel grid requires separate native option labels')
            from historical_nodes import image_at_width
            panel_width=binding.get('panel_width_fraction',1)
            if type(panel_width)not in [int,float] or not .4<=panel_width<=1:raise ValueError('Invalid image-panel scale')
            position=binding.get('panel_label_position','beside')
            grid_width=binding.get('panel_grid_width_fraction',1)
            left=binding.get('panel_left_indent_em',0)
            if(position not in ['beside','above']or type(grid_width)not in [int,float]or not .4<=grid_width<=1
               or type(left)not in [int,float]or not 0<=left<=4):raise ValueError('Invalid image-panel label/grid geometry')
            if position=='beside'and(grid_width!=1 or left!=0):raise ValueError('Inset image grid requires above-panel labels')
            label_inset=binding.get('panel_label_inset_em',0)
            if type(label_inset)not in [int,float]or not 0<=label_inset<=2 or(label_inset and position!='above'):
                raise ValueError('Invalid above-panel numeral inset')
            label_prefix=r'\hspace*{'+str(label_inset)+'em}'if label_inset else''
            before=binding.get('panel_before_pt',0);label_gap=binding.get('panel_label_gap_pt',2)
            if any(type(v)not in [int,float]or not 0<=v<=20 for v in [before,label_gap]):raise ValueError('Invalid image-panel vertical spacing')
            if position!='above'and(before or label_gap!=2):raise ValueError('Panel vertical spacing requires above-panel labels')
            hashes=[]
            for n,value in enumerate(values,1):
                if not isinstance(value,dict)or set(value)!={'html'}:raise ValueError('Image-panel option must be exact rich content')
                soup=BeautifulSoup(value['html'],'html.parser')
                if len(soup.find_all('img'))!=1 or soup.get_text(strip=True):raise ValueError('Image-panel option must contain exactly one image and no text')
                node=soup.img;hashes.append(hashlib.sha256(base64.b64decode(node['src'].split(',',1)[1])).hexdigest())
                graphic=image_at_width(conv,node,panel_width,block=False)
                width={1:'1',2:'.5',4:'.25'}[columns]
                if position=='above':
                    parts.append(r'\noindent\begin{minipage}[t]{'+width+r'\linewidth}\vspace{0pt}\noindent'+label_prefix+r'{\ChoiceNumerals '+str(n)+r'}\par\nointerlineskip\vspace{'+str(label_gap)+r'pt}\noindent '+graphic+r'\par\end{minipage}')
                else:
                    parts.append(r'\noindent\begin{minipage}[t]{'+width+r'\linewidth}\vspace{0pt}\noindent'
                        r'\begin{minipage}[t]{1.8em}\vspace{0pt}{\ChoiceNumerals '+str(n)+r'}\end{minipage}'
                        r'\begin{minipage}[t]{\dimexpr\linewidth-1.8em\relax}\vspace{0pt}\noindent '+graphic+r'\par\end{minipage}\par\end{minipage}')
                if n%columns==0:parts.append(r'\par\nointerlineskip'+(r'\vspace{'+str(binding.get('row_gap_pt',8))+r'pt}'if n<4 else''))
                else:parts.append('%\n')
            conv.features.append(dict(kind='historical_image_option_grid',target=item['id'],columns=columns,image_sha256=hashes,original_pixels_preserved=True,canonical_changed=False))
            if position=='above':
                conv.features[-1].update(label_position=position,grid_width_fraction=grid_width,left_indent_em=left)
                if label_inset:conv.features[-1]['label_inset_em']=label_inset
                if before or label_gap!=2:conv.features[-1].update(before_pt=before,label_gap_pt=label_gap)
                return(r'\par'+(r'\vspace{'+str(before)+'pt}'if before else'')+r'\noindent\hspace*{'+str(left)+r'em}\begin{minipage}[t]{'+str(grid_width)+r'\linewidth}\vspace{0pt}'+''.join(parts)+r'\par\end{minipage}\par')
            return ''.join(parts)
        if binding.get('source_four_panel_page'):
            sources={
                ('reading-q017','8560bf8ef92b4e2d58559b3e14882b76d3307586f5d55b0e7fa33cc2f5fa931f'):
                    ('N1_1997',314,'9e8a7a531e22215c32a0cf53e102dc9f540c5cbee1a9137387ee67b1dee72c70'),
                ('reading-q018','0a6634758dce0a258ffaf92c6c8ea1a738a4b8ceb52cd75cb44a4d8d340dfa64'):
                    ('N2_1997',292,'b7ff1e3a7e7cc86c542627ad2f30ee08a78fb396fd0a465baebd4479abbb47ec')}
            source=sources.get((item['id'],binding['evidence']['source_sha256']))
            if (source is None or columns!=1 or numbered or len(values)!=4
                    or binding['evidence']['physical_pages']!=[source[1]] or digest(values)!=source[2]):
                raise ValueError('Invalid source-bound four-panel page')
            from historical_artwork import render as render_art
            for n,value in enumerate(values,1):
                soup=BeautifulSoup(value['html'],'html.parser')
                if len(soup.find_all('img'))!=1 or soup.get_text(strip=True):raise ValueError('Four-panel page requires four image-only options')
                key=hashlib.sha256(base64.b64decode(soup.img['src'].split(',',1)[1])).hexdigest()
                art=conv.historical_artworks[key]['art']
                if (art['unit']!=source[0] or art['item_id']!=item['id'] or art['kind']!='household_purchase_option'
                        or art['data']['option']!=n or art['source']['physical_page']!=source[1]
                        or art['source']['source_sha256']!=binding['evidence']['source_sha256']):
                    raise ValueError('Four-panel page must retain its exact source artwork/order')
                graphic=render_art(conv,key,conv.embedded_image_styles[key],block=False)
                # The first panel alone carries the shared legend above its
                # axes. Keep its choice number aligned with the plot top.
                drop=r'\dimexpr-.75\baselineskip-.0766\linewidth\relax' if n==1 else r'-.75\baselineskip'
                parts.append(r'\noindent\makebox[1.8em][l]{\raisebox{'+drop+r'}[0pt][0pt]{{\ChoiceNumerals '+str(n)+r'}}}\begin{minipage}[t]{\dimexpr\linewidth-1.8em\relax}\vspace{0pt}'+graphic+r'\par\end{minipage}\par\nointerlineskip')
                if n<4:parts.append(r'\vspace{6pt}')
            conv.features.append(dict(kind='historical_four_panel_source_page',target=item['id'],source_page=source[1],options=4,canonical_changed=False))
            return r'\noindent\begin{minipage}{\linewidth}'+''.join(parts)+r'\par\end{minipage}\par'
        label_width=binding.get('label_width_em',getattr(conv,'historical_option_label_width_em',1.8))
        if isinstance(label_width,bool)or not isinstance(label_width,(int,float))or not .8<=label_width<=3:
            raise ValueError('Invalid historical option label width')
        label_width=str(label_width)+'em'
        paired=binding.get('paired_fragments')
        arrow=binding.get('sequence_arrow_indent_em')
        if arrow is not None:
            if columns!=1 or numbered or not binding.get('multiline') or type(arrow)not in [int,float]or not 2<=arrow<=16:
                raise ValueError('Invalid source-bound option arrow sequence')
            converted=[]
            for value in values:
                if not isinstance(value,dict)or set(value)!={'html'}:raise ValueError('Arrow sequence requires exact rich options')
                pieces=re.split(r'<br\s*/?>',value['html'])
                if len(pieces)!=5 or any(BeautifulSoup(pieces[j],'html.parser').get_text().strip()!='↓'for j in [1,3]):
                    raise ValueError('Arrow sequence changed its three steps/two connectors')
                steps=[conv.value({'html':pieces[j]},'option')for j in [0,2,4]]
                connector=r'\par\nobreak\noindent\hspace*{'+str(arrow)+r'em}'+conv.text('↓')+r'\par\nobreak\noindent '
                converted.append(connector.join(steps))
            conv.features.append(dict(kind='historical_option_arrow_sequence',target=item['id'],arrow_indent_em=arrow,options=4,arrows=8,canonical_changed=False))
        widths=binding.get('column_widths')
        if widths and (len(widths)!=columns or any(not .1<=w<=.75 for w in widths) or not .9<=sum(widths)<=1):
            raise ValueError('Invalid bound asymmetric option grid')
        if binding.get('contiguous_strip'):
            if columns!=4 or not numbered:raise ValueError('Contiguous strip requires four source-numbered panels')
            from historical_nodes import image_at_width
            from PIL import Image
            import io
            images=[BeautifulSoup(v['html'],'html.parser').img for v in values]
            sizes=[Image.open(io.BytesIO(base64.b64decode(n['src'].split(',',1)[1]))).size for n in images]
            if len({s[1]for s in sizes})!=1:raise ValueError('Strip panels must share their original height')
            total=sum(s[0]for s in sizes)
            panels=[image_at_width(conv,n,s[0]/total,block=False)for n,s in zip(images,sizes)]
            conv.features.append(dict(kind='historical_contiguous_answer_strip',target=item['id'],panel_sizes=sizes,original_bytes_preserved=True))
            return r'\par\addvspace{8pt}\noindent\hbox{'+''.join(panels)+r'}\par\addvspace{8pt}'
        if paired:
            if columns!=2 or numbered or set(paired)!= {'gap_em'} or not .5<=paired['gap_em']<=4:
                raise ValueError('Paired fragments require a bound two-column textual grid')
            converted=[]
            for value in values:
                if not isinstance(value,str) or len(value.split('\u3000'))!=2 or not all(value.split('\u3000')):
                    raise ValueError('Paired fragments require two exact source fragments')
                left,right=value.split('\u3000')
                converted.append(r'\mbox{'+conv.value(left,'option')+r'\hspace{'+str(paired['gap_em'])+'em}'+conv.value(right,'option')+'}')
            conv.features.append({'kind':'historical_paired_fragments','target':item['id'],'gap_em':paired['gap_em'],'canonical_changed':False})
        for n,(value,tex)in enumerate(zip(values,converted),1):
            if numbered:
                soup=BeautifulSoup(value['html'],'html.parser')if isinstance(value,dict)else None
                if soup is None or len(soup.find_all('img'))!=1 or soup.get_text(strip=True):
                    raise ValueError('Source-numbered grid requires one image and no duplicate native text per option')
                node=soup.img;raw=base64.b64decode(node['src'].split(',',1)[1]);key=hashlib.sha256(raw).hexdigest()
                style=conv.embedded_image_styles[key]
                if style['role']!='illustration':raise ValueError('Image grid requires illustration role')
                # The source width is relative to a complete question. Within
                # the explicit cell the same image consumes its cell width.
                previous=conv.embedded_image_styles[key]
                panel_width=binding.get('panel_width_fraction',1)
                if not .65<=panel_width<=1:raise ValueError('Invalid source-bound panel scale')
                conv.embedded_image_styles[key]={**previous,'width_fraction':panel_width}
                try:tex=conv.node(node,'body')
                finally:conv.embedded_image_styles[key]=previous
            elif binding.get('multiline'):
                # Bound multiline options start beside their number. HTML's
                # outer paragraph container must not create an empty first or
                # last line; interior source paragraph boundaries remain.
                tex=re.sub(r'^(?:\s*\\Para\s*)+','',tex)
                tex=re.sub(r'(?:\s*\\Para\s*)+$','',tex)
                tex=tex.replace(r'\linebreak[2]',r'\par')
            # Equal pitches share one anchor system: the right column of a
            # two-column arrangement starts at the third four-column anchor.
            # Explicit source-bound asymmetric arrangements remain available.
            width=str(widths[(n-1)%columns]) if widths else {1:'1',2:'.5',3:'.33333333',4:'.25'}[columns]
            row_strut=r'\strut{}'
            cell=r'\begin{minipage}[t]{'+width+r'\linewidth}\vspace{0pt}'
            if numbered:cell+=tex
            elif columns==1 and arrow is None and not binding.get('multiline'):
                # One paragraph owns both the label and the continuation.
                # A separate text minipage erased the existing one-moji
                # continuation rule for every bound historical long option.
                tex=re.sub(r'^(?:\s*\\Para\s*)+','',tex)
                tex=re.sub(r'(?:\s*\\Para\s*)+$','',tex)
                cell+=(r'\leftskip=0pt\rightskip=0pt plus 1fil\parfillskip=0pt plus 1fil\relax'
                       r'\setlength\parindent{0pt}\hangindent=\dimexpr'+label_width+r'-\OptionContinuationPullback\relax\hangafter=1'
                       r'\noindent'+row_strut+r'\makebox['+label_width+r'][l]{{\ChoiceNumerals '+str(n)+r'}}'
                       +tex+r'\unskip\nobreak'+row_strut+r'\par')
            else:cell+=(r'\noindent\begin{minipage}[t]{'+label_width+r'}\vspace{0pt}'+row_strut+r'{\ChoiceNumerals '+str(n)
                        +r'}\end{minipage}\begin{minipage}[t]{\dimexpr\linewidth-'+label_width+r'\relax}\vspace{0pt}'
                        +row_strut+tex+r'\unskip\nobreak'+row_strut+r'\par\end{minipage}')
            cell+=r'\par\end{minipage}'
            parts.append(cell)
            gap=str(binding.get('row_gap_pt',row_gap_pt if row_gap_pt is not None else getattr(conv,'historical_option_row_gap_pt',0)))
            if n==4:parts.append(r'\par\nointerlineskip')
            else:parts.append(r'\par\nointerlineskip\vspace{'+gap+r'pt}\noindent 'if n%columns==0 else r'\hfill 'if widths else '%\n')
        grid=r'\par\noindent '+''.join(parts)+r'\par'
        def compact_braced_grid(reserved_em):
            # Measure the actual option glyphs, ruby and label gutter in the
            # active option face. Long choices still wrap at the available
            # measure with the existing one-moji continuation paragraph.
            if binding.get('multiline')or arrow is not None:raise ValueError('Compact closing brace requires single-paragraph choices')
            setup=[r'\begingroup\setlength\HistoricalBracedOptionsWidth{0pt}']
            for n,t in enumerate(converted,1):
                t=re.sub(r'^(?:\s*\\Para\s*)+','',t);t=re.sub(r'(?:\s*\\Para\s*)+$','',t)
                if r'\Para'in t or r'\par'in t:raise ValueError('Closing brace choice contains an internal paragraph')
                setup.append(r'\settowidth\HistoricalBracedOptionProbe{\makebox['+label_width+r'][l]{{\ChoiceNumerals '+str(n)+r'}}'+t+'}')
                setup.append(r'\ifdim\HistoricalBracedOptionProbe>\HistoricalBracedOptionsWidth\setlength\HistoricalBracedOptionsWidth{\HistoricalBracedOptionProbe}\fi')
            setup.append(r'\addtolength\HistoricalBracedOptionsWidth{.2em}')
            cap=r'\dimexpr\linewidth-'+str(reserved_em)+r'em\relax'
            setup.append(r'\ifdim\HistoricalBracedOptionsWidth>'+cap+r'\setlength\HistoricalBracedOptionsWidth{'+cap+r'}\fi')
            conv.features.append(dict(kind='historical_braced_intrinsic_width',target=item['id'],method='measured_longest_choice_capped_at_available_width',continuation='existing_one_moji',canonical_changed=False))
            return ''.join(setup)
        if 'braced_prefix'in binding and 'braced_suffix'in binding:
            braced_stem(item,binding)
            pre=binding['braced_prefix'];post=binding['braced_suffix']
            pw=pre['prefix_width_em'];sw=post['suffix_width_em']
            indent=pre.get('indent_em',0);gap=pre.get('brace_gap_em',0)
            paragraphs=BeautifulSoup(item['stem']['html'],'html.parser').find_all('p',recursive=False)
            prefix_node=paragraphs[-2]
            prefix=conv.value({'html':prefix_node.decode_contents()}if prefix_node.find()else pre['text'],'body')
            suffix_node=paragraphs[-1]
            suffix=conv.value({'html':suffix_node.decode_contents()}if suffix_node.find()else post['text'],'body')
            for side,b in [('prefix',pre),('suffix',post)]:
                conv.features.append(dict(kind='historical_braced_answer_'+side,target=item['id'],text=b['text'],stem_sha256=b['stem_sha256'],canonical_changed=False))
            return (compact_braced_grid(pw+sw+4+indent+gap)+r'\par\noindent'+(r'\hspace*{'+str(indent)+r'em}'if indent else'')
                +r'\begin{minipage}[c]{'+str(pw)+r'em}'+prefix+r'\end{minipage}'
                +r'\(\left\{\vcenter{\hbox{'+(r'\hspace{'+str(gap)+r'em}'if gap else'')
                +r'\begin{minipage}{\HistoricalBracedOptionsWidth}'
                +grid+r'\end{minipage}}}\right\}\)\hspace{.5em}'
                +r'\begin{minipage}[c]{'+str(sw)+r'em}'+suffix+r'\end{minipage}\par\endgroup')
        if 'braced_prefix'in binding:
            braced_stem(item,binding)
            b=binding['braced_prefix'];width=b['prefix_width_em']
            indent=b.get('indent_em',0);gap=b.get('brace_gap_em',0)
            # Preserve printed ruby in the source's shared phrase. Plain
            # phrases follow their unchanged path; the exact stem is bound.
            last=BeautifulSoup(item['stem']['html'],'html.parser').find_all('p',recursive=False)[-1]
            prefix=conv.value({'html':last.decode_contents()} if last.find() else b['text'],'body')
            conv.features.append(dict(kind='historical_braced_answer_prefix',target=item['id'],text=b['text'],stem_sha256=b['stem_sha256'],canonical_changed=False))
            return (r'\par\noindent'+(r'\hspace*{'+str(indent)+r'em}'if indent else'')+r'\begin{minipage}[c]{'+str(width)+r'em}'+prefix+r'\end{minipage}'
                +r'\(\left\{\vcenter{\hbox{'+(r'\hspace{'+str(gap)+r'em}'if gap else'')+r'\begin{minipage}{\dimexpr\linewidth-'+str(width+2+indent+gap)+r'em\relax}'
                +grid+r'\end{minipage}}}\right.\)\par')
        if 'braced_suffix'in binding:
            braced_stem(item,binding)
            b=binding['braced_suffix'];width=b['suffix_width_em']
            last=BeautifulSoup(item['stem']['html'],'html.parser').find_all('p',recursive=False)[-1]
            suffix=conv.value({'html':last.decode_contents()}if last.find()else b['text'],'body')
            conv.features.append(dict(kind='historical_braced_answer_suffix',target=item['id'],text=b['text'],stem_sha256=b['stem_sha256'],canonical_changed=False))
            return (compact_braced_grid(width+2)+r'\par\noindent\(\left.\vcenter{\hbox{\begin{minipage}{\HistoricalBracedOptionsWidth}'
                +grid+r'\end{minipage}}}\right\}\)\hspace{.5em}\begin{minipage}[c]{'+str(width)+r'em}'
                +suffix+r'\end{minipage}\par\endgroup')
        return grid
    if kind=='combination':
        keys=binding['keys'];width=binding['width_fraction'];parsed=[]
        if len(keys)not in {2,3,4} or len(set(keys))!=len(keys) or not .45<=width<=1:
            raise ValueError('Combination answers require two to four distinct bound columns')
        syntax=binding.get('cell_syntax','key_colon_value')
        if syntax not in {'key_colon_value','circled_key_space_value','key_fullwidth_value','key_dash_value'}:
            raise ValueError('Unknown combination cell syntax')
        value_width=binding.get('value_width_em',1.2)
        if isinstance(value_width,bool)or not isinstance(value_width,(int,float))or not 1<=value_width<=12:
            raise ValueError('Invalid combination value width')
        columns=binding.get('cell_columns',len(keys))
        if type(columns)is not int or (columns!=len(keys)and not(columns==2 and len(keys)==4)):
            raise ValueError('Combination grouping must be one complete row or two pairs')
        from historical_combination import parse
        parsed=parse(values,keys,syntax)
        # Converted options have already recorded every source ruby. These
        # exact cell fragments replace that rendering, rather than add text.
        cell_conv=copy.copy(conv);cell_conv.features=[]
        rows=[]
        block_gap=binding.get('block_gap_pt',0)
        if type(block_gap)not in [int,float]or not 0<=block_gap<=16:raise ValueError('Invalid combination block gap')
        for n,row in enumerate(parsed,1):
            cells=[]
            for m in row:
                body=cell_conv.value(m['value'],'option') if isinstance(m['value'],dict) else conv.text(m['value'])
                cells.append(conv.text(m['key'])+conv.text(m['separator'])+r'\makebox['+str(value_width)+r'em][l]{'+body+'}')
            if columns==len(keys):
                rows.append(' & '.join([r'{\ChoiceNumerals '+str(n)+'}']+cells)+r' \\')
            else:
                rows.append(' & '.join([r'\SetCell[r=2]{valign=t}{\ChoiceNumerals '+str(n)+'}']+cells[:2])+r' \\')
                rows.append(' & '.join(['']+cells[2:])+r' \\')
        conv.features.append({'kind':'historical_combination_columns','target':item['id'],'keys':keys,'width_fraction':width,'canonical_changed':False})
        row_count=1 if columns==len(keys)else 2
        padding=','.join('row{'+str(n*row_count)+r'}={belowsep='+str(block_gap)+'pt}'for n in range(1,4))if block_gap else''
        return (r'\par\noindent\begin{tblr}{width='+str(width)+r'\linewidth,colspec={Q[l,wd=1.5em]'+('X[l]'*columns)+r'},colsep=0pt,rowsep=0pt,cells={valign=t}'+(','+padding if padding else'')+'}'
                +'\n'.join(rows)+r'\end{tblr}\par')
    if kind=='shared_header_table':
        parsed=[];headers=None
        for value in values:
            soup=BeautifulSoup(value['html'],'html.parser');tables=soup.find_all('table')
            if len(tables)!=1 or tables[0].get('data-historical-option-table')not in {'culture-civilization','shared-two-column'}:
                raise ValueError('Shared historical table needs four canonical marked tables')
            rows=tables[0].find_all('tr');cells=[r.find_all(['th','td'],recursive=False)for r in rows]
            if len(rows)!=2 or any(len(c)!=2 for c in cells):raise ValueError('Invalid historical option table dimensions')
            head=[c.decode_contents()for c in cells[0]]
            if headers is None:headers=head
            if headers!=head:raise ValueError('Historical option headers differ')
            parsed.append([c.decode_contents()for c in cells[1]])
        cell=lambda html:conv.value({'html':html},'cell')
        if binding.get('header_tracking_em'):
            tracking=binding['header_tracking_em']
            if headers!=['文化','文明'] or not .3<=tracking<=1.2:raise ValueError('Unexpected tracked culture/civilization headers')
            head=lambda t:conv.text(t[0])+r'\hspace{'+str(tracking)+'em}'+conv.text(t[1])
            rows=[r' & '+head(headers[0])+' & '+head(headers[1])+r' \\']
        else:rows=[r' & '+cell(headers[0])+' & '+cell(headers[1])+r' \\']
        for n,row in enumerate(parsed,1):rows.append(str(n)+' & '+cell(row[0])+' & '+cell(row[1])+r' \\')
        conv.features.append({'kind':'historical_coalesced_option_header','canonical_header_count':4,'native_header_count':1,'text':headers})
        before=binding.get('before_pt',8);row_sep=binding.get('row_sep_pt',7)
        if not 0<=before<=24 or not 0<=row_sep<=12:raise ValueError('Invalid historical table clearance/padding')
        leading=binding.get('cell_baseline_pt',conv.table_baseline_pt)
        first_pad=binding.get('first_option_row_sep_pt',row_sep)
        if type(leading)not in [int,float]or not conv.table_body_pt<=leading<=24 or type(first_pad)not in [int,float]or not 0<=first_pad<=16:raise ValueError('Invalid table cell leading/first-option padding')
        align=binding.get('table_cell_alignment','left');separator=binding.get('table_inner_separator','solid');width=binding.get('width_fraction',1)
        if align not in ['left','center']or separator not in ['solid','dashed']or type(width)not in [int,float]or not .45<=width<=1:raise ValueError('Invalid source-bound shared-table style')
        col='l'if align=='left'else'c';measure=r'\linewidth'if width==1 else str(width)+r'\linewidth'
        vertical=r'vline{2-4},'if separator=='solid'else r'vline{2,4},vline{3}={dashed},'
        return (r'\par\vspace*{'+str(before)+r'pt}{\fontsize{'+str(conv.table_body_pt)+'}{'+str(leading)+r'}\selectfont\noindent\begin{tblr}{width='+measure+r',colspec={Q[c,wd=1.6em]X['+col+']X['+col+r']},'
                r'hline{2-6},hline{1}={2-3}{solid},'+vertical+r'vline{1}={2-5}{solid},'
                r'cells={valign=t},row{1}={halign=c},rowsep='+str(row_sep)+r'pt,row{2}={abovesep='+str(first_pad)+'pt,belowsep='+str(first_pad)+'pt}}'+'\n'.join(rows)+r'\end{tblr}\par}')
    parsed=[]
    for value in values:
        soup=BeautifulSoup(value['html'],'html.parser');fixed=soup.select('span[data-historical-fixed-column="true"]')
        if len(fixed)!=1 or fixed[0].get_text()!='a':raise ValueError('Chronology needs its shared third column')
        plain=soup.get_text();m=re.fullmatch(r'([a-d]) − ([a-d]) − a − ([a-d])',plain)
        if not m:raise ValueError('Invalid four-column chronology option')
        parsed.append([m[1],'−',m[2],'−','a','−',m[3]])
    rows=[r'\cline{6-6}']
    for n,row in enumerate(parsed,1):rows.append(str(n)+' & '+' & '.join(conv.text(c)for c in row)+r' \\')
    rows.append(r'\cline{6-6}')
    # Source chronology rows use the same baseline as the preceding a-d list.
    return r'\par\noindent{\renewcommand\arraystretch{1}\setlength\tabcolsep{7pt}\begin{tabular}{@{}lcccc|c|cc@{}}'+'\n'.join(rows)+r'\end{tabular}}\par'


def grammar_two_column_section_gaps(model):
    """Select a family gap from a complete declared grammar arrangement."""
    gap=model['style'].get('historical_typography',{}).get('grammar_two_column_section_gap_pt')
    if gap is None:return {}
    if model.get('exam',{}).get('generation')!='historical-1991-2009' or type(gap)not in [int,float]or not 12<=gap<=36:
        raise ValueError('Invalid Old two-column grammar section gap')
    result={}
    for section in model['document']['sections']:
        if model['layout']['sections'][section['id']]['task']!='grammar':continue
        items=section['items']
        if not items or any('stem'not in i or len(i.get('options',[]))!=4 for i in items):continue
        grids=[model['layout']['items'][i['id']].get('historical_options',{})for i in items]
        if any(b.get('kind')!='grid'or b.get('columns')!=2 or b.get('source_numbered')is not False for b in grids):continue
        for i,b in zip(items,grids):
            if digest(i['options'])!=b['options_sha256']:raise ValueError('Stale two-column grammar arrangement')
            source_binding(model['unit'],b['evidence'])
            result[i['id']]=dict(section=section['id'],question_gap_pt=gap,questions=len(items),columns=2)
    return result
