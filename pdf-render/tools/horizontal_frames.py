"""Exact local inner edges for one native horizontal reading rectangle."""
import re
from model import digest


def apply(tex, value, binding):
    keys = {'content_sha256', 'evidence', 'left_pt', 'right_pt', 'top_pt', 'bottom_pt'}
    if not keys <= set(binding) or set(binding) - keys - {'pins'} or not binding['evidence']:
        raise ValueError('Horizontal frame requires an exact content/source/edge binding')
    if digest(value) != binding['content_sha256']:
        raise ValueError('Stale horizontal frame geometry')
    geometry = {k: binding[k] for k in ['left_pt', 'right_pt', 'top_pt', 'bottom_pt']}
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not 0 <= v <= 40
           for v in geometry.values()):
        raise ValueError('Invalid horizontal frame edge')
    begin, end = r'\begin{NoticeFrame}', r'\end{NoticeFrame}'
    if tex.count(begin) != 1 or tex.count(end) != 1 or tex.index(begin) > tex.index(end):
        raise ValueError('Horizontal geometry requires one complete reading rectangle')
    if re.search(re.escape(begin) + r'\s*\[', tex):
        raise ValueError('Horizontal geometry conflicts with existing frame options')
    if 'pins' in binding:
        from notice_pins import decorate
        pins = binding['pins']
        if len(set(geometry.values())) != 1:
            raise ValueError('Horizontal pinned notice requires equal native frame padding')
        pad = geometry['left_pt']
        # A pin and its stroke must stay inside the reserved empty corners.
        frame = decorate('', pins)
        if pad < pins['inset_pt'] + pins['radius_pdf_pt'] + 2:
            raise ValueError('Horizontal pinned notice lacks corner clearance')
        prefix, _, remainder = tex.partition(begin)
        body, _, suffix = remainder.partition(end)
        frame = decorate(r'\PinnedNotice{' + str(pad) + '}{' + body + '}', pins)
        return prefix + frame + suffix, {**geometry, 'pins': pins}
    options = ','.join(option + '=' + str(geometry[key]) + 'pt' for key, option in [
        ('left_pt', 'innerleftmargin'), ('right_pt', 'innerrightmargin'),
        ('top_pt', 'innertopmargin'), ('bottom_pt', 'innerbottommargin')])
    return tex.replace(begin, begin + '[' + options + ']', 1), geometry
