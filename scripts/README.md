# Repository validation

From the repository root run `python scripts/check_repository.py` using Python 3.12+ and Git. No packages or application setup are required. CI runs the same checker on Ubuntu; local development may use Windows.

The checker validates required files/directories, local Markdown targets, source SHA-256 copies, placeholder-only environment example, ignore behavior, text encoding/newlines and limited credential/large-artifact hygiene for tracked and unignored files. It does not inspect ignored secrets, network URLs, Markdown anchors or physical performance and is not a comprehensive secret scanner/security audit. Matched secret values are never printed.

Review `git diff --check`, staged filenames and staged content before committing. Future tests should target real application/scientific behavior; none are invented here.

For M02 also run `python scripts/check_m02_design.py` and `python scripts/test_m02_design_checker.py -v`. These inspect design consistency and deliberate invalid-design examples; they do not execute an application backend.

Independent OpenAPI review uses a separate virtual environment with `scripts/openapi-validation-requirements.txt`. Run its Python executable with `-m openapi_spec_validator --schema 3.1 --validation-errors all docs/architecture/openapi-design.json` and `scripts/validate_openapi_design.py`. Do not add these packages to an application environment. Exact executed versions/results and isolation notes are in [M02 review validation](../docs/testing/M02_REVIEW_VALIDATION.md).
