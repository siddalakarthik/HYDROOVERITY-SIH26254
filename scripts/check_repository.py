"""Validate the actual M01 foundation using only Python's standard library.

This is a limited hygiene check, not a security audit or hardware experiment.
Only tracked and unignored files are inspected; credential values are never printed.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DIRS = """
apps/web services/api services/ingestion services/notifications
packages/shared-types packages/shared-config
simulations/hydraulics simulations/acoustics simulations/guard5
simulations/scenarios simulations/evaluation simulations/results
hardware/guard5-collar hardware/hydro-watch hardware/acoustic-acquisition
hardware/mechanical-cad hardware/electronics hardware/firmware hardware/bom
hardware/calibration data/demo data/schemas data/samples
docs/project docs/requirements docs/architecture docs/research docs/engineering
docs/testing docs/deployment docs/decisions docs/presentations
tests/unit tests/integration tests/e2e tests/security scripts
design/ui-ux design/wireframes design/design-system
animation/storyboard animation/scripts animation/scenes animation/renders
.github/workflows .github/ISSUE_TEMPLATE
""".split()
REQUIRED_FILES = """
README.md AGENTS.md CONTRIBUTING.md SECURITY.md .gitignore .gitattributes
.editorconfig .env.example docs/README.md
docs/project/PROJECT_CHARTER.md docs/project/ROADMAP.md
docs/project/HYDROOVERITY_MASTER_CONTEXT.md docs/project/MILESTONE_01_REQUEST.md
docs/project/SOURCE_MANIFEST.json docs/requirements/SYSTEM_REQUIREMENTS.md
docs/requirements/WEBSITE_REQUIREMENTS.md docs/architecture/SYSTEM_ARCHITECTURE.md
docs/architecture/DATA_DICTIONARY.md docs/architecture/THREAT_MODEL.md
docs/engineering/HARDWARE_STATUS.md docs/engineering/ENGINEERING_LIMITATIONS.md
docs/engineering/ARTIFACT_POLICY.md docs/testing/SIMULATION_PLAN.md
docs/testing/EVIDENCE_REGISTER.md docs/decisions/DECISION_LOG.md
.github/README.md .github/backlog.json .github/PULL_REQUEST_TEMPLATE.md
.github/ISSUE_TEMPLATE/feature_request.md .github/ISSUE_TEMPLATE/bug_report.md
.github/ISSUE_TEMPLATE/engineering_investigation.md
.github/ISSUE_TEMPLATE/simulation_experiment.md
.github/ISSUE_TEMPLATE/hardware_design_task.md
.github/workflows/repository-integrity.yml scripts/README.md
scripts/check_repository.py simulations/results/README.md animation/renders/README.md
""".split()


def git(*args: str, input_text: str | None = None) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, input=input_text, encoding="utf-8",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
    )
    return result.stdout


def validate() -> list[str]:
    errors: list[str] = []
    for name in REQUIRED_DIRS:
        if not (ROOT / name).is_dir():
            errors.append(f"Missing required directory: {name}")
    for name in REQUIRED_FILES:
        if not (ROOT / name).is_file():
            errors.append(f"Missing required file: {name}")
    if errors:
        return errors

    # Git determines the review set: do not inspect ignored local secrets.
    names = sorted(set(filter(None, git(
        "ls-files", "--cached", "--others", "--exclude-standard", "-z"
    ).split("\0"))))
    if not names:
        errors.append("No tracked/unignored repository files found")
    common_credentials = [
        re.compile(r"gh[pousr]_" + r"[A-Za-z0-9]{20,}"),
        re.compile(r"github_pat_" + r"[A-Za-z0-9_]{20,}"),
        re.compile(r"AKIA" + r"[A-Z0-9]{16}"),
        re.compile(r"-----BEGIN " + r"(?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        re.compile(r"https?://" + r"[^\s/:]+:[^\s/@]+@"),
    ]
    checked_links = 0
    for name in names:
        path = ROOT / name
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            errors.append(f"Unsupported symlink or outside-root path: {name}")
            continue
        if not path.is_file():
            errors.append(f"Tracked path missing from worktree: {name}")
            continue
        if path.stat().st_size > 1024 * 1024:
            errors.append(f"Artifact exceeds 1 MiB review gate: {name}")
            continue
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            # Future binary source needs a deliberate artifact-policy review.
            errors.append(f"Binary/non-UTF8 file needs review: {name}")
            continue
        preserved_source = name in {
            "docs/project/HYDROOVERITY_MASTER_CONTEXT.md",
            "docs/project/MILESTONE_01_REQUEST.md",
        }
        if raw and not raw.endswith(b"\n") and not preserved_source:
            errors.append(f"Missing final newline: {name}")
        if any(pattern.search(text) for pattern in common_credentials):
            errors.append(f"Possible credential pattern in: {name} (value withheld)")
        if path.suffix == ".md":
            without_fences = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
            for target in re.findall(r"\]\(([^)\n]+)\)", without_fences):
                target = target.strip().strip("<>")
                parts = urlsplit(target)
                if parts.scheme or parts.netloc or not parts.path:
                    continue
                dest = (path.parent / unquote(parts.path)).resolve()
                checked_links += 1
                if not dest.is_relative_to(ROOT) or not dest.exists():
                    errors.append(f"Invalid local Markdown target in {name}: {target}")

    manifest = json.loads((ROOT / "docs/project/SOURCE_MANIFEST.json").read_text("utf-8"))
    for source in manifest["sources"]:
        path = ROOT / source["path"]
        if not path.resolve().is_relative_to(ROOT):
            errors.append("Source manifest contains an outside-root path")
            continue
        digest = hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        if digest != source["git_text_sha256"]:
            errors.append(f"Preserved source hash differs: {source['path']}")

    env_text = (ROOT / ".env.example").read_text("utf-8")
    for line in env_text.splitlines():
        if line and not line.startswith("#"):
            if not re.fullmatch(r"[A-Z][A-Z0-9_]*=__SET_[A-Z0-9_]+__", line):
                errors.append(".env.example must contain placeholder assignments only")

    ignored_examples = [
        ".env", ".env.local", "services/api/.env.production", ".venv/test.py",
        "services/api/__pycache__/test.pyc", "apps/web/node_modules/package/index.js",
        "apps/web/.next/cache", "local.sqlite3", "uploads/private.jpg",
        "data/private/person.json", "simulations/results/raw.csv",
        "hardware/mechanical-cad/part.FCStd1", "animation/renders/demo.mp4",
        "secrets/credential.txt",
    ]
    kept_examples = [".env.example", "services/api/.env.example", "simulations/results/README.md",
                     "animation/renders/README.md", "hardware/mechanical-cad/collar.FCStd"]
    ignored = set(git("check-ignore", "--no-index", "--stdin", "-z", input_text="\0".join(
        ignored_examples + kept_examples
    ) + "\0").split("\0"))
    for name in ignored_examples:
        if name not in ignored:
            errors.append(f"Ignore rule missing for: {name}")
    for name in kept_examples:
        if name in ignored:
            errors.append(f"Useful source/example unexpectedly ignored: {name}")
    for name in names:
        parts = Path(name).parts
        if Path(name).name.startswith(".env") and Path(name).name != ".env.example":
            errors.append(f"Environment secret file tracked/unignored: {name}")
        if any(part in {"node_modules", ".venv", "__pycache__", "uploads", "secrets"} for part in parts):
            errors.append(f"Generated/private directory tracked/unignored: {name}")

    backlog = json.loads((ROOT / ".github/backlog.json").read_text("utf-8"))
    milestone_titles = [item["title"] for item in backlog["milestones"]]
    if len(milestone_titles) != 10 or len(set(milestone_titles)) != 10:
        errors.append("Backlog must contain ten unique milestones")
    label_names = {item["name"] for item in backlog["labels"]}
    for item in backlog["milestones"]:
        if not set(item["labels"]) <= label_names:
            errors.append(f"Backlog references undefined label: {item['title']}")

    workflow = (ROOT / ".github/workflows/repository-integrity.yml").read_text("utf-8")
    if "contents: read" not in workflow or "persist-credentials: false" not in workflow:
        errors.append("Workflow must retain read-only contents and disable stored credentials")
    if not re.search(r"uses: actions/checkout@[0-9a-f]{40}\b", workflow):
        errors.append("Checkout must be pinned to a full official commit SHA")
    if "pull_request_target:" in workflow:
        errors.append("Privileged PR trigger is outside this foundation's CI scope")
    print(f"Checked {len(names)} files, {len(REQUIRED_DIRS)} required directories, "
          f"{checked_links} local Markdown links, source hashes, ignore rules, "
          "placeholder config, backlog and limited credential hygiene.")
    return errors


def main() -> int:
    try:
        errors = validate()
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        # Do not relay subprocess stderr or file contents that might expose secrets.
        print(f"FAIL: validator could not complete ({type(exc).__name__})")
        return 1
    for error in errors:
        print(f"FAIL: {error}")
    if errors:
        return 1
    print("PASS: repository foundation integrity (not application or hardware validation).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
