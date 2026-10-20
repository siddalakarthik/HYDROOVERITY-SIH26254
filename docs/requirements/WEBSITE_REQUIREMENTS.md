# Website and operations requirements

Status: planned product, no pages or authentication implemented. Official name HYDROOVERITY; optional product sublabel HYDROOVERITY Operations. Source: [master context](../project/HYDROOVERITY_MASTER_CONTEXT.md), sections 7–9.

## Roles and privacy

| Role | Authorized workflow | Boundary |
| --- | --- | --- |
| Administrator | Organization settings, users/roles, provisioning, access-policy audit | Authorized destructive actions require confirmation; no implied unrestricted simulation truth |
| Utility engineer | Topology, devices, conditions, evidence, simulations and technical reports | Tenant-scoped technical access; truth access separately designed |
| Maintenance supervisor | Triage, priority, assignment, overdue review, repair review | Traceable ownership/status changes and duplicate merges |
| Field worker / technician | Assigned investigation, notes/photos, service challenge, repair and follow-up | Mobile/offline queue; backend-checked assignment/tenant scope |
| Citizen / customer | Register/login/recovery, rough location, leak/pressure/service complaint, consented photo, own status/notifications | No other residents' records or internal sensors/valves/hydrants/topology |

## Public and authenticated workflows

Public pages: home/value, How It Works with conceptual cross-section/state/acoustic diagrams, benefits/scale with coverage/cost limits, citizen reporting, contact/team/feedback, accessibility/privacy/terms. No testimonials or reliability figures invented.

Portal: sector/device overview; network explorer with real graph structure and material/diameter/length/accessibility metadata; installed collar/acoustic eligibility and coverage gaps; monitoring with flow/pressure/temperature/wetness, signal quality and stale/buffered/fault states; searchable incident center with raw evidence and reasons; acoustic lab with delays, speed assumptions, uncertainty, baselines and unresolved cases; GUARD-5 timelines, EXT/BYPASS and self-test/crosstalk/drain/fault diagnostics.

Operations: work-order priorities/assignees/deadlines/staged updates/photos/comments; assets/calibration/service status; analytics for response/MTTR/coverage and labeled-case false alerts; assumption-labeled loss estimates; date/zone-filtered CSV/PDF reports; organization/session/retention/credential settings; feedback severity, linked issue, assignee, resolution and release tracking.

Initial realtime feed is synthetic and globally marked SIMULATION, including exports and captures. Implement transport reconnect, freshness, fallback polling and useful offline/error states; choose SSE/WebSocket in M02. Real hardware ingestion is a later interface, never a fake live feed.

## Repair lifecycle

Observation -> suspected/needs review -> verified incident -> prioritized -> assigned -> field investigation -> repair recorded -> post-repair check -> closed/reopened/unverifiable. These labels describe workflow, not interchangeable proof levels. Confirmed local wetness does not establish physical leak origin. Complaints can merge with traceable provenance but are not automatic confirmation. Define comparable operating windows and allow not-verifiable repairs.

## Completion and quality

Working authentication/recovery, protected routes, persistent database, validated inputs, backend role/tenant enforcement, secure uploads/retries, rate limiting, audit history and secure APIs are mandatory. No fake login, inert forms/buttons, or hardcoded incidents portrayed as live. Implement complete user workflows with E2E evidence and loading/empty/error/offline states.

Use accessible high-contrast utility UI, text+reason alongside status colors, compact fast charts/maps and mobile-first field tasks. Optional Telugu/Hindi/English requires reviewed translation. Define practical offline scope, local storage/privacy, conflict resolution, upload retry, notification delivery and maintenance hours in M02. Do not assume offline maps without a tile/license/cache decision. Routing through external apps requires authorization.

Provisional stack is documented in [architecture](../architecture/SYSTEM_ARCHITECTURE.md); no dependencies are installed now. M02 must settle role matrix, schema, session/CSRF/recovery design, API contracts, UX, hosting compatibility and acceptance tests before implementation.
