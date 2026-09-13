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


def get_customer_by_id(customer_id: int, conn: Optional[sqlite3.Connection] = None) -> Optional[Dict[str, Any]]:
    """Retrieve a single customer by ID.

    Args:
        customer_id: The customer ID.
        conn: Optional existing sqlite3 connection.

    Returns:
        Optional[Dict[str, Any]]: Customer data as a dictionary, or None if not found.
    """
    owns_conn = conn is None
    connection = conn or get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        if owns_conn:
            connection.close()


def get_customer_by_phone(phone: str, conn: Optional[sqlite3.Connection] = None, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieve a single customer by phone number.

    Args:
        phone: The customer phone number.
        conn: Optional existing sqlite3 connection.
        db_path: Optional database path override.

    Returns:
        Optional[Dict[str, Any]]: Customer data as a dictionary, or None if not found.
    """
    owns_conn = conn is None
    connection = conn or get_db_connection(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM customers WHERE phone = ?", (phone,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        if owns_conn:
            connection.close()


def get_all_customers(conn: Optional[sqlite3.Connection] = None) -> List[Dict[str, Any]]:
    """Retrieve all customers.

    Args:
        conn: Optional existing sqlite3 connection.

    Returns:
        List[Dict[str, Any]]: List of customer records as dictionaries.
    """
    owns_conn = conn is None
    connection = conn or get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM customers ORDER BY id ASC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        if owns_conn:
            connection.close()


def insert_customer(customer_data: Dict[str, Any], conn: Optional[sqlite3.Connection] = None) -> int:
    """Insert a new customer into the database.

    Args:
        customer_data: Dictionary containing customer fields.
        conn: Optional existing sqlite3 connection.

    Returns:
        int: The ID of the inserted customer.
    """
    owns_conn = conn is None
    connection = conn or get_db_connection()
    try:
        cursor = connection.cursor()
        # Support explicit ID if provided, otherwise let autoincrement handle it
        if "id" in customer_data and customer_data["id"] is not None:
            query = """
                INSERT INTO customers (id, name, age, language, monthly_income, monthly_emi, phone, pin_hash, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                customer_data["id"],
                customer_data["name"],
                customer_data.get("age"),
                customer_data.get("language", "en"),
                customer_data.get("monthly_income"),
                customer_data.get("monthly_emi"),
                customer_data.get("phone"),
                customer_data.get("pin_hash"),
                customer_data.get("created_at"),
            )
        else:
            query = """
                INSERT INTO customers (name, age, language, monthly_income, monthly_emi, phone, pin_hash, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                customer_data["name"],
                customer_data.get("age"),
                customer_data.get("language", "en"),
                customer_data.get("monthly_income"),
                customer_data.get("monthly_emi"),
                customer_data.get("phone"),
                customer_data.get("pin_hash"),
                customer_data.get("created_at"),
            )
        cursor.execute(query, params)
        if owns_conn:
            connection.commit()
        return cursor.lastrowid
    finally:
        if owns_conn:
            connection.close()
