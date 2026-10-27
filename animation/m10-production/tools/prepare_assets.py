"""Copy only an explicit allowlist of already sanitized public-safe evidence."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('--workspace',type=Path,required=True)
p.add_argument('--project',type=Path,required=True)
a=p.parse_args()
a.project=a.project.resolve()
repo=a.project.parents[1]
out=a.project/'public'
(out/'data').mkdir(exist_ok=True)
summary=json.loads((repo/'simulations/evaluation/reference_summary.json').read_text('utf-8'))
bom=json.loads((repo/'hardware/bom/m08_bom.json').read_text('utf-8'))
groups={}
for item in bom['items']:
    groups[item['group']]=groups.get(item['group'],0)+item['extended_cost_inr']
facts={'baseline':'886bf01d1c775ce0f1f7ec9f2ff2f27bc65a1d91','operations':119,'tables':57,
       'guard_f1':{key:summary['guard']['nominal'][key]['f1'] for key in ['guard5','pad','multizone']},
       'acoustics':summary['acoustics'] if 'acoustics' in summary else summary['acoustic'],
       'bom_groups':groups,'bom_item_count':len(bom['items']),
       'hardware_status':'DIGITAL DESIGN / NOT PHYSICALLY VALIDATED'}
(out/'data/facts.json').write_text(json.dumps(facts,indent=2)+'\n',encoding='utf-8')
sources=['hardware/mechanical-cad/guard5.py','hardware/mechanical-cad/rig_layout.json',
         'hardware/guard5-collar/envelope.json','hardware/bom/m08_bom.json',
         'hardware/electronics/interfaces.json','hardware/electronics/netlist.json',
         'simulations/evaluation/reference_summary.json','docs/testing/PRE_M10_COMPLETION_REGISTER.md']
manifest=[{'path':s,'sha256':hashlib.sha256((repo/s).read_bytes()).hexdigest(),'classification':'REVIEWED_PUBLIC_SOURCE'} for s in sources]
captures={
 'home.png':('pre-m10-devices-browser-evidence','home-desktop.png'),
 'resident-intake.png':('pre-m10-realtime-browser-evidence','M07-A-01-resident-intake-desktop.png'),
 'supervisor-triage.png':('pre-m10-realtime-browser-evidence','M07-A-02-supervisor-triage-desktop.png'),
 'resident-timeline.png':('pre-m10-realtime-browser-evidence','M07-A-03-safe-resident-timeline.png'),
 'findings.png':('pre-m10-realtime-browser-evidence','M07-A-04-technician-findings-desktop.png'),
 'resident-mobile.png':('pre-m10-realtime-browser-evidence','M07-A-05-resident-mobile.png'),
 'supervisor.png':('pre-m10-devices-browser-evidence','supervisor-overview-desktop.png'),
 'technician-mobile.png':('pre-m10-devices-browser-evidence','technician-task-mobile.png'),
 'verification.png':('pre-m10-devices-browser-evidence','verification-desktop.png'),
 'science-watch.png':('m09-browser-evidence','M06-WATCH-desktop.png'),
 'science-ear.png':('m09-browser-evidence','M06-EAR-desktop.png'),
 'science-guard.png':('m09-browser-evidence','M06-GUARD5-mobile.png'),
 'inbox.png':('m07c-browser-evidence','M07C-resident-inbox-desktop.png'),
 'feedback.png':('m07c-browser-evidence','M07C-resident-feedback-mobile.png'),
}
(out/'captures').mkdir(exist_ok=True)
for target,(folder,file) in captures.items():
    src=a.workspace/'work'/folder/file
    if not src.is_file():
        raise FileNotFoundError(src)
    shutil.copyfile(src,out/'captures'/target)
    manifest.append({'asset':f'captures/{target}','source':f'work/{folder}/{file}',
        'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
        'classification':'AUTHENTIC_SYNTHETIC_BROWSER_TEST_CAPTURE',
        'continuity':'Within-test cases only; different test families are separate demonstrations.',
        'visual_privacy_review':'PENDING'})
(a.project/'local').mkdir(exist_ok=True)
(a.project/'local/asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print('Prepared public aggregate facts and',len(captures),'authentic captures; privacy inspection pending.')
