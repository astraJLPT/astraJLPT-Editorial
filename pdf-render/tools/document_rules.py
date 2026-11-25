"""Explicit native gray/black document rules, independent by boundary role."""
import re


def rule_tex(rule):
    if set(rule)!={'width_pt','gray','pattern'} or rule['pattern']not in ['solid','dotted']:
        raise ValueError('Unsupported document rule')
    if not .1<=rule['width_pt']<=5 or not 0<=rule['gray']<=.9:
        raise ValueError('Document rule geometry out of range')
    command=r'\DocumentSolidRule'if rule['pattern']=='solid'else r'\DocumentDottedRule'
    return command+'{'+str(rule['width_pt'])+'}{'+str(rule['gray'])+'}'


def email_frame(tex,rules):
    if set(rules)-{'top','inner','bottom','internal','terminal_internal_as_bottom','top_gap_pt','bottom_gap_pt','before_pt','after_pt'}or not {'top','bottom'}<=set(rules):
        raise ValueError('Document frame needs exact top/bottom rule roles')
    for key in ['top_gap_pt','bottom_gap_pt','before_pt','after_pt']:
        if key in rules and (isinstance(rules[key],bool) or not isinstance(rules[key],(int,float)) or not 0<=rules[key]<=48):
            raise ValueError('Invalid document rule clearance')
    marker=r'\par\smallskip\hrule\smallskip '
    internal=list(rules.get('internal',[]))
    if 'terminal_internal_as_bottom' in rules:
        if rules['terminal_internal_as_bottom'] is not True or not internal or internal[-1]!=rules['bottom']:
            raise ValueError('Terminal email rule requires an identical explicit bottom rule')
        if tex.count(marker)!=len(internal):raise ValueError('Internal document rule count changed')
        pattern=re.escape(marker)+r'(?:\s*\\(?:Para|EmailLine)\s*)*(?=\\end\{RuleFrame\})'
        if len(re.findall(pattern,tex))!=1:raise ValueError('Terminal email rule must be the complete frame tail')
        tex=re.sub(pattern,'',tex,count=1);internal.pop()
    if internal:
        if tex.count(marker)!=len(internal):raise ValueError('Internal document rule count changed')
        for rule in internal:
            tex=tex.replace(marker,r'\par\vspace{8pt}'+rule_tex(rule)+r'\vspace{8pt}',1)
    begin,end=r'\begin{RuleFrame}',r'\end{RuleFrame}'
    if tex.count(begin)!=1 or tex.count(end)!=1:raise ValueError('Document rule must select one complete frame')
    margins=''.join(','+option+'='+str(rules[key])+'pt' for key,option in [('before_pt','skipabove'),('after_pt','skipbelow')] if key in rules)
    return tex.replace(begin,begin+r'[topline=false,bottomline=false,innertopmargin=0pt,innerbottommargin=0pt'+margins+']'+rule_tex(rules['top'])+r'\nobreak\vspace{'+str(rules.get('top_gap_pt',10))+'pt}',1).replace(end,r'\par\nobreak\vspace{'+str(rules.get('bottom_gap_pt',12))+'pt}'+rule_tex(rules['bottom'])+end,1)
