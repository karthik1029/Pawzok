from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class SQLResult:
    """Details about a successful SQL state assertion."""

    expected: Mapping[str, Any]
    actual: Mapping[str, Any]
    attempts: int
    elapsed: float
