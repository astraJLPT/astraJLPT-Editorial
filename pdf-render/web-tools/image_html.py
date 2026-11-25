"""Exact embedded image assets and source-bound TeX dimensions.

Images are decoded once into the shared asset pool. Editorial markup and bytes
remain untouched; only the web projection replaces data URLs and capture CSS.
"""
import base64
import hashlib
from bs4 import BeautifulSoup
from embedded_images import configure
from model import iter_fields


def source_pixels(m):
    if '_web_source_pixels' not in m:
        from historical_source_pixels import collect
        m['_web_source_pixels']=collect(m)
    return m['_web_source_pixels']


def artwork(m):
    if '_web_artwork' not in m:
        from historical_artwork import collect,tex,asset_path
        from historical_diagrams import collect as diagrams,sets_tex,flow_tex
        from native_svg import project
        bindings=collect(m);native=diagrams(m);result={}
        for key,binding in bindings.items():
            art=binding['art'];row={**binding,'contract_path':asset_path(binding['asset'])}
            if art['kind']=='raster':
                path=asset_path(art['image']);digest=art['image']['sha256']
                row['raster']={'path':'assets/illustrations/'+digest[:20]+path.suffix.lower(),'data':path.read_bytes(),'source_path':path}
            else:row.update(project(tex(art),m,'a-'+key[:16]))
            result[key]=row
        for key,binding in native.items():
            source=sets_tex(binding)if binding['kind']=='sets_choice'else flow_tex(binding)
            result[key]={**binding,**project(source,m,'d-'+key[:16])}
        m['_web_artwork']=result
    return m['_web_artwork']


def asset(src):
    if not src.startswith(('data:image/png;base64,', 'data:image/jpeg;base64,')):
        raise ValueError('Unregistered embedded image source')
    header, encoded = src.split(',', 1)
    data = base64.b64decode(encoded, validate=True)
    digest = hashlib.sha256(data).hexdigest()
    suffix = '.png' if 'png' in header else '.jpg'
    return digest, 'assets/illustrations/' + digest[:20] + suffix, data


def inventory(m):
    styles = configure(m['document'], m['style'].get('embedded_image_styles', {}))
    found = {}
    for field in iter_fields(m['document']):
        value = field['value']
        if not isinstance(value, dict):
            continue
        for image in BeautifulSoup(value['html'], 'html.parser').find_all('img'):
            digest, path, data = asset(image.get('src', ''))
            found[digest] = {'path': path, 'data': data, 'style': styles.get(digest)}
    for original,binding in source_pixels(m).items():
        spec=binding['art']['image'];digest=spec['sha256'];data=binding['path'].read_bytes()
        if hashlib.sha256(data).hexdigest()!=digest:raise ValueError('Source-pixel asset changed')
        from historical_artwork import asset_path
        found[digest]={'path':'assets/illustrations/'+digest[:20]+'.png','data':data,'style':styles[original],'source_path':binding['path'],'source_contract':asset_path(binding['asset']),'canonical_sha256':original}
    for original,binding in artwork(m).items():
        found[original]['source_contract']=binding.get('contract_path')
        if binding.get('art'):
            from historical_artwork import asset_path
            found[original]['source_dependencies']=[asset_path(binding['art']['raw_crop'])]
        for key,row in binding.get('images',{}).items():found[key]=row
        if binding.get('raster'):
            row=binding['raster'];found[hashlib.sha256(row['data']).hexdigest()]=row
    from notice_html import artifact
    for spec in m['style'].get('block_styles',{}).values():
        if spec.get('asset'):
            source,target=artifact(m,spec['asset']);data=source.read_bytes()
            found[hashlib.sha256(data).hexdigest()]={'path':target,'data':data,'source_path':source}
    from renditions import variant
    if variant(m)=='norubi':
        from rendition_assets import web_row
        # Replaced canonical bitmaps remain available as source identities,
        # but only their validated pixel/vector replacement is emitted.
        shadows=set(source_pixels(m))|set(artwork(m))
        found={key:web_row(row,allow_shadow=key in shadows) for key,row in found.items()}
    return found


