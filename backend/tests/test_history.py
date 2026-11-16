import httpx
import pytest
from fastapi.testclient import TestClient

from app.coingecko import BASE_URL, get_client
from app.main import app


@pytest.fixture
def use_upstream():
    """Route CoinGecko calls to `handler` instead of the network."""

    def install(handler):
        async def fake_client():
            async with httpx.AsyncClient(
                base_url=BASE_URL, transport=httpx.MockTransport(handler)
            ) as client:
                yield client

        app.dependency_overrides[get_client] = fake_client

    yield install
    app.dependency_overrides.pop(get_client, None)


client = TestClient(app)


def test_returns_prices(use_upstream):
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={"prices": [[1000, 0.1], [2000, 0.2]], "market_caps": []})

    use_upstream(handler)
    response = client.get("/api/history/dogecoin?days=7&vs_currency=eur")
    assert response.status_code == 200
    assert response.json() == {
        "coin_id": "dogecoin",
        "vs_currency": "eur",
        "days": 7,
        "prices": [[1000, 0.1], [2000, 0.2]],
    }
    assert seen[0].url.path == "/api/v3/coins/dogecoin/market_chart"
    assert seen[0].url.params["days"] == "7"


@pytest.mark.parametrize(
    ("upstream_status", "body", "expected"),
    [
        (404, {"error": "coin not found"}, 404),
        (400, {"error": "invalid vs_currency"}, 400),
        (429, {}, 429),
        (500, {}, 502),
        (200, {"unexpected": True}, 502),
    ],
)
def test_upstream_errors(use_upstream, upstream_status, body, expected):
    use_upstream(lambda request: httpx.Response(upstream_status, json=body))
    assert client.get("/api/history/dogecoin").status_code == expected


def test_network_failure(use_upstream):
    def handler(request):
        raise httpx.ConnectError("boom")

    use_upstream(handler)
    assert client.get("/api/history/dogecoin").status_code == 502


@pytest.mark.parametrize("query", ["days=0", "days=366", "vs_currency=US$"])
def test_rejects_bad_params(use_upstream, query):
    use_upstream(lambda request: pytest.fail("should not call upstream"))
    assert client.get(f"/api/history/dogecoin?{query}").status_code == 422


def test_rejects_bad_coin_id(use_upstream):
    use_upstream(lambda request: pytest.fail("should not call upstream"))
    assert client.get("/api/history/Doge..coin").status_code == 422
