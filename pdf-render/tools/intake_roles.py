"""Reviewable semantic-role candidates and strict declared-role consumer checks.

Candidates are evidence for intake authoring, never automatic content edits or
claims about source typography. Exact bindings remain in each unit editorial.
"""
import re
from model import Projection, digest


def cloze_frame(level, reviewed_two_page_exception=False):
    """A long-passage exception is authored after measurement, never level-wide."""
    if level not in ['N1','N2','N3','N4','N5']:raise ValueError('Unknown cloze level')
    if not isinstance(reviewed_two_page_exception,bool):raise ValueError('Explicit cloze exception required')
    return 'none'if reviewed_two_page_exception else'box'


def introductions(value):
    lines = [line.strip() for line in Projection(value).text.splitlines() if line.strip()]
    return [line for line in lines[:3]
            if re.match(r'^(以下は|次は|これは|つぎは)', line)
            and re.search(r'(文章|作文|メール|手紙|お知らせ|エッセイ|コラム|メモ|書|届いた|送った|掲載|述べられ)', line)
            and len(line) < 180]


def candidates(model):
    from dialogue import candidates as dialogue_candidates
    from richtex import remove_number
    rows = []
    for section in model['document']['sections']:
        task = model['layout']['sections'][section['id']]['task']
        for item in section['items']:
            layout = model['layout']['items'][item['id']]
            exclusion = layout.get('intake_candidate_exclusions')
            excluded = []
            if exclusion:
                from presentation import source_binding
                if ('content' not in item or task not in ['reading', 'cloze']
                        or item['type'] == 'example' or layout.get('introduction')
                        or digest(item['content']) != exclusion['content_sha256']):
                    raise ValueError('Stale or conflicting intake candidate exclusion')
                excluded = exclusion['introduction_texts']
                actual = introductions(item['content'])
                if (not excluded or len(excluded) != len(set(excluded))
                        or any(t not in actual or Projection(item['content']).text.count(t) != 1
                               for t in excluded)):
                    raise ValueError('Intake exclusion must select exact unique current candidates')
                source_binding(model['unit'], exclusion['evidence'])
            if 'stem' in item:
                stem = remove_number(item['stem'], layout.get('printed_label', {}).get('source_prefix'))[1]
                turns = dialogue_candidates(stem)
                if turns:
                    rows.append({'target': item['id'], 'role': 'dialogue', 'turns': turns,
                                 'bound': bool(layout.get('dialogue')),
                                 'resolved': bool(layout.get('dialogue'))})
            elif task in ['reading', 'cloze'] and item['type'] != 'example':
                for text in introductions(item['content']):
                    rows.append({'target': item['id'], 'role': 'introduction', 'text': text,
                                 'bound': bool(layout.get('introduction')),
                                 'resolved': bool(layout.get('introduction')) or text in excluded,
                                 'disposition': 'reviewed_body_prose' if text in excluded else
                                                'bound_introduction' if layout.get('introduction') else
                                                'unresolved'})
    return rows


def reached(layout, tex):
    result = {}
    intro = layout.get('introduction')
    if intro:
        macro = {'passage': r'\PassageIntroduction{', 'document': r'\DocumentIntroduction{'}[intro['role']]
        count = tex.count(macro)
        if count != 1:
            raise ValueError('Declared introduction did not reach its component exactly once')
        result['introduction'] = {'role': intro['role'], 'component': macro, 'count': count,
                                  'projection_sha256': intro['projection_sha256']}
    dialogue = layout.get('dialogue')
    if dialogue:
        count = tex.count(r'\DialogueTurn{')
        if count != len(dialogue['turns']) or tex.count(r'\DialogueSetup{') != 1:
            raise ValueError('Declared dialogue did not reach its complete component')
        result['dialogue'] = {'component': r'\DialogueTurn{', 'count': count,
                              'speaker_align': dialogue.get('speaker_align', 'center'),
                              'projection_sha256': dialogue['projection_sha256']}
    keep = layout.get('keep_with_previous')
    if keep:
        count = tex.count(r'\KeepWithPreviousParagraph{')
        if count != len(keep['paragraphs']):
            raise ValueError('Declared paragraph keep did not reach its component')
        result['keep_with_previous'] = {'component': r'\KeepWithPreviousParagraph{', 'count': count,
                                       'projection_sha256': keep['projection_sha256']}
    return result
