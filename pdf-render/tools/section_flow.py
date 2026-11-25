"""Explicit section continuation within a booklet; no inferred page compression."""


def start_tex(section, index, previous_booklet):
    task, booklet = section['task'], section['booklet']
    policy = section.get('start_policy', 'new_page')
    if policy not in ['new_page', 'flow']:
        raise ValueError('Unknown section start policy')
    if policy == 'flow':
        gap, keep = section.get('flow_before_pt'), section.get('flow_keep_lines')
        if (index == 0 or previous_booklet != booklet or task == 'information_retrieval'
                or type(gap) not in [int, float] or not 0 <= gap <= 40
                or type(keep) is not int or not 4 <= keep <= 20 or not section.get('flow_basis')):
            raise ValueError('Section flow needs an exact same-booklet role, gap and keep binding')
        return r'\par\addvspace{' + str(gap) + r'pt}\Needspace{' + str(keep) + r'\baselineskip}'
    return r'\StartInformationTask' if task == 'information_retrieval' else r'\clearpage' if index else ''
