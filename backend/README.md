# Backend 🐍 — единственный, кто вообще разговаривает с Proxmox

English: [README.en.md](README.en.md)

FastAPI, у которого на руках токен PVE, Mongo с доверенными чатами и Influx, если тот сегодня в настроении. Бот и мини-апп ходят только сюда. В `:8006` — только этот процесс, и так спокойнее спать.

Общая картина стенда, скрины и LXC: [корневой README](../README.md).

### Зачем он один такой

Все вызовы `/api2/json/...` живут в `src/proxmox/client.py`. Заголовок всегда:

```
Authorization: PVEAPIToken={PROXMOX_TOKEN_ID}={PROXMOX_TOKEN_SECRET}
```

Таймаут HTTP — 30 с. Ответ PVE с кодом ≥ 400 или полем `errors` становится `ProxmoxError`, а снаружи — HTTP **502** с текстом. Так проще увидеть в Telegram «Proxmox HTTP 403», чем молчаливый отказ.

На старте (`lifespan` в `src/api/app.py`):

1. Подключение к Mongo, индекс `(user_id, chat_id)` unique, коллекция `admins`.
2. Upsert двух пар: `(ADMIN_USER_ID, ADMIN_CHAT_ID)` и `(ADMIN_USER_ID, MINI_APP_CHAT_ID)`.
3. Клиент Proxmox, `ActionGuard` из `PROTECTED_GUESTS`, сервисы inventory / metrics / power.

Чужие пары, которые уже лежат в базе, старт **не выключает**. Поменял id — рестарт подхватит новую пару, старую сними в Mongo (`active: false`) или она так и останется пропуском.

### Кто имеет право звать API

Каждый метод кроме `GET /health` ждёт три заголовка:

| Заголовок | Смысл |
|-----------|--------|
| `X-Bot-Token` | общий секрет `BOT_API_TOKEN` (бот и BFF) |
| `X-Telegram-User-Id` | user id из Telegram |
| `X-Telegram-Chat-Id` | chat id того чата, где нажали кнопку или открыли Mini App |

Нет пары в `admins` с `active: true` → **403**. Это и есть вся «авторизация». Отдельной ручки «добавить админа» снаружи нет.

### HTTP

| Метод | Путь | Что делает |
|-------|------|------------|
| GET | `/health` | `{"status":"ok"}`, без токена |
| GET | `/access` | 204, если пара живая |
| GET | `/summary` | сводка ноды + гости |
| GET | `/node` | status ноды |
| GET | `/guests?kind=qemu\|lxc` | список |
| GET | `/guests/{kind}/{vmid}` | карточка, 404 если нет |
| POST | `/guests/{kind}/{vmid}/{action}` | питание гостя |
| POST | `/node/shutdown` | `command=shutdown` на ноду |
| POST | `/node/reboot` | `command=reboot` на ноду |
| GET | `/node/metrics` | графики за час + storage |
| GET | `/node/health` | uptime и диски ≥ 90% |

`action`: `start`, `stop`, `shutdown`, `suspend`, `resume`, `reboot`.

Guard (`src/services/guard.py`) режет до похода в PVE:

- гость из `PROTECTED_GUESTS` → **403** `Guest is protected`;
- `start` на уже running, `stop`/`shutdown` на stopped → 200 и текст «уже в состоянии», без вызова PVE;
- `suspend` / `reboot` не из `running`, `resume` не из `paused`, `start` из `paused` → **400**.

Формат защиты: `lxc:100,qemu:105`. Кривой кусок без числа молча пропускается.

Shutdown хоста **не** смотрит на `PROTECTED_GUESTS`. Защищённый LXC умрёт вместе с нодой, если нода — это его гипервизор. Так и должно читаться: guard спасает от клика «stop» по контейнеру пульта, не от кнопки питания сервера.

### Proxmox с этой стороны провода

`PROXMOX_HOST` — база без хвоста `/api2/json`, клиент допишет сам. В проде из контейнера это LAN IP ноды, например `https://192.168.1.10:8006`.

- `127.0.0.1:8006` внутри контейнера `api` — пусто. `pveproxy` слушает на ноде, не в контейнере приложения.
- В dev на ноутбуке `http://127.0.0.1:8006` — это mock, так и задумано.
- В demo-compose хост `http://proxmox-mock:8006` (имя сервиса).
- Самоподписанный сертификат по IP: `PROXMOX_VERIFY_SSL=false`. Иначе httpx завернёт handshake ещё до API.
- Файрвол PVE должен пускать TCP 8006 с IP той машины, где крутится compose (LXC). Докер делает SNAT, источник для PVE — адрес LXC, не подсеть моста.
- Пустой `PROXMOX_NODE`: `GET /nodes`, и если нода ровно одна — берём её. Иначе ошибка, задай имя из UI (`pve`). Имя кэшируется в процессе.
- VE 9 отдаёт `memory.used/total`, `rootfs`, `cpuinfo.cpus` вместо плоских `mem` / `maxmem` / `disk`. `normalize_node_status_raw` приводит это к старому виду до сборки `NodeStatus`.

Токен и привилегии — в [корневом README](../README.md), раздел про прод. Коротко: id вида `user@pam!name`, ACL на **токен** (privilege separation), права `Sys.Audit`, `Sys.PowerMgmt`, `VM.Audit`, `VM.PowerMgmt`, `Datastore.Audit`. Без `Sys.PowerMgmt` списки живые, а shutdown ноды — 403 от PVE и 502 от нас.

### Метрики

`NodeMetricsService`:

