# HYDROOVERITY — Complete Project Context for Codex

**This is the authoritative onboarding brief for a completely fresh Codex conversation.**

**Project:** HYDROOVERITY  
**Team:** TARK  
**Team ID shown in already-submitted deck:** 155480  
**Competition:** Smart India Hackathon 2026 (SIH), Hardware / Clean & Green Technology  
**Problem statement:** SIH26254  
**Problem-setting ministry:** Ministry of Jal Shakti, India  
**Date of context brief:** 20 October 2026  
**Current stage:** Architecture frozen at the *system level*; no physical prototype or field validation. The immediate work is GitHub, full-stack software, simulations, engineering CAD/schematics, test automation, and a concept/demo animation.  
**Material procurement ceiling:** INR 60,000 for a possible complete hardware demonstration. Current planning allocation: INR 56,750 **including contingency**; estimates, not purchase quotations and not an SIH reimbursement promise.  
**Official project name:** Always **HYDROOVERITY**. Do **not** invent or use numbered version names.  
**Mission:** **“Find the leak. Understand the evidence. Verify the repair.”**

---

## IMPORTANT: HOW YOU MUST HANDLE THIS BRIEF

You are joining the project as our senior full-stack, scientific-software, embedded-systems, and DevOps coding partner. The human owner is an engineering student who wants a disciplined, useful product rather than a generic college dashboard. Your job is to understand the entire concept now and to execute future development tasks one by one when the owner authorizes them.

**FIRST RESPONSE ONLY:** read this brief, summarize your understanding, point out the few blocking contradictions or necessary choices, outline the first GitHub/repository setup milestone, and **STOP**. **Do not create a repository, files, code, branches, issues, cloud resources, or website yet. Do not incur charges or install tools.** We will send the actual first implementation instruction separately. If the Codex environment cannot access the attachments or connected services, state precisely what is missing instead of pretending to have read it.

Throughout this project:

1. Treat the **already-submitted six-slide SIH PPT/PDF** as the authoritative historical submission; do not quietly replace its core five-channel collar or mission.
2. The current architecture is frozen at the functional level, but particular sensors, housings, amplifier values, schematics and algorithms remain engineering hypotheses until tested. Propose substantive changes in writing; do not silently change the architecture.
3. Separate **DOCUMENTED / SIMULATED / CODE-TESTED / HARDWARE-TESTED / FIELD-VALIDATED / UNKNOWN** for every performance claim. Never label simulated readings as live physical measurements.
4. Do not fabricate accuracy, field data, run-time results, patent novelty, official SIH points, battery years, hardware photographs, supplier quotations, government budgets, or grant entitlements.
5. Be scientifically adversarial: detect physical impossibilities and error paths; prefer simpler reliable hardware over complicated unjustified modules.
6. Deliver every software feature as an integrated, tested workflow, with persistence, validation, authorization, error states and reproducible tests. No inert UI buttons or fake API success.
7. Explain technical decisions in plain language when reporting to the owner. Use professional code, commits, documentation and tests.
8. Use India-relevant units and operating conditions; default currency INR, pressure in bar, flow in L/min or m³/h (clearly labeled), distance metres, durations seconds, local presentation in Asia/Kolkata, and UTC internally.
9. Respect the user's current **digital-first** decision: no physical purchases or prototype construction at this stage; prepare buildable engineering design and a clearly labeled digital simulation/animation. Do not describe a video as a hardware demonstration.
10. Respect third-party intellectual property and open-source licenses. No blind copying of other teams' assets or code.

---

## 1. THE EXACT SIH PROBLEM WE MUST SOLVE

**Title:** *Development of Indigenous Leak Detection Sensor Systems for Operation & Maintenance of Water Supply Pipelines.*

**User-provided problem description (controlling scope):**

> Water losses due to leakages in distribution networks significantly impact the efficiency, reliability, and sustainability of water supply systems. Undetected leaks can lead to wastage of treated water, increased operational costs, reduced service levels, and potential contamination through ingress of pollutants. Current leak detection technologies are often expensive and may not be suitable for widespread deployment, particularly in rural and small-town water supply systems. There is a need for indigenous, affordable, and scalable sensor-based solutions capable of real-time detection and localization of leaks within water distribution networks.

**Explicit solution expectations:**

- Detect and accurately locate leakages in pipelines.
- Provide real-time alerts and monitoring.
- Be energy-efficient and cost-effective.
- Integrate with existing water-supply infrastructure.
- Support remote monitoring and maintenance planning.

**Expected outcomes:**

1. Indigenous sensor systems for water distribution networks.
2. Early identification and localization of leaks.
3. Reduction in non-revenue water and operational losses.
4. More effective operations and maintenance.
5. Greater reliability, sustainability and service delivery.

**Engineering context:** Indian rural and small-town networks may have intermittent supply, low pressures, PVC/HDPE or mixed pipe materials, sparse inspection points, pumps, storage tanks, customer draw-off, unstable power/connectivity, rainfall/soil-moisture confounding, and limited technician budgets. This is **water-distribution pipe leakage**, not hydropower, flood alerts, reservoir-overflow prediction, irrigation scheduling or an unrelated consumer tap automation project.

**IMPORTANT BOUNDARY:** The supplied SIH problem statement does **not** itself promise a INR 60,000 or INR 200,000 government grant, or give a fixed rupee component budget. INR 60,000 is our voluntary prototype material cap, not an official allowance. An older SIH hardware BOM allowance reportedly existed in 2025; it must not be asserted as the 2026 rule without new verification.

---

## 2. WHAT HAS ALREADY BEEN SUBMITTED

The team **already submitted a six-slide SIH idea-presentation** with these commitments:

