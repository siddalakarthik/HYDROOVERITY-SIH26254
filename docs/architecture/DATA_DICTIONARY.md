# Proposed data dictionary

Status: conceptual entities and invariants only, not a database schema or migration. IDs, SQL types, indexes, retention, relationship cardinalities and exact enums require M02 review. All tenant-owned relationships must reject cross-organization references.

| Entity | Purpose / proposed information |
| --- | --- |
| Organization | Utility tenant, settings, zones and retention policies |
| User | Identity/contact, credential references, account/recovery state; private fields restricted |
| Role / Permission | Tenant-scoped grants for admin, engineer, supervisor, technician, citizen |
| WaterZone | Monitored/operated sector, supply/demand context and access boundaries |
| Junction / PipeSegment / PipeMaterial | Pipe graph, endpoints, geometry, length/metres, diameter, material and access/path confidence |
| SupplyWindow / HydraulicState | Observed operating intervals and OFF/FILLING/STEADY/DRAINING/UNKNOWN with reasons/freshness |
| Device / SensorChannel | Station and independent channel identity, type/units, provisioning, health, hardware config |
| CalibrationRecord | Method, date, validity, reference, uncertainty and source artifact |
| SensorObservation | Measured/synthetic value or capture reference with collection/receipt time, units, identity, provenance, quality and calibration |
| AcousticCapture | Stereo waveform artifact, sample rate/clock, channel calibration, clipping/interface/pressure and path metadata |
| LeakLocationEstimate | Eligible path/endpoints, lag sign, speed assumptions, candidate interval(s), uncertainty, method and abstention reason |
| EvidenceAssessment / EvidenceRecord | Observation references, status/reasons, competing explanations, method/config version and qualified confidence |
| Incident / IncidentEvent | Reviewed concern, zone/location bounds, priority/ownership; append-only event history |
| WorkOrder / WorkOrderAction | Assignment, authorized lifecycle, checklist, timestamps, deadlines and technician evidence |
| Repair / RepairEvidence | What was repaired, by whom/when, notes/photos and related incident/order |
| VerificationRecord | Before/after observation sets, comparability rationale, reviewer and verified/reopened/not-verifiable outcome |
| CitizenComplaint | Reporter's own service/leak concern, coarse location, consented attachments, status and duplicate links |
| Feedback | Actor, severity, linked issue/context, assignment/status, resolution and release reference |
| SimulationRun | Seed, config/hash, scenario/algorithm versions, environment/commit, output artifacts and provenance |
| SimulationScenario | Versioned conditions, generation assumptions and tuning/holdout designation |
| GroundTruth | Restricted actual simulated source/label, separate from inference inputs and ordinary APIs |
| HardwareConfiguration | Versioned board/sensor/channel mapping, clock/firmware/calibration and assembly references |
| Attachment | Ownership, consent/classification, checked type/size, storage/hash and authorization |
| Notification | Scoped recipient/event, channel, attempt/delivery outcome and deduplication |
| AuditLog | Actor/tenant/action/resource, UTC time and safe metadata for privileged changes |

## Observation provenance contract

At minimum retain `source_type` (SIMULATION, HARDWARE or MANUAL) and a distinct acquisition context (SIMULATION, LABORATORY, FIELD or MANUAL; exact enums provisional). HARDWARE alone must not erase lab-versus-field origin. Include organization/device/channel IDs, collection and receipt UTC timestamps, units/value or artifact reference, quality/freshness, calibration/config reference and optional operator.

Synthetic observations require run/scenario version and config/seed linkage. A manual note attached to a simulated incident does not turn its sensor evidence into field data. Reports/exports must preserve source context. Hardware observations require actual capture provenance, not a simulation toggle.

Ground-truth source position/labels must never appear in detector observation payloads. Access to restricted evaluation truth is separate from ordinary roles and audited. Evidence status is distinct from source: CODE-TESTED describes executed software checks, not a sensor origin or validated leak.

## Outstanding semantics

Choose canonical NOT_VERIFIABLE versus UNVERIFIABLE terminology; separate evidence, incident and task enums. Define water-sector measurement boundaries, comparability, time aggregation, missing data, uncertainty representation, idempotent event IDs, upload retention and conflict policy before migrations. No accuracy or confidence numeric threshold is invented here.
