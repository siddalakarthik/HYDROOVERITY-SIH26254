# Artifact and data policy

Git stores editable source, small reviewed synthetic fixtures, configurations, manifests and concise result summaries. Avoid committing large binary results simply to show activity. The repository checker currently rejects unignored files over 1 MiB as a review gate; deliberately revise policy/check together if legitimate editable CAD source needs more space later.

Generated waveforms, simulation result arrays, renders, CAD exports and manufacturing bundles belong in ignored output directories or owner-approved private artifact storage. `simulations/results/` and `animation/renders/` retain READMEs but ignore generated payloads. Source CAD/electronics stays in Git when practical; exports use ignored `hardware/mechanical-cad/exports/` or `hardware/electronics/exports/`. Large-source Git LFS or external storage is a future explicit decision, not configured now.

For an externally stored artifact commit a small manifest recording source commit, environment, run/config/seed/scenario version, source provenance, creation time, checksum, size, retention/access policy and approved retrieval location. Do not put signed URLs, credentials or private observations in manifests. Curated small synthetic summaries may be placed outside generated directories after review; they must include denominators and failures.

Private citizen uploads, actual field captures with sensitive metadata, secrets and local databases must not enter Git or public CI artifacts. Use ignored `uploads/`, `data/private/`, `data/raw/` or `data/local/` during authorized local development, then apply a reviewed storage/retention design. Synthetic examples must be clearly labeled and contain no real personal data.

M01 does not configure external storage, Git LFS, paid services or artifact uploads. Render/video creation and CAD/PCB generation remain later milestones.