**Title:** *HYDROOVERITY — Evidence-Qualified Leak Detection and O&M Intelligence for Intermittent Water Networks*.

**Slide 1 — Identity:** Team TARK; team ID 155480; SIH26254; Ministry of Jal Shakti; Hardware / Clean & Green; title and mission. It says software/hydraulic-model checks passed while hardware qualification remained outstanding.

**Slide 2 — Proposed solution:** a five-channel diagnostic collar with independently collected zones **A/B/C**, an **external** wetness reference and a lower **bypass / collection-failure gutter**; supply-state qualification; acoustic escalation when warranted; evidence levels / explicit unresolved and fault outcomes; detection-to-repair loop.

**Slide 3 — Technical approach:** prototype-level references to ESP32-WROOM, ADS1115 inputs, SHT31, DS18B20; flow/pressure + supply-state model; acoustic correlation on qualified spans; measurement equations; bounded synthetic acoustic result. The 30.1–38.9 m synthetic candidate interval is NOT a confirmed physical pipe hole.

**Slide 4 — Feasibility:** prior artifact reports **184 Python tests, five frontend tests, 17 browser checks, six package checks, and an EPANET 2.2 model**, while declaring **physical trials: 0; field trials: 0**. The INR 18,000–31,000 range was an earlier *development/qualification bench* allowance **excluding field instrumentation / acoustic kit**, NOT our current complete material BOM. Do not reinterpret these historic tests as tests Codex has independently rerun or code Codex has in the new repository.

**Slide 5 — Impact:** water/service, accountable maintenance, ingress-risk attention, clean/green benefits; a hypothetical example (1 L/min × 8 hours/day = 480 L/day). The illustrated avoided loss is synthetic, not measured recovery. The system does **not** directly detect contamination.

**Slide 6 — Research:** JJM context, EPANET/WNTR, acoustic and water-loss references; acknowledges prior art in flow/pressure monitoring, acoustic correlation, wetness sensing, GIS and event management. Differentiation was **evidence-qualified integration**, not invention of basic acoustic or moisture physics.

Codex should preserve continuity with this official submission. If new terminology or new functionality is introduced, map it back to the original physical and operational commitments.

---

## 3. THE FROZEN SYSTEM: OVERVIEW

**One integrated water-leak operations system, with two complementary physical observation routes.**

The system can be summarized as:

`HYDRO-WATCH -> [GUARD-5 local joint route || HYDRO-EAR qualified pipe-span route] -> Evidence Decision -> Incident -> Work Order -> Repair -> HYDRO-VERIFY`.

**A. HYDRO-WATCH — hydraulic context and supply-state monitoring:** Pressure, available flow/meter inputs, temperature/time, monitoring-node health, expected authorized withdrawal/storage context. State machine `OFF`, `FILLING`, `STEADY`, `DRAINING`, `UNKNOWN`.

**B. GUARD-5 — physical guarded five-channel diagnostic collar at accessible exposed joints:** Three *independently channeled* internal wetness collection pockets A/B/C; external rain/splash reference; separate lower bypass witness; physical guards, drip breaks, drainage and labeled maintenance test ports. This is our primary targeted **mechanical/hardware differentiation hypothesis**.

**C. HYDRO-EAR / EAR-PAIR — two-sensor pipe-contact acoustic investigation:** For an eligible and adequately pressurized, surveyed, simply connected span with two accessible bracketing attachment positions. Two matched acoustic pickup channels (contact piezo or measured alternative), analog front-end, and **one stereo PCM1808-class ADC / one physical sampling clock** to eliminate independent wireless capture-clock ambiguity in the demonstration.

**D. Evidence/decision engine — honest diagnosis:** distinguish a joint-local wetness suspicion from network-wide hydraulic suspicion, acoustic candidate interval, environmental exposure, sensor fault and unresolved physical ambiguity. Attach reasons, measurement provenance, signal-quality evidence, confidence *with calibrated meaning*, and next actions.

**E. HYDRO-VERIFY — closed-loop operations:** Offline-first event logging, incident ownership, field investigation notes, photographs if appropriate, maintenance worker assignment, repair steps, comparable before/after operating measurements, review, final outcome, and auditable evidence record.

The design is **NOT** a promise that one collar detects all leaks in a village, or that one acoustic pair automatically pinpoints any leak over kilometres of buried pipeline.

### 3.1 Clear division of physical coverage

- **GUARD-5 protects an accessible fitting/joint only when leaked water reaches its collection paths.** It does not guarantee exact crack coordinates; underground soil migration and gravity can lead to ambiguous water arrival.
- **HYDRO-EAR estimates position on an eligible, bounded, instrumented pipe span** if adequate passive leak signal reaches both pickups, timing is valid, and the sound propagation path is understood sufficiently.
- **HYDRO-WATCH can detect hydraulic abnormalities**, but with unknown demand/storage, a positive flow imbalance cannot uniquely establish a pipe leak.
- **No-pressure/dry pipe:** passive leak noise may be absent. Use `UNOBSERVABLE`, or request a future authorized pressurized measurement; do not invent a leak coordinate.
- **Remote network-wide instantaneous localization:** not delivered by one two-endpoint kit. Permanent automatic pinpointing applies only to fully instrumented eligible spans; a portable pair is a technician investigation tool.

---

## 4. GUARD-5: PHYSICAL MECHANISM AND OPERATING LOGIC

**Mechanical concept:** Split/removable, non-pressure-bearing, preferably 3D-printable housing that fits around a suitable exposed pipe fitting without opening the drinking-water line. Detachable liners, baffles, drip edges, independent wetting paths, gravity drainage, protected wiring and replaceable probe elements. Detailed dimensions, tolerances and actual water-path geometry are not frozen; CAD work must define and review them.

