"""Validate all canonical editorial schemas, STAR coverage and release bindings."""
import collections
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parent
sys.path[:0] = [str(BASE / 'tools'), str(BASE.parent / 'rubi-restore/tools')]
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from era_registry import editorial_schema
from release_contract import contract, checked_owner
from star_answers import validate_document


def main():
    star = json.loads((BASE / 'schema/star-answer.schema.json').read_text(encoding='utf-8'))
    registry = Registry().with_resource(star['$id'], Resource.from_contents(star))
    validators = {}
    counts = collections.Counter()
    star_units = 0
    for unit in contract()['owners']:
        row = checked_owner(unit)
        path = BASE.parent / row['selection']['editorial']['path']
        editorial = json.loads(path.read_text(encoding='utf-8'))
        schema_path = editorial_schema(editorial)
        if schema_path not in validators:
            schema = json.loads(schema_path.read_text(encoding='utf-8'))
            Draft202012Validator.check_schema(schema)
            validators[schema_path] = Draft202012Validator(schema, registry=registry)
        validators[schema_path].validate(editorial)
        result = validate_document(editorial)
        counts.update(result)
        star_units += bool(result['questions'])
    print(json.dumps({'result': 'pass', 'editorial_schema_version': '4.1.0',
                      'units': len(contract()['owners']), 'star_units': star_units,
                      'star': dict(counts)}, indent=2))


if __name__ == '__main__':
    main()
