// Чиста логіка сторінки Tradeline без роботи з DOM,
// щоб її можна було перевіряти юніт-тестами (frontend/tests).

export const COPY = {
  uk: {
    nav_markets: 'Ринки', nav_why: 'Переваги', nav_start: 'Як почати', nav_login: 'Увійти', nav_home: 'Головна',
    tagline: 'Ставки на мемкоїни віртуальними грошима',
    h1: 'Ставте на мемкоїни без ризику',
    lead: 'Прогнозуйте, чи ціна мемкоїна піде вгору чи вниз за обраний час. Віртуальний баланс, живі ціни, жодних реальних грошей.',
    email_label: 'Електронна пошта', email_ph: 'Ваш email',
    cta: 'Створити акаунт', cta_hint: 'Безкоштовно. Реальні гроші та банківська картка не потрібні.',
    cta_ok: 'Дякуємо! Ми надіслали лист для підтвердження.',
    empty_err: 'Введіть email.',
    wl_title: 'Список спостереження', wl_note: 'Живі ціни CoinGecko, USD', wl_err: 'Не вдалося завантажити ціни.',
    watch: 'Стежити', unwatch: 'Не стежити',
    s1_n: '11', s1_l: 'монет для ставок',
    s2_n: '1 000 $', s2_l: 'віртуальних коштів на старті',
    s3_n: '0 $', s3_l: 'реальних грошей у грі',
    s4_n: '5 с – 1 год', s4_l: 'тривалість ставки',
    why_h: 'Чому Tradeline',
    why_p: 'Прості інструменти, реальні ціни, віртуальні гроші.',
    f1_h: 'Живі графіки', f1_p: 'Історія цін за 24 год, 7, 30, 90 днів або рік з підказками при наведенні.',
    f2_h: 'Ставки вгору/вниз', f2_p: 'Оберіть монету, суму та час: виграш подвоює ставку, програш її забирає.',
    f3_h: 'Віртуальний гаманець', f3_p: 'Кожен новий гравець отримує стартовий баланс; усі ставки та виплати записуються в історію.',
    steps_h: 'Почніть за три кроки',
    st1_h: 'Зареєструйтесь', st1_p: 'Придумайте логін і пароль, і акаунт готовий за хвилину.',
    st2_h: 'Отримайте віртуальні кошти', st2_p: 'Кожен новий гравець одразу отримує стартовий віртуальний баланс.',
    st3_h: 'Відкрийте першу угоду', st3_p: 'Оберіть монету, суму й час та натисніть «Вгору» або «Вниз».',
    login_h: 'Вхід у кабінет', login_p: 'Введіть email, і ми надішлемо код для входу.',
    login_btn: 'Отримати код', login_ok: 'Код надіслано, перевірте пошту.',
    login_err: 'Перевірте адресу: схоже, в ній є помилка.',
    foot_terms: 'Умови', foot_priv: 'Конфіденційність', foot_support: 'Підтримка',
    foot_note: 'Tradeline — навчальний проєкт. Уся гра відбувається на віртуальних коштах. Це не інвестиційна порада.'
  },
  en: {
    nav_markets: 'Markets', nav_why: 'Features', nav_start: 'Get started', nav_login: 'Log in', nav_home: 'Home',
    tagline: 'Virtual-money bets on meme coins',
    h1: 'Bet on meme coins without risk',
    lead: 'Predict whether a meme coin price goes up or down within a chosen time. Virtual balance, live prices, no real money.',
    email_label: 'Email address', email_ph: 'Your email',
    cta: 'Create account', cta_hint: 'Free. No real money or bank card needed.',
    cta_ok: 'Thanks! We sent you a confirmation email.',
    empty_err: 'Please enter your email.',
    wl_title: 'Watchlist', wl_note: 'Live CoinGecko prices, USD', wl_err: 'Could not load prices.',
    watch: 'Watch', unwatch: 'Unwatch',
    s1_n: '11', s1_l: 'coins to bet on',
    s2_n: '$1,000', s2_l: 'virtual funds to start with',
    s3_n: '$0', s3_l: 'real money at stake',
    s4_n: '5 s – 1 h', s4_l: 'bet duration',
    why_h: 'Why Tradeline',
    why_p: 'Simple tools, real prices, virtual money.',
    f1_h: 'Live charts', f1_p: 'Price history for 24 h, 7, 30, 90 days or a year with hover tooltips.',
    f2_h: 'Up/down bets', f2_p: 'Pick a coin, stake and time: a win doubles your stake, a loss takes it.',
    f3_h: 'Virtual wallet', f3_p: 'Every new player gets a starting balance; all stakes and payouts are recorded.',
    steps_h: 'Get started in three steps',
    st1_h: 'Sign up', st1_p: 'Pick a username and password and your account is ready in a minute.',
    st2_h: 'Get virtual funds', st2_p: 'Every new player instantly receives a starting virtual balance.',
    st3_h: 'Open your first trade', st3_p: 'Pick a coin, stake and time, then press Up or Down.',
    login_h: 'Log in to your account', login_p: 'Enter your email and we will send you a sign-in code.',
    login_btn: 'Get code', login_ok: 'Code sent, check your inbox.',
    login_err: 'Check the address: it looks like it contains a mistake.',
    foot_terms: 'Terms', foot_priv: 'Privacy', foot_support: 'Support',
    foot_note: 'Tradeline is a learning project. All play uses virtual funds. Not investment advice.'
  }
};

