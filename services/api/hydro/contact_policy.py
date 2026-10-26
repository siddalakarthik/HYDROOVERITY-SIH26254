"""Synthetic private-test policy only; not an operational activation mechanism."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ContactTestPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    provenance: Literal["SYNTHETIC_TEST_POLICY_ONLY"]
    operator_reference: str = Field(min_length=10, max_length=128)
    policy_reference: str = Field(min_length=10, max_length=128)
    retention_days: Literal[30]
    capacity: int = Field(ge=1, le=10000)
