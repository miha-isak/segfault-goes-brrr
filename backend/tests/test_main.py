from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_serves_frontend():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_task_lifecycle():
    response = client.post("/api/tasks", json={"text": "  new task  "})
    assert response.status_code == 201
    task = response.json()
    assert task["text"] == "new task" and task["done"] is False

    assert task in client.get("/api/tasks").json()

    response = client.post(f"/api/tasks/{task['id']}/toggle")
    assert response.json()["done"] is True

    response = client.post(f"/api/tasks/{task['id']}/delete")
    assert response.status_code == 200
    assert all(t["id"] != task["id"] for t in client.get("/api/tasks").json())


def test_task_errors():
    assert client.post("/api/tasks", json={"text": "   "}).status_code == 400
    assert client.post("/api/tasks", json={}).status_code == 422
    assert client.post("/api/tasks/9999/toggle").status_code == 404
    assert client.post("/api/tasks/9999/delete").status_code == 404
