"""SQLite database (Python's built-in sqlite3 module).

The database is a single file, backend/app.db. It is created automatically.
"""

import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.environ.get("DB_PATH", Path(__file__).parent.parent / "app.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY,
    username      TEXT NOT NULL UNIQUE COLLATE NOCASE,  -- "Alice" and "alice" count as the same
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    token_hash TEXT PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expires_at TEXT NOT NULL
);
"""


def connect(path=DB_PATH) -> sqlite3.Connection:
    """Open the database and create the tables if they don't exist yet."""
    # check_same_thread=False: FastAPI may use the connection from another thread
    # during the same request. Each request gets its own connection, so this is safe.
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # lets us write row["username"] instead of row[1]
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn


def get_db():
    """Give each request its own connection.

    Changes are saved (committed) if the request succeeds and undone if it fails.
    Routes get it with: `db=Depends(get_db)`.
    """
    conn = connect()
    try:
        with conn:
            yield conn
    finally:
        conn.close()
