"""Negative contract/source-scope tests; never bless unrelated modifications."""
import copy
import json
import unittest
from pre_m10_realtime_sources import ROOT,manifest,validate_manifest,before_realtime,digest


class RealtimeCompatibilityTests(unittest.TestCase):
    def test_entire_prior_contract(self):
        spec=json.loads((ROOT/'apps/web/contracts/implemented.openapi.json').read_text())
        self.assertEqual(digest(before_realtime(spec)),manifest()['previous_openapi_sha256'])
        spec['paths']['/orgs/{organization_id}/events/history']['get']['security']=[]
        with self.assertRaises(AssertionError):before_realtime(spec)

    def test_prior_auth_contract_cannot_change(self):
        spec=json.loads((ROOT/'apps/web/contracts/implemented.openapi.json').read_text())
        spec['paths']['/auth/login']['post']['security']=[]
        spec['info']['title']='UNREVIEWED'
        with self.assertRaises(AssertionError):before_realtime(spec)

    def test_partial_stream_contract_refused(self):
        spec=json.loads((ROOT/'apps/web/contracts/implemented.openapi.json').read_text())
        del spec['paths']['/orgs/{organization_id}/events']
        with self.assertRaises(AssertionError):before_realtime(spec)

    def test_unrelated_source_and_missing_new_source_refused(self):
        value=copy.deepcopy(manifest())
        value['source_revisions']['simulations/guard5/model.py']=next(iter(value['source_revisions'].values()))
        with self.assertRaises(AssertionError):validate_manifest(value)
        value=copy.deepcopy(manifest())
        value['new_source_sha256'].pop('services/api/hydro/realtime.py')
        with self.assertRaises(AssertionError):validate_manifest(value)


if __name__=='__main__':unittest.main()
