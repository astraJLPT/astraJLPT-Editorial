"""Exact frozen file/page approval records, with no new source approval."""
import json
from package_paths import BASE,digest_file
from release_contract import verify_source
REGISTRY=BASE/'contracts/reference-approvals.json'
def sha(path):return digest_file(path)
def registry_sha():return json.loads(REGISTRY.read_text('utf-8'))['original_registry_sha256']
def full_source_records(text=None):
 if text is not None:raise ValueError('Use an explicitly reviewed contract to change approvals')
 rows=json.loads(REGISTRY.read_text('utf-8'))['records']
 return {(r['source_path'],r['source_sha256']):r for r in rows}
def approved_reference(witness):
 result=full_source_records().get((witness.get('source_path'),witness.get('source_sha256')))
 if result is not None:
  verify_source(result['source_path'],result['source_sha256'])
  return {**result,'approval_registry':{'path':'pdf-render/contracts/reference-approvals.json','sha256':registry_sha()},
   'scope':'Approved question-page appearance only; registry exclusions apply. No custody, key-correctness, completeness or original-sheet-size claim.'}
 return None
