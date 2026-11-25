"""Exact accepted modern roster, frozen after full source release validation."""
from release_contract import contract,PATH as SCOPE_PATH
SCOPE=contract()['modern_scope']
UNITS=tuple(u for u in contract()['owners'] if int(u[-4:])>=2010 or 'sample' in u)
ENTRIES={u:contract()['owners'][u]['admission'] for u in UNITS}
PILOT=tuple(u for u in UNITS if ENTRIES[u].get('existing_pilot'))
WAVES=SCOPE.get('waves',[])
def read_scope():return SCOPE
