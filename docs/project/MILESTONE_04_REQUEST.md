# HYDROOVERITY — M04 PROFESSIONAL FRONTEND IMPLEMENTATION
## Complete Engineering, UI/UX, Integration, Security, Accessibility, Testing and Delivery Instructions

**Project:** HYDROOVERITY\
**Team:** TARK\
**Challenge:** SIH26254\
**Repository:** https://github.com/siddalakarthik/HYDROOVERITY-SIH26254\
**Milestone:** M04 — Frontend Foundation\
**GitHub Issue:** #4\
**Implementation Branch:** `feature/m04-frontend-foundation`\
**Reference main commit at authorization:** `e0122f5ee4146e49ae6113a1aa6a5ee444b25973`

---

# 0. YOUR ROLE AND MISSION

You are joining HYDROOVERITY as a coordinated senior engineering and product-design team.

Perform the responsibilities of:

- Principal Frontend Engineer
- Senior Next.js/React Architect
- Professional UI/UX and Design Systems Engineer
- Water-Utility Operations Product Designer
- GIS and Geospatial Interface Engineer
- Frontend Application Security Engineer
- Accessibility Engineer
- Full-Stack Integration Engineer
- Automated Browser Testing Engineer
- DevOps and CI Engineer
- Technical Documentation and Code Review Engineer

You are responsible for creating an exceptionally polished, understandable, responsive, technically accurate, secure and maintainable website.

Your output must be **working production-quality application code suitable for further engineering review**, not a collection of attractive screenshots or disconnected components.

The website should demonstrate professional product-design craftsmanship comparable to carefully designed enterprise infrastructure software.

Do not optimize for generating the maximum number of pages. Optimize for genuine usefulness, information clarity, reliable operation, excellent visual design and truthful engineering representation.

The completed frontend must be usable by ordinary people, technical engineers, supervisors, administrators and field technicians within their actual authorized capabilities.

## Primary mission

Transform HYDROOVERITY's completed engineering architecture and M03 backend into a cohesive, working web application that:

1. Explains the project clearly to the public.
2. Gives authorized users their appropriate workspaces.
3. Provides real authentication and persistent workflows.
4. Visualizes actual permitted infrastructure records.
5. Connects implemented UI interactions to real M03 APIs.
6. Makes scientific uncertainty and provenance understandable.
7. Remains professionally designed across desktop, tablet and mobile.
8. Gives honest states for capabilities not yet connected.
9. Uses free/open-source development dependencies and avoids compulsory paid services.
10. Produces reproducible browser, integration, security and CI evidence.
11. Preserves the existing sensing architecture, technical records and Git history.
12. Opens a reviewed M04 pull request without autonomously merging or closing issue #4.

**This owner-supplied request explicitly authorizes implementation of M04, but not other milestones or deployment to public infrastructure.**

---

# 1. CONFIRMED PROJECT STATUS

Do not restart previously completed milestones.

The following are merged and completed:

- M01 — Repository Foundation
- M02 — Website Architecture and Database Design
- M03 — Backend Foundation
- M05 — Scientific Simulations
- M08 — Digital Hardware Engineering

M03 recovery PR #15 has been merged.

Latest verified main baseline:

`e0122f5ee4146e49ae6113a1aa6a5ee444b25973`

Main GitHub Actions run:

`39588590017`

All three required CI jobs passed.

GitHub issue #3 is closed.

GitHub issue #4 is open and is the implementation target.

## Existing M03 backend

M03 has:

- Python/FastAPI application
- PostgreSQL/PostGIS persistence
- Session authentication and CSRF protection
- Role-based and tenant-scoped authorization
- Organization and membership management
- Zone and pipeline-asset operations
- Citizen complaints and follow-ups
- Incident triage and state transitions
- Work-order creation and assignments
- Technician action and repair records
- Independent verification records
- Audit history
- Strict evidence-based traceability
- Executed authentication and workflow testing
- Local HTTPS integration

Canonical design inventory:

- 117 planned API operations
- 58 currently implemented and tested API operations
- 59 deferred API operations
- 57 target database tables
- 30 currently migrated database tables
- 46 M02-designed website routes
- 10 M02 design wireframes

These counts are the verified starting baseline, not a guarantee that future Git changes cannot affect them.

Read the current repository state and verify before coding.

Do not implement the missing 59 operations merely to make a frontend page look functional.

---

# 2. REQUIRED REPOSITORY INSPECTION — BEFORE ANY CODE

Read the repository instructions and canonical contracts.

At minimum inspect:

## General

- `AGENTS.md`
- `README.md`
- `docs/project/HYDROOVERITY_MASTER_CONTEXT.md`
- `docs/project/ROADMAP.md`
- `docs/project/M03_M04_IMPLEMENTATION_SEQUENCE.md`
- `docs/project/PROJECT_CHARTER.md`
- `docs/decisions/DECISION_LOG.md`

## Product and design

- `docs/architecture/PRODUCT_INFORMATION_ARCHITECTURE.md`
- `docs/requirements/WEBSITE_REQUIREMENTS.md`
- `docs/requirements/SYSTEM_REQUIREMENTS.md`
- `design/design-system/UI_UX_DESIGN_SYSTEM.md`
- `design/wireframes/PAGE_AND_WIREFRAME_SPECIFICATIONS.md`
- `design/ui-ux/m02-route-catalog.json`

## Backend and contracts

- `docs/architecture/API_CONTRACTS.md`
- `docs/architecture/openapi-design.json`
- `data/schemas/m02-api-inventory.json`
- `data/schemas/m03-implementation-matrix.json`
- `docs/architecture/ROLE_PERMISSION_MATRIX.md`
- `docs/architecture/AUTH_SECURITY_AND_PRIVACY.md`
- `docs/architecture/DOMAIN_STATE_MACHINES.md`
- `docs/architecture/DATA_CONTRACTS_AND_PROVENANCE.md`
- `docs/architecture/REALTIME_OFFLINE_AND_NOTIFICATIONS.md`
- `docs/architecture/SYSTEM_ARCHITECTURE.md`
- `docs/architecture/THREAT_MODEL.md`

## Implemented application

- `services/api/README.md`
- `services/api/compose.yaml`
- `services/api/hydro/main.py`
- `services/api/hydro/routes.py`
- `services/api/hydro/contracts.py`
- `services/api/hydro/auth.py`
- `services/api/hydro/security.py`
- `services/api/hydro/services/`
- `docs/engineering/M03_BACKEND_IMPLEMENTATION_REPORT.md`
- `docs/testing/M03_ACCEPTANCE_RESULTS.md`
- `docs/testing/M03_POST_MERGE_CI_RECOVERY.md`

## Deployment

- `docs/deployment/DEPLOYMENT_AND_STACK_DECISIONS.md`
- `.github/workflows/repository-integrity.yml`

Treat any historical documentation that says M03 has not yet started as stale status, not permission to overwrite completed work.

Prefer the actual current backend implementation and reviewed M03 contract corrections when resolving differences between old planning language and executable code.

### Required first deliverable

Before modifying code, produce a concise engineering implementation plan identifying:

