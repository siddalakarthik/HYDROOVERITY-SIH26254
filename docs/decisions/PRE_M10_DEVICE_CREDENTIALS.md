# Pre-M10 device identity and credential boundary

Owner authority: master pre-M10 A08 and trusted-ingestion preparation. Start from
verified main506e9ed64f69d36703cc958350ef6c32bebaeb91; all four postmerge jobs
40361239810 passed. Preserve all114 prior runtime operations and all frozen
scientific/hardware source.

First increment implements the existing M02 list/register/read-device and
issue/revoke-credential contracts. Registration records proposed metadata with
UNKNOWN health; it is not physical provisioning, a capture receipt or scientific
proof. Device kind/environment become immutable. No payload or human-facing
registration can approve a physical acquisition binding.

A separate append-only provisioning-binding table is writable only by the
existing migration/test operator, never hydro_app or an ADMIN UI. This increment
permits bindings only in an explicitly named hydro_disposable_ database with
SYNTHETIC_TEST_ONLY classification. Real physical binding/provisioning stays
closed pending independent hardware/operator review. This is an executable
security foundation, not activation of field hardware. No new elevated database
function or public deployment is needed.

Issue requires current active ADMIN, devices.write, same device/utility, fresh
reauthentication, CSRF, UUID idempotency key, matching credential environment,
bounded future expiry and an eligible binding. Return a random secret only on
first committed response; persist only its verifier. Replays reauthorize before
returning409 with no secret; no raw-response or credential/body cache. Lost reply
requires revocation and a new operation key. Revocation checks the same device
and current binding/utility and is auditable/idempotent. No secret in audit,
outbox, logs, frontend persistence or ordinary device reads. Token possession
never authenticates human APIs or authorizes infrastructure control.

Additive migration refuses populated downgrade. Real PostgreSQL tests must
cover one-time issuance, non-redisclosure, wrong tenant/device/environment,
expired/revoked identity, old role, CSRF, TTL, concurrency, RLS and no verifier
projection. Ordinary registration remains usable without hardware approval;
credential issuance is explicitly unavailable without reviewed binding. Contact
retention, offline/media, evaluator truth and physical verification remain gated.

A08 remains BLOCKED while ordinary contact governance and actual physical
provisioning remain unresolved. No claim of physical capture is introduced.

Executed focused evidence:13 real PostgreSQL cases passed, including concurrent
same-key issuance, durable key non-redisclosure after ordinary receipt cleanup,
SQL RLS, current role/tenant denial, CSRF/Origin/fresh-auth, permanent revocation,
immutable profile/binding, atomic rollback, bounded expiry and populated downgrade
refusal and an executed empty downgrade/upgrade. The round-trip test releases
its read transaction before Alembic opens a separate DDL connection. Proposed-device registration/read and server-side credential denial also
passed an actual HTTPS320px browser workflow with no axe violations. The browser
fixture account mismatch was corrected; no application authorization was relaxed.
Runtime119 registered operations and57 tables are candidate inventory, with all114
previous operations preserved by an explicit additive source/whole-API amendment.
Local regression evidence:118 existing backend tests and30 frontend unit tests
passed; frontend typecheck, lint, format and production build passed. Final
required CI must pass on the review commit before conditional merge.
