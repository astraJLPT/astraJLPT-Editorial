"""Explicit Old dialogue/prose picture examples with bound choices and answer strips."""
import hashlib
from bs4 import BeautifulSoup,Tag
from model import Projection,digest
from presentation import source_binding
from dialogue import candidates,render as dialogue_tex
from historical_layout import options_tex

def parts(value):
    if not isinstance(value,dict)or set(value)!={'html'}:raise ValueError('Picture example needs complete rich content')
    soup=BeautifulSoup(value['html'],'html.parser')
    nodes=[n for n in soup.children if isinstance(n,Tag)or str(n).strip()]
    if len(nodes)!=7 or [n.name for n in nodes]!=['p']*6+['table']:
        raise ValueError('Picture example requires label,three turns,question,answer label and strip')
    plain=lambda n:Projection({'html':n.decode_contents()}).text.strip()
    if plain(nodes[0])!='（れい）'or not plain(nodes[4]).startswith('【しつもん】 ')or plain(nodes[5])!='（かいとうようし）':
        raise ValueError('Changed picture-example labels')
    dialogue={'html':''.join(str(n)for n in nodes[1:4])}
    turns=[dict(line=n,speaker=s)for n,s in enumerate(['A','B','A'])]
    if candidates(dialogue)!=turns:raise ValueError('Picture example must preserve all three exact speaker turns')
    rows=nodes[6].find_all('tr');cells=rows[0].find_all('td',recursive=False)if len(rows)==1 else[]
    if len(cells)!=5 or [plain(c)for c in cells]!=['（れい）','●','②','③','④']:
        raise ValueError('Picture example requires its original choice1 answer strip')
    return nodes,dialogue,turns,cells

def validate(item,binding,unit):
    prose=binding.get('kind')=='prose'
    if binding.get('kind')not in [None,'prose']:raise ValueError('Unknown picture-example kind')
    key=item.get('key')
    if (item.get('type')!='example'or type(key)is not int or key not in ([1,2,3,4]if prose else[1]) or len(item.get('options',[]))!=4
            or digest(item['content'])!=binding['content_sha256']
            or digest(item['options'])!=binding['options_sha256']):
        raise ValueError('Stale picture-example content/options/key')
    if prose:prose_parts(item['content'],key)
    else:parts(item['content'])
    for value in item['options']:
        if not isinstance(value,dict)or set(value)!={'html'}:raise ValueError('Picture example needs four image-only choices')
        soup=BeautifulSoup(value['html'],'html.parser')
        if len(soup.find_all('img'))!=1 or soup.get_text(strip=True):raise ValueError('Picture example choice is not one image')
    for key in ['dialogue_indent_em','example_label_width_em']:
        if key in binding and(type(binding[key])not in [int,float]or not 3<=binding[key]<=9 or prose):raise ValueError('Invalid picture-example dialogue geometry')
    if 'image_grid'in binding:
        grid=binding['image_grid']
        if not isinstance(grid,dict)or set(grid)-{'panel_label_position','panel_grid_width_fraction','panel_left_indent_em','panel_width_fraction','panel_label_inset_em','panel_before_pt','panel_label_gap_pt'}:raise ValueError('Invalid picture-example image geometry')
    if 'prose_geometry'in binding:
        g=binding['prose_geometry']
        if(not prose or not isinstance(g,dict)or set(g)-{'body_inset_em','first_line_indent_em','query_left_inset_em'}or not {'body_inset_em','first_line_indent_em'}<=set(g)
           or any(type(g[k])not in [int,float]for k in g)or not 2<=g['body_inset_em']<=8 or not 0<=g['first_line_indent_em']<=2 or not 0<=g.get('query_left_inset_em',1)<=4):
            raise ValueError('Invalid source-bound picture-example prose geometry')
    source_binding(unit,binding['evidence'])

def prose_parts(value,key):
    if not isinstance(value,dict)or set(value)!={'html'}:raise ValueError('Prose example needs complete rich content')
    soup=BeautifulSoup(value['html'],'html.parser')
    nodes=[n for n in soup.children if isinstance(n,Tag)or str(n).strip()]
    if len(nodes)!=5 or [n.name for n in nodes]!=['p']*4+['table']:
        raise ValueError('Prose example requires label,prose,question,answer label and strip')
    plain=lambda n:Projection({'html':n.decode_contents()}).text.strip()
    if (plain(nodes[0])!='（れい）'or not plain(nodes[1])or nodes[1].find(['img','table'])
            or not plain(nodes[2]).startswith('【しつもん】 ')or plain(nodes[3])!='（かいとうようし）'):
        raise ValueError('Changed prose picture-example structure')
    rows=nodes[4].find_all('tr');cells=rows[0].find_all('td',recursive=False)if len(rows)==1 else[]
    expected=['（れい）']+['●'if n==key else'①②③④'[n-1]for n in range(1,5)]
    if len(cells)!=5 or [plain(c)for c in cells]!=expected:
        raise ValueError('Prose example answer strip differs from its key')
    return nodes,cells