**Exactly five water sensing channels:**

1. `COLLAR_A` — first protected local collection pocket.
2. `COLLAR_B` — second protected local collection pocket.
3. `COLLAR_C` — third protected local collection pocket.
4. `COLLAR_EXT` — separate outside environmental/rain/splash witness.
5. `COLLAR_BYPASS` — lower collection/overflow/water-missed-intended-path witness.

Avoid confusing `COLLAR_B` (inner zone B) with `COLLAR_BYPASS` (fifth channel). All five require distinct, independently measured electronic channels. Proposed probes are corrosion-limiting pulsed/current-limited or alternately driven conductivity electrode pairs with appropriate protection; avoid permanently biased bare copper corrosion. Humidity and pipe temperature are context sensors, not sixth/seventh wetness channels.

**Local physical self-test:** Optional technician performs an **external, clean-water syringe challenge** through a labeled access port at each pocket, e.g. an experimental 0.2–1.0 mL reference addition. Log injected location/nominal volume, contact response, response delay, neighboring-channel crosstalk, run-off/drain response, sensor faults and blocked-path behavior. This is performed on the **outer collar only**; never inject water into a pressurized municipal drinking-water line.

**Competing explanations the system must preserve:**

- Protected inner wetness during pressurized service, external dry -> **local fitting leak suspected**, *not proved*.
- External sensor wets first -> environmental exposure likely; crossflow may make source uncertain.
- Lower bypass wet while inner channel dry -> collection bypass, blocked/misdirected water or external entry; **not proof of leakage**.
- Strong humidity/dew and pipe temperature context -> condensation possible; not a perfect distinction.
- No wetness + disconnected/corroded electrodes -> **sensor fault**, not “definitely no leak.”
- Collectors fail test injection / neighboring channels wet incorrectly -> local collection or wiring fault.
- Supply is filling -> do not blindly suppress a direct important wetness/fault observation; pressure-state gates apply to *routine hydraulic attribution*, not all urgent physical events.

**Primary R&D comparison:** ordinary single moisture pad versus (1) a multi-zone collar without guards/bypass and (2) full guarded GUARD-5 with service test. Test real joint wetness, rain/spray, condensation, blocked drains, external run-off, off-axis leak migration, disconnected electrodes and no-leak controls. Physical advantages are **targets** until tested.

---

## 5. HYDRO-WATCH: HYDRAULIC MODELLING RULES

**Input examples:** available inlet/outlet water-meter readings, pressure transducers, pump status, valve/opening state if genuinely observed, tank level if available, ambient/pipe temperature, state freshness and calibration.

**Operating states:** `OFF | FILLING | STEADY | DRAINING | UNKNOWN`. Require explainable transitions and pressure/flow conditions. Do not infer `STEADY` only from passage of a fixed number of minutes.

For a controlled rig or known hydraulic sector:

`V_unexplained = V_in - V_out - V_authorized_demand - Delta_storage`.

Also expose instrument uncertainty. A positive residual is **unexplained water loss**, not necessarily proof of physical leakage; unknown consumption, meter drift, filling a storage tank or unmetered outlets can produce the same residual.

**Alert logic has two separate lanes:**

- *Routine*: only compare suitable stable, pressurized periods with other genuinely comparable periods. Persistent anomalies may mark a sector as suspected.
- *Urgent/independent*: instrument fault, direct wetting observation, or severe confirmed pressure collapse may be recorded during filling/draining as relevant. The routine gate must not hide everything.

**Good adaptation from JalNaadi:** Learn flow baselines with explainable EWMA/CUSUM or similar detectors, but only after explicit state qualification. A hard-coded 02:00–04:00 “night-flow window” is inappropriate when that rural network is not pressurized then. Train/test on event simulations with unknown legitimate demand, pressure recovery, filling and sensor drift.

**Limit of simulation:** EPANET/WNTR is appropriate for quasi-steady/extended-period, pressurized hydraulic network studies, but not automatically a validated model of all rapid two-phase filling, trapped-air transients and water hammer. State model assumptions prominently.

---

## 6. HYDRO-EAR: ACOUSTIC ENGINEERING RULES

**Proposed demonstrator electronics (NOT purchased or validated):**

- Two paired or swappable non-intrusive pipe-contact pickups on accessible brackets; exact sensor type unresolved. Low-cost piezoelectric elements are *candidates*, not a guarantee for quiet plastic leaks.
- Two independently buffered, matched, high-input-impedance, low-noise analog front ends with input protection, filtering and shielded cables.
- One compatible stereo audio ADC, `PCM1808`-class, feeding a compatible ESP32-I²S-capable processor. Check the actual module's source/MCLK/clock pins and true stereo timing rather than only quoting chip specifications.
- One **common sampling clock for both channels**. Do not treat LoRa, Wi-Fi, ESP-NOW or USB packets as sub-sample synchronization.
- Raw waveform capture with timestamp, sample rate, channel calibration, clipping flags, sensor interface state, pressure and path metadata.
- If future alternatives include PVDF, geophones or a fluid-borne hydrophone, they must be introduced as properly qualified experimental alternatives, not quietly made mandatory. Live potable-line insertion is outside scope.

**Acoustic candidate location on an eligible simple path:**

`x_A = (L - c * Delta_t)/2`, where:

- `L` is measured path length between pickup stations;
- `c` is relevant propagation speed for the actual observed mode;
- `Delta_t = t_B - t_A` is measured acoustic arrival-time difference;
- `x_A` is distance measured from endpoint A.

This sign convention must be tested with known simulated sources near A, center, and B. Incorporate uncertainty in timing, propagation speed, sensor mounting, path length and ambiguous peaks. Show a **candidate distance interval** (or multiple candidates) only if the evidence supports it.

