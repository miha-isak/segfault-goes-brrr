"""
Бекенд на FastAPI.

Поки що тут тільки те, що відповідає за звʼязок з фронтендом:
- віддає статичні файли (index.html, style.css, script.js)
- має API, яке працює через GET і POST

Бази даних поки немає — замість неї звичайний список у памʼяті.
Перезапустив сервер — дані зникли. Для першого етапу це нормально.

Запуск:
    uvicorn main:app --reload --port 5000
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="Тестова звʼязка фронт-бек")


# ---------------------------------------------------------------
# "База даних" — просто список словників
# ---------------------------------------------------------------
tasks = [
    {"id": 1, "text": "Подивитись, як працює fetch", "done": True},
    {"id": 2, "text": "Написати перший POST-запит", "done": False},
]

next_id = 3  # id для наступної задачі


# ---------------------------------------------------------------
# Модель тіла POST-запиту.
# FastAPI сам перевірить, що у JSON є поле text і що це рядок.
# Якщо поля немає або тип не той — автоматично поверне 422.
# ---------------------------------------------------------------
class TaskCreate(BaseModel):
    text: str


# ---------------------------------------------------------------
# Віддача фронтенду
# ---------------------------------------------------------------

# Усі файли з папки static стають доступні за адресою /static/...
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def index():
    # Головна сторінка — це і є наша болванка
    return FileResponse("static/index.html")


# ---------------------------------------------------------------
# GET /api/tasks — віддати список усіх задач
# ---------------------------------------------------------------
@app.get("/api/tasks")
def get_tasks():
    return tasks


# ---------------------------------------------------------------
# POST /api/tasks — створити нову задачу
# Тіло запиту (JSON): {"text": "якась справа"}
# ---------------------------------------------------------------
@app.post("/api/tasks", status_code=201)
def create_task(task: TaskCreate):
    global next_id

    # strip() прибирає пробіли з початку і кінця
    text = task.text.strip()

    if text == "":
        raise HTTPException(status_code=400, detail="Поле text не може бути порожнім")

    new_task = {
        "id": next_id,
        "text": text,
        "done": False,
    }

    tasks.append(new_task)
    next_id += 1

    # 201 Created — так прийнято відповідати на успішне створення
    return new_task


# ---------------------------------------------------------------
# POST /api/tasks/<id>/toggle — перемкнути "зроблено / не зроблено"
# Використовуємо POST, бо DELETE/PUT поки домовились не використовувати
# ---------------------------------------------------------------
@app.post("/api/tasks/{task_id}/toggle")
def toggle_task(task_id: int):
    task = find_task(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Задачу з таким id не знайдено")

    task["done"] = not task["done"]

    return task


# ---------------------------------------------------------------
# POST /api/tasks/<id>/delete — видалити задачу
# ---------------------------------------------------------------
@app.post("/api/tasks/{task_id}/delete")
def delete_task(task_id: int):
    task = find_task(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Задачу з таким id не знайдено")

    tasks.remove(task)

    return {"message": "Видалено", "id": task_id}


# ---------------------------------------------------------------
# Допоміжна функція: знайти задачу по id
# ---------------------------------------------------------------
def find_task(task_id):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None
