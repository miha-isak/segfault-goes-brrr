import pytest
from fastapi.testclient import TestClient

from app.db import connect, get_db
from app.main import app


@pytest.fixture
def client(tmp_path):
    db_path = tmp_path / "test.db"

    def test_db():
        conn = connect(db_path)
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    app.dependency_overrides[get_db] = test_db
    yield TestClient(app)
    app.dependency_overrides.clear()


CREDS = {"username": "alice", "password": "correct horse"}


def test_register_login_me_logout(client):
    r = client.post("/api/auth/register", json=CREDS)
    assert r.status_code == 201
    assert r.json()["username"] == "alice"

    assert client.get("/api/auth/me").status_code == 401

    r = client.post("/api/auth/login", json=CREDS)
    assert r.status_code == 200
    assert "httponly" in r.headers["set-cookie"].lower()

    r = client.get("/api/auth/me")
    assert r.status_code == 200
    assert r.json()["username"] == "alice"

    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/auth/me").status_code == 401


def test_duplicate_username_case_insensitive(client):
    client.post("/api/auth/register", json=CREDS)
    r = client.post("/api/auth/register", json={**CREDS, "username": "ALICE"})
    assert r.status_code == 409


@pytest.mark.parametrize(
    "creds",
    [
        {"username": "alice", "password": "wrong password"},
        {"username": "nobody", "password": "correct horse"},
    ],
)
def test_bad_login(client, creds):
    client.post("/api/auth/register", json=CREDS)
    r = client.post("/api/auth/login", json=creds)
    assert r.status_code == 401
    assert "set-cookie" not in r.headers


def test_password_not_stored_plaintext(client, tmp_path):
    client.post("/api/auth/register", json=CREDS)
    stored = connect(tmp_path / "test.db").execute("SELECT password_hash FROM users").fetchone()[0]
    assert CREDS["password"] not in stored


def test_forged_session_rejected(client):
    client.cookies.set("session", "not-a-real-token")
    assert client.get("/api/auth/me").status_code == 401


@pytest.mark.parametrize(
    "creds",
    [
        {"username": "al", "password": "correct horse"},
        {"username": "al ice", "password": "correct horse"},
        {"username": "alice", "password": "short"},
    ],
)
def test_rejects_invalid_input(client, creds):
    assert client.post("/api/auth/register", json=creds).status_code == 422