1. Current repository/branch status.
2. Actual available backend operations.
3. Required frontend modules.
4. Design-system decisions.
5. Authentication integration strategy.
6. Route-by-route availability classification.
7. Free map/data strategy.
8. Browser and security testing strategy.
9. Incremental implementation checkpoints.
10. Existing constraints, unresolved choices and risks.

Then proceed with authorized M04 work. Do not stop after generating the plan unless a destructive action, expense, unavailable credential or substantive contract change requires owner intervention.

---

# 3. GIT SAFETY AND BRANCH STRATEGY

Work from the latest approved remote `main`.

Before coding:

1. Inspect `git status`.
2. Inspect the current branch.
3. Fetch remote refs.
4. Confirm the latest main SHA.
5. Check for existing worktrees and uncommitted changes.
6. Preserve all unrelated changes.
7. Create an isolated M04 branch or worktree.

Use:

`feature/m04-frontend-foundation`

If that exact branch already exists, inspect and reuse it safely rather than overwriting work.

Never force-push main.

Never reset, delete or discard another milestone's files.

Never merge M04 into main automatically.

Never close issue #4 automatically.

Commit reviewable checkpoints.

At the end, push the tested feature branch, open a pull request targeting main, associate issue #4, and stop for owner review.

---

# 4. FROZEN HYDROOVERITY ARCHITECTURE

HYDROOVERITY is an integrated water-infrastructure evidence and maintenance platform.

Its subsystems remain:

## HYDRO-WATCH

Hydraulic pressure/flow context, intermittent supply-state interpretation and anomaly qualification.

## GUARD-5

A proposed external non-pressure-bearing joint collar with exactly five independent wetness channels:

- `COLLAR_A`
- `COLLAR_B`
- `COLLAR_C`
- `COLLAR_EXT`
- `COLLAR_BYPASS`

EXT is an environmental reference.

BYPASS is a separate collection-bypass witness.

They are not interchangeable with protected pockets A/B/C.

## HYDRO-EAR

Two pipe-contact acoustic channels captured under one physical stereo sampling clock.

Acoustic localization is a qualified interval on an eligible surveyed span, not an automatically precise geographic leak marker.

## Evidence Qualification

Distinguishes observation, suspicion, qualified candidates, faults and unresolved outcomes.

Preserve uncertainty, source classification and freshness.

## HYDRO-VERIFY

Incident, investigation, assignment, repair and independent evidence-based verification.

A finished work order does not automatically prove the leak is eliminated.

### Mandatory integrity

Do not fabricate:

- Connected devices
- Live sensor telemetry
- Physical measurements
- Real leak locations
- Field deployment
- Physically validated performance
- Water savings
- Actual customer testimonials
- Actual installation counts
- False-positive/accuracy results
- Repair verification success
- Geographical infrastructure coverage

Historical simulation outputs may be referenced only with accurate source and limitations.

Hardware connection remains pending.

The frontend must be architecturally ready to display future authorized hardware records without claiming the connection already exists.

Do not implement hardware acquisition, firmware integration, sensor provisioning or simulated-to-field conversion in M04.

The explanation video remains paused.

---

# 5. TECHNICAL STACK

Use the approved M02 technology direction unless a verified compatibility issue requires a documented correction.

## Core frontend

- Node.js 24 LTS, maintained compatible patch
- Next.js 16 App Router family
- React 19 compatible stable release
- TypeScript strict mode
- Tailwind CSS 4
- CSS custom properties/design tokens
- Native Web Platform APIs where sufficient

## UI dependencies

Use a small, well-reviewed set of open-source libraries.

Candidates:

- Lucide React for consistent vector icons
- Radix accessible primitives where necessary
- React Hook Form for complex forms
- Zod for frontend validation when beneficial
- TanStack Query only where its caching and mutation behavior are justified
- TanStack Table for advanced tables where helpful
- Recharts for genuinely sourced measurements, when enabled
- MapLibre GL JS for authorized geospatial views
- Vitest and React Testing Library
- Playwright
- axe-core or equivalent accessibility tooling

Do not add every library automatically.

Check current packages, maintenance, compatibility, peer dependencies, licensing and bundle consequences.

Use exact reproducible dependencies and commit an appropriate lockfile.

Do not use vulnerable or incompatible versions just because they appear in an example.

Do not introduce large animation or component packages without a demonstrated need.

## Backend ownership

FastAPI remains the sole authentication and domain authority.

Do not add:

- A second identity database
- NextAuth as a parallel authentication system
- Firebase Authentication
- Supabase Authentication
- Client-trusted roles
- Separate mock authentication tokens
- Hardcoded backend response stubs in production

## Hosting and cost

No paid SaaS dependency is allowed without separate approval.

The application must run locally.

No production domain purchase or cloud bill is authorized.

Developer tooling may require internet access for free package installation, but core local workflows must not depend on a paid cloud account.

Document any externally supplied service that is free only within usage limits; do not call that universally free.

---

# 6. PRODUCT DESIGN PHILOSOPHY

The design must appear human-crafted, credible, distinctive and operationally useful.

Avoid recognizable low-effort template patterns such as:

- Excessive gradient backgrounds
- Glassmorphism across every panel
- Purple/pink AI-style gradients
- Too many floating cards
- Arbitrary decorative percentages
- Giant empty hero sections
- Repeated identical card arrangements
- Emoji in operational navigation
- Unnecessary 3D illustrations
- Fake animated data streams
- Fabricated map markers
- Irrelevant stock photographs
- Overwhelming animation
- Tiny gray text
- Generic marketing buzzwords
- Screens containing dozens of meaningless buttons

Do not imitate another company's trademarked design or copy proprietary assets.

### Desired character

HYDROOVERITY should feel like:

- A serious civil infrastructure platform
- A refined modern enterprise application
- A product prepared by thoughtful engineers and experienced designers
- Precise, calm, understandable and trustworthy
- Capable of handling operational complexity without becoming confusing

The visual language should balance technology with public-service usability.

Use deliberate visual hierarchy, typographic restraint, space, grid rhythm, clean alignment, meaningful imagery, correct units and precise terminology.

Visual polish must not come at the cost of functionality.

---

# 7. APPROVED DESIGN SYSTEM AND VISUAL DETAILS

Use M02's approved design tokens as the baseline.

## Primary light palette

| Role | Color |
|---|---|
| Canvas | `#F4F7FA` |
| Surface | `#FFFFFF` |
| Primary text | `#172B3A` |
| Muted text | `#47596B` |
| Brand/action | `#075985` |
| Border | `#CBD5E1` |
| Danger | `#991B1B` |
| Warning | `#854D0E` |
| Success | `#166534` |
| Simulation | `#6B21A8` |

Implement accessible shades and interactive states using these foundational values.

Avoid using color alone to indicate status.

A scientifically unverified repair must never inherit a success color solely because a work order is complete.

## Typography

Use a professional, consistently rendered font strategy.

Prefer a high-quality native/system sans-serif stack compatible with the approved M02 standard.

On Windows, Segoe UI is a suitable system-font component.

If a bundled open-license font such as Inter demonstrably improves consistency, verify its license and document the decision before adopting it.

Do not load proprietary or paid font files.

