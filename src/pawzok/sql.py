import sqlite3
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence, Union

from .exceptions import PawzokAssertionError
from .polling import poll_until
from .result import SQLResult

Connection = Union[str, Path, sqlite3.Connection]


def _fetch_one(
    connection: Connection,
    query: str,
    params: Optional[Union[Sequence[Any], Mapping[str, Any]]],
) -> dict[str, Any]:
    owns_connection = not isinstance(connection, sqlite3.Connection)
    db = sqlite3.connect(str(connection)) if owns_connection else connection
    db.row_factory = sqlite3.Row

    try:
        cursor = db.execute(query, params or ())
        row = cursor.fetchone()
        return {} if row is None else dict(row)
    finally:
        if owns_connection:
            db.close()


def _matches(actual: Mapping[str, Any], expected: Mapping[str, Any]) -> bool:
    return all(actual.get(key) == value for key, value in expected.items())


def _failure_message(
    expected: Mapping[str, Any],
    actual: Mapping[str, Any],
    attempts: int,
    elapsed: float,
) -> str:
    differences = []
    for key, expected_value in expected.items():
        actual_value = actual.get(key, "<missing>")
        if actual_value != expected_value:
            differences.append(
                f"  {key}: expected {expected_value!r}, got {actual_value!r}"
            )

    details = "\n".join(differences) or "  returned row did not match"
    return (
        "Pawzok SQL assertion failed.\n"
        f"Expected: {dict(expected)!r}\n"
        f"Actual:   {dict(actual)!r}\n"
        f"Attempts: {attempts}\n"
        f"Elapsed:  {elapsed:.2f}s\n"
        "Differences:\n"
        f"{details}"
    )


def assert_sql(
    *,
    connection: Connection,
    query: str,
    expected: Mapping[str, Any],
    params: Optional[Union[Sequence[Any], Mapping[str, Any]]] = None,
    timeout: float = 0,
    poll_every: float = 1,
) -> SQLResult:
    """Assert that one SQLite query row contains the expected values.

    When timeout is greater than zero, Pawzok polls until the row matches or
    the timeout expires. Only keys supplied in ``expected`` are compared.
    """
    if not query or not query.strip():
        raise ValueError("query must not be empty")
    if not expected:
        raise ValueError("expected must contain at least one field")

    operation = lambda: _fetch_one(connection, query, params)
    actual, attempts, elapsed = poll_until(
        operation,
        lambda row: _matches(row, expected),
        timeout=timeout,
        poll_every=poll_every,
    )

    if not _matches(actual, expected):
        raise PawzokAssertionError(
            _failure_message(expected, actual, attempts, elapsed)
        )

    return SQLResult(
        expected=dict(expected),
        actual=dict(actual),
        attempts=attempts,
        elapsed=elapsed,
    )
