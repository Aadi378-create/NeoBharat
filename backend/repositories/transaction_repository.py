import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure project root and backend directory are in sys.path
_backend_dir = Path(__file__).resolve().parent.parent
_project_root = _backend_dir.parent
for _p in (str(_project_root), str(_backend_dir)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from backend.database.connection import get_db_connection
except ImportError:
    from database.connection import get_db_connection


def get_transactions_for_customer(
    customer_id: int, conn: Optional[sqlite3.Connection] = None
) -> List[Dict[str, Any]]:
    """Retrieve all transactions for a specific customer.

    Args:
        customer_id: Customer identifier.
        conn: Optional existing sqlite3 connection.

    Returns:
        List[Dict[str, Any]]: List of transactions as dictionaries.
    """
    owns_conn = conn is None
    connection = conn or get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM transactions WHERE customer_id = ?", (customer_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        if owns_conn:
            connection.close()


def get_all_transactions_for_customer_ordered(
    customer_id: int, order: str = "ASC", conn: Optional[sqlite3.Connection] = None
) -> List[Dict[str, Any]]:
    """Retrieve all transactions for a customer ordered by timestamp.

    Args:
        customer_id: Customer identifier.
        order: 'ASC' for chronological or 'DESC' for reverse chronological.
        conn: Optional existing sqlite3 connection.

    Returns:
        List[Dict[str, Any]]: Ordered list of transactions as dictionaries.
    """
    owns_conn = conn is None
    connection = conn or get_db_connection()
    sort_direction = "DESC" if order.upper() == "DESC" else "ASC"
    try:
        cursor = connection.cursor()
        query = f"SELECT * FROM transactions WHERE customer_id = ? ORDER BY timestamp {sort_direction}"
        cursor.execute(query, (customer_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        if owns_conn:
            connection.close()


def insert_transaction(
    transaction_data: Dict[str, Any], conn: Optional[sqlite3.Connection] = None
) -> int:
    """Insert a single transaction.

    Args:
        transaction_data: Dictionary containing transaction fields.
        conn: Optional existing sqlite3 connection.

    Returns:
        int: The ID of the inserted transaction.
    """
    owns_conn = conn is None
    connection = conn or get_db_connection()
    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO transactions (customer_id, timestamp, amount, type, category, merchant, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        from datetime import datetime, timezone
        ts = transaction_data.get("timestamp") or datetime.now(timezone.utc).isoformat()
        params = (
            transaction_data["customer_id"],
            ts,
            float(transaction_data["amount"]),
            transaction_data["type"],
            transaction_data["category"],
            transaction_data.get("merchant"),
            transaction_data.get("status", "SUCCESS"),
        )
        cursor.execute(query, params)
        if owns_conn:
            connection.commit()
        return cursor.lastrowid
    finally:
        if owns_conn:
            connection.close()
