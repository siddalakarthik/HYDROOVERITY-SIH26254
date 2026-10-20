# Data contracts and provenance

Issue #2; schema design only. Canonical wire definitions are [OpenAPI](openapi-design.json); storage fields are [database design](DATABASE_DESIGN.md). No synthetic measurements are generated in M02.

## Trusted origins

| Principal / source | Category | Environment | Required binding |
| --- | --- | --- | --- |
| Simulation producer | SIMULATION | SIMULATION | Active run/job lease, virtual channel and immutable config |
| Physical adapter | HARDWARE | LABORATORY or FIELD | Provisioned device credential profile, channel/config, actual capture receipt |
| Human measurement/receipt | MANUAL | MANUAL | Authenticated actor, method/limitations; never relabel as calibrated hardware |

The ingestion request does not contain writable category/environment. Server derives them from authenticated adapter/run and rejects conflicts, unknown fields, wrong channel/config or run. A device profile declaring FIELD means acquisition context, not field-validated performance. Manual observations attached to field investigations remain manual. Hardware source does not imply calibration or a confirmed leak.

Observation retains stable event/channel ID, collection/receipt UTC times, unit, finite scalar XOR artifact, quality, fresh_until, source/environment, config/hash, calibration or explicit null, and simulation_run_id where required. Accepted observations are immutable; correcting a bad record creates a superseding receipt, never edits history. Freshness derives from source-specific reviewed configuration; no invented universal stale threshold. Late/out-of-order events may be stored but cannot masquerade as current evidence. UI includes collection versus receipt and known calibration status.

Canonical units: pressure bar, flow L/min (or m³/h with explicit conversion retained), temperature Celsius, relative humidity percent, wetness instrument-unit/state with method, distance m, delay s, sample rate Hz, diameter mm. Retain raw-unit/source conversion metadata in config/artifact; reject quantity/unit mismatch and nonfinite/overflow values. Flow residual boundary excludes only authorized demand not already included in measured outflow; storage-change uncertainty is explicit. Supply-state and interpretation configuration remain versioned science, not fixed numeric heuristics.

## Truth isolation and reproducibility

Runs expose scenario version, allow-listed parameters, algorithm config/hash and observation-noise seed. Actual leak labels/positions and separate truth-generation seed live in restricted_simulation_truth and a separate private object namespace. Detector contracts receive only OBSERVED data and allowed context, never generator truth, source positions, labels or a seed sufficient to reconstruct them. The generator and evaluator use separate DB/object credentials unavailable to detector/ordinary API workers. A process holding both sets of credentials is not an acceptable isolation boundary.

Ordinary engineer APIs expose nontruth outputs. Evaluation requires ENGINEER plus explicitly granted EVALUATOR, tenant ownership, completed sealed run, and an audited evaluation request. Detector tuning and blind evaluation use separate run/holdout definitions; evaluation results do not flow back into operational streams/caches. A hash-only reference is not permission to download a truth artifact. Reproduction manifests retain public config plus restricted truth-seed linkage for authorized evaluation; regular report exports omit restricted values. No global administrator bypass in application UI.

## Modes, intervals and repairs

WorkspaceMode SIMULATION/OPERATIONAL is separate from source environment. Simulation records have persistent SIMULATED DATA banners, API provenance, report watermarks and mode-filtered metrics. Operational queries default to excluding simulation; mixed evidence cannot silently enter operational incidents or performance reports. Lab/field/manual remain separately filterable within operational context. Field-performance denominators must include only appropriate physical trials and labeled ground truth, never ordinary service complaints.

Acoustic result includes actual recorded lag convention, path/endpoint metadata, assumed/calibrated speed and uncertainty, quality reasons and candidate intervals or explicit abstention. A noise peak is not an exact location. Qualified output requires interval validity; unresolved outcomes carry no candidate coordinate. API review must preserve numeric timing/speed/path uncertainty fields before analysis implementation; text-only confidence is insufficient. A confidence percentage requires a calibration reference and defined meaning.

GUARD-5 channels remain independent A/B/C/EXT/BYPASS, with temperature/humidity context separate. EXT-first, bypass-only, condensation context and collection failures retain competing explanations. Dry versus disconnected is UNKNOWN unless the actual hardware supervision is supported and evidenced.

Repair records are reports of work. Verification compares before/after time windows, pressure/supply state, legitimate demand/storage, calibration, quality/freshness and uncertainty. Store evidence references and reviewer reasoning. VERIFICATION_PASSED/FAILED requires interpretable comparable evidence; otherwise NOT_VERIFIABLE. A completed task or closed citizen complaint is never scientific proof of a repaired leak or saved litres.

## Final review guards

Simulation ingestion has explicit credential/run-derived SIMULATION source and environment metadata; both batch wrappers and scalar inputs reject writable source/environment/truth overrides. Ordinary nested responses and requests must not reach EvaluationResult, actual labels/positions or private truth-generation seeds. Public observation_noise_seed remains permitted; it must never derive the sealed truth seed. Artifact downloads check current tenant membership, nontruth classification and parent ACL; output listings/exports/SSE must also omit restricted artifact IDs. Reclassification cannot move a truth object into an ordinary namespace. Auth/global contact carry no scientific claim or fabricated tenant source. Structural mutation tests inspect the design only; backend and object-store denial tests remain future work.
