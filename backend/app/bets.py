"""Virtual wallet and up/down bets.

Money rules: amounts are integer cents. A wallet balance is the SUM of the user's `ledger`
rows (every bonus, stake and payout is a row), so it can't drift from the history.
A bet is settled lazily: the first request after `settles_at` compares the current price
with the entry price. Win pays 2x stake, an unchanged price refunds the stake, loss pays 0.
"""

import asyncio
import logging
import time
from datetime import UTC, datetime, timedelta
from typing import Literal

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app import coingecko
from app.auth import current_user, now
from app.db import connect, get_db

router = APIRouter()

START_BALANCE = 100_000  # $1000.00
RETRY_COUNT = 2  # extra price attempts after the first failure
RETRY_DELAY = 10  # seconds between attempts
MIN_STAKE = 100  # $1.00
MAX_OPEN_BETS = 10
_retries: dict[int, list] = {}  # bet id -> [failed attempts, next try (monotonic)]
COINS = {"dogecoin", "shiba-inu", "pepe", "dogwifcoin", "bonk", "floki"}


class BetCreate(BaseModel):
    coin_id: str
    direction: Literal["up", "down"]
    stake: int = Field(ge=MIN_STAKE, le=START_BALANCE, description="integer cents")
    seconds: int = Field(ge=5, le=3600)


def ensure_wallet(db, user_id: int) -> None:
    """Give every user a one-time starting balance (also covers users made before wallets)."""
    has = db.execute("SELECT 1 FROM ledger WHERE user_id = ? LIMIT 1", (user_id,)).fetchone()
    if has is None:
        db.execute(
            "INSERT INTO ledger (user_id, amount, kind, created_at) VALUES (?, ?, 'bonus', ?)",
            (user_id, START_BALANCE, now()),
        )


def balance(db, user_id: int) -> int:
    row = db.execute(
        "SELECT COALESCE(SUM(amount), 0) AS b FROM ledger WHERE user_id = ?", (user_id,)
    ).fetchone()
    return row["b"]


async def settle_due(db, user_id: int | None, client: httpx.AsyncClient) -> None:
    """Settle due bets (of one user, or of everyone if user_id is None)."""
    query = "SELECT * FROM bets WHERE status = 'open' AND settles_at <= ?"
    args: tuple = (now(),)
    if user_id is not None:
        query += " AND user_id = ?"
        args += (user_id,)
    due = db.execute(query, args).fetchall()
    for bet in due:
        retry = _retries.get(bet["id"], [0, 0.0])
        if time.monotonic() < retry[1]:
            continue  # waiting before the next price attempt
        try:
            price = await coingecko.fetch_price(client, bet["coin_id"], fresh=True)
        except HTTPException:
            retry[0] += 1
            if retry[0] <= RETRY_COUNT:
                retry[1] = time.monotonic() + RETRY_DELAY
                _retries[bet["id"]] = retry
                continue
            # Price still unavailable: give the stake back (no multiplier) and flag an error.
            status, payout, price = "error", bet["stake"], None
        else:
            if price == bet["entry_price"]:
                status, payout = "push", bet["stake"]
            elif (price > bet["entry_price"]) == (bet["direction"] == "up"):
                status, payout = "won", bet["stake"] * 2
            else:
                status, payout = "lost", 0
        _retries.pop(bet["id"], None)
        # Only the caller that flips open -> settled may pay out (no double payout).
        changed = db.execute(
            "UPDATE bets SET status = ?, exit_price = ?, payout = ? WHERE id = ? AND status = 'open'",
            (status, price, payout, bet["id"]),
        ).rowcount
        if changed and payout:
            db.execute(
                "INSERT INTO ledger (user_id, amount, kind, bet_id, created_at)"
                " VALUES (?, ?, 'payout', ?, ?)",
                (bet["user_id"], payout, bet["id"], now()),
            )


def bet_row(row) -> dict:
    return dict(row)