def project_rendition(markup,m):
    """Map only emitted, already bound visible images to reviewed derivatives."""
    from renditions import variant
    if variant(m)!='norubi':return markup
    assets=inventory(m);paths={row.get('original_path',row['path']):row for row in assets.values()}
    soup=BeautifulSoup(markup,'html.parser')
    for node in soup.select('img[src],svg image[href]'):
        attr='src' if node.name=='img' else 'href';path=node[attr]
        if not path.startswith('../'):raise ValueError('Unbound visible no-rubi image URL')
        row=paths.get(path[3:])
        if row is None or not row.get('norubi_reviewed_sha256'):
            raise ValueError('Visible no-rubi image lacks its exact raster review: '+path)
        node[attr]='../'+row['path'];node['data-raster-sha256']=row['norubi_reviewed_sha256']
        if row.get('norubi_source_sha256'):node['data-norubi-source-sha256']=row['norubi_source_sha256']
    return str(soup)


def present(soup, m):
    for image in soup.find_all('img'):
        digest, path, _ = asset(image.get('src', ''))
        style = m['style'].get('embedded_image_styles', {}).get(digest)
        if style is None:
            # The explicit unselected legacy fallback in RichTeX.node(img).
            style = {'role': 'glyph', 'height_em': 1.05, 'raise_em': -.12}
        image['src'] = '../' + path
        image['data-source-sha256'] = digest
        image['class'] = ['source-image', 'source-image-' + style['role']]
        for attr in ('width', 'height'):
            image.attrs.pop(attr, None)
        if style['role'] == 'glyph':
            image['style'] = ('display:inline-block;width:auto;max-width:none;'
                              f'height:calc(var(--nominal-em) * {style["height_em"]});'
                              f'vertical-align:calc(var(--nominal-em) * {style.get("raise_em",0)});margin:0;')
        else:
            image['style'] = ('display:block;height:auto;max-width:none;'
                              f'width:{style["width_fraction"] * 100:g}%;'
                              'margin:calc(8 * var(--point)) 0;')
        replacement=source_pixels(m).get(digest)
        if replacement:
            art=replacement['art'];image['src']='../assets/illustrations/'+art['image']['sha256'][:20]+'.png'
            image['data-presentation-sha256']=art['image']['sha256']
            w,h=art['canonical_pixels']
            if style['role']=='glyph':
                width=style['height_em']*w/h
                image['style']+=f'width:calc(var(--nominal-em) * {width});'
                if art['contract']=='historical-source-pixels-1.1':
                    x0,y0,x1,y1=art['source_pixels']['source_pixel_box'];left,top,right,bottom=art['source_pixels']['display_window_source_pixels']
                    frame=soup.new_tag('span',attrs={'class':'source-pixel-window','data-canonical-image':digest})
                    frame['style']=f'display:inline-block;position:relative;overflow:hidden;width:calc(var(--nominal-em) * {width});height:calc(var(--nominal-em) * {style["height_em"]});vertical-align:calc(var(--nominal-em) * {style.get("raise_em",0)});'
                    image.wrap(frame)
                    image['style']=f'position:absolute;max-width:none;width:{(x1-x0)/(right-left)*100}%;height:{(y1-y0)/(bottom-top)*100}%;left:{-(left-x0)/(right-left)*100}%;top:{-(top-y0)/(bottom-top)*100}%;margin:0;'
            else:image['style']+=f'aspect-ratio:{w}/{h};height:auto;'
        native=artwork(m).get(digest)
        if native:
            if style['role']!='illustration':raise ValueError('Native artwork requires its bound illustration role')
            if native.get('raster'):
                image['src']='../'+native['raster']['path'];image['data-presentation-sha256']=hashlib.sha256(native['raster']['data']).hexdigest()
            else:
                visual=BeautifulSoup(native['svg'],'html.parser').svg
                visual['style']=image['style'];visual['data-native-artwork']=native.get('art',{}).get('kind',native.get('kind'))
                visual['data-native-source-sha256']=native['source_sha256'];visual['class']+=['source-image','source-image-illustration']
                visual['data-source-sha256']=digest
                if image.get('alt'):
                    label=soup.new_tag('span',attrs={'class':'source-literal sr-only','role':'img','aria-label':image['alt']})
                    image.insert_before(label)
                image.replace_with(visual)
                image=visual
            if native.get('left_inset_fraction'):image['style']+=f'margin-left:{native["left_inset_fraction"]*100}%;'
            if native.get('block_spacing'):
                spacing=native['block_spacing'];image['style']+=f'margin-top:calc(var(--point) * {spacing["before_pt"]});margin-bottom:calc(var(--point) * {spacing["after_pt"]});'
