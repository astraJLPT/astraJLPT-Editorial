"""Source-bound H22 artwork. Source image payloads remain canonical and recoverable."""
import base64
import hashlib
import json
import math
from pathlib import Path
from bs4 import BeautifulSoup
from model import ROOT,digest,file_hash
from presentation import source_binding
from richtex import text_tex

KINDS={'raster','annotated_waist_skirt','spinning_top','cylinder','purchase_graph','recycling_pies','metropolitan_population','infant_mirror','household_purchase_option','family_relationship_option','source_label_overlay','gender_equality_bars','university_enrolment_option','economic_category_option','private_room_graph','animal_group_option','consciousness_option','sleep_distribution_bars'}
KINDS.update({'life_goals_lines','transport_radars'})
KINDS.update({'company_choice_lines','national_condition_lines','career_preparation_bars'})
KINDS.update({'scale_comparison_bars','conversation_opinion_lines','education_goal_bars','phone_reading_bars','employment_intent_option','score_distribution_option','smoking_distribution_option'})

# This is a local, source-traced variant, not an Old or level default. Retain
# the original H22 drawing for old assets that do not select this geometry.
CYLINDER_H23_GEOMETRY = dict(profile='h23-source-421', radius_x=46, radius_y=25,
    side_height=110, bounding_box=[-66,-143,66,36],
    rear_arc='observed_right_segment_with_inferred_light_left_continuation')


def asset_path(ref):
    if set(ref)!={'path','sha256'} or not isinstance(ref['path'],str):raise ValueError('Invalid artwork asset reference')
    from package_paths import resource
    path=resource(ref['path'])
    if path.is_absolute() and not path.is_relative_to(ROOT/'editorial-json/assets'):
        raise ValueError('Artwork outside maintained preprocess assets')
    current=ROOT
    for part in path.relative_to(ROOT).parts:
        if part in ['..','.']or part.lower()=='zdiamond_scans':raise ValueError('Unsafe artwork path')
        current=current/part
        if current.is_symlink()or current.is_junction():raise ValueError('Linked artwork path')
    if not path.is_file()or file_hash(path)!=ref['sha256']:raise ValueError('Stale or missing artwork asset: '+str(path))
    return path