Suggested typographic scale, subject to M02:

- Main heading: 32px / 40px
- Section heading: 24px / 32px
- Subsection heading: 20px / 28px
- Body: 16px / 24px
- Labels: 14px with appropriate weight
- Metadata: approximately 14px
- Avoid routine text below 12px

Prefer tabular numerals for engineering values.

Always display measurement units.

## Layout

- Maximum content width: approximately 1440px
- Desktop: 12-column grid
- Side navigation: approximately 240px
- Tablet: adaptive/collapsible navigation
- Mobile: single-column primary content below 640px
- Touch targets: 44px preferred product target
- Consistent spacing scale: 4, 8, 12, 16, 24, 32, 48, 64px
- Input corner radius approximately 6px
- Panel corner radius approximately 10px
- Subtle and consistent elevation only where it conveys hierarchy

Do not leave desktop screens awkwardly empty.

Do not squeeze desktop tables into unreadable mobile layouts.

## Page anatomy

Authenticated pages should consistently provide:

1. Organization and mode context.
2. Page title and short purpose.
3. Appropriate breadcrumbs.
4. Relevant current navigation section.
5. Primary authorized action.
6. Useful filters where supported.
7. Main content.
8. Visible data provenance/freshness when applicable.
9. Accessible error/empty/loading conditions.
10. Helpful context or next step.

Build a small, reusable component system rather than individually hardcoding every page.

Suggested primitives:

- AppShell
- PublicShell
- Header
- Sidebar
- MobileNavigation
- OrganizationSwitcher
- Breadcrumbs
- PageHeading
- SectionHeading
- StatusBadge
- ProvenanceLabel
- DataQualityNotice
- EmptyState
- LoadingSkeleton
- ErrorState
- PermissionDenied
- SearchInput
- FilterBar
- DataTable
- DetailPanel
- Timeline
- FormField
- ConfirmationDialog
- Toast/Receipt
- ModeIndicator
- SourceTimestamp
- MapLegend
- UnavailableFeatureNotice

Each component must solve a real need.

Do not create a giant component factory or abstract design system that becomes difficult to maintain.

---

# 8. INFORMATION ARCHITECTURE AND ALL 46 ROUTES

The M02 route catalogue is the authoritative source for the complete intended product.

Do not silently rename established paths.

Do not pretend every planned route is already backed by an implemented service.

Before implementation, generate an M04 route capability matrix with the following fields:

- M02 page ID
- Canonical route
- Audience/roles
- Required backend operations
- Implemented/deferred operation status
- Actual M04 delivery status
- Required view components
- Security checks
- Expected data
- Empty/error states
- Browser acceptance tests
- Future dependency if deferred

Classify each of the 46 planned routes as:

**ACTIVE_FUNCTIONAL:** Supported by working implemented APIs or genuine static reviewed content.

**ACTIVE_READ_ONLY:** Legitimate permitted data inspection, without unsupported actions.

**INFORMATIONAL:** Explains a concept or upcoming capability without pretending to operate it.

**DEFERRED:** Not activated in the user navigation because the required backend or data pipeline is missing.

Do not build 46 fake dashboard shells simply to say all 46 pages are completed.

## Public routes — PAGE-01 to PAGE-11

### PAGE-01 `/`

Build a premium public landing page.

Provide:

- Professional HYDROOVERITY identity
- Clear mission statement
- Concise problem context
- Overview of the five-part architecture
- Explanation of detection versus evidence versus verification
- Direct paths to the solution, project status and reporting
- Appropriate visuals derived from reviewed engineering concepts
- Clear technical limitations
- Professional responsive footer

Suggested hero message:

**Find the leak. Understand the evidence. Verify the repair.**

Supporting language should be specific and factual, not exaggerated.

Do not claim deployed coverage or proven leak-detection accuracy.

### PAGE-02 `/solution`

Explain the integrated architecture through a carefully structured visual flow.

Describe how WATCH, GUARD-5, EAR, evidence qualification and VERIFY complement one another.

Use clear original diagrams and concise technical explanations.

### PAGE-03 `/how-it-works`

Present a step-by-step explanation understandable to non-specialists.

Distinguish available measurements, interpretations, limitations and maintenance actions.

### PAGE-04 `/solution/guard5`

Explain exactly five wetness channels.

Include an accessible conceptual representation of A/B/C/EXT/BYPASS.

Clearly distinguish proposed guard geometry from physically verified performance.

### PAGE-05 `/solution/acoustics`

Explain the two synchronized pickup channels, signal conditions, candidate interval and unresolved states.

Do not visually imply an exact street-level crack location.

### PAGE-06 `/benefits-and-limitations`

Explain intended benefits and engineering limitations side by side.

No invented financial savings, percentages or field success rates.

### PAGE-07 `/project-status`

Consume the real implemented public project-status endpoint.

Present approved statuses such as documented, simulated, digitally designed, code-tested, physically unvalidated and pending integration.

Avoid converting backend project status into unsupported operational metrics.

### PAGE-08 `/report`

Provide a clear reporting entry point.

Use the real enabled-utility lookup and appropriate authentication/organization flow.

No publicly searchable complaint details.

### PAGE-09 `/contact`

The M02 design includes a contact operation, but it is not among the 58 implemented M03 routes.

Do not submit to a fictional endpoint.

Provide approved static contact information only if present in canonical sources, or a clear unavailable-contact state. Do not invent addresses or silently route private submissions to third parties.

### PAGE-10 `/privacy`

Present accurate current software privacy practices and applicable development limitations.

Do not claim compliance certification or legal terms that have not been reviewed.

### PAGE-11 `/terms`

Provide a clearly identified project-use/information page based on approved content, with legal-review status explicit where needed.

Do not invent a finalized binding legal agreement.

---

# 9. AUTHENTICATION AND ACCOUNT EXPERIENCE — PAGE-12 TO PAGE-19

This entire section must use real FastAPI authentication.

Required interfaces:

- Login
- Citizen registration
- Forgot password
- Password reset
- Account verification
- Invitation acceptance
- Account/profile
- Membership selection
- Session management
- Logout

## Session ownership

FastAPI exclusively owns sessions.

Use the established same-origin architecture.

Preserve:

`__Host-hydro_session`

Cookie attributes:

- Secure
- HttpOnly
- SameSite=Lax
- Path=/
- No Domain

Do not weaken cookie security merely to simplify local development.

Do not store session tokens in localStorage, sessionStorage, URLs or client-readable cookies.

## CSRF

Before appropriate mutations, obtain the real synchronizer token via:

`GET /api/v1/auth/csrf`

Use the actual endpoint contract and validated Origin/Referer policy.

Authenticated mutations must send the proper `X-CSRF-Token`.

Handle session/CSRF rotation after login and changes in authentication state.

Do not fabricate a token or bypass protection.

## Next.js integration

Prefer fixed same-origin API routing through the reviewed HTTPS proxy.

If SSR must forward cookies to the internal API, send them only to the fixed internal API destination.

Never reflect raw attacker-provided URLs into server requests.

Do not log cookies or sensitive headers.

Prevent private SSR responses from entering shared caches.

Do not build an independent identity layer in the Next.js application.

## Login UX

