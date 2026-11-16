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
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from pydantic import BaseModel, Field

from app.db import get_db

router = APIRouter(prefix="/auth")

SESSION_DAYS = 7


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
    return datetime.now(timezone.utc).isoformat()


def current_user(session: str | None = Cookie(default=None), db=Depends(get_db)) -> dict:
    """Find the logged-in user from the `session` cookie, or answer 401.

    Use it in any route that needs a logged-in user: `user: dict = Depends(current_user)`.
    """
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


# ---------- routes ----------


@router.post("/register", status_code=201)
def register(creds: Credentials, db=Depends(get_db)):
    try:
        cursor = db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (creds.username, make_password_hash(creds.password)),
        )
    except sqlite3.IntegrityError:  # the UNIQUE rule on username was broken
        raise HTTPException(409, "Username already taken")
    return {"id": cursor.lastrowid, "username": creds.username}


@router.post("/login")
def login(creds: Credentials, response: Response, db=Depends(get_db)):
    user = db.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?", (creds.username,)
    ).fetchone()

    stored_hash = user["password_hash"] if user else FAKE_HASH
    if not check_password(creds.password, stored_hash) or user is None:
        raise HTTPException(401, "Invalid username or password")

    token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)
    db.execute("DELETE FROM sessions WHERE expires_at <= ?", (now(),))  # tidy up old sessions
    db.execute(
        "INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)",
        (hash_token(token), user["id"], expires.isoformat()),
    )

    # httponly: page JavaScript can't read the cookie. samesite: other sites can't send it.
    response.set_cookie(
        "session", token, max_age=SESSION_DAYS * 24 * 3600, httponly=True, samesite="lax"
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
