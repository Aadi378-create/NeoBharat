import sqlite3
import sys
from pathlib import Path
from typing import Optional

# Ensure project root and backend directory are in sys.path
_backend_dir = Path(__file__).resolve().parent.parent
_project_root = _backend_dir.parent
for _p in (str(_project_root), str(_backend_dir)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from backend.config import DATABASE_PATH
except ImportError:
    from config import DATABASE_PATH

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Create and return a configured SQLite connection.

    Args:
        db_path: Optional database path override. Defaults to config.DATABASE_PATH.

    Returns:
        sqlite3.Connection: Configured connection with Row factory and foreign keys enabled.
    """
    path = db_path or DATABASE_PATH
    # Ensure directory exists
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize database tables and indexes from schema.sql.

    Args:
        db_path: Optional database path override. Defaults to config.DATABASE_PATH.
    """
    conn = get_db_connection(db_path)
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        conn.commit()
    finally:
        conn.close()
