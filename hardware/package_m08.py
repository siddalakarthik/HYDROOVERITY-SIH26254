"""Build/verify an allowlisted M08 screening ZIP; never traverse the workspace.

Generate CAD and figures, then run scripts/check_m08.py --artifacts first.
This packages digital evidence only; it does not validate physical hardware.
"""
import argparse
import hashlib
import importlib.metadata
import importlib.util
import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REVIEWED_HEAD = '3e5fcbb3fba1653b3c6ce3b50a71ecbd958e6986'
PACKAGE_NAME = 'HYDROOVERITY_M08_PPT_ENGINEERING_PACKAGE.zip'
CONTACT = 'hardware/results/ppt/M08_CONTACT_SHEET.png'
STEMS = ('H01_architecture', 'H02_guard5_cad', 'H03_guard5_cutaway',
         'H04_watch_electronics', 'H05_ear_shared_clock', 'H06_test_rig', 'H07_budget')
SOURCE_FILES = (
    'hardware/package_m08.py', 'hardware/render_m08.py', 'hardware/requirements-m08-cad.txt',
    'hardware/guard5-collar/envelope.json', 'hardware/mechanical-cad/guard5.py',
    'hardware/mechanical-cad/rig_layout.json', 'hardware/electronics/interfaces.json',
    'hardware/electronics/datasheet_review.json', 'hardware/electronics/generate_schematics.py',
    'hardware/electronics/connections.csv', 'hardware/electronics/netlist.json',
    'hardware/electronics/watch.kicad_sch', 'hardware/electronics/wetness.kicad_sch',
    'hardware/electronics/ear.kicad_sch', 'hardware/electronics/power.kicad_sch',
    'hardware/acoustic-acquisition/acquisition.schema.json',
    'hardware/firmware/INTERFACE_READINESS.md', 'hardware/calibration/VALIDATION_PLAN.md',
    'hardware/bom/m08_bom.json', 'hardware/bom/m08_bom.csv', 'hardware/bom/M08_BOM.md',
    'hardware/VALIDATION_RESULTS.md', 'hardware/results/README.md',
    'docs/engineering/M08_DIGITAL_HARDWARE_REPORT.md', 'docs/engineering/HARDWARE_STATUS.md',
    'docs/engineering/ENGINEERING_LIMITATIONS.md', 'docs/architecture/SYSTEM_ARCHITECTURE.md',
    'docs/architecture/openapi-design.json', 'scripts/check_m08.py',
    'tests/unit/test_m08_checks.py', 'tests/unit/test_m08_package.py',
)
LIMITATIONS = '''PROPOSED DESIGN / NOT PHYSICALLY TESTED
DIGITAL DESIGN / NOT PHYSICALLY VALIDATED

CadQuery geometry is digitally checked, not physically fit-tested.
KiCad files are connectivity drafts; native ERC was not executed.
No complete field firmware or physically validated acoustic recorder exists.
All 41 BOM prices are estimates, not supplier quotations.
The proposed 0-16 bar pressure sensor is poorly suited to sensitive low-pressure measurements.
GUARD-5 physical collector performance remains unverified.
M05 nominal simulation: GUARD-5 missed 36/96 local leaks versus multizone 12/96;
these unfavorable results and the scientific methodology remain unchanged.
Budget: INR 59,870 including INR 5,000 contingency; INR 130 residual headroom
is a procurement risk, not verified affordability. Taxes/shipping need review.
This is a screening presentation package, not fabrication-ready or cost-verified.
No purchases, construction, pressure operation or field deployment are authorized.
'''


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_payload(name):
    path = ROOT / name
    if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
        raise ValueError('Outside-root or symbolic payload: ' + name)
    return path.read_bytes()


def expected_payloads(geometry):
    if len(geometry['parts']) != 25:
        raise ValueError('Expected 25 reviewed CAD parts')
    for name in geometry['parts']:
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', name):
            raise ValueError('Unsafe CAD part name')
    figures = [f'hardware/results/ppt/{stem}.{ext}' for stem in STEMS for ext in ('png', 'svg')]
    return set(SOURCE_FILES) | set(figures) | {
        CONTACT, 'hardware/results/ppt/CAPTIONS.md', 'hardware/results/ppt/manifest.json',
        'hardware/results/details/ear_clock_timing.png',
        'hardware/results/details/ear_clock_timing.svg',
        'hardware/mechanical-cad/exports/geometry_checks.json',
        'hardware/mechanical-cad/exports/GUARD5_assembly.step',
        'REPRODUCE.md', 'LIMITATIONS.txt', 'package_manifest.json',
    } | {f'hardware/mechanical-cad/exports/{name}.step' for name in geometry['parts']}


