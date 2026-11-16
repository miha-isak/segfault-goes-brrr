# segfault-goes-brrr

- `frontend/` — plain HTML, CSS and JavaScript (no build step)
- `backend/` — FastAPI (managed with [uv](https://docs.astral.sh/uv/)); also serves `frontend/`

## Development

```bash
cd backend
uv sync
uv run fastapi dev app/main.py
```

### CoinGecko API key

Prices come from CoinGecko. Without a key it works, but hits the rate limit quickly.
Put the team's Demo key in `backend/.env` (ignored by git — never commit it):

```bash
echo 'COINGECKO_API_KEY=CG-...' > backend/.env
cd backend && uv run --env-file .env fastapi dev app/main.py
```

Open http://localhost:8000. API routes live under `/api` (docs at `/docs`).
Frontend code calls `fetch("/api/...")` — same origin, so no CORS setup is needed.

## Tests

```bash
cd backend && uv run pytest
```

Frontend unit tests (Node 22+, no dependencies):

```bash
cd frontend && node --test
```


## API for scripts (quant mode)

Log in on the site, open "API для скриптів", and create a key (shown once, stored only as a hash).
Send it as `Authorization: Bearer <key>` or `X-API-Key: <key>`. Limit: 60 requests/minute per key.

| Endpoint | Auth | What |
|---|---|---|
| `GET /api/prices` | none | live USD prices + 24h change for all coins |
| `GET /api/history/{coin}?days=7` | none | price history |
| `GET /api/wallet` | key | balance in cents |
| `POST /api/bets` | key | `{"coin_id","direction":"up"/"down","stake":cents,"seconds":5-3600}` |
| `GET /api/bets` | key | your last 50 bets |

```python
import requests
BASE = "https://segfault-goes-brrrrrrr.duckdns.org/api"
H = {"Authorization": "Bearer sgb_..."}
print(requests.get(f"{BASE}/wallet", headers=H).json())
bet = {"coin_id": "bitcoin", "direction": "up", "stake": 1000, "seconds": 60}
print(requests.post(f"{BASE}/bets", json=bet, headers=H).json())
```