def validate_art(art):
    if art.get('contract')!='historical-artwork-1.0' or art.get('kind')not in KINDS:raise ValueError('Unknown historical artwork contract')
    allowed={'contract','id','kind','unit','item_id','source','raw_crop','selection_note','limits','image','data','native_map_labels'}
    if set(art)-allowed or not {'id','unit','item_id','source','raw_crop','selection_note','limits'}<=set(art):raise ValueError('Invalid artwork fields')
    if 'native_map_labels'in art and art['kind']!='metropolitan_population':raise ValueError('Map labels require the population composite')
    if art['kind']in ['scale_comparison_bars','conversation_opinion_lines','education_goal_bars','phone_reading_bars','employment_intent_option','score_distribution_option','smoking_distribution_option']:
        from historical_earlier_statistical_charts import validate
        validate(art)
    elif art['kind']in ['company_choice_lines','national_condition_lines','career_preparation_bars']:
        from historical_late_statistical_charts import validate
        validate(art)
    elif art['kind']in ['life_goals_lines','transport_radars']:
        from historical_statistical_charts import validate
        validate(art)
    elif art['kind']=='sleep_distribution_bars':
        from historical_sleep_distribution import validate
        validate(art)
    elif art['kind']=='consciousness_option':
        from historical_consciousness import validate
        validate(art)
    elif art['kind']in ['private_room_graph','animal_group_option']:
        from historical_1993_level1_art import validate
        validate(art)
    elif art['kind']=='economic_category_option':
        from historical_economic_sets import validate
        validate(art)
    elif art['kind']=='university_enrolment_option':
        from historical_enrolment import validate
        validate(art)
    elif art['kind']=='gender_equality_bars':
        from historical_stacked_bars import validate
        validate(art)
    elif art['kind']=='source_label_overlay':
        from historical_label_overlays import validate
        validate(art,asset_path)
    elif art['kind']in ['raster','annotated_waist_skirt']:
        asset_path(art['image'])
    elif art['kind']=='cylinder' and 'data' in art:
        if art['data'] != CYLINDER_H23_GEOMETRY:
            raise ValueError('Unknown or altered source-traced cylinder geometry')
        if (art['unit'],art['item_id'],art['source']['physical_page'],art['source']['source_sha256']) != (
                'N1_1999','reading-b005',421,'8560bf8ef92b4e2d58559b3e14882b76d3307586f5d55b0e7fa33cc2f5fa931f'):
            raise ValueError('Cylinder geometry belongs to the inspected source 421 only')
    elif art['kind']=='purchase_graph':
        d=art['data'];series=d['series']
        if d.get('coordinate_status')!='approximate_digitization_not_exact_historical_data' or len(series)!=4:raise ValueError('Curve digitization must remain approximate')
        expected=[('テレビ','solid',1980),('自動車','dashed',1980),('テープレコーダー','dotted',1980),('ビデオテープレコーダー','dashdot',1985)]
        for s,(name,style,first) in zip(series,expected):
            if (s['label'],s['style'],s['first_year'])!=(name,style,first):raise ValueError('Graph series identity/order changed')
            if [p[0]for p in s['points']]!=list(range(first,1994)) or any(type(p[1])not in [int,float]or not 80<=p[1]<=260 for p in s['points']):raise ValueError('Invalid traced curve')
    elif art['kind']=='recycling_pies':
        charts=art['data']['charts']
        expected=[('テレビ',[12,3,1,26,53,5]),('冷蔵庫',[49,4,1,43,3]),('エアコン',[54,18,9,16,3]),('洗濯機',[52,2,4,33,9])]
        cats=[['鉄','銅','アルミ','プラスチック','ガラス','その他']]+[['鉄','銅','アルミ','プラスチック','その他']]*3
        for ch,(title,values),labels in zip(charts,expected,cats):
            if ch['title']!=title or ch['percentages']!=values or ch['categories']!=labels:raise ValueError('Printed pie data/order changed')
        if len(charts)!=4 or art['data'].get('normalization')!='none_use_printed_percentages':raise ValueError('Do not normalize printed percentages')
    elif art['kind']=='metropolitan_population':
        observed={
            ('N1_1998','reading-b007',368,'8560bf8ef92b4e2d58559b3e14882b76d3307586f5d55b0e7fa33cc2f5fa931f'),
            ('N2_1998','reading-b007',342,'0a6634758dce0a258ffaf92c6c8ea1a738a4b8ceb52cd75cb44a4d8d340dfa64')}
        if (art['unit'],art['item_id'],art['source']['physical_page'],art['source']['source_sha256']) not in observed:
            raise ValueError('Population composite requires its exact inspected owner, item and source page')
        expected=dict(normalization='none_use_printed_percentages',start='noon_clockwise',
            title='3大都市圏の人口が全国の人口に占める割合',
            categories=['東京を中心とした50キロの地域','大阪を中心とした50キロの地域','名古屋を中心とした50キロの地域','その他'],
            patterns=['black','north east lines','dots','white'],
            charts=[dict(year=1960,percentages=[16.7,10.9,5.7,66.7]),dict(year=1996,percentages=[23.7,12.9,6.9,56.5])])
        if art.get('data')!=expected:raise ValueError('Population data, year, legend or pattern differs from the printed source')
        asset_path(art['image'])
        if 'native_map_labels'in art:
            from historical_label_overlays import validate
            validate({**art,'data':art['native_map_labels']},asset_path)
    elif art['kind']=='household_purchase_option' and art['unit']=='N2_1997':
        if (art['item_id'],art['source']['physical_page'],art['source']['source_sha256'])!=('reading-q018',292,'0a6634758dce0a258ffaf92c6c8ea1a738a4b8ceb52cd75cb44a4d8d340dfa64'):
            raise ValueError('N2 1997 graph requires its exact inspected item/page/source')
        if art.get('data')!=n2_1997_purchase_data(art.get('data',{}).get('option')):
            raise ValueError('N2 1997 graph source trace or option identity changed')
    elif art['kind'] in ['infant_mirror','household_purchase_option','family_relationship_option']:
        kind=art['kind'];option=art.get('data',{}).get('option')
        item,page,sha={'infant_mirror':('reading-b001',307,'8560bf8ef92b4e2d58559b3e14882b76d3307586f5d55b0e7fa33cc2f5fa931f'),
            'household_purchase_option':('reading-q017',314,'8560bf8ef92b4e2d58559b3e14882b76d3307586f5d55b0e7fa33cc2f5fa931f'),
            'family_relationship_option':('reading-q014',536,'e3555741c8f14b855a32e7d09b42eb790492e3818a85a875f99d84703c752e00')}[kind]
        if (art['unit'],art['item_id'],art['source']['physical_page'],art['source']['source_sha256'])!=('N1_1997',item,page,sha):raise ValueError('N1 1997 figure requires exact inspected owner/item/page/source')
        if art.get('data')!=n1_1997_data(kind,option):raise ValueError('N1 1997 source trace or option identity changed')
        if kind=='infant_mirror':asset_path(art['image'])
    asset_path(art['raw_crop'])
    return art


