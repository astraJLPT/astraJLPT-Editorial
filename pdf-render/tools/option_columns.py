"""Exact native amount columns; punctuation and values remain canonical."""
import re
from model import digest


def render(conv,options,binding,numeric_roles=None):
    if digest(options)!=binding['options_sha256']or len(options)!=4:raise ValueError('Stale option column binding')
    widths=binding['amount_widths_em']
    if len(widths)!=2 or any(isinstance(w,bool)or not isinstance(w,(int,float))or not 1<=w<=6 for w in widths):raise ValueError('Invalid option amount widths')
    if numeric_roles is not None and len(numeric_roles)!=4:raise ValueError('Incomplete option numeral roles')
    rows=[];saved=getattr(conv,'numeric_role',None)
    for index,option in enumerate(options):
        if not isinstance(option,str):raise ValueError('Money option columns require exact plain source')
        match=re.fullmatch(r'([0-9]+(?:,[0-9]{3})*)(円から)(、?)([0-9]+(?:,[0-9]{3})*)(円引いたものを支払う。)',option)
        if not match:raise ValueError('Unknown option money structure')
        a,bridge,punctuation,b,tail=match.groups()
        try:
            if numeric_roles is not None:conv.numeric_role=numeric_roles[index]
            rows.append(r'\makebox['+str(widths[0])+r'em][r]{'+conv.text(a)+'}'+conv.text(bridge)+r'\makebox[1em][l]{'+conv.text(punctuation)+'}'+r'\makebox['+str(widths[1])+r'em][r]{'+conv.text(b)+'}'+conv.text(tail))
        finally:conv.numeric_role=saved
    conv.features.append({'kind':'option_money_columns','options_sha256':binding['options_sha256'],'exact_options':options,'amount_widths_em':widths,'canonical_changed':False})
    return rows
