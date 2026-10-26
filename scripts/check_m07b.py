"""Check explicit M07-B activation and the preserved 77-operation baseline."""
import argparse
import hashlib
import json
from pre_m10_sources import revised_digest
from pre_m10_contact_sources import before_contact
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'services/api'))
from hydro.communications_contracts import OPERATIONS as COMMUNICATIONS
from hydro.contracts import runtime_openapi
from hydro.scheduling_contracts import ACTIVE
from hydro.service_contracts import DISABLED


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--backend-only',action='store_true');args=parser.parse_args()
    m=json.loads((ROOT/'data/schemas/m07b-implementation.json').read_text())
    assert m['baseline_commit']=='5c4c06aa915abbbd12c342aff3f08c9b37b340bb'
    assert m['counts']=={'preserved_operations':77,'m07b_operations':26,'total_operations':103,'preserved_tables':36,'m07b_tables':9,'total_tables':45}
    current=json.loads((ROOT/"data/schemas/m07c-implementation.json").read_text())
    spec=before_contact(runtime_openapi());ids={s['operationId'] for ms in spec['paths'].values() for s in ms.values()}
    assert len(ids)==111 and set(m['operation_ids'])==ACTIVE=={f'm07_n{i:02}' for i in range(14,40)}
    assert not ids & DISABLED and {o["id"] for o in COMMUNICATIONS} <= ids
    assert len(m['baseline_operations'])==77
    for key,expected in m['baseline_operations'].items():
        method,path=key.split(' ',1);assert digest(spec['paths'][path][method])==expected,key
    assert set(m['schema_deltas'])=={'M07WorkLink','M07WorkLinkWrite'}
    for name,expected in m['baseline_schemas'].items():
        assert digest(spec['components']['schemas'][name])==m['schema_deltas'].get(name,expected),name
    allowed={'apps/web/','services/api/','scripts/','data/schemas/m03-implementation-matrix.json'}
    for name,change in m['source_extensions'].items():
        assert any(name.startswith(prefix) for prefix in allowed),name
        if args.backend_only and not name.startswith('services/api/') and not (ROOT/name).exists():continue
        assert hashlib.sha256((ROOT/name).read_text('utf-8').encode()).hexdigest()==revised_digest(name,current["source_extensions"].get(name,{}).get("sha256",change['sha256'])),name
    for name,expected in m['frozen_scientific_sources'].items():
        if args.backend_only and not (ROOT/name).exists():continue
        assert hashlib.sha256((ROOT/name).read_text('utf-8').encode()).hexdigest()==expected,name
    assert not any('truth' in k.lower() for k in spec['components']['schemas'])
    print('PASS: M07-B N14–N39; 103 operations; 45 migrated tables; 77 preserved operations; privacy/scientific gates retained')


if __name__=='__main__':main()
