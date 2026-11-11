"""Explicit Old answer labels tied to a preceding source context."""
import re
from bs4 import BeautifulSoup
from model import Projection,digest
from presentation import source_binding


def circled_instruction(instruction):
    forms=[
        ('①②③','bracketed_shitsumon_numbered','【しつもん1】',r'【しつもん1】\s*①～③の\s*〔[ 　]+〕には\s*どんな\s*ことばを\s*入れたら\s*いいですか。'),
        ('①②③④','bracketed_shitsumon','【しつもん】',r'【しつもん】\s*①～④の\s*〔[ 　]+〕には、\s*なにを\s*いれますか。')]
    for labels,kind,prefix,pattern in forms:
        if re.fullmatch(pattern,instruction):return labels,kind,prefix
    raise ValueError('Changed shared circled-answer instruction')


def label_parts(item,binding):
    """Keep the existing kana form exact; circled rows may own one prompt."""
    label=binding['label']
    if binding.get('label_style')!='circled':
        if binding.get('label_style')not in [None,'bare_kana'] or binding.get('kana_font','gothic')not in ['gothic','body'] or 'shared_instruction'in binding or not re.fullmatch('[アイウエ]',label):
            raise ValueError('Invalid historical kana answer label')
        marker='（'+label+'）'
        if item.get('stem')!=marker:raise ValueError('Changed historical kana label stem')
        return marker,None
    if 'kana_font'in binding:raise ValueError('Kana font on a circled answer label')
    if label not in ['①','②','③','④']:
        raise ValueError('Invalid historical circled answer label')
    value=item.get('stem')
    if binding.get('shared_instruction'):
        if label!='①' or binding['shared_instruction']is not True or not isinstance(value,dict)or set(value)!={'html'}:
            raise ValueError('Only first circled row can own the shared instruction')
        soup=BeautifulSoup(value['html'],'html.parser');roots=[n for n in soup.contents if str(n).strip()]
        if (len(roots)!=2 or any(getattr(n,'name',None)!='p'or n.attrs or n.find() for n in roots)
                or roots[1].get_text()!=label):
            raise ValueError('Circled prompt requires two exact plain canonical paragraphs')
        instruction=roots[0].get_text()
        circled_instruction(instruction)
        return label,instruction
    if 'shared_instruction'in binding or value!=label:
        raise ValueError('Changed historical circled label stem')
    return label,None


def collect(model):
    bindings={qid:m['historical_label_answer']for qid,m in model['layout']['items'].items()if 'historical_label_answer'in m}
    if not bindings:return {}
    if model.get('exam',{}).get('generation')!='historical-1991-2009':
        raise ValueError('Historical label answer outside Old JLPT')
    places={i['id']:(s,n,i)for s in model['document']['sections']for n,i in enumerate(s['items'])}
    for qid,b in bindings.items():
        section,n,q=places[qid];meta=model['layout']['items'][qid];grid=meta.get('historical_options',{})
        label=b['label'];marker,instruction=label_parts(q,b)
        if (digest(q['stem'])!=b['stem_sha256']
            or digest(q['options'])!=b['options_sha256']or len(q['options'])!=4
            or meta.get('printed_label',{}).get('value')!=label):
            raise ValueError('Stale or invalid historical kana answer label')
        if (grid.get('kind')!='grid'or grid.get('columns')not in [1,2,4]or grid.get('source_numbered')is not False
            or grid.get('options_sha256')!=b['options_sha256']
            or any(k in meta for k in ['historical_question_label','historical_target_row','historical_answer_list','dialogue'])):
            raise ValueError('Historical label answer requires an unambiguous bound grid')
        cid=b['context_id']
        if cid not in places:raise ValueError('Missing historical label-answer context')
        context_section,index,context=places[cid]
        context_marker='〔'+label+'〕'if b.get('label_style')=='circled'else marker
        if (context_section is not section or index>=n or context.get('type')!='passage'
            or digest(context['content'])!=b['context_sha256']
            or re.sub(r'\s+','',Projection(context['content']).text).count(context_marker)!=1):
            raise ValueError('Stale or ambiguous historical kana context')
        if b.get('label_style')=='circled':
            start=n-'①②③④'.index(label)
            if start<0:raise ValueError('Incomplete circled answer group')
            first=section['items'][start];first_binding=bindings.get(first['id'],{})
            if first_binding.get('label')!='①' or not first_binding.get('shared_instruction'):
                raise ValueError('Circled group must begin with its shared instruction')
            _,first_instruction=label_parts(first,first_binding)
            labels,_,_=circled_instruction(first_instruction)
            group=section['items'][start:start+len(labels)]
            if label not in labels or len(group)!=len(labels):raise ValueError('Incomplete circled answer group')
            for j,item in enumerate(group):
                other=bindings.get(item['id'],{})
                if (other.get('label')!=labels[j] or other.get('label_style')!='circled'
                    or other.get('context_id')!=cid or bool(other.get('shared_instruction'))!=(j==0)):
                    raise ValueError('Circled rows must share one preceding context and one instruction')
        source_binding(model['unit'],b['evidence'])
    return bindings


def render(conv,item,binding,option_tex,gap):
    marker,instruction=label_parts(item,binding)
    if binding.get('label_style')=='bare_kana':marker=binding['label']
    heading=''
    if instruction:
        from historical_layout import question_label
        _,kind,prefix=circled_instruction(instruction)
        _,setup=question_label(kind,'1')
        heading=(r'{\par\addvspace{'+str(gap)+r'pt}'+setup+r'\QuestionStem{1}{'
            +conv.value(instruction[len(prefix):].lstrip(),'body')+r'}\par}\nobreak')
        conv.features.append(dict(kind='historical_shared_question_instruction',target=item['id'],text=instruction,canonical_changed=False))
    conv.features.append(dict(kind='historical_label_answer',target=item['id'],context_id=binding['context_id'],
        label=marker,stem_sha256=digest(item['stem']),options_sha256=digest(item['options']),canonical_changed=False))
    font=r'\rmfamily\mcfamily\mdseries 'if binding.get('label_style')=='circled'or binding.get('kana_font')=='body'else r'\sffamily\gtfamily\mdseries '
    return (heading+r'{\par\addvspace{'+str(gap)+r'pt}\noindent\begin{minipage}{\linewidth}\setlength\parindent{0pt}'
        +r'\hypertarget{'+item['id']+r'}{}\label{'+item['id']+'}'
        +r'\noindent\begin{minipage}[t]{2.8em}\vspace{0pt}\strut{}{'+font+marker+r'}\end{minipage}'
        +r'\begin{minipage}[t]{\dimexpr\linewidth-2.8em\relax}\vspace{0pt}'+option_tex
        +r'\end{minipage}\par\end{minipage}\par}')
