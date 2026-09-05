import sqlite3
import threading
import time

import pytest

from pawzok import PawzokAssertionError, assert_sql


@pytest.fixture
def orders_db(tmp_path):
    path = tmp_path / "orders.db"
    connection = sqlite3.connect(path)
    connection.execute(
        "CREATE TABLE orders (order_id INTEGER PRIMARY KEY, status TEXT, amount REAL)"
    )
    connection.execute(
        "INSERT INTO orders (order_id, status, amount) VALUES (?, ?, ?)",
        (123, "CONFIRMED", 49.99),
    )
    connection.commit()
    connection.close()
    return path


def test_assert_sql_matches_expected_fields(orders_db):
    result = assert_sql(
        connection=orders_db,
        query="SELECT status, amount FROM orders WHERE order_id = ?",
        params=(123,),
        expected={"status": "CONFIRMED", "amount": 49.99},
    )

    assert result.actual["status"] == "CONFIRMED"
    assert result.attempts == 1


def test_assert_sql_raises_clear_failure(orders_db):
    with pytest.raises(PawzokAssertionError, match="expected 'READY', got 'CONFIRMED'"):
        assert_sql(
            connection=orders_db,
            query="SELECT status FROM orders WHERE order_id = ?",
            params=(123,),
            expected={"status": "READY"},
        )


def test_assert_sql_polls_until_state_changes(orders_db):
    def update_order():
        time.sleep(0.1)
        connection = sqlite3.connect(orders_db)
        connection.execute(
            "UPDATE orders SET status = ? WHERE order_id = ?",
            ("READY", 123),
        )
        connection.commit()
        connection.close()

    worker = threading.Thread(target=update_order)
    worker.start()

    result = assert_sql(
        connection=orders_db,
        query="SELECT status FROM orders WHERE order_id = ?",
        params=(123,),
        expected={"status": "READY"},
        timeout=1,
        poll_every=0.05,
    )

    worker.join()
    assert result.actual == {"status": "READY"}
    assert result.attempts >= 2
