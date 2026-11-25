"""One attached-ribbon primitive for notice titles and bound document lines."""


def render(conv, text, bar, align, size, padding, slant=0, line_index=0):
    if bar['edge'] != align or align not in ['left', 'right']:
        raise ValueError('Attached ribbon must meet its aligned frame edge')
    from document_rules import rule_tex
    rule_tex({'width_pt': bar['thickness_pt'], 'gray': bar['gray'], 'pattern': 'solid'})
    family = getattr(conv, 'notice_title_ribbon_overhang_em', 1.4)
    if isinstance(family, bool) or not isinstance(family, (int, float)) or not .5 <= family <= 3:
        raise ValueError('Invalid title ribbon family default')
    overhang = bar.get('inner_overhang_pt', round(size * family, 3))
    if isinstance(overhang, bool) or not isinstance(overhang, (int, float)) or not 0 <= overhang <= 60:
        raise ValueError('Invalid title ribbon overhang')
    if not 0 <= bar['gap_pt'] <= 12:
        raise ValueError('Invalid ribbon text clearance')
    command = r'\AttachedTitleLeft' if align == 'left' else r'\AttachedTitleRight'
    if overhang:
        command += '[' + str(overhang) + ']'
    conv.features.append({'kind': 'attached_title_bar', 'line_index': line_index,
        'edge': align, 'gray': bar['gray'], 'thickness_pt': bar['thickness_pt'],
        'inner_overhang_pt': overhang, 'title_font_pt': size,
        'overhang_owner': 'explicit_local' if 'inner_overhang_pt' in bar else 'notice_title_ribbon_overhang_em',
        'family_default_em': family, 'line_slant': slant})
    return command + '{' + text + '}{' + str(padding) + '}{' + str(bar['thickness_pt']) + '}{' + str(bar['gray']) + '}{' + str(bar['gap_pt']) + '}'
