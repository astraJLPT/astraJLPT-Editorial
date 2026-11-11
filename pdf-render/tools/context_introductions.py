"""Bind a separate introduction or numbered label to its adjacent document."""
import hashlib
import re
from model import Projection, digest


def collect(model):
    result = {}
    for section in model['document']['sections']:
        items = section['items']
        for index, item in enumerate(items):
            meta = model['layout']['items'][item['id']]
            intro = meta.get('introduction', {})
            label = meta.get('context_label')
            binding = label if label is not None else intro
            link = binding.get('following_context')
            if link is None:
                if label is not None:
                    raise ValueError('Separate label requires an exact following context')
                continue
            if (model['layout']['sections'][section['id']]['task'] != 'reading'
                    or 'content' not in item or item.get('type') == 'example'
                    or (label is None and (intro.get('role') != 'document' or intro.get('following_prefix')))
                    or meta.get('notes') or index + 1 >= len(items)):
                raise ValueError('Separate introduction must precede a reading document')
            if label is not None and any(meta.get(k) for k in
                    ['introduction', 'structured_document', 'document_role', 'document_lines', 'paragraph_breaks', 'keep_with_previous']):
                raise ValueError('Separate label cannot also own document content roles')
            if any(item['id'] in model.get('style', {}).get(name, {}) for name in
                   ['section_styles', 'block_styles', 'content_frames', 'passage_boundaries']):
                raise ValueError('Separate introduction cannot own a document frame or boundary override')
            projection = Projection(item['content']); text = projection.text
            if hashlib.sha256(text.encode()).hexdigest() != binding['projection_sha256']:
                raise ValueError('Stale separate introduction projection')
            if label is not None:
                if (text.strip() != label['text'] or projection.ruby
                        or not re.fullmatch(r'(?:\([0-9０-９]{1,2}\)|（[0-9０-９]{1,2}）)', text.strip())):
                    raise ValueError('Separate label must contain only one unannotated numbered label')
            else:
                body = re.sub(r'^\s*[（(][0-9０-９]{1,2}[）)]\s*', '', text).strip()
                if body != intro['text'] or not body.endswith('。') or '\n' in body:
                    raise ValueError('Separate introduction item contains other content')
            following = items[index + 1]
            if (following['id'] != link['id'] or 'content' not in following
                    or following.get('type') == 'example'
                    or digest(following['content']) != link['content_sha256']):
                raise ValueError('Separate introduction needs its exact adjacent context')
            following_meta = model['layout']['items'][following['id']]
            if (following_meta.get('introduction', {}).get('following_context') is not None
                    or following_meta.get('context_label') is not None):
                raise ValueError('Separate introductions cannot form chains')
            if any(model['directions'][i['id']]['render_value'] != 'horizontal-tb' for i in [item, following]):
                raise ValueError('Separate introduction requires horizontal contexts')
            if following['id'] in result:
                raise ValueError('Duplicate separate introduction destination')
            result[following['id']] = {('label_id' if label is not None else 'introduction_id'): item['id'],
                                      'context_id': following['id'],
                                      'projection_sha256': binding['projection_sha256'],
                                      'context_sha256': link['content_sha256']}
    return result
