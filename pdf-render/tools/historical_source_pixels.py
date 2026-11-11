"""Old-only source-pixel presentation repairs; canonical image bytes stay intact."""
import base64
import hashlib
import io
import json
import math
from bs4 import BeautifulSoup
from PIL import Image
from model import digest,iter_fields
from presentation import source_binding


def occurrences(document,keys):
    found={key:[]for key in keys};sizes={}
    for field in iter_fields(document):
        value=field['value']
        if not isinstance(value,dict):continue
        for ordinal,node in enumerate(BeautifulSoup(value['html'],'html.parser').find_all('img'),1):
            src=node.get('src','')
            if not src.startswith('data:image/'):continue
            raw=base64.b64decode(src.split(',',1)[1],validate=True)
            key=hashlib.sha256(raw).hexdigest()
            if key not in found:continue
            found[key].append(dict(owner=field['owner'],pointer=field['pointer'],ordinal=ordinal,field_sha256=digest(value)))
            if key not in sizes:
                with Image.open(io.BytesIO(raw))as image:sizes[key]=list(image.size)
    return found,sizes


def validate_asset(art,unit,key,actual,canonical_size):
    from historical_artwork import asset_path
    required={'contract','id','unit','canonical_image_sha256','canonical_pixels','image','source','evidence','occurrences','source_pixels','selection_note','limits'}
    if set(art)!=required or art['contract']not in ['historical-source-pixels-1.0','historical-source-pixels-1.1']:
        raise ValueError('Invalid Old source-pixel asset contract')
    if art['unit']!=unit or art['canonical_image_sha256']!=key or not actual or art['occurrences']!=actual or art['canonical_pixels']!=canonical_size:
        raise ValueError('Stale source-pixel owner, occurrence or canonical dimensions')
    if not art['selection_note']or not art['limits']:raise ValueError('Source-pixel decision needs provenance and limits')
    src=art['source'];ev=art['evidence'];source_binding(unit,ev)
    if set(src)!={'source_path','source_sha256','physical_page'}or any(src[k]!=ev[k]for k in ['source_path','source_sha256'])or src['physical_page']not in ev['physical_pages']:
        raise ValueError('Source-pixel evidence does not match the selected source page')
    trace=art['source_pixels']
    expected={'xref','source_dimensions','source_pixel_box','dimensions','mode','filter','image_transform','source_stream_sha256','decoded_source_rgb_sha256','decoded_crop_rgb_sha256','polarity','resampling','lossy_steps'}
    fractional=art['contract']=='historical-source-pixels-1.1'
    if fractional:expected.add('display_window_source_pixels')
    if set(trace)!=expected or trace['resampling']is not False or trace['lossy_steps']!=[]:
        raise ValueError('Source pixels must be retained without resampling or new lossy encoding')
    sw,sh=trace['source_dimensions'];x0,y0,x1,y1=trace['source_pixel_box']
    if any(type(v)is not int for v in [sw,sh,x0,y0,x1,y1])or not(0<=x0<x1<=sw and 0<=y0<y1<=sh)or trace['dimensions']!=[x1-x0,y1-y0]:
        raise ValueError('Invalid integer source-pixel crop')
    if type(trace['xref'])is not int or trace['xref']<=0 or trace['mode']not in ['1','L','RGB']:
        raise ValueError('Invalid source image identity or mode')
    if fractional:
        window=trace['display_window_source_pixels']
        if not isinstance(window,list)or len(window)!=4 or any(type(v)not in [int,float]or not math.isfinite(v)for v in window):
            raise ValueError('Invalid fractional source-pixel window')
        left,top,right,bottom=window
        if not(x0<=left<right<=x1 and y0<=top<bottom<=y1)or [math.floor(left),math.floor(top),math.ceil(right),math.ceil(bottom)]!=[x0,y0,x1,y1]:
            raise ValueError('Fractional window must match the outward integer source crop')
    path=asset_path(art['image'])
    if path.suffix.lower()!='.png':raise ValueError('Source-pixel derivative must be lossless PNG')
    with Image.open(path)as image:
        if list(image.size)!=trace['dimensions']or image.mode!=trace['mode']or hashlib.sha256(image.convert('RGB').tobytes()).hexdigest()!=trace['decoded_crop_rgb_sha256']:
            raise ValueError('Source-pixel asset dimensions or decoded pixels changed')
        if fractional and 'dpi'in image.info:
            raise ValueError('Fractional pixel clipping requires a PNG without DPI metadata')
    return path


