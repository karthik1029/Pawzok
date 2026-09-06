# Pawzok

**Follow the trail. Verify what actually happened.**

Pawzok is a Python testing library for verifying application state without repetitive connection, polling, request, and assertion code.

## v0.2

Pawzok now supports both API and SQL validation:

- `assert_api()` for HTTP status and JSON response validation
- `assert_sql()` for concise database assertions
- smart polling for eventually consistent database state
- clear, pytest-friendly failure messages
- SQLite support
- Python 3.9 through 3.13

## Installation

```bash
pip install pawzok
```

For development:

```bash
git clone https://github.com/karthik1029/Pawzok.git
cd Pawzok
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python3 -m pip install -e ".[dev]"
python3 -m pytest
```

## API validation

```python
from pawzok import assert_api

result = assert_api(
    method="GET",
    url="https://api.example.com/orders/123",
    expected_status=200,
    expected={"status": "READY"},
)
```

Pawzok checks the HTTP status and the expected JSON fields. Extra fields in the response are allowed.

If the API returns the wrong state, Pawzok reports the difference clearly:

```text
Pawzok API assertion failed.
Expected status: 200
Actual status:   200
Differences:
  status: expected 'READY', got 'PROCESSING'
```

## SQL validation

```python
from pawzok import assert_sql

assert_sql(
    connection="orders.db",
    query="""
        SELECT status
        FROM orders
        WHERE order_id = 123
    """,
    expected={"status": "CONFIRMED"},
)
```

For state that may take time to appear:

```python
assert_sql(
    connection="orders.db",
    query="SELECT status FROM orders WHERE order_id = 123",
    expected={"status": "READY"},
    timeout=20,
    poll_every=2,
)
```

Pawzok keeps checking until the expected state appears or the timeout expires.

## Roadmap

- **0.1** — SQL assertions and smart polling ✅
- **0.2** — API validation ✅
- **0.3** — API + SQL workflow traces
- **0.4** — event-stream validation
- **0.5** — cross-system correlation

## Why Pawzok?

A successful response does not always mean the system reached the correct state. Pawzok is being built to follow the trail of an operation and verify the state behind the response.

## License

MIT
