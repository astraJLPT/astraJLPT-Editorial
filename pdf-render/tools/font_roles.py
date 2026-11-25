"""Resolve declared font roles to pinned local font files and native TeX families."""
from pathlib import Path
from model import ROOT, file_hash

ROLES = {
    'choice_numeral': 'ChoiceNumerals', 'boxed_numeral': 'BoxNumerals',
    'answer_bubble_numeral': 'BubbleNumerals', 'passage_label': 'PassageNumerals',
    'running_latin': 'RunningLatin', 'instruction_latin': 'InstructionLatin',
    'body_latin': 'BodyLatin', 'annotation': 'AnnotationLatin',
    'notice_heading': 'NoticeHeadingLatin', 'letter': 'LetterLatin',
    'task_label': 'TaskLabelLatin',
    'paired_label': 'PairedLabelLatin',
}


def font_spec(style, role):
    spec = style['font_roles'][role]
    path = Path(spec['path']) if 'path' in spec else Path(style['fonts'][spec['source']])
    from package_paths import resource
    path = resource(path)
    if not path.is_file():raise ValueError('Missing role font: ' + role)
    if spec.get('sha256')and file_hash(path)!=spec['sha256']:raise ValueError('Stale pinned role font: '+role)
    options = 'Path={' + path.parent.as_posix() + '/}'
    if 'font_index' in spec and path.suffix.lower()=='.ttc':options += ',FontIndex=' + str(spec['font_index'])
    features = spec.get('features', [])
    if not isinstance(features, list) or set(features) - {'fwid', 'palt', 'tnum', 'lnum', 'vert', 'vrt2'}:
        raise ValueError('Unsupported role font features: ' + role)
    if features:options += ',RawFeature={' + ','.join('+' + f for f in features) + '}'
    if 'bold_same_face' in spec and not isinstance(spec['bold_same_face'],bool):raise ValueError('Invalid fixed-weight font role')
    if spec.get('bold_same_face') is True:options += ',BoldFont={' + path.name + '}'
    if 'embolden' in spec:
        value=spec['embolden']
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not 0<=value<=.5:
            raise ValueError('Invalid role font emboldening: '+role)
        options+=',FakeBold='+str(value)
    for key, option in [('horizontal_scale', 'FakeStretch'), ('scale', 'Scale')]:
        if key in spec:
            value = spec[key]
            if not isinstance(value, (int, float)) or not .6 <= value <= 1.4:
                raise ValueError('Invalid role font scale: ' + role)
            # Preserve the declared identity scale without requesting an
            # unnecessary synthetic font instance from fontspec.
            if key == 'horizontal_scale' and value == 1:
                continue
            options += ',' + option + '=' + str(value)
    return path, options