def collect(model):
    result={}
    for section in model['document']['sections']:
        for item in section['items']:
            b=model['layout']['items'][item['id']].get('historical_artwork')
            if b is None:continue
            if model['schema_version']!='4.1.0' or model.get('exam',{}).get('generation')!='historical-1991-2009':raise ValueError('H22 artwork requires the component-aware Old contract')
            field=b.get('field','content')
            if set(b)-{'field','field_sha256','panels','evidence','left_inset_fraction','block_spacing'} or not {'field_sha256','panels','evidence'}<=set(b) or field not in ['content','stem','options'] or digest(item.get(field))!=b['field_sha256']:raise ValueError('Stale artwork field binding')
            if 'left_inset_fraction'in b and (field=='options' or type(b['left_inset_fraction'])not in (int,float) or not 0<=b['left_inset_fraction']<=.5):
                raise ValueError('Invalid source-bound artwork inset')
            if 'block_spacing'in b:
                spacing=b['block_spacing']
                if (field=='options'or not isinstance(spacing,dict)or set(spacing)!={'before_pt','after_pt','no_interline_after'}
                    or type(spacing['before_pt'])not in [int,float]or not 0<=spacing['before_pt']<=36
                    or type(spacing['after_pt'])not in [int,float]or not 0<=spacing['after_pt']<=24
                    or spacing['no_interline_after']is not True):raise ValueError('Invalid source-bound artwork block spacing')
            if field=='options' and ('stem'not in item or len(item.get('options',[]))!=4):raise ValueError('Artwork options require four choices in a question')
            source_binding(model['unit'],b['evidence'])
            values=item['options']if field=='options'else[item[field]]
            images=[]
            for value in values:
                if not isinstance(value,dict)or set(value)!={'html'}:raise ValueError('Artwork field must contain rich HTML')
                found=BeautifulSoup(value['html'],'html.parser').find_all('img')
                if field=='options'and len(found)!=1:raise ValueError('Artwork choice requires exactly one source image')
                images.extend(found)
            hashes=[hashlib.sha256(base64.b64decode(im['src'].split(',',1)[1])).hexdigest()for im in images]
            if len(hashes)!=len(b['panels']):raise ValueError('Artwork panel/image count mismatch')
            for option_index,(key,panel) in enumerate(zip(hashes,b['panels']),1):
                if set(panel)!={'source_image_sha256','asset'} or panel['source_image_sha256']!=key or key in result:raise ValueError('Stale or duplicate artwork selector')
                path=asset_path(panel['asset']);art=validate_art(json.loads(path.read_text('utf-8')))
                if (art['unit'],art['item_id'])!=(model['unit'],item['id']):raise ValueError('Artwork owner mismatch')
                if art['kind']in ['household_purchase_option','family_relationship_option','university_enrolment_option','economic_category_option','animal_group_option','employment_intent_option','score_distribution_option','smoking_distribution_option'] and (field!='options'or art['data']['option']!=option_index):raise ValueError('Source diagram option order changed')
                if art['kind']=='infant_mirror'and field!='content':raise ValueError('Mirror composite belongs to passage content')
                if any(art['source'][k]!=b['evidence'][k] for k in ('source_path','source_sha256')) or art['source']['physical_page']not in b['evidence']['physical_pages']:raise ValueError('Artwork source/page mismatch')
                result[key]=dict(art=art,asset=panel['asset'],owner=item['id'],source_image_sha256=key)
                if 'left_inset_fraction'in b:result[key]['left_inset_fraction']=b['left_inset_fraction']
                if 'block_spacing'in b:result[key]['block_spacing']=b['block_spacing']
    return result


def top_tex():
    return r'''\begin{tikzpicture}[x=1pt,y=1pt,line width=.9pt]
\path[use as bounding box](-58,-60)rectangle(59,65);
\begin{scope}[rotate=30]
\fill(-53,13)--(-39,-17)--(0,-43)--(47,-9)--(53,13)--cycle;
\draw[line width=9pt,line cap=round](0,-36)--(0,-50);
\draw[fill=white](0,13)ellipse[x radius=53,y radius=22];
\fill(0,13)ellipse[x radius=39,y radius=14];
\fill[white](0,13)ellipse[x radius=11,y radius=4.4];
\draw[line width=9pt,line cap=round](0,14)--(0,54);
\end{scope}\end{tikzpicture}'''


