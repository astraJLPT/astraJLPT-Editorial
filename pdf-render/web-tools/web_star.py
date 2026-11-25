"""Project validated canonical STAR records into the existing reader data shape."""
from star_answers import reconstruct, validate
from ruby_core import Projection


def star_data(models):
    out = {}
    for model in models:
        canonical = {q['id']: q for section in model['canonical_editorial']['sections']
                     for q in section['items'] if 'stem' in q}
        for section in model['document']['sections']:
            if model['tasks'][section['id']] != 'sentence_composition':
                continue
            for question in section['items']:
                if 'stem' not in question:
                    continue
                qid = question['id']
                authored = canonical[qid]
                record = model['star_answers'].get(qid)
                validate({**authored, 'star': record})
                # Optional display ruby must never change the source fragments.
                for field in ('stem', 'options'):
                    a = authored[field] if field == 'options' else [authored[field]]
                    b = question[field] if field == 'options' else [question[field]]
                    if [Projection(v).text for v in a] != [Projection(v).text for v in b]:
                        raise ValueError('STAR display content differs from canonical question: ' + qid)
                order = record['order']
                out[model['unit'] + ':' + qid] = {
                    'order': order,
                    'star_slot': record['star_position'],
                    'key': authored['key'],
                    'fragments': [Projection(v).text for v in question['options']],
                    'stem': Projection(question['stem']).text,
                    'reconstructed_sentence': reconstruct(question, order) if order else None,
                    'provenance': {
                        'order_evidence': record['order_evidence'],
                        'position_evidence': record['position_evidence'],
                    },
                    'review_status': record['status'],
                    'editorial_sha256': model['input']['editorial_sha256'],
                    'question_binding': record['question_sha256'],
                }
    return out
