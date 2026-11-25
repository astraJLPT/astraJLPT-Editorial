"""Presentation-only Japanese label separators, shared by both renditions.

Recognition is confined to a leading label, a note definition, a circled
group, or one of the listed inline metadata labels. Technical punctuation
is never rewritten. Bindings must be resolved before calling prepare().
"""
import html
import re
from model import Projection

JP=re.compile(r'[ぁ-ヿ㐀-鿿]')
INLINE=re.compile(r'(?:単位|電話|電話番号|日時|時刻|営業時間|受付時間|期間|料金|参加費|件名|宛て先|あて先|差出人|送信日時|場所|担当|ホームページ|ウェブサイト|URL|TEL|FAX)[ \u3000]*$')
NOTE=re.compile(r'^[ \u3000]*[（(][ \u3000]*注[ \u3000]*[0-9０-９]*[ \u3000]*[)）]')

def candidates(text):
    rows=[]
    for match in re.finditer(r'[:：]',text):
        pos=match.start();left=text[:pos];right=text[pos+1:]
        if not right or not right.strip():continue
        # Time, numerical ratio, URL scheme, drive path and identifier syntax.
        if (re.search(r'\d[ \u3000]*$',left) and re.match(r'[ \u3000]*\d',right)) or right.startswith(('//','\\')):continue
        line=left.rsplit('\n',1)[-1];prefix=line.strip(' \u3000')
        # Administrative problem labels have a separately bound consumer.
        if re.fullmatch(r'(?:問題|もんだい)[ \u3000]*[0-9０-９]+',prefix):continue
        role=None
        if NOTE.match(prefix) and not re.search(r'[:：]',prefix):role='definition'
        elif re.fullmatch(r'[①-⑳⑴-⒇]+[ \u3000]*',prefix.rsplit('：',1)[-1].rsplit(':',1)[-1].strip()):role='group'
        elif INLINE.search(line):role='metadata'
        elif (0<len(prefix)<=48 and JP.search(prefix)
              and not re.search(r'[:：。！？!?=;{}<>/\\]',prefix)
              and not re.search(r'[はがをにもでとへ]$|[（(]注',prefix)):
            # A Japanese label starts its logical line; sentence fragments do
            # not qualify merely because they contain a colon later on.
            role='label'
        if role is None:continue
        a=pos;b=pos+1
        while a and text[a-1] in ' \u3000':a-=1
        while b<len(text) and text[b] in ' \u3000':b+=1
        rows.append(dict(start=a,end=b,colon=pos,before=text[a:b],role=role))
    return rows

def emit_html(raw):
    """Apply display text only after every source-bound consumer has run."""
    from bs4 import BeautifulSoup
    soup=BeautifulSoup(raw,'html.parser')
    for node in soup.select('[data-japanese-label-colon]'):
        if node.name!='span' or node.find() or node.get_text() not in (':','：'):
            raise ValueError('Invalid prepared Japanese label separator')
        node.string='：'
    for node in soup.select('[data-japanese-label-space]'):
        if node.name!='span' or node.find() or not re.fullmatch(r'[ \u3000]+',node.get_text()):
            raise ValueError('Invalid prepared Japanese label whitespace')
        node.decompose()
    return str(soup)

def prepare(value,*,presentation=True,source_context=None):
    raw=value['html'] if isinstance(value,dict) else html.escape(value).replace('\n','<br/>')
    if ':' not in raw and '：' not in raw:return value,[]
    projection=Projection({'html':raw});rows=candidates(projection.text);edits=[];used=[]
    if source_context is not None:
        full=Projection(source_context).text
        if not projection.text or full.count(projection.text)!=1:raise ValueError('Label prefix must match one exact source span')
        offset=full.index(projection.text);end=offset+len(projection.text);rows=[]
        for row in candidates(full):
            if offset<=row['colon']<end:
                a=max(row['start'],offset)-offset;b=min(row['end'],end)-offset
                rows.append({**row,'start':a,'end':b,'colon':row['colon']-offset,'before':projection.text[a:b]})
    for row in rows:
        point=row['colon'];a,b=projection.raw_span(point,point+1)
        # Re-entrant rendering (table cells and bound note tails) must not
        # nest markers, and explicit code/preformatted content is literal.
        prefix=raw[:a]
        stack=[]
        for token in re.finditer(r'<(/?)([A-Za-z][\w:-]*)\b([^>]*)>',prefix):
            close,name,attrs=token.groups();name=name.lower()
            if close:
                if name in [x[0] for x in stack]:stack=stack[:len(stack)-1-next(i for i,x in enumerate(reversed(stack)) if x[0]==name)]
            elif name not in ('br','img','hr','wbr','input','meta','link') and not attrs.rstrip().endswith('/'):
                stack.append((name,attrs))
        if any(name in ('rt','rp','code','pre','script','style') or 'data-japanese-label-colon' in attrs for name,attrs in stack):continue
        # Existing note markers keep their audited role and separator count.
        note=any('data-note-definition-colon' in attrs for _,attrs in stack)
        if projection.overlaps_ruby(row['start'],row['end']):raise ValueError('Label separator overlaps ruby')
        if note:
            # The colon itself is already prepared; normalize only adjacent
            # whitespace outside its marker using the common spacing owner.
            pass
        else:
            edits.append((a,b,'<span data-japanese-label-colon="'+row['role']+'">'+raw[a:b]+'</span>'))
        for n in range(row['start'],row['end']):
            if n!=point:
                a,b=projection.raw_span(n,n+1)
                edits.append((a,b,'<span data-japanese-label-space="true">'+raw[a:b]+'</span>'))
        used.append(row)
    for a,b,replacement in sorted(edits,reverse=True):raw=raw[:a]+replacement+raw[b:]
    if not used:return value,[]
    final=Projection({'html':raw})
    if final.text!=projection.text:raise ValueError('Separator tagging changed binding text')
    old=[(r['base'],r['reading']) for r in projection.ruby]
    if old!=[(r['base'],r['reading']) for r in final.ruby]:raise ValueError('Label presentation changed ruby')
    return {'html':emit_html(raw) if presentation else raw},used
