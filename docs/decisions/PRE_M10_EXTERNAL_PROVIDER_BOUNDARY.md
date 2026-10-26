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

Integrated with green main `6c211066b75f21e4bc65a273a2aac4472530bb51` only after four post-merge jobs passed in run 40282063124. The new test file is collected by the existing backend CI (84 prior + 34 new = 118 tests); original historical test evidence stays unchanged. No existing source, API, schema, media asset or historical hash is amended by this slice. The completion register preserves R05 BLOCKED. Native Chrome zoom was separately attempted with the Computer Use skill, but app approval timed out; U01 remains unverified for native zoom.

The integrated real-PostgreSQL backend suite passed all 118 cases locally (4755.41 s, unusually slow wall-clock environment). No failure or skip was suppressed. Targeted pure tests completed in 0.17 s; the earlier cache-write warning was avoided for the full run with the nonessential pytest cache plugin disabled. Final CI timing is a separate measurement, not a claimed production SLA.

PR run 40293057929 passed both 118-case backend executions (82.30 s / 84.13 s), all focused PostgreSQL suites and the other three jobs, but strict traceability rejected pytest's empty `[]` ID for the empty provider name. Explicit descriptive IDs retain that exact negative case and every assertion. All 34 cases passed again (0.14 s), and all 34 actually collected IDs passed the unchanged traceability reference validator. No checker, runtime control or test assertion was relaxed. Final four-job CI must pass on the corrected head.
