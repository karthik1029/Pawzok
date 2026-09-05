import time
from typing import Callable, TypeVar

T = TypeVar("T")


def poll_until(
    operation: Callable[[], T],
    predicate: Callable[[T], bool],
    *,
    timeout: float = 0,
    poll_every: float = 1,
) -> tuple[T, int, float]:
    """Run operation until predicate is true or timeout expires.

    The operation always runs at least once. A timeout of 0 means a single
    immediate check.
    """
    if timeout < 0:
        raise ValueError("timeout must be >= 0")
    if poll_every <= 0:
        raise ValueError("poll_every must be > 0")

    started = time.monotonic()
    deadline = started + timeout
    attempts = 0

    while True:
        attempts += 1
        value = operation()
        elapsed = time.monotonic() - started

        if predicate(value):
            return value, attempts, elapsed

        if time.monotonic() >= deadline:
            return value, attempts, elapsed

        remaining = deadline - time.monotonic()
        time.sleep(min(poll_every, max(0, remaining)))