- Clear email/password fields
- Password visibility toggle
- Password-manager compatibility
- Paste support
- Validated error handling
- Pending state
- No duplicate submissions
- Forgot-password path
- Appropriate destination after successful authentication

## Registration

Allow only the intended citizen registration workflow.

Do not expose open staff registration.

Organization eligibility must come from actual server data.

Do not assign administrator, engineer, evaluator or technician rights in the frontend.

## Recovery and verification

Follow the existing one-time token contracts exactly.

Avoid exposing token values through analytics, logs, browser history or unnecessary referrers.

Respect reset-session revocation.

Give generic public responses where required to prevent account enumeration.

For local private development, clearly document the existing private development-mail procedure. Do not claim external email delivery is implemented.

## Profile

Use actual `/me` endpoints and response schemas.

Support authorized profile changes, membership selection and current identity details.

## Sessions

Present permitted session records and real session revocation.

Do not expose session secrets.

After current-session revocation, show the correct logged-out state.

## Role/organization changes

Clear organization-scoped client caches on every organization switch.

Do not preserve previous tenant data in the next tenant's view.

Treat returned memberships as navigation options, not as user-authorized permissions unless the backend confirms access.

A role visible in the UI does not bypass actual operation-level permission checks.

---

# 10. CITIZEN REPORTING EXPERIENCE — PAGE-20 TO PAGE-22

Build a genuinely usable public-service reporting workflow for signed-in citizens.

## My reports

Show only the authenticated citizen's authorized reports.

Use real list responses.

Provide understandable:

- Tracking reference where supported
- Complaint category
- Current state
- Created/updated dates
- Safe public progress
- Link to report details

## New report

Build a fully validated form using the exact implemented complaint schema.

Possible concepts include complaint category, description, permitted approximate area and appropriate consent fields, but only enable fields supported by the actual contract.

Do not invent a public precise-location requirement.

Do not force users to expose exact home coordinates.

Do not enable photograph upload until the real secure attachment lifecycle exists.

Explain that photos are not currently supported if necessary.

## Report details

Display only citizen-safe responses.

Allow authorized follow-up through the implemented endpoint.

Keep follow-up content and length within actual backend limits.

Show persisted status after server confirmation.

Do not mark complaints as confirmed physical leaks simply because citizens submitted them.

Do not expose:

- Internal pipeline topology
- Sensor locations
- Technician private notes
- Other residents' records
- Internal infrastructure security details

## Mobile usability

A citizen should be able to understand and submit a report comfortably on a low- or mid-range Android phone.

Use an uncomplicated, short, forgiving form.

Retain safe unsent form input when reasonable, without leaving confidential data in persistent browser storage without approval.

---

# 11. AUTHORIZED UTILITY WORKSPACE — PAGE-23

Build a genuinely useful organization overview.

Use only the available organization, incident, complaint, zone, pipeline and work-order data permitted for the current role.

The overview should not be one enormous grid of unrelated cards.

Prefer a clear task-oriented composition:

- Organization identity
- Current work requiring attention
- Incident status summaries
- Open work-order overview
- Relevant complaint activity
- Safe links to assigned or authorized actions
- Data coverage and availability notices
- Last-refreshed time

Compute totals only from an authoritative complete response or explicitly label them as current-page counts.

Do not infer organization-wide totals from the first page of a paginated API.

Do not show sensor uptime, flow charts, leak percentages, pressure readings or water savings without their implemented sources.

Where no data exists, show an informative empty state.

A truly empty dashboard is acceptable when honestly represented.

Do not insert random realistic-looking values.

---

# 12. NETWORK EXPLORER AND GIS — PAGE-24

This is an important product feature.

Use actual M03 organization-authorized data for:

- Water zones
- Network junctions
- Pipe segments

Use the implemented GET/POST/PATCH operations when authorized by role.

## Map technology

Prefer MapLibre GL JS for the interactive map.

No compulsory paid tile service.

Do not assume OpenStreetMap's public tile server is an unlimited free production backend.

Investigate an appropriately licensed local basemap option, such as a small, bounded local tile package or PMTiles source, if it can be reproduced and hosted without new subscription charges.

If that is not practical within M04, deliver a fully usable asset-map view using actual API-provided geometry and a clearly styled blank/schematic geographical canvas.

The map must still work without external basemap requests.

A real infrastructure map can be useful without a proprietary satellite layer.

## Real GIS functionality

Where the current API supports the necessary data:

- Display actual permitted junction geometry.
- Display actual permitted pipe LineStrings.
- Fit viewport to available geometry.
- Highlight selected elements.
- Distinguish zones and asset types.
- Provide useful accessible popovers/details.
- Filter asset records.
- Show asset metadata, material and length when present.
- Preserve units.
- Provide a corresponding accessible table.
- Allow reviewed engineer creation/editing workflows only when backed by implemented contract operations.

## Geometry constraints

Respect GeoJSON coordinate order.

Validate geometry through the actual server contract.

Do not invent coordinates for missing geometry.

Do not fabricate a complete water network.

Do not infer confirmed physical installation or survey accuracy merely from a digital record.

When the backend marks topology quality as unverified or review-required, show that clearly.

When tiles fail, preserve the authenticated asset overlay or a useful non-map table view.

## Map security

Never expose internal asset geometry to a citizen or unauthenticated visitor.

Never include internal geometry in public marketing screenshots unless explicitly approved as synthetic illustrative artwork.

Maps must not trigger external geocoding requests containing sensitive infrastructure coordinates.

## Licensing

Record attribution for each actual basemap/dataset source.

Keep license notices visible where required.

No API keys in public source unless explicitly designed to be public and approved.

---

# 13. INCIDENT MANAGEMENT — PAGE-31 AND PAGE-32

Create a professional incident center.

## Incident list

- Actual permitted incident records
- Clear status and priority distinctions
- Search/filter support matching API capabilities
- Server-backed pagination
- Stable loading and empty states
- Direct link to details
- Meaningful timestamps
- Appropriate authorization-sensitive actions

## Incident details

Use:

- Incident detail
- Real immutable timeline
- Linked evidence when supported
- Current state/version
- Authorized transitions
- Linked work context

Only show transition actions permitted by the current server state and current role.

The server must remain the final validator.

## State integrity

Do not allow arbitrary status changes through frontend-only logic.

Use real transition endpoints and the approved state machine.

Respect:

- Version preconditions
- `If-Match`
- Required reasons
- Idempotency keys
- Tenant scope
- Related record authorization

For a stale version, present a conflict/reload flow instead of overwriting data.

Show the difference between an incident requiring investigation and one actually verified.

---

# 14. WORK ORDERS AND FIELD TECHNICIAN UX — PAGE-33 AND PAGE-34

This should feel like professional utility field-service software.

## Supervisor experience

Show:

- Authorized work-order lists
- Current state and priority
- Assignment status
- Due dates if actually available
- Related incident
- Available actions
- Appropriate filters
- Conflict and stale-record handling

Implement real work-order creation and assignment workflows.

## Technician experience

Display only currently authorized assignments.

Prioritize mobile usability:

- Task identity
- Safe location/context
- Work instructions
- Current task status
- Allowed next action
- Work history
- Repair-record entry

