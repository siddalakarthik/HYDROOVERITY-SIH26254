"""Negative checks mutate copies of actual, independently executed acceptance."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))


def pytest_addoption(parser):
    parser.addoption("--acceptance-evidence", action="append", default=[])


@pytest.fixture(scope="session")
def actual_evidence(pytestconfig):
    paths = [Path(p).resolve() for p in pytestconfig.getoption("acceptance_evidence")]
    if len(paths) != 2 or paths[0] == paths[1]:
        raise pytest.UsageError("Provide two independently generated --acceptance-evidence files")
    return tuple(json.loads(path.read_text()) for path in paths)
