"""Exact native date fields; canonical HTML and ruby associations are untouched."""
import re
from bs4 import BeautifulSoup, NavigableString
from model import Projection
from notice_layout import html_lines


def anchored_dates(conv, cell, binding):
    if Projection({'html':str(cell)}).text.strip()!=binding['text']:
        raise ValueError('Stale date cell binding')
    result=[]
    for raw in html_lines(cell.decode_contents()):
        soup=BeautifulSoup(raw,'html.parser')
        nodes=[n for n in soup.contents if not isinstance(n,NavigableString) or n.strip()]
        if len(nodes)!=5 or not isinstance(nodes[0],NavigableString) or not re.fullmatch(r'[0-9]{1,2}',str(nodes[0])):
            raise ValueError('Date anchor requires one unchanged day number and weekday')
        day,base,opening,weekday,closing=nodes
        if Projection({'html':str(base)}).text!='日' or str(opening) not in ['（','('] or str(closing)!=('）'if str(opening)=='（'else')') or not re.fullmatch('[月火水木金土日]',Projection({'html':str(weekday)}).text):
            raise ValueError('Date anchor structure changed')
        # One right-aligned number field absorbs 1/2-digit width differences.
        # Separate day and weekday fields retain their exact ruby fragments.
        value=(r'\makebox[1.2em][r]{'+conv.text(str(day))+r'}\hspace{.08em}' +
               r'\makebox[1em][c]{'+conv.value({'html':str(base)},'cell')+'}'+
               conv.text(str(opening))+r'\makebox[1em][c]{'+conv.value({'html':str(weekday)},'cell')+'}'+conv.text(str(closing)))
        result.append(r'\mbox{'+value+'}')
    if len(result)<2:raise ValueError('Date anchoring requires repeated fields')
    conv.features.append({'kind':'anchored_date_cell','row':binding['row'],'column':binding['column'],'text':binding['text'],'line_count':len(result)})
    return r'\par '.join(result)
