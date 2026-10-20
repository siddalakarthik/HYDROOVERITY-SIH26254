"""Limited M02 structural/consistency validation, not application tests."""
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_text('utf-8'))
def main():
    spec=read('docs/architecture/openapi-design.json')
    db=read('data/schemas/m02-database-design.json')
    routes=read('design/ui-ux/m02-route-catalog.json')['pages']
    inventory=read('data/schemas/m02-api-inventory.json')['operations']
    tables={t['name']:t for t in db['tables']}
    errors=[]
    def require(condition,message):
        if not condition:errors.append(message)
    def walk(node):
        if isinstance(node,dict):
            if '$ref' in node:
                ref=node['$ref'];require(ref.startswith('#/'),'External reference requires separate review')
                current=spec
                try:
                    for key in ref[2:].split('/'):current=current[key]
                except KeyError:errors.append('Unresolved reference: '+ref)
            for v in node.values():walk(v)
        elif isinstance(node,list):
            for v in node:walk(v)
    walk(spec)
    ids=set()
    for path,methods in spec['paths'].items():
        for method,op in methods.items():
            require(op['operationId'] not in ids,'Duplicate operation ID')
            ids.add(op['operationId'])
            declared={p['name'] for p in op['parameters'] if p['in']=='path'}
            require(set(re.findall(r'{([^}]+)}',path))==declared,'Path parameter mismatch: '+path)
            require(bool(op.get('x-roles')) and bool(op.get('x-scope')),'Missing authorization scope: '+path)
            if method!='get':
                headers={p['name'] for p in op['parameters'] if p['in']=='header'}
                require('Idempotency-Key' in headers,'Missing idempotency: '+path)
                if op['security']!=[{'deviceBearer':[]}]:require('X-CSRF-Token' in headers,'Missing CSRF: '+path)
    require(ids=={o['id'] for o in inventory},'API inventory diverges from contract')
    for r in routes:require(set(r['operations'])<=ids,'Route references missing operation: '+r['route'])
    for t in tables.values():
        columns={c['name'] for c in t['columns']}
        require(len(columns)==len(t['columns']),'Duplicate columns: '+t['name'])
        require('id' in columns,'Missing primary ID')
        if t['scope']=='tenant':require('organization_id' in columns,'Missing tenant ownership')
        for f in t['foreign_keys']:
            require(f['target'] in tables,'Missing FK target: '+f['target'])
            require(f['column'] in columns,'Missing FK column: '+t['name'])
            if f['same_tenant']:require(tables[f['target']]['scope']=='tenant','Invalid tenant FK classification')
    for name,values in db['enums'].items():require(spec['components']['schemas'][name]['enum']==values,'Enum drift: '+name)
    observed=spec['components']['schemas']['ObservationInput']['properties']
    require(not {'source_category','environment','source_positions_m','actual_labels','truth_generation_seed'}&set(observed),'Detector/ingest truth or source override')
    require(spec['components']['schemas']['ObservationInput']['additionalProperties'] is False,'Observation allows arbitrary truth keys')
    truth_ops=[o for o in inventory if o['restricted']]
    require(len(truth_ops)==1 and truth_ops[0]['roles']==['ENGINEER+EVALUATOR'],'Truth access boundary drift')
    pages=(ROOT/'design/wireframes/PAGE_AND_WIREFRAME_SPECIFICATIONS.md').read_text('utf-8')
    require(pages.count('## Wireframe — ')==10,'Ten principal wireframes required')
    for r in routes:require(r['id'] in pages,'Missing detailed page specification')
    require(len(read('data/schemas/m02-acceptance-cases.json')['cases'])>=28,'Acceptance catalogue incomplete')
    require(spec['openapi']=='3.1.0','Expected OpenAPI3.1 design')
    for error in errors:print('FAIL:',error)
    print(f"Checked {len(tables)} tables, {len(ids)} API operations, {len(routes)} routes, enum/FK/reference/provenance consistency and ten wireframes.")
    print('Full OpenAPI validator, SQL execution and Mermaid renderer unavailable; not claimed.')
    return 1 if errors else 0
if __name__=='__main__':raise SystemExit(main())
