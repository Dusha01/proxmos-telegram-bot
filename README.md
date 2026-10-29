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
# заполнить TELEGRAM_BOT_TOKEN, BOT_API_TOKEN, REGISTRATION_TOKEN, PROXMOX_*
```

2. Запуск:

```bash
docker compose -f docker-compose.dev.yml up --build
```

3. Зарегистрировать администратора (с хоста, API на `127.0.0.1:8000`):

```bash
curl -s -X POST http://127.0.0.1:8000/admins \
  -H "Content-Type: application/json" \
  -H "X-Registration-Token: YOUR_REGISTRATION_TOKEN" \
  -d '{"user_id": YOUR_TELEGRAM_ID, "chat_id": YOUR_TELEGRAM_ID, "name": "Speed"}'
```

В личке `chat_id` совпадает с `user_id`. Для группы нужна отдельная запись с отрицательным `chat_id`.

4. Написать боту `/start`.

## Prod

```bash
cp .env.prod.example .env.prod
docker compose -f docker-compose.prod.yml up -d --build
```

Регистрация админа — из сети compose (`docker compose exec api ...`), порт API наружу не публикуется.

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
