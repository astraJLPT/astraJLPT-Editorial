"""Observed early Japanese-only cover with writing specimen and identity grids."""
from pathlib import Path
from PIL import Image
from model import ROOT,BASE,file_hash


def validate_printed(cover):
    p=cover['printed'];grid=p.get('identity_fields',{});spec=p.get('digit_specimen',{})
    bilingual=p['family']=='bilingual_five_instruction'
    observed1990=(cover['unit']=='N4_1990'and p['year_text']=='1990'and p['level_number']==4 and bilingual)
    registration='Examinee\nRegistration No'+(''if observed1990 else'.')
    if (p['family']not in {'japanese_five_instruction','bilingual_five_instruction'} or (p['year_text']!='1991'and not observed1990)
            or p['level_number']not in ([3,4]if bilingual else[1,2])
            or cover['historical_level']!=str(p['level_number'])+'級'
            or cover['style_id']!=f'{p["family"]}_L{p["level_number"]}'
            or not p.get('english_field_labels_observed') or p['english_booklet_title']is not None
            or grid!={'registration_digit_cells':7,'name_character_cells':20,
                      'name_rows':[{'japanese':'姓','english':'Family Name'},
                                   {'japanese':'名','english':'Given Name(s)'}]}
            or p['labels'].get('registration_english')!=registration
            or p['labels'].get('name_english')!='Name'):
        raise ValueError('Early cover requires its directly observed identity grid and labels')
    from historical_booklets import text
    adverb='はっきり'+('と'if p['level_number']in [2,3,4] else'')
    name='なまえ'if p['level_number']==4 and cover['booklet_id']=='vocabulary'and not observed1990 else'名前'
    if observed1990:
        carry='もってかえる'if cover['booklet_id']=='vocabulary'else'持って帰る'
        if text(p['instructions'][1]['japanese'])!='この問題用紙を'+carry+'ことはできません。':
            raise ValueError('1990 cover must preserve its observed carrying instruction')
    if (text(p['instructions'][2]['japanese'])!=f'受験番号は、下のような数字で{adverb}書いてください。'
            or text(p['instructions'][3]['japanese'])!=f'問題用紙と解答用紙の、受験番号・{name}は、受験票と同じように{adverb}書いてください。'
            or text(p['instructions'][4]['japanese'])!=f'この問題用紙は、全部で{p["source_body_pages"]}ページあります。'):
        raise ValueError('Early writing specimen must follow its exact source instruction')
    if set(spec)!={'path','sha256','width','height','digits'}or spec['digits']!='1234567890':
        raise ValueError('Invalid cover numeral-writing specimen')
    from package_paths import resource
    path=resource(spec['path']);allowed=ROOT/'editorial-json'/cover['unit'][:2]/cover['unit']/'assets'
    if not path.is_relative_to(allowed):raise ValueError('Cover specimen outside its owner assets')
    current=ROOT
    for part in path.relative_to(ROOT).parts:
        if part in ['..','.']or part.lower()=='zdiamond_scans':raise ValueError('Unsafe cover specimen path')
        current=current/part
        if current.is_symlink()or current.is_junction():raise ValueError('Linked cover specimen path')
    if not path.is_relative_to(allowed)or file_hash(path)!=spec['sha256']:
        raise ValueError('Writing specimen must be an exact owner asset')
    with Image.open(path)as im:
        binary=(im.mode=='1' or (im.mode=='L' and set(im.tobytes())<={0,255}))
        if not binary or list(im.size)!=[spec['width'],spec['height']]:
            raise ValueError('Writing specimen pixels or dimensions changed')
    return path


