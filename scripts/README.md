# Repository validation

From the repository root run `python scripts/check_repository.py` using Python 3.12+ and Git. No packages or application setup are required. CI runs the same checker on Ubuntu; local development may use Windows.

The checker validates required files/directories, local Markdown targets, source SHA-256 copies, placeholder-only environment example, ignore behavior, text encoding/newlines and limited credential/large-artifact hygiene for tracked and unignored files. It does not inspect ignored secrets, network URLs, Markdown anchors or physical performance and is not a comprehensive secret scanner/security audit. Matched secret values are never printed.

Review `git diff --check`, staged filenames and staged content before committing. Future tests should target real application/scientific behavior; none are invented here.
