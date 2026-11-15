"""One question payload per unit, shared by both reader editions."""
from pathlib import Path
import json,re

SITE=Path(__file__).resolve().parents[2]/'astraJLPT'
PAGE_DATA=re.compile(r'(<script\b[^>]*\bid="page-data"[^>]*>)(.*?)(</script>)',re.S)
QUESTION_SCRIPT=re.compile(r'<script\b[^>]*\bid="question-data"[^>]*>.*?</script>',re.S)
PREFIX='globalThis.AstraQuestions = '


def asset_path(unit):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+',unit):
        raise ValueError('Invalid question asset unit: '+unit)
    return 'assets/questions/'+unit+'.js'


def encode(value):
    return json.dumps(value,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')


def question_script(unit,questions):
    return PREFIX+encode({'unit':unit,'questions':questions})+';\n'


def read_page_data(markup,site=SITE):
    data=json.loads(PAGE_DATA.search(markup)[2])
    if 'paper' in data and 'questions' not in data:
        unit=data['paper']['unit']
        text=(site/asset_path(unit)).read_text('utf8').rstrip()
        if not text.startswith(PREFIX) or not text.endswith(';'):
            raise ValueError('Invalid shared question data: '+unit)
        shared=json.loads(text[len(PREFIX):-1])
        if shared['unit']!=unit or not isinstance(shared['questions'],list):
            raise ValueError('Shared question identity differs: '+unit)
        data['questions']=shared['questions']
    return data


def shared_page_data(markup,data):
    local={key:value for key,value in data.items() if key!='questions'}
    script='<script id="question-data" src="../'+asset_path(data['paper']['unit'])+'" defer></script>'
    markup=QUESTION_SCRIPT.sub('',markup)
    return PAGE_DATA.sub(lambda m:m[1]+encode(local)+m[3]+script,markup)
