# proxmos-telegram-bot

Telegram-бот и FastAPI-бэкенд для мониторинга и управления Proxmox (QEMU, LXC, выключение хоста).

## Стек

- **bot** — aiogram 3, long polling, опциональный `TELEGRAM_PROXY_URL`
- **api** — FastAPI, единственный клиент Proxmox API
- **mongo** — коллекция `admins`: две доверенные пары `(ADMIN_USER_ID, ADMIN_CHAT_ID)` и `(ADMIN_USER_ID, MINI_APP_CHAT_ID)`

## Быстрый старт (dev)

1. Скопировать шаблон окружения:

```bash
cp backend/.env.dev.example backend/.env.dev
cp bot/.env.dev.example bot/.env.dev
# BOT_API_TOKEN одинаковый в обоих файлах
# backend: PROXMOX_*, ADMIN_*, MONGO_*
# bot: TELEGRAM_BOT_TOKEN; API_BASE_URL=http://127.0.0.1:8000 при локальном api
```

2. Запуск dev-инфраструктуры в Docker (только Mongo + Proxmox mock):

```bash
docker compose -f docker-compose.dev.yml up --build
```

Порты на хосте: Mongo `127.0.0.1:27017`, mock `127.0.0.1:8006`.

3. Локально API и бот (из своих каталогов, после `cp` env-файлов):

```bash
cd backend && python run.py
cd bot && python run.py
```

В `backend/.env.dev` — `MONGO_URL=mongodb://127.0.0.1:27017`, `PROXMOX_HOST=http://127.0.0.1:8006` (см. `.env.dev.example`).  
В `bot/.env.dev` — `API_BASE_URL=http://127.0.0.1:8000`, тот же `BOT_API_TOKEN`.

4. Написать боту `/start` **в группе** с `ADMIN_CHAT_ID`.

| Переменная | Назначение |
|------------|------------|
| `ADMIN_USER_ID` | Telegram user админа |
| `ADMIN_CHAT_ID` | Группа, где стоит бот (команды / кнопки) |
| `MINI_APP_CHAT_ID` | Чат, из которого открывают Mini App (часто личка = user id) |

При старте API upsert обе пары в Mongo. Mini App из группы **не** принимается (BFF проверяет `MINI_APP_CHAT_ID`).

## Prod

```bash
cp .env.prod.example .env.prod
docker compose -f docker-compose.prod.yml up -d --build
```

Регистрация через API не нужна — админ задаётся в `.env.prod`.

## Mini App (Telegram WebApp)

Каталог [`app/`](app/) — SvelteKit + FSD + BFF (`initData` / dev auth). Подробности: [`app/README.md`](app/README.md).

```bash
cp app/.env.example app/.env
cd app && npm install && npm run dev
```

В BotFather укажи URL mini app; в `bot/.env` — `WEBAPP_URL`. Menu button / ссылку на Mini App настрой **в чате `MINI_APP_CHAT_ID`** (не в ops-группе).

## Демо без Proxmox

Локальный стенд с mock API в каталоге [`mock/`](mock/) — фикстурный кластер `pve`, QEMU/LXC в памяти, команды start/stop меняют статус.

```bash
cp .env.demo.example .env.demo
# TELEGRAM_BOT_TOKEN, ADMIN_USER_ID, ADMIN_CHAT_ID, BOT_API_TOKEN
docker compose -f mock/docker-compose.yml up --build
```

Сервисы: `mongo`, `proxmox-mock`, `api`, `bot`. Параметры Proxmox для demo лежат в [`mock/.env.proxmox.example`](mock/.env.proxmox.example); подробности — [`mock/README.md`](mock/README.md).

Проверка API без Telegram:

```bash
curl -s http://127.0.0.1:8000/health
```

В боте: `/start` — сводка с demo-VM; LXC **100** защищён (`PROTECTED_GUESTS=lxc:100`); «Выключить хост» только пишет в лог mock, demo-стек не останавливается.

Сброс mock-состояния к JSON (из сети compose): `POST http://proxmox-mock:8006/mock/reset`.

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

Mock Proxmox:

```bash
cd mock
python -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

Либо `uv sync --extra dev` в каталоге `backend/`, `bot/` или `mock/`.

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
| `mock/app.py` | HTTP mock Proxmox API |
| `mock/fixtures/cluster.json` | начальные VM/LXC для demo |
