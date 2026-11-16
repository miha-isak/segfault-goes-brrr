// API key management: create / revoke a key for scripts. The key is shown only once.
import { api, currentUser } from "/js/api.js";

const card = document.getElementById("api-card");
const status = document.getElementById("api-status");
const box = document.getElementById("api-key-box");

async function refresh() {
  const info = await api("/api/auth/api-key");
  status.textContent = info.has_key ? `Активний ключ: ${info.prefix}…` : "Ключа ще немає.";
}

document.getElementById("api-create").addEventListener("click", async () => {
  try {
    const res = await api("/api/auth/api-key", { method: "POST" });
    box.textContent = res.api_key;
    box.hidden = false;
    await refresh();
    status.textContent += " Скопіюйте ключ зараз: далі він не буде показаний.";
  } catch (err) {
    status.textContent = err.message;
  }
});

document.getElementById("api-revoke").addEventListener("click", async () => {
  try {
    await api("/api/auth/api-key", { method: "DELETE" });
    box.hidden = true;
    await refresh();
  } catch (err) {
    status.textContent = err.message;
  }
});

if (await currentUser().catch(() => null)) {
  card.hidden = false;
  refresh().catch(() => {});
}
