"""Literal authorized R02 amendment; preserve the entire prior runtime contract."""
import copy
import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = frozenset({
    '.github/workflows/repository-integrity.yml',
    'apps/web/contracts/implemented.openapi.json',
    'apps/web/src/components/ui.tsx',
    'apps/web/src/features/workspace.tsx',
    'apps/web/src/lib/generated.ts',
    'apps/web/tools/browser-suite.mjs',
    'apps/web/tools/contracts.py',
    'apps/web/tools/local_proxy.py',
    'scripts/check_pre_m10_contact.py',
    'scripts/check_pre_m10_f01.py',
    'scripts/check_pre_m10_revisit.py',
    'scripts/pre_m10_contact_sources.py',
    'scripts/pre_m10_sources.py',
    'services/api/hydro/auth.py',
    'services/api/hydro/cli.py',
    'services/api/hydro/contracts.py',
    'services/api/hydro/db.py',
    'services/api/hydro/local.py',
    'services/api/hydro/routes.py',
    'services/api/hydro/services/bookings.py',
    'services/api/tests/m09_acceptance.py',
    'services/api/tests/prem10_complaint_acceptance.py',
    'services/api/tests/prem10_contact_acceptance.py',
    'services/api/tests/test_communications.py',
    'services/api/tests/test_concurrency_resilience.py',
    'services/api/tests/test_foundation.py',
    'services/api/tests/test_schema_boundaries.py',
    'services/api/tests/test_workflow.py',
    'services/api/tools/verify_backend.py',
})
NEW = frozenset({
    'services/api/hydro/realtime.py',
    'services/api/migrations/versions/pre_m10_003.py',
    'services/api/tests/prem10_realtime_acceptance.py',
    'services/api/tools/verify_prem10_realtime.py',
    'apps/web/src/components/record-updates.tsx',
    'apps/web/src/lib/record-events.ts',
    'apps/web/tests/record-events.test.tsx',
    'apps/web/browser/realtime.spec.ts',
})
PATHS = frozenset({'/orgs/{organization_id}/events', '/orgs/{organization_id}/events/history'})
SCHEMAS = frozenset({'EventEnvelope', 'Page_EventEnvelope'})


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def validate_manifest(value):
    assert value['baseline_commit'] == '3b14b40024d424a173c60f12462ee8b1603d3221'
    assert set(value['source_revisions']) == ALLOWED, 'Unexpected realtime source scope'
    assert set(value['new_source_sha256']) == NEW, 'Unexpected new realtime source'
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
    return validate_manifest(json.loads((ROOT/'data/schemas/pre-m10-realtime-revisions.json').read_text(encoding='utf-8')))


def extend_digest(name, expected):
    row=manifest()['source_revisions'].get(name)
    if row is None:
        row_hash=manifest()['new_source_sha256'].get(name)
        if row_hash is not None:
            assert row_hash == expected, f'Unexpected prior hash for new realtime source: {name}'
        return expected
    assert row['baseline_sha256'] == expected, f'Broken realtime source chain: {name}'
    return row['sha256']


def before_realtime(spec):
    previous=copy.deepcopy(spec)
    present=PATHS.intersection(previous['paths'])
    if not present:
        assert not SCHEMAS.intersection(previous['components']['schemas'])
        return previous
    assert present == PATHS, 'Partial realtime contract'
    value=manifest()
    for path,expected in value['added_paths'].items():
        assert digest(previous['paths'][path]) == expected, path
        del previous['paths'][path]
    for name,expected in value['added_schemas'].items():
        assert digest(previous['components']['schemas'][name]) == expected, name
        del previous['components']['schemas'][name]
    assert digest(previous) == value['previous_openapi_sha256'], 'Previous 112-operation contract changed'
    return previous