def generate(cover,profile,common,data,folio_extent,tex_path):
    from historical_cover_native import rich
    from historical_cover_reconstruction import digit_tex
    from cover_native import escape
    asset=validate_printed(cover);p=cover['printed'];s=profile['styles'][cover['style_id']]['type'];g=profile['styles'][cover['style_id']]['geometry'];labels=p['labels'];bilingual=p['family']=='bilingual_five_instruction'
    family=profile['styles'][cover['style_id']]
    overrides=family.get('year_type_overrides',{}).get(p['year_text'],{})
    if set(overrides)-{'english_font','notes_font'}:raise ValueError('Invalid early-cover year typography override')
    s={**s,**overrides}
    english_font=s.get('english_font','OldCoverEnglishBold');notes_font=s.get('notes_font','LatinBold')
    if english_font not in ['Latin','OldCoverEnglishBold']or notes_font not in ['LatinSans','LatinBold']:
        raise ValueError('Invalid early-cover English font role')
    pre=[r'\def\CoverMarkOpacity{'+str(common['mark']['opacity'])+'}',r'\def\CoverMarkSize{'+str(common['mark']['size_bp'])+'}',
         r'\documentclass[a4paper]{article}',r'\input{'+(BASE/'tex/cover-components.tex').as_posix()+'}',
         r'\usepackage{luatexja-ruby,tikz}',r'\setlength\parindent{0pt}\setlength\parskip{0pt}',
         r'\newfontfamily\OldCoverDigit[Path={\AstraRoot/pdf-render/fonts/}]{1fd6d7dddab7-A-OTF-GothicMB101Pr6N-DeBold.otf}',
         r'\newjfontfamily\OldCoverGothic[Path={\AstraRoot/pdf-render/fonts/},YokoFeatures={JFM=mono}]{cf33366000ee-A-OTF-GothicMB101Pr6N-Bold.otf}',
         r'\newcommand\OldCoverHeavy{\LatinBold\OldCoverGothic}',r'\newsavebox\OldCoverNotice',r'\begin{document}\null']
    if bilingual:
        pre.insert(-1,r'\newfontfamily\OldCoverEnglishBold[Path={\AstraRoot/pdf-render/fonts/}]{621b4a765fef-timesbd.ttf}')
        pre.insert(-1,r'\ltjsetruby{size=.48,intergap=0}')
    put=[]
    def line(x,y,t,size,font='Mincho',align='lb',ruby_size=.48):
        ruby_setup=r'\ltjsetruby{size='+str(ruby_size)+'}'if bilingual else''
        put.append(r'\put('+str(x)+',-'+str(y)+r'){\makebox(0,0)['+align+']{{\\'+font+r'\fontsize{'+str(size)+'bp}{'+str(size)+r'bp}\selectfont '+ruby_setup+t+'}}}')
    def rect(x,y,w,h,rule=.5):put.append(f'\\RuleRect{{{x}}}{{{y}}}{{{w}}}{{{h}}}{{{rule}}}')
    def rule(x,y,xx,yy,width=.4):put.append(f'\\RuleLine{{{x}}}{{{y}}}{{{xx}}}{{{yy}}}{{{width}}}')
    line(g['label_right_mm'],g['label_y_mm'],rich(labels['upper_right']),s['upper_label_bp'],'OldCoverHeavy','rb',.24)
    year=(r'\hspace{'+str(s['year_tracking_em'])+'em}').join(p['year_text'])
    line(105,g['year_y_mm'],'('+year+')',s['year_bp'],'Date','b')
    line(105,g['level_y_mm'],digit_tex(p['level_number'],s['level_bp']*s['level_digit_scale'])+r'\hspace{'+str(s['level_gap_em'])+'em}'+rich(labels['level_unit']),s['level_bp'],'OldCoverHeavy','b',.2)
    line(105,g['title_y_mm'],rich(labels['title'],s['title_dot_width_em']),s['title_bp'],'OldCoverHeavy','b',.2)
    line(105,g['time_y_mm'],'('+str(p['score'])+rich(labels['score_unit'])+r'\hspace{'+str(s['time_gap_em'])+'em}'+str(p['minutes'])+rich(labels['minute_unit'])+')',s['time_bp'],'OldCoverHeavy','b',.28)
    x,y,w,h=g['frame_mm'];rect(x,y,w,h,.45)
    line(105,y+g['notice_heading_offset_mm'],rich(labels['notice'])if bilingual else r'注\hspace{1.6em}意',s['notice_heading_bp'],'OldCoverHeavy','b')
    if bilingual:line(105,y+g['notes_offset_mm'],'Note',s['notes_bp'],notes_font,'b')
    body=[]
    for row in p['instructions']:
        body.append(r'\hangindent=1em\hangafter=1\noindent\makebox[2em][l]{'+str(row['number'])+'.}'+rich(row['japanese'])+r'\par')
        if bilingual:
            body.append((r'\nobreak{\%s\fontsize{'%english_font)+str(s['english_bp'])+'bp}{'+str(s['english_baseline_bp'])+r'bp}\selectfont\leftskip=2em\noindent '+rich(row['english'])+r'\par}')
        if row['number']==3:
            body.append(r'\nobreak\vspace{4bp}\noindent\hspace*{2em}\includegraphics[width='+str(g['digit_specimen_width_mm'])+'mm]{'+asset.as_posix()+r'}\par\nobreak')
        if row['number']<5:body.append(r'\vspace{'+str(s['rule_gap_bp'])+'bp}')
    by=y+g['body_offset_mm'];available=y+h-by-3
    pre.append(r'\sbox\OldCoverNotice{\begin{minipage}[t]{'+str(w-2*g['body_inset_mm'])+r'mm}\vspace{0pt}\Mincho\fontsize{'+str(s['notice_bp'])+'bp}{'+str(s['notice_baseline_bp'])+r'bp}\selectfont '+'\n'.join(body)+r'\par\end{minipage}}')
    pre.append(r'\typeout{Old1991cover notice height: \the\dimexpr\ht\OldCoverNotice+\dp\OldCoverNotice\relax; allowed='+str(available)+'mm}')
    pre.append(r'\ifdim\dimexpr\ht\OldCoverNotice+\dp\OldCoverNotice\relax>'+str(available)+r'mm\errmessage{Old1991cover notice exceeds source frame}\fi')
    put.append(r'\put('+str(x+g['body_inset_mm'])+',-'+str(by)+r'){\makebox(0,0)[lt]{\usebox\OldCoverNotice}}')
    gx=g['early_fields_x_mm'];gy=g['registration_y_mm'];gw=g['registration_width_mm'];gh=g['registration_height_mm'];split=g['registration_label_width_mm'];count=p['identity_fields']['registration_digit_cells']
    rect(gx,gy,gw,gh,.65)
    for i in range(count):
        xx=gx+split+(gw-split)*i/count;rule(xx,gy,xx,gy+gh)
    line(gx+2,gy+3.7,rich(labels['registration']),s['field_bp'])
    for j,t in enumerate(labels['registration_english'].split('\n')):line(gx+2,gy+6.6+j*2.6,escape(t),6.6,'Latin')
    ny=g['name_y_mm'];nw=g['name_width_mm'];nh=g['name_height_mm'];main=g['name_label_width_mm'];side=g['name_row_label_width_mm'];cells=p['identity_fields']['name_character_cells'];start=gx+main+side
    rect(gx,ny,nw,nh,.65);rule(gx+main,ny,gx+main,ny+nh);rule(gx+main,ny+nh/2,gx+nw,ny+nh/2)
    for i in range(cells):
        xx=start+(nw-main-side)*i/cells;rule(xx,ny,xx,ny+nh)
    line(gx+main/2,ny+6.2,rich(labels['name']),s['field_bp'],align='b');line(gx+main/2,ny+11.8,escape(labels['name_english']),s['field_english_bp'],'Latin','b')
    for j,row in enumerate(p['identity_fields']['name_rows']):
        yy=ny+j*nh/2;cx=gx+main+side/2;line(cx,yy+3.2,escape(row['japanese']),7.3,align='b');line(cx,yy+6.6,escape(row['english']),s['field_english_bp'],'Latin','b')
    if data['coverage_notes']:raise ValueError('Early cover partial disclosures need an explicitly reviewed layout')
    put.append(r'\EditorialMark');pre.append(r'\AddToShipoutPictureFG*{\AtPageUpperLeft{\setlength{\unitlength}{1mm}'+'\n'+'\n'.join(put)+'\n}}');pre.append(r'\end{document}')
    tex_path.write_text('\n'.join(pre)+'\n',encoding='utf-8');return tex_path
