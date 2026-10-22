# Product information architecture

M07 review note: the [candidate route catalogue](../../design/ui-ux/m07-route-catalog.json) proposes five additional service pages and gated associations for existing maintenance/work/notifications/admin pages. The live M04 catalogue remains46 classified routes and is byte-unchanged. All new pages are PROPOSED_NOT_ROUTED, online-only, with existing M02 tokens and M04 design direction preserved. See [page specifications](m07/README.md) and do not enable navigation before real backend acceptance.

Issue #2; HYDROOVERITY Operations, design only. Public explanation, citizen ownership, assigned field work, supervisor operations, engineer investigation and tenant administration share a visual system but separate navigation/permissions. One organization switcher chooses an active membership; selecting an organization never grants access. Every API path revalidates it. Internal route `{org}` resolves to authorized UUID, not arbitrary client organization context.

Public header: Solution, How it works, Benefits/limitations, Project status, Report water issue, Contact. Citizen navigation: My reports, New report, Notifications, Account. Worker navigation: My tasks, Pending sync, Notifications. Supervisor navigation: Overview, Incidents, Work orders, Complaints, Maintenance, Reports. Engineer adds Network, Monitoring, Devices, Acoustics, Simulations. Admin navigation: Users, Settings, Audit; admin does not inherit telemetry rights. Shared account/session pages are outside tenant data views.

Primary journeys: citizen reports -> private tracking -> supervisor review -> concern/investigation -> assigned task -> worker repair receipt -> supervisor review -> comparable verification -> public-safe update. Engineer's measurement journey: select mode/zone -> freshness/quality -> competing explanation -> eligible capture -> candidate interval/abstention -> incident evidence. Simulation journey: allow-listed scenario -> validated config/noise seed -> queued isolated job -> explicit synthetic outputs -> separately authorized evaluation -> provenance-preserving report. No world-readable tracking-number search: authentication and ownership remain required.

Related diagnostics are tabs inside device/collar pages rather than redundant standalone hardware dashboards. Maintenance planning reuses work-order filters; analytics uses the reports projection rather than a separate metrics warehouse. Every route below has detailed behavior in the page specification; machine-readable route catalogue is a consistency index, not a running router.

