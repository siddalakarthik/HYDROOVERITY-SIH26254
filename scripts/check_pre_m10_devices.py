"""Verify explicit source scope, additive contract and accurate device inventory."""
import hashlib
import sys
from pre_m10_devices_sources import ROOT, manifest, before_devices
from pre_m10_docs_sources import extend_digest



def main():
    value=manifest()
    expected={name:row['sha256'] for name,row in value['source_revisions'].items()}
    expected.update(value['new_source_sha256'])
    for name,sha in expected.items():
        assert hashlib.sha256((ROOT/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()==extend_digest(name,sha), name
    sys.path.insert(0,str(ROOT/'services/api'))
    from hydro.contracts import runtime_openapi, OPERATIONS
    from hydro.db import MIGRATION_HEAD
    spec=runtime_openapi()
    assert len(OPERATIONS)==58 and sum(len(ms) for ms in spec['paths'].values())==119
    assert MIGRATION_HEAD=='pre_m10_004'
    before_devices(spec)
    assert 'EvaluationResult' not in spec['components']['schemas']
    print('PASS: all114 previous operations preserved; five device operations,57 tables; frozen scientific sources unchanged')


if __name__=='__main__':main()