Never give the technician a wider infrastructure view merely for convenience.

## Work-order transitions

Follow the backend's actual state machine.

Do not fake immediate success.

Preserve pending, completed and rejected mutation states.

## Reassignment

If the task is reassigned or access is revoked:

- Stop showing sensitive data.
- Invalidate cached task detail.
- Deny obsolete mutation attempts.
- Offer a safe explanation.
- Do not expose the new assignee's private identity unless authorized.

## Offline limitation

Full offline encrypted draft/sync capability belongs to later maintenance hardening.

Do not build an insecure pseudo-offline queue or store task records unencrypted in localStorage.

An explicit online-required state is preferable to a misleading offline feature.

---

# 15. REPAIRS AND INDEPENDENT VERIFICATION — PAGE-35

Preserve the distinction between:

1. Work performed
2. Repair recorded
3. Evidence reviewed
4. Repair outcome verified

The frontend must use real repair and verification endpoints.

The verification interface must:

- Show the submitted repair record.
- Show permitted evidence or its absence.
- Show current review state.
- Enforce available reviewer workflow.
- Display scientifically honest limitations.
- Handle permission denials.
- Handle concurrency/version conflicts.

## Current supported verification

M03 implements the genuine minimal verification workflow with `NOT_VERIFIABLE` where comparable evidence is missing.

Do not present `VERIFICATION_PASSED` or `VERIFICATION_FAILED` as available M04 outcomes unless the current backend legitimately supports them with qualified comparable evidence.

Do not create a success-looking green screen for a completed repair with no scientific verification.

The repair performer must not be allowed to approve their own repair through frontend role confusion.

---

# 16. SUPERVISOR COMPLAINT REVIEW — PAGE-36

Implement actual supervisor complaint review and linkage functionality.

The interface should support:

- Authorized complaint list
- Report details
- Reporter-safe and supervisor-private fields correctly separated
- Review action
- Reason where required
- Linked incident flow where supported
- Clear audit/status result
- Version and idempotency handling

Never expose private review reasoning to the citizen response projection.

Never automatically classify a complaint as a verified leak.

---

# 17. ADMINISTRATION — PAGE-44 AND PAGE-46

## Users and memberships

Build a professional tenant-scoped administration interface for actual implemented functions:

- Member directory
- Staff invitations
- Role changes
- Membership activation/suspension
- Clear authorization errors
- Recent reauthentication requirements
- Last-administrator safeguards

Role options must come from the legitimate contract.

No arbitrary evaluator self-grant.

No unreviewed super-admin features.

## Audit history

Use the real audit endpoint.

Show authorized safe records with:

- Action
- Timestamp
- Safe actor/resource identifiers where permitted
- Appropriate filters and pagination
- Accessible details

Do not display raw passwords, tokens, secret request bodies or personal data dumps.

## Settings

The planned M02 settings route contains capabilities not fully implemented by M03.

Do not create a fake settings-save operation.

Provide account/organization information where supported and restrict unsupported settings actions.

---

# 18. MONITORING, DEVICES, ACOUSTICS AND SIMULATION MODULES

M02 includes future routes for:

- Monitoring
- Device inventory
- Device details
- GUARD-5 diagnostic timelines
- Acoustic capture views
- Acoustic estimates
- Simulation runs
- Simulation evaluation
- Advanced analytics
- Reporting
- Notifications
- Feedback
- Maintenance expansion
- Full offline operation

Some or all of these require currently deferred backend operations.

## M04 rule

Do not activate unsupported modules as if they are functional.

You may create shared layout infrastructure or carefully reviewed informational content needed for future integration.

But do not create fake dashboard data to visually populate these areas.

Do not implement device ingestion, synthetic sensor streaming, scientific computation or live acoustic capture under M04.

Future simulation data must remain globally and visibly labeled as simulation.

Operational mode must not silently include synthetic records.

No ordinary frontend should receive restricted evaluation truth, generation seeds or privileged simulator credentials.

## Correct wording

For capabilities without genuine implemented integration, use concise status explanations such as:

- Hardware connection pending
- Monitoring data not available
- Simulation integration pending
- No authorized observations available
- Verification not possible with current evidence
- Feature not yet enabled

Do not mention any selection decision or imply physical connection already exists.

---

# 19. AUTHORIZED API INTEGRATION

Inspect `data/schemas/m03-implementation-matrix.json`.

Treat operations marked `CODE_TESTED` as the candidate set for M04 frontend integration, subject to actual runtime conformance.

The implemented groups include:

- Authentication
- Current user
- Public project status and utility lookup
- Organization reading
- Water zones
- Network junctions
- Pipe segments
- Evidence assessments
- Incidents
- Work orders
- Repairs
- Verification
- Citizen complaints
- Membership administration
- Audit logs

Do not hardcode guessed response fields.

Generate or construct typed client models from the actual implemented OpenAPI schemas.

Review:

- Required properties
- Optional properties
- Nullability
- Enumerations
- UUID representations
- Error responses
- ETags
- Cursor pagination
- Timestamp formats
- Retry policies
- Permission boundaries

## Client architecture

Create a maintainable and small API client layer.

It must provide:

- Typed requests and responses
- Safe URL construction
- Consistent credential forwarding
- CSRF handling
- Stable error normalization
- Session-expiration handling
- Cursor support
- ETag support
- Idempotency support
- Request cancellation
- Appropriate cache invalidation
- Request IDs where available

Never concatenate untrusted path strings without encoding/validation.

## Idempotency

Tenant business writes must use a UUID `Idempotency-Key` as specified.

Retain the same key only when retrying an identical operation and payload.

A new logically distinct action requires a new key.

Do not automatically replay stale destructive actions.

Auth/global mutations that reject this header must not receive it.

## ETag/If-Match

On versioned changes:

- Read the authoritative version/ETag.
- Send the proper precondition.
- Handle 412 or 428.
- Offer reload/compare/retry based on new authoritative state.
- Never silently overwrite concurrent changes.

## Pagination

Respect the actual list response:

`items`, `next_cursor`, `as_of`

Do not invent offset pagination.

Do not assume the first response includes all records.

## Error handling

Support at least:

- 400 malformed request
- 401 authentication required
- 403 forbidden
- 404 inaccessible/not found
- 409 conflict
- 412 stale precondition
- 422 validation error
- 428 missing precondition
- 429 rate limit
- 503 service unavailable
- Network failure
- Timeout/abort
- Unexpected response

Use the server's safe error code and request ID.

Never expose stack traces to users.

---

# 20. FRONTEND SECURITY

Security is a mandatory acceptance condition.

## Required controls

- Backend-owned sessions
- Server-authoritative authorization
- Correct CSRF
- Same-origin cookies
- No public client-side session secret storage
- No arbitrary redirects
- No untrusted backend URL forwarding
- No unauthorized cross-tenant cache sharing
- Correct protected-route behavior
- No protected content before auth resolution
- Safe rendering of user-generated text
- No unsafe HTML injection
- No secret leakage in logs/build artifacts
- No sensitive content in public metadata
- No accidental client access to private environment variables
- Proper logout cleanup
- Cache invalidation on role and organization change

