"""Local fake-provider fault injection only; zero external requests or real delivery."""

from dataclasses import replace
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from hydro.errors import Problem
from hydro.external_provider_boundary import (
    ExternalIntent,
    PlanningState,
    ProviderResult,
    SyntheticRetryPolicy,
    next_attempt_number,
    plan_attempt,
    resolve_external_provider,
)

NOW = datetime(2026, 10, 20, tzinfo=UTC)


def intent():
    return ExternalIntent(uuid4(), uuid4(), uuid4(), uuid4(), uuid4(), "SERVICE_PROGRESS")


def policy(retry_unknown=False):
    return SyntheticRetryPolicy(
        "SYNTHETIC_FAKE_PROVIDER_ONLY", "SYNTHETIC-FAULT-INJECTION", (2, 5), retry_unknown
    )


class LocalFake:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = []
        self.possible_effects = 0

    def send(self, value, operation_key):
        self.calls.append(operation_key)
        outcome = self.outcomes.pop(0)
        if outcome in {ProviderResult.ACKNOWLEDGED, ProviderResult.UNKNOWN}:
            self.possible_effects += 1
        return outcome


def exercise(fake, retry_policy):
    value, attempts, at, risk = intent(), 0, NOW, False
    while (number := next_attempt_number(attempts)) is not None:
        outcome = fake.send(value, value.notification_id)
        attempts += 1
        result = plan_attempt(outcome, number, at, retry_policy, risk)
        risk = result.duplicate_risk
        if result.retry_at is None:
            return result, attempts
        at = result.retry_at
    raise AssertionError("The final attempt must not schedule another call")


@pytest.mark.parametrize(
    "name", ["email", "sms", "push", "https://unrelated.invalid", "", "python:plugin"]
)
def test_every_external_provider_remains_disabled(name):
    with pytest.raises(Problem) as error:
        resolve_external_provider(name)
    assert error.value.status == 503 and error.value.code == "EXTERNAL_DELIVERY_DISABLED"


def test_three_total_attempts_and_explicit_delays():
    fake = LocalFake([ProviderResult.RETRYABLE_REJECTION] * 3)
    result, attempts = exercise(fake, policy())
    assert attempts == len(fake.calls) == 3
    assert len(set(fake.calls)) == 1  # Stable opaque provider operation key.
    assert result.state == PlanningState.FAILED and result.retry_at is None
    assert next_attempt_number(3) is None
    assert (
        plan_attempt(ProviderResult.RETRYABLE_REJECTION, 1, NOW, policy()).retry_at - NOW
    ).total_seconds() == 2
    assert (
        plan_attempt(ProviderResult.RETRYABLE_REJECTION, 2, NOW, policy()).retry_at - NOW
    ).total_seconds() == 5


def test_missing_policy_stops_after_first_attempt():
    fake = LocalFake([ProviderResult.RETRYABLE_REJECTION])
    result, attempts = exercise(fake, None)
    assert attempts == 1 and result.state == PlanningState.POLICY_REQUIRED


@pytest.mark.parametrize("retry_policy", [None, policy(False)])
def test_unknown_provider_effect_requires_review_without_explicit_retry(retry_policy):
    fake = LocalFake([ProviderResult.UNKNOWN])
    result, attempts = exercise(fake, retry_policy)
    assert attempts == 1 and fake.possible_effects == 1
    assert result.state == PlanningState.UNKNOWN_REVIEW and result.duplicate_risk


def test_explicit_synthetic_unknown_retry_can_duplicate_and_ack_is_not_delivery():
    fake = LocalFake([ProviderResult.UNKNOWN, ProviderResult.ACKNOWLEDGED])
    result, attempts = exercise(fake, policy(True))
    assert attempts == 2 and fake.possible_effects == 2
    assert result.duplicate_risk and result.state == PlanningState.PROVIDER_ACKNOWLEDGED
    assert result.safe_code == "NOT_DELIVERY_OR_READ_PROOF"
    assert "DELIVERED" not in {state.value for state in PlanningState}
    assert "READ" not in {state.value for state in PlanningState}


