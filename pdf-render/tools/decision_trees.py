"""Source-bound native geometry for an existing nested binary decision list."""
import copy,re
from bs4 import BeautifulSoup,Tag,NavigableString
from model import Projection,digest


def plain(nodes):
    return Projection({'html':''.join(map(str,nodes))}).text.strip()


def collect(root):
    """Read a left-leaf/right-continuation chain without inventing outcomes."""
    levels=[];outcomes=[]
    def visit(ul,prompt=None):
        children=[n for n in ul.children if not isinstance(n,NavigableString)or n.strip()]
        if len(children)!=2 or any(not isinstance(n,Tag)or n.name!='li'for n in children):
            raise ValueError('Decision level requires exactly two existing list choices')
        labels=[];next_level=None
        for index,li in enumerate(children):
            nodes=[copy.deepcopy(n)for n in li.children if not isinstance(n,NavigableString)or n.strip()]
            nested=[n for n in nodes if isinstance(n,Tag)and (n.name=='ul'or n.find('ul'))]
            if nested:
                if index!=1 or len(nested)!=1 or nested[0]is not nodes[-1]or len(levels)>=4:
                    raise ValueError('Only the right branch may continue into one nested decision')
                container=nodes.pop();following=container if container.name=='ul'else container.find('ul',recursive=False)
                if following is None or (container.name!='ul'and container.name!='div'):
                    raise ValueError('Decision prompt must directly contain its list')
                prompt_nodes=[] if container.name=='ul'else [n for n in container.children if n is not following]
                if any(isinstance(n,Tag)and n.find(['ul','li','div','table'])for n in prompt_nodes):
                    raise ValueError('Unsupported nested decision prompt')
                next_level=(following,prompt_nodes)
            else:
                if len(nodes)<2 or not isinstance(nodes[-1],Tag)or nodes[-1].name!='strong':
                    raise ValueError('Decision leaf requires one terminal strong outcome')
                outcome=nodes.pop()
                if outcome.find(['ul','li','div','table','p','br']):raise ValueError('Outcome must be inline')
                if not isinstance(nodes[-1],NavigableString)or not re.search(r'→\s*$',str(nodes[-1])):
                    raise ValueError('Decision leaf requires its literal terminal arrow')
                nodes[-1]=NavigableString(re.sub(r'\s*→\s*$','',str(nodes[-1])))
                outcomes.append(list(outcome.children))
            if not plain(nodes)or '\n'in plain(nodes)or '→'in plain(nodes):
                raise ValueError('Decision choice must be one exact inline label')
            labels.append(nodes)
        levels.append({'labels':labels,'prompt':prompt or []})
        if next_level:visit(*next_level)
    visit(root)
    if not 2<=len(levels)<=5 or len(outcomes)!=len(levels)+1:
        raise ValueError('Decision chain must terminate in one more outcome than levels')
    return levels,outcomes


def validate(root,binding):
    if set(binding)-{'content_sha256','evidence','list_sha256','levels','outcomes','body_pt','baseline_pt','level_heights_pt','level_gap_pt','outcome_gap_pt','outcome_height_pt','inset_fraction','before_pt','after_pt'}:
        raise ValueError('Unknown decision-tree property')
    if digest({'html':str(root)})!=binding['list_sha256']:
        raise ValueError('Stale decision-list content')
    levels,outcomes=collect(root)
    expected=[{'labels':[plain(n)for n in row['labels']],'prompt':plain(row['prompt'])}for row in levels]
    if expected!=binding['levels']or [plain(n)for n in outcomes]!=binding['outcomes']:
        raise ValueError('Decision branches or outcome associations changed')
    heights=binding['level_heights_pt']
    if len(heights)!=len(levels)or any(isinstance(x,bool)or not isinstance(x,(int,float))or not 18<=x<=100 for x in heights):
        raise ValueError('Invalid decision level heights')
    limits={'body_pt':(8,14),'baseline_pt':(10,22),'level_gap_pt':(8,40),'outcome_gap_pt':(12,40),'outcome_height_pt':(18,40),'inset_fraction':(.08,.2),'before_pt':(0,20),'after_pt':(0,20)}
    for key,(lo,hi)in limits.items():
        x=binding[key]
        if isinstance(x,bool)or not isinstance(x,(int,float))or not lo<=x<=hi:raise ValueError('Invalid decision geometry: '+key)
    if binding['inset_fraction']*(len(levels)-1)>.65:raise ValueError('Decision levels leave insufficient text width')
    if any(not re.match(r'^[ab][ \u3000]',plain(label))for row in levels for label in row['labels']):
        raise ValueError('Decision connector labels require explicit a/b choices')
    return levels,outcomes


