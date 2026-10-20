# HYDROOVERITY contributor and agent instructions

## Authority and project integrity

Human task authorization governs scope. Read `docs/project/HYDROOVERITY_MASTER_CONTEXT.md` and relevant requirements before work. Its FIRST RESPONSE ONLY restrictions describe onboarding, not continuing implementation authorization. `docs/project/MILESTONE_01_REQUEST.md` authorized M01 only; later milestones need separate owner instructions.

- Preserve HYDROOVERITY, Team TARK, SIH26254 and the frozen functional architecture. No arbitrary sensing technology or numbered product renaming.
- GUARD-5 has exactly five independent wetness channels: A/B/C, EXT and BYPASS. Keep EXT/BYPASS distinct; temperature/humidity are context.
- Respect supply states and independent urgent/fault observations. EAR-PAIR uses one physical sampling clock, eligible spans, uncertainty and abstention.
- Keep the ₹60,000 materials ceiling; no purchases, real infrastructure actuation or paid deployments without explicit approval.
- Prefer simple reliable engineering, follow existing architecture records, trace changes and record substantive decisions before implementing them.
- Never fabricate results or mix simulated, laboratory and field evidence. Hardware/field validation is not complete.

## Code and interfaces

- TypeScript frontend; Python backend and scientific software. Embedded languages are selected during the firmware milestone.
- Use strict typing, modular code, documented interfaces, explicit errors and appropriate tests for important logic. Avoid unnecessary dependencies.
- Keep web, API, ingestion, hardware and simulation responsibilities distinct. Folder names do not require independent microservice deployments.
- Select compatible versions and record decisions before installing the provisional stack. No fake application, fake login, inert controls or placeholder endpoints presented as implemented features.
- Feature completion requires backend/persistence wiring, validation, permissions, loading/error/offline states where relevant, reproducible checks and user-workflow evidence.

## Science and evidence

- Label assumptions, model validity, input parameters, seed, configuration hash, run/scenario version and provenance.
- Keep private ground truth separate from detector inputs and ordinary client APIs. Use blind holdouts; no cherry-picking.
- Report false positives/negatives, localization error denominators, accepted fraction, unresolved cases and confident mistakes.
- Distinguish DOCUMENTED / SIMULATED / CODE-TESTED / HARDWARE-TESTED / FIELD-VALIDATED / UNKNOWN. Historic counts are attributed, never silently rerun claims.
- No noise or no wetness is not definitive no-leak evidence. Tap calibration does not establish passive leak audibility. Confirmed wetness does not confirm its source.
- INR, bar, labeled L/min or m³/h, metres, seconds; UTC storage and Asia/Kolkata presentation.

## Security

- No credentials in source or history; `.env.example` contains placeholders only. Do not print credentials while checking authentication.
- Enforce role and tenant authorization on the backend. Citizens must not receive internal topology, device controls, private sensors or others' personal information.
- Secure uploads, rate-limit public/auth APIs and audit privileged changes. Do not expose device-control endpoints without authorization.
- Review resolved targets before destructive operations. Never overwrite unrelated files or force-push shared history.
- Review third-party licenses and attribution before copying code/assets. Project license is undecided.

## Workflow

1. Inspect relevant files and current Git state.
2. State a focused implementation plan within the authorized milestone.
3. Make focused changes and update traceability/decisions when needed.
4. Run `python scripts/check_repository.py`, `git diff --check` and relevant implemented-code tests.
5. Review the diff and staged files for scope, provenance and credentials.
6. Report changes, executed commands, passes/failures, limits and blockers honestly.
7. Commit only completed, authorized changes; use short-lived branches and PRs for substantial future work.

M01's single initial commit directly to `main` is explicitly authorized. Do not impose review rules that block the sole maintainer. Do not begin M02 merely because the backlog exists.
