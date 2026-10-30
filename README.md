# proxmos-telegram-bot

Telegram-бот и FastAPI-бэкенд для мониторинга и управления Proxmox (QEMU, LXC, выключение хоста).

## Стек

- **bot** — aiogram 3, long polling, опциональный `TELEGRAM_PROXY_URL`
- **api** — FastAPI, единственный клиент Proxmox API
- **mongo** — коллекция `admins` (`user_id` + `chat_id`)

## Быстрый старт (dev)

1. Скопировать шаблон окружения:

```bash
cp .env.dev.example .env.dev
# заполнить TELEGRAM_BOT_TOKEN, BOT_API_TOKEN, ADMIN_USER_ID, ADMIN_CHAT_ID, PROXMOX_*
```

2. Запуск:

```bash
docker compose -f docker-compose.dev.yml up --build
```

3. Написать боту `/start` из чата, для которого в `.env` заданы `ADMIN_USER_ID` и `ADMIN_CHAT_ID`.

В личке `ADMIN_CHAT_ID` обычно равен `ADMIN_USER_ID`. Для группы укажи отрицательный `chat_id` (узнать можно через `@userinfobot` или лог бота).

При каждом старте API синхронизирует эту пару в Mongo (upsert).

## Prod

```bash
cp .env.prod.example .env.prod
docker compose -f docker-compose.prod.yml up -d --build
```

Регистрация через API не нужна — админ задаётся в `.env.prod`.

## Тесты

Backend:

```bash
cd backend
python -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

Bot:

```bash
cd bot
python -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

Либо `uv sync --extra dev` в каталоге `backend/` или `bot/` (см. локальный `pyproject.toml`).

## Структура

| Путь | Назначение |
|------|------------|
| `backend/src/api/app.py` | HTTP API |
| `backend/src/db/models/` | DTO администраторов |
| `backend/src/db/repositories/` | репозиторий Mongo |
| `backend/src/proxmox/` | Клиент Proxmox |
| `backend/src/services/` | inventory, guard, power |
| `bot/core/` | настройки, proxy, main |
| `bot/src/handlers/` | Telegram UI |
| `bot/src/api/api_client.py` | клиент API |
| `bot/src/core/middleware.py` | проверка `/access` |
