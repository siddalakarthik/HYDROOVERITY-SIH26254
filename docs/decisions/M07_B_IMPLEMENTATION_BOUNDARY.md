# M07-B implementation boundary

Owner-authorized scope: N14–N39 scheduling and dispatch, using the approved M07 candidate contracts. Base: `5c4c06aa915abbbd12c342aff3f08c9b37b340bb` (merged PR #19). Post-merge push run [40041137861](https://github.com/siddalakarthik/HYDROOVERITY-SIH26254/actions/runs/40041137861) passed repository-integrity, m03-backend, m08-cad-and-figures and m04-frontend; independently checked before branch creation.

Implementation proceeds through database constraints and governance, transactional bookings, existing-page integration, and real PostgreSQL/browser acceptance. This document records implementation boundaries, not a claim that those stages have passed.

- Real utility policy starts UNCONFIGURED and disabled. No shifts, rosters, durations, buffers, service commitments or availability are seeded outside isolated synthetic tests.
- Requests and offers do not reserve capacity. Confirmation and replacement must atomically update the allocation ledger, assignment, appointment, service history and audit. Failed replacement preserves the original commitment.
- Dated shifts and finite half-open allocation ranges use PostgreSQL constraints. Enrollment is exclusive per global user. Legacy assignment and cancellation paths must participate in scheduler guards.
- Visit completion remains separate from repair completion and independent verification. M06 observations remain SIMULATION evidence. M05/M08 sources and results remain unchanged.
- N10–N12 remain disabled. No home-entry information, external delivery, images, offline synchronization or public deployment is introduced.
- Approval gate: one tested M07-B review PR; no automatic merge or milestone closure.
