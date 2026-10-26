# Pre-M10 completion register

Authoritative current register: [machine-readable details](pre-m10-completion.json). Revision 1 starts from green main `d772045ba6d44ddd1bbee1e4baf890c5786628d5`. Historical [M09 evidence](M09_FULL_SYSTEM_ACCEPTANCE.md) and [40-case traceability](m09-traceability.json) are unchanged.

All four [post-merge CI jobs](https://github.com/siddalakarthik/HYDROOVERITY-SIH26254/actions/runs/40181138969) passed. This is the starting baseline, not a claim that pre-M10 completion work has passed.

Runtime: **111 implemented operations, 51 migrated tables, `pre_m10_001`**. Historical M09: **21 PASS / 13 BLOCKED / 6 NOT IMPLEMENTED**. Current original-40 status after F01: **22 PASS / 12 BLOCKED / 6 NOT IMPLEMENTED**. Revision 2 records green main `008bd507c09352dcbb8098ec9812448693e0d99b` and [four passing post-merge jobs](https://github.com/siddalakarthik/HYDROOVERITY-SIH26254/actions/runs/40261562317). Eight additional M09 risks retain their scoped PASS results.

Issues #6 (synthetic integration) and #9 (scoped acceptance) were closed with evidence after post-merge verification. #7 and #10 remain open. The repository is public; application deployment remains private-development only.

## Original acceptance and M09 risks

Each ID below has historical/current status, root cause, implementation, test, gate, risk, source files, completion commit/PR, evidence and limitations in the companion JSON. PASS rows inherit M09 evidence only; no new tests or physical validation are implied.

| ID | Requirement | Historical | Current | Remaining limitation |
| --- | --- | --- | --- | --- |
| F01 | Citizen creates report | BLOCKED | PASS | Real opt-in receipt, replay/ownership tests and browser inbox workflow; PR25 and post-merge CI green |
| F02 | Citizen ownership | PASS | PASS | Media absent; boundary denial is not secure-media functionality |
| F03 | Triage | PASS | PASS | Synthetic operator decisions, no actual utility triage |
| F04 | Assignment | BLOCKED | BLOCKED | Offline synchronization remains deferred D9 |
| F05 | Worker repair | BLOCKED | BLOCKED | D7 photo processing/storage not implemented |
| F06 | Verification | BLOCKED | BLOCKED | Operational comparable before/after acquisition and positive field verification are not implemented |
| F07 | Reopen | BLOCKED | BLOCKED | Current-cycle guard fix tested; comparable measured verification and final integrated review remain open |
| S01 | No authentication | PASS | PASS | Private loopback only |
| S02 | Tenant isolation | PASS | PASS | No third-party penetration testing |
| S03 | CSRF/session | PASS | PASS | Single-process in-memory rate limiter; public release blocked |
| S04 | Role/resource checks | PASS | PASS | No broader production identity certification |
| S05 | Uploads | NOT IMPLEMENTED | NOT IMPLEMENTED | D7 scanner, licensing, processing and storage review required |
| S06 | Audit | PASS | PASS | Audit retention/operations policy requires review |
| P01 | Truth exclusion | BLOCKED | BLOCKED | Sealed evaluator/artifact access system deferred |
| P02 | Origin integrity | PASS | PASS | No live sensor adapter |
| P03 | Lab versus field | NOT IMPLEMENTED | NOT IMPLEMENTED | Physical adapters and evidence not implemented |
| P04 | Acoustic abstention | PASS | PASS | Modeled common clock; no passive audibility/field location proof |
| P05 | Guard wetness | PASS | PASS | Physical collector and electrical supervision unverified |
| P06 | Staleness | BLOCKED | BLOCKED | Live late/out-of-order ingestion/freshness pipeline deferred |
| R01 | Idempotency | PASS | PASS | Short bounded races, not long-duration load |
| R02 | Realtime recovery | BLOCKED | BLOCKED | Live snapshot/subscription race, durable event cursor expiry and backpressure not implemented |
| R03 | Offline vault | NOT IMPLEMENTED | NOT IMPLEMENTED | D9 encrypted offline vault deferred |
| R04 | Offline conflict | NOT IMPLEMENTED | NOT IMPLEMENTED | No offline reconciliation engine |
| R05 | Jobs and delivery | BLOCKED | BLOCKED | External providers and provider timeout handling deferred D8 |
| U01 | Responsive UI | BLOCKED | BLOCKED | 640/320 reflow approximates 200/400% of1280px; native browser zoom not executed |
| U02 | Accessible forms | BLOCKED | BLOCKED | Full screen reader/manual assistive technology certification not performed |
| U03 | Mode/freshness | PASS | PASS | No field savings or sensor-performance claim |
| U04 | States | PASS | PASS | Bounded local/CI browser runs |
| A01 | Registration retries | PASS | PASS | Private auth mail adapter only |
| A02 | Login lost response and logout | PASS | PASS | No public deployment or distributed session load |
| A03 | Logout retry | PASS | PASS | No credentials redisclosed |
| A04 | Recovery retry | PASS | PASS | Private development delivery only |
| A05 | One-use reset race | PASS | PASS | Synthetic identities only |
| A06 | Verification retry | PASS | PASS | External email disabled |
| A07 | Invitation retry | PASS | PASS | No external identity provider |
| A08 | Business versus auth receipts | BLOCKED | BLOCKED | Contact endpoint/device credential issuance remain deferred |
| C01 | Project contact ownership | NOT IMPLEMENTED | NOT IMPLEMENTED | No global private contact inbox implemented |
| C02 | Project contact abuse/retention | NOT IMPLEMENTED | NOT IMPLEMENTED | D10 retention not approved legal policy |
| P07 | Artifact and truth isolation | BLOCKED | BLOCKED | Restricted sealed-run object downloads/evaluator grants deferred |
| S07 | Authorization on retry | PASS | PASS | No privilege widening for cached results |
| M09-E2E | Persisted resident-to-feedback chain | PASS | PASS | Investigation has NOT_APPLICABLE verification; separate manual repair remains NOT_VERIFIABLE |
| M09-RACES | Competing scheduling transactions | PASS | PASS | Short deterministic scenarios, not exhaustive interleavings |
| M09-QUEUE | Real worker process restart and attempts | PASS | PASS | No external adapters or default retry delays |
| M09-RECOVERY | Actual HTTPS/API/database failure | PASS | PASS | Only marked disposable DB disrupted; no infrastructure failover/long soak |
| M09-SCIENCE | Numerical reproduction and all69 public snapshots | PASS | PASS | Simulation-only; M05 unfavorable results unchanged |
| M09-UI | Responsive and inert hostile text | PASS | PASS | Native zoom/full assistive technology certification not performed |
| M09-HARDWARE | Digital consistency and physical boundary | PASS | PASS | Digital only; native ERC, MCU firmware, physical fit/calibration/field tests absent |
| M09-RELEASE | Fail-closed negative capabilities | PASS | PASS | Boundary PASS is not implementation of D6/D7/D8/D9/D10/public deployment |

## Completion work and gates

| ID | Item | Current | Required work |
| --- | --- | --- | --- |
| META-COUNTS | Runtime inventory | PASS | Preserve compatibility and record every additive count transition. |
| META-ISSUES | Milestone closure | PASS | Close #7 only against original criteria; no M10 before readiness review. |
| EVIDENCE-01 | Stale HTTPS evidence migration label | PASS | Query live alembic_version; explicitly version source-baseline transition without rewriting historical evidence. |
| DOC-01 | Current repository presentation | PASS | Update actual status, estimated INR 59870 plus INR 130 margin, source-linked media and reproducible navigation. |
| DOC-02 | Subsystem documentation | NOT TESTED | Audit important folder guides and distinguish implementation from proposals. |
| UI-01 | Website quality audit | NOT TESTED | Inspect actual public/auth/role workflows and fix only demonstrated defects using accepted design system. |
| DEP-01 | Development dependency and license limitations | BLOCKED | Assess affected tools and safe targeted upgrades; preserve attribution; owner chooses project license. |
| HW-01 | Physical and fabrication evidence | BLOCKED | Keep accurate digital-only labels and procurement risk; actual hardware testing requires separate authorization. |
| GATE-01 | Privacy and deployment controls | BLOCKED | Implement safe independent development work while retaining each activation gate. |
| DEMO-01 | Pre-M10 readiness | BLOCKED | Complete safe slices, final exact-main CI and honest before/after acceptance review. |

## Execution sequence

1. Correct the stale evidence label through an explicit reviewed source-baseline extension and live database evidence.
2. Implement independent complaint/contact/device/realtime/evaluator improvements in focused, reviewed slices with unchanged scientific evidence.
3. Keep offline, media, visit-access and external delivery activation closed until their actual controls and approvals exist; test safe interfaces without claiming the full requirement passes.
4. Audit and improve the actual website, README and subsystem guides with source-derived visuals and real screenshots.
5. Run fresh combined acceptance, record before/after the same 40 cases, and request final readiness review before M10.

Each slice requires critical diff review, exact-head four-job CI, normal protected merge and post-merge CI before dependent work. No baseline pin is disabled by this register. No scheduled availability, legal retention, field performance or procurement quotation is invented.

## Executed foundation validation

On 2026-10-25, the corrected tool executed the complete synthetic HTTPS workflow against `hydro_disposable_prem10_demo`: certificate verification PASS, actual API restart PASS and independent outcome NOT_VERIFIABLE. Its summary reported `m07_c_001`, independently matched against the live `alembic_version` query. Private output stays outside Git at workspace `work/pre-m10-https-demo`; no credentials, keys or mail are published.

The existing CI backend job executes this same tool and uploads its sanitized summary. Exact-head CI remains required before merging. Local foundation, M02/M07 design mutations, M07-A/B/C, M06, M09 boundary and four new source-revision regression checks passed. This correction changes only the evidence label, not application runtime, API contracts, migrations or scientific results. Original 40-case statuses remain unchanged.

PR #23 merged at `848c1c8a1dbf72f980c1f58454a41d0bd332eab8`; all four [post-merge CI jobs](https://github.com/siddalakarthik/HYDROOVERITY-SIH26254/actions/runs/40193968696) passed. Its exact-head CI artifact independently confirms the corrected revision, verified TLS, actual restart and NOT_VERIFIABLE outcome. The repository-presentation slice adds seven unchanged reviewed previews and corrects root/current navigation; GitHub rendering and its final CI are still pending. Original 40-case statuses remain unchanged.
