"""Explicit source-bound target/choice rows in Old JLPT worked examples."""
from bs4 import BeautifulSoup, Tag
from model import Projection, digest
from presentation import source_binding


def validate(item, binding):
    if (item.get('type') != 'example' or not isinstance(item.get('content'), dict)
            or digest(item['content']) != binding['content_sha256']
            or len(item.get('options', [])) != 4
            or digest(item['options']) != binding['options_sha256']):
        raise ValueError('Stale historical example target-row content/options')
    if binding['columns'] not in (2, 4) or isinstance(binding['columns'], bool):
        raise ValueError('Historical example requires an explicit 2/4-column grid')
    for key, low, high in [('target_width_em', 3, 12), ('left_indent_em', 0, 8)]:
        v = binding[key]
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not low <= v <= high:
            raise ValueError('Invalid historical example row dimension: ' + key)
    # The ordinary form owns a separate, underlined target paragraph. The
    # explicitly bound DOC form keeps its absent underline and embedded list.
    soup = BeautifulSoup(item['content']['html'], 'html.parser')
    children = [n for n in soup.children if isinstance(n, Tag) or str(n).strip()]
    index = binding['target_part']
    shape = binding.get('source_shape')
    if shape is not None:
        if shape != 'merged_prompt_target_embedded_choices':
            raise ValueError('Unknown historical example source shape')
        from notice_layout import html_lines
        if (type(index) is not int or index != 1 or len(children) != 3
                or [getattr(n, 'name', None) for n in children] != ['p', 'ol', 'p']
                or len(children[0].find_all('br')) != 1 or children[0].find('u')):
            raise ValueError('Unsupported merged example prompt/target')
        parts = html_lines(children[0].decode_contents())
        if len(parts) != 2:
            raise ValueError('Merged example requires exactly one target line')
        prompt, target = [Projection({'html': p}) for p in parts]
        options = children[1].find_all('li', recursive=False)
        if (target.text != binding['target_text'] or not target.text
                or prompt.text.count(target.text) != 1 or len(options) != 4
                or len(children[1].find_all('li')) != 4):
            raise ValueError('Merged example target/options are ambiguous')
        for node, option in zip(options, item['options']):
            actual, expected = Projection({'html': node.decode_contents()}), Projection(option)
            if (actual.text, actual.ruby) != (expected.text, expected.ruby):
                raise ValueError('Merged example embedded options differ from metadata')
        return
    if (isinstance(index, bool) or index != 1 or len(children) < 3
            or any(not isinstance(n, Tag) or n.name != 'p' for n in children[:2])):
        raise ValueError('Unsupported historical example target paragraph')
    target = Projection({'html': children[index].decode_contents()})
    marks = children[0].find_all('u')
    if len(marks) != 1:
        raise ValueError('Ambiguous historical example prompt target')
    marked = Projection({'html': marks[0].decode_contents()})
    if target.text != binding['target_text'] or (target.text, target.ruby) != (marked.text, marked.ruby):
        raise ValueError('Historical example target differs from its prompt')


def collect(model):
    bindings = {iid: m['historical_example_target_row'] for iid, m in model['layout']['items'].items()
                if 'historical_example_target_row' in m}
    if not bindings:
        return {}
    if model.get('exam', {}).get('generation') != 'historical-1991-2009':
        raise ValueError('Historical example row outside Old JLPT')
    items = {i['id']: i for s in model['document']['sections'] for i in s['items']}
    for iid, binding in bindings.items():
        meta = model['layout']['items'][iid]
        if meta.get('example_layout') or meta.get('example_variant', 'ordinary') != 'ordinary':
            raise ValueError('Conflicting historical example layout')
        validate(items[iid], binding)
        source_binding(model['unit'], binding['evidence'])
    return bindings


def resolve_options_geometry(binding, style):
    """Source-bound exceptions precede family defaults; absent keys preserve output."""
    result=dict(binding)
    for key, default_key, low, high in [
            ('left_indent_em','ordinary_options_left_indent_em',0,8),
            ('prompt_label_indent_em','ordinary_options_prompt_indent_em',0,4),
            ('prompt_label_gap_em','ordinary_options_label_gap_em',0,5),
            ('width_fraction',None,.4,1)]:
        if key not in result and default_key in style:result[key]=style[default_key]
        if key in result and (type(result[key]) not in (int,float) or not low<=result[key]<=high):
            raise ValueError('Invalid historical example geometry: '+key)
    return result


