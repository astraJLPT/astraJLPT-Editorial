"""Pass 4 helpers. All run artifacts are local to this new directory."""
from pathlib import Path
import hashlib, json, sys

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
PREV = RUN.parent / 'ruby3-20261105'
CONTEXT = RUN.parent / 'context-20261105'
RUBY_ID = 'rubi-pass4-20261106-v1'
PDF_ID = 'pdf-written-ruby4-20261106-v1'
sys.path[:0] = [str(ROOT/'rubi-restore/tools'), str(ROOT/'pdf-render/tools')]

def load(path):
    return json.loads(Path(path).read_text('utf-8-sig'))

def digest(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def ref(path):
    p = Path(path)
    return dict(path=p.relative_to(ROOT).as_posix(), sha256=digest(p), bytes=p.stat().st_size)

def check(row):
    p = ROOT / row['path']
    assert digest(p) == row['sha256'], p
    if 'bytes' in row: assert p.stat().st_size == row['bytes'], p
    return p

def save(name, value, *, replace=False):
    p = RUN / name
    assert p.resolve().is_relative_to(RUN)
    p.parent.mkdir(parents=True, exist_ok=True)
    data = (value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=1, allow_nan=False)+'\n').encode('utf-8')
    if p.exists() and not replace:
        assert p.read_bytes() == data, f'Sealed evidence differs: {p}'
        return
    tmp = p.with_suffix(p.suffix+'.partial')
    tmp.write_bytes(data)
    tmp.replace(p)

def progress(step, state, next_action, evidence=None):
    p = RUN / 'progress.json'
    data = load(p) if p.exists() else dict(run=RUN.name, ruby_release=RUBY_ID, written_release=PDF_ID, checkpoints={})
    data['checkpoints'][step] = dict(state=state, evidence=evidence)
    data['next_action'] = next_action
    save(p.name, data, replace=True)