**Processing baselines:** bandpassed time-domain cross-correlation and GCC-PHAT on the same recordings. Qualified method may add coherence/band availability, repeated windows, independent pump-noise controls, calibration stability, sensor reseat check and interval/abstention logic. Benchmark against competent baseline; no one method wins by design.

**Critically:** Active tap/chirp path calibration may estimate timing or path transmission, but cannot by itself prove that a tiny *passive leak* emits enough acoustic energy for identification. The source depends on pressure, leak geometry, burial/backfill and pipe properties. Acoustic slit leaks can be much quieter than an open nozzle.

**No automatic guarantee:** low or zero pressure; too-quiet leak; strong pump noise; multipath; branches or mixed pipes; inaccurate topology; multiple simultaneous leaks; damaged sensor/clock. Explicit `NO_PRESSURE`, `INSUFFICIENT_SIGNAL`, `PATH_AMBIGUOUS`, `SENSOR_FAULT`, `UNRESOLVED` states are functional outputs.

**Sanity examples, NOT advertised sensitivity:** a 12 m simple span at assumed 400 m/s has 30 ms full-path travel time. An idealized 1 mm hole at 1 bar might release ~0.41 L/min, but discharge does *not* establish audibility. Under specific simulation conditions, synthetic delay estimates may appear accurate; they must never be presented as measured field accuracy.

---

## 7. HYDRO-VERIFY: REAL MAINTENANCE AND CITIZEN VALUE

The system exists to reduce wasted technician visits, improve repair accountability, and help people receive reliable water service. Its operational software is a real application, not a poster.

**Roles and access levels:**

1. **System administrator** — tenant settings, users/roles, sensor provisioning and access-policy audit. Keep administrator destructive actions behind confirmation and authorization.
2. **Water utility engineer** — pipeline topology, sensors, pressure/flow conditions, investigation evidence, simulations and technical reports.
3. **Supervisor / maintenance manager** — incident triage, prioritize visits, assign work orders, review repairs, inspect overdue incidents.
4. **Field technician** — assigned investigations, offline-friendly checklist, evidence/photos, field notes, repair status, sensor service/test receipts and follow-up.
5. **Resident / citizen / customer** — submit reports of visible water leaks, low pressure or service failure, provide rough location/photo (with consent), track only their own requests, receive appropriate status. Do **not** expose private network sensors, other residents' information or sensitive infrastructure detail.

An organization may support multiple users and zones; implement tenant-aware access. Authentication, password recovery, data validation, rate limiting, immutable/auditable status history and least-privilege authorization are required.

**End-to-end workflow:** `OBSERVATION -> SUSPECTED / NEEDS_REVIEW -> VERIFIED INCIDENT -> PRIORITIZED -> ASSIGNED -> FIELD INVESTIGATION -> REPAIR RECORDED -> POST-REPAIR CHECK -> CLOSED / REOPENED / UNVERIFIABLE`.

Allow citizens' reports to coexist with sensor evidence without automatically converting every citizen complaint into a confirmed leak. Supervisors may merge probable duplicates with traceable provenance. A repair is only **VERIFIED** when the available before/after evidence is actually comparable; support `NOT_VERIFIABLE` legitimately.

**Field-centric features:** mobile responsive PWA style, optional Telugu/Hindi/English UI if feasible and correctly translated, offline notes / queued updates, connection indicator, upload retries, maintenance service hours, worker task assignment/ownership, safe public complaint status, map routing via external app only when authorized, incident history, and exportable reports.

---

## 8. WEBSITE / WEB APPLICATION: COMPLETE PRODUCT REQUIREMENTS

**Name:** HYDROOVERITY Operations (as product sublabel). **Official project name remains HYDROOVERITY.**

**Separate public site and authenticated portal:**

### 8.1 Public presentation and citizen-facing pages

- Home: concise value proposition, what the system detects, limitations, evidence-before-action message.
- How It Works: physical GUARD-5 cross-section, hydraulic states, qualified acoustics, maintenance loop; diagrams marked conceptual.
- Benefits & Scale: how shared investigation kit + selectively installed collars could work in rural water networks; transparent coverage and cost caveats.
- Citizens: user registration/login, leak/service complaint creation, safe rough location selection, photo upload (consent), status lookup, notifications.
- Contact / team info / feedback, accessibility, privacy and terms.
- Engineering transparency: **SIMULATION**, **DESIGN**, **UNTESTED** labels; do not manufacture testimonial/reliability metrics.

### 8.2 Authenticated utility portal

- Overview dashboard with sector states, incident counts, device health, **simulation mode visible globally** when using synthetic data.
- Network explorer/map for real pipe graph models, node IDs, pipe material/diameter/length/known accessibility, demand zones, installed collars, eligible acoustic pairs, coverage gaps.
- Realtime/live-compatible monitoring: flow, pressure, temperatures, water channels, acoustic signal quality, buffering/freshness, device fault events. **The initial feed is synthetic**; real sensor ingestion is a future interface.
- Incident center: list/filter/search, signal provenance, evidence status, `SUSPECTED`, `UNRESOLVED`, `FAULT`, `CONFIRMED_LOCAL_WETNESS`, `REPAIR_CHECK` semantics, drill-down raw data and evidence.
- Acoustic lab: signal visualization, candidate delay/time-lag, speed assumption, uncertainty interval, baseline comparison and unresolvable cases.
- GUARD-5 diagnostics: zone timelines, E external, bypass, recorded self-test receipt, migration/cross-talk warnings, blocked drains and sensor disconnections.
- Work orders: assignment, priority, technician updates, photos, comments, staged status transitions, deadlines, verification.
- Asset management: stations, collars, probes, calibration dates, metadata, maintenance and fault status.
- Operations analytics: MTTR, response delay, eligible-span coverage, recorded false alerts from *known labeled test cases*, water loss *estimates* with clearly labeled assumptions. No fabricated field savings.
- Reports: date/zone filters, CSV/PDF export with data provenance, incident timeline and simulation settings.
- Admin/settings: users, roles, organization, session security, webhook/API credentials, data retention.
- Feedback backlog: owner/mentor/user comments, severity, linked issue, assignee, status, resolution note and release version.

