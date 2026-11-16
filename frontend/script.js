
const API_URL = "/api/tasks";

const form = document.getElementById("task-form");
const input = document.getElementById("task-input");
const taskList = document.getElementById("task-list");
const message = document.getElementById("message");
const reloadButton = document.getElementById("reload-button");

function showMessage(text, type) {
  message.textContent = text;
  message.className = "message " + type;
}

function clearMessage() {
  message.textContent = "";
  message.className = "message";
}

function renderTasks(tasks) {
  taskList.innerHTML = ""; 

  if (tasks.length === 0) {
    const empty = document.createElement("li");
    empty.textContent = "Задач поки немає";
    taskList.appendChild(empty);
    return;
  }

  for (const task of tasks) {
    const li = document.createElement("li");

    const span = document.createElement("span");
    span.className = "text";
    if (task.done) {
      span.classList.add("done");
    }
    span.textContent = task.text;
    li.appendChild(span);

    const toggleButton = document.createElement("button");
    toggleButton.type = "button";
    toggleButton.textContent = task.done ? "Повернути" : "Зробити";
    toggleButton.addEventListener("click", function () {
      toggleTask(task.id);
    });
    li.appendChild(toggleButton);

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.textContent = "Видалити";
    deleteButton.addEventListener("click", function () {
      deleteTask(task.id);
    });
    li.appendChild(deleteButton);

    taskList.appendChild(li);
  }
}


async function loadTasks() {
  clearMessage();

  try {
    const response = await fetch(API_URL, { method: "GET" });

    // fetch не кидає помилку на 404/500, тому перевіряємо вручну
    if (!response.ok) {
      throw new Error("Сервер відповів статусом " + response.status);
    }

    const tasks = await response.json();
    renderTasks(tasks);
  } catch (error) {
    showMessage("Не вдалося завантажити задачі: " + error.message, "error");
  }
}


async function addTask(text) {
  clearMessage();

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text: text }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Помилка при створенні задачі");
    }

    showMessage("Задачу додано", "success");
    input.value = "";
    loadTasks();
  } catch (error) {
    showMessage(error.message, "error");
  }
}


async function toggleTask(id) {
  clearMessage();

  try {
    const response = await fetch(API_URL + "/" + id + "/toggle", {
      method: "POST",
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Не вдалося змінити задачу");
    }

    loadTasks();
  } catch (error) {
    showMessage(error.message, "error");
  }
}


// ------------------------------------------------------------
// POST /api/tasks/<id>/delete — видалити задачу
// ------------------------------------------------------------
async function deleteTask(id) {
  clearMessage();

  try {
    const response = await fetch(API_URL + "/" + id + "/delete", {
      method: "POST",
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Не вдалося видалити задачу");
    }

    loadTasks();
  } catch (error) {
    showMessage(error.message, "error");
  }
}


// ------------------------------------------------------------
// Обробники подій + перше завантаження
// ------------------------------------------------------------
form.addEventListener("submit", function (event) {
  // щоб браузер не перезавантажував сторінку
  event.preventDefault();

  const text = input.value.trim();

  if (text === "") {
    showMessage("Спочатку напиши текст задачі", "error");
    return;
  }

  addTask(text);
});

reloadButton.addEventListener("click", function () {
  loadTasks();
});

// Коли сторінка завантажилась — одразу робимо GET
loadTasks();