def cylinder_tex(art=None):
    if art is not None and 'data' in art:
        # Source ink is about 92 x 160 original pixels. The larger empty box
        # sets its source-relative size in the existing paired-note component;
        # the adjacent spinning top and common note layout are unchanged.
        g=art['data'];rx=g['radius_x'];ry=g['radius_y'];h=g['side_height']
        x0,y0,x1,y1=g['bounding_box']
        return (rf'''\begin{{tikzpicture}}[x=1pt,y=1pt,line width=.7pt]
\path[use as bounding box]({x0},{y0})rectangle({x1},{y1});
\path[fill=white](-{rx},0)--(-{rx},-{h})arc[start angle=180,end angle=360,x radius={rx},y radius={ry}]--({rx},0)--cycle;
% Rear rim: only the right-hand segment has visible scan support. The lighter
% left continuation is an explicit geometric inference, not recovered ink.
\draw[black!65,line width=.4pt,dash pattern=on .7pt off 1pt]({rx},-{h})arc[start angle=0,end angle=65,x radius={rx},y radius={ry}];
\draw[black!40,line width=.35pt,dash pattern=on .7pt off 1.4pt]({rx*math.cos(math.radians(65)):.4f},{-h+ry*math.sin(math.radians(65)):.4f})arc[start angle=65,end angle=180,x radius={rx},y radius={ry}];
\begin{{scope}}
\clip(-{rx},0)--(-{rx},-{h})arc[start angle=180,end angle=360,x radius={rx},y radius={ry}]--({rx},0)--cycle;
\fill(31,12)..controls(34,-18)and(27,-50)..(31,-75)..controls(34,-97)and(29,-112)..(34,-137)--(50,-137)--(50,15)--cycle;
\end{{scope}}
\draw(-{rx},0)--(-{rx},-{h})arc[start angle=180,end angle=360,x radius={rx},y radius={ry}]--({rx},0);
\draw[fill=white](0,0)ellipse[x radius={rx},y radius={ry}];
\begin{{scope}}\clip(0,0)ellipse[x radius=45.5,y radius=24.5];
\fill(-47,-24)..controls(-30,-20)and(-22,-17)..(-29,-7)..controls(-35,3)and(-29,17)..(-26,25)--(-52,25)--cycle;
\end{{scope}}\end{{tikzpicture}}''')
    return r'''\begin{tikzpicture}[x=1pt,y=1pt,line width=.7pt]
\path[use as bounding box](-53,-133)rectangle(53,31);
\draw[fill=white](-46,0)--(-46,-106)arc[start angle=180,end angle=360,x radius=46,y radius=23]--(46,0);
\begin{scope}
\clip(-46,0)--(-46,-106)arc[start angle=180,end angle=360,x radius=46,y radius=23]--(46,0)--cycle;
\fill(34,15)..controls(44,10)and(46,5)..(46,0)--(46,-132)--(34,-132)--cycle;
\end{scope}
\draw[fill=white](0,0)ellipse[x radius=46,y radius=23];
\begin{scope}\clip(0,0)ellipse[x radius=45.5,y radius=22.5];
\fill(-46,-22)..controls(-31,-15)and(-32,12)..(-33,23)--(-55,23)--(-55,-22)--cycle;
\end{scope}\end{tikzpicture}'''


def waist_tex(art):
    p=asset_path(art['image']).as_posix()
    return (r'\begin{tikzpicture}[x=1pt,y=1pt,line width=.65pt]'
        r'\path[use as bounding box](0,0)rectangle(162,165);'
        r'\node[anchor=south west,inner sep=0pt]at(0,0){\includegraphics[width=62pt]{'+p+'}};'
        r'\draw[line width=1.2pt,-{Triangle[length=7pt,width=5pt]}](104,51)--(62,51);'
        r'\node[anchor=west,inner sep=0pt,font=\HistoricalQuestionJapanese\fontsize{18.5}{24}\selectfont]at(109,51){\ruby{腰蓑}{こしみの}};'
        r'\end{tikzpicture}')


def graph_tex(art):
    d=art['data'];lines=[r'\begin{tikzpicture}[x=1pt,y=1pt,line width=.65pt,every node/.style={inner sep=0pt,font=\InstructionLatin\InstructionJapanese\fontsize{11}{13}\selectfont}]',
        r'\path[use as bounding box](0,0)rectangle(485,312);']
    x=lambda year:42+(year-1980)*32
    y=lambda value:30+(value-80)*1.45
    lines += [rf'\draw(42,30)--(42,{y(260):.2f});',r'\draw(42,30)--(458,30);',rf'\draw[line width=.8pt](42,{y(100):.2f})--(458,{y(100):.2f});']
    for value in range(80,261,20):
        yy=y(value);lines += [rf'\draw(42,{yy:.2f})--(46,{yy:.2f});',rf'\node[anchor=east]at(32,{yy:.2f}){{{value}}};']
    for year in range(1980,1994):
        xx=x(year);label="'"+str(year)[2:]+('年'if year==1993 else'')
        lines += [rf'\draw({xx},30)--({xx},34);',rf'\node[anchor=north]at({xx},22){{{label}}};']
    styles={'solid':'line width=.95pt','dashed':'line width=.95pt,dash pattern=on 5pt off 2.5pt',
            'dotted':'line width=1.15pt,line cap=round,dash pattern=on .01pt off 2.6pt',
            'dashdot':'line width=.95pt,dash pattern=on 5pt off 2pt on .7pt off 2pt'}
    for s in d['series']:
        coordinates='--'.join(f'({x(yr):.2f},{y(v):.2f})'for yr,v in s['points'])
        lines.append(r'\draw['+styles[s['style']]+']'+coordinates+';')
    lines += [r'\node at(398,243){テレビ};',r'\draw[line width=.9pt,-{Triangle[length=6pt,width=3.5pt]}](398,252)--(398,279);',
        r'\node at(413,181){自動車};',r'\draw[line width=.9pt,-{Triangle[length=6pt,width=3.5pt]}](413,173)--(413,146);',
        r'\node[align=left]at(345,107){テープ\\レコーダー};',r'\draw[line width=.9pt,-{Triangle[length=6pt,width=3.5pt]}](350,119)--(350,127);',
        r'\node at(395,67){ビデオテープレコーダー};',r'\draw[line width=.9pt,-{Triangle[length=5pt,width=3pt]}](350,76)--(350,87);',
        r'\end{tikzpicture}']
    return '\n'.join(lines)


