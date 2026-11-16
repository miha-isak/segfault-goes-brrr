// Юніт-тести логіки сторінки Tradeline. Запуск: cd frontend && node --test
import { test, describe } from 'node:test';
import assert from 'node:assert/strict';

import {
  COPY,
  LANGS,
  DEFAULT_LANG,
  DEFAULT_INSTRUMENTS,
  normalizeLang,
  translate,
  isValidEmail,
  validateEmail,
  formatChange,
  toggleWatched
} from '../js/tradeline-core.js';

describe('COPY (переклади)', () => {
  test('є українська та англійська', () => {
    assert.deepEqual(LANGS.sort(), ['en', 'uk']);
    assert.equal(DEFAULT_LANG, 'uk');
  });

  test('в обох мовах однаковий набір ключів', () => {
    assert.deepEqual(Object.keys(COPY.en).sort(), Object.keys(COPY.uk).sort());
  });

  test('жоден текст не порожній', () => {
    for (const lang of LANGS) {
      for (const [key, value] of Object.entries(COPY[lang])) {
        assert.ok(typeof value === 'string' && value.trim() !== '', `${lang}.${key} порожній`);
      }
    }
  });

  test('не залишилося заглушок на кшталт [ЧИСЛО] чи [NUMBER]', () => {
    for (const lang of LANGS) {
      for (const [key, value] of Object.entries(COPY[lang])) {
        assert.doesNotMatch(value, /\[[A-ZА-ЯІЇЄҐ]+\]/, `${lang}.${key}: ${value}`);
      }
    }
  });
});

describe('normalizeLang', () => {
  test('залишає відомі мови', () => {
    assert.equal(normalizeLang('uk'), 'uk');
    assert.equal(normalizeLang('en'), 'en');
  });

  test('невідома або порожня мова → мова за замовчуванням', () => {
    for (const value of ['de', '', undefined, null, 'EN']) {
      assert.equal(normalizeLang(value), DEFAULT_LANG);
    }
  });
});

describe('translate', () => {
  test('повертає текст потрібною мовою', () => {
    assert.equal(translate('uk', 'nav_login'), 'Увійти');
    assert.equal(translate('en', 'nav_login'), 'Log in');
  });

  test('невідомий ключ дає порожній рядок', () => {
    assert.equal(translate('en', 'no_such_key'), '');
  });

  test('невідома мова падає на українську', () => {
    assert.equal(translate('fr', 'nav_login'), 'Увійти');
  });
});

describe('isValidEmail', () => {
  test('приймає правильні адреси', () => {
    for (const email of ['name@example.com', 'a.b+tag@mail.co.uk', 'x@y.io']) {
      assert.equal(isValidEmail(email), true, email);
    }
  });

  test('відхиляє неправильні адреси', () => {
    for (const email of ['', 'name', 'name@', '@example.com', 'name@example', 'name@example.c', 'na me@example.com', 'name@@example.com']) {
      assert.equal(isValidEmail(email), false, email);
    }
  });
});

describe('validateEmail', () => {
  test('порожнє поле або лише пробіли → empty_err', () => {
    for (const value of ['', '   ', undefined, null]) {
      assert.deepEqual(validateEmail(value, 'cta_ok'), { type: 'error', key: 'empty_err' });
    }
  });

  test('неправильна адреса → login_err', () => {
    assert.deepEqual(validateEmail('not-an-email', 'cta_ok'), { type: 'error', key: 'login_err' });
  });

  test('правильна адреса → переданий ключ успіху', () => {
    assert.deepEqual(validateEmail('name@example.com', 'cta_ok'), { type: 'success', key: 'cta_ok' });
    assert.deepEqual(validateEmail('name@example.com', 'login_ok'), { type: 'success', key: 'login_ok' });
  });

  test('пробіли навколо адреси обрізаються', () => {
    assert.equal(validateEmail('  name@example.com  ', 'cta_ok').type, 'success');
  });

  test('усі ключі, які повертає перевірка, мають переклад', () => {
    for (const key of ['empty_err', 'login_err', 'cta_ok', 'login_ok']) {
      for (const lang of LANGS) assert.notEqual(translate(lang, key), '', `${lang}.${key}`);
    }
  });
});

describe('formatChange', () => {
  test('зростання', () => {
    assert.deepEqual(formatChange(0.32), { direction: 'up', text: '▲ +0.32%' });
  });

  test('падіння, зі справжнім знаком мінус', () => {
    assert.deepEqual(formatChange(-0.85), { direction: 'down', text: '▼ −0.85%' });
  });

  test('нуль вважається зростанням', () => {
    assert.deepEqual(formatChange(0), { direction: 'up', text: '▲ +0.00%' });
  });

  test('округлення до двох знаків', () => {
    assert.equal(formatChange(1.739).text, '▲ +1.74%');
    assert.equal(formatChange(-12.3).text, '▼ −12.30%');
  });
});

describe('toggleWatched', () => {
  const list = [
    { symbol: 'A', watched: false },
    { symbol: 'B', watched: true }
  ];

  test('перемикає лише вибраний інструмент', () => {
    assert.deepEqual(toggleWatched(list, 0), [
      { symbol: 'A', watched: true },
      { symbol: 'B', watched: true }
    ]);
    assert.deepEqual(toggleWatched(list, 1)[1], { symbol: 'B', watched: false });
  });

  test('не змінює вихідний масив', () => {
    const before = structuredClone(list);
    toggleWatched(list, 0);
    assert.deepEqual(list, before);
  });

  test('подвійне перемикання повертає початковий стан', () => {
    assert.deepEqual(toggleWatched(toggleWatched(list, 0), 0), list);
  });

  test('індекс поза списком нічого не змінює', () => {
    assert.deepEqual(toggleWatched(list, 5), list);
  });
});

describe('DEFAULT_INSTRUMENTS', () => {
  test('кожен інструмент має символ, ціну, зміну й не відстежується на старті', () => {
    assert.ok(DEFAULT_INSTRUMENTS.length > 0);
    for (const item of DEFAULT_INSTRUMENTS) {
      assert.equal(typeof item.symbol, 'string');
      assert.equal(typeof item.price, 'string');
      assert.equal(typeof item.change, 'number');
      assert.equal(item.watched, false);
    }
  });

  test('символи не повторюються', () => {
    const symbols = DEFAULT_INSTRUMENTS.map(i => i.symbol);
    assert.equal(new Set(symbols).size, symbols.length);
  });
});
