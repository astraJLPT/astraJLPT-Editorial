"""Reviewed bitmap policy, including explicitly accepted original-image readings."""
import hashlib,json,re
from functools import lru_cache
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CONFIG=ROOT/'pdf-render/config/norubi-raster-assets.json'

def sha(data):return hashlib.sha256(data).hexdigest()

@lru_cache(maxsize=1)
def registry():
    data=json.loads(CONFIG.read_text('utf-8'))
    # 805 emitted body/HTML bitmaps plus ten historical cover digit strips.
    if data['format']!='norubi-raster-assets-v1' or len(data['assets'])!=815:
        raise ValueError('No-rubi raster review roster changed')
    retained={key:row for key,row in data['assets'].items() if row['policy']=='reuse_with_retained_furigana'}
    if retained:
        binding=data['accepted_image_furigana_exceptions'];path=ROOT/binding['path']
        if path.resolve()!=ROOT/'pdf-render/config/norubi-retained-image-exceptions.json' or sha(path.read_bytes())!=binding['sha256']:
            raise ValueError('Accepted image-furigana exception binding changed')
        exceptions=json.loads(path.read_text('utf-8'))
        if exceptions['format']!='norubi-retained-image-exceptions-v1' or exceptions['status']!='user_accepted_originals_unchanged' or len(retained)!=13 or set(retained)!=set(exceptions['assets']):
            raise ValueError('Accepted image-furigana exception scope changed')
        for key,row in retained.items():
            approved=exceptions['assets'][key]
            if row['exception_id']!=exceptions['exception_id'] or any(row[field]!=approved[field] for field in ('source','review_key','owners','pixels')):
                raise ValueError('Accepted image-furigana exception identity changed: '+key)
    return data['assets']

def retained_exceptions(unit):
    return [{'sha256':key,'review_key':row['review_key'],'exception_id':row['exception_id']}
            for key,row in registry().items() if row['policy']=='reuse_with_retained_furigana' and unit in row['owners']]

def reviewed(data,*,allow_shadow=False):
    key=sha(data);row=registry().get(key)
    if row is None:
        if allow_shadow:return None
        raise ValueError('Unreviewed visible no-rubi bitmap: '+key)
    if row['policy']=='reuse_without_furigana':return {'source_sha256':key,'sha256':key,'data':data,'replacement':False}
    if row['policy']=='reuse_with_retained_furigana':
        return {'source_sha256':key,'sha256':key,'data':data,'replacement':False,
                'retained_furigana':True,'exception_id':row['exception_id']}
    if row['policy']!='replace_exact_reading_regions' or not row.get('replacement'):
        raise ValueError('No-rubi bitmap derivative still pending: '+key)
    ref=row['replacement'];path=(ROOT/ref['path']).resolve()
    if not path.is_relative_to(ROOT/'pdf-render/assets/norubi'):
        raise ValueError('No-rubi replacement is outside its dedicated asset directory')
    replacement=path.read_bytes()
    if sha(replacement)!=ref['sha256']:raise ValueError('No-rubi replacement hash changed')
    proof=ROOT/row['pixel_proof']['path']
    if sha(proof.read_bytes())!=row['pixel_proof']['sha256']:raise ValueError('No-rubi pixel-preservation proof changed')
    return {'source_sha256':key,'sha256':ref['sha256'],'data':replacement,'path':path,'replacement':True}

def emit_tex(source,model,component):
    substitutions=[];retained=[]
    def replace(match):
        path=Path(match['path'])
        if not path.is_absolute():raise ValueError('No-rubi native asset needs an exact absolute source path')
        row=reviewed(path.read_bytes())
        if row.get('retained_furigana'):
            retained.append({'source_sha256':row['source_sha256'],'exception_id':row['exception_id']})
        if not row['replacement']:return match[0]
        substitutions.append({'source_sha256':row['source_sha256'],'sha256':row['sha256'],'path':row['path'].relative_to(ROOT).as_posix()})
        return match['prefix']+row['path'].as_posix()+'}'
    result=re.sub(r'(?P<prefix>\\includegraphics(?:\[[^]]*\])?\{)(?P<path>[^}]+)\}',replace,source)
    if substitutions:model.setdefault('rendition_emissions',[]).append({'component':component,'bitmap_substitutions':substitutions})
    if retained:model.setdefault('rendition_emissions',[]).append({'component':component,'retained_image_furigana':retained})
    return result

def web_row(row,*,allow_shadow=False):
    result=reviewed(row['data'],allow_shadow=allow_shadow)
    if result is None:return row
    if not result['replacement']:return {**row,'norubi_reviewed_sha256':result['sha256'],
        **({'norubi_retained_furigana':result['exception_id']} if result.get('retained_furigana') else {})}
    return {**row,'original_path':row['path'],'path':'assets/illustrations-norubi/'+result['sha256'][:20]+'.png',
            'data':result['data'],'source_path':result['path'],'norubi_source_sha256':result['source_sha256'],
            'norubi_reviewed_sha256':result['sha256']}