- `METRICS_SOURCE=influx` **и** непустые `INFLUX_URL` + `INFLUX_TOKEN` → Flux в `/api/v2/query` (таймаут `INFLUX_QUERY_TIMEOUT`, по умолчанию 15 с). Storage и текущий status ноды всё равно с PVE.
- иначе → `rrddata?timeframe=hour` прямо с ноды. Grafana-ссылка в этом режиме в ответ не кладётся.

Запросы ждут тег `host`, равный `INFLUX_HOST_TAG`, иначе `PROXMOX_NODE`, иначе литерал `pve`. Имя ноды в UI и hostname в Telegraf часто различаются (`pve` vs `dusha` в примере env). Пустые графики при зелёном Influx — сначала сверка этого тега.

Бакет `proxmox`: `cpustat` / `memory` с `object=nodes`. Бакет `hardware`: температура CPU (`coretemp_package_id_0`) и дисков (`temp` + `smart_device`). Пример Telegraf, чтобы два NVMe не слиплись в один `nvme_composite`: [`docs/telegraf-disk-temperature.example.conf`](../docs/telegraf-disk-temperature.example.conf). SMART снимается на гипервизоре, у LXC с ботом дисков ноды нет.

Influx недоступен при включённом источнике → **502** на `/node/metrics`. Тихого отката на RRD нет. Откат бывает только когда токен пустой и клиент вообще не создаётся.

`/node/health` берёт те же метрики и добавляет предупреждения: uptime ≤ 0, storage или root ≥ 90%.

### Переменные

Файл выбирает `src/core/env_loader.py`: `ENV_FILE`, иначе `.env.dev`, иначе `.env.prod` рядом с пакетом. В Docker прод всё приезжает из корневого `.env.prod` через `env_file`, файл внутри образа не обязателен. Лишние ключи игнорируются (`extra=ignore`).

| Переменная | Пример / дефолт | Зачем |
|------------|-----------------|--------|
| `APP_ENV` | `dev` \| `prod` | DEBUG-логи только в dev |
| `BOT_API_TOKEN` | длинная случайная строка | `X-Bot-Token` |
| `ADMIN_USER_ID` | Telegram user | доверенный человек |
| `ADMIN_CHAT_ID` | id группы, часто `-100…` | бот |
| `MINI_APP_CHAT_ID` | обычно тот же user id | Mini App |
| `ADMIN_NAME` | можно пусто | подпись в Mongo |
| `MONGO_URL` | `mongodb://mongo:27017` | в проде имя сервиса; локально `127.0.0.1` |
| `MONGO_DB` | `proxmos_bot_prod` | имя базы |
| `PROXMOX_HOST` | `https://192.168.1.10:8006` | `pveproxy` |
| `PROXMOX_TOKEN_ID` | `bot@pam!telegram` | |
| `PROXMOX_TOKEN_SECRET` | секрет токена | |
| `PROXMOX_NODE` | пусто или `pve` | одна нода на процесс |
| `PROXMOX_VERIFY_SSL` | `false` | самоподписанный IP |
| `PROTECTED_GUESTS` | `lxc:100` | через запятую |
| `METRICS_SOURCE` | `influx` \| `proxmox` | |
| `INFLUX_URL` | `http://192.168.1.148:8086` | с контейнера, не localhost LXC, если Influx на другой машине |
| `INFLUX_ORG` | `homelab` | |
| `INFLUX_TOKEN` | | пусто → RRD |
| `INFLUX_HOST_TAG` | `dusha` | тег `host` |
| `INFLUX_BUCKET_PROXMOX` | `proxmox` | |
| `INFLUX_BUCKET_HARDWARE` | `hardware` | |
| `INFLUX_QUERY_TIMEOUT` | `15` | секунды |
| `GRAFANA_NODE_DASHBOARD_URL` | | ссылка как есть |

Шаблоны: [`backend/.env.dev.example`](.env.dev.example), корневой [`.env.prod.example`](../.env.prod.example).

Mongo в прод-compose **без логина и без проброса порта**. Не публикуй `27017` в LAN «на всякий». Данных там мало, но это всё ещё список, кого бот слушает.

### Запуск

Локально (из `backend/`, рядом `.env.dev`):

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
# или: uv sync
python run.py
```

Слушает `API_HOST` / `API_PORT` (`0.0.0.0:8000`). Reload только если `APP_ENV=dev` **и** `API_RELOAD=1`.

Прод-образ: `Docker/Dockerfile.prod`, `python:3.12-slim`, `PYTHONPATH=/app/src`, команда `python run.py`. Сервис `api` в `docker-compose.prod.yml` зависит от `mongo`, порт на хост не висит. Логи: `docker compose -f docker-compose.prod.yml logs -f api`.

### Тесты

```bash
cd backend
python -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/ruff check . && .venv/bin/ruff format --check .
.venv/bin/python -m pytest -q
```

Proxmox в unit-тестах подменяется (respx и фикстуры). Живой стенд без PVE — это [`mock/`](../mock/README.md), не замена pytest.

### Каталог

```
backend/
  run.py
  src/api/app.py            # маршруты
  src/core/settings.py
  src/db/repositories/      # admins
  src/proxmox/client.py     # /api2/json
  src/proxmox/models.py
  src/services/guard.py     # защита и переходы статусов
  src/services/power.py
  src/services/inventory.py
  src/services/node_metrics.py
  src/services/influx_metrics.py
  src/influx/queries.py     # Flux
  Docker/Dockerfile.prod
  tests/
```
