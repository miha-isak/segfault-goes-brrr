const COPY = {
  uk: {
    nav_markets: 'Ринки', nav_why: 'Переваги', nav_start: 'Як почати', nav_login: 'Увійти',
    tagline: 'Навчальний тренажер для трейдерів',
    h1: 'Вчіться торгувати без ризику',
    lead: 'Практикуйтеся на віртуальні кошти: тестуйте стратегії на валютах, акціях та індексах, аналізуйте свої угоди й ростіть як трейдер. Без депозитів і без втрат.',
    email_label: 'Електронна пошта', email_ph: 'Ваш email',
    cta: 'Почати навчання', cta_hint: 'Безкоштовно. Реальні гроші та банківська картка не потрібні.',
    cta_ok: 'Дякуємо! Ми надіслали лист для підтвердження.',
    empty_err: 'Введіть email.',
    wl_title: 'Список спостереження', wl_note: 'Демонстраційні дані',
    watch: 'Стежити', unwatch: 'Не стежити',
    s1_n: '20+', s1_l: 'інструментів для практики',
    s2_n: '1 000 $', s2_l: 'віртуальних коштів на старті',
    s3_n: '0 ₴', s3_l: 'реальних грошей у грі',
    s4_n: '10+', s4_l: 'уроків і практичних завдань',
    why_h: 'Чому обирають Tradeline',
    why_p: 'Інструменти, які допомагають приймати рішення, а не відволікають від них.',
    f1_h: 'Графіки та аналітика', f1_p: 'Індикатори, малювання на графіку та сповіщення про рух ціни в одному вікні.',
    f2_h: 'Рейтинг і прогрес', f2_p: 'Статистика угод, історія помилок і таблиця лідерів, щоб бачити свій ріст і порівнювати результати.',
    f3_h: 'Уроки та практика', f3_p: 'Короткі уроки з теорії та завдання, результат яких ви одразу перевіряєте на віртуальному рахунку.',
    steps_h: 'Почніть за три кроки',
    st1_h: 'Зареєструйтесь', st1_p: 'Вкажіть email, і ваш навчальний акаунт готовий за хвилину.',
    st2_h: 'Отримайте віртуальні кошти', st2_p: 'Кожен новий учень одразу отримує стартовий віртуальний баланс для практики.',
    st3_h: 'Відкрийте першу угоду', st3_p: 'Оберіть інструмент, задайте обсяг і стоп-лосс та натисніть «Купити» або «Продати».',
    login_h: 'Вхід у кабінет', login_p: 'Введіть email, і ми надішлемо код для входу.',
    login_btn: 'Отримати код', login_ok: 'Код надіслано, перевірте пошту.',
    login_err: 'Перевірте адресу: схоже, в ній є помилка.',
    foot_terms: 'Умови', foot_priv: 'Конфіденційність', foot_support: 'Підтримка',
    foot_note: 'Tradeline — навчальна платформа. Уся торгівля відбувається на віртуальних коштах, реальні гроші не використовуються й не виводяться. Дані на цій сторінці демонстраційні та не є інвестиційною порадою.'
  },
  en: {
    nav_markets: 'Markets', nav_why: 'Features', nav_start: 'Get started', nav_login: 'Log in',
    tagline: 'Trading simulator for learners',
    h1: 'Learn to trade without risk',
    lead: 'Practice with virtual funds: test strategies on currencies, stocks and indices, review your trades and grow as a trader. No deposits, no losses.',
    email_label: 'Email address', email_ph: 'Your email',
    cta: 'Start learning', cta_hint: 'Free. No real money or bank card needed.',
    cta_ok: 'Thanks! We sent you a confirmation email.',
    empty_err: 'Please enter your email.',
    wl_title: 'Watchlist', wl_note: 'Sample data',
    watch: 'Watch', unwatch: 'Unwatch',
    s1_n: '20+', s1_l: 'instruments to practice on',
    s2_n: '$1,000', s2_l: 'virtual funds to start with',
    s3_n: '$0', s3_l: 'real money at stake',
    s4_n: '10+', s4_l: 'lessons and practice tasks',
    why_h: 'Why learners choose Tradeline',
    why_p: 'Tools that help you make decisions instead of distracting you from them.',
    f1_h: 'Charts and analytics', f1_p: 'Indicators, chart drawing and price alerts in a single window.',
    f2_h: 'Ranking and progress', f2_p: 'Trade statistics, a history of mistakes and a leaderboard to see your growth and compare results.',
    f3_h: 'Lessons and practice', f3_p: 'Short theory lessons and tasks whose results you check right away on a virtual account.',
    steps_h: 'Get started in three steps',
    st1_h: 'Sign up', st1_p: 'Enter your email and your learning account is ready in a minute.',
    st2_h: 'Get virtual funds', st2_p: 'Every new learner instantly receives a starting virtual balance to practice with.',
    st3_h: 'Open your first trade', st3_p: 'Pick an instrument, set the size and a stop-loss, then press Buy or Sell.',
    login_h: 'Log in to your account', login_p: 'Enter your email and we will send you a sign-in code.',
    login_btn: 'Get code', login_ok: 'Code sent, check your inbox.',
    login_err: 'Check the address: it looks like it contains a mistake.',
    foot_terms: 'Terms', foot_priv: 'Privacy', foot_support: 'Support',
    foot_note: 'Tradeline is a learning platform. All trading uses virtual funds; no real money is used or withdrawn. Data on this page is for demonstration only and is not investment advice.'
  }
};

// Демонстраційні дані для списку спостереження
const instruments = [
  { symbol: 'EUR/USD', price: '1.0850', change: 0.32, watched: false },
  { symbol: 'AAPL', price: '189.40', change: -0.85, watched: false },
  { symbol: 'BTC/USD', price: '37,250', change: 1.74, watched: false },
  { symbol: 'S&P 500', price: '4,510', change: 0.41, watched: false },
  { symbol: 'XAU/USD', price: '1,985', change: -0.12, watched: false }
];

let lang = 'uk';

const watchlistEl = document.getElementById('watchlist');

function t(key) {
  return COPY[lang][key] ?? '';
}

function isValidEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value);
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
    const up = item.change >= 0;
    change.className = 'change ' + (up ? 'up' : 'down');
    change.textContent = (up ? '▲ +' : '▼ −') + Math.abs(item.change).toFixed(2) + '%';

    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = item.watched ? t('unwatch') : t('watch');
    button.addEventListener('click', () => {
      instruments[index].watched = !instruments[index].watched;
      renderWatchlist();
    });

    li.append(text, price, change, button);
    watchlistEl.appendChild(li);
  });
}

function applyLang(next) {
  lang = next;
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
    const value = input.value.trim();

    if (value === '') {
      showMessage(message, t('empty_err'), 'error');
    } else if (!isValidEmail(value)) {
      showMessage(message, t('login_err'), 'error');
    } else {
      showMessage(message, t(successKey), 'success');
      input.value = '';
    }
    input.focus();
  });
}

document.querySelectorAll('.lang button').forEach(btn => {
  btn.addEventListener('click', () => applyLang(btn.dataset.lang));
});

handleEmailForm('signup-form', 'signup-email', 'signup-message', 'cta_ok');
handleEmailForm('login-form', 'login-email', 'login-message', 'login_ok');

applyLang(lang);
