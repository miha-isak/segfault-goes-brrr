import pytest
from fastapi.testclient import TestClient

from app.db import connect, get_db, init_db
from app.main import app


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "test.db"
    init_db(path)

    def test_db():
        conn = connect(path)
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    app.dependency_overrides[get_db] = test_db
    yield path
    app.dependency_overrides.clear()


def add_bet(conn, bet_id, user_id, stake, payout):
    conn.execute(
        "INSERT INTO bets (id, user_id, coin_id, direction, stake, seconds, entry_price,"
        " opened_at, settles_at, status, payout) VALUES (?, ?, 'pepe', 'up', ?, 30, 1.0, 't', 't', ?, ?)",
        (bet_id, user_id, stake, "won" if payout else "lost", payout),
    )
    conn.execute(
        "INSERT INTO ledger (user_id, amount, kind, bet_id, created_at) VALUES (?, ?, 'stake', ?, 't')",
        (user_id, -stake, bet_id),
    )
    if payout:
        conn.execute(
            "INSERT INTO ledger (user_id, amount, kind, bet_id, created_at) VALUES (?, ?, 'payout', ?, 't')",
            (user_id, payout, bet_id),
        )


@pytest.mark.usefixtures("db_path")
def test_empty_leaderboard():
    assert TestClient(app).get("/api/leaderboard").json() == []


def test_leaderboard_ranks_by_current_balance(db_path):
    with connect(db_path) as conn:
        conn.executemany(
            "INSERT INTO users (id, username, password_hash) VALUES (?, ?, 'x')",
            [(1, "alice"), (2, "bob"), (3, "carol")],
        )
        conn.executemany(
            "INSERT INTO ledger (user_id, amount, kind, created_at) VALUES (?, 100000, 'bonus', 't')",
            [(1,), (2,), (3,)],
        )
        add_bet(conn, 1, 1, 50000, 100000)  # alice: 1000 -> 500 -> 1500 (max)
        add_bet(conn, 2, 1, 100000, 0)  # alice: 1500 -> 500
        add_bet(conn, 3, 2, 10000, 20000)  # bob: 1000 -> 900 -> 1100
        # carol only has the starting bonus, never bet -> not listed

    assert TestClient(app).get("/api/leaderboard").json() == [
        {"rank": 1, "username": "bob", "current": 110000, "max": 110000},
        {"rank": 2, "username": "alice", "current": 50000, "max": 150000},
    ]


def test_serves_leaderboard_page():
    response = TestClient(app).get("/leaderboard/")
    assert response.status_code == 200
    assert "/js/leaderboard.js" in response.text
