"""Source-observed1992–1994 registration cells and stacked field labels."""
VARIANT='seven_cell_registration_1992_1994'


def validate(cover):
    p=cover['printed']
    observed=(p['year_text']in {'1992','1993','1994'} and
              p['family']in {'four_instruction','bilingual_four_instruction'})
    if not observed:
        if 'field_layout'in p:raise ValueError('Seven-cell field variant requires its observed date/family')
        return False
    if (p.get('field_layout')!=VARIANT or cover['status']!='source_transcribed' or
            not cover.get('source')or p['level_number']not in [1,2,3,4]):
        raise ValueError('Observed1992–1994cover is missing its seven-cell registration field binding')
    english=not(p['year_text']=='1992'and p['level_number']in [1,2])
    labels=p['labels']
    if p.get('english_field_labels_observed')is not english:
        raise ValueError('Date/level field-label language differs from the inspected source')
    if english:
        if labels.get('registration_english')!='Examinee\nRegistration No.'or labels.get('name_english')!='Name':
            raise ValueError('Seven-cell cover requires exact stacked English field labels')
    elif any(k in labels for k in ['registration_english','name_english']):
        raise ValueError('Japanese-only1992field labels cannot invent English')
    return True


def generate(cover,profile,family,line,rect,rule,rich,escape):
    if not validate(cover):return False
    p=cover['printed'];v=profile['field_layouts'][VARIANT];g=family['geometry'];s=family['type']
    labels=p['labels'];english=p['english_field_labels_observed'];x=g['frame_mm'][0]+(g['frame_mm'][2]-v['name_width_mm'])/2
    y=g['registration_y_mm'];w=v['registration_width_mm'];h=v['height_mm'];split=v['registration_label_width_mm']
    rect(x,y,w,h,.65)
    for i in range(7):
        xx=x+split+(w-split)*i/7;rule(xx,y,xx,y+h,.45)
    ny=y+v['row_top_step_mm'];nw=v['name_width_mm'];ns=v['name_label_width_mm']
    rect(x,ny,nw,h,.65);rule(x+ns,ny,x+ns,ny+h,.45)
    if english:
        line(x+2,y+4.5,rich(labels['registration']),s['field_bp'],'Mincho',ruby_size=.45)
        for j,t in enumerate(labels['registration_english'].split('\n')):
            line(x+2,y+7.4+j*2.8,escape(t),v['registration_english_bp'],'Latin')
        line(x+2,ny+5.2,rich(labels['name']),s['field_bp'],'Mincho',ruby_size=.45)
        line(x+2,ny+9.8,escape(labels['name_english']),v['name_english_bp'],'Latin')
    else:
        line(x+2,y+h*.62,rich(labels['registration']),s['field_bp'],'Mincho',ruby_size=.45)
        line(x+2,ny+h*.62,rich(labels['name']),s['field_bp'],'Mincho',ruby_size=.45)
    return True
