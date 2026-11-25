"""Paths are rooted at this checkout, independently of the current directory."""
import hashlib,json,os,re,shutil
from pathlib import Path
from functools import lru_cache
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'pdf-render'
@lru_cache(maxsize=1)
def mappings():return json.loads((BASE/'contracts/resource-map.json').read_text('utf-8'))
def source_identity(value):
 """Normalize frozen source-set names; these identities are not local files."""
 match=re.fullmatch(r'preprocess/N[1-5]/([^/]+)/principal_source_set_\1\.json',value or '')
 return 'source-set:'+match[1] if match else value

def resource(value):
 if str(value).startswith('source-set:'):raise ValueError('Reference-only source identity is not a file')
 p=Path(value)
 if p.is_absolute():
  if not p.resolve().is_relative_to(ROOT):raise ValueError('Resource outside checkout: '+str(p))
  value=p.relative_to(ROOT).as_posix()
 else:value=p.as_posix()
 mapped=mappings().get(value)
 if mapped is None:
  for old,new in [('schema-v3/','pdf-render/schema/'),('preprocess/','editorial-json/')]:
   if value.startswith(old):value=new+value[len(old):];break
  mapped=value
 target=(ROOT/mapped).resolve()
 if not target.is_relative_to(ROOT):raise ValueError('Resource escapes checkout')
 return target
def engine():
 candidate=os.environ.get('ASTRAJLPT_LUALATEX') or shutil.which('lualatex')
 if not candidate:raise RuntimeError('Install LuaLaTeX and add it to PATH, or set ASTRAJLPT_LUALATEX')
 return Path(candidate).resolve()
def digest_file(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