def pattern_tex():
    return "\n".join([r'\pgfdeclarepatternformonly{HistoricalIron}{\pgfqpoint{-.2pt}{-.2pt}}{\pgfqpoint{1.8pt}{1.8pt}}{\pgfqpoint{1.6pt}{1.6pt}}{\pgfsetlinewidth{.3pt}\pgfpathmoveto{\pgfqpoint{0pt}{0pt}}\pgfpathlineto{\pgfqpoint{0pt}{1.6pt}}\pgfusepath{stroke}}',
           r'\pgfdeclarepatternformonly{HistoricalCopper}{\pgfqpoint{0pt}{0pt}}{\pgfqpoint{6pt}{6pt}}{\pgfqpoint{6pt}{6pt}}{\pgfpathrectangle{\pgfqpoint{0pt}{0pt}}{\pgfqpoint{3pt}{3pt}}\pgfpathrectangle{\pgfqpoint{3pt}{3pt}}{\pgfqpoint{3pt}{3pt}}\pgfusepath{fill}}'])


def pies_tex(art):
    # Clockwise from noon; use each printed value directly. No rescaling to 100.
    lines=[r'\begin{tikzpicture}[x=1pt,y=1pt,line width=.45pt,every node/.style={inner sep=0pt,font=\rmfamily\mcfamily\fontsize{10}{12}\selectfont}]',
           r'\path[use as bounding box](0,0)rectangle(320,350);']
    patterns={'鉄':'HistoricalIron','銅':'HistoricalCopper','アルミ':'dots','プラスチック':'horizontal lines','ガラス':'crosshatch','その他':None}
    centers=[(78,264),(244,264),(78,89),(244,89)];r=48
    # Positions are source-traced label/leader layouts. Small sectors are labeled
    # outside the circle; material categories and clockwise order are unchanged.
    placements=[
      [('in',92,290),('out',137,315),('out',144,290),('in',103,252),('in',57,247),('out',25,322)],
      [('in',265,264),('out',302,197),('out',193,194),('in',223,263),('out',191,321)],
      [('in',99,89),('in',55,64),('out',12,88),('out',35,153),('out',134,151)],
      [('in',266,89),('out',214,20),('out',182,35),('in',221,88),('out',190,150)],
    ]
    for chart,(cx,cy),layout in zip(art['data']['charts'],centers,placements):
        title=text_tex(chart['title']);lines.append(rf'\node[draw,minimum height=18pt,inner xsep=5pt]at({cx},{cy+75}){{{title}}};')
        start=90;labels=[]
        for cat,percent,place in zip(chart['categories'],chart['percentages'],layout):
            end=start-percent*3.6;pattern=patterns[cat]
            shape=rf'({cx},{cy})--++({start:.3f}:{r})arc[start angle={start:.3f},end angle={end:.3f},radius={r}]--cycle'
            lines.append(r'\path[fill=white]'+shape+';')
            if pattern:lines.append(r'\path[pattern='+pattern+',pattern color=black]'+shape+';')
            lines.append(r'\draw'+shape+';')
            mid=(start+end)/2;labels.append((cat,percent,place,mid));start=end
        assert abs(start+270)<.001
        for cat,percent,(kind,tx,ty),angle in labels:
            label=(r'プラス\チック'if cat=='プラスチック' else text_tex(cat))
            label=label.replace('\\チック',r'\\チック')
            value=label+r'\\'+str(percent)+r'\%'
            if kind=='out':
                px=cx+math.cos(math.radians(angle))*r;py=cy+math.sin(math.radians(angle))*r
                ex=cx+math.cos(math.radians(angle))*(r+7);ey=cy+math.sin(math.radians(angle))*(r+7)
                toward=tx+(10 if tx<cx else -10)
                lines.append(rf'\draw({px:.3f},{py:.3f})--({ex:.3f},{ey:.3f})--({toward},{ty});')
            lines.append(rf'\node[align=center,fill=white,inner sep=.7pt]at({tx},{ty}){{{value}}};')
    lines.append(r'\end{tikzpicture}');return '\n'.join(lines)


