// A single-series price line drawn as SVG, with a crosshair + tooltip on hover/keyboard.
const SVG = "http://www.w3.org/2000/svg";
const HEIGHT = 300;
const PAD = { top: 12, right: 12, bottom: 28, left: 72 };

function el(name, attrs = {}, parent) {
  const node = document.createElementNS(SVG, name);
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
  parent?.append(node);
  return node;
}

// ~count "nice" round values covering [min, max].
function niceTicks(min, max, count = 5) {
  if (min === max) return [min];
  const raw = (max - min) / count;
  const magnitude = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * magnitude).find((s) => s >= raw);
  const ticks = [];
  for (let v = Math.ceil(min / step) * step; v <= max + step / 1e6; v += step) ticks.push(v);
  return ticks;
}

/**
 * Draw `points` ([[timestampMs, price], ...]) into `svg`.
 * formatPrice / formatTime turn values into text; tooltip is a positioned <div>.
 */
export function renderChart(svg, tooltip, points, { formatPrice, formatTime, formatTick }) {
  const width = svg.parentElement.clientWidth;
  svg.replaceChildren(svg.querySelector("title"));
  svg.setAttribute("viewBox", `0 0 ${width} ${HEIGHT}`);
  svg.setAttribute("height", HEIGHT);
  tooltip.hidden = true;
  if (points.length < 2) return;

  const times = points.map((p) => p[0]);
  const prices = points.map((p) => p[1]);
  const [t0, t1] = [times[0], times.at(-1)];
  let [lo, hi] = [Math.min(...prices), Math.max(...prices)];
  const margin = (hi - lo) * 0.05 || hi * 0.01;
  [lo, hi] = [lo - margin, hi + margin];

  const x = (t) => PAD.left + ((t - t0) / (t1 - t0)) * (width - PAD.left - PAD.right);
  const y = (p) => PAD.top + (1 - (p - lo) / (hi - lo)) * (HEIGHT - PAD.top - PAD.bottom);

  // Grid + y labels
  for (const tick of niceTicks(lo, hi)) {
    el("line", { class: "grid", x1: PAD.left, x2: width - PAD.right, y1: y(tick), y2: y(tick) }, svg);
    const label = el("text", { class: "axis-label", x: PAD.left - 8, y: y(tick), "text-anchor": "end", "dominant-baseline": "middle" }, svg);
    label.textContent = formatPrice(tick);
  }
  // X labels: a few evenly spaced times
  const xCount = Math.max(2, Math.floor((width - PAD.left - PAD.right) / 120));
  for (let i = 0; i <= xCount; i++) {
    const t = t0 + ((t1 - t0) * i) / xCount;
    const anchor = i === 0 ? "start" : i === xCount ? "end" : "middle";
    const label = el("text", { class: "axis-label", x: x(t), y: HEIGHT - 8, "text-anchor": anchor }, svg);
    label.textContent = formatTick(t);
  }
  el("line", { class: "baseline", x1: PAD.left, x2: width - PAD.right, y1: HEIGHT - PAD.bottom, y2: HEIGHT - PAD.bottom }, svg);

  // Area + line
  const path = points.map(([t, p], i) => `${i ? "L" : "M"}${x(t).toFixed(1)},${y(p).toFixed(1)}`).join("");
  el("path", { class: "area", d: `${path}L${x(t1)},${HEIGHT - PAD.bottom}L${x(t0)},${HEIGHT - PAD.bottom}Z` }, svg);
  el("path", { class: "line", d: path }, svg);

  // Hover layer: crosshair snaps to the nearest point.
  const crosshair = el("line", { class: "crosshair", y1: PAD.top, y2: HEIGHT - PAD.bottom, visibility: "hidden" }, svg);
  const dot = el("circle", { class: "dot", r: 4, visibility: "hidden" }, svg);
  const hit = el("rect", { x: PAD.left, y: 0, width: width - PAD.left - PAD.right, height: HEIGHT, fill: "transparent", tabindex: 0 }, svg);
  hit.setAttribute("aria-label", "Наведіть або використовуйте стрілки, щоб побачити ціну");
  let index = points.length - 1;

  function show(i) {
    index = Math.max(0, Math.min(points.length - 1, i));
    const [t, p] = points[index];
    for (const node of [crosshair, dot]) node.setAttribute("visibility", "visible");
    crosshair.setAttribute("x1", x(t));
    crosshair.setAttribute("x2", x(t));
    dot.setAttribute("cx", x(t));
    dot.setAttribute("cy", y(p));
    const value = document.createElement("strong");
    value.textContent = formatPrice(p);
    const time = document.createElement("span");
    time.textContent = formatTime(t);
    tooltip.replaceChildren(value, time);
    tooltip.hidden = false;
    const left = Math.min(x(t) + 12, width - tooltip.offsetWidth - 4);
    tooltip.style.left = `${left < x(t) ? x(t) - tooltip.offsetWidth - 12 : left}px`;
    tooltip.style.top = `${Math.max(0, y(p) - tooltip.offsetHeight - 12)}px`;
  }
  function hide() {
    for (const node of [crosshair, dot]) node.setAttribute("visibility", "hidden");
    tooltip.hidden = true;
  }
  function nearest(clientX) {
    const px = clientX - svg.getBoundingClientRect().left;
    const t = t0 + ((px - PAD.left) / (width - PAD.left - PAD.right)) * (t1 - t0);
    let best = 0;
    for (let i = 1; i < times.length; i++) if (Math.abs(times[i] - t) < Math.abs(times[best] - t)) best = i;
    return best;
  }

  hit.addEventListener("pointermove", (e) => show(nearest(e.clientX)));
  hit.addEventListener("pointerleave", hide);
  hit.addEventListener("focus", () => show(index));
  hit.addEventListener("blur", hide);
  hit.addEventListener("keydown", (e) => {
    const step = { ArrowLeft: -1, ArrowRight: 1, Home: -Infinity, End: Infinity }[e.key];
    if (step === undefined) return;
    e.preventDefault();
    show(Number.isFinite(step) ? index + step : step < 0 ? 0 : points.length - 1);
  });
}
