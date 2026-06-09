# 🛒 Кошык — Telegram Mini App для сумесных пакупак

Бот і міні-праграма для вядзення агульнага спіса пакупак у Telegram-групе.  
Інтэрфейс на **беларускай мове**. Дэплой на Vercel + Supabase (абодва бясплатна).

## Стэк

| Слой | Тэхналогія |
|------|-----------|
| Frontend | React 18 + Vite |
| Backend | Python (Vercel Serverless Functions) |
| База даных | PostgreSQL (Supabase) |
| Хостынг | Vercel |

## Магчымасці

- 📋 Агульны спіс тавараў для групы
- 🙋 Узяць тавар — іншыя бачаць хто што бярэ
- ✅ Адзначаць купленае з анімацыяй collapse + fade
- 💰 Улік выдаткаў і аўтаматычны баланс
- 🔔 Push-апавяшчэнні ў групу пры кожным дзеянні
- ⚙️ Кіраванне апавяшчэннямі прама з праграмы
- 🛒 Кнопка адкрыцця спіса ў апавяшчэнні аб даданні тавара

## Структура праекта

```
├── api/
│   ├── webhook.py      ← Telegram бот (/start, deep link)
│   ├── items.py        ← API спіса пакупак
│   ├── expenses.py     ← API выдаткаў і балансу
│   ├── notify.py       ← адпраўка апавяшчэнняў у групу
│   └── settings.py     ← API налад апавяшчэнняў
├── webapp/
│   ├── index.html      ← кропка ўваходу
│   ├── vite.config.js  ← налады Vite
│   ├── package.json
│   └── src/
│       ├── main.jsx        ← createRoot(<App />)
│       ├── App.jsx         ← навігацыя + роўтынг старонак
│       ├── index.css       ← усе стылі
│       ├── tg.js           ← Telegram кантэкст, haptic
│       ├── api.js          ← усе запыты да бэка
│       ├── utils.js        ← em(), fmtDate()
│       ├── components/
│       │   ├── ShoppingList.jsx
│       │   ├── Card.jsx
│       │   ├── TagInput.jsx
│       │   ├── Expenses.jsx
│       │   ├── Balance.jsx
│       │   ├── Settings.jsx
│       │   └── Toast.jsx
│       └── hooks/
│           └── useToast.js
├── database.py         ← праца з PostgreSQL
├── auth.py             ← праверка Telegram initData
├── requirements.txt    ← залежнасці Python
└── vercel.json         ← налады Vercel
```

## Крок 1 — Supabase (база даных)

1. Зайсці на [supabase.com](https://supabase.com) → Sign up праз GitHub
2. New Project → прыдумаць назву і пароль
3. Settings → Database → Connection string → URI
4. Скапіраваць радок выгляду:
   ```
   postgresql://postgres:[ПАРОЛЬ]@db.xxxx.supabase.co:5432/postgres
   ```

## Крок 2 — Telegram Bot

1. Напісаць [@BotFather](https://t.me/BotFather) → `/newbot`
2. Захаваць токен
3. `/newapp` → прывязаць міні-праграму да бота (спатрэбіцца пасля дэплою)

## Крок 3 — Vercel (хостынг)

1. Заліць файлы ў GitHub рэпазіторый
2. Зайсці на [vercel.com](https://vercel.com) → New Project → Import з GitHub
3. У Settings → Environment Variables дадаць:

   | Зменная          | Значэнне                                  |
   |------------------|-------------------------------------------|
   | `BOT_TOKEN`      | токен ад BotFather                        |
   | `BOT_USERNAME`   | username бота без @                       |
   | `BOT_APP_NAME`   | назва міні-праграмы ад BotFather          |
   | `DATABASE_URL`   | радок падключэння ад Supabase             |
   | `WEBAPP_URL`     | `https://ВАШ_ПРАЕКТ.vercel.app`          |

4. Deploy

## Крок 4 — Падключыць webhook

Пасля дэплою адкрыць у браўзеры:
```
https://api.telegram.org/botВАШ_ТОКЕН/setWebhook?url=https://ВАШ_ПРАЕКТ.vercel.app/api/webhook
```

## Крок 5 — Дадаць бота ў групу

1. Знайсці бота па username у Telegram
2. Дадаць у патрэбную групу
3. Напісаць `/start` — з'явіцца кнопка міні-праграмы

## Лакальная распрацоўка

```bash
cd webapp
npm install
npm run dev      # http://localhost:5173
npm run build    # → webapp_dist/
```

## Пераезд / змена хостынгу

Мяняюцца толькі зменныя асяроддзя:
- `DATABASE_URL` — любы PostgreSQL-сумяшчальны сэрвіс
- `WEBAPP_URL` — новы адрас дэплою

