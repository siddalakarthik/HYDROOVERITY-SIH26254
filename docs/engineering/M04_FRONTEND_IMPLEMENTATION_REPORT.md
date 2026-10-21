# M04 frontend implementation record

Issue #4; branch `feature/m04-frontend-foundation`; approved base `e0122f5ee4146e49ae6113a1aa6a5ee444b25973`.

## Authorization and implementation plan

The owner's comprehensive M04 request and subsequent visual approval authorize a real local Next.js application, not a prototype-only substitution. Option 3 is the public visual direction; the structured resident/staff separation in Option 2 informs authenticated workspaces. M02 tokens, canonical routes, permissions and the implemented M03 contracts remain authoritative. Mockup copy is not an engineering source. HYDRO-WATCH is hydraulic context; only GUARD-5 owns the five wetness channels.

1. Preserve other worktrees and create the exact isolated M04 branch from fetched main. All three baseline jobs passed in run 39588590017; issue #3 is closed and #4 open.
2. Generate the browser contracts from the reachable implemented M03 OpenAPI subset: 58 operations, with 59 deferred canonical operations excluded.
3. Build shared public/application shells, typed API transport, forms and accessible states before enabling workflows.
4. Implement authentication and account/session management, citizen reports, assets/network, incident/work-order/repair workflows, administration and audit in reviewable checkpoints.
5. Use M02 colors, system fonts, spacing, touch targets and one responsive design system. Preserve source/freshness and uncertainty labels.
6. Classify all 46 routes in a capability matrix; future endpoints do not become active navigation or fabricated success.
7. Keep FastAPI the sole identity authority. Browser requests use same-origin HTTPS, HttpOnly cookies and CSRF. Tenant writes use idempotency and version preconditions; errors never silently replay a stale mutation.
8. Use MapLibre with authorized WGS84 geometry, a blank local style and accessible lists. No mandatory tile service, external geocoder or citizen topology access.
9. Execute strict typing, lint, format, build, unit/component tests, real backend/browser workflows, denial cases, mobile/axe and source-vs-render visual review. Add an isolated CI job without weakening M02/M03/M05/M08 jobs.
10. Commit checkpoints, push and open a PR for review. No merge, issue closure, public deployment, purchases or other milestones.

## Dependency decisions before installation

Use exact Next.js 16 / React 19 stable packages, strict TypeScript 5.9 (compatible with the OpenAPI generator's declared peer), Tailwind 4 and native platform APIs. Lucide supplies UI icons; MapLibre is loaded only for authorized infrastructure views. Avoid a second auth system, persistent browser credentials, generic API caches and unnecessary animation/state libraries. Test-only dependencies include Vitest, Testing Library, Playwright and axe. Exact installed versions/licenses, audit results and execution evidence will be recorded after resolution. No claim of vulnerability-free software follows from package selection.

## Delivery status

IN PROGRESS. This file is a durable implementation record, not acceptance evidence. No M04 browser, accessibility, performance or CI pass is claimed until execution is recorded. Hardware remains physically untested; M05 results and M08 digital-only caveats are unchanged.