**Critical product requirement:** Website must be *functional* with working authentication, protected routes, real backend persistence, validated inputs, role permissions, simulated streamed updates, useful errors and end-to-end tests. Avoid a page full of inert cards, random changing metrics or placeholder buttons.

**Visual standard:** utility operations tool, not crypto/marketing spectacle. Clear hierarchy, high contrast, mobile-first worker workflows, status+reason in text (not color alone), fast charts, compact map, terminology ordinary workers can understand, meaningful empty/loading/error/offline states, and no huge claims.

**Safety/privacy:** mask citizen contact details in broad maps, do not expose precise internal valve/hydrant data to public accounts, rate-limit complaints/auth, audit privileged actions and secure uploads.

---

## 9. SOFTWARE STACK: RECOMMENDED STARTING POINT, SUBJECT TO ONE ARCHITECTURE REVIEW

Proposed for a student team needing a credible and maintainable platform:

- **Frontend:** Next.js + React + TypeScript + Tailwind CSS; accessible UI library with clear design primitives.
- **Backend:** Python 3.12+ with FastAPI, Pydantic and SQLAlchemy/Alembic.
- **Database:** PostgreSQL + PostGIS for pipe spatial features; use PostgreSQL for sensor time-series/events initially instead of installing five databases.
- **Map:** MapLibre and permitted OpenStreetMap-based tile provider; avoid embedding secrets or violating tile limits.
- **Charts:** ECharts or Recharts, selected once.
- **Realtime updates:** WebSocket or server-sent events from backend; retain fallback polling and reconnect logic.
- **Science:** NumPy, SciPy, Pandas where needed, WNTR / EPANET 2.2 for valid hydraulic models, explicit tests and random seeds.
- **Authentication:** secure password hashing, role and tenant authorization, CSRF/session/token design consistent with the chosen stack. No fake front-end role switching as security.
- **Sensor ingestion:** versioned API with MQTT adapter as optional future bridge; simulation producer is a **separate source** clearly identified and reversible.
- **Local developer environment:** Docker Compose for API/PostgreSQL/web if supported; portable `.env.example` without secrets.
- **Testing:** pytest for API/science, Vitest for frontend units and Playwright for browser E2E.
- **CI:** GitHub Actions with lint, typing, unit tests, API integration and E2E smoke tests; avoid storing credentials in the repository.
- **Deployment:** document an inexpensive deployment path; do not purchase hosting or access credentials without explicit permission.

Codex may propose a clearly better coherent stack before implementation, but **must not silently replace scientific Python/WNTR or introduce proprietary paid infrastructure**. Keep the app operational offline/local during development.

### Suggested domain model (to be refined before schema migrations)

`Organization`, `User`, `Role`, `Permission`, `Zone`, `Junction`, `PipeSegment`, `PipeMaterial`, `SupplyWindow`, `Device`, `SensorChannel`, `CalibrationRecord`, `Observation`, `HydraulicState`, `AcousticCapture`, `AcousticEstimate`, `EvidenceAssessment`, `Incident`, `IncidentEvent`, `CitizenReport`, `WorkOrder`, `WorkOrderAction`, `RepairEvidence`, `PostRepairVerification`, `SimulationRun`, `Scenario`, `GroundTruth`, `Feedback`, `Attachment`, `Notification`, `AuditLog`.

Every observation should specify `source_type` (`SIMULATION`, `HARDWARE`, `MANUAL`, or appropriate), collection timestamp, units, device identity, quality/freshness, scenario/run ID if synthetic, and immutable ground-truth separation. No direct leak-source truth should enter the inference input.

---

## 10. THREE REPRODUCIBLE SIMULATION ENGINES

**All simulations are software experiments**, not assertions of measured real-world performance. Each has saved config, seed, reproducible output and automated scientific sanity checks.

### 10.1 SIM-HYDRAULICS — pressurized network and supply states

Use WNTR/EPANET to define example village-like water networks: pump/tank, branches, material/diameter lengths, legitimate demand, pressure dependence and leakage as modelled, and operating periods where the solver is valid. Compare flow pressure events under leak vs customer draw-off vs tank filling. Qualify `OFF`, `FILLING`, `STEADY`, `DRAINING` states using an explicit model—be transparent where EPANET cannot model rapid transition dynamics. Provide known-node leak cases, topology variants, false positive/negative tests, and correct units/time windows.

### 10.2 SIM-ACOUSTICS — physical parameter sweeps, not only easy examples

Generate passive leak source signals with tunable level/bandwidth/temporal variation; frequency-dependent attenuation, measured/assumed wave speed, sensor position, transducer response, clipping/noise, different sample phases, correlated pump vibration, environmental disturbances, reflections/multipath, branch ambiguity, multiple sources, different pipe materials and weakening acoustic source at low pressure. Run baseline filtered cross-correlation and GCC-PHAT, then a qualified multi-window decision scheme. Separate test seeds/conditions from any threshold tuning. Report detection recall, accepted fraction, false-location rate, correct-within-distance among all cases and accepted cases, confidence calibration and unresolved counts. Show comparisons without cherry-picking.