## Frontend permission behavior

Hiding a button is usability, not security.

The server remains authoritative for every action.

A user must never gain permissions by editing local role strings, browser storage or route parameters.

## Content Security Policy

Introduce an appropriate compatible CSP after considering Next.js requirements, map worker behavior and any approved resources.

Avoid broad `unsafe-eval` or unrestricted third-party script access.

Document unavoidable development-only exceptions separately.

## Third-party content

Use local bundled assets where practical.

Do not include unreviewed trackers, analytics SDKs, chat widgets or external image CDNs.

Do not send contact details or internal topology to outside providers.

---

# 21. RESPONSIVE DESIGN

The website must be genuinely usable on:

- Small mobile screens
- Common Android screen sizes
- Tablets
- Laptop screens
- Full HD desktop
- High-density displays

Test at widths including:

- 360px
- 390px
- 640px
- 768px
- 1024px
- 1280px
- 1440px
- 1920px

Do not rely exclusively on CSS breakpoints; test content behavior.

At mobile sizes:

- Navigation must remain understandable.
- Forms must remain easy to complete.
- Tables must have accessible alternatives or controlled horizontal scrolling.
- Charts must remain readable or provide textual/table alternatives.
- Dialogs must fit the viewport.
- Buttons must not overlap.
- No unintended horizontal page overflow.
- Errors and confirmation messages must remain visible.

Avoid a bottom navigation with too many options.

Use an appropriate limited number of primary mobile destinations and a More menu where needed.

Preserve keyboard focus when navigation collapses.

---

# 22. ACCESSIBILITY

Target WCAG 2.2 AA.

Implement and test:

- Keyboard navigation
- Visible focus
- Skip-to-content
- Semantic landmarks
- Logical heading levels
- Accessible forms
- Programmatic labels
- Required-field identification
- Error summaries
- Focus management after form errors
- Accessible dialogs
- Screen-reader-readable status updates
- Reduced-motion preference
- Color contrast
- Text resizing
- Browser zoom
- Non-color status labels
- Touch usability
- Map/list alternatives

Use automated accessibility tools plus manual keyboard checks.

Do not claim WCAG certification based only on automated results.

Record which aspects were tested and which still require real-user assistive-technology evaluation.

---

# 23. UX STATES — MANDATORY FOR EACH ACTIVE FEATURE

Each active screen must handle:

1. Initial loading
2. Loaded with data
3. Loaded with zero records
4. API validation failure
5. Unauthenticated session
6. Unauthorized access
7. Expired/revoked session
8. Server unavailable
9. Network interrupted
10. Mutation in progress
11. Mutation succeeded with actual server receipt
12. Mutation rejected
13. Stale data or version conflict
14. Rate-limited request
15. Small-screen layout

Not every state requires its own large component, but the app must behave correctly.

Do not use random numbers, skeletons that never finish, or success toasts disconnected from server acknowledgement.

Do not disable controls without explanation when the action is important.

Use understandable copy that tells the person what happened and what can be done next.

---

# 24. CONTENT, TONE AND MICROCOPY

The product voice should be:

- Professional
- Clear
- Human
- Technically accurate
- Calm
- Concise
- Helpful

Avoid:

- Vague AI-marketing language
- Repeated "revolutionizing the future" claims
- Long unbroken paragraphs in dashboards
- Unexplained engineering jargon in public pages
- Decorative pseudo-technical phrases
- Overuse of exclamation marks
- Overclaiming innovation or validation

Use plain-language explanations alongside technical information when useful.

Examples of good system language:

**No incident records available**

"No incidents match the current filters."

**Access changed**

"Your access to this organization has changed. Reload to see your current workspace."

**Verification unavailable**

"Comparable evidence is not available for this repair. The result cannot be verified."

**Hardware status**

"Hardware connection pending."

**Source status**

"Simulation data — not a field measurement."

Proofread every visible label and tooltip.

English is the initial implemented language.

Structure copy for later Telugu/Hindi localization without claiming completed translations.

---

# 25. PERFORMANCE

The frontend should feel fast on a normal student laptop and mid-range Android phone.

Optimize for:

- Efficient component rendering
- Small client-side bundles
- Server rendering where appropriate
- Route-level code splitting
- Lazy loading expensive maps/charts
- Stable list rendering
- Proper request cancellation
- Avoiding unnecessary duplicate fetches
- Limited unnecessary animation
- Minimal third-party JavaScript
- Font stability
- Proper loading states

Use measured performance rather than invented scores.

Evaluate Core Web Vitals where practical.

Target good LCP, CLS and interaction responsiveness under documented development conditions, but report actual measurements instead of declaring perfect performance.

Do not sacrifice security or truthful state handling to increase a synthetic benchmark score.

---

# 26. LOCAL DEVELOPMENT AND DEPLOYMENT INTEGRATION

The frontend must run alongside the existing real M03 backend.

Preferred architecture:

Browser
→ local HTTPS same-origin proxy
→ Next.js frontend or FastAPI `/api/v1`
→ private PostgreSQL/PostGIS

Inspect the current Compose and Caddy configuration.

Preserve M03's existing backend reproduction and CI behavior.

Add frontend integration as a documented, opt-in development configuration or carefully reviewed extension.

Do not break backend-only acceptance.

Do not expose PostgreSQL publicly.

Do not silently weaken TLS or cookie policy.

Document:

- Required Node version
- Package installation command
- Development startup commands
- Backend startup
- Local HTTPS certificate procedure
- Frontend URL
- Required environment variables
- Private operator/bootstrap setup
- Database scope
- Test setup
- Shutdown procedure
- Troubleshooting

## Database safety

Use existing authorized disposable development databases.

Do not reset the owner's personal or shared database.

Never run destructive acceptance against a database whose identity has not been explicitly confirmed.

Do not commit operator configurations, passwords, certificates, private mail, database dumps or secrets.

M04 should not require new migrations.

If a genuine missing backend capability blocks an M04 feature, document and defer it rather than silently rewriting M03.

---

# 27. TESTING STRATEGY

Do not call M04 complete after a successful build alone.

## Unit tests

Test:

- Data formatters
- Unit formatting
- Timezone rendering
- Status label mapping
- Route authorization/navigation rules
- Idempotency-key lifecycle
- API error normalization
- Pagination logic
- Search/filter serialization
- Validation behavior
- Cache isolation
- GeoJSON handling where enabled

## Component tests

Test:

- Login form
- Citizen report form
- Organization switcher
- Permission-denied state
- Incident table
- Work-order action panel
- Version-conflict handling
- Verification outcome display
- Responsive navigation
- Empty/loading/error components

## Real integration

Use the real M03 backend and isolated PostgreSQL/PostGIS.

Do not use mock handlers as the only acceptance proof.

Construct test identities through the approved private bootstrap/fixture procedure.

Use synthetic operational records clearly labeled as fixtures.

Test cross-role workflow:

