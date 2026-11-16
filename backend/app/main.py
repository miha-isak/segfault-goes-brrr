import pathlib
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Path, Query
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app import auth, coingecko

FRONTEND_DIR = pathlib.Path(__file__).resolve().parents[2] / "frontend"

app = FastAPI(title="segfault-goes-brrr")

api = APIRouter(prefix="/api")

# In-memory store for now; data is lost on restart.
tasks = [
    {"id": 1, "text": "Подивитись, як працює fetch", "done": True},
    {"id": 2, "text": "Написати перший POST-запит", "done": False},
]
next_id = 3


class TaskCreate(BaseModel):
    text: str


def find_task(task_id: int) -> dict:
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Задачу з таким id не знайдено")


@api.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@api.get("/tasks")
def get_tasks() -> list[dict]:
    return tasks


@api.post("/tasks", status_code=201)
def create_task(task: TaskCreate) -> dict:
    global next_id
    text = task.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Поле text не може бути порожнім")
    new_task = {"id": next_id, "text": text, "done": False}
    tasks.append(new_task)
    next_id += 1
    return new_task


# Toggle/delete use POST by team convention (no PUT/DELETE for now).
@api.post("/tasks/{task_id}/toggle")
def toggle_task(task_id: int) -> dict:
    task = find_task(task_id)
    task["done"] = not task["done"]
    return task


@api.post("/tasks/{task_id}/delete")
def delete_task(task_id: int) -> dict:
    tasks.remove(find_task(task_id))
    return {"message": "Видалено", "id": task_id}


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
app.include_router(api)

# Mounted last so /api routes take precedence; serves index.html at "/".
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
