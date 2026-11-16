import { api } from "/js/api.js";

const message = document.getElementById("message");

function show(text, type) {
  message.textContent = text;
  message.className = `message ${type}`;
}

// Both forms send {username, password}. After registering we log in right away.
for (const form of document.querySelectorAll("form[data-endpoint]")) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const creds = Object.fromEntries(new FormData(form));
    const button = form.querySelector("button");
    button.disabled = true;
    show("…", "");
    try {
      if (form.dataset.endpoint === "/api/auth/register") {
        await api("/api/auth/register", { method: "POST", body: creds });
      }
      await api("/api/auth/login", { method: "POST", body: creds });
      location.href = "/";
    } catch (err) {
      show(err.message, "error");
      button.disabled = false;
    }
  });
}
