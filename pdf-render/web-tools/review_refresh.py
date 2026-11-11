"""Refresh current case registers while retaining the installed review shell/history."""
from collections import Counter
import json
import re

from bs4 import BeautifulSoup


def prepare(model, web):
    from review_sources import bundle
    unit = model['unit']
    root = web.HUB / 'editorial-json' / unit[:2] / unit
    rows = {kind: [json.loads(line) for line in
                   (root / f'{kind}_{unit}.jsonl').read_text(encoding='utf-8-sig').splitlines()
                   if line.strip()]
            for kind in ('unresolved_cases', 'principal_differences')}
    principal, links = bundle(model, web.HUB, web.copy, web.sha)
    content, mapping = web.review_registers(
        model, rows, '../' + principal, lambda value: web.review_markup(value, model), links)
    return {'content': content, 'mapping': mapping,
            'counts': {kind: len(values) for kind, values in rows.items()},
            'statuses': Counter(row['status'] for row in rows['unresolved_cases'])}


def reader(soup, unit, review, safe_json):
    paper = soup.select_one('.paper.editorial')
    for note in paper.select('a.developer-note'):
        note.decompose()
    for item, anchor in review['mapping'].items():
        target = paper.find(id=item) if item else None
        if target is not None:
            note = soup.new_tag('a', href=f'../reviews/{unit}.html#{anchor}')
            note['class'] = ['developer-only', 'developer-note']
            note.string = 'Cases & principal differences →'
            target.append(note)
    node = soup.select_one('#page-data')
    data = json.loads(node.get_text())
    data['paper']['case_counts'] = review['counts']
    node.string = safe_json(data)


def page(soup, review):
    content = soup.select_one('.review-content')
    if content is None:
        raise ValueError('Installed review page lacks its content shell')
    summary = next((p for p in content.find_all('p', recursive=False)
                    if p.get_text().startswith('Uncertainty index:')), None)
    if summary is None:
        raise ValueError('Installed review page lacks its summary')
    # This index assesses the original source. It is not derived from case counts.
    counts, statuses = review['counts'], review['statuses']
    value = re.sub(r' · \d+ differences · \d+ unresolved · \d+ provisional fixes',
                   f' · {counts["principal_differences"]} differences'
                   f' · {statuses["unresolved"]} unresolved'
                   f' · {statuses["provisional_fix"]} provisional fixes', str(summary))
    summary.replace_with(BeautifulSoup(value, 'html.parser').p)
    for node in content.select('.review-controls, #review-count, .review-group'):
        node.decompose()
    fresh = BeautifulSoup(review['content'], 'html.parser')
    for node in list(fresh.contents):
        content.append(node.extract())