export const LANGS = Object.keys(COPY);
export const DEFAULT_LANG = 'uk';

// Демонстраційні дані для списку спостереження
export const COIN_NAMES = {
  bitcoin: 'Bitcoin', ethereum: 'Ethereum', solana: 'Solana', binancecoin: 'BNB', ripple: 'XRP',
  dogecoin: 'Dogecoin', 'shiba-inu': 'Shiba Inu', pepe: 'Pepe',
  dogwifcoin: 'dogwifhat', bonk: 'Bonk', floki: 'Floki'
};

// Поки живі ціни не завантажені: ті самі монети, що й у ставках, без ціни.
export const DEFAULT_INSTRUMENTS = Object.values(COIN_NAMES).map(symbol => (
  { symbol, price: '—', change: 0, watched: false }
));

// Відповідь /api/prices -> список інструментів; стан "стежу" зберігається.
export function instrumentsFromPrices(data, previous = []) {
  return Object.entries(data).map(([id, d]) => {
    const symbol = COIN_NAMES[id] || id;
    const old = previous.find(i => i.symbol === symbol);
    return {
      symbol,
      price: '$' + Number(d.price).toPrecision(4),
      change: d.change ?? 0,
      watched: old ? old.watched : false
    };
  });
}

// Мова, яку реально можна показати: невідома мова → мова за замовчуванням.
export function normalizeLang(lang) {
  return LANGS.includes(lang) ? lang : DEFAULT_LANG;
}

// Переклад за ключем; невідомий ключ дає порожній рядок, а не "undefined".
export function translate(lang, key) {
  return COPY[normalizeLang(lang)][key] ?? '';
}

export function isValidEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value);
}

// Результат перевірки поля email у формі: тип повідомлення і ключ тексту.
export function validateEmail(rawValue, successKey) {
  const value = String(rawValue ?? '').trim();
  if (value === '') return { type: 'error', key: 'empty_err' };
  if (!isValidEmail(value)) return { type: 'error', key: 'login_err' };
  return { type: 'success', key: successKey };
}

// Зміна ціни у відсотках: напрям для CSS-класу і текст зі стрілкою.
export function formatChange(change) {
  const up = change >= 0;
  return {
    direction: up ? 'up' : 'down',
    text: (up ? '▲ +' : '▼ −') + Math.abs(change).toFixed(2) + '%'
  };
}

// Новий список, де в інструмента з індексом index перемкнуто "стежу".
// Вихідний масив не змінюється.
export function toggleWatched(instruments, index) {
  return instruments.map((item, i) =>
    i === index ? { ...item, watched: !item.watched } : item
  );
}