def render_prose(conv,item,binding,value,options,style=None):
    nodes,cells=prose_parts(value,item['key'])
    label=r'\HistoricalExampleLabel{'+conv.value({'html':nodes[0].decode_contents()},'option')+'}'
    prose=conv.value({'html':nodes[1].decode_contents()},'example')
    question=nodes[2].decode_contents();prefix='【しつもん】 '
    if not question.startswith(prefix):raise ValueError('Prose-example question needs its literal leading label')
    q=conv.value({'html':question[len(prefix):]},'example')
    grid=options_tex(conv,{'id':item['id'],'options':options},dict(kind='grid',columns=4,source_numbered=False,image_panels=True,**{'panel_width_fraction':1,**binding.get('image_grid',{})}),[None]*4)
    answer=r'\AnswerLine{'+conv.value({'html':nodes[3].decode_contents()},'option')+'}{'+' & '.join(conv.answer_cell(c.decode_contents())for c in cells)+'}'
    conv.example_options_embedded=False
    conv.features.append(dict(kind='historical_picture_example',variant='prose',target=item['id'],picture_choices=4,answer_key=item['key'],content_sha256=binding['content_sha256'],options_sha256=binding['options_sha256'],canonical_changed=False))
    if binding.get('prose_geometry'):
        g=binding['prose_geometry'];inset=g['body_inset_em'];opening=inset+g['first_line_indent_em']
        from historical_layout import question_label
        query_style=style
        if 'query_left_inset_em'in g:
            typography=(style or{}).get('historical_typography',{})
            query_style={**(style or{}),'historical_typography':{**typography,'shitsumon_label':{**typography.get('shitsumon_label',dict(width_em=6,font='body')),'left_inset_em':g['query_left_inset_em']}}}
        _,setup=question_label('bracketed_shitsumon','1',query_style)
        query='{'+setup+r'\QuestionStem{1}{'+q+r'}}\par\nobreak\nointerlineskip\vspace{4pt}'
        conv.features.append(dict(kind='historical_picture_example_prose_geometry',target=item['id'],**g,canonical_changed=False))
        return(r'\noindent\hangindent='+str(inset)+r'em\hangafter=1\makebox['+str(opening)+r'em][l]{'+label+'}'+prose+r'\par\vspace{8pt}'+query+grid+answer)
    return (r'\noindent\hangindent=3.5em\hangafter=1\makebox[3.5em][l]{'+label+'}'+prose+r'\par\vspace{8pt}\noindent'
            r'\hangindent=7em\hangafter=1\makebox[7em][l]{{\HistoricalQuestionJapanese 【しつもん】}}'+q+r'\par\nobreak\vspace{4pt}'+grid+answer)

def render(conv,item,binding,unit,value,options,meta,style=None):
    if not getattr(conv,'source_target_markers',False):raise ValueError('Picture example outside Old JLPT')
    if any(meta.get(k)for k in ['example_layout','historical_example_options','historical_example_target_row','historical_reading_dialogue','dialogue'])or meta.get('example_variant','ordinary')!='ordinary':
        raise ValueError('Conflicting picture-example layout')
    validate(item,binding,unit)
    if (Projection(value).text,Projection(value).ruby)!=(Projection(item['content']).text,Projection(item['content']).ruby):
        raise ValueError('Picture-example presentation changed source text/ruby')
    if digest(options)!=binding['options_sha256']:raise ValueError('Picture choices changed during presentation')
    if binding.get('kind')=='prose':return render_prose(conv,item,binding,value,options,style)
    nodes,dialogue,turns,cells=parts(value)
    structure=dict(projection_sha256=hashlib.sha256(Projection(dialogue).text.encode()).hexdigest(),turns=turns,state='observed',speaker_align='left')
    tex=dialogue_tex(conv,dialogue,structure)
    label=r'\HistoricalExampleLabel{'+conv.value({'html':nodes[0].decode_contents()},'option')+'}'
    tex=tex.replace(r'\DialogueTurn{',r'\leavevmode\llap{\makebox['+str(binding.get('example_label_width_em',5))+r'em][l]{'+label+r'}}\DialogueTurn{',1)
    question=nodes[4].decode_contents();prefix='【しつもん】 '
    if not question.startswith(prefix):raise ValueError('Picture-example question needs its literal leading label')
    q=conv.value({'html':question[len(prefix):]},'example')
    grid=options_tex(conv,{'id':item['id'],'options':options},dict(kind='grid',columns=4,source_numbered=False,image_panels=True,**{'panel_width_fraction':1,**binding.get('image_grid',{})}),[None]*4)
    answer=r'\AnswerLine{'+conv.value({'html':nodes[5].decode_contents()},'option')+'}{'+' & '.join(conv.answer_cell(c.decode_contents())for c in cells)+'}'
    conv.example_options_embedded=False
    conv.features.append(dict(kind='historical_picture_example',target=item['id'],turns=3,picture_choices=4,answer_key=1,content_sha256=binding['content_sha256'],options_sha256=binding['options_sha256'],canonical_changed=False))
    if (style or{}).get('historical_typography',{}).get('shitsumon_label'):
        from historical_layout import question_label
        _,setup=question_label('bracketed_shitsumon','1',style)
        query='{'+setup+r'\QuestionStem{1}{'+q+r'}}\par\nobreak\nointerlineskip\vspace{4pt}'
    else:query=r'\hangindent=7em\hangafter=1\makebox[7em][l]{{\HistoricalQuestionJapanese 【しつもん】}}'+q+r'\par\nobreak\vspace{4pt}'
    return (r'\HistoricalReadingDialogue{'+str(binding.get('dialogue_indent_em',5))+'}{'+tex+r'}\par\vspace{8pt}\noindent'+query+grid+answer)
