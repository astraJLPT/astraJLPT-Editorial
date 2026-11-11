"""Native covers from resolved editorial facts and level geometry; no prototype reads."""
from pathlib import Path
import re
BASE=Path(__file__).resolve().parents[1]

def escape(s):
    return ''.join({'\\':r'\textbackslash{}','{':r'\{','}':r'\}','%':r'\%','&':r'\&','#':r'\#','_':r'\_','$':r'\$','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}.get(c,c)for c in s)
def generate(m, family, common, tex_path):
    if m.get('publication',{}).get('kind') in ['sample', 'practice_set']:
        from h28_publication_cover import generate as generate_publication
        return generate_publication(m, common, tex_path)
    if m.get('coverage') == 'partial_available_written':
        return generate_partial(m, common, tex_path)
    if m.get('publication',{}).get('kind') == 'workbook':
        return generate_workbook(m, common, tex_path)
    fam=family['native']
    g=family['geometry']
    # Vector frame is identified by area. All rule coordinates are in PDF bp.
    frame=max([r['rect_pt']for r in fam['rules']if r['kind']=='rect'],key=lambda r:(r[2]-r[0])*(r[3]-r[1]))
    a,b,c,d=frame;left,top,right,bottom=g['frame_mm'];sx=(right-left)/(c-a);sy=(bottom-top)/(d-b)
    def X(x):return left+(x-a)*sx
    fieldsrc=sorted(set(round(r['points'][0][1],2)for r in fam['rules']if r['kind']=='line'and abs(r['points'][0][1]-r['points'][1][1])<.01 and r['points'][0][1]>d))
    fielddst=g['field_line_y_mm']
    def Y(y):
        knots=[(b,top),(d,bottom)]+list(zip(fieldsrc,fielddst))
        for (y0,v0),(y1,v1) in zip(knots,knots[1:]):
            if y0<=y<=y1:return v0+(y-y0)*(v1-v0)/(y1-y0)
        if y<b:return top+(y-b)*25.4/72
        return knots[-1][1]+(y-knots[-1][0])*25.4/72
    def scaleY(y):return sy/(25.4/72)if b<=y<=d else 1
    lines=[]
    def run(x,y,w,size,font,t):
        lines.append('\\Run{%.5f}{%.5f}{%.5f}{%.5f}{%s}{%s}'%(x,y,w,size,font,escape(t)))
    spans=fam['spans']
    if m.get('rendition',{}).get('variant')=='norubi':
        from norubi_covers import spans as norubi_spans
        spans,removed=norubi_spans(fam)
        m['removed_cover_reading_spans']=removed
    for s in spans:
        # Replace row 4 English as one native sentence to preserve word spaces across split source runs.
        if 585<s['y_pt']<598 and (s['text'].isascii() or s['role']=='page_count'):
            if s['text']=='This':
                run(X(s['x_pt']),Y(s['y_pt']),58,9.2,'Latin',f'This question booklet has {m["displayed_body_folios"]} pages.')
            continue
        t=s['text'].replace('{pages}',str(m['displayed_body_folios'])).replace('{minutes}',str(m['minutes'])).replace('{minute_reading}',m['minute_reading'])
        t=re.sub(r'has(\d+)pages\.',r'has \1 pages.',t)
        # Standardize item and field numerals to actual text; retain their native rule boxes separately.
        if s['role']=='page_count' and t.isdigit():t=str(m['displayed_body_folios'])
        run(X(s['x_pt']),Y(s['y_pt']),s['width_pt']*sx,(g['level_cap_height_mm']*72/25.4/.716 if s['text']==m['level'] else s['size_bp']*scaleY(s['y_pt'])),('SansBold' if s['font']=='Heavy' and t.isascii() else s['font']),t)
    for r in fam['rules']:
        if r['kind']=='rect':
            x0,y0,x1,y1=r['rect_pt'];lines.append('\\RuleRect{%.5f}{%.5f}{%.5f}{%.5f}{%.5f}'%(X(x0),Y(y0),X(x1)-X(x0),Y(y1)-Y(y0),r['width_bp']))
        else:
            (x0,y0),(x1,y1)=r['points'];lines.append('\\RuleLine{%.5f}{%.5f}{%.5f}{%.5f}{%.5f}'%(X(x0),Y(y0),X(x1),Y(y1),r['width_bp']))
    datew=88 if m['measurement_family']=='exam_2018_N2'else 58
    run(105-datew/2,47.5,datew,(34 if m['measurement_family']=='exam_2018_N2' else 26),'Date',f'( {" ".join(m["date_label"])} )')
    if m['code']:
        lines.append('\\CodeCircle{14.5}{13.8}{%s}'%m['code'])
    if m['copyright_year']:
        run(18.5,284.7,173,8,'Latin',f'Copyright ©{m["copyright_year"]} The Japan Foundation, and Japan Educational Exchanges and Services. All Rights Reserved.')
        run(18.5,288.3,140,8,'Latin','Any reproduction or representation by any means, in whole or in part, is strictly prohibited.')
    lines.append(r'\EditorialMark')
    p=Path(tex_path)
    p.write_text('\\def\\CoverMarkOpacity{'+str(common['mark']['opacity'])+'}\n'+'\\def\\CoverMarkSize{'+str(common['mark']['size_bp'])+'}\n'+r'\documentclass[a4paper]{article}'+'\n'+r'\input{'+(BASE/'tex/cover-components.tex').as_posix()+'}\n'+r'\begin{document}\null'+'\n'+r'\AddToShipoutPictureFG*{\AtPageUpperLeft{\setlength{\unitlength}{1mm}'+'\n'+'\n'.join(lines)+'\n}}\n'+r'\end{document}'+'\n',encoding='utf-8')
    return p


def generate_workbook(m, common, tex_path):
    """Explicit editorial workbook front; no invented sitting or examination time."""
    publication = m['publication']
    identities = {
        'N1_workbook_2018': ('JLPT_WORKBOOK_2018_N1', 2018, 'N1'),
        'N2_workbook_2018': ('JLPT_WORKBOOK_2018_N2', 2018, 'N2'),
        'N3_workbook_2018': ('JLPT_WORKBOOK_2018_N3', 2018, 'N3'),
        'N2_workbook_2012': ('JLPT_WORKBOOK_2012_N2', 2012, 'N2'),
        'N4_workbook_2012': ('JLPT_WORKBOOK_2012_N4', 2012, 'N4'),
        'N4_workbook_2018': ('JLPT_WORKBOOK_2018_N4', 2018, 'N4'),
        'N5_workbook_2012': ('JLPT_WORKBOOK_2012_N5', 2012, 'N5'),
        'N5_workbook_2018': ('JLPT_WORKBOOK_2018_N5', 2018, 'N5'),
    }
    if (publication['id'], publication['year'], m['level']) != identities.get(m['unit']):
        raise ValueError('Workbook cover requires the exact admitted registry identity')
    expected_title = 'Official Practice Workbook' + (' Vol. 2' if publication['year'] == 2018 else '')
    if publication['title'] != expected_title:
        raise ValueError('Workbook title differs from its registered volume')
    if m['minutes'] is not None or m.get('date_label') is not None:
        raise ValueError('Workbook front must not inherit exam timing or sitting')
    titles = {'vocabulary': ('言語知識（文字・語彙）', 'Vocabulary'),
              'language_knowledge': ('言語知識（文法）・読解', 'Grammar and Reading'),
              'combined_written': ('言語知識（文字・語彙・文法）・読解', 'Vocabulary, Grammar and Reading')}
    title, english = titles[m['booklet_id']]
    def run(x,y,w,size,font,text):
        return '\\put(105,-%s){\\makebox(0,0){\\%s\\fontsize{%sbp}{%sbp}\\selectfont %s}}' % (y,font,size,size,escape(text))
    lines = [run(27,42,156,19,'SansBold','日本語能力試験'),
             run(27,61,156,26,'Heavy','公式問題集'),
             run(27,83,156,18,'Latin',f'{publication["year"]} {publication["title"]}'),
             run(27,108,156,44,'SansBold',m['level']),
             r'\RuleLine{27}{136}{183}{136}{0.7}',
             run(27,154,156,18,'SansBold',title),
             run(27,171,156,15,'Latin',english),
             run(27,202,156,12,'Latin',f'Editorial booklet: {m["displayed_body_folios"]} body pages'),
             run(27,221,156,11,'Latin',f'Native editorial rendition of the verified {publication["year"]} workbook.'),
             run(27,233,156,11,'Latin','Page count refers to this edition.'), r'\EditorialMark']
    p=Path(tex_path)
    p.write_text('\\def\\CoverMarkOpacity{'+str(common['mark']['opacity'])+'}\n'+'\\def\\CoverMarkSize{'+str(common['mark']['size_bp'])+'}\n'+r'\documentclass[a4paper]{article}'+'\n'+r'\input{'+(BASE/'tex/cover-components.tex').as_posix()+'}\n'+r'\begin{document}\null'+'\n'+r'\AddToShipoutPictureFG*{\AtPageUpperLeft{\setlength{\unitlength}{1mm}'+'\n'+'\n'.join(lines)+'\n}}\n'+r'\end{document}'+'\n',encoding='utf-8')
    return p


def generate_partial(m, common, tex_path):
    """An explicit untimed front for the one authorized incomplete recovery."""
    expected = {'vocabulary': 6, 'language_knowledge': 14}
    if (m['unit'] != 'N3_07_2026' or m['level'] != 'N3'
            or m['booklet_id'] not in expected or m['recovered_questions'] != expected[m['booklet_id']]
            or m['minutes'] is not None or not m.get('partial_warning') or m.get('publication')):
        raise ValueError('Partial front requires the exact untimed N3 recovery')
    vocabulary = m['booklet_id'] == 'vocabulary'
    title = '言語知識（文字・語彙）' if vocabulary else '言語知識（文法）'
    english = 'Vocabulary: 6 recovered questions' if vocabulary else 'Grammar: 14 recovered questions'
    def run(y, size, font, text):
        return '\\put(105,-%s){\\makebox(0,0){\\%s\\fontsize{%sbp}{%sbp}\\selectfont %s}}' % (y, font, size, size, escape(text))
    lines = [run(40, 19, 'SansBold', '日本語能力試験 N3'),
             run(64, 23, 'Heavy', '部分復元・練習用'),
             run(86, 21, 'SansBold', 'PARTIAL PRACTICE'),
             run(106, 15, 'Latin', 'July 2026 · available recovered content'),
             r'\RuleLine{27}{127}{183}{127}{0.7}',
             run(146, 18, 'SansBold', title), run(165, 14, 'Latin', english),
             run(188, 12, 'SansBold', '問題番号の欠番は原資料の復元状況によるものです。'),
             run(205, 11, 'Latin', 'Original numbering gaps are preserved.'),
             run(219, 11, 'Latin', 'No recovered reading passages. This is not a complete paper.'),
             run(233, 11, 'Latin', 'One recovered worked example is included in Grammar.'),
             run(251, 11, 'Latin', f'This editorial booklet: {m["displayed_body_folios"]} body page' + ('s' if m['displayed_body_folios'] != 1 else '')),
             r'\EditorialMark']
    p = Path(tex_path)
    p.write_text('\\def\\CoverMarkOpacity{' + str(common['mark']['opacity']) + '}\n'
        + '\\def\\CoverMarkSize{' + str(common['mark']['size_bp']) + '}\n'
        + r'\documentclass[a4paper]{article}' + '\n'
        + r'\input{' + (BASE / 'tex/cover-components.tex').as_posix() + '}\n'
        + r'\begin{document}\null' + '\n'
        + r'\AddToShipoutPictureFG*{\AtPageUpperLeft{\setlength{\unitlength}{1mm}' + '\n'
        + '\n'.join(lines) + '\n}}\n' + r'\end{document}' + '\n', encoding='utf-8')
    return p