1. Bootstrap organization and appropriate accounts.
2. Authenticate actual users.
3. Select current authorized membership.
4. Citizen submits a complaint.
5. Supervisor reads/reviews it.
6. Supervisor creates or links an incident.
7. Supervisor creates and assigns a work order.
8. Technician sees only the assigned task.
9. Technician performs authorized actions and submits repair.
10. Independent authorized reviewer submits NOT_VERIFIABLE with reason where applicable.
11. Citizen reads the permitted safe update.
12. Unauthorized users cannot access another tenant's or another citizen's data.

Verify real persistence and audit history.

## Security negative tests

Test:

- Cross-tenant URLs
- Arbitrary organization changes
- Citizen access to internal records
- Technician access to unassigned tasks
- Role removal while a screen is open
- Session revocation
- Missing CSRF
- Invalid Origin
- Missing Idempotency-Key
- Stale ETag
- Idempotent same-payload retry
- Conflicting retry payload
- Invalid required fields
- Rate-limited actions
- Unauthorized administration
- Browser back-navigation after logout
- Cache contamination between organizations

## Browser tests

Use Playwright in an actual browser.

Cover at least:

- Chromium
- Mobile viewport
- Keyboard navigation
- Real API-backed workflow
- Critical form error states
- Navigation changes on role
- Session expiry
- Responsive layout
- Map fallback
- Route not found
- Deferred-feature behavior

If another browser engine is installed and supported, test it as well and record the environment.

## Visual regression and screenshots

Create reviewable screenshots for:

- Public homepage
- How It Works
- Login
- Citizen report
- Citizen reports list
- Utility overview
- Network explorer
- Incident list/detail
- Work orders
- Technician task detail
- Repair verification
- Admin users
- Mobile navigation

Use synthetic non-sensitive records only.

Capture at desktop and mobile sizes.

Review:

- Alignment
- Typography
- Color hierarchy
- Contrast
- Wrapping
- Overflow
- Broken icons
- Blank areas
- Dialog positioning
- Button states
- Visual consistency

Do not merely produce screenshots—inspect them and correct defects.

---

# 28. QUALITY AND SECURITY GATES

Before requesting M04 approval, run the applicable commands and record actual results.

At minimum:

- Reproducible frontend installation
- TypeScript typecheck
- Lint
- Formatting check
- Production build
- Unit tests
- Component tests
- Playwright tests
- Accessibility checks
- Relevant frontend/backend integration tests
- Real role-authorization deny tests
- Repository integrity checker
- M02 design checker
- Git whitespace/diff checker
- Current main CI regression checks

Add an M04 frontend GitHub Actions job or appropriately isolated frontend workflow.

It must not weaken, remove or silence previously existing jobs.

If installation or testing is blocked by an unavailable environment, report the exact blocker.

Do not claim tests passed if they were not executed.

Do not replace tests with written assurances.

---

# 29. IMPLEMENTATION PHASES

Work incrementally.

Maintain one reviewed feature branch.

## Phase A — Baseline and architecture

- Verify Git state.
- Read canonical specifications.
- Inventory current APIs.
- Build the route capability matrix.
- Select maintained dependencies.
- Write a focused implementation plan.
- Establish exact acceptance criteria.
- Record unresolved issues.

Checkpoint A: architecture and scope ready.

## Phase B — Frontend foundation

- Initialize `apps/web`.
- Establish strict TypeScript.
- Install reviewed compatible dependencies.
- Configure Tailwind and design tokens.
- Build public/app layouts.
- Implement responsive navigation.
- Implement the shared component primitives.
- Establish typography, iconography and accessibility foundations.
- Set up lint, typecheck, test and build scripts.

Checkpoint B: visually coherent, reproducible application skeleton.

## Phase C — Public website

Implement high-quality public pages based on approved M02 content.

Include architecture diagrams, truthful status and well-designed mobile layouts.

Do not use fake performance figures.

Checkpoint C: reviewed public information experience.

## Phase D — Authentication and tenancy

Implement real login, registration, recovery, verification, session management, organization selection and guarded navigation.

Use the actual M03 backend.

Checkpoint D: real authenticated workflows and positive/negative browser tests.

## Phase E — Citizen experience

Implement actual complaint creation, listings, safe detail views and follow-ups.

Checkpoint E: citizen flow proven against the real database.

## Phase F — Engineer and supervisor experience

Implement useful permitted organization overview, zone/asset network explorer, incident and complaint workflows.

Use actual pipe geometry for the map when supported.

Checkpoint F: real records and correctly authorized navigation.

## Phase G — Technician and verification experience

Implement work orders, assignments, technician actions, repairs and independent verification.

Checkpoint G: complete real complaint-to-NOT_VERIFIABLE workflow through the frontend.

## Phase H — Administration

Implement real membership governance and safe audit history.

Checkpoint H: successful authorized administration with negative tests.

## Phase I — Quality and visual refinement

Perform comprehensive:

- Browser inspection
- Mobile inspection
- Visual consistency review
- Accessibility testing
- Performance review
- Security review
- Error/empty/loading-state review
- Cross-tenant isolation tests
- Regression checks

Fix real defects discovered.

Checkpoint I: reviewed and measured M04 acceptance.

## Phase J — Publication

- Review final diff.
- Run all available checks.
- Update accurate documentation.
- Commit implementation.
- Push feature branch.
- Open PR targeting main.
- Link issue #4.
- Report tested and deferred scope.
- Wait for owner review.

Do not autonomously merge or close the issue.

---

# 30. CODE STRUCTURE

Prefer a clear feature-oriented structure under `apps/web`.

A reasonable starting design:

```text
apps/web/
  app/
    (public)/
    (auth)/
    (citizen)/
    (operations)/
    (administration)/
  components/
    ui/
    layout/
    navigation/
    feedback/
    data/
    maps/
  features/
    auth/
    account/
    organizations/
    complaints/
    assets/
    incidents/
    work-orders/
    repairs/
    administration/
  lib/
    api/
    security/
    contracts/
    validation/
    formatting/
  styles/
  tests/
    unit/
    component/
    e2e/
  public/
```

This is a suggested conceptual structure, not a mandate to create unused directories.

Next.js route groups must preserve actual M02 URLs.

Avoid:

- Giant page files
- One enormous service/client class
- Circular dependencies
- Magic role strings throughout components
- Duplicated form validation
- Duplicated API error handling
- Duplicated styling
- A generic page generator that erases the distinctions between user workflows

Prefer readable code and appropriately sized modules.

Record architectural decisions only when necessary.

---

# 31. REQUIRED DELIVERABLES

At the end of M04, provide:

## A. Functional frontend

A reproducible Next.js application under the existing repository.

## B. Design system implementation

Actual reusable tokens/components aligned with M02.

## C. Route capability matrix

Every M02 route classified with its actual M04 status, including intentional deferrals.

## D. API integration documentation

Implemented operation IDs, page consumers, authentication details and error/retry contracts.

## E. Role-specific workflows

Actually working citizens, supervisors, technicians, engineers and administrators, to the extent supported by M03.

## F. Map capability

Authorized existing asset visualization with a free/licensed or provider-independent rendering path, and an accessible non-map alternative.

## G. Test suite

Unit, component, browser, security and integration checks.

## H. Visual evidence

Desktop/mobile review screenshots with non-sensitive test data.

## I. Engineering report

Create a document such as:

