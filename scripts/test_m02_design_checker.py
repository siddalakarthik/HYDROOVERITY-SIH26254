"""Mutation tests of design checks only, never backend/security execution claims."""
import copy
import unittest

from check_m02_design import load_design, validate_design

ORG = '/orgs/{organization_id}'


class DesignCheckerTests(unittest.TestCase):
    def test_valid_design_accepts_2020_12_tuple(self):
        design = load_design()
        point = design[0]['components']['schemas']['PointGeometry']['properties']['coordinates']
        self.assertIs(point['items'], False)
        self.assertEqual(len(point['prefixItems']), 2)
        self.assertEqual(validate_design(*design), [])

    def test_negative_examples(self):
        baseline = load_design()

        def op(d, path, method='get'):
            return d[0]['paths'][path][method]

        def schema(d, name):
            return d[0]['components']['schemas'][name]

        def table(d, name):
            return next(t for t in d[1]['tables'] if t['name'] == name)

        def remove_header(d, name):
            operation = op(d, '/auth/login', 'post')
            operation['parameters'] = [p for p in operation['parameters'] if p['name'] != name]

        mutations = [
            ('auth business header', lambda d: op(d, '/auth/login', 'post')['parameters'].append({'in':'header','name':'Idempotency-Key','required':True,'schema':{'type':'string'}}), 'inherits business'),
            ('auth business policy', lambda d: op(d, '/auth/reset', 'post').update({'x-retry-policy':'TENANT_7_DAY'}), 'Retry policy drift'),
            ('missing CSRF', lambda d: remove_header(d, 'X-CSRF-Token'), 'Missing required CSRF'),
            ('optional CSRF', lambda d: next(p for p in op(d, '/auth/login', 'post')['parameters'] if p['name']=='X-CSRF-Token').update({'required':False}), 'Missing required CSRF'),
            ('auth bearer CSRF bypass', lambda d: op(d, '/auth/login', 'post').update({'security':[{'deviceBearer':[]}]}), 'Cookie/preauth authentication missing'),
            ('unknown security', lambda d: op(d, '/me').update({'security':[{'unknownScheme':[]}]}), 'Broken security scheme'),
            ('optional path parameter', lambda d: op(d, ORG)['parameters'][0].update({'required':False}), 'Path parameter not required'),
            ('missing path parameter', lambda d: op(d, ORG).update({'parameters':[]}), 'Path parameter mismatch'),
            ('duplicate parameter', lambda d: op(d, ORG)['parameters'].append(copy.deepcopy(op(d, ORG)['parameters'][0])), 'Duplicate parameter'),
            ('duplicate operation ID', lambda d: op(d, '/me').update({'operationId':op(d, '/auth/csrf')['operationId']}), 'Duplicate/missing operation ID'),
            ('broken local reference', lambda d: schema(d, 'Observation')['properties'].update({'bad':{'$ref':'#/components/schemas/Absent'}}), 'Unresolved reference'),
            ('inventory method mismatch', lambda d: d[2][0].update({'method':'post'}), 'API inventory mismatch'),
            ('inventory path mismatch', lambda d: d[2][0].update({'path':'/wrong'}), 'API inventory mismatch'),
            ('inventory request mismatch', lambda d: d[2][1].update({'request':'Login'}), 'Inventory request mismatch'),
            ('inventory response mismatch', lambda d: d[2][1].update({'response':'UserView'}), 'Inventory response mismatch'),
            ('source override', lambda d: schema(d, 'ObservationInput')['properties'].update({'environment':{'type':'string'}}), 'source override'),
            ('nested source override', lambda d: schema(d, 'SimulationObservationBatch')['properties'].update({'nested':{'type':'object','properties':{'source_category':{'type':'string'}}}}), 'source override'),
            ('arbitrary observation keys', lambda d: schema(d, 'ObservationInput').update({'additionalProperties':True}), 'arbitrary properties'),
            ('missing provenance', lambda d: schema(d, 'Observation')['required'].remove('provenance'), 'loses provenance'),
            ('sim claims FIELD', lambda d: op(d, '/ingest/simulation/observations', 'post')['x-derived-provenance'].update({'environment':'FIELD'}), 'origin authority'),
            ('simulator at hardware endpoint', lambda d: op(d, '/ingest/hardware/observations', 'post').update({'x-roles':['SIMULATOR']}), 'Hardware origin authority'),
            ('ordinary truth response', lambda d: schema(d, 'RunOutput')['properties'].update({'actual_labels':{'type':'string'}}), 'exposes restricted truth'),
            ('ordinary truth seed input', lambda d: schema(d, 'SimulationParameters')['properties'].update({'truth_generation_seed':{'type':'integer'}}), 'accepts restricted truth'),
            ('truth without evaluator', lambda d: op(d, ORG+'/simulations/runs/{run_id}/evaluation').update({'x-roles':['ENGINEER']}), 'Truth access boundary'),
            ('artifact classification missing', lambda d: op(d, ORG+'/artifacts/{artifact_id}/download')['x-authorization-guards'].remove('ARTIFACT_CLASS_NONTRUTH'), 'Artifact classification'),
            ('citizen ownership missing', lambda d: op(d, ORG+'/complaints/{complaint_id}')['x-authorization-guards'].remove('CITIZEN_OWNED'), 'Citizen ownership'),
            ('technician assignment missing', lambda d: op(d, ORG+'/work-orders/{work_order_id}')['x-authorization-guards'].remove('TECHNICIAN_ASSIGNED'), 'Technician assignment'),
            ('ADMIN inherits engineer', lambda d: op(d, ORG+'/observations')['x-roles'].append('ADMIN'), 'ADMIN inherits engineering'),
            ('cross-tenant FK downgraded', lambda d: next(f for f in table(d, 'work_orders')['foreign_keys'] if f['same_tenant']).update({'same_tenant':False}), 'Tenant FK classification'),
            ('auth can cache', lambda d: next(r for status,r in op(d, '/auth/recovery', 'post')['responses'].items() if status.startswith('2'))['headers'].clear(), 'Auth response may be cached'),
            ('secret replay allowed', lambda d: next(o for methods in d[0]['paths'].values() for o in methods.values() if o.get('x-secret-replay')).pop('x-secret-replay'), 'Issued secret can be replayed'),
            ('secret stored in receipts', lambda d: table(d, 'idempotency_records')['columns'].append({'name':'response_body','type':'text','nullable':True}), 'stores secrets/bodies'),
            ('contact tenant injection', lambda d: table(d, 'project_contact_submissions')['columns'].append({'name':'organization_id','type':'uuid','nullable':False}), 'Contact fabricates'),
        ]
        for name, mutate, diagnostic in mutations:
            with self.subTest(name=name):
                design = copy.deepcopy(baseline)
                mutate(design)
                errors = validate_design(*design)
                self.assertTrue(any(diagnostic in error for error in errors), errors)
        print(f'Executed {len(mutations)} deliberate invalid-design mutation cases.')


if __name__ == '__main__':
    unittest.main()