def collect_options(model):
    """Source grids for examples whose target remains in the prompt."""
    bindings = {iid: m['historical_example_options'] for iid, m in model['layout']['items'].items()
                if 'historical_example_options' in m}
    if not bindings:
        return {}
    if model.get('exam', {}).get('generation') != 'historical-1991-2009':
        raise ValueError('Historical example grid outside Old JLPT')
    items = {i['id']: i for s in model['document']['sections'] for i in s['items']}
    for iid, b in bindings.items():
        item = items[iid];meta = model['layout']['items'][iid]
        if (item.get('type') != 'example' or len(item.get('options', [])) != 4
                or digest(item['content']) != b['content_sha256']
                or digest(item['options']) != b['options_sha256']
                or isinstance(b['columns'], bool) or b['columns'] not in (1, 2, 4)):
            raise ValueError('Stale or invalid historical example option grid')
        if (meta.get('historical_example_target_row') or meta.get('example_layout')
                or meta.get('example_variant', 'ordinary') != 'ordinary'):
            raise ValueError('Conflicting historical example option layout')
        resolve_options_geometry(b,{})
        if 'spacing_role' in b and (b['spacing_role'] != 'word_usage' or b['columns'] != 1):
            raise ValueError('Word-usage example requires a bound one-column grid')
        if 'after_pt' in b and (type(b['after_pt']) not in (int,float) or not 0<=b['after_pt']<=100):
            raise ValueError('Invalid source-bound example after gap')
        source_binding(model['unit'], b['evidence'])
    return bindings


def after_gap(style, binding, fallback):
    """Resolve explicit example roles; local source evidence has final priority."""
    value,origin=fallback,None
    by_columns=style.get('ordinary_after_by_columns_pt',{})
    if not isinstance(by_columns,dict) or set(by_columns)-{'1','2','4'}:
        raise ValueError('Invalid Old example column-gap map')
    for gap in by_columns.values():
        if type(gap) not in (int,float) or not 0<=gap<=100:
            raise ValueError('Invalid Old example column after gap')
    key=str(binding['columns'])
    if key in by_columns:value,origin=by_columns[key],'option_columns_default'
    if binding.get('spacing_role')=='word_usage' and 'ordinary_word_usage_after_pt' in style:
        value,origin=style['ordinary_word_usage_after_pt'],'word_usage_default'
    if 'after_pt' in binding:value,origin=binding['after_pt'],'source_bound_exception'
    if origin and (type(value) not in (int,float) or not 0<=value<=100):
        raise ValueError('Invalid Old example role after gap')
    return value,origin


def render(conv, item_id, target_html, options, binding):
    from historical_layout import options_tex
    if Projection({'html': target_html}).text != binding['target_text']:
        raise ValueError('Historical example parser target differs from binding')
    target = conv.value({'html': target_html}, 'example')
    grid = options_tex(conv, {'id': item_id, 'options': options},
        {'kind': 'grid', 'columns': binding['columns'], 'source_numbered': False},
        [conv.value(v, 'option') for v in options], row_gap_pt=0)
    conv.features.append(dict(kind='historical_example_target_row', target=item_id,
        columns=binding['columns'], target_text=binding['target_text'],
        target_width_em=binding['target_width_em'], left_indent_em=binding['left_indent_em'],
        content_sha256=binding['content_sha256'], options_sha256=binding['options_sha256'],
        canonical_changed=False))
    before=getattr(conv,'historical_example_target_before_pt',0)
    if isinstance(before,bool)or not isinstance(before,(int,float))or not 0<=before<=30:
        raise ValueError('Invalid historical example target gap')
    gap=r'\par\vspace{'+str(before)+'pt}'if before else ''
    after=getattr(conv,'historical_example_target_after_pt',0)
    if type(after)not in [int,float]or not 0<=after<=30:raise ValueError('Invalid example target after gap')
    return (gap+r'\HistoricalExampleTargetRow{' + str(binding['left_indent_em']) + 'em}{'
            + str(binding['target_width_em']) + 'em}{' + target + '}{' + grid + '}'
            +(r'\par\vspace{'+str(after)+'pt}'if after else''))
