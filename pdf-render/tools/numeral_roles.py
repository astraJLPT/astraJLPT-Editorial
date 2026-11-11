"""Content-digit roles, separate from Japanese text, Latin letters and furniture."""
import re
from model import digest, iter_fields

MACROS = {'body_numeral':'BodyContentNumerals',
          'option_content_numeral':'OptionContentNumerals',
          'notice_numeral':'NoticeContentNumerals'}
WRAPPER = r'\\ContentDigits\{\\(?:Body|Option|Notice)ContentNumerals\}\{([0-9０-９]+)\}'


def literal_digits(tex):
    return re.sub(WRAPPER, lambda m:m[1], tex)


def token(pattern=r'[0-9０-９]+'):
    return r'(?:'+pattern+r'|\\ContentDigits\{\\(?:Body|Option|Notice)ContentNumerals\}\{'+pattern+r'\})'


def render(text, role, escape):
    if role is None:return escape(text)
    macro=MACROS[role]
    return ''.join('\\ContentDigits{\\'+macro+'}{'+part+'}' if re.fullmatch(r'[0-9０-９]+',part) else escape(part)
                   for part in re.split(r'([0-9０-９]+)',text))


def exceptions(model):
    rows=model['style'].get('content_numeral_overrides',{})
    fields={f['owner']+'/'+f['slot']:f['value'] for f in iter_fields(model['document'])}
    for target,row in rows.items():
        if target not in fields or digest(fields[target])!=row['content_sha256']:
            raise ValueError('Stale content numeral exception: '+target)
        if row['role'] not in MACROS or not row['basis']:
            raise ValueError('Invalid content numeral exception')
        from presentation import source_binding
        source_binding(model['unit'],row['evidence'])
    return rows
