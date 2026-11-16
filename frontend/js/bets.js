// Betting panel: place an up/down bet on the selected coin, show balance and bet history.
import { api, currentUser } from "/js/api.js";

const card = document.getElementById("bet-card");
const form = document.getElementById("bet-form");
const balanceEl = document.getElementById("balance");
const messageEl = document.getElementById("bet-message");
const body = document.getElementById("bets-body");
const filters = document.getElementById("filters");

const usd = (cents) => `$${(cents / 100).toFixed(2)}`;

function result(bet) {
  if (bet.status === "open") return `⏳ до ${new Date(bet.settles_at).toLocaleTimeString("uk-UA")}`;
  if (bet.status === "won") return `✅ +${usd(bet.payout - bet.stake)}`;
  if (bet.status === "push") return "➖ повернуто";
  if (bet.status === "error") return "⚠️ помилка ціни, ставку повернуто";
  return `❌ −${usd(bet.stake)}`;
}

async function refresh() {
  const [wallet, bets] = await Promise.all([api("/api/wallet"), api("/api/bets")]);
  balanceEl.textContent = usd(wallet.balance);
  body.replaceChildren(
    ...bets.map((bet) => {
      const tr = document.createElement("tr");
      for (const text of [bet.coin_id, bet.direction === "up" ? "▲" : "▼", usd(bet.stake), result(bet)]) {
        const td = document.createElement("td");
        td.textContent = text;
        tr.append(td);
      }
      return tr;
    }),
  );
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = new FormData(form, event.submitter);
  messageEl.className = "message";
  messageEl.textContent = "";
  try {
    await api("/api/bets", {
      method: "POST",
      body: {
        coin_id: new FormData(filters).get("coin"),
        direction: data.get("direction"),
        stake: Math.round(Number(data.get("stake")) * 100),
        seconds: Number(data.get("seconds")),
      },
    });
    messageEl.className = "message success";
    messageEl.textContent = "Ставку прийнято";
    await refresh();
  } catch (err) {
    messageEl.className = "message error";
    messageEl.textContent = err.message;
  }
});

if (await currentUser().catch(() => null)) {
  card.hidden = false;
  refresh().catch(() => {});
  setInterval(() => refresh().catch(() => {}), 5000); // settles finished bets
}
