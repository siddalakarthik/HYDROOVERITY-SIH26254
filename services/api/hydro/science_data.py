"""Fail-closed observation catalogue boundary. No scientific generator imports."""

import hashlib
import json
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, model_validator

LABEL = "SIMULATED / CODE-TESTED / PHYSICALLY UNVALIDATED"
Number = FiniteFloat | None
Series = Annotated[list[Number], Field(min_length=1, max_length=8192)]
Flags = Annotated[list[bool], Field(min_length=1, max_length=8192)]


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Common(Strict):
    label: Literal["SIMULATED / CODE-TESTED / PHYSICALLY UNVALIDATED"]
    limitations: Annotated[
        list[Annotated[str, Field(max_length=500)]], Field(min_length=1, max_length=8)
    ]


class Urgent(Strict):
    time_s: FiniteFloat
    reason: Literal["MISSING_SENSOR_DATA", "PRESSURE_COLLAPSE_REVIEW"]


class Watch(Common):
    module: Literal["HYDRO-WATCH"]
    time_s: Series
    pressure_bar: Series
    inlet_lpm: Series
    customer_outlet_lpm: Series
    pump_on: Flags
    storage_known: Flags
    solver_valid: Flags
    meter_sigma_lpm: FiniteFloat
    state: list[Literal["UNKNOWN", "OFF", "DRAINING", "FILLING", "STEADY"]]
    qualified_outcome: list[
        Literal["NO_PERSISTENT_ANOMALY", "UNEXPLAINED_LOSS_SUSPECTED", "UNRESOLVED"]
    ]
    fixed_alarm: Flags
    watch_alarm: Flags
    residual_lpm: Series
    urgent_events: Annotated[list[Urgent], Field(max_length=8192)]
    threshold_lpm: FiniteFloat

    @model_validator(mode="after")
    def aligned(self):
        for name in (
            "pressure_bar",
            "inlet_lpm",
            "customer_outlet_lpm",
            "pump_on",
            "storage_known",
            "solver_valid",
            "state",
            "qualified_outcome",
            "fixed_alarm",
            "watch_alarm",
            "residual_lpm",
        ):
            if len(getattr(self, name)) != len(self.time_s):
                raise ValueError("Hydraulic sample lengths differ")
        return self


class Guard(Common):
    module: Literal["GUARD-5"]
    channels: list[Literal["A", "B", "C", "EXT", "BYPASS"]]
    time_s: Series
    wet: list[Annotated[list[bool], Field(min_length=5, max_length=5)]]
    health: Annotated[list[Literal["UNKNOWN"]], Field(min_length=5, max_length=5)]
    outcome: Literal[
        "LOCAL_SUSPECT",
        "ENVIRONMENTAL_OR_AMBIGUOUS",
        "COLLECTION_UNRESOLVED",
        "NO_WETNESS_UNKNOWN_HEALTH",
        "SERVICE_TEST",
    ]
    local_suspect: bool
    blockage_suspected: bool
    service: Literal["NOT_PERFORMED", "RESPONSE_OBSERVED", "COLLECTION_OR_SENSOR_UNRESOLVED"]
    reference_pad_alarm: bool
    reference_multizone_alarm: bool

    @model_validator(mode="after")
    def channels_and_samples(self):
        if self.channels != ["A", "B", "C", "EXT", "BYPASS"] or len(self.wet) != len(self.time_s):
            raise ValueError("Exactly five aligned channels are required")
        return self


