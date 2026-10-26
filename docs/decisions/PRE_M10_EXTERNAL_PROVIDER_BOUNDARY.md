# Pre-M10 disabled provider boundary

Owner authorization: master pre-M10 R05 permits a safely disabled external
interface with local fake-provider fault injection. D8 remains authoritative.
There is no real adapter, destination lookup, HTTP client, plugin import,
environment opt-in, endpoint or database migration in this increment. Resolving
any external provider always fails with EXTERNAL_DELIVERY_DISABLED.

The interface accepts opaque UUID references for tenant, member, notification,
destination verification and consent; these references are not authorization.
A future adapter must reauthorize all of them against current records before
any send. No adapter is implemented here. Safe message text comes only from the
existing fixed notification templates; arbitrary address/message input is absent.

The deterministic retry planner accepts only an explicitly labelled synthetic
policy with two configured delays and a separate decision about unknown outcomes.
There are three total attempts including the first. No delay default or automatic
external retry is introduced. Check the attempt budget before a provider call.
The planner does not replace the actual in-app worker, queue, leases or history.

Provider acknowledgement is neither delivery nor reading. A timeout after a
possible provider effect remains UNKNOWN_REVIEW unless an explicit synthetic
retry policy permits a retry; such retry can duplicate the effect even with a
stable operation key. Prior uncertainty survives a later rejection or exhausted
budget. Fake tests demonstrate this duplicate risk rather than claim exactly-once
delivery. The helper can never set real notifications to DELIVERED or READ.

The local fake has no network code. Tests cover missing policies, bounded attempts,
explicit delays, terminal replies, lost response after a possible side effect,
unknown-outcome retries, malformed policy/time/count values, safe input shape and
all provider names being disabled. These are executable interface/planner tests,
not an external provider integration or measured notification SLA.

R05 remains BLOCKED under its original acceptance criterion. Real providers,
verified destinations, consent/custody, approved delays, current authorization,
durable external-send intents/reconciliation and operating approval remain open.
The existing in-app worker and its PostgreSQL/process-restart tests are unchanged.
No API/table/scientific/physical claim changes are made.

Executed locally: 34 pure local fake-provider cases passed in 0.17 s; Ruff and repository/whitespace checks passed. Pytest reported one nonessential cache-write permission warning; no acceptance was skipped. This evidence does not establish durable external-job recovery or actual provider delivery. Mandatory combined CI remains required on the integrated branch.
