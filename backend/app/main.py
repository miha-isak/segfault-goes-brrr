from pathlib import Path

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app import auth

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

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


api.include_router(auth.router)
app.include_router(api)

# Mounted last so /api routes take precedence; serves index.html at "/".
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
