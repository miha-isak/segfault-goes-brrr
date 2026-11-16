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
