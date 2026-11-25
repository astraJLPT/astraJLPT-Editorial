"""Line-break protection for short, spaced groups in modern beginner papers."""
import re

from bs4 import NavigableString, Tag


def spaced_task(model, task):
    level = model['unit'][:2]
    modern = model.get('exam', {}).get('generation', 'modern-2010') == 'modern-2010'
    return modern and (level == 'N5' or level == 'N4' and task not in
                       {'reading', 'paired_reading', 'information_retrieval'})


JAPANESE = r'ぁ-ゖァ-ヶー一-龯々〆'
GROUP = re.compile(rf'[「『（]?[{JAPANESE}0-9０-９]+[、。？！]?[」』）]?')
PIECES = re.compile(r'([\s　]+|[、。？！][」』）]?)')
STOP = '、。？！'
INLINE = {'ruby', 'u', 'b', 'strong', 'em', 'i', 'span'}
INLINE_CLASSES = {'tex-latin', 'heading-no-break', 'heading-punctuation', 'content-digits',
                  'instruction-digit', 'mixed-before', 'mixed-after'}
PROSE = {'p', 'div', 'section', 'blockquote', 'ol', 'ul', 'li', 'center',
         'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'table', 'tr', 'td', 'th', 'tbody', 'thead',
         'u', 'b', 'strong', 'em', 'i'}


def short_group(text):
    return bool(1 < len(text) <= 12 and GROUP.fullmatch(text) and re.search(f'[{JAPANESE}]', text))


def classes(node):
    value = node.get('class', [])
    return value.split() if isinstance(value, str) else value


def bind_groups(soup, *, web):
    """Join base text across ruby and emphasis; leave separators outside the group."""
    def inline_text(node):
        if node.name not in INLINE:
            return ''
        if node.name == 'span':
            roles = set(classes(node))
            if roles & {'content-digits', 'instruction-digit'}:
                digits = node.get_text()
                return digits if re.fullmatch('[0-9０-９]+', digits) else ''
            if not (roles & INLINE_CLASSES or node.has_attr('data-workbook-font')
                    or (not node.attrs)):
                return ''
        if node.name == 'ruby':
            return ''.join(str(c) if isinstance(c, NavigableString) else c.get_text()
                           for c in node.children if c.name not in ('rt', 'rp'))
        parts = [str(c) if isinstance(c, NavigableString) else inline_text(c) for c in node.children]
        return ''.join(parts) if all(parts) else ''

    def visit(parent):
        output, word, bases = [], [], []

        def flush():
            text = ''.join(bases)
            # Native text() already boxes a plain group; HTML needs explicit protection.
            inline = len(word) == 1 and isinstance(word[0], Tag)
            if short_group(text) and (web or len(word) > 1 or inline) and not (
                    inline and 'heading-no-break' in classes(word[0])):
                wrapper = soup.new_tag('span')
                if web:
                    wrapper['class'] = 'wakachi'
                else:
                    wrapper['data-bounded-word'] = 'exact-source-group'
                for piece in word:
                    wrapper.append(piece)
                output.append(wrapper)
            else:
                output.extend(word)
            word.clear()
            bases.clear()

        for node in list(parent.children):
            if isinstance(node, NavigableString):
                parts = [(NavigableString(s), s) for s in PIECES.split(str(node)) if s]
            else:
                base = inline_text(node)
                if not base or re.search(r'[\s　]', base):
                    flush()
                    # Only descend into prose and emphasis. A layout box, its displayed
                    # duplicate, a selector or a ruby reading has its own break policy.
                    if node.name in PROSE or (node.name == 'span' and (
                            base or node.has_attr('data-workbook-font') or not node.attrs)):
                        visit(node)
                    output.append(node)
                    continue
                parts = [(node, base)]
            for part, base in parts:
                if base.isspace():
                    flush()
                    output.append(part)
                else:
                    word.append(part)
                    bases.append(base)
                    if base.rstrip('」』）').endswith(tuple(STOP)):
                        flush()
        flush()
        parent.clear()
        for index, node in enumerate(output):
            if (not web and isinstance(node, NavigableString) and str(node) == '　'
                    and 0 < index < len(output) - 1 and
                    all(isinstance(part, NavigableString) or part.name in INLINE
                        for part in (output[index-1], output[index+1]))):
                gap = soup.new_tag('span', attrs={'data-wakachi-wide-gap': 'true'})
                gap.append(node)
                node = gap
            parent.append(node)

    visit(soup)
    soup.smooth()
