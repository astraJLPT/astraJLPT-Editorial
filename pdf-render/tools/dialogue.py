"""Explicit dialogue structure bound to unchanged base projection."""
import hashlib, html, re
from model import Projection
from notice_layout import html_lines


def lines(value, split_prefixes=None, *, preserve_underlined_blanks=False, preserve_historical_word_gaps=False):
    raw = value['html'] if isinstance(value, dict) else html.escape(value).replace('\n', '<br/>')
    result = html_lines(raw.replace('\n', '<br/>'),preserve_underlined_blanks=preserve_underlined_blanks,
                        preserve_historical_word_gaps=preserve_historical_word_gaps)
    if split_prefixes:
        from semantic_lines import split_before
        result=split_before(result,split_prefixes)
    return result


def candidates(value, split_prefixes=None, *, named_colon=False):
    result = []
    for index, raw in enumerate(lines(value,split_prefixes)):
        qa = re.match(r'^\s*([QAＱＡ][:：])', raw)
        if qa:
            result.append({'line': index, 'speaker': qa[1]})
            continue
        named = re.match(r'^\s*([A-Za-zＡ-Ｚぁ-んァ-ヶ一-龥々ー\s]{1,10}[:：])', raw) if named_colon else None
        if named:
            result.append({'line': index, 'speaker': named[1].strip()})
            continue
        quote=next((c for c in raw if c in '「｢'),None)
        if quote is None:
            continue
        prefix = raw.split(quote, 1)[0]
        speaker = Projection({'html': prefix}).text.strip()
        if re.fullmatch(r'[A-Za-zＡ-Ｚぁ-んァ-ヶ一-龥々ー\s:：]{1,10}', speaker):
            result.append({'line': index, 'speaker': speaker})
    return result if len(result) >= 2 else []


def render(conv, value, structure, source_value=None, scene_lines=(), turn_style=None, *, named_colon=False):
    if named_colon and not getattr(conv, 'source_target_markers', False):
        raise ValueError('Named colon dialogue requires an Old source binding')
    turn_font = ''
    if turn_style is not None:
        if not getattr(conv, 'source_target_markers', False):
            raise ValueError('Reading dialogue metrics require an Old edition')
        limits = {'body_pt': (8, 20), 'baseline_pt': (10, 40), 'word_space_em': (0, 2)}
        if set(turn_style) != set(limits) or any(type(turn_style[k]) not in [int, float] or not lo <= turn_style[k] <= hi for k, (lo, hi) in limits.items()):
            raise ValueError('Invalid reading dialogue metrics')
        turn_font = r'\fontsize{' + str(turn_style['body_pt']) + '}{' + str(turn_style['baseline_pt']) + r'}\selectfont '

    projection = Projection(value if source_value is None else source_value).text
    if hashlib.sha256(projection.encode()).hexdigest() != structure['projection_sha256']:
        raise ValueError('Stale dialogue projection')
    if source_value is not None and re.sub(r'\n+','\n',projection)!=re.sub(r'\n+','\n',Projection(value).text):
        raise ValueError('Dialogue presentation changed its source text')
    raw_lines = lines(value,structure.get('split_before'),
                      preserve_underlined_blanks=getattr(conv,'source_target_markers',False),
                      preserve_historical_word_gaps=getattr(conv,'source_target_markers',False))
    turns = {row['line']: row for row in structure['turns']}
    single = structure.get('single_speaker', False)
    if single and (single is not True or not getattr(conv, 'source_target_markers', False) or len(turns) != 1):
        raise ValueError('Single speaker requires an explicit Old monologue')
    if len(turns) != len(structure['turns']) or len(turns) < (1 if single else 2):
        raise ValueError('Duplicate or incomplete dialogue turns')
    if scene_lines and (not getattr(conv,'source_target_markers',False) or len(set(scene_lines))!=len(scene_lines) or any(type(n)is not int or n in turns or not 0<=n<len(raw_lines)for n in scene_lines)):
        raise ValueError('Invalid bound historical dialogue scene')
    speakers = []
    body = []
    continuations={r['line']:r['turn_line']for r in structure.get('continuation_lines',[])}
    if len(continuations)!=len(structure.get('continuation_lines',[]))or any(n in turns or t not in turns or n!=t+1 or n>=len(raw_lines)for n,t in continuations.items()):raise ValueError('Invalid authored dialogue continuation')
    for index, raw in enumerate(raw_lines):
        if index in continuations:continue
        if index not in turns:
            text=conv.value({'html': raw})
            body.append(r'\HistoricalDialogueScene{'+text+'}'if index in scene_lines else text+r'\par')
            continue
        qa=re.match(r'^\s*([A-Za-zＡ-Ｚぁ-んァ-ヶ一-龥々ー\s]{1,10}[:：])' if named_colon else r'^\s*([QAＱＡ][:：])',raw)
        if qa and turns[index]['speaker']==qa[1]:
            speaker,utterance,quote=raw[:qa.end()],raw[qa.end():],''
        else:
            quote=next((c for c in raw if c in '「｢'),None)
            if quote is None:
                raise ValueError('Missing dialogue quote')
            speaker, utterance = raw.split(quote, 1)
        if index+1 in continuations and continuations[index+1]==index:
            # An authored continuation is an OCR wrap within the same turn.
            # Do not manufacture a word space inside Japanese (e.g. よ\nね).
            utterance+=raw_lines[index+1]
        if Projection({'html': speaker}).text.strip() != turns[index]['speaker']:
            raise ValueError('Changed dialogue speaker')
        # Indentation before a source speaker is layout, not part of its measured
        # name. Preserve internal spaces, punctuation and intact ruby markup.
        from label_separators import prepare as prepare_labels
        speaker_value,_=prepare_labels({'html':speaker.strip()},presentation=False,source_context={'html':raw})
        if turn_style is None:
            speaker_tex = conv.value(speaker_value, 'option')
            utterance_tex = conv.value({'html': quote + utterance})
        else:
            saved_word_space = conv.word_space_em
            try:
                conv.word_space_em = turn_style['word_space_em']
                speaker_tex = conv.value(speaker_value, 'option')
                utterance_tex = conv.value({'html': quote + utterance})
            finally:
                conv.word_space_em = saved_word_space
        # The speaker is typeset twice, once off-page to measure the column.
        # Keep the same glue in the measurement and identify only the visible copy.
        measured = re.sub(r'\\AuthoredWordGap\{([0-9.]+)\}\{[0-9a-f]{20}\}',
                          r'\\AuthoredWordGap{\1}{}', speaker_tex)
        speakers.append('{' + turn_font + measured + '}' if turn_font else measured)
        turn_tex = r'\DialogueTurn{' + speaker_tex + '}{' + utterance_tex + '}'
        body.append('{' + turn_font + turn_tex + '}' if turn_font else turn_tex)
    if set(turns) - set(range(len(raw_lines))):
        raise ValueError('Unknown dialogue line')
    conv.features.append({'kind': 'dialogue', 'turns': structure['turns'], 'decision_state': structure['state']})
    result=r'\DialogueSetup{' + ''.join(r'\MeasureDialogueSpeaker{' + s + '}' for s in speakers) + '}' + '\n'.join(body)
    if turn_style is not None:
        conv.features.append(dict(kind='historical_reading_dialogue_turn_metrics',turn_count=len(turns),**turn_style,canonical_changed=False))
    if 'speaker_align'in structure:
        align={'left':'l','center':'c','right':'r'}[structure['speaker_align']]
        result=r'{\renewcommand\DialogueSpeakerAlignment{'+align+'}'+result+'}'
    return result