@router.get("/prices")
async def prices(client: httpx.AsyncClient = Depends(coingecko.get_client)) -> dict:
    """Live USD price and 24h change of every bettable coin."""
    return await coingecko.fetch_prices(client, sorted(COINS))


async def settle_loop() -> None:
    """Background task: settle bets right when they expire (not on the next request)."""
    while True:
        try:
            conn = connect()
            try:
                async with coingecko.make_client() as client:
                    with conn:
                        await settle_due(conn, None, client)
            finally:
                conn.close()
        except Exception:
            logging.getLogger("app.bets").exception("settle loop failed; retrying")
        await asyncio.sleep(2)


@router.post("/wallet/reset")
def reset_wallet(user: dict = Depends(current_user), db=Depends(get_db)) -> dict:
    """Set the balance back to the starting amount (refused while bets are open)."""
    db.execute("BEGIN IMMEDIATE")
    ensure_wallet(db, user["id"])
    open_count = db.execute(
        "SELECT COUNT(*) AS n FROM bets WHERE user_id = ? AND status = 'open'", (user["id"],)
    ).fetchone()["n"]
    if open_count:
        raise HTTPException(400, "Wait for your open bets to finish before resetting")
    diff = START_BALANCE - balance(db, user["id"])
    if diff:
        db.execute(
            "INSERT INTO ledger (user_id, amount, kind, created_at) VALUES (?, ?, 'reset', ?)",
            (user["id"], diff, now()),
        )
    return {"balance": START_BALANCE}


@router.get("/wallet")
async def wallet(
    user: dict = Depends(current_user),
    db=Depends(get_db),
    client: httpx.AsyncClient = Depends(coingecko.get_client),
):
    ensure_wallet(db, user["id"])
    await settle_due(db, user["id"], client)
    return {"balance": balance(db, user["id"])}


@router.get("/bets")
async def my_bets(
    user: dict = Depends(current_user),
    db=Depends(get_db),
    client: httpx.AsyncClient = Depends(coingecko.get_client),
) -> list[dict]:
    ensure_wallet(db, user["id"])
    await settle_due(db, user["id"], client)
    rows = db.execute(
        "SELECT * FROM bets WHERE user_id = ? ORDER BY id DESC LIMIT 50", (user["id"],)
    ).fetchall()
    return [bet_row(r) for r in rows]


@router.post("/bets", status_code=201)
async def place_bet(
    bet: BetCreate,
    user: dict = Depends(current_user),
    db=Depends(get_db),
    client: httpx.AsyncClient = Depends(coingecko.get_client),
) -> dict:
    if bet.coin_id not in COINS:
        raise HTTPException(400, "Unknown coin")
    price = await coingecko.fetch_price(client, bet.coin_id, fresh=True)
    opened = datetime.now(UTC)

    db.execute("BEGIN IMMEDIATE")  # lock so two requests can't spend the same balance
    ensure_wallet(db, user["id"])
    if balance(db, user["id"]) < bet.stake:
        raise HTTPException(400, "Not enough balance")
    open_count = db.execute(
        "SELECT COUNT(*) AS n FROM bets WHERE user_id = ? AND status = 'open'", (user["id"],)
    ).fetchone()["n"]
    if open_count >= MAX_OPEN_BETS:
        raise HTTPException(400, f"Too many open bets (max {MAX_OPEN_BETS})")
    cursor = db.execute(
        "INSERT INTO bets (user_id, coin_id, direction, stake, seconds, entry_price,"
        " opened_at, settles_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            user["id"], bet.coin_id, bet.direction, bet.stake, bet.seconds, price,
            opened.isoformat(), (opened + timedelta(seconds=bet.seconds)).isoformat(),
        ),
    )
    db.execute(
        "INSERT INTO ledger (user_id, amount, kind, bet_id, created_at) VALUES (?, ?, 'stake', ?, ?)",
        (user["id"], -bet.stake, cursor.lastrowid, now()),
    )
    row = db.execute("SELECT * FROM bets WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return bet_row(row)
