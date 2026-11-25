"""Independent Old component metrics; defaults preserve structure30 output."""
DEFAULTS = dict(option_label_width_em=1.8, target_group_before_pt=8,
                target_group_after_pt=10, target_prose_after_pt=8,
                example_target_before_pt=0, example_target_after_pt=0)
LIMITS = dict(option_label_width_em=(.8, 3), target_group_before_pt=(0, 30),
              target_group_after_pt=(0, 30), target_prose_after_pt=(0, 30),
              example_target_before_pt=(0, 30), example_target_after_pt=(0, 30))


def parameters(style, task=None):
    scoped=style.get('task_overrides',{}).get(task,{}).get('historical_component_metrics',{}) if task else {}
    if not isinstance(scoped,dict) or set(scoped)-{'target_group_before_pt','target_group_after_pt','target_prose_after_pt'}:
        raise ValueError('Invalid task-scoped target component metrics')
    values = {**DEFAULTS, **style.get('historical_component_metrics', {}), **scoped}
    if set(values) != set(LIMITS):
        raise ValueError('Unknown historical component metric')
    for key, value in values.items():
        lo, hi = LIMITS[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not lo <= value <= hi:
            raise ValueError('Invalid historical component metric: ' + key)
    return values
