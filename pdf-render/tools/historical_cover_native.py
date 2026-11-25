"""Source-transcribed and explicitly inferred Old covers with native geometry."""
import json
from bs4 import BeautifulSoup,NavigableString
from model import BASE
from cover_native import escape

def rich(value, title_dot_width_em=None, centered_ruby=False):
    soup=BeautifulSoup(value['html'],'html.parser')
    def node(n):
        if isinstance(n,NavigableString):
            text=escape(str(n))
            if title_dot_width_em is not None:
                text=text.replace('・',r'\makebox['+str(title_dot_width_em)+r'em][c]{・}')
            return text
        if n.name=='ruby':
            rt=n.find_all('rt',recursive=False)
            if len(rt)!=1 or n.find('rp'):raise ValueError('Cover ruby requires one explicit reading')
            base=''.join(node(c)for c in n.children if c is not rt[0])
            return (r'\ruby[stretchruby=101,maxmargin=1]{'if centered_ruby else r'\ruby{')+base+'}{'+escape(rt[0].get_text())+'}'
        if n.name=='span'and n.attrs=={'data-cover-answer-number':'true'}and n.get_text()in {'1','2','3'}:
            return r'\CoverAnswerNumber{'+n.get_text()+'}'
        raise ValueError('Unrecognized cover rich-text node: '+str(n))
    return ''.join(node(c)for c in soup.children)