### 10.3 SIM-GUARD-5 — five-channel water-path/collector-failure logic

Model simplified water-arrival time/volume or transfer between `A`, `B`, `C`, `EXT`, `BYPASS` with explicitly **assumed** transport/migration paths, delay, evaporation/retention, sensor thresholds, noise, sensor faults and blocked drain. Add external rain/spray, dew-like environmental states, true joint seepage and dry cases. Compare baseline single-pad detector vs unguarded multizone vs full guarded/bypass/physical service-challenge logic. **Do not represent toy transfer coefficients as validated CFD or physical separation geometry.** A model can demonstrate logical advantage under assumptions but does not prove the actual manufactured collar works.

### 10.4 Integrated scenario engine and scientific controls

A scenario orchestrator creates ground truth privately then emits only appropriately limited **observations** to the application's ingestion path. Require run ID, deterministic seed, config hash, scenario version, event timestamps, provenance and repeatable evaluation. Tests must explicitly prevent ground-truth contamination into the detector. Use blind holdout cases. Record data separately as `TRUTH` and `OBSERVED` and prevent client APIs from leaking truth in regular accounts.

**Mandatory scenario catalogue:** no leak; weak pinhole; longitudinal slit; loose joint; fully pressurized leak; low/zero pressure; filling/draining; normal customer draw; pump noise; external rain; condensation; blocked collector path; electrode disconnect; stale sensor; multiple leaks; mixed material/branch; acoustic insufficient signal; false confident correlation case; repair attempted but incomplete; successfully repaired case.

**Metrics:** event detection precision/recall, false alarm events per observation hours/cycles, `UNRESOLVED`/coverage rate, wrong-confident location among accepted estimates, median and 95th-percentile position error with clearly defined denominator, incident handling latency, repair workflow completion, resource and power *estimates* distinctly from measurements.

### Suggested acceptance targets (aspirations, never reported achievements)

- Under a predeclared controlled physical trial that does **not yet exist**, GUARD-5 aims for 90% or better local joint-event recognition and no more than 5% misleading leak declarations on appropriate holdout environmental controls, while identifying specified seeded collector blockages.
- On a future bounded, qualified, roughly 10–15 m simple physical segment, acoustic accepted estimates aspire to at least 80% within 1 m *with useful coverage and low confident-error rate*. No such physical results exist.
- Simulations should report honest outcomes (including failures), *not* be tuned to produce these goals automatically.

---

## 11. HARDWARE DESIGN FILES TO PREPARE, WITHOUT CLAIMING BUILD

### 11.1 Proposed demonstration rig (not presently authorized to purchase/build)

- Approximately 10–15 m modular, conservative-pressure PVC/HDPE line with suitable rated fittings, pump, tank, bypass/relief and leak discharge collection.
- 12/24 V appropriately sized pump using pressure-flow curve, 60–80 L tank, closed-loop clean nonpotable rig, rated fittings/valves, gauge, protective electrical isolation, no unsafe deadheading or dry run.
- Approximately six controllable leak/dummy stations of different geometry; unknown true leak selected independently of inference software.
- A collar at an eligible exposed joint and two accessible acoustic endpoints. Optional mixed-material branch for intentionally ambiguous stress tests.
- Initial hypothetical operating conditions around 0.5, 1.0 and 1.5 bar with documented component-rated safety margins—not commercial field performance.
- Flow sensors may track *bulk* flow only; measure tiny leak truth by controlled water collection and weighing, because common YF-S201-type devices are not accurate micro-leak reference meters.

### 11.2 CAD and electronics deliverables

- FreeCAD-compatible manufacturing drawings of split GUARD-5 collar, A/B/C inner channel geometry, outside `EXT` guard, physically distinct `BYPASS` path, replaceable liners, gaskets, drains, mount and service challenge ports. Clearly mark unresolved pipe diameter/gasket tolerance until constrained.
- KiCad schematics/PCB design for slow sensing and matched acoustic front ends, proper input and power protection, two ADS1115 module addresses, clock-compatible stereo ADC, I²S wiring, SD logging, connectors.
- Firmware architectures for ESP32 devices and automated simulation/HIL stubs; board-level pin maps, serial protocol, sample clock plan, calibration state and error-code tables.
- Stepwise power budget and service/field cost model clearly separated from the complete demonstration rig cost.
- Safety review and potable-water boundary: NO unauthorized field insertion, NO pressure load transferred to printed collar, NO automatic violent municipal valve closures, NO hydraulic shock experiments.

**Do not invent actual finished CAD models, Gerbers, component test measurements or physical electrical validations if only theoretical requirements exist.**

---

## 12. MATERIALS COST CEILING AND BOM ALLOCATION

**Maximum allowed purchased components and materials for full potential SIH bench demo: INR 60,000.** Plan currently totals **INR 56,750** including INR 5,000 contingency; remaining cap headroom INR 3,250. This is **not** the cost per village installation and **not** a guaranteed reimbursement from SIH.

| Group | Specific elements | Planning INR |
|---|---|---:|
| Physical pipeline/safety rig | Pipe, fittings, support, pump, tank, bypass/relief, six leak inserts, small flow reference | 19,900 |
| GUARD-5 | Two-piece collar, 3 isolated collectors, environmental guard, bypass gutter, five electrode channels, manual challenge ports | 4,600 |
| HYDRO-WATCH and slow electronics | Two ESP32-class boards, two ADS1115 modules, two pressure sensors, two bulk-flow modules, RH/temperature, storage, conditioning | 8,800 |
| HYDRO-EAR | Two pickups, two matched preamps/filters, stereo PCM1808-class ADC, shielded cabling/mounts, alternative pickup allowance | 12,550 |
| Common fabrication/interface | Power protection, enclosures, PCB fabrication, connectors, fittings and cables | 5,900 |
| Contingency | Freight/GST changes, replacement sensors and failed acoustic components | 5,000 |
| **TOTAL** | **Only planned hardware/material purchases, not labor, research publishing, laptop, software services or filmmaking expenses** | **56,750** |

