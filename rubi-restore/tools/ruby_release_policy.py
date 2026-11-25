"""Final release acceptance; canonical annotation checks remain in current_ruby."""
import hashlib,json
TYPOGRAPHY='rubi-typography-20261109-v1'
def is_current(release):return release==TYPOGRAPHY
def is_expanded(release):return release==TYPOGRAPHY
def validate_derivative_overlay(overlay):
 from release_contract import owner
 row=owner(overlay['unit_id'])
 encoded=json.dumps(overlay['annotations'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
 if overlay['release_id']!=TYPOGRAPHY or hashlib.sha256(encoded).hexdigest()!=row['annotations_sha256']:
  raise ValueError('Accepted final annotations changed; explicit revalidation required')
 if len(overlay['annotations'])!=row['annotation_count']:raise ValueError('Changed annotation count')
 return set(row['allowed_annotation_releases'])
