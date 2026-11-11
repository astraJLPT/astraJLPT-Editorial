"""Checked snapshot of the accepted written release; not a new approval grant.

Reference-only witnesses are explicitly identified and never opened as local
files. All packaged inputs and the exact current annotations remain hash-bound.
"""
import copy,hashlib,json
from functools import lru_cache
from package_paths import ROOT,BASE,resource,digest_file
PATH=BASE/'contracts/accepted-release.json'
@lru_cache(maxsize=1)
def contract():
 value=json.loads(PATH.read_text('utf-8'))
 expected=(PATH.with_suffix('.sha256')).read_text('ascii').strip()
 if digest_file(PATH)!=expected:raise ValueError('Changed accepted release contract')
 if len(value['owners'])!=201:raise ValueError('Changed owner roster')
 for name,digest in value.get('runtime_inputs',{}).items():
  target=ROOT/name
  if not target.is_file() or digest_file(target)!=digest:raise ValueError('Changed accepted renderer input: '+name)
 return value
def owner(unit):
 from unit_identity import canonical_unit
 unit=canonical_unit(unit)
 try:return contract()['owners'][unit]
 except KeyError:raise ValueError('Unit outside the accepted written release: '+unit)
def check_binding(binding):
 path=resource(binding['path'])
 if not path.is_file() or digest_file(path)!=binding['sha256']:raise ValueError('Changed accepted input: '+binding['path'])
 return path
def verify_source(source_id,expected):
 record=contract()['sources'].get(source_id)
 if record is None or record['sha256']!=expected:raise ValueError('Unregistered source evidence: '+source_id)
 if record.get('packaged_path'):
  check_binding({'path':record['packaged_path'],'sha256':expected})
 elif record['role']!='frozen_evidence_reference':raise ValueError('Unavailable rendering dependency')
 return record
def identity(unit,witness=None,edition=None):
 row=owner(unit);admission=row['admission']
 if witness and admission.get('source_path'):
  if any(witness.get(k)!=admission[k] for k in ('source_path','source_sha256')):raise ValueError('Unbound public source identity')
 result=copy.deepcopy(row['public_output'])
 if edition is not None:result['internal_render_edition']=edition
 return result
def checked_owner(unit):
 row=owner(unit)
 check_binding(row['selection']['editorial']);check_binding(row['selection']['sidecar'])
 check_binding(row['selection']['defaults'])
 return row