`docs/engineering/M04_FRONTEND_IMPLEMENTATION_REPORT.md`

Include:

- Implemented features
- Page routes
- Design decisions
- Dependencies and licenses
- Frontend/backend integration
- Permissions
- Test results
- Accessibility findings
- Performance findings
- Map data/attribution decision
- Deferred features
- Known limitations
- Reproduction instructions
- Final commit and PR reference

## J. Acceptance ledger

Create an executed acceptance report under `docs/testing/` covering real commands, actual results, environment and limitations.

## K. Pull request

Open the complete M04 PR against main.

Include summary, changed components, tests, screenshots/artifacts, known limitations, reviewers' attention items and reference to issue #4.

---

# 32. M04 ACCEPTANCE CRITERIA

M04 is acceptable only when the following statements are supported by real evidence.

### Functionality

- Public information pages are coherent and genuinely usable.
- Real authentication works.
- Current account/session workflows work.
- Organization switching works.
- Permitted citizen complaint flows work.
- Permitted incident workflows work.
- Permitted work-order and technician workflows work.
- Real repair-verification workflows behave correctly.
- Actual implemented asset data can be inspected.
- Basic administration and audit interfaces work within existing permissions.
- Unsupported actions do not pretend to succeed.

### Interface

- Professional visual design across core screens.
- Clear consistent typography and spacing.
- No fabricated operational metrics.
- No meaningless charts or placeholder maps.
- Responsive desktop/tablet/mobile layouts.
- Good loading/error/empty states.
- Clear role-specific navigation.
- Accessible core interactions.

### Security

- FastAPI retains authentication authority.
- No token leakage.
- Real CSRF integration.
- No cross-tenant information leakage.
- No unauthorized technician data.
- No citizen access to internal topology.
- Correct logout and revocation behavior.
- No privilege escalation through navigation.
- No insecure caching of private content.

### Engineering quality

- Reproducible install/build.
- Typecheck passes.
- Relevant lint/test suites pass.
- Real backend integration is demonstrated.
- Browser tests are executed.
- CI is green on the reviewed branch.
- No regression to M03/M05/M08.
- Documentation matches actual code.
- No invented evidence.
- No unauthorized costs.

### Publication

- Feature branch pushed.
- PR opened for owner review.
- Issue #4 remains open until approved.
- Main is not automatically modified by merger.
- Later milestones have not been silently implemented.

---

# 33. IMPORTANT LIMITS AND NON-GOALS

Do not:

1. Redesign the frozen sensing architecture.
2. Restart M03.
3. Change scientific simulation results.
4. Claim physical verification.
5. Build a fake full monitoring application.
6. Replace backend authentication.
7. Add unauthorized paid services.
8. Claim universal free basemap availability.
9. Expose private pipeline data publicly.
10. Add untested backend routes to satisfy the interface.
11. Introduce proprietary stock illustrations or fonts without licenses.
12. Create meaningless KPI cards.
13. Present simulated data as field data.
14. Declare M06/M07/M09 complete.
15. Produce the explanation video.
16. Merge M04 automatically.
17. Close issue #4 automatically.
18. Commit secrets or private development evidence.
19. Weaken passing repository checks.
20. Conclude M04 is complete merely because a Next.js development server starts.

A visually sophisticated frontend is not a substitute for correct domain behavior.

A technically functional frontend is not an excuse for an unfinished or confusing user experience.

Both engineering correctness and design craftsmanship are required.

---

# 34. FINAL VISUAL AUDIT — MANDATORY

Before opening the M04 pull request, evaluate the application as an experienced human product designer would.

Ask:

- Can a first-time visitor understand HYDROOVERITY within 30 seconds?
- Does the homepage communicate the actual problem and approach?
- Is the branding distinctive without being flashy?
- Are headings and typography coherent?
- Do dashboards clearly indicate what requires action?
- Can a citizen complete a report without technical training?
- Can a field technician identify the next permitted task quickly?
- Can a supervisor distinguish a complaint from a confirmed incident?
- Can an engineer distinguish observed evidence from unresolved interpretation?
- Does the network map show genuine permitted data?
- Does the interface make missing observations obvious?
- Are state labels accurate and consistent?
- Does every active control have a genuine outcome?
- Are forms simple and errors understandable?
- Do all core screens work on mobile?
- Is every visible figure sourced?
- Does the design avoid recognizable AI-template clichés?
- Does the site look cohesive when screens are viewed together?
- Are the most important features easiest to find?
- Would a professional software reviewer trust this implementation and its evidence?

Use screenshots and browser inspection to answer these questions.

Correct weaknesses rather than writing an optimistic self-review.

---

# 35. CODING AND EXECUTION INSTRUCTIONS

You are authorized to carry M04 implementation forward within these defined boundaries.

Do not stop after writing a plan, creating folders, installing dependencies or building one homepage.

Proceed through the implementation checkpoints while the environment and authorization permit.

If the full milestone cannot be completed in one run, leave durable committed checkpoints and provide exact continuation instructions. Never label partial work as completed M04.

For any blocking ambiguity:

1. Inspect the canonical contract.
2. Inspect implemented code and tests.
3. Resolve the matter using the smallest consistent interpretation if it does not change substantive requirements.
4. Document the decision.
5. If it would change security, scope, spending or authoritative semantics, request owner approval.
6. Do not silently invent behavior.

Keep output manageable and factual.

At meaningful checkpoints, report:

- Phase
- Implemented files/features
- Tests executed
- Failures found
- Fixes applied
- Remaining work
- Commit references

Do not waste time on excessive narration instead of implementation.

---

# 36. FINAL RESPONSE FORMAT

When finished, return a structured engineering handoff containing:

**A. Executive Summary**

What M04 implemented and what it did not.

**B. Git Status**

Branch, base commit, current head and PR URL.

**C. Implemented Route Matrix**

Active functional, read-only, informational and deferred routes.

**D. UI/UX Delivery**

Design system, screenshots, mobile behavior and accessibility evidence.

**E. Backend Integration**

Implemented M03 operations consumed, security/session/retry behavior.

**F. GIS/Maps**

Map renderer, map-data source, attribution, cost conditions and fallback.

**G. Security**

Authentication, CSRF, role and tenant checks, negative cases.

**H. Testing**

Actual commands, counts, browser coverage, green/failing results and environment.

**I. CI**

Workflow link, jobs and artifact references.

**J. Known Limitations**

Unimplemented capabilities, blocked items and remaining engineering risks.

**K. Owner Review**

Exact decisions/actions required before merging.

Do not provide a final "everything perfect" statement unsupported by evidence.

---

# 37. START IMPLEMENTATION

Begin with repository inspection and the M04 route/API capability audit.

Confirm that issue #4 remains open and the current main branch is the expected approved baseline or a newer verified successor.

Create the isolated M04 branch.

Then implement the professional HYDROOVERITY frontend through the controlled phases.

Preserve all authoritative project decisions.

**Design for people. Implement against real contracts. Test real workflows. Preserve scientific honesty.**

**Final objective: a polished, credible, fully functional M04 frontend within its actual authorized scope, ready for owner engineering and visual review—not an imitation of a completed water-monitoring deployment.**
