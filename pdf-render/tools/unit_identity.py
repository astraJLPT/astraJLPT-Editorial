"""Current unit IDs and stable historical/browser identities for the release."""
import json
from pathlib import Path

PATH = Path(__file__).resolve().parents[2] / 'editorial-json/unit_aliases.json'
ALIASES = json.loads(PATH.read_text('utf-8'))['aliases']
LEGACY = {current: old for old, current in ALIASES.items()}
if len(LEGACY) != len(ALIASES):
    raise ValueError('Ambiguous unit alias map')

def canonical_unit(unit):
    return ALIASES.get(unit, unit)

def legacy_unit(unit):
    """Original evidence/storage ID; its date is not a publication claim."""
    return LEGACY.get(unit, unit)
