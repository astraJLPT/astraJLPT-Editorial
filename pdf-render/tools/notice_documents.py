"""Bind one complete information document across unchanged adjacent contexts."""
from bs4 import BeautifulSoup, Tag
from model import Projection, digest


def collect(model):
    groups={}
    style=model['style']
    for section in model['document']['sections']:
        meta=model['layout']['sections'][section['id']]
        binding=meta.get('notice_document')
        if binding is None:continue
        if set(binding)!={'members','unwrap_outer_divs','evidence'} or not isinstance(binding['unwrap_outer_divs'],bool) or not binding['evidence']:
            raise ValueError('Notice document requires exact members, explicit wrapper handling and evidence')
        if meta['task']!='information_retrieval':
            raise ValueError('A notice document requires an information-retrieval section')
        items=[i for i in section['items'] if 'content' in i]
        members=binding['members']
        if not 2<=len(items)<=6 or len(items)!=len(members) or [i['id'] for i in items]!=[b.get('id') for b in members]:
            raise ValueError('Notice document must bind every context once in original order')
        positions=[section['items'].index(i) for i in items]
        if positions!=list(range(positions[0],positions[0]+len(items))):
            raise ValueError('Notice document members must be adjacent')
        lead=items[0]['id'];lead_style=style.get('block_styles',{}).get(lead)
        if not lead_style or lead_style.get('content_sha256')!=digest(items[0]['content']):
            raise ValueError('Notice document requires a hash-bound leading notice style')
        if set(lead_style)&{'page_frame','page_segments','content_selector'}:
            raise ValueError('Grouped notice uses the complete combined document')
        fragments=[];tables={};table_offset=0
        for item,bound in zip(items,members):
            iid=item['id'];value=item['content']
            if set(bound)!={'id','content_sha256'} or digest(value)!=bound['content_sha256']:
                raise ValueError('Stale notice document member')
            if item.get('type')=='example' or not isinstance(value,dict) or set(value)!={'html'}:
                raise ValueError('Notice document requires complete rich non-example contexts')
            if model['directions'][iid]['render_value']!='horizontal-tb':
                raise ValueError('Notice document requires horizontal member directions')
            if set(model['layout']['items'][iid])-{'writing_mode'}:
                raise ValueError('Notice document conflicts with another item role')
            for name in ['inline_presentations','inline_cloze_boxes','section_styles','content_frames',
                         'email_headers','underline_references','passage_boundaries','embedded_image_styles']:
                if iid in style.get(name,{}):
                    raise ValueError('Notice document conflicts with an independent content presentation')
            if iid!=lead and iid in style.get('block_styles',{}):
                raise ValueError('Notice document has a second independent notice style')
            # Exact item word groups and numeral exceptions need their original
            # per-field emitter; never silently bypass them in a grouped document.
            if any(f.get('source_plain_text') and f['owner']==iid for f in model.get('field_manifest',[])):
                raise ValueError('Grouped notice cannot reinterpret source-plain line breaks')
            if any(k==iid or k.startswith(iid+'/') for k in style.get('numeral_exceptions',{})):
                raise ValueError('Grouped notice conflicts with a member numeral exception')
            soup=BeautifulSoup(value['html'],'html.parser')
            count=len(soup.find_all('table'))
            local=style.get('table_styles',{}).get(iid,{})
            if any(not str(k).isdigit() or int(k)>=count for k in local):
                raise ValueError('Unknown grouped notice member table index')
            for index,spec in local.items():tables[str(table_offset+int(index))]=spec
            table_offset+=count
            if binding['unwrap_outer_divs']:
                for node in list(soup.children):
                    if isinstance(node,Tag) and node.name=='div':node.unwrap()
            fragments.append(str(soup))
        original={'html':'\n'.join(i['content']['html'] for i in items)}
        value={'html':'\n'.join(fragments)}
        before,after=Projection(original),Projection(value)
        compact=lambda text:text.replace('\r','').replace('\n','')
        if compact(before.text)!=compact(after.text) or [(r['base'],r['reading']) for r in before.ruby]!=[(r['base'],r['reading']) for r in after.ruby]:
            raise ValueError('Notice grouping changed characters or frozen ruby')
        groups[section['id']]={'items':items,'value':value,'style':lead_style,'table_styles':tables,'binding':binding}
    return groups
