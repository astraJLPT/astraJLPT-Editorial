"""Regenerate the accepted written editions using paths relative to this checkout."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent/'tools'))
from package_paths import ROOT,BASE,engine
from release_contract import contract
from model import compose
from build import generate,environment

def render(unit,variant,compile_pdf=True):
    from unit_identity import canonical_unit
    unit=canonical_unit(unit)
    model=compose(unit,variant=variant)
    work=BASE/'work'/unit/variant
    work.mkdir(parents=True,exist_ok=True)
    (BASE/'runtime/fonts').mkdir(parents=True,exist_ok=True)
    (work/'paper.tex').write_text(generate(model,work),encoding='utf-8')
    if not compile_pdf:return {'unit':unit,'variant':variant,'status':'native-tex-validated'}
    env=environment()
    for pass_number in (1,2):
        log=work/f'compile-{pass_number}.txt'
        with log.open('w',encoding='utf-8') as stream:
            result=subprocess.run([str(engine()),'-no-shell-escape','-interaction=nonstopmode','-halt-on-error','-file-line-error','-recorder','paper.tex'],cwd=work,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=300)
        if result.returncode:raise RuntimeError(f'LuaLaTeX failed; inspect {log}')
    from public_paths import RENAMED,stem
    name=stem(unit)+('.norubi' if variant=='norubi' and unit in RENAMED else '' )+'.pdf' if unit in RENAMED else unit+'.'+model['public_output']['class']+'.pdf'
    target=BASE/('outputnorubi' if variant=='norubi' else 'output')/name
    target.parent.mkdir(exist_ok=True)
    if model['layout'].get('booklets'):
        from assemble import assemble
    else:
        from era_registry import for_unit
        assemble=for_unit(unit).assemble
    model['assembly']=assemble(model,work/'paper.pdf',target,work,env)
    record={'unit':unit,'variant':variant,'path':target.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
    (work/'result.json').write_text(json.dumps(record,indent=2)+'\n')
    return record

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    from unit_identity import ALIASES
    parser.add_argument('--unit',action='append',choices=tuple(contract()['owners'])+tuple(ALIASES))
    parser.add_argument('--all',action='store_true')
    parser.add_argument('--variant',choices=['regular','norubi','both'],default='both')
    parser.add_argument('--no-compile',action='store_true',help='Validate all native emission guards and write TeX only')
    args=parser.parse_args()
    units=list(contract()['owners']) if args.all else args.unit
    if not units:parser.error('Choose --unit or --all')
    variants=['regular','norubi'] if args.variant=='both' else [args.variant]
    for unit in units:
        for variant in variants:print(json.dumps(render(unit,variant,not args.no_compile)),flush=True)
if __name__=='__main__':main()
