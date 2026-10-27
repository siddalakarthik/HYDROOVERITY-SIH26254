"""Tessellate accepted M08 BReps. Meshes are illustrations, not validation results."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--repo', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
args = p.parse_args()
source = args.repo / 'hardware/mechanical-cad/guard5.py'
spec = importlib.util.spec_from_file_location('reviewed_guard5', source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
parts, ports = module.build()
args.output.mkdir(parents=True, exist_ok=True)
records = []
for name, shape in parts.items():
    assert shape.isValid() and shape.Volume() > 0
    vertices, triangles = shape.tessellate(0.12, 0.15)
    payload = {'positions': [component for v in vertices for component in (v.x, v.y, v.z)],
               'indices': [index for triangle in triangles for index in triangle]}
    output = args.output / f'{name}.json'
    output.write_text(json.dumps(payload, separators=(',', ':')), encoding='utf-8')
    records.append({'name': name, 'vertices': len(vertices), 'triangles': len(triangles),
                    'volume_mm3': shape.Volume(), 'sha256': hashlib.sha256(output.read_bytes()).hexdigest()})
(args.output / 'manifest.json').write_text(json.dumps({'source': 'hardware/mechanical-cad/guard5.py',
    'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'units': 'mm', 'parts': records, 'drain_ports': ports,
    'label': 'DIGITAL DESIGN / NOT PHYSICALLY VALIDATED',
    'tessellation_tolerance_mm': 0.12, 'angular_tolerance_radians': 0.15}, indent=2), encoding='utf-8')
print('Exported', len(records), 'accepted CAD parts;', sum(r['triangles'] for r in records), 'triangles', flush=True)
