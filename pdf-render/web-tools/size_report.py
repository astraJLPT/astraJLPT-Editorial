"""Deterministic on-disk size accounting for generated website resources."""
import collections
import hashlib
import re
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'pdf-render/tools'))
from public_paths import html_path,site_pdf

ROOTS = ('assets', 'data', 'levels', 'papers', 'papers-norubi', 'reviews', 'sources')
EXCLUDED = {'data/size-report.json', 'build-manifest.json'}


def category(name):
    for prefix, label in [('assets/fonts/', 'fonts'), ('assets/pdfs/', 'released_pdfs'),('assets/pdfs-norubi/','norubi_pdfs'),
                          ('assets/principals/', 'principal_sources'), ('assets/covers/', 'covers'),
                          ('assets/', 'other_shared_assets'), ('papers/', 'paper_html'),('papers-norubi/','norubi_html'),
                          ('reviews/', 'review_html'), ('data/', 'metadata')]:
        if name.startswith(prefix):
            return label
    return 'catalog_html'


def measure_site(site, generated, units, budgets):
    for key in ('max_paper_html_bytes', 'max_shared_assets_bytes', 'max_runtime_bundle_bytes'):
        if type(budgets.get(key)) is not int or budgets[key] <= 0:
            raise ValueError('Invalid size budget: ' + key)
    expected = set(generated) - EXCLUDED
    files = [site / 'index.html'] + [p for root in ROOTS for p in (site / root).rglob('*') if p.is_file()]
    actual = {p.relative_to(site).as_posix(): p.stat().st_size for p in files
              if p.relative_to(site).as_posix() not in EXCLUDED}
    groups = collections.defaultdict(lambda: {'files': 0, 'bytes': 0})
    failures = []
    for name, size in sorted(actual.items()):
        group = groups[category(name)]
        group['files'] += 1
        group['bytes'] += size
        if name.endswith('.html'):
            html = (site / name).read_text(encoding='utf-8')
            if re.search(r'data:(?:font/|application/(?:font|x-font))|@font-face', html):
                failures.append('Embedded font in normal website page: ' + name)
            if 'id="theme-data" type="application/json"' in html:
                failures.append('Repeated inline theme data: ' + name)
    missing = sorted(expected - actual.keys())
    unlisted = sorted(actual.keys() - expected)
    if missing:
        failures.append('Missing generated files: ' + ', '.join(missing))
    if unlisted:
        failures.append('Unlisted runtime files (inspect; do not delete automatically): ' + ', '.join(unlisted))
    papers = {}
    bindings_path=site/'data/principal-assets.json'
    principal_bindings=json.loads(bindings_path.read_text(encoding='utf8')) if bindings_path.is_file() else {}
    for unit in units:
        name = html_path(unit)
        size = actual.get(name, 0)
        if size > budgets['max_paper_html_bytes']:
            failures.append(name + ' exceeds the paper HTML budget')
        no_name=html_path(unit,'norubi')
        if actual.get(no_name,0)>budgets['max_paper_html_bytes']:failures.append(no_name+' exceeds the paper HTML budget')
        papers[unit] = {'html_bytes': size,
                       'norubi_html_bytes':actual.get(no_name,0),'norubi_pdf_bytes':actual.get(site_pdf(unit,'norubi'),0),
                       'released_pdf_bytes': actual.get(site_pdf(unit), 0),
                       'principal_source_bytes': sum(actual.get(p,0) for p in {r['path'] for r in principal_bindings[unit]}) if unit in principal_bindings else sum(v for n, v in actual.items() if n.startswith(('assets/principals/' + unit + '.', 'assets/principals/' + unit + '-'))),
                       'principal_assets': principal_bindings.get(unit,[]),
                       'review_html_bytes': actual.get('reviews/' + unit + '.html', 0)}
    shared = groups['fonts']['bytes'] + groups['other_shared_assets']['bytes']
    total = sum(actual.values())
    hashes=collections.defaultdict(list)
    for name in actual:
        hashes[hashlib.sha256((site/name).read_bytes()).hexdigest()].append(name)
    duplicates=[]
    for digest,names in sorted(hashes.items()):
        if len(names)<2:continue
        names=sorted(names);duplicates.append({'sha256':digest,'files':names,'repeated_bytes':sum(actual[n] for n in names[1:])})
        if any(category(n) in ('fonts','other_shared_assets') for n in names):
            failures.append('Duplicate shared resource bytes: '+', '.join(names))
    if shared > budgets['max_shared_assets_bytes']:
        failures.append('Shared assets exceed their size budget')
    if total > budgets['max_runtime_bundle_bytes']:
        failures.append('Runtime bundle exceeds its size budget')
    return {'format': 'astra-size-report-v1', 'scope': list(units),
            'accounting': 'Logical bytes of all runtime files, including retained files. Excludes this report and build-manifest.json; excludes source, vendor, tools, work and Git history.',
            'total_bytes': total, 'shared_asset_bytes': shared,
            'groups': dict(sorted(groups.items())), 'papers': papers,
            'duplicate_resources':duplicates,'duplicate_bytes':sum(g['repeated_bytes'] for g in duplicates),
            'duplication_policy':'Shared font, stylesheet, script and artwork byte duplicates fail. Unit-bound PDF/principal/metadata aliases, if any, remain listed and count fully against the budget; no files are deleted automatically.',
            'files': dict(sorted(actual.items())), 'budgets': budgets,
            'missing_files': missing, 'unlisted_files': unlisted, 'failures': failures}
