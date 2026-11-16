import {
  DEFAULT_LANG,
  DEFAULT_INSTRUMENTS,
  normalizeLang,
  translate,
  validateEmail,
  formatChange,
  toggleWatched
} from '/js/tradeline-core.js';

let lang = DEFAULT_LANG;
let instruments = DEFAULT_INSTRUMENTS;

const watchlistEl = document.getElementById('watchlist');

function t(key) {
  return translate(lang, key);
}

function showMessage(el, text, type) {
  el.textContent = text;
  el.className = 'message' + (type ? ' ' + type : '');
}

function renderWatchlist() {
  watchlistEl.innerHTML = '';

  instruments.forEach((item, index) => {
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

    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = item.watched ? t('unwatch') : t('watch');
    button.addEventListener('click', () => {
      instruments = toggleWatched(instruments, index);
      renderWatchlist();
    });

    li.append(text, price, change, button);
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

  showMessage(document.getElementById('signup-message'), '');
  showMessage(document.getElementById('login-message'), '');
  renderWatchlist();
}

function handleEmailForm(formId, inputId, messageId, successKey) {
  const form = document.getElementById(formId);
  const input = document.getElementById(inputId);
  const message = document.getElementById(messageId);

  form.addEventListener('submit', event => {
    event.preventDefault();
    const result = validateEmail(input.value, successKey);
    showMessage(message, t(result.key), result.type);
    if (result.type === 'success') input.value = '';
    input.focus();
  });
}

document.querySelectorAll('.lang button').forEach(btn => {
  btn.addEventListener('click', () => applyLang(btn.dataset.lang));
});

handleEmailForm('signup-form', 'signup-email', 'signup-message', 'cta_ok');
handleEmailForm('login-form', 'login-email', 'login-message', 'login_ok');

applyLang(lang);
