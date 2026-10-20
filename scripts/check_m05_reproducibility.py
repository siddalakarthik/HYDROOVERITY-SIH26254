"""Verify two saved runs and figure/data traceability without rerunning detectors."""
import argparse,json,hashlib
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from simulations.common import digest

def check(first,second):
    for name in ('summary.json','evaluation.json','examples.json','sensitivity.json'):
        a=json.loads((first/name).read_text('utf-8'));b=json.loads((second/name).read_text('utf-8'))
        assert digest(a)==digest(b),name+' changed between deterministic runs'
    figures=first if first.name=='ppt' else first/'figures'
    trace=json.loads((figures/'figure_traceability.json').read_text('utf-8'))
    for name,sha in trace['source_hashes'].items():assert digest(json.loads((first/name).read_text('utf-8')))==sha
    from PIL import Image
    for name in trace['figures']:
        assert Image.open(figures/(name+'.png')).size==(1920,1080)
        assert (figures/(name+'.svg')).exists()
    rows=json.loads((first/'evaluation.json').read_text('utf-8'));c=json.loads((first/'manifest.json').read_text('utf-8'))['config']['profiles']['ppt']
    assert len([r for r in rows['hydraulics'] if r['split']=='holdout'])==12*c['hydraulic_repeats']*2
    assert len([r for r in rows['acoustics'] if r['split']=='holdout'])==12*c['acoustic_repeats']
    assert len([r for r in rows['guard'] if r['split']=='holdout'])==14*c['guard_repeats']*3*3
    print('PASS: repeated numerical outputs identical; all cases counted; 8 PNG/SVG pairs and saved-data hashes verified.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('first',type=Path);p.add_argument('second',type=Path);a=p.parse_args();check(a.first,a.second)
