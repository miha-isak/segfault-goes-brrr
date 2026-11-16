import asyncio
import pathlib
from contextlib import asynccontextmanager
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, FastAPI, Path, Query
from fastapi.staticfiles import StaticFiles

from app import auth, bets, coingecko
from app.db import init_db

FRONTEND_DIR = pathlib.Path(__file__).resolve().parents[2] / "frontend"


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()  # create tables once at startup
    task = asyncio.create_task(bets.settle_loop())
    yield
    task.cancel()


app = FastAPI(title="segfault-goes-brrr", lifespan=lifespan)

api = APIRouter(prefix="/api")

@api.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@api.get("/history/{coin_id}")
async def history(
    coin_id: Annotated[str, Path(pattern=r"^[a-z0-9-]{1,64}$")],
    days: Annotated[int, Query(ge=1, le=365)] = 7,
    vs_currency: Annotated[str, Query(pattern=r"^[a-z]{2,10}$")] = "usd",
    client: httpx.AsyncClient = Depends(coingecko.get_client),
) -> dict:
    prices = await coingecko.fetch_price_history(client, coin_id, vs_currency, days)
    return {"coin_id": coin_id, "vs_currency": vs_currency, "days": days, "prices": prices}


api.include_router(auth.router)
api.include_router(bets.router)
app.include_router(api)

# Mounted last so /api routes take precedence; serves index.html at "/".
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
