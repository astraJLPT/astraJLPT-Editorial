"""Attach a nonprinting end anchor to content, before discardable exterior glue."""
import re


def mark(tex, item):
    if not re.fullmatch(r'(?:reading|vocab)-[bq][0-9]+', item):
        raise ValueError('Invalid content extent identity')
    anchor = r'\label{context-end-' + item + '}'
    if anchor in tex:
        raise ValueError('Duplicate content extent anchor')
    # A frame's final write stays with that frame, including continuation pages.
    # Do not select an earlier frame when a citation or notes follow it.
    shell = r'(?:\s|[{}]|\\(?:par|Para)\s*|\\vspace\{[0-9.]+pt\})*'
    ends = list(re.finditer(r'\\end\{(?:NoticeFrame|RuleFrame|ClozeFrame|PairedFrame|ReadingNotes|minipage)\}', tex))
    position = len(tex)
    for end in reversed(ends):
        if re.fullmatch(shell, tex[end.end():]):
            position = end.start()
            break
    # Ordinary prose and standalone tables end a real paragraph. A write after
    # its exterior vspace can disappear at end-of-document or move to a new page.
    for end in re.finditer(r'\\(?:Para|par)(?![A-Za-z])', tex[:position]):
        if re.fullmatch(shell, tex[end.end():position]):
            position = end.start()
            break
    return tex[:position] + anchor + tex[position:]
