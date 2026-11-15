"""Pure font-profile preparation using already installed, pinned font subsets."""
import hashlib,json
from functools import lru_cache
from pathlib import Path
from fontTools.ttLib import TTFont
from package_paths import ROOT,BASE,resource


def role_specs(m):
    styles=m['style'];roles={'Body':{'source':'body'},'BodyBold':{'source':'bold'},'Heading':styles['font_roles']['instruction_japanese'],'Label':styles['font_roles']['boxed_numeral'],'Choice':styles['font_roles']['choice_numeral'],'Annotation':styles['font_roles']['annotation']}
    roles.update({name:styles['font_roles'][role] for name,role in [('InstructionLatin','instruction_latin'),('TaskLabelLatin','task_label'),('AsciiParen','ascii_parenthesis'),('NoticeHeading','notice_heading'),('ContactLatin','contact_latin'),('PairedLabel','paired_label'),('AnswerBubble','answer_bubble_numeral'),('Memo','memo'),('Letter','letter')]})
    roles['TaskLabelJapanese']=styles['font_roles'].get('task_label_japanese',styles['font_roles']['task_label'])
    if 'instruction_selector' in styles['font_roles']:roles['SelectorDigits']=styles['font_roles']['instruction_selector']
    if 'instruction_numeral' in styles['font_roles']:roles['AdministrativeNumerals']=styles['font_roles']['instruction_numeral']
    from workbook_typography import macro as workbook_font_macro
    roles.update({workbook_font_macro(role.removeprefix('workbook_')):spec for role,spec in styles['font_roles'].items() if role.startswith('workbook_')})
    roles.update({name:styles['font_roles'][role] for name,role in [('BodyLatin','body_latin'),('DocumentLatin','document_latin'),('NoticeLatin','notice_latin'),('NoticeLabel','notice_label'),('BodyNumeral','body_numeral'),('OptionNumeral','option_content_numeral'),('NoticeNumeral','notice_numeral')] if role in styles['font_roles']})
    roles.update({name:styles['font_roles'][role] for name,role in [('OldQuestion','historical_question_japanese'),('OldDigit','historical_question_digit'),('OldSelector','historical_instruction_digit')] if role in styles['font_roles']})
    return roles


def logical_font_target(digest,index=0):
    """Stable source identity, independent of web compression and deduplication."""
    return 'assets/fonts/'+digest[:16]+'-'+str(index)+'.woff'


@lru_cache(maxsize=128)
def _digest(path,modified,size):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def font_digest(path):
    path=Path(path);stat=path.stat()
    return _digest(path,stat.st_mtime_ns,stat.st_size)


@lru_cache(maxsize=1)
def _installed_records():
    return json.loads((BASE/'contracts/package-files.json').read_text('utf-8'))['files']


def installed_asset(logical,site):
    """Resolve an explicit source alias and verify the installed payload hash."""
    resolved=resource('astraJLPT/'+logical)
    try:target=resolved.relative_to(ROOT/'astraJLPT').as_posix()
    except ValueError:raise ValueError('Font asset escapes website: '+logical)
    if not target.startswith('assets/fonts/') or not target.endswith('.woff2'):
        raise ValueError('Unregistered WOFF2 font asset: '+logical)
    path=Path(site)/target
    if not path.is_file():raise ValueError('Missing installed font subset: '+target)
    record=_installed_records().get('astraJLPT/'+target)
    if record is None or font_digest(path)!=record['sha256']:
        raise ValueError('Changed installed font subset: '+target)
    return target


def font_face(name,target,site):
    return '@font-face{font-family:"'+name+'";src:url("'+target.removeprefix('assets/')+'?v='+font_digest(Path(site)/target)[:12]+'") format("woff2");font-display:swap;font-weight:400;}'


def installed_profile(model,site):
    """Return a profile name and bytes; never create or replace a font subset."""
    site=Path(site);styles=model['style'];bindings={};source_bindings={}
    for name,spec in role_specs(model).items():
        path=resource(spec.get('path',styles['fonts'].get(spec.get('source',''),'')))
        digest=font_digest(path)
        if spec.get('sha256') and spec['sha256']!=digest:raise ValueError('Font binding changed: '+name)
        logical=logical_font_target(digest,spec.get('font_index',0))
        target=installed_asset(logical,site)
        if name=='SelectorDigits':
            chars='1234・' if styles.get('instruction_selector',{}).get('display_digits')=='ascii' else '１２３４・'
            with TTFont(site/target) as font:
                missing=set(map(ord,chars))-set(font.getBestCmap())
            if missing:raise ValueError('Installed selector subset lacks required glyphs')
        bindings[name]=target;source_bindings[name]=logical
    signature=json.dumps(source_bindings,ensure_ascii=False,sort_keys=True,separators=(',',':'))
    target='assets/fonts-'+hashlib.sha256(signature.encode()).hexdigest()[:16]+'.css'
    rules=[font_face(name,font,site) for name,font in bindings.items()]
    rules.append(font_face('Roboto Mono',installed_asset('assets/fonts/RobotoMono-Regular.woff',site),site))
    data='\n'.join(rules).encode('utf-8')
    # Preserve the installed order of distinct @font-face rules. Historical
    # workbook profiles used a different role insertion order; reordering those
    # equivalent rules must not invalidate CSS hashes on every scoped rebuild.
    for candidate in ('assets/fonts.css',target):
        if (site/candidate).is_file():
            installed=(site/candidate).read_bytes()
            if sorted(installed.splitlines())==sorted(data.splitlines()):
                return candidate,installed
    return target,data
