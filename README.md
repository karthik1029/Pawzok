# Pawzok 🐾

**Follow the trail. Verify what actually happened.**

Pawzok is a Python testing library for verifying application state without repetitive database connection, polling, and assertion code.

## v0.1

The first release focuses on SQL state validation:

- `assert_sql()` for concise database assertions
- smart polling for eventually consistent state
- clear, pytest-friendly failure messages
- SQLite support with no external database required
- a small foundation designed for future validators

## Installation for development

```bash
git clone https://github.com/karthik1029/Pawzok.git
cd Pawzok
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

## Quick start

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

- **0.1** — SQL assertions and smart polling
- **0.2** — API validation
- **0.3** — API + SQL workflow traces
- **0.4** — event-stream validation
- **0.5** — cross-system correlation

## Why Pawzok?

A successful response does not always mean the system reached the correct state. Pawzok is being built to follow the trail of an operation and verify the state behind the response.

## License

MIT
