"""No invented passing coverage: valid inputs come from two real 45-test runs."""

from copy import deepcopy

import pytest
import traceability as t


@pytest.fixture
def valid(actual_evidence):
    return deepcopy(actual_evidence[0])


def test_identical_evidence_and_ordering_regenerate_stably(valid):
    tests = t.validate_evidence(valid)
    first = t.matrix(tests)
    reordered = {k: list(reversed(v)) for k, v in reversed(list(tests.items()))}
    assert first == t.matrix(reordered) == t.matrix(tests)
    assert (
        first["canonical_operations"],
        first["implemented_operations"],
        first["deferred_operations"],
    ) == (117, 58, 59)
    assert sum(row["status"] == "MIGRATED" for row in first["tables"]) == 30


def test_independently_executed_acceptance_has_equivalent_coverage(actual_evidence):
    first, second = actual_evidence
    assert first["backend_source_sha256"] == second["backend_source_sha256"]
    assert first["collected"] == second["collected"] >= 45
    assert t.matrix(t.validate_evidence(first)) == t.matrix(t.validate_evidence(second))


@pytest.mark.parametrize("empty", [False, True])
def test_missing_positive_evidence_rejected(valid, empty):
    oid = next(iter(valid["operation_tests"]))
    if empty:
        valid["operation_tests"][oid] = []
    else:
        del valid["operation_tests"][oid]
    with pytest.raises(t.TraceabilityError, match=oid):
        t.validate_evidence(valid)


@pytest.mark.parametrize("oid", ["unknown_operation", "canonical_deferred_operation"])
def test_unknown_or_deferred_operation_rejected(valid, oid):
    if oid == "canonical_deferred_operation":
        enabled = {op["id"] for op in t.OPERATIONS}
        oid = next(op["id"] for op in t.INVENTORY if op["id"] not in enabled)
    valid["operation_tests"][oid] = next(iter(valid["operation_tests"].values()))
    with pytest.raises(t.TraceabilityError, match=oid):
        t.validate_evidence(valid)


@pytest.mark.parametrize(
    "field,value",
    [("permission", "administration.write"), ("status", "DEFERRED"), ("table", "users")],
)
def test_incorrect_operation_metadata_rejected(valid, field, value):
    tests = t.validate_evidence(valid)
    saved = t.matrix(tests)
    oid = saved["operations"][0]["id"]
    saved["operations"][0][field] = value
    with pytest.raises(t.TraceabilityError, match=oid) as error:
        t.check_matrix(saved, tests)
    assert field in str(error.value)


@pytest.mark.parametrize("change", ["missing", "classification", "duplicate"])
def test_table_drift_rejected(valid, change):
    tests = t.validate_evidence(valid)
    saved = t.matrix(tests)
    if change == "missing":
        saved["tables"].pop(0)
    elif change == "classification":
        saved["tables"][0]["status"] = "DEFERRED"
    else:
        saved["tables"].append(deepcopy(saved["tables"][0]))
    with pytest.raises(t.TraceabilityError, match="tables|name"):
        t.check_matrix(saved, tests)


@pytest.mark.parametrize(
    "field,value",
    [
        ("failed", 1),
        ("exit_status", 1),
        ("errors", 1),
        ("skipped", 1),
        ("collected", 44),
        ("collected", True),
        ("collected_tests", []),
        ("fixture_provenance", "INVENTED"),
        ("positive_response_conformance", "FAIL"),
        ("implemented_operations", 59),
        ("deferred_operations", 58),
        ("backend_source_sha256", None),
        ("physical_trials", 1),
        ("field_trials", 1),
    ],
)
def test_invalid_or_failed_acceptance_rejected(valid, field, value):
    valid[field] = value
    with pytest.raises(t.TraceabilityError):
        t.validate_evidence(valid)


@pytest.mark.parametrize(
    "reference",
    [
        "unknown",
        "services/api/tests/test_absent.py::test_absent",
        "services/api/tests/test_auth.py::test_absent",
        "services/api/tests/test_auth.py::test_session_expiry_and_recognized_cleanup[not-executed]",
    ],
)
def test_missing_or_unexecuted_test_reference_rejected(valid, reference):
    oid = next(iter(valid["operation_tests"]))
    valid["operation_tests"][oid] = [reference]
    with pytest.raises(t.TraceabilityError):
        t.validate_evidence(valid)


@pytest.mark.parametrize("field", ["permission", "request", "response", "path", "table"])
def test_genuine_canonical_change_has_actionable_failure(valid, monkeypatch, field):
    tests = t.validate_evidence(valid)
    saved = t.matrix(tests)
    changed = deepcopy(t.INVENTORY)
    changed[0][field] = "deliberately-invalid-contract"
    monkeypatch.setattr(t, "INVENTORY", changed)
    with pytest.raises(t.TraceabilityError, match=changed[0]["id"]) as error:
        t.check_matrix(saved, tests)
    assert field in str(error.value)


def test_counts_and_order_only_drift_are_not_silently_accepted(valid):
    tests = t.validate_evidence(valid)
    saved = t.matrix(tests)
    saved["implemented_operations"] += 1
    with pytest.raises(t.TraceabilityError, match="implemented_operations"):
        t.check_matrix(saved, tests)
    saved = t.matrix(tests)
    saved["operations"].reverse()
    assert t.describe_drift(saved, t.matrix(tests))["classification"] == "ORDERING_ONLY"
    with pytest.raises(t.TraceabilityError, match="ORDERING_ONLY"):
        t.check_matrix(saved, tests)


def test_evidence_diff_identifies_added_removed_reference(valid):
    tests = t.validate_evidence(valid)
    generated = t.matrix(tests)
    saved = deepcopy(generated)
    oid = "authentication_post_auth_login"
    row = next(op for op in saved["operations"] if op["id"] == oid)
    reference = (
        "services/api/tests/test_auth.py::test_reset_login_race_never_leaves_old_password_session"
    )
    assert reference in row["positive_response_tests"]
    row["positive_response_tests"].remove(reference)
    drift = t.describe_drift(saved, generated)
    assert drift["classification"] == "POSITIVE_RESPONSE_EVIDENCE"
    assert drift["operations"] == [
        {"id": oid, "added_tests": [reference], "removed_tests": [], "metadata": {}}
    ]
    assert not drift["counts"] and not drift["tables"]
    with pytest.raises(t.TraceabilityError, match=reference):
        t.check_matrix(saved, tests)
