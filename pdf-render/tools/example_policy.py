"""Validate optional example refinements at the actual rendering boundary."""
BOUNDS={'ordinary_word_space_em':(0,1.5),'ordinary_label_gap_em':(0,2),
        'ordinary_before_pt':(0,30),'ordinary_top_padding_pt':(0,30),
        'bubble_glyph_size_em':(.5,1),'answer_label_width_em':(2,5),
        'answer_label_ruby_base_height_em':(.65,1)}

def validate(examples):
 for key,(low,high) in BOUNDS.items():
  if key not in examples:continue
  value=examples[key]
  if isinstance(value,bool) or not isinstance(value,(int,float)) or not low<=value<=high:
   raise ValueError('Invalid example refinement: '+key)
 if examples.get('choice_numeral_role','literal') not in ['literal','choice']:
  raise ValueError('Unknown example numeral role')

def schema():
 return {'type':'object','properties':{**{k:{'type':'number','minimum':a,'maximum':b} for k,(a,b) in BOUNDS.items()},'choice_numeral_role':{'enum':['literal','choice']}},'additionalProperties':True}