def contact_sheet():
    from PIL import Image, ImageDraw, ImageFont
    import matplotlib
    font_path = Path(matplotlib.get_data_path()) / 'fonts/ttf/DejaVuSans.ttf'
    title_font = ImageFont.truetype(str(font_path), 38)
    font = ImageFont.truetype(str(font_path), 26)
    # Exact 16:9 thumbnails preserve all margins and untested labels.
    sheet = Image.new('RGB', (2560, 3040), '#e7eef5')
    draw = ImageDraw.Draw(sheet)
    draw.text((35, 18), 'HYDROOVERITY M08 | seven engineering figures', fill='#102b46', font=title_font)
    draw.text((35, 72), 'PROPOSED DESIGN / NOT PHYSICALLY TESTED', fill='#b94c50', font=font)
    for index, stem in enumerate(STEMS):
        with Image.open(ROOT / f'hardware/results/ppt/{stem}.png') as original:
            original.load()
            thumbnail = original.convert('RGB').resize((1280, 720), Image.Resampling.LANCZOS)
        sheet.paste(thumbnail, ((index % 2) * 1280, 130 + (index // 2) * 720))
    x, y = 1320, 2350
    for line in ('SCREENING REVIEW ONLY', 'A / B / C + EXT + BYPASS = 5 channels',
                 'One physical stereo ADC sampling clock', '12 m supply span + full 12 m return',
                 'INR 59,870 estimated; INR 130 residual', 'No physical validation or native ERC',
                 'Use individual PNG/SVG files in the PPT.'):
        draw.text((x, y), line, fill='#102b46', font=font)
        y += 55
    path = ROOT / CONTACT
    sheet.save(path)
    return path


def verify_checksums(archive):
    names = archive.namelist()
    if len(names) != len(set(names)):
        raise ValueError('Duplicate archive members')
    for name in names:
        p = PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name:
            raise ValueError('Unsafe archive path')
    entries = {}
    for line in archive.read('SHA256SUMS.txt').decode('utf-8').splitlines():
        value, name = line.split('  ', 1)
        if not re.fullmatch('[0-9a-f]{64}', value) or name in entries:
            raise ValueError('Invalid checksum ledger')
        entries[name] = value
    if set(names) != set(entries) | {'SHA256SUMS.txt'}:
        raise ValueError('Checksum coverage differs from archive members')
    for name, expected in entries.items():
        if digest(archive.read(name)) != expected:
            raise ValueError('Checksum mismatch: ' + name)


def verify_package(path):
    from PIL import Image
    with zipfile.ZipFile(path) as archive:
        verify_checksums(archive)
        geometry = json.loads(archive.read('hardware/mechanical-cad/exports/geometry_checks.json'))
        if set(archive.namelist()) != expected_payloads(geometry) | {'SHA256SUMS.txt'}:
            raise ValueError('Package differs from the reviewed allowlist')
        figure_manifest = json.loads(archive.read('hardware/results/ppt/manifest.json'))
        if [f['stem'] for f in figure_manifest['figures']] != list(STEMS):
            raise ValueError('Unexpected figure set/order')
        for name, value in figure_manifest['source_sha256'].items():
            if name not in SOURCE_FILES or digest(archive.read(name)) != value:
                raise ValueError('Figure source mismatch: ' + name)
        for stem in STEMS:
            with Image.open(io.BytesIO(archive.read(f'hardware/results/ppt/{stem}.png'))) as png:
                if png.size != (2560, 1440):
                    raise ValueError('Incorrect PNG dimensions')
                png.verify()
            if b'PROPOSED DESIGN / NOT PHYSICALLY TESTED' not in archive.read(f'hardware/results/ppt/{stem}.svg'):
                raise ValueError('Missing figure limitation')
        budget_svg = archive.read('hardware/results/ppt/H07_budget.svg').decode('utf-8')
        if '₹59,870' not in budget_svg or '₹130' not in budget_svg:
            raise ValueError('Budget figure differs from reviewed amount')
        with Image.open(io.BytesIO(archive.read(CONTACT))) as sheet:
            if sheet.size != (2560, 3040):
                raise ValueError('Incorrect contact-sheet dimensions')
            sheet.verify()
    return {'package': str(path), 'sha256': digest(Path(path).read_bytes()), 'verified': True}


def build(output_dir=None):
    # Existing scientific/engineering consistency checks run before any ZIP is made.
    spec = importlib.util.spec_from_file_location('m08_check', ROOT / 'scripts/check_m08.py')
    checks = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checks)
    checks.run(artifacts=True)
    contact_sheet()
    geometry = json.loads(read_payload('hardware/mechanical-cad/exports/geometry_checks.json'))
    payload = {name: read_payload(name) for name in expected_payloads(geometry)
               if name not in {'REPRODUCE.md', 'LIMITATIONS.txt', 'package_manifest.json'}}
    instructions = read_payload('hardware/results/README.md').decode('utf-8')
    payload['REPRODUCE.md'] = instructions.replace('](../../docs/', '](docs/').replace('](../calibration/', '](hardware/calibration/').encode('utf-8')
    payload['LIMITATIONS.txt'] = LIMITATIONS.encode('utf-8')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    manifest = {'status': 'PROPOSED DESIGN / NOT PHYSICALLY TESTED',
                'reviewed_design_head': REVIEWED_HEAD, 'checkout_commit': commit,
                'python': sys.version.split()[0],
                'dependencies': {name: importlib.metadata.version(name) for name in
                                 ('cadquery', 'cadquery-ocp', 'matplotlib', 'numpy', 'pillow')},
                'scope': 'M08 digital screening assets and reproduction sources only',
                'sha256': {name: digest(data) for name, data in sorted(payload.items())}}
    payload['package_manifest.json'] = (json.dumps(manifest, indent=2) + '\n').encode('utf-8')
    payload['SHA256SUMS.txt'] = ''.join(f'{digest(data)}  {name}\n' for name, data in sorted(payload.items())).encode('utf-8')
    folder = Path(output_dir) if output_dir else ROOT / 'hardware/results/package'
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / PACKAGE_NAME
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(payload.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 20, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    result = verify_package(path)
    path.with_suffix('.zip.sha256').write_text(f'{result["sha256"]}  {path.name}\n', encoding='utf-8', newline='\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--verify', type=Path, help='Verify an existing ZIP without extraction')
    args = parser.parse_args()
    print(json.dumps(verify_package(args.verify) if args.verify else build(args.output_dir), indent=2))