def generate(cover,profile,common,data,folio_extent,tex_path):
    if common['mark']['text']!='astraJLPT Editorial':raise ValueError('Unexpected editorial watermark')
    if cover.get('printed',{}).get('family')in {'japanese_five_instruction','bilingual_five_instruction'}:
        from historical_cover_1991 import generate as generate_early
        return generate_early(cover,profile,common,data,folio_extent,tex_path)
    family=profile['styles'][cover['style_id']]
    pre=[r'\def\CoverMarkOpacity{'+str(common['mark']['opacity'])+'}',
         r'\def\CoverMarkSize{'+str(common['mark']['size_bp'])+'}',
         r'\documentclass[a4paper]{article}',r'\input{'+(BASE/'tex/cover-components.tex').as_posix()+'}',
         r'\usepackage{luatexja-ruby}',r'\setlength\parindent{0pt}\setlength\parskip{0pt}',
         r'\usepackage{tikz}',
         r'\newfontfamily\OldCoverDigit[Path={\AstraRoot/pdf-render/fonts/}]{1fd6d7dddab7-A-OTF-GothicMB101Pr6N-DeBold.otf}',
         r'\newjfontfamily\OldCoverGothic[Path={\AstraRoot/pdf-render/fonts/},YokoFeatures={JFM=mono}]{cf33366000ee-A-OTF-GothicMB101Pr6N-Bold.otf}',
         r'\newjfontfamily\OldCoverMedium[Path={\AstraRoot/pdf-render/fonts/},YokoFeatures={JFM=mono}]{b338caa746da-1738155110_A-OTF-RyuminPr5-Medium.otf}',
         r'\newfontfamily\OldCoverEnglishBold[Path={\AstraRoot/pdf-render/fonts/}]{621b4a765fef-timesbd.ttf}',
         r'\newcommand\OldCoverHeavy{\LatinBold\OldCoverGothic}',
         r'\newcommand\CoverAnswerNumber[1]{{\setlength\fboxsep{.05em}\setlength\fboxrule{.35pt}\fbox{\makebox[1.6em]{\LatinBold #1}}}}',
         r'\newsavebox\OldCoverNotice',r'\ltjsetruby{size=.48,intergap=0}',r'\begin{document}\null']
    put=[]
    def line(x,y,value,size,font='Mincho',center=False,ruby_size=.48,right=False):
        put.append(r'\put('+str(x)+',-'+str(y)+r'){\makebox(0,0)['+('rb'if right else'b'if center else'lb')+']{{\\'+font+r'\fontsize{'+str(size)+'bp}{'+str(size)+r'bp}\selectfont\ltjsetruby{size='+str(ruby_size)+'}'+value+'}}}')
    def rect(x,y,w,h,rule=.5):put.append(f'\\RuleRect{{{x}}}{{{y}}}{{{w}}}{{{h}}}{{{rule}}}')
    def rule(x1,y1,x2,y2,width=.5):put.append(f'\\RuleLine{{{x1}}}{{{y1}}}{{{x2}}}{{{y2}}}{{{width}}}')
    def paragraph_box(x,y,w,tex,size=8,baseline=11):
        put.append(r'\put('+str(x)+',-'+str(y)+r'){\makebox(0,0)[lt]{\begin{minipage}[t]{'+str(w)+r'mm}\vspace{0pt}\Mincho\fontsize{'+str(size)+'bp}{'+str(baseline)+r'bp}\selectfont '+tex+r'\par\end{minipage}}}')
    title={'vocabulary':'文字・語彙','reading_grammar':'読解・文法'}[cover['booklet_id']]
    if cover['status']=='unavailable':
        raise ValueError('Resolve missing Old covers into the documented reconstruction family before rendering')
    else:
        p=cover['printed'];g=family['geometry'];s=family['type'];labels=p['labels'];bilingual=p['family']!='four_instruction'
        if 'label_right_mm' in g:
            line(g['label_right_mm'],g['label_y_mm'],rich(labels['upper_right']),s['upper_label_bp'],'OldCoverHeavy',ruby_size=.24,right=True)
        else:
            line(g['label_left_mm'],g['label_y_mm'],rich(labels['upper_right']),s['upper_label_bp'],'OldCoverHeavy',ruby_size=.24)
        if p['english_booklet_title']:
            line(g['english_title_x_mm'],g['english_title_y_mm'],escape(p['english_booklet_title']),s['english_title_bp'],'LatinBold')
        # Source-wide digit rhythm is a cover role; canonical numeric values stay ASCII.
        year=(r'\hspace{'+str(s.get('year_tracking_em',.16))+'em}').join(escape(c)for c in p['year_text'])
        line(105,g['year_y_mm'],'('+year+')',s['year_bp'],'Date',True)
        digit_size=s['level_bp']*s.get('level_digit_scale',1)
        from historical_cover_reconstruction import digit_tex
        digit=digit_tex(p['level_number'],digit_size)
        line(105,g['level_y_mm'],digit+r'\hspace{'+str(s.get('level_gap_em',.7))+'em}'+rich(labels['level_unit'],centered_ruby=True),s['level_bp'],'OldCoverHeavy',True,.2)
        line(105,g['title_y_mm'],rich(labels['title'],s.get('title_dot_width_em')),s['title_bp'],'OldCoverHeavy',True,.2)
        timing='('+str(p['score'])+rich(labels['score_unit'])+r'\hspace{'+str(s.get('time_gap_em',.9))+'em}'+str(p['minutes'])+rich(labels['minute_unit'])+')'
        line(105,g['time_y_mm'],timing,s['time_bp'],'OldCoverHeavy',True,.28)
        x,y,w,h=g['frame_mm'];rect(x,y,w,h,.45)
        if p['notice_heading_observed']:
            n=BeautifulSoup(labels['notice']['html'],'html.parser')
            pieces=[rich({'html':str(c)})if not isinstance(c,NavigableString) else escape(str(c))for c in n.children]
            if len(pieces)==1 and pieces[0]=='注意':pieces=list('注意')
            line(105,y+g['notice_heading_offset_mm'],r'\hspace{1.6em}'.join(pieces),s['notice_heading_bp'],'OldCoverHeavy',True,.4)
            if bilingual:line(105,y+g['notes_offset_mm'],'Notes',s['notes_bp'],'LatinSans',True)
        body=[]
        for r in p['instructions']:
            ja=rich(r['japanese'])
            body.append('{\\'+s['notice_font']+r'\fontsize{'+str(s['notice_bp'])+'bp}{'+str(s['notice_baseline_bp'])+r'bp}\selectfont\hangindent=1em\hangafter=1\noindent\makebox[2em][l]{'+str(r['number'])+'.}'+ja+r'\par}')
            if r['english']:
                body.append('{\\'+s['english_font']+r'\fontsize{'+str(s['english_bp'])+'bp}{'+str(s['english_baseline_bp'])+r'bp}\selectfont\leftskip='+str(s['english_indent_mm'])+r'mm\noindent '+rich(r['english'])+r'\par}')
            if r['number']<len(p['instructions']):body.append(r'\vspace{'+str(s['rule_gap_bp'])+'bp}')
        body_y=y+(g['body_offset_mm']if p['notice_heading_observed']else g['body_no_heading_offset_mm'])
        available=y+h-body_y-3
        pre.append(r'\sbox\OldCoverNotice{\begin{minipage}[t]{'+str(w-2*g['body_inset_mm'])+r'mm}\vspace{0pt}'+'\n'.join(body)+r'\par\end{minipage}}')
        pre.append(r'\typeout{Old cover notice height: \the\dimexpr\ht\OldCoverNotice+\dp\OldCoverNotice\relax; allowed='+str(available)+'mm}')
        pre.append(r'\ifdim\dimexpr\ht\OldCoverNotice+\dp\OldCoverNotice\relax>'+str(available)+r'mm\errmessage{Old cover notice exceeds source frame}\fi')
        put.append(r'\put('+str(x+g['body_inset_mm'])+',-'+str(body_y)+r'){\makebox(0,0)[lt]{\usebox\OldCoverNotice}}')
        from historical_cover_fields import generate as generate_fields
        if not generate_fields(cover,profile,family,line,rect,rule,rich,escape):
            for k,field_y,split in [('registration',g['registration_y_mm'],g['registration_split_mm']),('name',g['name_y_mm'],g['name_split_mm'])]:
                rect(x,field_y,w,g['field_height_mm'],.65);rule(x+split,field_y,x+split,field_y+g['field_height_mm'],.45)
                line(x+2,field_y+g['field_height_mm']*.62,rich(labels[k]),s['field_bp'],'Mincho',ruby_size=.45)
                if p.get('english_field_labels_observed',True):
                    eng=escape(labels.get(k+'_english','Examinee Registration Number'if k=='registration'else'Name'))
                    line(x+(17 if k=='registration'else 12),field_y+g['field_height_mm']*.62,eng,s['field_english_bp'],'Latin')
        if data['coverage_notes']:
            paragraph_box(x,g['disclosure_y_mm'],w,escape(' '.join(data['coverage_notes'])),s['disclosure_bp'],s['disclosure_baseline_bp'])
    put.append(r'\EditorialMark')
    pre.append(r'\AddToShipoutPictureFG*{\AtPageUpperLeft{\setlength{\unitlength}{1mm}'+'\n'+'\n'.join(put)+'\n}}')
    pre.append(r'\end{document}')
    tex_path.write_text('\n'.join(pre)+'\n',encoding='utf-8')
    return tex_path
