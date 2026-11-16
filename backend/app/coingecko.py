"""Thin client for the CoinGecko public API."""

import time
from collections.abc import AsyncIterator

import httpx
from fastapi import HTTPException

from app.config import settings

BASE_URL = "https://api.coingecko.com/api/v3"


async def get_client() -> AsyncIterator[httpx.AsyncClient]:
    """FastAPI dependency yielding a CoinGecko HTTP client.

    Sends the free Demo API key if COINGECKO_API_KEY is set; works keyless otherwise.
    """
    headers = {"accept": "application/json"}
    api_key = settings.coingecko_api_key
    if api_key:
        headers["x-cg-demo-api-key"] = api_key
    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=10) as client:
        yield client


async def fetch_price_history(
    client: httpx.AsyncClient, coin_id: str, vs_currency: str, days: int
) -> list[list[float]]:
    """Return [[timestamp_ms, price], ...] for the last `days` days."""
    try:
        response = await client.get(
            f"/coins/{coin_id}/market_chart",
            params={"vs_currency": vs_currency, "days": days},
        )
    except httpx.HTTPError:
        raise HTTPException(502, "CoinGecko is unreachable")

    if response.status_code == 404:
        raise HTTPException(404, f"Unknown coin '{coin_id}'")
    if response.status_code == 400:
        raise HTTPException(400, _upstream_error(response) or "Invalid request")
    if response.status_code == 429:
        raise HTTPException(429, "CoinGecko rate limit reached, try again later")
    if response.is_error:
        raise HTTPException(502, f"CoinGecko returned HTTP {response.status_code}")

    try:
        return response.json()["prices"]
    except (ValueError, KeyError, TypeError):
        raise HTTPException(502, "Unexpected response from CoinGecko")


def _upstream_error(response: httpx.Response) -> str | None:
    try:
        error = response.json().get("error")
    except (ValueError, AttributeError):
        return None
    return error if isinstance(error, str) else None


_price_cache: dict[tuple[str, str], tuple[float, object]] = {}
PRICE_TTL = 10  # seconds; keeps us under CoinGecko's rate limit (display prices only)
FRESH_TTL = 1  # bets use (almost) uncached prices so entry/exit prices are accurate


def make_client() -> httpx.AsyncClient:
    """A standalone client (for background tasks, outside a request)."""
    headers = {"accept": "application/json"}
    if settings.coingecko_api_key:
        headers["x-cg-demo-api-key"] = settings.coingecko_api_key
    return httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=10)


async def fetch_prices(client: httpx.AsyncClient, coin_ids: list[str]) -> dict[str, dict]:
    """{coin: {"price": usd, "change": 24h %}} for several coins in one call (cached)."""
    key = ("__all__:" + ",".join(coin_ids), "usd")
    cached = _price_cache.get(key)
    if cached and time.monotonic() - cached[0] < PRICE_TTL:
        return cached[1]
    try:
        response = await client.get(
            "/simple/price",
            params={"ids": ",".join(coin_ids), "vs_currencies": "usd", "include_24hr_change": "true"},
        )
    except httpx.HTTPError:
        raise HTTPException(502, "CoinGecko is unreachable")
    if response.status_code == 429:
        raise HTTPException(429, "CoinGecko rate limit reached, try again later")
    if response.is_error:
        raise HTTPException(502, f"CoinGecko returned HTTP {response.status_code}")
    try:
        data = response.json()
        out = {
            c: {"price": float(data[c]["usd"]), "change": data[c].get("usd_24h_change")}
            for c in coin_ids if c in data
        }
    except (ValueError, KeyError, TypeError):
        raise HTTPException(502, "Unexpected response from CoinGecko")
    _price_cache[key] = (time.monotonic(), out)
    return out


async def fetch_price(
    client: httpx.AsyncClient, coin_id: str, vs_currency: str = "usd", fresh: bool = False
) -> float:
    """Current price of a coin, cached for PRICE_TTL seconds (FRESH_TTL if fresh=True)."""
    key = (coin_id, vs_currency)
    cached = _price_cache.get(key)
    if cached and time.monotonic() - cached[0] < (FRESH_TTL if fresh else PRICE_TTL):
        return cached[1]
    try:
        response = await client.get(
            "/simple/price", params={"ids": coin_id, "vs_currencies": vs_currency}
        )
    except httpx.HTTPError:
        raise HTTPException(502, "CoinGecko is unreachable")
    if response.status_code == 429:
        raise HTTPException(429, "CoinGecko rate limit reached, try again later")
    if response.is_error:
        raise HTTPException(502, f"CoinGecko returned HTTP {response.status_code}")
    try:
        price = float(response.json()[coin_id][vs_currency])
    except (ValueError, KeyError, TypeError):
        raise HTTPException(404, f"Unknown coin '{coin_id}'")
    _price_cache[key] = (time.monotonic(), price)
    return price