def collect(model):
    selected=model['style'].get('historical_source_pixels',{})
    if not selected:return {}
    if model.get('schema_version')!='4.1.0'or model.get('exam',{}).get('generation')!='historical-1991-2009':
        raise ValueError('Source-pixel repairs are restricted to Old written models')
    from historical_artwork import asset_path,collect as artworks
    from historical_diagrams import collect as diagrams
    if not isinstance(selected,dict):raise ValueError('Invalid source-pixel selectors')
    conflict=set(selected)&(set(artworks(model))|set(diagrams(model)))
    if conflict:raise ValueError('Source-pixel repair conflicts with a native artwork binding')
    actual,sizes=occurrences(model['document'],selected)
    styles=model['style'].get('embedded_image_styles',{})
    result={}
    for key,ref in selected.items():
        if key not in styles or styles[key].get('role')not in ['glyph','illustration']:
            raise ValueError('Source-pixel repair requires an explicit image role')
        art=json.loads(asset_path(ref).read_text('utf8'))
        path=validate_asset(art,model['unit'],key,actual.get(key),sizes.get(key))
        if art['contract']=='historical-source-pixels-1.1'and styles[key]['role']!='glyph':
            raise ValueError('Fractional source-pixel clipping is restricted to glyphs')
        result[key]=dict(asset=ref,art=art,path=path)
    return result


def render(conv,key,style):
    binding=getattr(conv,'historical_source_pixels',{}).get(key)
    if binding is None:return None
    if not getattr(conv,'source_target_markers',False)or style is None:
        raise ValueError('Source-pixel presentation requires Old image roles')
    art=binding['art'];native=art['image'];path=conv.assets/(native['sha256']+'.png')
    data=binding['path'].read_bytes()
    if hashlib.sha256(data).hexdigest()!=native['sha256']:raise ValueError('Source-pixel image changed during emission')
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    w,h=art['canonical_pixels']
    conv.features.append(dict(kind='historical_source_pixel_image',source_image_sha256=key,embedded_image_sha256=native['sha256'],asset=binding['asset'],image=native,source=art['source'],path=str(path),presentation=dict(style),canonical_image_preserved=True,original_pixel_crop=True,original_display_dimensions=[w,h],resampling=False,new_lossy_encoding=False))
    # Width AND height preserve the prior layout box. Outward integer crop
    # rounding cannot repaginate neighbouring text or change option spacing.
    if style['role']=='glyph':
        height=style['height_em'];width=height*w/h
        if art['contract']=='historical-source-pixels-1.1':
            x0,y0,x1,y1=art['source_pixels']['source_pixel_box']
            left,top,right,bottom=art['source_pixels']['display_window_source_pixels']
            trim=[left-x0,y1-bottom,x1-right,top-y0]
            conv.features[-1].update(display_window_source_pixels=[left,top,right,bottom],native_pixel_trim=trim,fractional_source_window_preserved=True)
            # PNGs without DPI metadata use one pixel per bp within this local
            # group. graphicx clips through a Form BBox before applying the
            # prior display dimensions; the underlying image stays untouched.
            trim_tex=' '.join((format(v,'.12f').rstrip('0').rstrip('.')or'0')+'bp'for v in trim)
            return (r'{\pdfvariable imageresolution=72\relax\raisebox{'+str(style.get('raise_em',0))+r'em}{\includegraphics[trim='+trim_tex+',clip,height='+str(height)+'em,width='+format(width,'.12g')+'em]{'+path.as_posix()+'}}}')
        return (r'\raisebox{'+str(style.get('raise_em',0))+r'em}{\includegraphics[height='+str(height)+'em,width='+format(width,'.12g')+'em]{'+path.as_posix()+'}}')
    if style['role']!='illustration':raise ValueError('Unknown source-pixel presentation role')
    width=style['width_fraction'];height=width*h/w
    return (r'\par\addvspace{8pt}\noindent\includegraphics[width='+str(width)+r'\linewidth,height='+format(height,'.12g')+r'\linewidth]{'+path.as_posix()+r'}\par\addvspace{8pt}')
