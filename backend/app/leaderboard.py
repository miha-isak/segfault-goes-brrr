"""Leaderboard: users who have placed at least one bet, ranked by current wallet balance.

Balances come from the `ledger` (see app.bets): current = SUM(amount), and the maximum is the
highest running total the wallet ever reached. Amounts are integer cents.
"""

from fastapi import APIRouter, Depends

from app.db import get_db

router = APIRouter()


@router.get("/leaderboard")
def leaderboard(db=Depends(get_db)) -> list[dict]:
    rows = db.execute(
        """
        WITH running AS (
            SELECT user_id,
                   SUM(amount) OVER (PARTITION BY user_id ORDER BY id) AS total
            FROM ledger
            WHERE user_id IN (SELECT user_id FROM bets)
        )
        SELECT users.username,
               (SELECT SUM(amount) FROM ledger WHERE ledger.user_id = users.id) AS current,
               MAX(running.total) AS max_balance
        FROM running JOIN users ON users.id = running.user_id
        GROUP BY users.id
        ORDER BY current DESC, max_balance DESC, users.username
        """
    ).fetchall()
    return [
        {"rank": i, "username": r["username"], "current": r["current"], "max": r["max_balance"]}
        for i, r in enumerate(rows, start=1)
    ]