def test_unknown_at_attempt_limit_remains_unknown():
    fake = LocalFake([ProviderResult.UNKNOWN] * 3)
    result, attempts = exercise(fake, policy(True))
    assert attempts == 3 and result.state == PlanningState.UNKNOWN_REVIEW


def test_safe_template_accepts_no_address_or_untrusted_message():
    value = intent()
    assert "Open your service timeline" in value.safe_message
    with pytest.raises(ValueError):
        replace(value, event_category="UNTRUSTED_CUSTOMER_MESSAGE")
    with pytest.raises(ValueError):
        replace(value, organization_id="caller-controlled")
    with pytest.raises(TypeError):
        ExternalIntent(**{**value.__dict__, "destination": "unverified@example.invalid"})


@pytest.mark.parametrize(
    "changes",
    [
        {"delays": (0, 1)},
        {"delays": (1,)},
        {"delays": (True, 2)},
        {"delays": (1, 86401)},
        {"policy_reference": "APPROVED-BY-NOBODY"},
        {"policy_reference": None},
        {"delays": [2, 5]},
        {"provenance": "PRODUCTION"},
        {"retry_unknown": 1},
    ],
)
def test_rejects_unreviewed_or_malformed_synthetic_policy(changes):
    with pytest.raises(ValueError):
        replace(policy(), **changes)


@pytest.mark.parametrize("number", [0, 4, True, -1])
def test_rejects_invalid_attempt_number(number):
    with pytest.raises(ValueError):
        plan_attempt(ProviderResult.RETRYABLE_REJECTION, number, NOW, policy())


def test_naive_time_is_rejected_and_uncertainty_survives_later_failure():
    with pytest.raises(ValueError):
        plan_attempt(ProviderResult.RETRYABLE_REJECTION, 1, datetime(2026, 10, 20), policy())
    result = plan_attempt(ProviderResult.PERMANENT_REJECTION, 2, NOW, policy(), prior_unknown=True)
    assert result.state == PlanningState.UNKNOWN_REVIEW and result.duplicate_risk
    exhausted = plan_attempt(
        ProviderResult.RETRYABLE_REJECTION, 3, NOW, policy(), prior_unknown=True
    )
    assert exhausted.state == PlanningState.UNKNOWN_REVIEW and exhausted.retry_at is None


@pytest.mark.parametrize("category", [None, {}, ["SERVICE_PROGRESS"]])
def test_untyped_template_data_is_rejected(category):
    with pytest.raises(ValueError):
        replace(intent(), event_category=category)


@pytest.mark.parametrize(
    "outcome,expected",
    [
        (ProviderResult.ACKNOWLEDGED, PlanningState.PROVIDER_ACKNOWLEDGED),
        (ProviderResult.PERMANENT_REJECTION, PlanningState.FAILED),
    ],
)
def test_terminal_provider_reply_never_schedules_another_call(outcome, expected):
    fake = LocalFake([outcome])
    result, attempts = exercise(fake, policy())
    assert attempts == 1 and result.state == expected and result.retry_at is None


def test_local_timeout_after_side_effect_does_not_prove_failure_or_resend():
    class TimeoutAfterEffect:
        calls = 0

        def send(self, value, key):
            self.calls += 1
            # Simulate the provider accepting before the response is lost.
            raise TimeoutError("SYNTHETIC timeout after possible provider effect")

    fake = TimeoutAfterEffect()
    value = intent()
    with pytest.raises(TimeoutError):
        fake.send(value, value.notification_id)
    result = plan_attempt(ProviderResult.UNKNOWN, 1, NOW)
    assert fake.calls == 1 and result.state == PlanningState.UNKNOWN_REVIEW
    assert result.retry_at is None and result.duplicate_risk


def test_recovered_attempt_budget_does_not_restart_at_one():
    # The actual in-app worker has separate PostgreSQL/process lease tests.
    # This planner merely consumes a persisted count supplied by a future adapter.
    attempts_made = 2
    assert next_attempt_number(attempts_made) == 3
    result = plan_attempt(ProviderResult.RETRYABLE_REJECTION, 3, NOW, policy())
    assert result.state == PlanningState.FAILED and result.retry_at is None
    assert next_attempt_number(3) is None
