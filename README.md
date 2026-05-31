# 🛒 Кошык — Telegram мини-приложение для совместных покупок

Бот и мини-приложение для ведения общего списка покупок в Telegram-группе.  
Интерфейс на **белорусском языке**. Деплой на Vercel + Supabase (оба бесплатно).

## Возможности

- 📋 Общий список товаров для группы
- 🙋 Взять товар на себя — другие видят, кто что берёт
- ✅ Отмечать купленное
- 💰 Учёт расходов и автоматический баланс — кто сколько должен
- 🔔 Push-уведомления в группу при каждом действии (настраиваются)
- ⚙️ Управление уведомлениями прямо из приложения

## Структура файлов

```
├── api/
│   ├── webhook.py    ← Telegram бот (обработка /start, уведомления)
│   ├── items.py      ← API списка покупок
│   ├── expenses.py   ← API расходов и баланса
│   ├── notify.py     ← отправка уведомлений в группу
│   └── settings.py   ← API настроек уведомлений
├── webapp.html       ← мини-приложение (весь UI)
├── database.py       ← работа с PostgreSQL (Supabase)
├── auth.py           ← проверка Telegram initData
├── requirements.txt  ← зависимости Python
└── vercel.json       ← настройки Vercel
```

## Шаг 1 — Supabase (база данных)

1. Зайти на [supabase.com](https://supabase.com) → Sign up через GitHub
2. New Project → придумать название и пароль
3. Settings → Database → Connection string → URI
4. Скопировать строку вида:
   ```
   postgresql://postgres:[ПАРОЛЬ]@db.xxxx.supabase.co:5432/postgres
   ```

## Шаг 2 — Telegram Bot

1. Написать [@BotFather](https://t.me/BotFather) → `/newbot`
2. Сохранить токен
3. `/newapp` → привязать мини-приложение к боту (понадобится после деплоя)

## Шаг 3 — Vercel (хостинг)

1. Залить все файлы в GitHub репозиторий
2. Зайти на [vercel.com](https://vercel.com) → New Project → Import из GitHub
3. В Settings → Environment Variables добавить:

   | Переменная     | Значение                                      |
   |----------------|-----------------------------------------------|
   | `BOT_TOKEN`    | токен от BotFather                            |
   | `DATABASE_URL` | строка подключения от Supabase                |
   | `WEBAPP_URL`   | `https://ВАШ_ПРОЕКТ.vercel.app`              |

4. Deploy

## Шаг 4 — Подключить webhook

После деплоя открыть в браузере:
```
https://api.telegram.org/botВАШ_ТОКЕН/setWebhook?url=https://ВАШ_ПРОЕКТ.vercel.app/api/webhook
```

## Шаг 5 — Добавить бота в группу

1. Найти бота по username в Telegram
2. Добавить в нужную группу
3. Написать `/start` — появится кнопка мини-приложения

## Переезд / смена хостинга

Меняются только переменные окружения:
- `DATABASE_URL` — любой PostgreSQL-совместимый сервис
- `WEBAPP_URL` — новый адрес деплоя
