"""Source-bound label/notice arrangements inside ordinary Old examples."""
import re
from bs4 import BeautifulSoup
from model import Projection, digest
from presentation import source_binding


METRICS={'label_width_em':(2,6),'padding_x_pt':(4,24),'padding_y_pt':(4,30),
         'rule_pt':(.3,1.5),'question_indent_em':(0,4)}


def collect(model):
    items={i['id']:i for s in model['document']['sections'] for i in s['items']}
    result={}
    for iid,meta in model['layout']['items'].items():
        binding=meta.get('historical_example_frame')
        if binding is None:continue
        required={'content_sha256','options_sha256','evidence','kind','question_prefix',*METRICS}
        if set(binding)!=required or binding['kind']!='label_beside_notice':raise ValueError('Invalid historical example frame fields')
        item=items[iid]
        if item.get('type')!='example' or meta.get('example_variant','ordinary')!='ordinary':raise ValueError('Example frame requires ordinary example')
        if digest(item['content'])!=binding['content_sha256'] or digest(item.get('options'))!=binding['options_sha256']:raise ValueError('Stale historical example frame')
        source_binding(model['unit'],binding['evidence'])
        for key,(low,high) in METRICS.items():
            if type(binding[key])not in [int,float] or not low<=binding[key]<=high:raise ValueError('Invalid example frame metric: '+key)
        prefix=binding['question_prefix']
        if not isinstance(prefix,str) or not 1<=len(prefix)<=20:raise ValueError('Invalid example frame question prefix')
        soup=BeautifulSoup(item['content']['html'],'html.parser')
        frames=soup.select('div[data-historical-framed-document="single"]')
        if len(frames)!=1 or frames[0].find(['table','img']):raise ValueError('Example arrangement requires one complete text notice')
        label=frames[0].find_previous_sibling();question=frames[0].find_next_sibling()
        if label is None or not re.fullmatch(r'[（(](?:例|れい)[）)]',Projection({'html':str(label)}).text.strip()):raise ValueError('Example notice has no adjacent label')
        if question is None or not Projection({'html':str(question)}).text.strip().startswith(prefix):raise ValueError('Example notice has no adjacent question')
        if sum(Projection({'html':str(p)}).text.strip().startswith(prefix)for p in soup.find_all('p'))!=1:raise ValueError('Example question prefix is ambiguous')
        result[iid]=binding
    return result


def render(conv,label,node,binding):
    if node.get('data-historical-framed-document')!='single' or node.find(['table','img']):raise ValueError('Invalid bound example notice')
    body=''.join(conv.node(c,'example')for c in node.children)
    args=[str(binding[k])+unit for k,unit in [('label_width_em','em'),('padding_x_pt','pt'),('padding_y_pt','pt'),('rule_pt','pt')]]
    conv.features.append(dict(kind='historical_example_label_beside_frame',target=conv.historical_example_target_id,
        content_sha256=binding['content_sha256'],metrics={k:binding[k]for k in METRICS},canonical_changed=False))
    return r'\HistoricalFramedExample'+''.join('{'+a+'}'for a in [*args,label,body])
