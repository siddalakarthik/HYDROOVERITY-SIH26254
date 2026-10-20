# Generated M08 digital engineering outputs

**PROPOSED DESIGN / NOT PHYSICALLY TESTED.** Generated payloads stay ignored; executable source and checks stay in Git. The commands below run from the repository root (the directory containing `AGENTS.md`, `hardware/` and `scripts/`), never from this results folder.

## Isolated CAD environment

Use Python 3.12. Create a dedicated environment; do not install CAD dependencies into the M02 OpenAPI or M05 scientific environment. With Python 3.12 selected as `python`, create it using `python -m venv .venv/m08-cad`.

On PowerShell, use the explicit interpreter without changing execution policy:

```powershell
$cadPython = (Resolve-Path .venv/m08-cad/Scripts/python.exe).Path
& $cadPython -m pip install --only-binary=:all: -r hardware/requirements-m08-cad.txt
$env:MPLCONFIGDIR = Join-Path $PWD '.venv/m08-cad/mpl-cache'
& $cadPython hardware/electronics/generate_schematics.py
& $cadPython hardware/mechanical-cad/guard5.py
& $cadPython hardware/render_m08.py
& $cadPython scripts/check_m08.py --artifacts
& $cadPython -m unittest discover -s tests/unit -p 'test_m08*.py' -v
& $cadPython hardware/package_m08.py
& $cadPython hardware/package_m08.py --verify hardware/results/package/HYDROOVERITY_M08_PPT_ENGINEERING_PACKAGE.zip
```

On Linux/macOS, activate that environment and run the equivalent commands:

```sh
. .venv/m08-cad/bin/activate
python -m pip install --only-binary=:all: -r hardware/requirements-m08-cad.txt
export MPLCONFIGDIR="$PWD/.venv/m08-cad/mpl-cache"
python hardware/electronics/generate_schematics.py
python hardware/mechanical-cad/guard5.py
python hardware/render_m08.py
python scripts/check_m08.py --artifacts
python -m unittest discover -s tests/unit -p 'test_m08*.py' -v
python hardware/package_m08.py
python hardware/package_m08.py --verify hardware/results/package/HYDROOVERITY_M08_PPT_ENGINEERING_PACKAGE.zip
```

The checked-in schematic drafts regenerate as connectivity drafts only; regeneration does not execute native KiCad ERC. No missing wrapper/runner is required. Existing isolated Python 3.12 environments with the pinned CAD requirements may be reused; replace `$cadPython` or activated `python` with that environment's interpreter.

## Output and archive contents

- Seven high-resolution 2560×1440 PNGs and editable SVGs: `hardware/results/ppt/H01_architecture` through `H07_budget`, using the exact stems in `hardware/results/ppt/manifest.json`.
- Seven-figure overview: `hardware/results/ppt/M08_CONTACT_SHEET.png` (2560×3040). Use individual images on PPT slides; the sheet is an overview.
- Captions/assumptions and figure source hashes: `hardware/results/ppt/CAPTIONS.md` and `manifest.json`.
- Supplementary ideal I²S timing PNG/SVG: `hardware/results/details/ear_clock_timing`.
- Assembly, 25 part STEP exports and digital geometry checks: `hardware/mechanical-cad/exports/`.
- Complete ZIP: `hardware/results/package/HYDROOVERITY_M08_PPT_ENGINEERING_PACKAGE.zip`; whole-ZIP checksum in the adjacent `.zip.sha256` file.

The ZIP contains an explicit allowlist of those assets and their engineering/reproduction sources. `package_manifest.json` records the reviewed design head, checkout commit, dependency versions and source/payload hashes. `SHA256SUMS.txt` covers every other archive member, including that manifest. Verify the ZIP with the command above before extraction. An extracted package mirrors repository paths; CAD/figure regeneration can run there, but Git commit metadata and full M02/M05 regression require the original repository checkout. No credentials, development environments, diagnostic `debug.step`, personal files or simulation evaluation truth are packaged.

## CI retrieval and retention

The `m08-cad-and-figures` job validates CAD/figures, builds and verifies this package, then uploads artifact `HYDROOVERITY_M08_PPT_ENGINEERING_PACKAGE` with **14-day retention**. A failed validation stops the upload. Open PR #13 → Checks → Repository integrity → workflow run → Artifacts; download the named artifact. GitHub sign-in/repository access may be required. GitHub wraps the engineering ZIP and its checksum in the artifact download; extract that outer download first. The upload's actual artifact URL appears in the workflow summary after success. After expiry, rerun the workflow or regenerate locally; the source remains in Git. No upload is implied before the run confirms it.

## Limits retained for screening

Digital geometry is not physically fit-tested; KiCad files are connectivity drafts with no native ERC. No complete field firmware or physically validated acoustic recorder exists. All 41 BOM prices are estimates. The proposed 0–16 bar sensor is poorly matched to sensitive low-pressure measurements. GUARD-5 collection remains physically unverified, and M05's unfavorable nominal result (36/96 misses versus multizone12/96) is unchanged. The ₹59,870 estimate leaves only **₹130 residual headroom**, a procurement risk. This package is neither fabrication-ready nor cost-verified. See the [engineering report](../../docs/engineering/M08_DIGITAL_HARDWARE_REPORT.md) and [qualification plan](../calibration/VALIDATION_PLAN.md).
