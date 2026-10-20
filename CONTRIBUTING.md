# Contributing

Read [AGENTS.md](AGENTS.md), the [master context](docs/project/HYDROOVERITY_MASTER_CONTEXT.md), [requirements](docs/requirements/SYSTEM_REQUIREMENTS.md) and [decision log](docs/decisions/DECISION_LOG.md). Obtain milestone authorization; a backlog entry is not permission to implement it.

## Working agreement

Use `main` for stable reviewed work. Create focused short-lived branches such as `docs/requirements` or `feat/incident-model`, use descriptive commits, and open PRs for substantial changes. M01 is the authorized initial commit. Do not force-push shared history, invite collaborators, publish the repository or select a license without owner approval. Sole-maintainer review remains practical; no mandatory outside approval is imposed.

Before editing inspect `git status`, relevant documents and existing code. Describe scope, update linked requirements and record material decisions. Preserve unrelated work. No package installation or app scaffolding is needed for the foundation.

## Validation and PR evidence

Run `python scripts/check_repository.py` and `git diff --check`; later run the relevant real tests. Report commands, actual results, failures and known limits. Use the PR template, link the issue, list changed areas, distinguish simulation/lab/field data, and explain security impact. Do not invent frontend/backend tests before code exists.

Experiments must retain config, seed, version, holdout policy and denominators. Failures and unresolved cases belong in reports. Hardware design is not hardware validation. Keep real personal data out of issues and fixtures.

## Source and artifact policy

The project license is undecided. Do not assume permission to reuse or redistribute third-party code, datasets, tiles, CAD or audiovisual assets. Record provenance/license before use; JalNaadi and AquaSense are references, not starter code.

Store editable, reviewable source and small synthetic examples in Git. Follow the [artifact policy](docs/engineering/ARTIFACT_POLICY.md) for generated outputs, raw captures and renders. Never commit secrets, private uploads or local databases. Report vulnerabilities through [SECURITY.md](SECURITY.md).
