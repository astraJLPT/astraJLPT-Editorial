"""Source-bound historical graph associations and mixed-direction passages."""
import base64
import hashlib
import re
from bs4 import BeautifulSoup, Tag
from model import digest, Projection
from presentation import source_binding


def image_hash(node):
    return hashlib.sha256(base64.b64decode(node['src'].split(',', 1)[1])).hexdigest()


def detach_graph(value, binding):
    if not isinstance(value, dict) or digest(value) != binding['content_sha256']:
        raise ValueError('Stale historical graph binding')
    soup = BeautifulSoup(value['html'], 'html.parser')
    if 'table_chart_sha256' in binding:
        roots = [node for node in soup.children if isinstance(node, Tag)]
        tables = soup.find_all('table'); images = soup.find_all('img')
        if len(tables) != 1 or len(images) != 1 or tables[0].parent is not soup:
            raise ValueError('Historical table/chart group requires one exact table and image')
        index = roots.index(tables[0]); group = roots[index - 1:index + 4]
        if (index < 2 or len(group) != 5
                or [node.name for node in group] != ['p', 'table', 'p', 'p', 'p']
                or not group[0].get_text().startswith('表')
                or not group[2].get_text().startswith('図')
                or group[3].get_text(strip=True) or group[3].find('img') is not images[0]
                or not group[4].get_text().startswith('（図：')
                or any(node.name != 'p' for node in roots[:index - 1])
                or any(node.name != 'p' or not node.get_text().startswith('（注')
                       for node in roots[index + 4:])
                or digest({'html': ''.join(str(node) for node in group)}) != binding['table_chart_sha256']
                or any(key in binding for key in ['image_sha256', 'native_chart_sha256', 'native_table_sha256'])):
            raise ValueError('Historical table/chart group requires exact captions, table, image and citation')
        figure = {'html': ''.join(str(node.extract()) for node in group)}
        return {'html': str(soup)}, figure
    if 'native_table_sha256' in binding:
        roots = [node for node in soup.children if isinstance(node, Tag)]
        if (len(roots) != 4 or [node.name for node in roots] != ['p', 'p', 'table', 'p']
                or len(soup.find_all('table')) != 1 or soup.find('img')
                or roots[2].find('caption') is None
                or 'citation' not in roots[3].get('class', [])
                or not roots[3].get_text().startswith('（グラフは')
                or digest({'html': str(roots[2])}) != binding['native_table_sha256']
                or 'image_sha256' in binding or 'native_chart_sha256' in binding):
            raise ValueError('Historical statistical display requires its exact title, table and citation')
        figure = {'html': ''.join(str(node.extract()) for node in roots[1:])}
        return {'html': str(soup)}, figure
    if 'native_chart_sha256' in binding:
        charts = soup.select('table[data-native-chart="historical-2009-pies"]')
        if (len(charts) != 1 or charts[0].parent is not soup
                or charts[0].find_next_sibling() is not None
                or digest({'html': str(charts[0])}) != binding['native_chart_sha256']
                or 'image_sha256' in binding):
            raise ValueError('Historical native chart requires its exact final table')
        figure = {'html': str(charts[0].extract())}
        return {'html': str(soup)}, figure
    images = soup.find_all('img')
    if len(images) != 1 or image_hash(images[0]) != binding['image_sha256']:
        raise ValueError('Historical graph image differs from binding')
    panel = images[0].parent
    citation = panel.find_next_sibling()
    citation_text = citation.get_text() if citation is not None else ''
    source_citation = (citation_text.startswith('（グラフ：') or
                       re.fullmatch(r'（[^（）\n]+による）', citation_text))
    if (panel.name != 'p' or panel.get_text(strip=True) or citation is None
            or citation.name != 'p' or not source_citation
            or citation.find_next_sibling() is not None):
        raise ValueError('Historical graph requires its exact final panel and citation')
    figure = {'html': str(panel.extract()) + str(citation.extract())}
    return {'html': str(soup)}, figure


