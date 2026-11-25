"""Authored native continuation at complete rows of a single notice table."""
import copy
from bs4 import BeautifulSoup, Tag
from model import Projection, digest
from notice_layout import notice_nodes, meaningful


def render_table_pages(conv,value,style,level_root,render):
    soup=BeautifulSoup(value['html'],'html.parser')
    tables=soup.find_all('table')
    if len(tables)!=1:raise ValueError('Row continuation requires one complete table')
    nodes=meaningful(notice_nodes(value,style))
    direct=[(n,x)for n,x in enumerate(nodes) if isinstance(x,Tag) and x.name=='table']
    if len(direct)!=1:raise ValueError('Row continuation requires a complete top-level table')
    position,table=direct[0];prefix=nodes[:position];suffix=nodes[position+1:]
    rows=table.find_all('tr')
    breaks=style['table_row_breaks']
    if breaks!=sorted(set(breaks)) or not all(type(n)is int and 0<n<len(rows) for n in breaks):
        raise ValueError('Invalid row continuation boundaries')
    for number,row in enumerate(rows):
        for cell in row.find_all(['td','th'],recursive=False):
            span=int(cell.get('rowspan',1))
            if span<1 or number+span>len(rows):raise ValueError('Invalid spanning cell')
            if any(number<boundary<number+span for boundary in breaks):
                raise ValueError('Row continuation cannot split spanning cells')
    index=conv.table_index;saved=conv.table_styles
    presentation=copy.deepcopy(saved.get(str(index),{}))
    supported={'column_weights','column_alignments','header_align','row_sep_pt','column_sep_pt','caption_style','body_pt','baseline_pt','width_fraction','vertical_align','cell_styles','before_pt','after_pt','top_gap_pt','rules'}
    if set(presentation)-supported:raise ValueError('Complex table selectors need explicit continuation support')
    if set(presentation.get('rules',{}))-{'default'}:
        raise ValueError('Indexed table rules need explicit continuation support')
    if set(style)&{'page_segments','page_frame','inset_panels','colon_fields','asset'}:
        raise ValueError('Row continuation conflicts with other notice selectors')
    parts=[];fragments=[];bounds=[0,*breaks,len(rows)]
    try:
        for number,(start,end) in enumerate(zip(bounds,bounds[1:])):
            fragment=BeautifulSoup('<table><tbody></tbody></table>','html.parser')
            fragment.table.attrs=copy.deepcopy(table.attrs)
            caption=table.find('caption',recursive=False)
            if number==0 and caption:fragment.table.insert(0,copy.deepcopy(caption))
            for row in rows[start:end]:fragment.tbody.append(copy.deepcopy(row))
            selected=copy.deepcopy(presentation)
            if 'cell_styles' in selected:
                selected['cell_styles']=[{**c,'row':c['row']-start}for c in selected['cell_styles']if start<=c['row']<end]
            if number:
                selected.pop('caption_style',None);selected.pop('header_align',None)
            conv.table_styles={str(index):selected};conv.table_index=index
            child=copy.deepcopy(style);child.pop('table_row_breaks');child.pop('content_selector',None)
            content={'html':(''.join(map(str,prefix))if number==0 else '')+str(fragment)+(''.join(map(str,suffix))if end==len(rows)else '')}
            child['content_sha256']=digest(content);child['flow_lines']=False
            if number:child['title']={'selector':'none','line_sizes_pt':[],'before_pt':0,'after_pt':0}
            if end<len(rows):child['contact']={'selector':'none','flow':'preserve','before_pt':0}
            if 'line_styles' in child:
                plain=Projection(content).text
                child['line_styles']=[s for s in child['line_styles']if s['text'] in plain]
            fragments.append(content);parts.append(render(conv,content,child,level_root))
    finally:
        conv.table_styles=saved;conv.table_index=index+1
    before=Projection(value);after=Projection({'html':''.join(f['html']for f in fragments)})
    if ''.join(before.text.split())!=''.join(after.text.split()) or [(r['base'],r['reading'])for r in before.ruby]!=[(r['base'],r['reading'])for r in after.ruby]:
        raise ValueError('Table continuation changed text, order or ruby')
    conv.features.append({'kind':'native_notice_table_row_continuation','table_index':index,'row_boundaries':bounds,
                          'caption_count':int(bool(table.find('caption'))),'repeated_content':False})
    return r'\clearpage'.join(parts)
