# 🛒 Koszyk — деплой на Vercel + Supabase

## Структура файлов
```
koszyk/
├── api/
│   ├── webhook.py    ← Telegram бот
│   ├── items.py      ← API списка
│   └── expenses.py   ← API расходов/баланса
├── webapp.html       ← мини-приложение
├── database.py       ← база данных
├── requirements.txt  ← зависимости
└── vercel.json       ← настройки Vercel
```

## Шаг 1 — Supabase (база данных, бесплатно)

1. Зайти на supabase.com → Sign up (через GitHub)
2. New Project → придумать название и пароль
3. Settings → Database → Connection string → URI
4. Скопировать строку вида:
   `postgresql://postgres:[ПАРОЛЬ]@db.xxxx.supabase.co:5432/postgres`

## Шаг 2 — Vercel (хостинг, бесплатно)

1. Зайти на vercel.com → Sign up (через GitHub)
2. New Project → Import из GitHub репозитория
3. Загрузить все файлы в репозиторий `koszyk` на GitHub:
   - webapp.html
   - database.py
   - requirements.txt
   - vercel.json
   - api/webhook.py
   - api/items.py
   - api/expenses.py
4. В Vercel → Settings → Environment Variables добавить:
   - `BOT_TOKEN` = токен от BotFather
   - `DATABASE_URL` = строка от Supabase
   - `WEBAPP_URL` = https://ВАШ_ПРОЕКТ.vercel.app
5. Deploy

## Шаг 3 — Настроить webhook

После деплоя открыть в браузере:
```
https://api.telegram.org/botВАШ_ТОКЕН/setWebhook?url=https://ВАШ_ПРОЕКТ.vercel.app/api/webhook
```

## Шаг 4 — Инициализировать базу данных

Открыть в браузере (один раз):
```
https://ВАШ_ПРОЕКТ.vercel.app/api/webhook
```

Или написать /start боту — он создаст таблицы автоматически.

## Шаг 5 — Добавить бота в группу

1. Найти бота по username в Telegram
2. Добавить в домашнюю группу
3. Написать /start → появится кнопка мини-приложения

## Переезд на другой сервис

Меняете только переменные окружения:
- `DATABASE_URL` — любой PostgreSQL
- `WEBAPP_URL` — новый адрес
- Для polling вместо webhook: раскомментировать код в api/webhook.py

