"""Safe stable errors; never echo input, database errors or stack traces."""

from dataclasses import dataclass


@dataclass
class Problem(Exception):
    status: int
    code: str
    message: str


def require(
    condition: object,
    status: int = 422,
    code: str = "INVALID_REQUEST",
    message: str = "Request does not satisfy the operation requirements",
) -> None:
    if not condition:
        raise Problem(status, code, message)
