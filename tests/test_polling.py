import pytest

from pawzok.polling import poll_until


def test_poll_until_succeeds_immediately():
    value, attempts, elapsed = poll_until(lambda: "READY", lambda x: x == "READY")

    assert value == "READY"
    assert attempts == 1
    assert elapsed >= 0


def test_poll_until_rejects_invalid_values():
    with pytest.raises(ValueError, match="timeout"):
        poll_until(lambda: 1, lambda x: True, timeout=-1)

    with pytest.raises(ValueError, match="poll_every"):
        poll_until(lambda: 1, lambda x: True, poll_every=0)
