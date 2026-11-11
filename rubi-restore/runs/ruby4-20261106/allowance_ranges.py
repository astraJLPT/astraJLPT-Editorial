from common import *
from allowances import forecast,allocate
cells=load(RUN/'coverage/cells.json');rows=load(RUN/'coverage/before-sections.json')
for grid in [True,False]:
    name='with-grid' if grid else 'without-grid';ranges=[]
    calculated=forecast(cells,rows,grid,ranges);papers=allocate(calculated)
    assert calculated==load(RUN/f'coverage/{name}-sections.json')
    assert papers==load(RUN/f'coverage/{name}-papers.json')
    save(f'coverage/{name}-paper-ranges.json',ranges)
    print(name,'ranges',len(ranges),'existing estimates and allowances unchanged',flush=True)