def tex(art):
    if art['kind']in ['scale_comparison_bars','conversation_opinion_lines','education_goal_bars','phone_reading_bars','employment_intent_option','score_distribution_option','smoking_distribution_option']:
        validate_art(art)
        from historical_earlier_statistical_charts import tex as chart_tex
        return chart_tex(art)
    if art['kind']in ['company_choice_lines','national_condition_lines','career_preparation_bars']:
        validate_art(art)
        from historical_late_statistical_charts import tex as late_statistical_tex
        return late_statistical_tex(art)
    if art['kind']in ['life_goals_lines','transport_radars']:
        validate_art(art)
        from historical_statistical_charts import tex as statistical_tex
        return statistical_tex(art)
    if art['kind']=='sleep_distribution_bars':
        from historical_sleep_distribution import tex as sleep_tex
        return sleep_tex(art)
    validate_art(art)
    if art['kind']=='consciousness_option':
        from historical_consciousness import tex as consciousness_tex
        return consciousness_tex(art)
    if art['kind']in ['private_room_graph','animal_group_option']:
        from historical_1993_level1_art import tex as level1_1993_tex
        return level1_1993_tex(art)
    if art['kind']=='economic_category_option':
        from historical_economic_sets import tex as category_tex
        return category_tex(art)
    if art['kind']=='university_enrolment_option':
        from historical_enrolment import tex as enrolment_tex
        return enrolment_tex(art)
    if art['kind']=='gender_equality_bars':
        from historical_stacked_bars import tex as stacked_tex
        return stacked_tex(art)
    if art['kind']=='source_label_overlay':
        from historical_label_overlays import tex as overlay_tex
        return overlay_tex(art,asset_path)
    return {'spinning_top':lambda:top_tex(),'cylinder':lambda:cylinder_tex(art),
            'annotated_waist_skirt':lambda:waist_tex(art),'purchase_graph':lambda:graph_tex(art),
            'recycling_pies':lambda:pies_tex(art),
            'metropolitan_population':lambda:population_tex(art),
            'infant_mirror':lambda:infant_mirror_tex(art),
            'household_purchase_option':lambda:household_purchase_tex(art),
            'family_relationship_option':lambda:family_relationship_tex(art)}[art['kind']]()


def n1_1997_data(kind,option=None):
    if kind=='infant_mirror':return dict(coordinate_status='approximate_digitization_not_exact_historical_data',ages=[9,12,15,18,21,24],percentages=[0,0,18.7,24.1,61.2,65.4],axis_maximum=70,citation='（Lewisら、1979より）')
    if type(option)is not int or option not in [1,2,3,4]:raise ValueError('Source diagram option must be1–4')
    if kind=='family_relationship_option':return dict(option=option,relationship_geometry='secondary536_exact_edges',appearance_status='inferred_secondary_not_approved')
    sweet=[2.02,2.18,2.36,2.49,2.49,2.43,2.43,2.56,2.88,2.92]
    fruit=[[.50,.70,1.23,1.47,1.79,2.14,2.60,3.00,3.28,3.55],[.50,.70,.82,1.01,1.21,1.42,1.73,1.99,2.23,2.35],[.50,1.02,1.18,1.81,1.97,1.63,2.03,2.23,2.36,2.41]]
    vals=[sweet,fruit[option-1]]if option<4 else[fruit[1],sweet]
    return dict(option=option,coordinate_status='approximate_digitization_not_exact_historical_data',axis_maximum=4,age_labels=['～24','25–29','30–34','35–39','40–44','45–49','50–54','55–59','60–64','65歳以上'],series=[dict(label='菓子類',pattern='north east lines',values=vals[0]),dict(label='果物類',pattern='black',values=vals[1])],shared_legend=option==1)


def n2_1997_purchase_data(option):
    """Independent primary292 digitization; do not borrow the N1 trace."""
    if type(option)is not int or option not in [1,2,3,4]:raise ValueError('Source diagram option must be1–4')
    traces=[
        [[2.01,2.19,2.38,2.49,2.49,2.41,2.43,2.55,2.83,2.86],[.5,.71,1.25,1.48,1.78,2.09,2.57,2.95,3.24,3.5]],
        [[2.02,2.2,2.36,2.49,2.48,2.43,2.4,2.55,2.84,2.9],[.53,.72,.81,1.04,1.23,1.42,1.72,1.98,2.2,2.36]],
        [[2.03,2.19,2.36,2.5,2.49,2.42,2.42,2.56,2.86,2.9],[.5,1.01,1.19,1.81,1.97,1.63,2.04,2.2,2.23,2.37]],
        [[.5,.71,.81,1.01,1.21,1.38,1.74,1.95,2.16,2.37],[2.01,2.14,2.37,2.48,2.47,2.42,2.41,2.56,2.87,2.94]]]
    return dict(option=option,coordinate_status='approximate_digitization_not_exact_historical_data',axis_maximum=4,age_labels=['～24','25–29','30–34','35–39','40–44','45–49','50–54','55–59','60–64','65歳以上'],series=[dict(label='菓子類',pattern='north east lines',values=traces[option-1][0]),dict(label='果物類',pattern='black',values=traces[option-1][1])],shared_legend=option==1)


