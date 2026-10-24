# M07-B scheduling and dispatch review package

Base: `5c4c06aa915abbbd12c342aff3f08c9b37b340bb`, merged PR #19. Its exact post-merge push [run 40041137861](https://github.com/siddalakarthik/HYDROOVERITY-SIH26254/actions/runs/40041137861) passed all four required jobs before implementation.

## Delivered scope

Explicitly activated candidate operations N14–N39: **26 scheduling operations**. Combined runtime: **103 = 58 M03 + 12 M07-A + 7 M06 + 26 M07-B**. The composed design remains 168 operations, including deferred designs; implementation counts do not activate other operations. The historical M07 candidate remains frozen and is extended by an explicit runtime overlay.

Nine new tables bring migrations from 36 to **45**: dispatch_calendar_subjects, dispatch_technician_profiles, dispatch_shifts, dispatch_allocations, dispatch_policy, appointment_windows, appointment_requests, appointments and appointment_events. Four additive revisions separate governance/allocation, booking records, scope/identity hardening and audited eligibility review of existing links. Populated scheduling/provenance downgrade is refused; empty roundtrips are tested.

The existing website contains resident appointments on service details, supervisor dispatch/workload and technician agenda on work-order pages, and administrator policy/enrollment on the existing membership page. No replacement shell or new identity system is introduced. All pages use actual backend responses, versioned commands and error/loading/empty states. Appointment requests, offered alternatives, confirmed reservations, cancellation pending, cancellation and visit outcomes remain separate.

## Contract reconciliation during execution

- The owner explicitly approved supervisor-reviewed service-area and required-skill fields on service/work linkage. Null historical linkage is unschedulable. The existing N13 command can review eligibility on the same work relationship under current service/work versions; it does not invent or duplicate work. Relationship identity, tenant, purpose and original actor remain immutable. Review history and prior/current eligibility are audited. No home-entry information is added.
- The candidate allowed ELIGIBLE roster entries with null profile versions but required nonempty skills/areas for every response. The runtime overlay permits empty arrays for unenrolled members and retains nonempty requirements for ENROLLED profiles. Enrollment writes still require explicit nonempty approved values.
- Calendar collections are complete only within an explicit range of at most 60 days and at most 100 items per collection. Larger snapshots return a conflict requiring a narrower range; the UI does not claim unseen capacity is free. No omitted-data availability calculation is used. Roster, windows and workload use scoped pagination.
- Service closure with active appointments is rejected until separate versioned appointment dispositions complete. Visit outcomes do not finish operational work or scientifically verify a repair.

## Transaction and security boundary

Confirmed appointments reserve finite half-open PostgreSQL ranges including the complete arrival interval, expected service duration and both buffers. GiST exclusions prevent overlapping active allocations. Same-tenant foreign keys, subject/profile binding, one active visit per case/work and one checked-in visit per subject constrain persistence. An appointment request or alternative offer creates no allocation.

Confirmation and replacement repeat live policy, shift, membership, role, enrollment, area, skill, work-link, incident, lead-time, daily-cap and revision checks. Replacement deactivates the old commitment only inside the transaction creating the new allocation; failure rolls back both changes. Per-utility PostgreSQL advisory serialization is shared by legacy operational and governance paths, with database constraints as independent overlap protection. This deliberately favors correctness over high-throughput concurrent scheduling.

Global enrollment uses a restricted function and unique global user. No cross-utility calendar listing exists. RLS is forced on new tables, runtime remains non-owner, and every API checks current roles and ownership. Resident, staff and technician DTOs are separate; residents receive no staff directory, internal reason or work IDs. Technician briefs repeat assignment authorization and use the existing 15-minute expiry. Revocation denies access without silently erasing commitments.

CSRF, UUID idempotency keys, resource-bound fingerprints and required If-Match remain mandatory. Receipt replay returns currently authorized lifecycle state. Legacy assignment, starting scheduled work and final work transitions cannot invalidate active commitments. Overrun is a manual event and inhibits further publication while a visit remains checked in; scheduled non-overlap is not a promise about physical travel or actual visit duration.

## Reproduction and review evidence

Use the existing pinned backend and frontend environments. PostgreSQL must be real PostgreSQL 17/PostGIS with btree_gist, a non-owner hydro_app runtime, and an explicitly confirmed `hydro_disposable_` acceptance database. Never point acceptance reset at a user database.

1. Run `python services/api/tools/verify_backend.py` with private operator/runtime configuration, the explicit disposable database confirmation, and an evidence directory outside Git. Repeat independently for the traceability checker.
2. Validate both actual summaries with `services/api/tools/traceability.py --check --evidence ...` and `services/api/traceability_tests`.
3. Run `scripts/check_repository.py`, M02/M07 design checkers, `scripts/check_m07a_implementation.py`, `scripts/check_m06.py`, `scripts/check_m07b.py`, independent runtime OpenAPI validation and `git diff --check`.
4. Reproduce browser contracts with `python apps/web/tools/contracts.py --check`; run frontend typecheck, lint, formatting, unit tests and production build.
5. Prepare a dedicated synthetic fixture with `apps/web/tools/prepare_browser_fixture.py` and its explicit database/private-directory arguments. The fixture alone provisions synthetic staff, shifts and policy. Run `pnpm test:browser` against its private HTTPS instance. The suite preserves M04, M07-A and M06 scenarios before M07-B. Four `M07B-*.png` screenshots are uploaded only after successful browser checks, retained for 14 days.

The PR records actual completed local/CI executions, exact review SHA and artifact links. This document is a reproduction guide, not a substitute for those results. Sanitized evidence excludes passwords, session cookies, private configuration and scientific evaluator truth.

Completed local acceptance: 73 PostgreSQL tests passed in each of two independent sequential executions, with all 103 operations covered and matching source digests. Original M04 (two scenarios), M07-A (two), M06 (one) and M07-B (one) browser workflows passed. The M07-B workflow exercises actual request/confirmation/check-in/visit completion and generates four inspected desktop/mobile screenshots; axe WCAG checks and mobile overflow assertions passed. Nonsuccessful replacement, concurrent confirmation/cancellation, exclusive enrollment and runtime exclusion behavior are tested against actual PostgreSQL. Frontend typecheck, lint, formatting, 19 unit tests and production build passed. All 39 M05/M06 scientific tests, M08 consistency and 13 focused tests passed; full CAD regeneration remains a mandatory final CI job. No hardware or field test was performed.

## Remaining release gates

Real scheduling starts UNCONFIGURED/disabled until actual authorized utility configuration is supplied. No operating hours, shifts, skills, staff capacity, service durations, travel buffers, SLA or holiday defaults are invented. The system models explicit ranges rather than a recurrence/holiday engine. Exclusive enrollment transfer and bulk replanning are not exposed; existing commitments require explicit disposition.

N10–N12 remain disabled. Home-entry storage, privacy/encryption/key custody/consent/retention review, media/scanner/storage licensing, external notifications, offline synchronization and public deployment remain gated under D1–D10. Existing development dependency/license limitations persist. M05 results, unfavorable GUARD-5/acoustic outcomes, M06 simulation qualification, M08 digital-only caveats and manual NOT_VERIFIABLE verification remain unchanged. This is private development software with synthetic acceptance evidence, not evidence of real utility visits or physical validation.

No automatic merge or milestone closure is authorized by this review package.
