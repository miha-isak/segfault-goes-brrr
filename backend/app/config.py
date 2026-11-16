"""Application settings, read once from environment variables.

In production the variables come from /opt/app/.env via docker compose.
"""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    db_path: Path = Path(
        os.environ.get("DB_PATH", Path(__file__).parent.parent / "app.db")
    )
    # Set COOKIE_SECURE=true when served over HTTPS (docker-compose does this).
    cookie_secure: bool = os.environ.get("COOKIE_SECURE", "").lower() in ("1", "true", "yes")
    # Optional CoinGecko Demo API key (set in /opt/app/.env); the API also works without one.
    coingecko_api_key: str | None = os.environ.get("COINGECKO_API_KEY") or None


settings = Settings()
