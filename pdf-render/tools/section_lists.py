"""Opt-in hanging hierarchy for existing unordered lists in bound documents."""
from bs4 import Tag, NavigableString
from model import Projection


def render(conv, root, context, layout):
    if set(layout) != {'list_count', 'item_count', 'levels'} or root.name != 'ul':
        raise ValueError('Section list requires explicit unordered-list structure')
    levels = layout['levels']
    if not isinstance(levels, list) or not 1 <= len(levels) <= 3:
        raise ValueError('Section list requires one to three explicit levels')
    for level in levels:
        if set(level) != {'indent_em', 'item_before_pt'}:
            raise ValueError('Section list requires exact level geometry')
        for key, lo, hi in [('indent_em', .5, 4), ('item_before_pt', 0, 12)]:
            v = level[key]
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not lo <= v <= hi:
                raise ValueError('Invalid section list geometry')
    for name in ['list_count', 'item_count']:
        if type(layout[name]) is not int or layout[name] < 1:
            raise ValueError('Invalid section list count')
    counts = {'lists': 0, 'items': 0, 'depth': 0}

    def plain(n):
        return Projection({'html': str(n)}).text.strip()

    def children(n):
        return [c for c in n.children if not isinstance(c, NavigableString) or c.strip()]

    def visit(node, depth):
        if depth >= len(levels):
            raise ValueError('Undeclared section list depth')
        counts['lists'] += 1
        counts['depth'] = max(counts['depth'], depth + 1)
        items = children(node)
        if not items or any(not isinstance(n, Tag) or n.name != 'li' for n in items):
            raise ValueError('Section unordered list must contain only complete items')
        parts = []
        for item in items:
            counts['items'] += 1
            content = children(item)
            lead, tail = [], []
            for child in content:
                if isinstance(child, Tag) and child.name in ['p', 'ul']:
                    tail.append(child)
                elif tail:
                    raise ValueError('Section list trailing content needs an explicit paragraph')
                else:
                    if isinstance(child, Tag) and (child.name in ['ol', 'li', 'table', 'div', 'section'] or child.find(['p', 'ul', 'ol', 'li', 'table', 'div', 'section'])):
                        raise ValueError('Unsupported section list content')
                    lead.append(child)
            if not ''.join(plain(n) for n in lead):
                raise ValueError('Section list item requires its original inline lead')
            level = levels[depth]
            body = ''.join(conv.node(n, context) for n in lead) + r'\par'
            for child in tail:
                if child.name == 'ul':
                    body += visit(child, depth + 1)
                else:
                    if not plain(child) or child.find(['p', 'ul', 'ol', 'li', 'table', 'div', 'section']):
                        raise ValueError('Section list detail must be one complete inline paragraph')
                    body += r'\noindent ' + ''.join(conv.node(n, context) for n in child.children) + r'\par'
            conv.features.append({'kind': 'layout_symbol', 'text': '・', 'basis': 'unordered HTML list marker'})
            parts.append(r'\par\addvspace{' + str(level['item_before_pt']) + r'pt}{\advance\leftskip by ' +
                         str(level['indent_em']) + r'em\relax\parindent=0pt\noindent\llap{・\hspace{.2em}}' + body + '}')
        return ''.join(parts)

    tex = visit(root, 0)
    if (counts['lists'], counts['items'], counts['depth']) != (layout['list_count'], layout['item_count'], len(levels)):
        raise ValueError('Section list structure changed or has unused levels')
    conv.features.append({'kind': 'observed_section_list', 'list_count': counts['lists'],
                          'item_count': counts['items'], 'levels': levels, 'text': plain(root)})
    return tex
