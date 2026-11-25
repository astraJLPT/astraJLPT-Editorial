"""Bind a terminal information-context table to its exact scored question.

Canonical fields remain intact. The native table is consumed once after the
question stem, and omitted once from its serialized context at render time.
"""
from bs4 import BeautifulSoup, Tag
from model import Projection, digest


def signature(value):
    p = Projection(value)
    return ''.join(p.text.split()), [(r['base'],r['reading']) for r in p.ruby]


def detach(value, binding):
    shape = binding.get('source_shape', 'notice_tail')
    if shape not in ['notice_tail', 'standalone_table']:
        raise ValueError('Unknown question-table source shape')
    if not isinstance(value, dict):
        raise ValueError('Question table requires rich context content')
    soup = BeautifulSoup(value['html'], 'html.parser')
    tables = soup.find_all('table')
    if len(tables) != 1 or binding['table_index'] != 0:
        raise ValueError('Question table requires exactly one native table')
    table = tables[0]
    if table.parent is not soup:
        raise ValueError('Question table must be a top-level context tail')
    if any(Projection({'html':str(n)}).text.strip() or
           isinstance(n,Tag) and n.name not in ['br'] for n in table.next_siblings):
        raise ValueError('Question table must be the complete terminal region')
    fragment = {'html':str(table)}
    if digest(fragment) != binding['table_sha256']:
        raise ValueError('Question table bytes differ from the authored table')
    table.extract()
    remainder = {'html':str(soup)}
    if signature({'html':remainder['html']+fragment['html']}) != signature(value):
        raise ValueError('Question table transfer changed text or ruby')
    if shape == 'standalone_table':
        if any(Projection({'html':str(n)}).text.strip() or
               isinstance(n,Tag) and n.name != 'br' for n in soup.children):
            raise ValueError('Standalone question table cannot discard other content')
    elif not Projection(remainder).text.strip():
        raise ValueError('Question table requires a remaining information notice')
    return remainder, fragment


def collect(model):
    contexts, questions = {}, {}
    for section in model['document']['sections']:
        items = {i['id']:i for i in section['items']}
        for item in section['items']:
            binding = model['layout']['items'][item['id']].get('question_table')
            if not binding:
                continue
            if model['layout']['sections'][section['id']]['task'] != 'information_retrieval':
                raise ValueError('Question table requires an information-retrieval section')
            if 'content' not in item or digest(item['content']) != binding['content_sha256']:
                raise ValueError('Stale question-table context')
            question = items.get(binding['question_id'])
            if not question or 'stem' not in question or digest(question['stem']) != binding['stem_sha256']:
                raise ValueError('Question table requires its exact same-section scored stem')
            if question['id'] in questions or '<table' in str(question['stem']):
                raise ValueError('Question already owns a table')
            meta = model['layout']['items'][item['id']]
            if any(k in meta for k in ['notes','decision_tree','table_captions','shared_note_anchors']):
                raise ValueError('Question table conflicts with another context structure')
            standalone = binding.get('source_shape') == 'standalone_table'
            if standalone:
                if item.get('type') != 'table':
                    raise ValueError('Standalone question table requires a table context')
                if any(item['id'] in model['style'].get(k,{}) for k in
                       ['block_styles','section_styles','inline_presentations']):
                    raise ValueError('Standalone question table conflicts with document styling')
                if not any(j['id'] != item['id'] and 'content' in j and
                           j.get('type') not in ['table','example'] for j in section['items']):
                    raise ValueError('Standalone question table requires its separate information notice')
            elif item['id'] not in model['style'].get('block_styles',{}):
                raise ValueError('Question table requires an authored native notice')
            remainder, table = detach(item['content'],binding)
            record = {'context_id':item['id'],'question_id':question['id'],
                      'binding':binding,'table':table,'remainder':remainder,
                      'standalone':standalone}
            contexts[item['id']] = record
            questions[question['id']] = record
    return contexts, questions


def validate_pages(model, section, anchors):
    """Information notices follow questions; question-owned tables travel with them."""
    questions = [i for i in section['items'] if 'stem' in i]
    qpages = {anchors[i['id']] for i in questions}
    notices, tables = [], []
    for item in section['items']:
        if 'content' not in item:
            continue
        binding = model['layout'].get('items',{}).get(item['id'],{}).get('question_table',{})
        if binding.get('source_shape') == 'standalone_table':
            if item.get('type') != 'table' or digest(item['content']) != binding['content_sha256']:
                raise ValueError('Stale standalone question-table pagination')
            found = [n for n,q in enumerate(questions) if q['id'] == binding['question_id'] and digest(q['stem']) == binding['stem_sha256']]
            if len(found) != 1:
                raise ValueError('Question-table pagination has no exact scored owner')
            if sum(f.get('kind') == 'standalone_question_table_consumed' and
                   f.get('context_id') == item['id'] and
                   f.get('question_id') == binding['question_id'] and
                   f.get('table_sha256') == binding['table_sha256']
                   for f in model['render_coverage']['features']) != 1:
                raise ValueError('Question-table pagination lacks exact consumption evidence')
            tables.append((item,binding,found[0]))
        else:
            notices.append(item)
    bpages = {anchors[i['id']] for i in notices}
    if not qpages or not bpages or max(qpages) >= min(bpages):
        raise ValueError('Information questions must precede their context')
    for item,binding,index in tables:
        first,last = anchors.get(item['id']),anchors.get('context-end-'+item['id'])
        if first is None or last is None or not anchors[binding['question_id']] <= first <= last < min(bpages):
            raise ValueError('Question table is outside its scored-question region')
        if index+1 < len(questions) and last > anchors[questions[index+1]['id']]:
            raise ValueError('Question table crosses the following scored question')
