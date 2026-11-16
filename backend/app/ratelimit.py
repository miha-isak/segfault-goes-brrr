"""Tiny in-memory rate limiter (per client IP). Resets on restart; fine for one server."""

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request


class RateLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window = window_seconds
        self.hits: dict[str, deque[float]] = defaultdict(deque)

    def reset(self) -> None:
        self.hits.clear()

    def __call__(self, request: Request) -> None:
        self.check(client_ip(request))

    def check(self, key: str) -> None:
        now = time.monotonic()
        hits = self.hits[key]
        while hits and now - hits[0] > self.window:
            hits.popleft()
        if len(self.hits) > 1000:  # drop idle clients so the map can't grow forever
            for k in [k for k, v in self.hits.items() if not v or now - v[-1] > self.window]:
                if k != key:
                    del self.hits[k]
        if len(hits) >= self.limit:
            raise HTTPException(429, "Too many attempts, try again later")
        hits.append(now)


def client_ip(request: Request) -> str:
    # Caddy (the only way in) sets X-Forwarded-For to the real client address.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.client.host if request.client else "unknown"