def prepare(value,binding,original=None):
    if digest(value if original is None else original)!=binding['content_sha256']or not isinstance(value,dict):
        raise ValueError('Stale decision-tree field')
    soup=BeautifulSoup(value['html'],'html.parser')
    roots=[n for n in soup.find_all('ul')if not n.find_parent('ul')]
    matches=[n for n in roots if digest({'html':str(n)})==binding['list_sha256']]
    if len(matches)!=1:raise ValueError('Decision tree must select one exact outer list')
    validate(matches[0],binding);matches[0]['data-native-decision-tree']='binary_chain'
    result={'html':str(soup)}
    if Projection(value).text!=Projection(result).text or Projection(value).ruby!=Projection(result).ruby:
        raise ValueError('Decision preparation changed text or ruby')
    return result


def render(conv,node,binding):
    source=copy.deepcopy(node);source.attrs.pop('data-native-decision-tree',None)
    levels,outcomes=validate(source,binding)
    def tex(nodes):return ''.join(conv.node(n,'cell')for n in nodes)
    inset=binding['inset_fraction'];heights=binding['level_heights_pt'];gap=binding['level_gap_pt']
    starts=[sum(heights[:j])+gap*j for j in range(len(levels))]
    end=starts[-1]+heights[-1];terminal_y=end+binding['outcome_gap_pt']+binding['outcome_height_pt']/2
    leaf_x=[.13+inset*j for j in range(len(levels))]+[1-inset/2-.12]
    out=[r'\begin{tikzpicture}[x=\linewidth,y=-1pt]']
    for j,(row,y,height)in enumerate(zip(levels,starts,heights)):
        left=inset*j;width=1-left;prompt=bool(row['prompt']);middle=y+height/2+(5 if prompt else 0)
        out.append(r'\draw[black!65,line width=.45pt] ('+str(left)+','+str(y)+') rectangle (1,'+str(y+height)+');')
        if prompt:out.append(r'\node[inner sep=0pt,align=center] at ('+str(left+width/2)+','+str(y+9)+') {'+tex(row['prompt'])+'};')
        for c,label in enumerate(row['labels']):
            out.append(r'\node[inner sep=0pt,align=left,text width=\dimexpr '+str(width/2)+r'\linewidth-12pt\relax] at ('+str(left+width*(.25+.5*c))+','+str(middle)+') {'+tex(label)+'};')
        for c in range(2):
            terminal=(c==0 or j==len(levels)-1);x=leaf_x[j if c==0 else -1]if terminal else left+width*.6
            bottom=terminal_y-binding['outcome_height_pt']/2 if terminal else starts[j+1]
            style='solid'if c==0 else 'dash pattern=on 1.3pt off 1.3pt'
            out.append(r'\draw[->,black!65,line width=.5pt,'+style+'] ('+str(x)+','+str(y+height)+') -- ('+str(x)+','+str(bottom)+');')
            out.append(r'\node[anchor=east,inner sep=2pt] at ('+str(x)+','+str(y+height+6)+') {'+'ab'[c]+'};')
    for x,label in zip(leaf_x,outcomes):
        out.append(r'\node[draw=black!65,line width=.45pt,inner sep=3pt,minimum height='+str(binding['outcome_height_pt'])+r'pt,align=center] at ('+str(x)+','+str(terminal_y)+') {'+tex(label)+'};')
    out.append(r'\end{tikzpicture}')
    conv.features.append({'kind':'native_decision_tree','levels':binding['levels'],'outcomes':binding['outcomes'],'native_terminal_arrows':len(outcomes),'native_continuation_arrows':len(levels)-1,'literal_arrows_consumed':len(outcomes),'layout_branch_labels':2*len(levels)})
    return (r'\par\nobreak\vspace{'+str(binding['before_pt'])+r'pt}{\fontsize{'+str(binding['body_pt'])+'}{'+str(binding['baseline_pt'])+r'}\selectfont\noindent '+''.join(out)+r'\par}\vspace{'+str(binding['after_pt'])+r'pt}')