| ID | Route | Audience | Primary objective |
| --- | --- | --- | --- |
| PAGE-01 | `/` | PUBLIC | Understand mission and honest project status |
| PAGE-02 | `/solution` | PUBLIC | Understand evidence-qualified integrated system |
| PAGE-03 | `/how-it-works` | PUBLIC | Follow WATCH, GUARD-5, EAR and VERIFY |
| PAGE-04 | `/solution/guard5` | PUBLIC | Inspect five conceptual channels and unvalidated collector mechanics |
| PAGE-05 | `/solution/acoustics` | PUBLIC | Understand eligible spans, intervals and abstention |
| PAGE-06 | `/benefits-and-limitations` | PUBLIC | Compare intended benefits with coverage and validation limits |
| PAGE-07 | `/project-status` | PUBLIC | See designed versus implemented versus physically validated status |
| PAGE-08 | `/report` | PUBLIC | Select an enabled utility and sign in to report |
| PAGE-09 | `/contact` | PUBLIC | Submit a bounded question or feedback |
| PAGE-10 | `/privacy` | PUBLIC | Understand data collection, retention and rights contact |
| PAGE-11 | `/terms` | PUBLIC | Read proposed service and demonstration boundaries |
| PAGE-12 | `/login` | PUBLIC | Sign in using the single backend session |
| PAGE-13 | `/register` | PUBLIC | Register as citizen for enabled utility only |
| PAGE-14 | `/forgot-password` | PUBLIC | Request generic account recovery |
| PAGE-15 | `/reset-password` | PUBLIC | Consume one-use reset token |
| PAGE-16 | `/verify-account` | PUBLIC | Verify an account with one-use token |
| PAGE-17 | `/accept-invitation` | PUBLIC | Accept exact tenant staff invitation |
| PAGE-18 | `/account` | ALL | Edit own profile and choose membership |
| PAGE-19 | `/account/sessions` | ALL | Inspect and revoke own sessions |
| PAGE-20 | `/citizen/{org}/reports` | CITIZEN | View only own reports |
| PAGE-21 | `/citizen/{org}/reports/new` | CITIZEN | Submit category, description, coarse area and consented photo |
| PAGE-22 | `/citizen/{org}/reports/{id}` | CITIZEN | Track safe updates, add followup and resolution feedback |
| PAGE-23 | `/app/{org}/overview` | ENGINEER,SUPERVISOR | Review supply states, active concerns, stale devices and coverage gaps |
| PAGE-24 | `/app/{org}/network` | ENGINEER,SUPERVISOR | Explore surveyed graph and instrumented/unobserved spans |
| PAGE-25 | `/app/{org}/monitoring` | ENGINEER,SUPERVISOR | Read fresh and historic observations with explicit provenance |
| PAGE-26 | `/app/{org}/devices` | ENGINEER,SUPERVISOR,ADMIN | Find devices by identity, health and source environment |
| PAGE-27 | `/app/{org}/devices/{id}` | ENGINEER,SUPERVISOR,ADMIN | Inspect permitted device metadata, diagnostics and calibration tabs |
| PAGE-28 | `/app/{org}/collars/{id}` | ENGINEER,SUPERVISOR | Inspect five channel timelines, EXT/BYPASS and service receipts |
| PAGE-29 | `/app/{org}/acoustics` | ENGINEER | Choose authorized capture and eligible span |
| PAGE-30 | `/app/{org}/acoustics/{id}` | ENGINEER | Compare delay baselines, assumptions, interval and unresolved reasons |
| PAGE-31 | `/app/{org}/incidents` | ENGINEER,SUPERVISOR | Filter and triage concerns without equating severity with confidence |
| PAGE-32 | `/app/{org}/incidents/{id}` | ENGINEER,SUPERVISOR | Read immutable evidence timeline and authorize next investigation action |
| PAGE-33 | `/app/{org}/work-orders` | ENGINEER,SUPERVISOR,TECHNICIAN | Use supervisor board or technician assigned-task list |
| PAGE-34 | `/app/{org}/work-orders/{id}` | ENGINEER,SUPERVISOR,TECHNICIAN | Investigate, record work and submit for review |
| PAGE-35 | `/app/{org}/repairs/{id}/verification` | ENGINEER,SUPERVISOR,TECHNICIAN | Review comparable before/after evidence and separate outcome |
| PAGE-36 | `/app/{org}/complaints` | SUPERVISOR | Review public-safe reports and link evidence without automatic confirmation |
| PAGE-37 | `/app/{org}/maintenance` | SUPERVISOR | Review overdue work and assign priorities and due dates |
| PAGE-38 | `/app/{org}/analytics` | ENGINEER,SUPERVISOR | Inspect explicit denominators, response time and observable coverage |
| PAGE-39 | `/app/{org}/reports` | ENGINEER,SUPERVISOR | Request scoped CSV/PDF and download authorized completed export |
| PAGE-40 | `/app/{org}/simulations` | ENGINEER | Select allowed scenario/config and queue a reproducible run |
| PAGE-41 | `/app/{org}/simulations/{id}` | ENGINEER | Inspect status and synthetic outputs; evaluation separately gated |
| PAGE-42 | `/app/{org}/feedback` | ALL | Review own feedback or authorized internal backlog |
| PAGE-43 | `/app/{org}/notifications` | ALL | Read only own safe notifications |
| PAGE-44 | `/app/{org}/admin/users` | ADMIN | Invite, grant primary roles and suspend tenant memberships |
| PAGE-45 | `/app/{org}/admin/settings` | ADMIN | Manage tenant and integration references without returning secrets |
| PAGE-46 | `/app/{org}/admin/audit` | ADMIN | Inspect safe privileged-action history |

No route is implemented. Conditional controls require the endpoint permission and resource scope, even when a page itself is visible. Hidden controls are usability, never security enforcement.
