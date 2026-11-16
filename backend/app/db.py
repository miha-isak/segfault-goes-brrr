"""SQLite database (Python's built-in sqlite3 module).

The database is a single file (DB_PATH, default backend/app.db), created at startup.
"""

import sqlite3
from pathlib import Path

from app.config import settings

DB_PATH = settings.db_path

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

-- Wallet: balance = SUM(amount) per user. Amounts are integer cents, never floats.
CREATE TABLE IF NOT EXISTS ledger (
    id         INTEGER PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount     INTEGER NOT NULL,
    kind       TEXT NOT NULL,  -- bonus | stake | payout
    bet_id     INTEGER,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ledger_user ON ledger(user_id);

CREATE TABLE IF NOT EXISTS bets (
    id          INTEGER PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    coin_id     TEXT NOT NULL,
    direction   TEXT NOT NULL,  -- up | down
    stake       INTEGER NOT NULL,
    seconds     INTEGER NOT NULL,
    entry_price REAL NOT NULL,
    opened_at   TEXT NOT NULL,
    settles_at  TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'open',  -- open | won | lost | push
    exit_price  REAL,
    payout      INTEGER
);
CREATE INDEX IF NOT EXISTS bets_user ON bets(user_id);
"""


def connect(path=DB_PATH) -> sqlite3.Connection:
    """Open a connection to the database."""
    # check_same_thread=False: FastAPI may use the connection from another thread
    # during the same request. Each request gets its own connection, so this is safe.
    conn = sqlite3.connect(path, check_same_thread=False, timeout=5)
    conn.row_factory = sqlite3.Row  # lets us write row["username"] instead of row[1]
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")  # wait up to 5 s if the database is locked
    return conn


def init_db(path=DB_PATH) -> None:
    """Create the tables if they don't exist yet. Called once at startup."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = connect(path)
    try:
        conn.execute("PRAGMA journal_mode = WAL")  # readers don't block the writer
        conn.executescript(SCHEMA)
    finally:
        conn.close()


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
