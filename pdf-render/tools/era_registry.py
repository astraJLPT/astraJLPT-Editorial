"""Neutral dispatch between independently maintained exam-era contracts."""
import importlib
import re


def for_unit(unit):
    from unit_identity import legacy_unit
    unit = legacy_unit(unit)
    from h28_identity import SAMPLES
    if unit in SAMPLES:
        return importlib.import_module('modern_era')
    match = re.fullmatch(r'N([1-5])_(?:(07|12)_)?(\d{4})', unit)
    if not match:
        raise ValueError('Invalid owner identifier')
    level, month, year = match.groups()
    year = int(year)
    if 2010 <= year <= 2026 and month:
        return importlib.import_module('modern_era')
    if (1991 <= year <= 2009 and int(level) <= 4) or unit == 'N4_1990':
        return importlib.import_module('historical_era')
    raise ValueError('Outside supported exam eras')


def for_editorial(editorial):
    era = for_unit(editorial['unit'])
    if editorial['exam']['generation'] != era.GENERATION:
        raise ValueError('Exam generation differs from owner era')
    return era


def editorial_schema(editorial):
    return for_editorial(editorial).SCHEMA_ROOT / 'editorial.schema.json'