def infant_mirror_tex(art):
    d=art['data'];p=asset_path(art['image']).as_posix()
    lines=[r'\begin{tikzpicture}[x=1pt,y=1pt,line width=.8pt,every node/.style={inner sep=0pt,font=\rmfamily\mcfamily\fontsize{14}{17}\selectfont}]',
        r'\path[use as bounding box](0,0)rectangle(825,365);',r'\draw(25,42)--(25,352);',r'\draw(25,42)--(249,42);']
    for value in range(0,71,10):
        y=42+value*4.43;lines+=[rf'\draw(25,{y:.2f})--(30,{y:.2f});',rf'\node[anchor=east]at(18,{y:.2f}){{{value}}};']
    for n,(age,value)in enumerate(zip(d['ages'],d['percentages'])):
        x=58+n*32
        if value:lines.append(rf'\draw[fill=white]({x-10},42)rectangle({x+10},{42+value*4.43:.2f});')
        lines.append(rf'\node[anchor=north]at({x},34){{{age}}};')
    lines += [r'\node at(145,7){月　齢};',r'\node[anchor=east]at(18,64){\%};',
        r'\node[anchor=west,font=\rmfamily\mcfamily\fontsize{23}{27}\selectfont]at(265,62){'+text_tex(d['citation'])+'};',
        r'\node[anchor=south west]at(630,96){\includegraphics[width=194pt]{'+p+'}};',r'\end{tikzpicture}']
    return '\n'.join(lines)


def household_purchase_tex(art):
    d=art['data'];height=390 if d['shared_legend']else 310
    lines=[r'\begin{tikzpicture}[x=1pt,y=1pt,line width=.8pt,every node/.style={inner sep=0pt,font=\HistoricalQuestionJapanese\fontsize{15}{18}\selectfont}]',rf'\path[use as bounding box](0,0)rectangle(825,{height});',r'\draw(75,60)rectangle(815,300);']
    for v in range(5):
        y=60+v*60;lines.append(rf'\node[anchor=east]at(67,{y}){{{v}}};')
        if v in [1,2,3]:lines.append(rf'\draw[densely dotted](75,{y})--(815,{y});')
    for n,label in enumerate(d['age_labels']):
        x=87+n*74
        for j,series in enumerate(d['series']):
            style='fill=black'if j else'fill=white,pattern=north east lines'
            lines.append(rf'\draw[{style}]({x+j*31},60)rectangle({x+j*31+30},{60+series["values"][n]*60:.2f});')
        lines.append(rf'\node[anchor=north]at({x+31},47){{'+text_tex(label)+'};')
    lines.append(r'\node at(445,10){世帯主の年齢};')
    for n,char in enumerate('一人当たりの年間購入金額'):lines.append(rf'\node at(15,{271-n*13}){{{char}}};')
    lines.append(r'\node[align=center]at(42,192){（万\\円）};')
    if d['shared_legend']:
        for y,label,style in [(370,'菓子類','fill=white,pattern=north east lines'),(340,'果物類','fill=black')]:
            lines += [rf'\draw[{style}](650,{y-8})rectangle(668,{y+10});',rf'\node[anchor=west,font=\HistoricalQuestionJapanese\fontsize{{21}}{{25}}\selectfont]at(680,{y}){{{label}}};']
    lines.append(r'\end{tikzpicture}');return '\n'.join(lines)


def family_relationship_tex(art):
    n=art['data']['option'];lines=[r'\begin{tikzpicture}[x=1pt,y=1pt,line width=.6pt,every node/.style={inner sep=0pt,font=\rmfamily\mcfamily\fontsize{19}{23}\selectfont}]',r'\path[use as bounding box](0,0)rectangle(400,200);']
    def node(x,y,t):lines.append(rf'\node at({x},{y}){{{t}}};')
    def line(points):lines.append(r'\draw'+'--'.join(f'({x},{y})'for x,y in points)+';')
    def couple(a,b,y):
        for dy in [-1.3,1.3]:line([(a,y+dy),(b,y+dy)])
    if n==1:
        for x,y,t in [(190,180,'義父'),(315,180,'義母'),(90,65,'高田さん'),(190,65,'妻'),(320,65,'義兄'),(145,20,'麻里')]:node(x,y,t)
        couple(211,294,180);line([(252,179),(252,130)]);line([(190,79),(190,130),(320,130),(320,79)]);couple(132,180,65);line([(145,64),(145,34)])
    elif n==2:
        for x,y,t in [(30,175,'義父'),(140,175,'義母'),(250,175,'父'),(350,175,'母'),(85,55,'義兄'),(230,55,'麻里'),(345,55,'高田さん')]:node(x,y,t)
        couple(51,119,175);couple(262,338,175);line([(85,174),(85,69)]);line([(300,174),(300,125)]);line([(230,69),(230,125),(345,125),(345,69)]);couple(106,209,55)
    elif n==3:
        for x,y,t in [(50,175,'義父'),(170,175,'義母'),(50,55,'義兄'),(170,55,'麻里'),(290,55,'高田さん')]:node(x,y,t)
        couple(71,149,175);line([(110,174),(110,125)]);line([(50,69),(50,125),(170,125),(170,69)]);couple(191,248,55)
    else:
        for x,y,t in [(30,175,'義父'),(140,175,'義母'),(245,175,'父'),(350,175,'母'),(35,55,'義兄'),(135,55,'妻'),(240,55,'高田さん'),(355,55,'麻里')]:node(x,y,t)
        couple(51,119,175);couple(257,338,175);line([(85,174),(85,125)]);line([(35,69),(35,125),(135,125),(135,69)]);line([(297,174),(297,125)]);line([(240,69),(240,125),(355,125),(355,69)]);couple(146,198,55)
    lines.append(r'\end{tikzpicture}');return '\n'.join(lines)