The detailed 26-line internal proposed BOM is stored separately in a previous engineering blueprint. Values and exact components must be cross-checked to prevent category overlap, arithmetic mistakes, unreliable pressure rating or false accuracy requirements. **No spending / ordering without explicit human approval.** Savings are welcome only if detection credibility and safety are not compromised. Avoid adding expensive research-grade instruments merely because they look advanced.

**Deployment economics:** A regional portable acoustic pair is reusable across many sectors; fixed collars are selective and only monitor local exposed joints. A village/utility cost requires separately modelled cost per node, installation/site service, batteries/connectivity, maintenance, equipment life and kilometers actually observable. Do not use INR 56,750 as “cost per sensor.”

---

## 13. REAL SCIENTIFIC PRIOR ART AND COMPETITOR LANDSCAPE

**We must be honest about novelty.** Basic flow/pressure alarms, wetness pads, more than one moisture sensor at a fitting, acoustic time-difference localization, hydrophones, PVDF, IoT and repair dashboards already exist.

**Relevant primary prior art:**

- Multi-moisture fitting detector with A/B/C and a lower sensor: `https://patents.google.com/patent/CN104819384A/en`. Avoid claiming “we invented multiple moisture sensors on a fitting.”
- Combined acoustic pressure + external strain sensing for leak localization: `https://patents.google.com/patent/US8346492B2/en`. Do not claim fluid/wall combination alone is unprecedented.
- Plastic-pipe acoustic filtering and different sensor modalities: `https://pmc.ncbi.nlm.nih.gov/articles/PMC4004009/`.
- 2026 laboratory study showing realistic longitudinal slits may produce particularly weak leak noise: `https://www.mdpi.com/1424-8220/26/14/4325` (DOI 10.3390/s26144325).
- Commercial advanced hydrophone correlation: `https://en.gutermann-water.com/product/zonescan-hydro/`. Do not claim industrial systems cannot monitor plastic pipes.

**Two GitHub student reference projects (do not copy unlicensed material):**

1. `https://github.com/TECHY-ENTHUSIAST/SIH26254-JalNaadi` — same SIH problem; has Python GCC-PHAT, one-tap wave-speed estimation, EWMA/CUSUM night-flow prototype, FastAPI backend, simulated classifier, and **ESP32 firmware skeletons with missing actual embedded GCC-PHAT function**. README explicitly says no physical validation; 100% synthetic classifier is not field proof. Its code is MIT-licensed in the examined snapshot; inspect the actual license before reuse. We can **independently** develop supply-state-aware adaptive screening, calibrated acoustic correlation and maintenance prioritization.
2. `https://github.com/vidhishabhosalee/AquaSense` — website/dashboard-focused concept; examined snapshot had a README and compiled website but no equally demonstrated sensor firmware/physical validation. No licensing permission was established in the examined repository; do not copy code/visual assets without explicit license/permission.

**Our credible differentiation hypothesis:** an inexpensive, protected, physically compartmentalized and maintenance-challengeable five-channel joint collar able to provide evidence of some wetness-source and collection-path failures; partnered with supply-state-aware hydraulic monitoring, shared-clock qualified acoustic measurement on eligible spans and verified repair workflow. Our ***current global patent-level novelty is not established***. Prior independent discussion gave a conservative ~4/10 global physical novelty assessment, with higher potentially useful system differentiation—these are subjective research judgments, not certified scores. A strong claim requires blind comparisons, specific mechanical claim chart and later professional patent review. The assistant must never pronounce “9/10 patent novelty” as a fact.

---

## 14. EVIDENCE STATUS AND WHAT MUST NOT BE MISREPRESENTED

**Actually documented in existing user materials:** Six-slide submitted presentation; a range of past simulation/design reports; independently generated research and source-code packages; some historic automated tests. They are **not automatically present in this fresh Codex repository**. Codex should ask to receive/source them if required, and inspect before saying anything was independently reproduced.

**Presently NOT established:** Fabricated working collar; real weak-leak measurements; field detection precision/recall; battery lifespan measured; industrial potable-water compliance; village-wide automatic pinpointing; validated improvement over commercial leak correlation; full-stack website implementation in a new team repository; completed CAD that has been manufactured; winning probability or SIH score.

**Owner's current development choice:** Prepare a **fully functional website, reproducible scientific simulations, GitHub repository, complete digital mechanical/electronics designs and a 2–3 minute polished animated explanation** before the final PPT. The owner **does not want to build a physical prototype now**. Respect this while prominently retaining “physical prototype/hardware validation: future, not done” in the submission plan. Since SIH problem category is Hardware, proactively show this as a competition risk rather than treating video as a substitute for physical validation.

**Video requirements:** ~2–3 min engaging, technically credible, professional animation with realistic pipe/drip physics and correct CAD geometry if available; concise problem, GUARD-5 mechanism, WATCH pressure-state logic, EAR-PAIR qualified location, website work order, technician repair and verification. Mark *CONCEPT ANIMATION / SIMULATED EXAMPLE* rather than implying filmed working hardware. Actual website screen captures can be genuine software demonstration while containing simulated sensor records.

---

## 15. DELIVERY WORKFLOW, TESTS AND GITHUB GOVERNANCE

### Proposed repository identity

`HYDROOVERITY-SIH26254` (ask owner for exact GitHub account/organization only when repository creation is authorized).

