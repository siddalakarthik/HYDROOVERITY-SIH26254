"""Run only in the isolated, pinned review environment (not an app dependency)."""
from importlib.metadata import version
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from openapi_spec_validator import OpenAPIV31SpecValidator

ROOT = Path(__file__).resolve().parents[1]


def main():
    spec = json.loads((ROOT / 'docs/architecture/openapi-design.json').read_text('utf-8'))
    for package in ('openapi-spec-validator', 'openapi-schema-validator', 'jsonschema', 'referencing'):
        print(f'{package}=={version(package)}')
    # Official validator owns standards conformance, not the project checker.
    OpenAPIV31SpecValidator(spec).validate()
    for schema in spec['components']['schemas'].values():
        Draft202012Validator.check_schema(schema)
    geometry = Draft202012Validator(spec['components']['schemas']['PointGeometry'])
    assert geometry.is_valid({'type': 'Point', 'coordinates': [77.0, 12.0]})
    assert not geometry.is_valid({'type': 'Point', 'coordinates': [77.0, 12.0, 1.0]})
    assert not geometry.is_valid({'type': 'Point', 'coordinates': [181.0, 12.0]})
    print(f'OpenAPI 3.1 conformance and {len(spec["components"]["schemas"])} component metaschemas: PASS')
    print('JSON Schema 2020-12 prefixItems/items:false: valid tuple accepted; extra item/out-of-range rejected.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
