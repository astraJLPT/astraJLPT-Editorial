"""1999-family covers for admitted missing fronts, with explicit inferred provenance."""
import copy
from model import BASE,ROOT,read,file_hash

CONFIG=BASE/'config/historical-cover-reconstruction.json'


def resolve(cover,data,folio_extent):
    if cover['status']!='unavailable':return cover,None
    config=read(CONFIG)
    row=config['levels'][data['historical_level']]
    control=row['booklets'][cover['booklet_id']]
    source=ROOT/control['source']['source_path']
    from release_contract import verify_source
    verify_source(control['source']['source_path'],control['source']['source_sha256'])
    p=copy.deepcopy(control['printed'])
    p.update(year_text=f"{data['year']}-{data['month']:02}",level_number=int(data['historical_level'][0]),
             family=row.get('family','four_instruction'),english_booklet_title=None,notice_heading_observed=True,
             source_body_pages=None)
    p['instructions']=copy.deepcopy(control['instructions'])
    if p['family']=='bilingual_four_instruction':
        if data['historical_level']!='3級':raise ValueError('Unreviewed bilingual reconstruction control')
        p['instructions'].append(dict(number=4,japanese=dict(html=f'この<ruby>問題用紙<rt>もんだいようし</rt></ruby>は、<ruby>全部<rt>ぜんぶ</rt></ruby>で{folio_extent}ページあります。'),
                                     english=dict(html=f'This question booklet contains {folio_extent} pages.')))
    else:
        p['instructions'].append(dict(number=4,japanese=dict(html=f'この問題用紙は、全部で{folio_extent}ページあります。'),english=None))
    result={**cover,'status':'editorial_reconstructed','style_id':row['style_id'],'printed':p}
    provenance=dict(status='inferred',design='1999 four-instruction cover family',
        source_cover_available=False,source_control=control['source'],
        original_source_body_page_count=None,printed_page_count=folio_extent,
        page_count_basis='actual generated body extent; no missing original count invented',
        sitting_basis='existing admitted owner identity',
        timing_score_basis='same-old-level UARS control; inferred for this sitting, not newly authenticated',
        instructions_basis='first three instructions borrowed from stated same-level control; fourth describes this rendered booklet',
        config=dict(path=CONFIG.relative_to(ROOT).as_posix(),sha256=file_hash(CONFIG)))
    return result,provenance


def digit_tex(number,size):
    """Cover-only visible geometry. Native outlines keep textual ActualText."""
    height=round(size*.72,4)
    if number==1:
        path=r'\fill(0,.82)--(.26,.82)--(.26,0)--(.45,0)--(.45,1)--(0,1)--cycle;'
        outline=r'\begin{tikzpicture}[x=1pt,y=1pt,baseline=0pt]'+path+r'\end{tikzpicture}'
        picture=r'\makebox['+str(round(size*.55,4))+r'bp][c]{\resizebox{!}{'+str(height)+'bp}{'+outline+'}}'
    elif number==2:
        # Broad flat bowl, shallow middle, squared lower stem: observed S96 45/62.
        path=(r'\fill(0,0)--(.94,0)--(.94,.17)--(.19,.17)--(.19,.25)'
              r'..controls(.19,.39)and(.34,.40)..(.54,.41)'
              r'..controls(.84,.42)and(.94,.49)..(.94,.70)'
              r'..controls(.94,.94)and(.84,1)..(.62,1)--(.31,1)'
              r'..controls(.09,1)and(0,.91)..(0,.69)--(.19,.69)'
              r'..controls(.19,.80)and(.23,.83)..(.36,.83)--(.60,.83)'
              r'..controls(.72,.83)and(.75,.80)..(.75,.70)'
              r'..controls(.75,.60)and(.69,.59)..(.50,.58)'
              r'..controls(.14,.56)and(0,.49)..(0,.25)--cycle;')
        picture=r'\resizebox{!}{'+str(height)+r'bp}{\begin{tikzpicture}[x=1pt,y=1pt,baseline=0pt]'+path+r'\end{tikzpicture}}'
    elif number==3:
        return r'\resizebox{!}{'+str(height)+r'bp}{{\OldCoverDigit\fontsize{'+str(size)+'bp}{'+str(size)+r'bp}\selectfont 3}}'
    else:return r'{\fontsize{'+str(size)+'bp}{'+str(size)+r'bp}\selectfont '+str(number)+'}'
    return r'\pdfextension literal direct{/Span << /ActualText <FEFF003'+str(number)+r'> >> BDC}'+picture+r'\pdfextension literal direct{EMC}'
