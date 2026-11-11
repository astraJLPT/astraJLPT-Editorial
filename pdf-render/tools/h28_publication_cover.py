"""Native untimed fronts for the exact H28 sample and attributed practice identities."""
from pathlib import Path
from h28_identity import validate_publication


def generate(m, common, tex_path):
    from cover_native import BASE, escape
    pub = m['publication']
    spec = validate_publication(m['unit'], pub)
    if m['minutes'] is not None or m.get('date_label') is not None:
        raise ValueError('A sample or expanded practice set has no sitting time/date')
    if m.get('question_count') != spec['questions']:
        raise ValueError('Publication front count differs from reviewed coverage')
    sample = pub['kind'] == 'sample'
    titles = {'vocabulary': ('言語知識（文字・語彙）', 'Vocabulary'),
              'language_knowledge': ('言語知識（文法）・読解', 'Grammar and Reading'),
              'combined_written': ('言語知識（文字・語彙・文法）・読解', 'Vocabulary, Grammar and Reading')}
    title, english = titles[m['booklet_id']]
    def run(y, size, font, text):
        return '\\put(105,-%s){\\makebox(0,0){\\%s\\fontsize{%sbp}{%sbp}\\selectfont %s}}' % (y,font,size,size,escape(text))
    lines = [run(35,19,'SansBold','日本語能力試験'),
             run(56,25,'Heavy','公式問題例' if sample else '練習問題'),
             run(80,19,'Latin','2009 Official Sample Questions' if sample else spec['subtitle']),
             run(96,12,'Latin','Introducing the revised 2010 JLPT' if sample else spec['sources']),
             run(120,42,'SansBold',m['level']),
             r'\RuleLine{27}{143}{183}{143}{0.7}',
             run(160,17,'SansBold',title), run(178,14,'Latin',english),
             run(202,12,'Latin',f'{spec["questions"]} written questions in the complete set'),
             run(220,11,'Latin',f'This booklet: {m["displayed_body_folios"]} body pages'),
             run(237,11,'Latin','Native editorial rendition; publication identity retained.' if sample else 'Attributed practice material; not an authenticated complete sitting.'),
             r'\EditorialMark']
    path = Path(tex_path)
    path.write_text('\\def\\CoverMarkOpacity{'+str(common['mark']['opacity'])+'}\n'
        +'\\def\\CoverMarkSize{'+str(common['mark']['size_bp'])+'}\n'
        +r'\documentclass[a4paper]{article}'+'\n'
        +r'\input{'+(BASE/'tex/cover-components.tex').as_posix()+'}\n'
        +r'\begin{document}\null'+'\n'
        +r'\AddToShipoutPictureFG*{\AtPageUpperLeft{\setlength{\unitlength}{1mm}'+'\n'
        +'\n'.join(lines)+'\n}}\n'+r'\end{document}'+'\n',encoding='utf-8')
    return path
