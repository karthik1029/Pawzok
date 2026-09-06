from dataclasses import dataclass
from typing import Any, Mapping, Optional

import requests

from .exceptions import PawzokAssertionError


@dataclass(frozen=True)
class APIResult:
    expected_status: int
    actual_status: int
    expected: Mapping[str, Any]
    actual: Mapping[str, Any]


def _matches(actual: Mapping[str, Any], expected: Mapping[str, Any]) -> bool:
    return all(actual.get(key) == value for key, value in expected.items())


def _failure_message(
    expected_status: int,
    actual_status: int,
    expected: Mapping[str, Any],
    actual: Mapping[str, Any],
) -> str:
    differences = []

    if actual_status != expected_status:
        differences.append(
            f"  status code: expected {expected_status}, got {actual_status}"
        )

    for key, expected_value in expected.items():
        actual_value = actual.get(key, "<missing>")
        if actual_value != expected_value:
            differences.append(
                f"  {key}: expected {expected_value!r}, got {actual_value!r}"
            )

    return (
        "Pawzok API assertion failed.\n"
        f"Expected status: {expected_status}\n"
        f"Actual status:   {actual_status}\n"
        f"Expected body:   {dict(expected)!r}\n"
        f"Actual body:     {dict(actual)!r}\n"
        "Differences:\n"
        + "\n".join(differences)
    )


def assert_api(
    *,
    method: str,
    url: str,
    expected_status: int = 200,
    expected: Optional[Mapping[str, Any]] = None,
    timeout: float = 10,
    **request_kwargs: Any,
) -> APIResult:
    if not method:
        raise ValueError("method must not be empty")

    if not url:
        raise ValueError("url must not be empty")

    expected = expected or {}

    response = requests.request(
        method=method,
        url=url,
        timeout=timeout,
        **request_kwargs,
    )

    try:
        actual = response.json()
    except ValueError:
        actual = {}

    if response.status_code != expected_status or not _matches(actual, expected):
        raise PawzokAssertionError(
            _failure_message(
                expected_status,
                response.status_code,
                expected,
                actual,
            )
        )

    return APIResult(
        expected_status=expected_status,
        actual_status=response.status_code,
        expected=dict(expected),
        actual=dict(actual),
    )
