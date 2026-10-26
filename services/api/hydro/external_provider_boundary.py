"""Disabled external-provider interface and deterministic synthetic retry decisions.

No adapter, destination lookup, network transport or activation setting exists.
These private planning states are not database/wire notification states.
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Protocol
from uuid import UUID

from .errors import Problem
from .notification_worker import TEMPLATES

MAX_ATTEMPTS = 3


class ProviderResult(StrEnum):
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RETRYABLE_REJECTION = "RETRYABLE_REJECTION"
    PERMANENT_REJECTION = "PERMANENT_REJECTION"
    UNKNOWN = "UNKNOWN"


class PlanningState(StrEnum):
    PROVIDER_ACKNOWLEDGED = "PROVIDER_ACKNOWLEDGED"
    FAILED = "FAILED"
    RETRY_WAIT = "RETRY_WAIT"
    UNKNOWN_REVIEW = "UNKNOWN_REVIEW"
    POLICY_REQUIRED = "POLICY_REQUIRED"


@dataclass(frozen=True)
class ExternalIntent:
    """Opaque references convey no authorization; future adapters must recheck it."""

    organization_id: UUID
    recipient_membership_id: UUID
    notification_id: UUID
    destination_verification_id: UUID
    consent_record_id: UUID
    event_category: str

    def __post_init__(self):
        if (
            not all(
                isinstance(value, UUID)
                for value in (
                    self.organization_id,
                    self.recipient_membership_id,
                    self.notification_id,
                    self.destination_verification_id,
                    self.consent_record_id,
                )
            )
            or not isinstance(self.event_category, str)
            or self.event_category not in TEMPLATES
        ):
            raise ValueError("Opaque UUID references and a safe template are required")

    @property
    def safe_message(self):
        return TEMPLATES[self.event_category]


class ExternalProvider(Protocol):
    def send(self, intent: ExternalIntent, operation_key: UUID) -> ProviderResult: ...


def resolve_external_provider(name: str) -> ExternalProvider:
    # No URL, plugin import, caller-supplied transport or environment opt-in.
    raise Problem(503, "EXTERNAL_DELIVERY_DISABLED", "External provider activation requires review")


@dataclass(frozen=True)
class SyntheticRetryPolicy:
    provenance: str
    policy_reference: str
    delays: tuple[int, int]
    retry_unknown: bool

    def __post_init__(self):
        if (
            self.provenance != "SYNTHETIC_FAKE_PROVIDER_ONLY"
            or not isinstance(self.policy_reference, str)
            or not self.policy_reference.startswith("SYNTHETIC-")
            or not 10 <= len(self.policy_reference) <= 128
            or type(self.delays) is not tuple
            or len(self.delays) != 2
            or not all(type(value) is int and 0 < value <= 86400 for value in self.delays)
            or type(self.retry_unknown) is not bool
        ):
            raise ValueError(
                "Explicit synthetic policy, two delays and unknown-outcome handling required"
            )


@dataclass(frozen=True)
class AttemptPlan:
    state: PlanningState
    safe_code: str
    retry_at: datetime | None
    duplicate_risk: bool


def next_attempt_number(attempts_made: int) -> int | None:
    """Check the budget before any future adapter call, including the first."""
    if type(attempts_made) is not int or not 0 <= attempts_made <= MAX_ATTEMPTS:
        raise ValueError("Invalid attempt count")
    return attempts_made + 1 if attempts_made < MAX_ATTEMPTS else None


def plan_attempt(
    outcome: ProviderResult,
    attempt_number: int,
    at: datetime,
    policy: SyntheticRetryPolicy | None = None,
    prior_unknown: bool = False,
) -> AttemptPlan:
    if (
        not isinstance(outcome, ProviderResult)
        or type(attempt_number) is not int
        or not 1 <= attempt_number <= MAX_ATTEMPTS
        or not isinstance(at, datetime)
        or at.tzinfo is None
        or at.utcoffset() is None
        or type(prior_unknown) is not bool
        or (policy is not None and not isinstance(policy, SyntheticRetryPolicy))
    ):
        raise ValueError("Typed outcome, bounded attempt and aware timestamp required")
    risk = prior_unknown or outcome == ProviderResult.UNKNOWN
    if outcome == ProviderResult.ACKNOWLEDGED:
        return AttemptPlan(
            PlanningState.PROVIDER_ACKNOWLEDGED, "NOT_DELIVERY_OR_READ_PROOF", None, risk
        )
    if outcome == ProviderResult.PERMANENT_REJECTION:
        if risk:
            return AttemptPlan(PlanningState.UNKNOWN_REVIEW, "PRIOR_EFFECT_UNCONFIRMED", None, True)
        return AttemptPlan(PlanningState.FAILED, "PERMANENT_REJECTION", None, risk)
    if outcome == ProviderResult.UNKNOWN:
        if attempt_number == MAX_ATTEMPTS or policy is None or not policy.retry_unknown:
            return AttemptPlan(
                PlanningState.UNKNOWN_REVIEW, "UNCONFIRMED_PROVIDER_EFFECT", None, True
            )
    elif attempt_number == MAX_ATTEMPTS:
        if risk:
            return AttemptPlan(PlanningState.UNKNOWN_REVIEW, "PRIOR_EFFECT_UNCONFIRMED", None, True)
        return AttemptPlan(PlanningState.FAILED, "ATTEMPTS_EXHAUSTED", None, risk)
    if policy is None:
        return AttemptPlan(PlanningState.POLICY_REQUIRED, "RETRY_POLICY_UNCONFIGURED", None, risk)
    return AttemptPlan(
        PlanningState.RETRY_WAIT,
        "UNKNOWN_RETRY_MAY_DUPLICATE" if risk else "PROVIDER_TRANSIENT",
        at.astimezone(UTC) + timedelta(seconds=policy.delays[attempt_number - 1]),
        risk,
    )
