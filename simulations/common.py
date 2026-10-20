"""Observation-only interfaces and reproducible serialization, never generator truth."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / 'simulations/scenarios/benchmark.json'
CHANNELS = ('COLLAR_A', 'COLLAR_B', 'COLLAR_C', 'COLLAR_EXT', 'COLLAR_BYPASS')
LABEL = 'SIMULATED / CODE-TESTED / PHYSICALLY UNVALIDATED'


def clean(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return clean(value.tolist())
    if isinstance(value, np.generic):
        return clean(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2, allow_nan=False) + '\n', encoding='utf-8', newline='\n')


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(clean(value), sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def config() -> dict:
    return json.loads(CONFIG_PATH.read_text('utf-8'))


@dataclass(frozen=True)
class HydraulicObservation:
    time_s: np.ndarray
    pressure_bar: np.ndarray
    inlet_lpm: np.ndarray
    customer_outlet_lpm: np.ndarray
    pump_on: np.ndarray
    storage_known: np.ndarray
    meter_sigma_lpm: float
    solver_valid: np.ndarray


@dataclass(frozen=True)
class Capture:
    samples: np.ndarray
    sample_rate_hz: int
    span_m: float
    speed_mps: float
    speed_fraction: float
    pressure_bar: float
    eligible_path: bool
    shared_clock: bool
    timing_uncertainty_s: float
    length_uncertainty_m: float = 0.1


@dataclass(frozen=True)
class CollarObservation:
    time_s: np.ndarray
    wet: np.ndarray
    health: tuple[str, ...]
    service_target: int | None
    service_start_s: float | None
    service_end_s: float | None


def readonly(array: np.ndarray) -> np.ndarray:
    array.setflags(write=False)
    return array
