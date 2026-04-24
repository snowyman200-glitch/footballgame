# World Cup Pick'em V2

Полный starter-kit под деплой в GitHub + Vercel + Render + Supabase.

## Состав проекта

- `miniapp/` — Telegram Mini App
- `backend/` — FastAPI API для сохранения прогнозов и community stats
- `bot/` — Telegram bot на python-telegram-bot
- `database/seed.sql` — SQL seed с турниром, командами и матчами
- `deploy/render.yaml` — blueprint для Render
- `miniapp/vercel.json` — конфиг Vercel
- `.env.example` — пример env

## Архитектура

### Mini App
Статический HTML/JS, который:
- показывает все группы A-L;
- даёт выбрать исход каждого матча в группах;
- автоматически считает таблицы;
- выбирает 8 лучших третьих мест;
- строит плей-офф по матчам 73–104;
- даёт выбрать победителя каждого матча плей-офф;
- показывает итоговые 1/2/3/4 места;
- запрашивает community snapshot с backend;
- отправляет финальный bracket payload в backend и в Telegram.

### Backend
FastAPI c endpoint'ами:
- `GET /health`
- `GET /api/tournament/{slug}`
- `POST /api/submissions`
- `GET /api/community/{slug}`
- `POST /api/admin/community/{slug}`

### Bot
Бот отдаёт кнопку Mini App и принимает `WEB_APP_DATA` как fallback.

## Деплой

### 1. GitHub
Загрузи весь проект в один репозиторий.

### 2. Supabase
1. Создай проект Supabase
2. Выполни `database/schema.sql`
3. Выполни `database/seed.sql`
4. Возьми `DATABASE_URL`

### 3. Render
1. Создай новый Blueprint через `deploy/render.yaml`
2. Добавь env:
   - `BOT_TOKEN`
   - `WEB_APP_URL`
   - `DATABASE_URL`
   - `APP_SECRET`
3. После деплоя получишь API и bot worker

### 4. Vercel
1. Импортируй репозиторий
2. Root Directory = `miniapp`
3. Framework preset = Other
4. Добавь env `VITE_BACKEND_BASE_URL` если хочешь пробросить backend URL на build-time, либо просто отредактируй `miniapp/config.js`
5. Получишь публичный HTTPS URL Mini App

### 5. BotFather
1. Открой @BotFather
2. `/newbot`
3. Скопируй токен
4. `/setmenubutton`
5. Укажи URL Mini App

## Последовательность запуска

1. Деплой backend на Render
2. Деплой miniapp на Vercel
3. Подставь `WEB_APP_URL` в Render env для бота
4. Перезапусти bot service
5. Открой Telegram и вызови `/start`

## После запуска

Можно добавить:
- lock deadline;
- админку результатов;
- реальные community stats;
- приватные лиги;
- leaderboard точности.