class Ear(Common):
    module: Literal["HYDRO-EAR"]
    time_s: Series
    waveforms: Annotated[list[Series], Field(min_length=2, max_length=2)]
    preview_stride: Annotated[int, Field(ge=1, le=32)]
    sample_rate_hz: Literal[4096]
    shared_clock: bool
    eligible_path: bool
    span_m: Annotated[FiniteFloat, Field(gt=0, le=100)]
    assumed_speed_mps: Annotated[FiniteFloat, Field(gt=0)]
    speed_fraction: Annotated[FiniteFloat, Field(ge=0, lt=1)]
    timing_uncertainty_s: Annotated[FiniteFloat, Field(ge=0)]
    pressure_bar: FiniteFloat
    correlation_lag_s: Series
    correlation: Series
    outcome: Literal[
        "UNRESOLVED",
        "INVALID_PATH",
        "NO_PRESSURE",
        "INVALID_CAPTURE",
        "INSUFFICIENT_SIGNAL",
        "QUALIFIED_CANDIDATE",
    ]
    interval_m: Annotated[list[FiniteFloat], Field(min_length=2, max_length=2)] | None
    peak_correlation: Number
    peak_ratio: Number

    @model_validator(mode="after")
    def aligned(self):
        if any(len(row) != len(self.time_s) for row in self.waveforms):
            raise ValueError("Waveform samples differ")
        if len(self.correlation) != len(self.correlation_lag_s):
            raise ValueError("Correlation samples differ")
        if (self.outcome == "QUALIFIED_CANDIDATE") != (self.interval_m is not None):
            raise ValueError("Only qualified candidates have intervals")
        if self.interval_m and not 0 <= self.interval_m[0] <= self.interval_m[1] <= self.span_m:
            raise ValueError("Interval outside eligible span")
        return self


class Verify(Common):
    module: Literal["HYDRO-VERIFY"]
    outcome: Literal["PASSED", "FAILED", "NOT_VERIFIABLE"]
    before_residual_lpm: FiniteFloat
    after_residual_lpm: Number
    watch: Watch
    ear: Ear
    guard: Guard


class Case(Strict):
    code: Annotated[
        str,
        Field(
            pattern=r"^(H\d{2}|A\d{2}|G\d{2}-(unfavorable|nominal|favorable)|V-(comparable_repair|missing_post_evidence|incomplete_repair))$"
        ),
    ]
    name: Annotated[str, Field(min_length=1, max_length=150)]
    data: Annotated[Watch | Guard | Ear | Verify, Field(discriminator="module")]


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def load_catalogue(path, expected_digest):
    from .config import ROOT

    location = Path(path)
    pins = json.loads((ROOT / "data/schemas/m06-observation-pins.json").read_text("utf-8"))
    if location.is_dir():
        index = json.loads((location / "catalogue.json").read_text("utf-8"))
        codes = index.pop("case_codes")
        if not isinstance(codes, list) or set(codes) != set(pins["cases"]) or len(codes) != 69:
            raise ValueError("Unknown catalogue paths")
        index["cases"] = [
            json.loads((location / (code + ".json")).read_text("utf-8")) for code in codes
        ]
        raw = json.dumps(index).encode()
    else:
        raw = location.read_bytes()
    if len(raw) > 4_000_000:
        raise ValueError("Catalogue exceeds bounded size")
    data = json.loads(raw)
    if digest(data) != expected_digest or expected_digest != pins["catalogue_sha256"]:
        raise ValueError("Catalogue digest differs from operator approval")
    expected = {
        "schema_version",
        "source_category",
        "label",
        "algorithm_version",
        "configuration_hash",
        "algorithm_source_hash",
        "reference_summary_hash",
        "historical_benchmark",
        "cases",
    }
    if set(data) != expected or data["source_category"] != "SIMULATION" or data["label"] != LABEL:
        raise ValueError("Invalid provenance envelope")
    if data["schema_version"] != "M06-observations-1" or data["algorithm_version"] != "M05-2":
        raise ValueError("Unknown scientific version")
    if digest(data["historical_benchmark"]) != pins["benchmark_sha256"]:
        raise ValueError("Historical benchmark differs from approved M05 aggregates")
    for item in data["cases"]:
        Case.model_validate(item)
        if digest(item) != pins["cases"].get(item["code"]):
            raise ValueError("Scenario differs from verified observation export")
    if len(data["cases"]) != 69 or len({v["code"] for v in data["cases"]}) != 69:
        raise ValueError("Incomplete or duplicate scenario catalogue")
    return data
