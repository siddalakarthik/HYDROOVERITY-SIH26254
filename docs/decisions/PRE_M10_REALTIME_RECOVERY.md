# Pre-M10 R02 bounded event recovery

Owner authorization: master pre-M10 R02. The existing M02 SSE/history contracts,
per-event current authorization and explicit reset/snapshot recovery remain the
target. No waveform, hidden truth, raw observation, contact or arbitrary summary
payload enters this stream. Events indicate authorized record changes, not live
physical sensing or scientific verification.

Durable opaque random cursors bind organization, user membership, current session,
workspace filter and permission fingerprint. Store only token hashes. A dedicated
cursor table avoids exposing the global outbox sequence in a readable token and
survives API restart without putting secrets in browser storage. Same-position
cursor reuse and bounded per-session admission prevent unlimited cursor creation.
Seven-day replay eligibility follows M02; no real data-erasure policy is approved.

Acquire the existing organization mutation advisory lock when selecting the
snapshot watermark. All supported business event producers use that same lock;
this closes the assigned-sequence/uncommitted-transaction race. Release it before
network delivery. No missing/expired/changed-permission cursor silently resumes:
return reset-required plus a new watermark and require authoritative refetch.

Each poll reauthenticates session and active membership, repeats role permissions,
and projects only allowlisted resources with current owner/assignment/parent ACL.
Never trust historical recipient, event permission or stored summary as present
authorization. Unknown topics are skipped and the cursor still advances. History
scans at most 100 outbox rows per call and bounds rendered payload at 256 KiB.

The SSE generator holds no database transaction while yielding. Backpressure is
demand-driven with no unbounded application queue. Recheck authorization before
each batch; heartbeat at most 15 seconds while connected. A bounded connection
lifetime requires reconnect and current authorization. Overflow or replay expiry
emits reset-required; never advertise a false current-state badge. The frontend
must treat connection state as record-update connectivity, not physical freshness.

Implementation: two existing M02 deferred GET operations are now executable;
the entire previous 112-operation OpenAPI remains unchanged. Runtime inventory
is 114 registered operations (113 active plus default-disabled contact), 54 tables
and additive migration `pre_m10_003`. `pre-m10-realtime-revisions.json` records
an explicit source amendment from verified main `3b14b40024d424a173c60f12462ee8b1603d3221`;
historical manifests and frozen scientific sources are unchanged.

Lock order is authentication/session, organization mutation lock, then current
membership/roles. Every individual event is checked again before emission.
Internal service history is supervisor-only; resident timelines use public
updates. Technician signals require the current assignment and version.
Confirmed/rescheduled bookings now emit empty safe appointment/work change
signals in the existing transaction, without creating extra notifications.

Bounds: 20 simultaneous streams per API process, 100 scanned rows per batch,
256 KiB payload, 1,000 active cursors per visible session/organization context
(oldest 100 revoked on admission pressure), 5-second transport write deadline,
15-second heartbeat, 2-second poll and 30-second connection lifetime. Generator
and response cleanup release capacity even before the first header is sent.
No transaction spans network delivery. The seven-day TTL is replay eligibility,
not approved legal retention: expired/revoked rows are retained. Populated
migration downgrade refuses to erase cursor data; empty downgrade remains usable.

Both private development proxies forward Last-Event-ID and flush bounded SSE
chunks. The website keeps cursors only in memory, uses one scoped subscription,
bounded deduplication, refetch bursts coalesced to at most once per five seconds, a 35-second idle watchdog, jittered
1–30-second reconnect and 30-second fallback refresh. Network loss is shown
immediately. Transient refresh failures preserve drafts with an explicit stale
record notice; authorization failure and organization/mode changes purge scoped
records. No offline storage or synchronization is introduced.

Executed local evidence: 19 real PostgreSQL acceptance cases cover snapshot-lock
races, replay/expiry, restart/key rotation, current ownership and reassignment,
session/role revocation, deactivated-user SQL RLS, foreign cursor denial,
transport backpressure/early disconnect, real loopback TCP SSE reconnect and
non-destructive downgrade refusal. The existing backend suite passed 118 tests.
Frontend passed 30 unit tests, typecheck, lint and production build. The real
HTTPS browser scenario recovered an actual authorized complaint created during
disconnection, preserved category/text/location/privacy values, submitted the
service request, and passed 320px overflow/axe checks. Browser TLS uses the
reviewed synthetic test certificate pin; this is not normal-browser OS trust.
Sanitized screenshots and exact-source summaries are uploaded by final CI.

Limitations: bounded synthetic integration evidence, not a production capacity
or delivery SLA; process-local admission is not a multi-instance global quota.
No physical sensing freshness, field validation, external delivery or legal
retention policy is established. Public deployment and D1–D10 gates remain.
The final PR records exact head, mandatory four-job CI and artifact verification.

The first PR CI run passed backend/repository/CAD but exposed request amplification
in the existing complete M04 workflow: background invalidations reached the
unchanged 120-request limit, and membership checks treated HTTP429 as permanent
access loss. The real local workflow reproduced the same verification-form
failure; a temporary bounded diagnostic confirmed RATE_LIMITED. Refresh bursts
are now bounded to one per five seconds. Membership rechecks serialize, honor
Retry-After, recover automatically, and qualify previously loaded access during
transient failure. Actual denial or changed membership still clears private
state. Four regressions cover initial429 recovery, transient/current-denial
behavior burst coalescing and resource-family filtering. Safe event types now identify only the already-authorized record family, so unrelated mounted resources and organization metadata are not refetched for every event. No server throttle or browser timeout changed;
the temporary diagnostic was removed and the original workflow test preserved.

The initial snapshot now waits for the committed stream watermark before its
resource reads begin. This removes speculative reads followed by an immediate
duplicate reset refetch, while preserving the race guarantee. If stream capacity
is unavailable, a bounded authorized history request establishes the same barrier
and ordinary snapshots remain usable with disconnected status. Later reset frames
still require refetch. Regression tests verify request ordering, no duplicate
initial snapshot and the unavailable-stream fallback. No request limit is raised.

Admission for the two new background endpoints is separately limited to 30
initial subscription/history requests per authenticated session per minute,
shared across utilities and modes. The unchanged existing business/auth APIs
retain their 120-request general limit. Internal per-event authorization checks
are not counted as fabricated HTTP requests. A real PostgreSQL regression proves
an exhausted old general budget still denies /me, admits only the independently
bounded new protocol, and denies its 31st request with Retry-After. Global stream
capacity remains 20. This prevents background subscriptions from starving human
work commands without weakening any pre-existing endpoint's limit.

After the corrected admission and snapshot ordering, both unchanged original M04
browser scenarios passed locally: the complete resident-to-independent-review
workflow (40.2s) and account/GIS/offline-denial/map-alternative workflow (1.3m).
These are synthetic local observations, not performance commitments. An interrupted
local PostgreSQL process was restarted from its existing data with normal WAL
recovery; no cluster or database was reset to hide a failure.
