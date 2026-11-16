"""Register, log in, log out, and "who am I".

How it works:
1. Register: we save the username and a *hash* of the password (never the password itself).
2. Log in: we check the password, create a random session token, save its hash in the
   `sessions` table, and give the token to the browser in a cookie.
3. Every later request sends that cookie back, so we can look up who is logged in.
4. Log out: we delete the session from the table and the cookie from the browser.
"""

import hashlib
import secrets
import sqlite3
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Response
from pydantic import BaseModel, Field

from app.config import settings
from app.db import get_db
from app.ratelimit import RateLimiter

router = APIRouter(prefix="/auth")

SESSION_DAYS = 7

# 10 register/login attempts per minute per IP.
auth_limiter = RateLimiter(limit=10, window_seconds=60)

# 60 API calls per minute per API key (scripts).
api_key_limiter = RateLimiter(limit=60, window_seconds=60)


class Credentials(BaseModel):
    """What the client sends to /register and /login (checked automatically by FastAPI)."""

    username: str = Field(min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=8, max_length=128)


# ---------- passwords ----------


def hash_password(password: str, salt: bytes) -> bytes:
    # scrypt is deliberately slow, so stolen hashes are hard to brute-force.
    return hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)


def make_password_hash(password: str) -> str:
    """Return "salt$hash" (both hex) to store in the database."""
    salt = secrets.token_bytes(16)  # random per user, so equal passwords get different hashes
    return salt.hex() + "$" + hash_password(password, salt).hex()


def check_password(password: str, stored: str) -> bool:
    salt_hex, hash_hex = stored.split("$")
    actual = hash_password(password, bytes.fromhex(salt_hex))
    return secrets.compare_digest(actual, bytes.fromhex(hash_hex))


# Used when the username doesn't exist, so a wrong username takes as long as a wrong password
# (otherwise an attacker could time responses to find out which usernames exist).
FAKE_HASH = make_password_hash("not-a-real-password")


# ---------- sessions ----------


def hash_token(token: str) -> str:
    # We store only a hash of the token, so a leaked database can't be used to log in.
    return hashlib.sha256(token.encode()).hexdigest()


def now() -> str:
    return datetime.now(UTC).isoformat()


def session_user(session: str | None = Cookie(default=None), db=Depends(get_db)) -> dict:
    """Find the logged-in user from the `session` cookie, or answer 401 (browser only)."""
    if session is None:
        raise HTTPException(401, "Not logged in")

    row = db.execute(
        """
        SELECT users.id, users.username
        FROM sessions JOIN users ON users.id = sessions.user_id
        WHERE sessions.token_hash = ? AND sessions.expires_at > ?
        """,
        (hash_token(session), now()),
    ).fetchone()

    if row is None:
        raise HTTPException(401, "Not logged in")
    return {"id": row["id"], "username": row["username"]}


def _bearer(authorization: str | None, x_api_key: str | None) -> str | None:
    if x_api_key:
        return x_api_key.strip()
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return None


def current_user(
    session: str | None = Cookie(default=None),
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None),
    db=Depends(get_db),
) -> dict:
    """The user making the request: an API key (`Authorization: Bearer <key>` or
    `X-API-Key`) if one is sent, otherwise the browser session cookie.

    Use it in any route that needs a logged-in user: `user: dict = Depends(current_user)`.
    """
    key = _bearer(authorization, x_api_key)
    if key is None:
        return session_user(session, db)
    row = db.execute(
        "SELECT users.id, users.username FROM api_keys JOIN users ON users.id = api_keys.user_id"
        " WHERE api_keys.key_hash = ?",
        (hash_token(key),),
    ).fetchone()
    if row is None:
        raise HTTPException(401, "Invalid API key")
    api_key_limiter.check(f"key:{row['id']}")
    return {"id": row["id"], "username": row["username"]}


# ---------- routes ----------


@router.post("/register", status_code=201, dependencies=[Depends(auth_limiter)])
def register(creds: Credentials, db=Depends(get_db)):
    try:
        cursor = db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (creds.username, make_password_hash(creds.password)),
        )
    except sqlite3.IntegrityError:  # the UNIQUE rule on username was broken
        raise HTTPException(409, "Username already taken")
    return {"id": cursor.lastrowid, "username": creds.username}


@router.post("/login", dependencies=[Depends(auth_limiter)])
def login(creds: Credentials, response: Response, db=Depends(get_db)):
    user = db.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?", (creds.username,)
    ).fetchone()

    stored_hash = user["password_hash"] if user else FAKE_HASH
    if not check_password(creds.password, stored_hash) or user is None:
        raise HTTPException(401, "Invalid username or password")

    token = secrets.token_urlsafe(32)
    expires = datetime.now(UTC) + timedelta(days=SESSION_DAYS)
    db.execute("DELETE FROM sessions WHERE expires_at <= ?", (now(),))  # tidy up old sessions
    db.execute(
        "INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)",
        (hash_token(token), user["id"], expires.isoformat()),
    )

    # httponly: page JavaScript can't read the cookie. samesite: other sites can't send it.
    response.set_cookie(
        "session", token, max_age=SESSION_DAYS * 24 * 3600, httponly=True,
        samesite="lax", secure=settings.cookie_secure,
    )
    return {"id": user["id"], "username": user["username"]}


@router.post("/logout", status_code=204)
def logout(response: Response, session: str | None = Cookie(default=None), db=Depends(get_db)):
    if session is not None:
        db.execute("DELETE FROM sessions WHERE token_hash = ?", (hash_token(session),))
    response.delete_cookie("session")


@router.get("/me")
def me(user: dict = Depends(current_user)):
    return user


# ---------- API keys (managed from the browser, used from scripts) ----------


@router.get("/api-key")
def api_key_info(user: dict = Depends(session_user), db=Depends(get_db)) -> dict:
    row = db.execute(
        "SELECT prefix, created_at FROM api_keys WHERE user_id = ?", (user["id"],)
    ).fetchone()
    return {"has_key": row is not None, "prefix": row["prefix"] if row else None}


@router.post("/api-key", status_code=201)
def create_api_key(user: dict = Depends(session_user), db=Depends(get_db)) -> dict:
    """Create (or replace) the user's API key. The key is returned once and never stored."""
    key = "sgb_" + secrets.token_urlsafe(32)
    db.execute(
        "INSERT INTO api_keys (user_id, key_hash, prefix, created_at) VALUES (?, ?, ?, ?)"
        " ON CONFLICT(user_id) DO UPDATE SET key_hash = excluded.key_hash,"
        " prefix = excluded.prefix, created_at = excluded.created_at",
        (user["id"], hash_token(key), key[:8], now()),
    )
    return {"api_key": key, "prefix": key[:8]}


@router.delete("/api-key", status_code=204)
def revoke_api_key(user: dict = Depends(session_user), db=Depends(get_db)):
    db.execute("DELETE FROM api_keys WHERE user_id = ?", (user["id"],))
