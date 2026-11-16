# segfault-goes-brrr

- `frontend/` — plain HTML, CSS and JavaScript (no build step)
- `backend/` — FastAPI (managed with [uv](https://docs.astral.sh/uv/)); also serves `frontend/`

## Development

```bash
cd backend
uv sync
uv run fastapi dev app/main.py
```

Open http://localhost:8000. API routes live under `/api` (docs at `/docs`).
Frontend code calls `fetch("/api/...")` — same origin, so no CORS setup is needed.

## Tests

```bash
cd backend && uv run pytest
```
