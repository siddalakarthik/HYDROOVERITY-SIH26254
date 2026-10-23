"""Explicit Pydantic 2 input models matching the approved M02 wire contract."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    @model_validator(mode="before")
    @classmethod
    def database_text(cls, value):
        def inspect(item, key=""):
            if isinstance(item, dict):
                for name, child in item.items():
                    inspect(child, name)
            elif isinstance(item, list):
                for child in item:
                    inspect(child, key)
            elif (
                isinstance(item, str) and key not in {"password", "new_password"} and "\x00" in item
            ):
                raise ValueError("NUL is not supported in persisted text")

        inspect(value)
        return value


class Register(Input):
    utility_slug: str = Field(max_length=80, pattern="^[a-z0-9-]+$")
    email: str = ...
    display_name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=15, max_length=128)


class Login(Input):
    email: str = ...
    password: str = Field(min_length=1, max_length=128)


class Recovery(Input):
    email: str = ...


class Reset(Input):
    token: str = Field(min_length=32, max_length=200)
    new_password: str = Field(min_length=15, max_length=128)


class TokenAction(Input):
    token: str = Field(min_length=32, max_length=200)


class ProfilePatch(Input):
    display_name: str = Field(min_length=1, max_length=120)


class DemandAccounting(Input):
    outflow_includes_customer_demand: bool = ...
    storage_observed: bool = ...
    notes: str = Field(max_length=2000)


class ZoneWrite(Input):
    name: str = Field(min_length=1, max_length=150)
    demand_boundary_version: str = Field(max_length=80)
    demand_accounting: DemandAccounting = ...


class PointGeometry(Input):
    type: Literal["Point"] = ...
    coordinates: list[float] = Field(min_length=2, max_length=2)


class JunctionWrite(Input):
    zone_id: UUID = ...
    external_ref: str = Field(max_length=80)
    geometry: PointGeometry = ...
    topology_quality: str = Field(max_length=40)


class LineGeometry(Input):
    type: Literal["LineString"] = ...
    coordinates: list[list[float]] = Field(min_length=2, max_length=10000)


class PipeWrite(Input):
    zone_id: UUID = ...
    from_junction_id: UUID = ...
    to_junction_id: UUID = ...
    geometry: LineGeometry = ...
    material: str = Field(max_length=80)
    diameter_mm: float = Field(gt=0)
    path_length_m: float | None = Field(gt=0)
    topology_quality: str = Field(max_length=40)


EvidenceKind = Literal[
    "HYDRAULIC_ANOMALY",
    "LOCAL_JOINT_SUSPICION",
    "ENVIRONMENTAL_WETNESS",
    "COLLECTION_FAILURE",
    "SENSOR_FAILURE",
    "ACOUSTIC_CANDIDATE",
    "INSUFFICIENT_SIGNAL",
    "UNRESOLVED_CAUSE",
]

EvidenceDisposition = Literal["OBSERVED", "SUSPECTED", "QUALIFIED_CANDIDATE", "UNRESOLVED", "FAULT"]


class AssessmentWrite(Input):
    kind: EvidenceKind = ...
    disposition: EvidenceDisposition = ...
    evidence_record_ids: list[UUID] = Field(max_length=100)
    reason: str = Field(min_length=10, max_length=2000)


WorkspaceMode = Literal["SIMULATION", "OPERATIONAL"]


class IncidentWrite(Input):
    zone_id: UUID = ...
    title: str = Field(min_length=5, max_length=200)
    severity: Literal["LOW", "MEDIUM", "HIGH", "URGENT"] = Field(max_length=30)
    assessment_ids: list[UUID] = Field(max_length=100)
    workspace_mode: WorkspaceMode = ...
    simulation_run_id: UUID | None = ...


IncidentStatus = Literal[
    "NEW",
    "UNDER_REVIEW",
    "INVESTIGATION_REQUIRED",
    "ACCEPTED",
    "IN_PROGRESS",
    "VERIFICATION_PENDING",
    "RESOLVED",
    "REOPENED",
    "NOT_VERIFIABLE",
    "DISMISSED",
]


class IncidentTransition(Input):
    target: IncidentStatus = ...
    reason: str = Field(min_length=10, max_length=2000)


class IncidentLinkWrite(Input):
    target_incident_id: UUID = ...
    relation: Literal["DUPLICATE_OF", "RELATED"] = Field(max_length=30)
    reason: str = Field(min_length=10, max_length=2000)


class WorkOrderWrite(Input):
    incident_id: UUID = ...
    priority: Literal["LOW", "MEDIUM", "HIGH", "URGENT"] = Field(max_length=30)
    instructions: str = Field(min_length=5, max_length=4000)
    task_purpose: Literal["REPAIR", "INVESTIGATION", "INSPECTION"] = "REPAIR"


class AssignmentWrite(Input):
    assignee_membership_id: UUID = ...
    due_at: datetime | None = ...
    reason: str = Field(min_length=5, max_length=2000)


class MaterialItem(Input):
    name: str = Field(max_length=120)
    quantity: float = Field(gt=0)
    unit: str = Field(max_length=30)


class WorkerAction(Input):
    operation_id: UUID = ...
    observed_at: datetime = ...
    base_version: int = Field(ge=1)
    assignment_version: int = Field(ge=1)
    note: str = Field(min_length=1, max_length=4000)
    materials: list[MaterialItem] = Field(max_length=30)
    attachment_ids: list[UUID] = Field(max_length=10)


WorkOrderStatus = Literal[
    "CREATED",
    "ASSIGNED",
    "ACCEPTED",
    "IN_PROGRESS",
    "BLOCKED",
    "SUBMITTED_FOR_REVIEW",
    "COMPLETED",
    "CANCELLED",
]


class WorkTransition(Input):
    target: WorkOrderStatus = ...
    reason: str = Field(min_length=5, max_length=2000)


class RepairWrite(Input):
    performed_at: datetime = ...
    description: str = Field(min_length=10, max_length=4000)
    materials: list[MaterialItem] = Field(max_length=30)
    attachment_ids: list[UUID] = Field(max_length=10)


VerificationOutcome = Literal["VERIFICATION_PASSED", "VERIFICATION_FAILED", "NOT_VERIFIABLE"]


class Comparability(Input):
    supply_state_comparable: bool = ...
    pressure_demand_storage_comparable: bool = ...
    calibration_quality_freshness_comparable: bool = ...
    unit_windows_comparable: bool = ...
    limitations: str = Field(max_length=4000)


class VerificationWrite(Input):
    outcome: VerificationOutcome = ...
    before_evidence_record_ids: list[UUID] = Field(max_length=100)
    after_evidence_record_ids: list[UUID] = Field(max_length=100)
    comparability: Comparability = ...
    reason: str = Field(min_length=10, max_length=4000)


class ComplaintWrite(Input):
    category: Literal["VISIBLE_LEAK", "LOW_PRESSURE", "SERVICE_INTERRUPTION"] = Field(max_length=40)
    description: str = Field(min_length=10, max_length=2000)
    coarse_area: str = Field(min_length=2, max_length=200)
    photo_consent: bool = ...
    attachment_ids: list[UUID] = Field(max_length=5)


class ComplaintFollowup(Input):
    description: str = Field(min_length=5, max_length=2000)
    photo_consent: bool = ...
    attachment_ids: list[UUID] = Field(max_length=5)


ComplaintStatus = Literal[
    "RECEIVED",
    "UNDER_REVIEW",
    "INVESTIGATING",
    "ACTION_PLANNED",
    "UPDATE_AVAILABLE",
    "RESOLVED",
    "CLOSED_NO_ACTION",
]


class ComplaintReview(Input):
    public_status: ComplaintStatus = ...
    public_message: str = Field(min_length=5, max_length=1000)
    incident_id: UUID | None = ...
    internal_reason: str = Field(min_length=5, max_length=2000)


class InviteWrite(Input):
    email: str = ...
    role: Literal["ENGINEER", "SUPERVISOR", "TECHNICIAN", "ADMIN"] = Field(max_length=30)


class RoleWrite(Input):
    roles: list[Literal["ENGINEER", "SUPERVISOR", "TECHNICIAN", "ADMIN", "CITIZEN"]] = Field(
        max_length=5
    )
    reason: str = Field(min_length=10, max_length=1000)


class MemberStatusWrite(Input):
    status: Literal["ACTIVE", "SUSPENDED"] = Field(max_length=20)
    reason: str = Field(min_length=10, max_length=1000)
