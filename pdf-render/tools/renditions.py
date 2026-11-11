"""Explicit output policy after authoritative content/binding validation."""
import copy
import re
from bs4 import BeautifulSoup

VARIANTS=('regular','norubi')

def variant(model):
    value=model.get('rendition',{}).get('variant','regular')
    if value not in VARIANTS:raise ValueError('Unknown paper rendition')
    return value

def select(model,value):
    if value not in VARIANTS:raise ValueError('Unknown paper rendition')
    model['rendition']={'variant':value,'ruby_policy':'all' if value=='regular' else 'none',
        'binding_policy':'Validate regular canonical, overlay and semantic bindings before emission; preserve base text and tested kana.'}
    # Derived render caches must never cross a rendition boundary.
    for key in list(model):
        if key.startswith('_web_'):model.pop(key)
    return model

def html_without_ruby(markup):
    soup=BeautifulSoup(markup,'html.parser');count=len(soup.find_all('ruby'))
    # BeautifulSoup visits template descendants too; CSS hiding is not used.
    for node in soup.find_all(['rt','rp']):node.decompose()
    for node in soup.find_all('ruby'):node.unwrap()
    for node in soup.select('[data-rubi-id],[data-rubi-origin]'):
        node.attrs.pop('data-rubi-id',None);node.attrs.pop('data-rubi-origin',None)
    # Native SVGs already retain the original illustration's identity. The
    # hidden source bitmap is validation history, not an additional reading
    # surface in the derivative. Its original bytes remain in the regular set.
    for node in soup.select('.source-literal img'):
        source=node.get('data-source-sha256')
        if not source or not soup.select('svg[data-source-sha256="'+source+'"]'):
            raise ValueError('Unpaired hidden source image in no-rubi HTML')
        node.decompose()
    if soup.find(['ruby','rt','rp']):raise ValueError('No-rubi HTML retained reading markup')
    return str(soup),count

def balanced(source,start,opening='{',closing='}'):
    if source[start:start+1]!=opening:raise ValueError('Malformed ruby command argument')
    depth=1;i=start+1
    while i<len(source):
        if source[i]=='\\':i+=2;continue
        if source[i]==opening:depth+=1
        elif source[i]==closing:
            depth-=1
            if not depth:return source[start+1:i],i+1
        i+=1
    raise ValueError('Unclosed ruby command argument')

def tex_without_ruby(source):
    """Consume complete ruby calls, retaining base TeX verbatim, including art."""
    result=[];end=0;count=0
    for match in re.finditer(r'\\ruby(?![A-Za-z])',source):
        if match.start()<end:continue
        result.append(source[end:match.start()]);i=match.end()
        while source[i:i+1].isspace():i+=1
        if source[i:i+1]=='[':_,i=balanced(source,i,'[',']')
        while source[i:i+1].isspace():i+=1
        base,i=balanced(source,i)
        while source[i:i+1].isspace():i+=1
        _,i=balanced(source,i)
        base,nested=tex_without_ruby(base);result.append(base);count+=1+nested;end=i
    result.append(source[end:]);return ''.join(result),count

def tex_without_tab_readings(source):
    """Remove the explicitly bound readings beside native task-edge labels.

    TaskTabCharacter's second argument is reading text, not a ruby macro.
    Preserve its first argument and strut/stack geometry, including actual kana
    elsewhere in the program. Source validation has already resolved label_parts.
    """
    result=[];end=0;count=0
    for match in re.finditer(r'\\TaskTabCharacter(?![A-Za-z])',source):
        if match.start()<end:continue
        result.append(source[end:match.start()]);i=match.end()
        while source[i:i+1].isspace():i+=1
        base,i=balanced(source,i)
        while source[i:i+1].isspace():i+=1
        reading,i=balanced(source,i)
        result.append(r'\TaskTabCharacter{'+base+'}{}')
        count+=bool(reading);end=i
    result.append(source[end:]);return ''.join(result),count

def emit_tex(source,model,component):
    if variant(model)=='regular':return source
    text,count=tex_without_ruby(source)
    text,tabs=tex_without_tab_readings(text)
    model.setdefault('rendition_emissions',[]).append({'component':component,'removed_ruby_calls':count,'removed_task_tab_readings':tabs})
    from rendition_assets import emit_tex as emit_assets
    return emit_assets(text,model,component)
