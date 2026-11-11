"""Exact-source semantic page relationships for Old written content.

These bindings identify passage starts and a stem/options boundary. They never
set page capacity, question-count cutoffs, fonts or per-page spacing.
"""
from model import digest
from presentation import source_binding


def collect(model):
    starts = {}
    splits = {}
    items = {i['id']: i for s in model['document']['sections'] for i in s['items']}
    for iid, meta in model['layout']['items'].items():
        for field, dest in [('historical_passage_start', starts),
                            ('historical_question_boundary', splits)]:
            if field not in meta:
                continue
            if model.get('exam', {}).get('generation') != 'historical-1991-2009':
                raise ValueError('Historical page relationship outside Old JLPT')
            b = meta[field]
            item = items[iid]
            required = {'kind', 'evidence'} | ({'content_sha256'} if dest is starts
                                             else {'stem_sha256', 'options_sha256'})
            if set(b) != required:
                raise ValueError('Invalid historical page relationship fields')
            if dest is starts:
                if ('content' not in item or item.get('type') == 'example'
                        or b['kind'] != 'independent_passage'
                        or digest(item['content']) != b['content_sha256']):
                    raise ValueError('Stale or invalid independent passage binding')
            else:
                if ('stem' not in item or b['kind'] != 'options_next_page'
                        or digest(item['stem']) != b['stem_sha256']
                        or digest(item['options']) != b['options_sha256']
                        or any(k in meta for k in ['historical_target_row',
                           'historical_answer_list', 'historical_label_answer'])
                        or meta.get('historical_options', {}).get('source_four_panel_page')):
                    raise ValueError('Stale or conflicting question boundary')
            source_binding(model['unit'], b['evidence'])
            dest[iid] = b
    return starts, splits


def split_question(iid, label_setup, label, stem_tex, options_tex, gap):
    return ('{' + label_setup + r'\par\addvspace{' + str(gap)
            + r'pt}\hypertarget{' + iid + r'}{}\label{' + iid
            + r'}\QuestionStem{' + label + '}{' + stem_tex
            + r'}\par\clearpage\label{options-' + iid + '}'
            + r'\noindent\hspace*{\OptionIndent}\begin{minipage}[t]{'
            + r'\dimexpr\linewidth-\OptionIndent\relax}' + options_tex
            + r'\end{minipage}\par}')