def population_tex(art):
    """Native data pies over an unchanged pixel map; source-relative geometry."""
    background=asset_path(art['image']).as_posix();d=art['data']
    lines=[r'\begin{tikzpicture}[x=1pt,y=1pt,line width=.6pt,every node/.style={inner sep=0pt,font=\rmfamily\mcfamily\fontsize{16}{19}\selectfont}]',
        r'\path[use as bounding box](0,0)rectangle(781,530);',
        r'\node[anchor=south west]at(0,0){\includegraphics[width=781pt,height=530pt]{'+background+'}};',
        r'\node[anchor=west,font=\HistoricalQuestionJapanese\fontsize{18}{22}\selectfont]at(40,513){'+text_tex(d['title'])+'};']
    positions=[[(140,452),(164,414),(176,379),(66,401)],[(354,442),(371,388),(355,350),(270,401)]]
    for chart,cx,places in zip(d['charts'],[110,316],positions):
        cy=406;r=87;start=90
        for j,(percent,(tx,ty))in enumerate(zip(chart['percentages'],places)):
            end=start-percent*3.6
            shape=rf'({cx},{cy})--++({start:.4f}:{r})arc[start angle={start:.4f},end angle={end:.4f},radius={r}]--cycle'
            lines.append(r'\path[fill='+('black'if j==0 else'white')+']'+shape+';')
            if j in [1,2]:lines.append(r'\path[pattern='+d['patterns'][j]+',pattern color=black]'+shape+';')
            lines.append(r'\draw'+shape+';')
            lines.append(rf'\node[fill=white,inner sep=.6pt]at({tx},{ty}){{{percent:.1f}\%}};')
            start=end
        assert abs(start+270)<.0001
        lines.append(rf'\node at({cx},299){{{chart["year"]}年}};')
    for j,label in enumerate(d['categories']):
        y=449-j*25
        lines.append(rf'\path[draw,fill='+('black'if j==0 else'white')+rf'](413,{y-6})rectangle(427,{y+8});')
        if j in [1,2]:lines.append(r'\path[pattern='+d['patterns'][j]+rf'](413,{y-6})rectangle(427,{y+8});')
        lines.append(rf'\node[anchor=west]at(436,{y}){{'+text_tex(label)+'};')
    if 'native_map_labels'in art:
        from historical_label_overlays import labels_tex
        lines.append(labels_tex({**art,'data':art['native_map_labels']}))
    lines.append(r'\end{tikzpicture}');return '\n'.join(lines)


def render(conv,key,style,block=True):
    binding=getattr(conv,'historical_artworks',{}).get(key)
    if binding is None:return None
    if not getattr(conv,'source_target_markers',False)or style is None or style['role']!='illustration':raise ValueError('Historical artwork needs an Old illustration role')
    art=binding['art'];width=str(style['width_fraction'])+r'\linewidth'
    inset=binding.get('left_inset_fraction',0)
    if inset+style['width_fraction']>1:raise ValueError('Artwork extends beyond its source-bound measure')
    if art['kind']=='raster':graphic=r'\includegraphics[width='+width+']{'+asset_path(art['image']).as_posix()+'}'
    else:graphic=r'\resizebox{'+width+r'}{!}{'+tex(art)+'}'
    conv.features.append(dict(kind='historical_authored_artwork',artwork_kind=art['kind'],artwork_id=art['id'],
        asset=binding['asset'],source_image_sha256=key,owner=binding['owner'],canonical_image_preserved=True,
        native_vectors=art['kind']!='raster',source=art['source']))
    if inset:graphic=r'\hspace*{'+str(inset)+r'\linewidth}'+graphic
    if block and binding.get('block_spacing'):
        spacing=binding['block_spacing']
        conv.features.append(dict(kind='historical_artwork_block_spacing',artwork_id=art['id'],left_inset_fraction=inset,**spacing,canonical_changed=False))
        return r'\par\addvspace{'+str(spacing['before_pt'])+r'pt}\noindent'+graphic+r'\par\nointerlineskip\addvspace{'+str(spacing['after_pt'])+r'pt}'
    # These validated room/sleep charts are immediately followed by their
    # source citation. A graphic paragraph has no text baseline to continue;
    # retain the explicit separation without adding ordinary interline glue.
    if block and art['kind']in {'private_room_graph','sleep_distribution_bars'}:
        conv.features.append(dict(kind='historical_chart_citation_spacing',artwork_id=art['id'],source=art['source'],interline_glue=False,explicit_gap_pt=8,canonical_changed=False))
        return r'\par\addvspace{8pt}\noindent'+graphic+r'\par\nointerlineskip\addvspace{8pt}'
    return r'\par\addvspace{8pt}\noindent'+graphic+r'\par\addvspace{8pt}' if block else graphic
