# System architecture

Status: functional architecture frozen; implementation and detailed hardware unbuilt. Source: [master context](../project/HYDROOVERITY_MASTER_CONTEXT.md).

## Physical observation routes

WATCH records available flow, pressure, demand/storage context, temperature, freshness and device faults. It qualifies OFF/FILLING/STEADY/DRAINING/UNKNOWN. For a consistently defined sector boundary, `V_unexplained = V_in - V_out - V_authorized_demand - Delta_storage`, with uncertainty. Define outlet/demand accounting before coding to avoid double subtraction. Unknown demand/storage prevents unique leak attribution.

GUARD-5 is a removable exposed-joint collar: protected A/B/C collection paths, independent EXT environmental reference and lower BYPASS witness, guards/drip breaks, drains, replaceable probes/liners and external clean-water service ports. The optional 0.2–1.0 mL challenge is an experimental external-collar procedure. Timing, neighboring responses and drainage faults must be logged. Pulsed/current-limited or alternating probe drive is proposed; dry-versus-disconnected discrimination needs an engineered supervision method.

EAR-PAIR uses two matched/swappable external pickups, independently buffered matched low-noise protected/filtering front ends, shielded cables and one stereo PCM1808-class ADC/common sample clock feeding a compatible ESP32/I²S processor. Exact pickup, module clock source/MCLK, pin allocation, sample rate and buffering are unresolved. Wireless delivery never substitutes for sampling synchronization.

On an eligible simple path, `x_A = (L - c * Delta_t)/2`, with `Delta_t = t_B - t_A`. Test near-A/center/B sign behavior. Bound path length, speed, mounting/timing and peak ambiguity; compare filtered cross-correlation and GCC-PHAT on identical captures. Active calibration cannot establish passive leak audibility.

## Information flow and operational decisions

Simulation producer / future device adapter -> versioned observation ingestion -> validation/provenance/storage -> supply/evidence assessment -> incident review -> assignment/work order -> field evidence/repair -> comparable verification -> closed/reopened/unverifiable.

Routine hydraulic decisions use comparable pressurized stable periods. Direct wetness, faults and severe confirmed pressure collapse have an independent lane during transitions. Preserve environmental, collection-fault, insufficient-signal and unresolved explanations. Evidence status, incident lifecycle, task status and repair outcome are separate domains; exact enums require M02 review.

## Software responsibilities

- `apps/web`: public explanation/citizen workflows and authorized utility/worker/admin interfaces.
- `services/api`: auth, tenant authorization, domain operations, evidence and persistent audit history.
- `services/ingestion`: future adapter/producer boundary; synthetic source remains explicit.
- `services/notifications`: future delivery/retry responsibility.
- `packages/shared-types` and `shared-config`: versioned contracts/configuration where useful.
- `simulations`: independent engines/orchestrator and restricted truth/evaluation.

These are logical boundaries, not a decision to deploy three microservices. Start with a coherent, simple deployment after M02 review. No service entrypoints exist in M01.

## Provisional stack and interfaces

Next.js/React/TypeScript/Tailwind; Python 3.12+ FastAPI/Pydantic/SQLAlchemy/Alembic; PostgreSQL/PostGIS, initially also for observations/events; MapLibre with permitted tiles; Recharts or equivalent; NumPy/SciPy/Pandas and WNTR/EPANET 2.2 where valid. Docker Compose if supported; pytest/Vitest/Playwright when implementations exist. Record compatible versions before installation.

Choose SSE or WebSocket with polling/reconnect fallback during M02. MQTT is an optional future bridge, not mandatory now. Local operation remains required. Session/CSRF/recovery design, tenant boundaries, attachment storage, offline conflict/idempotency policy and hosting remain open. `.env.example` is a future configuration sketch, not working runtime configuration.

## Cross-cutting contracts

All observations retain identity, collection/receipt timestamps, units, quality/freshness, calibration and explicit source environment. Simulation config/run IDs identify synthetic records; hidden truth is stored and authorized separately. UTC internally; Asia/Kolkata and India-relevant units in presentation. Sensitive citizen and infrastructure information must not cross public trust boundaries. See [data dictionary](DATA_DICTIONARY.md) and [threat model](THREAT_MODEL.md).

## M02 detailed design authority

The M01 text above is preserved as the baseline. M02 resolves its software choices in [DEPLOYMENT](../deployment/DEPLOYMENT_AND_STACK_DECISIONS.md) and the linked M02 documents; these detailed contracts supersede provisional software statements above, subject to owner PR review. Hardware/scientific unknowns remain deferred. No implementation is claimed.
