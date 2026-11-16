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


settings = Settings()
