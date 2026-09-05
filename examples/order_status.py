import sqlite3
from pathlib import Path

from pawzok import assert_sql


database = Path("orders.db")
connection = sqlite3.connect(database)
connection.execute(
    "CREATE TABLE IF NOT EXISTS orders (order_id INTEGER PRIMARY KEY, status TEXT)"
)
connection.execute(
    "INSERT OR REPLACE INTO orders (order_id, status) VALUES (?, ?)",
    (123, "CONFIRMED"),
)
connection.commit()
connection.close()

result = assert_sql(
    connection=database,
    query="SELECT status FROM orders WHERE order_id = ?",
    params=(123,),
    expected={"status": "CONFIRMED"},
)

print(f"Pawzok verified the order in {result.attempts} attempt(s).")
