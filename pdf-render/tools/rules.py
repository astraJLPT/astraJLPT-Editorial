"""Native rule primitives: weight, single/double/dashed style and edge selection."""


def validate_rule(rule):
    if set(rule)-{'style','width_pt','double_gap_pt','edges'}:
        raise ValueError('Unknown rule property')
    if rule.get('style','single') not in ['single','double','dashed','none']:
        raise ValueError('Unknown rule style')
    if not .1 <= rule.get('width_pt',.4) <= 3:
        raise ValueError('Invalid rule weight')
    if not .2 <= rule.get('double_gap_pt',1.2) <= 6:
        raise ValueError('Invalid double-rule gap')


def table_settings(rules, rows, columns):
    if set(rules)-{'default','horizontal','vertical','double_gap_pt'}:
        raise ValueError('Unknown table rule setting')
    default=rules.get('default',{'style':'single','width_pt':.4})
    validate_rule(default)
    gap=rules.get('double_gap_pt',1.2)
    if not .2 <= gap <= 6:raise ValueError('Invalid table double-rule gap')
    result=[',rulesep='+str(gap)+'pt']
    resolved={}
    for axis,count in [('horizontal',rows),('vertical',columns)]:
        key='hline' if axis=='horizontal' else 'vline'
        overrides=rules.get(axis,[])
        boundaries=[x['boundary'] for x in overrides]
        if len(boundaries)!=len(set(boundaries)) or any(type(b)!=int or not 0<=b<=count for b in boundaries):
            raise ValueError('Invalid or duplicate table rule boundary')
        by_index={x['boundary']:{k:v for k,v in x.items()if k!='boundary'}for x in overrides}
        resolved[axis]={index:by_index.get(index,default) for index in range(count+1)}
        for index in range(count+1):
            rule=by_index.get(index,default);validate_rule(rule)
            style=rule.get('style','single');weight=rule.get('width_pt',.4)
            if style=='none':continue
            dash='dashed' if style=='dashed' else 'solid'
            for stroke in range(1,3 if style=='double' else 2):
                # Single/double joins stay connected. Double/double crossings
                # receive source-supported open-center endpoints below.
                junction=',abovepos=1,belowpos=1'if axis=='vertical'else''
                result.append(','+key+'{'+str(index+1)+'}={'+str(stroke)+'}{-}{'+str(weight)+'pt,'+dash+junction+'}')
    for h,hrule in resolved['horizontal'].items():
        if hrule.get('style','single')!='double':continue
        hw=hrule.get('width_pt',.4);hpos=f'{hw/(2*hw+gap):.9f}'
        for v,vrule in resolved['vertical'].items():
            if vrule.get('style','single')!='double':continue
            vw=vrule.get('width_pt',.4);vpos=f'{vw/(2*vw+gap):.9f}'
            # Each native segment reaches the nearer paired stroke, leaving
            # the crossing's center open instead of drawing a four-line grid.
            # No geometry or endpoint of a single/double join is changed.
            for stroke in [1,2]:
                for col,side in [(v,'rightpos'),(v+1,'leftpos')]:
                    if 1<=col<=columns:
                        result.append(f',hline{{{h+1}}}={{{stroke}}}{{{col}}}{{{hw}pt,solid,{side}={vpos}}}')
                for row,side in [(h,'belowpos'),(h+1,'abovepos')]:
                    if 1<=row<=rows:
                        result.append(f',vline{{{v+1}}}={{{stroke}}}{{{row}}}{{{vw}pt,solid,{side}={hpos}}}')
    return ''.join(result)


def frame_options(rule):
    validate_rule(rule)
    style=rule.get('style','single');width=rule.get('width_pt',.4)
    if style=='dashed':raise ValueError('Dashed frames require a dedicated path primitive')
    edges=rule.get('edges',['top','bottom','left','right'])
    if len(edges)!=len(set(edges)) or set(edges)-{'top','bottom','left','right'}:
        raise ValueError('Invalid frame edges')
    result=[e+'line='+('true' if e in edges and style!='none' else 'false')for e in ['top','bottom','left','right']]
    if style=='double':
        result+=['innerlinewidth='+str(width)+'pt','outerlinewidth='+str(width)+'pt','middlelinewidth='+str(rule.get('double_gap_pt',1.2))+'pt','middlelinecolor=white']
    else:result+=['linewidth='+str(width)+'pt']
    return ','.join(result)
