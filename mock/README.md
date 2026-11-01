# Proxmox API Mock

HTTP-сервис, имитирующий **Proxmox VE API** (`/api2/json/...`) для локального запуска бота и backend **без реального сервера PVE**. Состояние кластера хранится в памяти и меняется при командах start/stop/suspend/resume/shutdown.

## Назначение

| Компонент | Роль |
|-----------|------|
| **mock** | отвечает как Proxmox на порту `8006` |
| **backend (api)** | ходит на `PROXMOX_HOST` — в demo это `http://proxmox-mock:8006` |
| **bot** | Proxmox не вызывает, только backend |

Формат ответов совместим с [`backend/src/proxmox/client.py`](../backend/src/proxmox/client.py): JSON `{"data": ...}`.

## Быстрый старт (Docker, весь demo-стек)

Из **корня репозитория**:

```bash
cp .env.demo.example .env.demo
cp mock/.env.proxmox.example mock/.env.proxmox   # опционально; compose по умолчанию использует .example
# заполнить в .env.demo: TELEGRAM_BOT_TOKEN, ADMIN_USER_ID, ADMIN_CHAT_ID, BOT_API_TOKEN

docker compose -f mock/docker-compose.yml up --build
```

Из каталога `mock/` (эквивалентно):

```bash
docker compose up --build
```

Сервисы: `mongo`, `proxmox-mock`, `api`, `bot`.

Проверка mock из другого контейнера в той же сети:

```bash
docker compose -f mock/docker-compose.yml exec api curl -s http://proxmox-mock:8006/api2/json/nodes
```

Сброс состояния к [`fixtures/cluster.json`](fixtures/cluster.json):

```bash
docker compose -f mock/docker-compose.yml exec api curl -s -X POST http://proxmox-mock:8006/mock/reset
```

## Запуск только mock (без Docker)

```bash
cd mock
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python run.py
```

Проверка с хоста:

```bash
curl -s http://127.0.0.1:8006/api2/json/nodes | jq
curl -s http://127.0.0.1:8006/api2/json/nodes/pve/qemu | jq
```

## Переменные окружения

### Сервис mock ([`.env.example`](.env.example))

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `MOCK_HOST` | `0.0.0.0` | bind address |
| `MOCK_PORT` | `8006` | порт (как у Proxmox) |
| `MOCK_ALLOW_RESET` | `1` | если `1`, доступен `POST /mock/reset` |

### Подключение backend к mock ([`.env.proxmox.example`](.env.proxmox.example))

Используется сервисами **api** (и косвенно bot) в [`docker-compose.yml`](docker-compose.yml). Это **не секреты production** — демо-токен, любая строка подойдёт; mock **не проверяет** `Authorization`.

| Переменная | Значение в demo |
|------------|-----------------|
| `PROXMOX_HOST` | `http://proxmox-mock:8006` |
| `PROXMOX_TOKEN_ID` | `demo@pam!demo` |
| `PROXMOX_TOKEN_SECRET` | `demo` |
| `PROXMOX_NODE` | `pve` |
| `PROXMOX_VERIFY_SSL` | `false` |

Локальная копия (не коммитится): `cp mock/.env.proxmox.example mock/.env.proxmox` и подставь в compose вместо `.example`, если нужны свои значения.

Общие настройки demo-стека (Telegram, Mongo, admin) — в **корневом** [`.env.demo.example`](../.env.demo.example).

## HTTP API

### Proxmox-совместимые маршруты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api2/json/nodes` | список нод `[{"node":"pve","status":"online"}]` |
| GET | `/api2/json/nodes/pve/status` | CPU, RAM, disk, uptime, loadavg |
| GET | `/api2/json/nodes/pve/qemu` | список VM |
| GET | `/api2/json/nodes/pve/lxc` | список CT |
| POST | `/api2/json/nodes/pve/{qemu\|lxc}/{vmid}/status/{action}` | `start`, `stop`, `shutdown`, `suspend`, `resume`, `reboot` |
| POST | `/api2/json/nodes/pve/status` | JSON или form: `{"command":"shutdown"}` — uptime ноды → 0, стек demo не останавливается |

Имя ноды зафиксировано: **`pve`**. В env backend задай `PROXMOX_NODE=pve`.

### Служебные

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/health` | `{"status":"ok"}` |
| POST | `/mock/reset` | сброс in-memory state к `fixtures/cluster.json` (если `MOCK_ALLOW_RESET=1`) |

## Фикстурные данные

Файл [`fixtures/cluster.json`](fixtures/cluster.json):

- **QEMU:** 101 running, 102 stopped, 103 paused  
- **LXC:** 100 `bot-stack` (running), 110, 111 — для проверки `PROTECTED_GUESTS=lxc:100` в demo  

Переходы статусов в [`state.py`](state.py) согласованы с backend [`ActionGuard`](../backend/src/services/guard.py): иначе API отрежет команду до mock.

## Структура каталога

```
mock/
  app.py              # FastAPI, маршруты
  state.py            # загрузка JSON, изменение статусов
  run.py              # uvicorn
  fixtures/cluster.json
  Docker/Dockerfile.prod
  docker-compose.yml   # demo-стек: mongo + proxmox-mock + api + bot
  tests/
  .env.example        # MOCK_*
  .env.proxmox.example # PROXMOX_* для demo
  requirements.txt
  pyproject.toml
```

## Тесты

```bash
cd mock
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

## Ограничения

- одна нода `pve`, без UPID/tasks и кластера;
- авторизация Proxmox не эмулируется;
- shutdown хоста не останавливает контейнеры demo;
- не заменяет unit-тесты backend на **respx** — это E2E-стенд для разработки бота.

## Сборка образа

```bash
docker build -f mock/Docker/Dockerfile.prod -t proxmos-mock ./mock
```
