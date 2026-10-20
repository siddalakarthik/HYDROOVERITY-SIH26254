"""Project-specific design checks; independent conformance and runtime tests are separate."""
import json
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
METHODS={'get','post','put','patch','delete','head','options','trace'}
TRUTH={'source_positions_m','actual_labels','truth_generation_seed','truth_seed','truth_manifest_hash'}
SOURCE={'source_category','environment','source_environment','hardware_tested','field_validated'}
def read(path):return json.loads((ROOT/path).read_text('utf-8'))
def load_design():
    return (read('docs/architecture/openapi-design.json'),read('data/schemas/m02-database-design.json'),read('data/schemas/m02-api-inventory.json')['operations'],read('design/ui-ux/m02-route-catalog.json')['pages'],(ROOT/'design/wireframes/PAGE_AND_WIREFRAME_SPECIFICATIONS.md').read_text('utf-8'),read('data/schemas/m02-acceptance-cases.json')['cases'])
def validate_design(spec,db,inventory,routes,pages,cases):
    errors=[]
    def require(ok,message):
        if not ok:errors.append(message)
    def resolve(node):
        seen=set()
        while isinstance(node,dict) and '$ref' in node:
            ref=node['$ref']
            if ref in seen:return {} # Recursive schemas are legal.
            seen.add(ref)
            if not isinstance(ref,str) or not ref.startswith('#/'):
                errors.append('External reference requires separate review: '+str(ref));return {}
            current=spec
            try:
                for key in ref[2:].split('/'):
                    key=key.replace('~1','/').replace('~0','~')
                    current=current[int(key)] if isinstance(current,list) else current[key]
            except (KeyError,IndexError,TypeError,ValueError):
                errors.append('Unresolved reference: '+ref);return {}
            node=current
        return node
    def walk(node):
        if isinstance(node,dict):
            if '$ref' in node:resolve(node)
            for v in node.values():walk(v)
        elif isinstance(node,list):
            for v in node:walk(v)
    def keys(node,seen=None):
        seen=set() if seen is None else seen
        result=set()
        if isinstance(node,dict):
            ref=node.get('$ref')
            if ref and ref not in seen:
                seen.add(ref);result|=keys(resolve(node),seen)
            result|=set(node.get('properties',{}))
            for k,v in node.items():
                if k!='$ref':result|=keys(v,seen)
        elif isinstance(node,list):
            for v in node:result|=keys(v,seen)
        return result
    walk(spec)
    schemas=spec['components']['schemas'];schemes=spec['components']['securitySchemes']
    for sec in spec.get('security',[]):require(set(sec)<=set(schemes),'Broken root security scheme')
    indexed={e['id']:e for e in inventory};ids=set();truth_ids=set()
    require(len(indexed)==len(inventory),'Duplicate inventory ID')
    for path,methods in spec['paths'].items():
        for method,op in methods.items():
            if method not in METHODS:continue
            label=method.upper()+' '+path;oid=op.get('operationId')
            require(bool(oid) and oid not in ids,'Duplicate/missing operation ID: '+label);ids.add(oid)
            # An operation may legally override a path-item parameter.
            params=[resolve(p) for p in methods.get('parameters',[])+op.get('parameters',[])]
            for collection in (methods.get('parameters',[]),op.get('parameters',[])):
                pk=[(p.get('in'),p.get('name')) for p in map(resolve,collection)]
                require(len(pk)==len(set(pk)),'Duplicate parameter: '+label)
            pp=[p for p in params if p.get('in')=='path']
            require(set(re.findall(r'{([^}]+)}',path))=={p.get('name') for p in pp},'Path parameter mismatch: '+label)
            require(all(p.get('required') is True for p in pp),'Path parameter not required: '+label)
            headers={p.get('name','').lower():p for p in params if p.get('in')=='header'}
            security=op.get('security',spec.get('security',[]))
            for sec in security:require(set(sec)<=set(schemes),'Broken security scheme: '+label)
            require(bool(op.get('x-roles')) and bool(op.get('x-scope')),'Missing authorization scope: '+label)
            policy='READ_ONLY' if method=='get' else 'AUTH_NO_CACHE' if path.startswith('/auth/') else 'GLOBAL_FINAL_STATE' if path.startswith('/me') else 'PROJECT_CONTACT' if path=='/public/contact' else 'TENANT_7_DAY'
            require(op.get('x-retry-policy')==policy,'Retry policy drift: '+label)
            if method!='get':
                if policy=='TENANT_7_DAY':require(headers.get('idempotency-key',{}).get('required') is True,'Missing business idempotency: '+label)
                else:require('idempotency-key' not in headers,'Auth/global/contact inherits business idempotency: '+label)
                if path.startswith('/ingest/'):
                    require(security==[{'deviceBearer':[]}],'Ingestion must use scoped bearer: '+label)
                else:
                    require(headers.get('x-csrf-token',{}).get('required') is True,'Missing required CSRF: '+label)
                    require(security==[{'sessionCookie':[]}],'Cookie/preauth authentication missing: '+label)
            if path.startswith('/auth/'):
                require(op.get('x-response-cache')=='NO_STORE','Auth response cache policy missing')
                if method!='get':
                    expected_states=['AUTHENTICATED_VERIFIED'] if path.endswith('/invitation-accept') else ['PREAUTH','AUTHENTICATED','REVOKED_CLEANUP_ONLY','EXPIRED_CLEANUP_ONLY'] if path.endswith('/logout') else ['PREAUTH','AUTHENTICATED']
                    require(op.get('x-auth-session-states')==expected_states,'Auth session-state boundary drift: '+label)
                for resp in op['responses'].values():
                    cache=resolve(resp).get('headers',{}).get('Cache-Control',{})
                    require(cache.get('required') is True and cache.get('schema',{}).get('const')=='no-store','Auth response may be cached: '+label)
            guards=set(op.get('x-authorization-guards',[]));roles=op.get('x-roles',[])
            if '{organization_id}' in path:require('TENANT' in guards and security==[{'sessionCookie':[]}] and 'PUBLIC' not in roles,'Tenant authorization missing: '+label)
            if 'CITIZEN' in roles:require('CITIZEN_OWNED' in guards,'Citizen ownership missing: '+label)
            if 'TECHNICIAN' in roles:require('TECHNICIAN_ASSIGNED' in guards,'Technician assignment missing: '+label)
            if op.get('x-required-permission','').split('.')[0] in {'observations','evidence','acoustics','simulations','pipeline_assets','water_zones'}:require('ADMIN' not in roles,'ADMIN inherits engineering access: '+label)
            restricted=op.get('x-restricted-truth') is True
            if restricted:
                truth_ids.add(oid)
                require(path.endswith('/evaluation') and method=='get' and roles==['ENGINEER+EVALUATOR'] and {'TENANT','ENGINEER_AND_EVALUATOR','SEALED_TERMINAL_RUN','AUDITED_TRUTH_ACCESS'}<=guards,'Truth access boundary drift: '+label)
            else:require(not(keys(op.get('responses',{}))&TRUTH),'Ordinary response exposes restricted truth: '+label)
            require(not(keys(op.get('requestBody',{}))&TRUTH),'Request accepts restricted truth: '+label)
            if '/artifacts/' in path:require({'TENANT','ARTIFACT_CLASS_NONTRUTH','ARTIFACT_PARENT_ACL'}<=guards,'Artifact classification/parent ACL missing')
            if 'CredentialView' in json.dumps(op.get('responses',{})):require(op.get('x-secret-replay')=='REJECT_409','Issued secret can be replayed')
            entry=indexed.get(oid);require(entry is not None,'Missing inventory entry: '+label)
            if entry:
                expected={'method':method,'path':path,'roles':roles,'scope':op.get('x-scope'),'effects':op.get('x-database-effect'),'permission':op.get('x-required-permission'),'restricted':restricted,'retry_policy':op.get('x-retry-policy'),'authorization_guards':op.get('x-authorization-guards')}
                request=resolve(op.get('requestBody',{})).get('content',{});name=entry.get('request')
                if name:require(resolve(op.get('requestBody',{})).get('required') is True,'Request body must be required: '+label)
                if name=='BINARY':require(request.get('application/octet-stream',{}).get('schema',{}).get('format')=='binary','Inventory binary request mismatch: '+label)
                elif name:require(request.get('application/json',{}).get('schema',{}).get('$ref')=='#/components/schemas/'+name,'Inventory request mismatch: '+label)
                else:require('application/json' not in request,'Inventory omits JSON request: '+label)
                name=entry.get('response')
                success=[resolve(r).get('content',{}) for code,r in op['responses'].items() if code.startswith('2')]
                if name in ('BINARY','SSE'):
                    media='application/octet-stream' if name=='BINARY' else 'text/event-stream'
                    require(any(media in content for content in success),'Inventory response media mismatch: '+label)
                elif name:
                    refs=[resolve(r).get('content',{}).get('application/json',{}).get('schema',{}).get('$ref') for code,r in op['responses'].items() if code.startswith('2')]
                    require('#/components/schemas/'+('Page_' if entry.get('list') else '')+name in refs,'Inventory response mismatch: '+label)
                require(all(entry.get(k)==v for k,v in expected.items()),'API inventory mismatch: '+label)
                filters={p['name'] for p in params if p.get('in')=='query'}-{'limit','cursor'}
                require(filters==set(entry.get('filters',[])),'Inventory filter mismatch: '+label)
    require(ids==set(indexed),'API inventory diverges from contract');require(len(truth_ids)==1,'Exactly one restricted evaluation operation required')
    for r in routes:
        require(set(r['operations'])<=ids,'Route references missing operation: '+r['route']);require(r['id'] in pages,'Missing detailed page specification')
    tables={t['name']:t for t in db['tables']};require(len(tables)==len(db['tables']),'Duplicate table')
    for t in tables.values():
        columns={c['name'] for c in t['columns']}
        require(len(columns)==len(t['columns']) and 'id' in columns,'Duplicate columns or missing primary ID: '+t['name'])
        if t['scope']=='tenant':require('organization_id' in columns,'Missing tenant ownership')
        for fk in t['foreign_keys']:
            target=tables.get(fk['target']);require(target is not None and fk['column'] in columns,'Invalid FK: '+t['name'])
            if target:
                same=t['scope']==target['scope']=='tenant' and fk['column']!='organization_id'
                require(fk['same_tenant']==same,'Tenant FK classification drift: '+t['name'])
    for name,values in db['enums'].items():require(schemas[name]['enum']==values,'Enum drift: '+name)
    for name in ('ObservationInput','ObservationBatch','SimulationObservationBatch','ManualObservationWrite'):
        require(not(keys(schemas[name])&(TRUTH|SOURCE)),'Detector/ingest truth or source override: '+name)
        require(schemas[name].get('additionalProperties') is False,'Observation accepts arbitrary properties: '+name)
    require('provenance' in schemas['Observation'].get('required',[]) and schemas['Observation']['properties'].get('provenance')=={'$ref':'#/components/schemas/Provenance'},'Observation loses provenance')
    sim=spec['paths']['/ingest/simulation/observations']['post']
    require(sim.get('x-derived-provenance')=={'source_category':'SIMULATION','environment':'SIMULATION','authority':'credential_and_active_run'} and sim.get('x-roles')==['SIMULATOR'] and sim.get('security')==[{'deviceBearer':[]}],'Simulation origin authority drift')
    hardware=spec['paths']['/ingest/hardware/observations']['post']
    require(hardware.get('x-derived-provenance')=={'source_category':'HARDWARE','environment':['LABORATORY','FIELD'],'authority':'provisioned_credential_profile'} and hardware.get('x-roles')==['DEVICE'],'Hardware origin authority drift')
    require('EVALUATOR' not in schemas['RoleWrite']['properties']['roles']['items']['enum'],'Evaluator self-grant contract drift')
    require(tables['restricted_simulation_truth']['privacy']=='RESTRICTED_TRUTH','Truth table privacy drift')
    receipt=tables['idempotency_records']
    require(receipt['scope']=='tenant' and 'excludes authentication' in receipt['purpose'] and len(receipt.get('invariants',[]))>=3,'Business receipt secret exclusion missing')
    require(not({'password','token','response_body','request_body','one_time_secret'}&{c['name'] for c in receipt['columns']}),'Business receipt stores secrets/bodies')
    contact=tables.get('project_contact_submissions',{})
    require(contact.get('scope')=='global' and not contact.get('foreign_keys') and not({'organization_id','author_id'}&{c['name'] for c in contact.get('columns',[])}),'Contact fabricates tenant/member ownership')
    require(pages.count('## Wireframe — ')==10 and len(cases)>=28,'Wireframe/acceptance catalogue incomplete')
    require(spec['openapi']=='3.1.0','Expected OpenAPI3.1 design')
    return errors

def main():
    design=load_design();errors=validate_design(*design)
    for error in errors:print('FAIL:',error)
    print(f'Checked {len(design[1]["tables"])} tables, {len(design[2])} API operations, {len(design[3])} routes and ten wireframes; {len(errors)} error(s).')
    print('Design checks only; run independent OpenAPI validation separately. No backend/SQL/security enforcement claimed.')
    return int(bool(errors))
if __name__=='__main__':raise SystemExit(main())