def collect_graphs(model):
    contexts, questions = {}, {}
    for section in model['document']['sections']:
        items = section['items']
        for index, item in enumerate(items):
            binding = model['layout']['items'][item['id']].get('historical_graph_after')
            if not binding:
                continue
            if 'content' not in item:
                raise ValueError('Historical graph must belong to a context')
            source_binding(model['unit'], binding['evidence'])
            detach_graph(item['content'], binding)
            following = []
            for q in items[index + 1:]:
                if 'stem' not in q:
                    break
                following.append(q['id'])
            qid = binding['question_id']
            if qid not in following or qid in questions:
                raise ValueError('Historical graph question must follow its own context exactly once')
            if 'table_chart_sha256' in binding and (binding.get('associated_question_ids') != following or qid != following[-1]):
                raise ValueError('Shared historical table/chart must follow its complete associated question group')
            placement = binding.get('placement', 'after_questions')
            if placement not in ('after_questions', 'source_order'):
                raise ValueError('Unknown historical graph placement')
            if placement == 'source_order' and binding.get('page_break_before_figure'):
                raise ValueError('Source-order graph conflicts with a deferred-figure page break')
            if 'keep_through_citation_if_fits' in binding and (binding['keep_through_citation_if_fits'] is not True or placement != 'source_order'):
                raise ValueError('Display keep requires an explicit source-order group')
            contexts[item['id']] = binding
            if placement == 'after_questions':questions[qid] = item['id']
    return contexts, questions


DISPLAY_KEEP_END = r'\HistoricalDisplayKeepEnd{}'


def mark_display_group(value, binding, original):
    """Mark the end of the exact source figure without pulling later notes in."""
    if binding.get('placement') != 'source_order' or binding.get('keep_through_citation_if_fits') is not True:
        raise ValueError('Missing source display keep declaration')
    _,figure=detach_graph(original,binding)
    roots=BeautifulSoup(figure['html'],'html.parser').find_all('p',recursive=False)
    if not roots or not roots[-1].get_text().startswith(('（図：','（グラフ：','（グラフは')):
        raise ValueError('Display keep requires an exact terminal figure citation')
    citation=Projection({'html':str(roots[-1])}).text
    return mark_display_boundary(value,citation)


def mark_sequence_display_group(value,binding,original,unit):
    """Keep an exact four-blank/four-fragment insertion structure through its citation."""
    if binding.get('keep_sequence_through_citation_if_fits')is not True or digest(original)!=binding['content_sha256']:
        raise ValueError('Stale or missing source sequence keep declaration')
    source_binding(unit,binding['evidence'])
    soup=BeautifulSoup(original['html'],'html.parser');roots=[n for n in soup.children if isinstance(n,Tag)]
    blanks=soup.select('[data-historical-framed-document="single"]');fragments=soup.select('[data-historical-labeled-frame]')
    citations=[p['text']for p in binding['paragraphs']if p['role']=='citation']
    if (len(blanks)!=4 or [n.get_text(strip=True)for n in blanks]!=list('アイウエ')
            or len(fragments)!=4 or [n['data-historical-labeled-frame']for n in fragments]!=list('ABCD')
            or any(n.get('data-historical-border-style')!='dashed'for n in fragments)
            or any(n.parent is not soup for n in blanks+fragments)or soup.find(['img','table'])
            or roots.index(blanks[-1])>=roots.index(fragments[0])or len(citations)!=1):
        raise ValueError('Sequence keep requires four ordered blank bars and four dashed fragments')
    citation=fragments[-1].find_next_sibling()
    if citation is None or citation.name!='p' or Projection({'html':str(citation)}).text.strip()!=citations[0]:
        raise ValueError('Sequence keep requires its exact citation immediately after fragment D')
    notes=roots[roots.index(citation)+1:]
    if (not notes or any(n.name!='p'for n in notes)
            or [Projection({'html':str(n)}).text.strip()for n in notes]!=[p['text']for p in binding['paragraphs']if p['role']=='note']):
        raise ValueError('Sequence keep must leave all following notes outside the measured group')
    return mark_display_boundary(value,citations[0])


def mark_display_boundary(value,citation):
    soup=BeautifulSoup(value['html'],'html.parser')
    hits=[p for p in soup.find_all('p')if Projection({'html':str(p)}).text.strip()==citation.strip()]
    if len(hits)!=1:raise ValueError('Ambiguous display citation boundary')
    last=hits[0]
    while last.parent is not soup:last=last.parent
    marker=soup.new_tag('span',attrs={'data-historical-display-keep-end':'true'})
    last.insert_after(marker)
    after={'html':str(soup)}
    if Projection(value).text!=Projection(after).text or Projection(value).ruby!=Projection(after).ruby:
        raise ValueError('Display keep changed protected text')
    return after


def keep_display_tex(tex, anchor, item_id):
    if tex.count(DISPLAY_KEEP_END)!=1:raise ValueError('Display keep boundary was not emitted once')
    prefix,suffix=tex.split(DISPLAY_KEEP_END)
    return r'\QuestionGroupKeep{'+item_id+r'-display}{'+anchor+prefix+'}'+suffix


