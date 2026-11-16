import {
  DEFAULT_LANG,
  DEFAULT_INSTRUMENTS,
  normalizeLang,
  translate,
  formatChange,
  instrumentsFromPrices
} from '/js/tradeline-core.js';

let lang = DEFAULT_LANG;
let instruments = DEFAULT_INSTRUMENTS;

const watchlistEl = document.getElementById('watchlist');

function t(key) {
  return translate(lang, key);
}

function renderWatchlist() {
  watchlistEl.innerHTML = '';

  instruments.forEach(item => {
    const li = document.createElement('li');
    if (item.watched) li.classList.add('watched');

    const text = document.createElement('span');
    text.className = 'text';
    text.textContent = item.symbol;

    const price = document.createElement('span');
    price.className = 'price';
    price.textContent = item.price;

    const change = document.createElement('span');
    const formatted = formatChange(item.change);
    change.className = 'change ' + formatted.direction;
    change.textContent = formatted.text;


    li.append(text, price, change);
    watchlistEl.appendChild(li);
  });
}

function applyLang(next) {
  lang = normalizeLang(next);
  document.documentElement.lang = lang;

  document.querySelectorAll('[data-i18n]').forEach(el => {
    el.textContent = t(el.dataset.i18n);
  });
  document.querySelectorAll('[data-i18n-ph]').forEach(el => {
    el.placeholder = t(el.dataset.i18nPh);
  });
  document.querySelectorAll('.lang button').forEach(btn => {
    const active = btn.dataset.lang === lang;
    btn.classList.toggle('active', active);
    btn.setAttribute('aria-pressed', String(active));
  });

  renderWatchlist();
}

document.querySelectorAll('.lang button').forEach(btn => {
  btn.addEventListener('click', () => applyLang(btn.dataset.lang));
});


applyLang(lang);

async function loadPrices() {
  const msg = document.getElementById('wl-msg');
  try {
    const res = await fetch('/api/prices');
    if (!res.ok) throw new Error();
    instruments = instrumentsFromPrices(await res.json(), instruments);
    msg.textContent = '';
  } catch {
    msg.textContent = t('wl_err');
  }
  renderWatchlist();
}

loadPrices();
setInterval(loadPrices, 15000);
