import { api } from "/js/api.js";

const message = document.getElementById("message");
const table = document.getElementById("board");
const body = document.getElementById("board-body");
const usd = new Intl.NumberFormat("uk-UA", { style: "currency", currency: "USD" });
const money = (cents) => usd.format(cents / 100);

try {
  const rows = await api("/api/leaderboard");
  if (rows.length === 0) {
    message.textContent = "Поки що ніхто не торгував.";
  } else {
    body.replaceChildren(
      ...rows.map((row) => {
        const tr = document.createElement("tr");
        for (const text of [row.rank, row.username, money(row.current), money(row.max)]) {
          const td = document.createElement("td");
          td.textContent = text;
          tr.append(td);
        }
        return tr;
      }),
    );
    message.textContent = "";
    table.hidden = false;
  }
} catch (err) {
  message.className = "message error";
  message.textContent = `Не вдалося завантажити лідерборд: ${err.message}`;
}
