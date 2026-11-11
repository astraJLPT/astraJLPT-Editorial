"""Source-bound target/choice rows for Old JLPT vocabulary groups.

The target/context relationship is checked against the canonical annotations;
the option grid is explicit and never selected by a measured text-length guess.
"""
from model import digest
from presentation import source_binding
from historical_groups import collect as collect_groups


DEFAULTS = dict(target_width_em=8.5, label_width_em=1.8,
                left_indent_em=1.0, row_gap_pt=0, choice_row_gap_pt=0)


def parameters(style, task=None):
    task_values = style.get('task_overrides', {}).get(task, {}).get('historical_target_rows', {}) if task else {}
    values = {**DEFAULTS, **style.get('historical_target_rows', {}), **task_values}
    limits = dict(target_width_em=(5, 16), label_width_em=(1, 3),
                  left_indent_em=(0, 3), row_gap_pt=(0, 12), choice_row_gap_pt=(0, 12))
    if set(values) != set(limits):
        raise ValueError('Unknown historical target-row parameter')
    for key, value in values.items():
        low, high = limits[key]
        if isinstance(value, bool) or not isinstance(value, (float, int)) or not low <= value <= high:
            raise ValueError('Invalid historical target-row parameter: ' + key)
    return values


def collect(model):
    bindings = {qid: meta['historical_target_row'] for qid, meta in model['layout']['items'].items()
                if 'historical_target_row' in meta}
    if not bindings:
        return {}
    if model.get('exam', {}).get('generation') != 'historical-1991-2009':
        raise ValueError('Historical target row outside Old JLPT')
    groups, _ = collect_groups(model)
    context_for = {qid: context for context, qids in groups.items() for qid in qids}
    items = {item['id']: item for section in model['document']['sections'] for item in section['items']}
    for qid, binding in bindings.items():
        item = items[qid]
        if ('stem' not in item or digest(item['stem']) != binding['stem_sha256']
                or context_for.get(qid) != binding['context_id']):
            raise ValueError('Stale or mismatched historical target-row binding')
        source_binding(model['unit'], binding['evidence'])
        if binding.get('choice_placement', 'inline') not in ('inline', 'below'):
            raise ValueError('Unknown historical target choice placement')
        if 'target_width_em' in binding:
            width=binding['target_width_em']
            if isinstance(width,bool) or not isinstance(width,(float,int)) or not 5<=width<=16:
                raise ValueError('Invalid source-bound target column width')
        grid = model['layout']['items'][qid].get('historical_options', {})
        if (grid.get('kind') != 'grid' or type(grid.get('columns')) is not int
                or grid['columns'] not in (1, 2, 3, 4)
                or grid.get('source_numbered') is not False or grid.get('multiline', False)
                or digest(item['options']) != grid.get('options_sha256')):
            raise ValueError('Historical target row requires its exact explicit 1/2/3/4-column options')
        if binding.get('choice_placement') == 'below' and grid['columns'] != 2:
            raise ValueError('Below-target choices require a source-bound two-column grid')
    return bindings


def render(conv, item, binding, display_label, stem_tex, option_tex, settings):
    import re
    compact=re.fullmatch(r'（([1-9][0-9]*)）',display_label)
    if compact:display_label=r'\HistoricalCompactNumber{'+compact[1]+'}'
    settings={**settings}
    if 'target_width_em' in binding:settings['target_width_em']=binding['target_width_em']
    below = binding.get('choice_placement') == 'below'
    conv.features.append(dict(kind='historical_below_target_row' if below else 'historical_inline_target_row', target=item['id'],
        context=binding['context_id'], stem_sha256=digest(item['stem']),
        options_sha256=digest(item['options']), settings=settings, canonical_changed=False))
    setup = ''.join('\\renewcommand\\' + macro + '{' + str(settings[key]) + suffix + '}'
        for key, macro, suffix in [('target_width_em','HistoricalTargetWidth','em'),
            ('label_width_em','HistoricalTargetLabelWidth','em'),
            ('left_indent_em','HistoricalTargetIndent','em'),
            ('row_gap_pt','HistoricalTargetRowGap','pt')])
    macro = r'\HistoricalTargetBelow' if below else r'\HistoricalTargetRow'
    return ('{' + setup + macro + '{' + item['id'] + '}{' + display_label + '}{'
            + stem_tex + '}{' + option_tex + '}}')
