"""Optional field-bound restoration sidecars over the current editorial only."""
import copy
import html
import re

from ruby_core import Projection, iter_fields, protected, resolve, KANJI_RE, PROJECTION_VERSION
from current_editorial import digest
from ruby_release_policy import is_current, validate_derivative_overlay


def apply_current_overlay(document, overlay, *, scope_document=None, expected_release=None):
    if (overlay.get('overlay_schema_version') != 2 or
            overlay.get('binding') != 'current-editorial-fields-v1' or
            overlay.get('projection_version') != PROJECTION_VERSION):
        raise ValueError('Unsupported current ruby sidecar contract')
    if overlay.get('unit_id') != document['unit']:
        raise ValueError('Ruby sidecar belongs to a different owner')
    release=overlay.get('release_id')
    if not release or (expected_release is not None and release!=expected_release):
        raise ValueError('Mixed or missing selected ruby release')
    new=is_current(release)
    if not new and release!='rubi-first-pass-20261009-v1':
        raise ValueError('Unknown current ruby release family')
    if new:
        from ruby2_scope import iter_current,protect
        authority=scope_document or document
        if authority.get('unit')!=document['unit'] or not ('layout' in authority and 'exam' in authority):
            raise ValueError('Current-v3 semantic scope required for selected release')
        fields={f['pointer']:f for f in iter_current(authority)}
        base={f['pointer']:f for f in iter_fields(document)}
        if set(fields)!=set(base):raise ValueError('Current field surface differs from release scope')
        for p,f in fields.items():f['value']=base[p]['value']
    else:fields = {f['pointer']: f for f in iter_fields(document)}
    if any('data-rubi-origin' in str(f['value']) for f in fields.values()):
        raise ValueError('Current editorial already contains project-restored ruby')
    allowed_releases=validate_derivative_overlay(overlay)
    groups, seen = {}, set()
    for annotation in overlay['annotations']:
        if annotation.get('release_id') not in allowed_releases:
            raise ValueError('Mixed annotation release in selected sidecar')
        if new and (annotation.get('basis')!='inferred' or not annotation.get('review_record_id') or annotation.get('score_is_calibrated_probability') is not False):
            raise ValueError('Missing selected inference/review provenance')
        aid = annotation['annotation_id']
        if aid in seen:
            raise ValueError('Duplicate restoration annotation identity')
        seen.add(aid)
        if annotation['origin'] != 'project_rubi_restore' or annotation['decision'] != 'accepted':
            raise ValueError('Unsupported restoration origin or decision')
        groups.setdefault(annotation['pointer'], []).append(annotation)
    out = copy.deepcopy(document)
    for pointer, annotations in groups.items():
        if pointer not in fields:
            raise ValueError('Stale ruby target: missing current field '+pointer)
        field = fields[pointer]
        projection = Projection(field['value'])
        inserts, previous_end = [], -1
        for annotation in sorted(annotations, key=lambda a: a['start']):
            if (annotation['section_id'], annotation['owner_id'], annotation['field']) != (
                    field['section'], field['owner'], field['slot']):
                raise ValueError('Stale ruby owner/section/field identity: '+pointer)
            if annotation['field_sha256'] != digest(field['value']):
                raise ValueError('Stale ruby sidecar: current field changed at '+pointer)
            start, end = annotation['start'], annotation['end']
            if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(projection.text):
                raise ValueError('Invalid ruby span: '+pointer)
            if start < previous_end:
                raise ValueError('Overlapping restoration annotations')
            previous_end = end
            if projection.text[start:end] != annotation['base'] or not KANJI_RE.search(annotation['base']):
                raise ValueError('Changed ruby base: '+pointer)
            if not annotation['reading'] or re.search(r'[^\u3040-\u309f\u30fc]', annotation['reading']):
                raise ValueError('Invalid ruby reading')
            if projection.overlaps_ruby(start, end):
                raise ValueError('Restoration would overwrite editorial ruby')
            if (protect(field,projection,start,end) if new else protected(field, document['unit'][:2], projection, start, end)):
                raise ValueError('Restoration targets a protected task span: '+pointer)
            lo, hi = projection.raw_span(start, end)
            inserts.append((lo, hi, annotation))
        raw = projection.raw
        if not projection.is_html:
            inserts = [(len(html.escape(raw[:lo], quote=False)),
                        len(html.escape(raw[:hi], quote=False)), a) for lo, hi, a in inserts]
            raw = html.escape(raw, quote=False)
        for lo, hi, annotation in sorted(inserts, reverse=True, key=lambda row: row[0]):
            aid = html.escape(annotation['annotation_id'], quote=True)
            raw = (raw[:lo] + '<ruby data-rubi-origin="project_rubi_restore" data-rubi-id="'+aid+'">' +
                   raw[lo:hi] + '<rt>'+html.escape(annotation['reading'])+'</rt></ruby>'+raw[hi:])
        parent, key = resolve(out, pointer)
        parent[key] = {'html': raw}
        if Projection(parent[key]).text != projection.text:
            raise ValueError('Ruby application changed underlying text')
    return out