def declarations(style):
    lines = []
    identities = []
    for role, macro in ROLES.items():
        path, options = font_spec(style, role)
        lines.append('\\newfontfamily\\' + macro + '[' + options + ']{' + path.name + '}')
        identities.append({'role': role, 'path': path.as_posix(), 'sha256': file_hash(path), **style['font_roles'][role]})
    body, opts = font_spec(style, 'body_latin')
    runtime = ROOT / 'pdf-render/runtime/fonts'
    bold = runtime / __import__('package_paths').resource(style['fonts']['bold']).name
    if 'path' not in style['font_roles']['body_latin']:
        # Retain the separately loaded Latin runtime copy. Loading the same
        # original path as Japanese changes native Latin spacing with this
        # LuaTeX/font stack, despite identical font bytes (H12 native probe).
        latin = runtime / body.name
        if file_hash(latin) != file_hash(body):raise ValueError('Stale Latin runtime font')
        opts = opts.replace('Path={' + body.parent.as_posix() + '/}', 'Path={' + runtime.as_posix() + '/}')
    # Honor the declared prose Latin path/features; Japanese and numbered
    # furniture retain their independently selected native families.
    lines.append(r'\setmainfont[' + opts + ',BoldFont={' + bold.name + '},BoldFeatures={Path={' + bold.parent.as_posix() + '/}}]{' + body.name + '}')
    instruction, opts = font_spec(style, 'instruction_latin')
    lines.append(r'\setsansfont[' + opts + ']{' + instruction.name + '}')
    label, opts = font_spec(style, 'task_label_japanese' if 'task_label_japanese' in style['font_roles'] else 'task_label')
    lines.append(r'\newjfontfamily\TaskLabelJapanese[' + opts + ']{' + label.name + '}')
    for role, macro in [('instruction_japanese', 'InstructionJapanese'), ('running_japanese', 'RunningJapanese'), ('notice_body_japanese', 'NoticeBodyJapanese'), ('notice_heading_japanese', 'NoticeHeadingJapanese'), ('notice_label_japanese', 'NoticeLabelJapanese')]:
        if role in style['font_roles']:
            path, opts = font_spec(style, role)
            lines.append('\\newjfontfamily\\' + macro + '[' + opts + ']{' + path.name + '}')
            identities.append({'role': role, 'path': path.as_posix(), 'sha256': file_hash(path), **style['font_roles'][role]})
    if 'task_label_japanese' in style['font_roles']:
        identities.append({'role': 'task_label_japanese', 'path': label.as_posix(), 'sha256': file_hash(label), **style['font_roles']['task_label_japanese']})
    for role, macro in [('document_latin','DocumentLatin'),('notice_latin','NoticeLatin'),('ascii_parenthesis','AsciiParenthesisFace'),('body_numeral','BodyContentNumerals'),('option_content_numeral','OptionContentNumerals'),('notice_numeral','NoticeContentNumerals'),('retained_chinese','RetainedChineseFace'),('breadcrumb_latin','BreadcrumbLatin'),('contact_latin','ContactLatin')]:
        if role in style['font_roles']:
            path, opts=font_spec(style,role)
            lines.append('\\newfontfamily\\'+macro+'['+opts+']{'+path.name+'}')
            identities.append({'role':role,'path':path.as_posix(),'sha256':file_hash(path),**style['font_roles'][role]})
    letter, letter_options = font_spec(style, 'letter')
    if 'instruction_selector' in style['font_roles']:
        path,selector_options=font_spec(style,'instruction_selector')
        lines.append(r'\newfontfamily\SelectorDigits['+selector_options+']{'+path.name+'}')
        identities.append({'role':'instruction_selector','path':path.as_posix(),'sha256':file_hash(path),**style['font_roles']['instruction_selector']})
    lines.append(r'\newjfontfamily\LetterJapanese[' + letter_options + ']{' + letter.name + '}')
    if 'instruction_numeral' in style['font_roles']:
        path, number_options = font_spec(style, 'instruction_numeral')
        lines.append(r'\newfontfamily\AdministrativeNumerals[' + number_options + ']{' + path.name + '}')
        identities.append({'role':'instruction_numeral','path':path.as_posix(),'sha256':file_hash(path),**style['font_roles']['instruction_numeral']})
    from workbook_typography import macro
    for role in sorted(r for r in style['font_roles'] if r.startswith('workbook_')):
        path, options = font_spec(style, role)
        name = macro(role.removeprefix('workbook_'))
        lines.extend(['\\newfontfamily\\' + name + 'Latin[' + options + ']{' + path.name + '}',
                      '\\newjfontfamily\\' + name + 'Japanese[' + options + ']{' + path.name + '}'])
        identities.append({'role':role,'path':path.as_posix(),'sha256':file_hash(path),**style['font_roles'][role]})
    if style.get('workbook_native_2012_furniture'):
        folio = macro('franklin_book_italic_exact2012')
        tab = macro('shingo_pro_regular_exact2012')
        lines.extend([
            '\\renewcommand\\FooterNumerals{\\' + folio + 'Latin}',
            r'\def\WorkbookFolioDigits#1{\ifx#1\relax\else\makebox[.586em][l]{#1}\expandafter\WorkbookFolioDigits\fi}',
            r'\newcommand\WorkbookFolio{\expandafter\WorkbookFolioDigits\expanded{\BookletPage}\relax}',
            '\\renewcommand\\DrawTaskTab{{\\setlength\\fboxsep{0pt}\\colorbox[gray]{\\TabGray}{\\parbox[c][\\TabHeight][c]{\\TabWidth}{\\centering\\color{white}\\' + tab + 'Japanese\\' + tab + r'Latin\fontsize{10}{10}\selectfont\raisebox{-8.8pt}{\shortstack[c]{\TabLabel}}}}}}'
        ])
    if 'memo' in style['font_roles']:
        memo,opts=font_spec(style,'memo')
        lines.extend([r'\newfontfamily\MemoLatin['+opts+']{'+memo.name+'}',r'\newjfontfamily\MemoJapanese['+opts+']{'+memo.name+'}'])
        identities.append({'role':'memo','path':memo.as_posix(),'sha256':file_hash(memo),**style['font_roles']['memo']})
    return lines, identities
