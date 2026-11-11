"""Exact links from one paired passage to definitions printed after its peer."""
from model import Projection, digest


def prepare(conv, model, item, value, binding):
    if digest(item['content']) != binding['content_sha256']:
        raise ValueError('Stale shared-note passage')
    before, current = Projection(item['content']), Projection(value)
    signature = lambda p: [(r['start'], r['end'], r['base'], r['reading']) for r in p.ruby]
    if before.text != current.text or signature(before) != signature(current):
        raise ValueError('Shared-note coordinates changed during presentation')
    sections = [s for s in model['document']['sections'] if any(i['id'] == item['id'] for i in s['items'])]
    if len(sections) != 1 or model['layout']['sections'][sections[0]['id']]['task'] != 'paired_reading':
        raise ValueError('Shared notes require one paired-reading section')
    sequence = sections[0]['items']
    target_index = next(n for n, i in enumerate(sequence) if i['id'] == item['id'])
    matches = [(n, i) for n, i in enumerate(sequence) if i['id'] == binding['definitions_item']]
    if len(matches) != 1 or matches[0][0] <= target_index or 'notes' in model['layout']['items'][item['id']]:
        raise ValueError('Shared definitions must follow this passage without a local note cluster')
    source = matches[0][1]
    if 'content' not in source or digest(source['content']) != binding['definitions_content_sha256']:
        raise ValueError('Stale shared-note definition content')
    notes = model['layout']['items'][source['id']].get('notes')
    if not notes or not binding['anchors']:
        raise ValueError('Shared notes require confirmed definitions and exact anchors')
    _, definitions = conv.split_notes(source['content'], notes)
    # Reuse the proven markup transform, including its ruby/underline checks.
    result = conv.note_markers(value, definitions, binding['anchors'])
    conv.features.append({'kind': 'shared_note_anchors', 'item': item['id'],
                          'definitions_item': source['id'], 'anchors': len(binding['anchors']),
                          'definitions_printed_here': False})
    return result
