"""Public source links, using the already installed principal bindings."""
import html
from public_paths import RENAMED, stem

OFFICIAL_DOWNLOAD = 'https://www.jlpt.jp/samples/sampleindex.html'
OFFICIAL_SAMPLE_DOWNLOAD = 'https://www.jlpt.jp/samples/sample09.html'
PUBLIC_CLASSES = {'workbook', 'base', 'sample'}

# Printed labels absent from the 2012 contained-set publication mappings in
# preprocess/{level}/{unit}/publication_mapping_{unit}.json.
OFFICIAL_OMISSIONS = {
    'N1_set_2011_2012': 'Q48, 69, 70',
    'N3_set_2011_2012': 'Vocabulary Q19, 23',
}


def official_url(unit):
    if unit in RENAMED or unit in OFFICIAL_OMISSIONS:
        return OFFICIAL_DOWNLOAD
    if unit in {f'N{n}_sample_2009' for n in range(1, 6)}:
        return OFFICIAL_SAMPLE_DOWNLOAD
    return None


def official_warning(unit):
    missing = OFFICIAL_OMISSIONS.get(unit)
    return ('. WARNING: Official Download does not have ' + missing
            + '. You can find the principal source in Github additional-assets/') if missing else ''


def official_link(unit, css_class=''):
    url = official_url(unit)
    if not url:
        return ''
    cls = f' class="{css_class}"' if css_class else ''
    return f'<a{cls} href="{url}" target="_blank" rel="noopener">Official Download ↗</a>'


def principal_target(row, assets):
    if row['public_class'] not in PUBLIC_CLASSES:
        return None
    pdfs = [a for a in assets[row['unit']] if a['path'].lower().endswith('.pdf')]
    if not pdfs:
        raise ValueError('Public principal has no PDF: ' + row['unit'])
    if len(pdfs) == 1:
        return pdfs[0]['path']
    return 'sources/' + stem(row['unit']) + '.html'


def source_pages(catalog, assets, themes, shell, write):
    labels = {'vocabulary_questions': 'Vocabulary', 'grammar_questions': 'Grammar',
              'reading_questions': 'Reading', 'principal': 'Principal source'}
    for row in catalog:
        target = principal_target(row, assets)
        if not target or not target.startswith('sources/'):
            continue
        title = row['level'] + ' · ' + row['sitting']
        links = ''.join('<li><a href="../' + html.escape(a['path'], quote=True)
                        + '" target="_blank" rel="noopener">'
                        + html.escape(labels.get(a['role'], a['role'].replace('_', ' ').title()))
                        + ' PDF ↗</a></li>' for a in assets[row['unit']]
                        if a['path'].lower().endswith('.pdf'))
        body = ('<main id="content" class="source-page"><a class="back-link" href="../levels/'
                + row['catalog_level'] + '.html">← ' + row['level'] + ' papers</a><h1>'
                + html.escape(title) + '</h1><h2>Principal source PDFs</h2>'
                + '<p>This workbook has separate written-section PDFs.</p><ul>' + links
                + '</ul><p>' + official_link(row['unit']) + '</p></main>')
        write(target, shell('Principal sources · ' + title, body, themes, '../', catalog=True))
