import httpx
import pytest
from fastapi.testclient import TestClient

from app import bets, coingecko
from app.auth import auth_limiter
from app.coingecko import BASE_URL, get_client
from app.db import connect, get_db, init_db
from app.main import app

PRICE = {"value": 1.0}


@pytest.fixture
def client(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    auth_limiter.reset()

    def test_db():
        conn = connect(db_path)
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def handler(request):
        return httpx.Response(200, json={"dogecoin": {"usd": PRICE["value"]}})

    async def fake_client():
        async with httpx.AsyncClient(
            base_url=BASE_URL, transport=httpx.MockTransport(handler)
        ) as c:
            yield c

    coingecko._price_cache.clear()
    PRICE["value"] = 1.0
    app.dependency_overrides[get_db] = test_db
    app.dependency_overrides[get_client] = fake_client
    c = TestClient(app)
    c.post("/api/auth/register", json={"username": "alice", "password": "correct horse"})
    c.post("/api/auth/login", json={"username": "alice", "password": "correct horse"})
    yield c
    app.dependency_overrides.clear()


BET = {"coin_id": "dogecoin", "direction": "up", "stake": 1000, "seconds": 5}


def test_requires_login():
    assert TestClient(app).get("/api/wallet").status_code == 401


def test_wallet_starts_with_bonus(client):
    assert client.get("/api/wallet").json() == {"balance": bets.START_BALANCE}


def test_place_bet_deducts_stake(client):
    r = client.post("/api/bets", json=BET)
    assert r.status_code == 201 and r.json()["status"] == "open"
    assert client.get("/api/wallet").json()["balance"] == bets.START_BALANCE - 1000


def test_rejects_overspend_and_bad_input(client):
    assert client.post("/api/bets", json={**BET, "stake": bets.START_BALANCE + 1}).status_code == 422
    assert client.post("/api/bets", json={**BET, "direction": "sideways"}).status_code == 422
    assert client.post("/api/bets", json={**BET, "coin_id": "nope"}).status_code == 400


def test_win_and_loss_settlement(client, monkeypatch):
    monkeypatch.setattr(bets, "now", lambda: "9999-01-01")  # everything is due
    for direction, new_price, expected in [("up", 2.0, 1000), ("down", 2.0, -1000)]:
        PRICE["value"] = 1.0
        coingecko._price_cache.clear()
        before = client.get("/api/wallet").json()["balance"]
        monkeypatch.undo()
        client.post("/api/bets", json={**BET, "direction": direction})
        PRICE["value"] = new_price
        coingecko._price_cache.clear()
        monkeypatch.setattr(bets, "now", lambda: "9999-01-01")
        after = client.get("/api/wallet").json()["balance"]
        assert after - before == expected
        monkeypatch.undo()
    history = client.get("/api/bets").json()
    assert {b["status"] for b in history} == {"won", "lost"}


def test_reset_wallet(client, monkeypatch):
    assert client.post("/api/bets", json=BET).status_code == 201
    assert client.post("/api/wallet/reset").status_code == 400  # bet still open
    PRICE["value"] = 0.5
    coingecko._price_cache.clear()
    monkeypatch.setattr(bets, "now", lambda: "9999-01-01")  # bet is due, price fell: lost
    assert client.get("/api/wallet").json()["balance"] == bets.START_BALANCE - 1000
    monkeypatch.undo()
    assert client.post("/api/wallet/reset").json() == {"balance": bets.START_BALANCE}
    assert client.get("/api/wallet").json()["balance"] == bets.START_BALANCE
