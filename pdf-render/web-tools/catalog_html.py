"""One catalog presentation with separate modern and old-level groups."""
import html
from collection import CONFIG, HISTORICAL
from public_paths import html_path
from source_links import official_link, official_warning, principal_target

COLLECTION_NOTE='Written components are available, listening is excluded. Partial papers are labelled.'
QUALITY_NOTE=('Ordered with higher quality papers presented first.\n'
              'Principal source PDF available here for good units, also in Github additional-assets/')
OLD_NOTE='The old level label is preserved; it is not a modern N-level equivalence.'

# Full painted frames in the two original 1983 x 793 hanafuda atlases.
# Each level and colour variant has its own bounds; no raster is altered.
CARD_RECTS={
    'dark':[(33,106,366,649),(419,106,370,649),(808,106,369,649),(1196,106,370,649),(1585,106,366,649)],
    'light':[(31,107,373,659),(417,107,375,659),(805,107,376,659),(1194,107,375,659),(1581,107,375,659)],
}

def homepage(catalog):
    art=[]
    for index,n in enumerate([5,4,3,2,1]):
        variables=[]
        for theme,rects in CARD_RECTS.items():
            x,y,w,h=rects[index]
            variables.extend([f'--card-{theme}-ratio:{w}/{h}',
                f'--card-{theme}-size:{1983/w*100:.8f}% {793/h*100:.8f}%',
                f'--card-{theme}-position:{x/(1983-w)*100:.8f}% {y/(793-h)*100:.8f}%'])
        art.append(f'<a class="level-card level-n{n}" href="levels/N{n}.html" aria-label="Choose N{n}"><span class="card-art" style="'+ ';'.join(variables)+f'" role="img" aria-label="N{n} hanafuda"></span><span class="level-card-caption">Explore N{n} <span aria-hidden="true">↗</span></span></a>')
    return ('<main id="content" class="entrance"><div class="entrance-title"><span class="ornament" aria-hidden="true">✧</span><h1>Choose your level.</h1></div><div class="level-grid">'+''.join(art)+'</div><div class="entrance-foot"><span>WRITTEN COLLECTION</span><p>'+COLLECTION_NOTE+'</p></div>'+historical_section(catalog)+'</main>')


def sort_key(row):
    index=row['uncertainty_assessment']
    return (index['evidence_tier'] if index['evidence_tier'] is not None else 5,
            index['concern_points'] if index['concern_points'] is not None else 0,
            -row['year'], -(row['month'] or 0), row['unit'])


def historical_section(catalog, prefix=''):
    links = []
    for n in range(1, 5):
        rows = [c for c in catalog if c['generation'] == HISTORICAL and c['level'] == f'{n}級']
        note = f'{len(rows)} written papers' if rows else 'No available written papers'
        links.append(f'<li><a href="{prefix}levels/old-{n}.html">Old {n}級</a> · {note}</li>')
    return ('<section id="historical" class="historical" hidden><h2>The older chapters</h2>'
            '<p>Written papers from the old test, with separate 1級, 2級, 3級 and 4級 collections. These levels are distinct from modern N1–N5.</p><ul>'
            + ''.join(links) + '</ul></section>')


def percent(part, whole):
    return f'{100 * part / whole:.2f}%' if whole else '—'


def cards(rows, level, principal_assets):
    result = ''
    ordered = sorted((c for c in rows if c['content_kind'] != 'sample'), key=sort_key)
    ordered += sorted((c for c in rows if c['content_kind'] == 'sample'), key=lambda c:c['unit'])
    for rank,c in enumerate(ordered):
        u = c['unit']
        regular=html_path(u);norubi=html_path(u,'norubi')
        title = (c['level'] + ' · ' if c['content_kind'] == 'sample' else '') + c['sitting']
        badge = 'Partial practice' if c['partial'] else 'Modern sample' if c['content_kind'] == 'sample' else 'Old written paper' if c['generation'] == HISTORICAL else 'Written paper'
        uncertainty = c['uncertainty'] if c['uncertainty'] is not None else 'Unassessed'
        ruby = c['ruby']
        target = principal_target(c, principal_assets)
        source_links = official_link(u, 'start-link')
        if target:
            source_links += f'<a class="start-link" href="../{html.escape(target, quote=True)}" target="_blank" rel="noopener">Open principal source ↗</a>'
        diagnostics = (
            '<p class="ruby-diagnostics">'
            f'<span data-ruby-stat="original" title="Original source/editorial ruby groups">rubi: {ruby["original"]:,}</span><br>'
            f'<span data-ruby-stat="restored" title="Added ruby groups in the selected release">restored rubi: {ruby["restored"]:,}</span><br>'
            f'<span data-ruby-stat="kanji-coverage" title="Authored kanji occurrences covered by original or restored ruby / all authored kanji occurrences × 100 (report coverage definition). Image text and generated examples are excluded.">%rubi: {percent(ruby["annotated_kanji"], ruby["kanji"])}</span></p>'
        )
        result += (f'<article class="paper-card" data-rank="{rank}" data-year="{c["year"]}" data-month="{c["month"] or 0}"><a class="paper-cover" href="../{regular}"><img src="../assets/covers/{u}.png" alt="{level} {c["sitting"]} PDF cover"></a>'
                   f'<div class="paper-card-info"><span class="badge">{badge}</span><h2><a href="../{regular}">{title} <span>↗</span></a></h2>'
                   f'<p>{c["questions"]} questions · {", ".join(c["domains"])}{official_warning(u)}</p>'
                   + (f'<p>{c["questions"] - c["gradable_questions"]} without a confirmed answer key</p>' if c['questions'] != c['gradable_questions'] else '')
                   + f'<div class="developer-only"><p>Uncertainty index: {uncertainty}</p>{diagnostics}<a href="../reviews/{u}.html">Cases & principal differences →</a></div>'
                   f'<div class="paper-launch-links"><a class="start-link" href="../{regular}">Start paper →</a>'
                   + source_links +
                   f'<a class="start-link developer-only" href="../{norubi}">Start no rubi paper →</a></div></div></article>')
    return result


def level_pages(catalog, themes, shell, write, principal_assets):
    from practice_pages import SORT
    for group, level, scope in [(f'N{n}', f'N{n}', f'{CONFIG["first_year"]}–{CONFIG["last_year"]} collection') for n in range(1, 6)] + [
            (f'old-{n}', f'Old {n}級', '1990–2009 historical collection') for n in range(1, 5)]:
        rows = [c for c in catalog if c['catalog_level'] == group]
        content = cards(rows, level, principal_assets)
        if not content:
            content = '<div class="empty-state"><h2>No available written papers.</h2><a href="../index.html">Choose another level →</a></div>'
        body = (f'<main id="content" class="catalog"><div class="catalog-navigation"><a class="back-link" href="../index.html">← All levels</a>'+SORT+f'</div><div class="catalog-heading"><div><h1>{level}</h1></div><p>{scope}</p></div>'
                + '<p class="collection-note"><span id="catalog-order-note">Ordered with higher quality papers presented first.</span><br>'+html.escape(OLD_NOTE if group.startswith('old-') else QUALITY_NOTE.split('\n',1)[1]).replace('\n','<br>')+'</p>'
                + f'<div class="paper-grid">{content}</div>' + historical_section(catalog, '../') + '</main>')
        write(f'levels/{group}.html', shell(level + ' papers', body, themes, '../', catalog=True))
