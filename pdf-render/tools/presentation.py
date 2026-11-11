"""Source-bound optional presentation facts and common layout mechanics."""
import re

def source_binding(unit, evidence):
    from era_registry import for_unit
    return for_unit(unit).presentation(unit, evidence)


def task_tabs(model):
    tabs = model['style'].get('task_edge_tabs')
    if tabs is None:
        return None
    if tabs['basis'] != 'observed_label_generated_outer_parity' or tabs['policy_decision'] != 'observed-task-edge-tabs':
        raise ValueError('Unsupported task-tab policy')
    if tabs['evidence'].get('kind') == 'approved_workbook_2012_furniture':
        if not model['style'].get('workbook_native_2012_furniture'):
            raise ValueError('Missing validated 2012 furniture source binding')
    else:
        source_binding(model['unit'], tabs['evidence'])
    known_tasks = {s['task'] for s in model['layout']['sections'].values()}
    if set(tabs['task_groups']) != known_tasks:
        raise ValueError('Task tabs must map every rendered task exactly')
    if set(tabs['task_groups'].values())-{None} != set(tabs['groups']):
        raise ValueError('Unused or unknown task-tab group')
    for group in tabs['groups'].values():
        parts = group.get('label_parts')
        if parts is not None:
            if (not parts or ''.join(p['base'] for p in parts) != group['label']
                or any(len(p['base']) != 1 or not re.fullmatch(r'[ぁ-ゖ]{1,4}', p['reading']) for p in parts)):
                raise ValueError('Task-tab readings must match the observed label characters')
    return tabs


def tab_pages(model, anchors, page_count):
    tabs = model['render_coverage'].get('task_edge_tabs')
    if not tabs:
        return {}
    blank = {v for k,v in anchors.items() if k.startswith('intentional-')}
    sections = [(anchors[s['id']], model['layout']['sections'][s['id']]) for s in model['document']['sections']]
    booklet_starts = {}
    for page, section in sections:
        booklet_starts.setdefault(section['booklet'], page)
    result = {}
    for page in range(1, page_count+1):
        if page in blank:
            continue
        section = [s for start,s in sections if start <= page][-1]
        key = tabs['task_groups'][section['task']]
        if key is None:
            continue
        group = tabs['groups'][key]
        result[page] = {'label':group['label'], 'reading_text':''.join(p['reading'] for p in group.get('label_parts', [])), 'top_pt':group['top_pt'], 'side':'right' if (page-booklet_starts[section['booklet']]+1)%2 else 'left'}
    return result