def vertical_parts(value, binding):
    if not isinstance(value, dict) or digest(value) != binding['content_sha256']:
        raise ValueError('Stale historical vertical inset binding')
    soup = BeautifulSoup(value['html'], 'html.parser')
    roots = [n for n in soup.children if isinstance(n, Tag)]
    roles = ['data-outer-passage-label', 'data-vertical-passage-body',
             'data-vertical-inset-figure', 'data-horizontal-passage-trailer']
    if len(roots) != 4 or any(n.get(role) != 'true' for n, role in zip(roots, roles)):
        raise ValueError('Vertical inset requires four explicit canonical component roles')
    label, body, inset, trailer = roots
    if len(inset.find_all('img')) != 1 or image_hash(inset.img) != binding['image_sha256']:
        raise ValueError('Historical vertical inset image differs from binding')
    if body.find('img') or trailer.find('img') or inset.get_text(strip=True):
        raise ValueError('Vertical figure must occur once in its explicit inset')
    paragraphs = body.find_all('p', recursive=False)
    if not paragraphs or any(n.name != 'p' for n in body.children if isinstance(n, Tag)):
        raise ValueError('Vertical body requires canonical paragraphs')
    return label, paragraphs, inset.img, trailer


def vertical_tex(conv, value, binding, unit, anchor=''):
    if not getattr(conv, 'source_target_markers', False):
        raise ValueError('Historical vertical inset outside historical edition')
    source_binding(unit, binding['evidence'])
    label, paragraphs, img, trailer = vertical_parts(value, binding)
    from historical_nodes import image_at_width
    saved = getattr(conv, 'active_vertical_body', False)
    conv.active_vertical_body = True
    try:
        # A single native paragraph keeps parshape's column count continuous.
        # Forced line endings retain every canonical paragraph boundary.
        body = r'\hfil\break\hskip1\zw '.join(
            ''.join(conv.node(c, 'body') for c in p.children) for p in paragraphs)
    finally:
        conv.active_vertical_body = saved
    graphic = image_at_width(conv, img, 1)
    trailer_paragraphs = trailer.find_all('p', recursive=False)
    if len(trailer_paragraphs) < 2 or any(not p.get_text().startswith('（注') for p in trailer_paragraphs[1:]):
        raise ValueError('Vertical exterior trailer requires a citation followed by source notes')
    gap=binding.get('citation_to_notes_pt',0)
    if not 0<=gap<=24:raise ValueError('Invalid vertical citation clearance')
    boundary=''
    if 'notes_page_boundary' in binding:
        if binding['notes_page_boundary']!='source_note_continuation' or len(binding['evidence']['physical_pages'])<2:
            raise ValueError('Vertical note continuation needs its exact multi-page source binding')
        boundary=r'\par\newpage '
        conv.features.append(dict(kind='historical_vertical_note_source_continuation',notes=len(trailer_paragraphs)-1,canonical_changed=False))
    caption_notes = (conv.node(trailer_paragraphs[0], 'body')+boundary
                     + r'\par\addvspace{'+str(gap)+r'pt}\noindent\begin{minipage}{\linewidth}'
                     + ''.join(conv.node(p, 'body') for p in trailer_paragraphs[1:])
                     + r'\par\end{minipage}\par')
    g = binding['geometry']
    extent, short = g['extent_em'], g['extent_em'] - g['inset_height_em']
    columns, pitch = g['inset_columns'], g['column_pitch_em']
    if not (36 <= extent <= 50 and 6 <= columns <= 10 and 1.7 <= pitch <= 2.2
            and 8 <= g['inset_height_em'] <= 14):
        raise ValueError('Invalid historical vertical inset geometry')
    shape = str(columns + 1) + ' ' + ('0pt ' + str(short) + r'\zw ') * columns + '0pt ' + str(extent) + r'\zw '
    conv.features.append({'kind': 'historical_native_vertical_inset', 'content_sha256': digest(value),
                          'image_sha256': binding['image_sha256'], 'paragraphs': len(paragraphs),
                          'geometry': g, 'figure_upright': True, 'horizontal_trailer': True})
    return (r'\par\noindent\begin{minipage}{\linewidth}'+anchor+r'\PassageLabel{' + conv.text(label.get_text()) + r'}\par\nobreak '
            r'\HistoricalVerticalInset{' + str(extent) + '}{' + str(pitch) + '}{' + shape + '}{' + body + '}{'
            + str((columns - .6) * pitch) + r'em}{' + graphic + '}'
            + r'\par\end{minipage}\par\addvspace{8pt}' + caption_notes)
