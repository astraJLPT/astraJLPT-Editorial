"""Independent Old Japanese/digit roles and calibrated label geometry."""
import re
from font_roles import font_spec
from model import file_hash


def instruction_digit_presentation(style, selector=True):
    """Preserve chosen selector faces; condense the generic Old digit fallback.

    The generic Gothic face also supplies the calibrated vocabulary digits.
    Reuse their horizontal width without inheriting their vertical adjustment.
    A separately selected selector face (e.g. Arial or Tw Cen Condensed) already
    owns its proportions, as does an explicit font-role horizontal scale.
    """
    roles = style['font_roles']
    role = 'historical_instruction_digit' if selector and 'historical_instruction_digit' in roles else 'instruction_latin'
    spec = roles[role]
    width = 1 if role == 'historical_instruction_digit' or 'horizontal_scale' in spec else style['historical_typography']['vocabulary_digit']['width']
    if type(width) not in (int, float) or not .6 <= width <= 1.4:
        raise ValueError('Invalid Old instruction digit width')
    return role, width


def question_tex(value, role='reading'):
    if role not in {'reading','vocabulary'}:raise ValueError('Unknown Old question-label role')
    if value=='【問い】':return r'{\HistoricalQuestionJapanese 【問い】}'
    m=re.fullmatch(r'(【?)(問|とい)([1-9][0-9]*)(】?)',value)
    if not m or bool(m[1])!=bool(m[4]):raise ValueError('Invalid Old question label')
    command='HistoricalVocabularyDigit' if role=='vocabulary' else 'HistoricalReadingDigit'
    opening=m[1]+(r'\hspace{\HistoricalQuestionOpenGap}'if m[1]else'')
    closing=(r'\hspace{\HistoricalQuestionCloseGap}'if m[4]else'')+m[4]
    return (r'{\HistoricalQuestionJapanese '+opening+m[2]+r'\hspace{\HistoricalQuestionDigitGap}'
            +'\\'+command+'{'+m[3]+'}'+closing+'}')


def declarations(style):
    p=style['historical_typography'];lines=[];identities=[]
    roles=[('historical_question_japanese','HistoricalQuestionJapanese',True),
           ('historical_question_digit','HistoricalQuestionDigitFace',False)]
    for role,macro,japanese in roles:
        path,opts=font_spec(style,role)
        lines.append(('\\newjfontfamily\\' if japanese else '\\newfontfamily\\')+macro+'['+opts+']{'+path.name+'}')
        identities.append({'role':role,'path':path.as_posix(),'sha256':file_hash(path),**style['font_roles'][role]})
    for role,macro in [('vocabulary','Vocabulary'),('reading','Reading')]:
        g=p[role+'_digit']
        if set(g)!={'width','height'} or any(type(v)not in [int,float]or not .75<=v<=1.1 for v in g.values()):
            raise ValueError('Invalid independent Old digit geometry')
        lines.append(r'\newcommand\Historical'+macro+r'Digit[1]{{\HistoricalQuestionDigitFace\scalebox{'+str(g['width'])+'}['+str(g['height'])+r']{#1}}}')
    for key,macro,lo,hi,suffix in [('question_digit_gap_em','HistoricalQuestionDigitGap',0,.3,'em'),
            ('parenthesis_side_em','HistoricalParenthesisSide',.2,.5,'em'),
            ('two_digit_width','HistoricalTwoDigitWidth',.5,1,''),
            ('inline_box_one_em','HistoricalInlineBoxOneWidth',0,2.5,'em'),
            ('inline_box_two_em','HistoricalInlineBoxTwoWidth',0,3,'em')]:
        val=p[key]
        if type(val)not in [int,float]or not lo<=val<=hi:raise ValueError('Invalid Old label dimension: '+key)
        lines.append('\\newcommand\\'+macro+'{'+str(val)+suffix+'}')
    for key,macro,default,hi in [('question_open_gap_em','HistoricalQuestionOpenGap',0,.4),
            ('question_close_gap_em','HistoricalQuestionCloseGap',0,.6),
            ('slot_outer_gap_em','HistoricalSlotOuterGap',.18,.6),
            ('note_after_chu_em','HistoricalNoteAfterChu',.22,.5),
            ('note_after_digit_em','HistoricalNoteAfterDigit',.12,.5)]:
        val=p.get(key,default)
        if type(val)not in [int,float]or not 0<=val<=hi:raise ValueError('Invalid Old role gap: '+key)
        lines.append('\\newcommand\\'+macro+'{'+str(val)+'em}')
    _, instruction_width = instruction_digit_presentation(style, selector=False)
    lines.append(r'\newcommand\HistoricalInstructionDigit[1]{{\InstructionLatin\scalebox{'+str(instruction_width)+r'}[1]{#1}}}')
    role='historical_instruction_digit'
    if role in style['font_roles']:
        path,opts=font_spec(style,role)
        lines.append(r'\newfontfamily\HistoricalSelectorDigitFace['+opts+']{'+path.name+'}')
        lines.append(r'\newcommand\HistoricalSelectorDigit[1]{{\HistoricalSelectorDigitFace #1}}')
        identities.append({'role':role,'path':path.as_posix(),'sha256':file_hash(path),**style['font_roles'][role]})
    else:
        lines.append(r'\newcommand\HistoricalSelectorDigit[1]{\HistoricalInstructionDigit{#1}}')
    center=p.get('boxed_digit_center',0)
    if type(center)is not int or center not in [0,1]:raise ValueError('Invalid Old boxed digit centering')
    lines.append(r'\newcommand\HistoricalBoxDigitCenter{'+str(center)+'}')
    for key,macro,default,lo,hi,suffix in [
            ('target_reference_pt','HistoricalTargetReferenceSize',5.5,5,8,''),
            ('target_reference_drop_ex','HistoricalTargetReferenceDrop',1.5,.8,2.5,'ex'),
            ('slot_inner_width_em','HistoricalSlotInnerWidth',2.4,1.5,4,'em'),
            ('example_explanation_tracking_em','HistoricalExampleExplanationTracking',0,0,.12,'em')]:
        val=p.get(key,default)
        if type(val)not in [int,float]or not lo<=val<=hi:raise ValueError('Invalid Old target/example metric: '+key)
        lines.append('\\newcommand\\'+macro+'{'+str(val)+suffix+'}')
    # Optional role controls leave every existing profile emission unchanged.
    # The Old component macros have been loaded before these declarations.
    if 'example_explanation_before_pt' in p:
        val=p['example_explanation_before_pt']
        if type(val)not in [int,float]or not 0<=val<=40:raise ValueError('Invalid Old explanation clearance')
        lines.append(r'\renewcommand\HistoricalExampleExplanationBefore{'+str(val)+'pt}')
    if 'example_explanation_inset_em' in p:
        val=p['example_explanation_inset_em']
        if type(val)not in [int,float]or not 0<=val<=3:raise ValueError('Invalid Old explanation inset')
        lines.append(r'\renewcommand\HistoricalExampleExplanation[1]{\par{\ifdim\HistoricalExampleExplanationTracking>0pt\relax\ltjsetparameter{kanjiskip=\HistoricalExampleExplanationTracking}\fi\leftskip='+str(val)+r'em\rightskip='+str(val)+r'em\relax\parindent=1em\indent #1\par}}')
    return lines,identities