### Proposed monorepo layout

```text
HYDROOVERITY-SIH26254/
├── AGENTS.md                    # Compact durable Codex instructions
├── README.md                    # Project, evidence status, quick start
├── LICENSE                      # Choose explicitly; do not silently license
├── .github/
│   ├── workflows/               # Continuous integration
│   └── ISSUE_TEMPLATE/          # Bugs, engineering tasks, mentor feedback
├── apps/
│   └── web/                     # Public site + authorized portals
├── services/
│   └── api/                     # Auth, domain operations, observation ingest
├── packages/
│   └── schemas/                 # Shared API contracts if helpful
├── simulations/
│   ├── hydraulics/              # WNTR/EPANET
│   ├── acoustics/               # DSP/uncertainty/baselines
│   ├── guard5/                  # Water paths, sensor faults
│   └── scenarios/               # Reproducible truth/observation generation
├── hardware/
│   ├── cad/                     # GUARD-5 models/drawings
│   ├── electronics/             # KiCad and pin assignment
│   ├── firmware/                # Buildable future device source
│   └── bom/                     # Components and quotation ledger
├── animation/                   # Storyboard, assets, video scripts
├── docs/
│   ├── context/                 # This authoritative project brief
│   ├── requirements/            # SIH traceability and acceptance criteria
│   ├── architecture/            # Decisions, diagrams, threat model
│   ├── evidence/                # Simulation vs test vs unknown ledger
│   ├── research/                # Prior art and external sources
│   └── testing/                 # Plans and outcomes
├── scripts/                     # Developer setup and run commands
├── tests/                       # System/integration tests
├── docker-compose.yml
└── .env.example
```

**Important:** This is a proposed structure to review, not an instruction to create it during onboarding. Do not copy 100 unused placeholder directories simply to appear complete; stage creation around actual milestones while preserving the architecture.

### Completion contract

A feature is finished only when it is actually wired to the backend/database; has loading/error/empty states; enforces permissions; has automated tests; includes useful documentation; does not fabricate sensor provenance; and is visible in the actual worker/engineer/citizen workflow. Every pull request/task should report files changed, commands run, test results, known limitations and next action. Avoid claiming tests passed unless executed.

### Work stages (execute only with new explicit owner instruction)

1. **Repository setup:** GitHub access/remote/branch, README, context, AGENTS.md, issue labels, CI basics, threat/evidence notes. This is the FIRST TASK after onboarding.
2. **Data model + backend foundation:** auth, roles/tenants, schema, events, citizen reports, work orders, sensor/observations, audit.
3. **Web UX and real workflows:** landing + multiple portals, maps, responsive worker/citizen experiences, real persistence.
4. **Scientific simulators:** hydraulics, acoustic and GUARD-5 scenario/metrics code; backend ingestion; blind simulation UI.
5. **Finish operations:** dashboards, reports, verification, live synthetic stream, offline robustness, feedback-to-issue pipeline.
6. **Digital hardware:** CAD, electronics, firmware design and document linked bill of materials.
7. **Quality, security and evidence audit:** E2E tests, false-claim review, source traceability, accessibility and performance.
8. **Explanation video + final PPT:** storyboard, real app recording, CAD-based mechanism animation and honest results.

Do not attempt to implement everything in one Codex turn. Propose short, testable milestones with acceptance criteria. Never run GitHub writes or paid deployments just because the context describes future steps.

---

## 16. WHAT CODEX SHOULD ANSWER AFTER READING THIS FILE — NO CHANGES YET

Please respond concisely but substantively, in this exact order:

1. **Project comprehension:** Explain HYDROOVERITY, who benefits, what physical evidence WATCH/GUARD-5/EAR-PAIR capture, and how verification closes the loop.
2. **Honest status:** Name exactly what is designed/simulated versus unbuilt, including the user's digital-only immediate plan and hardware-category risk.
3. **Nonnegotiable constraints:** Team/project identity, five collar channels, separate environmental/bypass, intermittent supply, one acoustic sampling clock, uncertainty/abstention, INR 60,000 materials ceiling, no fabricated hardware performance.
4. **Architecture recommendations:** Confirm or flag any *material* implementation contradictions. Do NOT redesign the fundamental concept without owner approval.
5. **GitHub readiness:** State which GitHub account / repo folder or access detail you will need in the next step, and the smallest safe action sequence once explicitly authorized.
6. **Minimal necessary integrations:** Confirm whether GitHub is accessible in this Codex session; suggest only other integrations necessary for the *upcoming* work, not a dozen optional plugins.
7. End with: **“I understand HYDROOVERITY. I have not created or modified anything. I am ready for the separate GitHub setup instruction.”** Only say this if true.

**Do not generate code, create folders, run git init, create the GitHub repository, install dependencies, publish pages, write files, or spend money in this onboarding response.**

---

## OPTIONAL SOURCE MATERIALS THE OWNER MAY ATTACH LATER

- Submitted six-slide SIH PDF: `HYDROOVERITYSIH2026FINAL20261005173117.pdf`.
- Most recent frozen-design engineering brief: `HYDROOVERITY_CHIEF_ENGINEER_REDESIGN_V1_60K.md` — use its CONTENT but do not repeat a numbered version label in the project name.
- Current theoretical under-INR-60k context: `HYDROOVERITY_UNDER_60000_THEORETICAL_FINAL_DESIGN.md`.
- Historical research, calculations, independent AI reviews and model source files if needed for substantive audit; do not assume Codex has them unless attached/available.
- SIH26254 problem statement pasted in conversation, included verbatim above.

**END OF AUTHORITATIVE HYDROOVERITY ONBOARDING BRIEF.**
