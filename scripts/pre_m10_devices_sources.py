"""Literal authorized device amendment; preserve the entire prior runtime contract."""
import copy
import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = frozenset({
    '.github/workflows/repository-integrity.yml',
    'apps/web/browser/workflow.spec.ts',
    'apps/web/contracts/implemented.openapi.json',
    'apps/web/src/features/workspace.tsx',
    'apps/web/src/lib/generated.ts',
    'apps/web/src/lib/route-capabilities.json',
    'apps/web/tools/browser-suite.mjs',
    'apps/web/tools/contracts.py',
    'scripts/check_pre_m10_realtime.py',
    'scripts/pre_m10_realtime_sources.py',
    'services/api/hydro/cli.py',
    'services/api/hydro/contracts.py',
    'services/api/hydro/db.py',
    'services/api/hydro/routes.py',
    'services/api/tests/m09_acceptance.py',
    'services/api/tests/prem10_complaint_acceptance.py',
    'services/api/tests/prem10_contact_acceptance.py',
    'services/api/tests/prem10_realtime_acceptance.py',
    'services/api/tests/test_communications.py',
    'services/api/tests/test_concurrency_resilience.py',
    'services/api/tests/test_foundation.py',
    'services/api/tests/test_schema_boundaries.py',
    'services/api/tests/test_workflow.py',
    'services/api/tools/verify_backend.py',
})
NEW = frozenset({
    'services/api/hydro/device_credentials.py',
    'services/api/migrations/versions/pre_m10_004.py',
    'services/api/tests/prem10_device_acceptance.py',
    'services/api/tools/verify_prem10_devices.py',
    'apps/web/src/features/devices.tsx',
    'apps/web/browser/devices.spec.ts',
})
PATHS = frozenset({'/orgs/{organization_id}/devices', '/orgs/{organization_id}/devices/{device_id}', '/orgs/{organization_id}/devices/{device_id}/credentials', '/orgs/{organization_id}/devices/{device_id}/credentials/{credential_id}'})
SCHEMAS = frozenset({'CredentialView', 'DeviceWrite', 'CredentialIssue', 'Device', 'DeviceHealth', 'Page_Device'})



def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def validate_manifest(value):
    assert value['baseline_commit'] == '506e9ed64f69d36703cc958350ef6c32bebaeb91'
    assert set(value['source_revisions']) == ALLOWED, 'Unexpected devices source scope'
    assert set(value['new_source_sha256']) == NEW, 'Unexpected new devices source'
    assert set(value['added_paths']) == PATHS and set(value['added_schemas']) == SCHEMAS
    for name,row in value['source_revisions'].items():
        assert row['reason'].strip(), name
        for key in ('baseline_sha256','sha256'):
            assert re.fullmatch(r'[a-f0-9]{64}',row[key]), name
        assert row['baseline_sha256'] != row['sha256'], name
    for expected in [*value['new_source_sha256'].values(),*value['added_paths'].values(),*value['added_schemas'].values(),value['previous_openapi_sha256']]:
        assert re.fullmatch(r'[a-f0-9]{64}',expected)
    return value


@lru_cache(maxsize=1)
def manifest():
    return validate_manifest(json.loads((ROOT/'data/schemas/pre-m10-devices-revisions.json').read_text(encoding='utf-8')))


def extend_digest(name, expected):
    row=manifest()['source_revisions'].get(name)
    if row is None:
        row_hash=manifest()['new_source_sha256'].get(name)
        if row_hash is not None:
            assert row_hash == expected, f'Unexpected prior hash for new devices source: {name}'
        return expected
    assert row['baseline_sha256'] == expected, f'Broken devices source chain: {name}'
    return row['sha256']


def before_devices(spec):
    previous=copy.deepcopy(spec)
    present=PATHS.intersection(previous['paths'])
    if not present:
        assert not SCHEMAS.intersection(previous['components']['schemas'])
        return previous
    assert present == PATHS, 'Partial devices contract'
    value=manifest()
    for path,expected in value['added_paths'].items():
        assert digest(previous['paths'][path]) == expected, path
        del previous['paths'][path]
    for name,expected in value['added_schemas'].items():
        assert digest(previous['components']['schemas'][name]) == expected, name
        del previous['components']['schemas'][name]
    assert digest(previous) == value['previous_openapi_sha256'], 'Previous 114-operation contract changed'
    return previous


_device_digest = extend_digest

def extend_digest(name, expected):
    from pre_m10_docs_sources import extend_digest as extend_docs
    return extend_docs(name, _device_digest(name, expected))
