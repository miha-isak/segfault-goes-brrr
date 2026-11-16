import { api, currentUser } from "/js/api.js";
import { renderChart } from "/js/chart.js";

const filters = document.getElementById("filters");
const chartBox = document.getElementById("chart");
const svg = document.getElementById("chart-svg");
const tooltip = document.getElementById("tooltip");
const message = document.getElementById("chart-message");
const priceEl = document.getElementById("price");
const changeEl = document.getElementById("change");
const tableBody = document.getElementById("table-body");
const account = document.getElementById("account");

let current = null; // last successful response, re-drawn on resize
let requestId = 0; // ignore responses to requests the user has already replaced

// ---------- account ----------

async function showAccount() {
  let user;
  try {
    user = await currentUser();
  } catch {
    account.textContent = "";
    return;
  }
  if (!user) {
    const link = document.createElement("a");
    link.href = "/login/";
    link.textContent = "Увійти / Зареєструватися";
    account.replaceChildren(link);
    return;
  }
  const name = document.createElement("span");
  name.textContent = `👤 ${user.username}`;
  const logout = document.createElement("button");
  logout.type = "button";
  logout.textContent = "Вийти";
  logout.addEventListener("click", async () => {
    await api("/api/auth/logout", { method: "POST" }).catch(() => {});
    showAccount();
  });
  account.replaceChildren(name, logout);
}

// ---------- formatting ----------

function formatters(currency, days) {
  const money = new Intl.NumberFormat("uk-UA", {
    style: "currency",
    currency: currency.toUpperCase(),
    maximumSignificantDigits: 4,
  });
  const dateTime = new Intl.DateTimeFormat("uk-UA", { dateStyle: "medium", timeStyle: "short" });
  const tick = new Intl.DateTimeFormat(
    "uk-UA",
    days <= 1 ? { hour: "2-digit", minute: "2-digit" } : days <= 90 ? { day: "numeric", month: "short" } : { month: "short", year: "2-digit" },
  );
  return {
    formatPrice: (v) => money.format(v),
    formatTime: (t) => dateTime.format(t),
    formatTick: (t) => tick.format(t),
  };
}

// ---------- data ----------

function draw() {
  if (!current) return;
  const fmt = formatters(current.vs_currency, current.days);
  renderChart(svg, tooltip, current.prices, fmt);
}

function showSummary() {
  const { prices, vs_currency, days } = current;
  const fmt = formatters(vs_currency, days);
  const first = prices[0][1];
  const last = prices.at(-1)[1];
  const pct = ((last - first) / first) * 100;
  priceEl.textContent = fmt.formatPrice(last);
  changeEl.textContent = `${pct >= 0 ? "▲" : "▼"} ${Math.abs(pct).toFixed(2)}% за період`;
  changeEl.className = `change ${pct >= 0 ? "up" : "down"}`;

  const rows = prices.map(([t, p]) => {
    const tr = document.createElement("tr");
    for (const text of [fmt.formatTime(t), fmt.formatPrice(p)]) {
      const td = document.createElement("td");
      td.textContent = text;
      tr.append(td);
    }
    return tr;
  });
  tableBody.replaceChildren(...rows.reverse());
}

async function load() {
  const form = new FormData(filters);
  const coin = form.get("coin");
  const params = new URLSearchParams({ days: form.get("days"), vs_currency: form.get("currency") });
  const id = ++requestId;

  chartBox.classList.add("loading"); // keep the old chart, dimmed, while loading
  message.className = "message";
  message.textContent = "Завантаження…";
  try {
    const data = await api(`/api/history/${encodeURIComponent(coin)}?${params}`);
    if (id !== requestId) return;
    if (data.prices.length < 2) throw new Error("Немає даних за цей період");
    current = data;
    svg.querySelector("title").textContent =
      `Ціна ${filters.coin.selectedOptions[0].text} у ${data.vs_currency.toUpperCase()} за ${data.days} дн.`;
    message.textContent = "";
    showSummary();
    draw();
  } catch (err) {
    if (id !== requestId) return;
    message.className = "message error";
    message.textContent = `Не вдалося завантажити дані: ${err.message}`;
  } finally {
    if (id === requestId) chartBox.classList.remove("loading");
  }
}

filters.addEventListener("change", load);
new ResizeObserver(draw).observe(chartBox);

showAccount();
load();
