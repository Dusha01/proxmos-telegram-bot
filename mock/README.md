# Proxmox API Mock 🎭

English: [README.en.md](README.en.md)

Маленький FastAPI, который притворяется `pveproxy`. Чтобы крутить бота и backend на ноутбуке или в demo-compose, **когда настоящей ноды рядом нет**. На боевой Proxmox его не ставь: там уже сидит настоящий `:8006`, и два «проксимокса» на одном порту — плохая шутка.

Как устроен живой стенд: [корневой README](../README.md).

### Кого он кормит

| Кто | Как связан |
|-----|------------|
| **mock** | слушает `8006`, отвечает `{"data": ...}` как PVE |
| **backend** | `PROXMOX_HOST` смотрит на mock |
| **bot** | PVE не видит, только backend |

Состояние кластера в памяти. Старт/стоп/пауза его меняют. Рестарт процесса или `POST /mock/reset` возвращает [`fixtures/cluster.json`](fixtures/cluster.json). Авторизацию заголовок `PVEAPIToken` **не** проверяет: токен в demo любой, лишь бы backend вообще его отправил.

Имя ноды зашито: **`pve`**. В env backend для этого стенда `PROXMOX_NODE=pve`. Несколько нод, UPID, задачи, кластер — нет.

«Выключить хост» и «перезагрузить» только двигают uptime в памяти и пишут warning в лог. Контейнеры demo, Docker и твой ноутбук живут дальше. На настоящем PVE та же кнопка гасит железо. Не перепутай, на какой `PROXMOX_HOST` смотрит API.

Переходы статусов в `state.py` совпадают с `ActionGuard` backend. Иначе API отвергнет команду ещё до mock, и ты будешь думать, что фикстура сломана.

### Фикстура

[`fixtures/cluster.json`](fixtures/cluster.json):

- QEMU: 101 running, 102 stopped, 103 paused;
- LXC: 100 `bot-stack` (running), плюс 110 и 111.

`100` специально под `PROTECTED_GUESTS=lxc:100`: backend ответит 403, mock даже не узнает. Так на demo проверяют, что пульт не может остановить «сам себя».

### Поднять весь demo-стек

Из **корня репозитория**. Файла `.env.demo.example` в дереве нет — создай `.env.demo` (он в gitignore):

```bash
APP_ENV=dev
TELEGRAM_BOT_TOKEN=...
BOT_API_TOKEN=...
ADMIN_USER_ID=...
ADMIN_CHAT_ID=...
MINI_APP_CHAT_ID=...
ADMIN_NAME=
MONGO_URL=mongodb://mongo:27017
MONGO_DB=proxmos_bot_demo
PROTECTED_GUESTS=lxc:100
API_BASE_URL=http://api:8000
WEBAPP_URL=
TELEGRAM_PROXY_URL=
```

`PROXMOX_*` compose подмешает из [`mock/.env.proxmox.example`](.env.proxmox.example): хост `http://proxmox-mock:8006`, токен `demo@pam!demo` / `demo`, нода `pve`, SSL выключен. Свой файл: `cp .env.proxmox.example .env.proxmox` и подставь его в `env_file` сервиса `api` вместо example.

```bash
docker compose -f mock/docker-compose.yml up --build
```

Из каталога `mock/` то же самое: `docker compose up --build`.

Сервисы: `mongo`, `proxmox-mock`, `api` (порт `127.0.0.1:8000`), `bot`. У `api` и `bot` примонтирован исходный код только для чтения — правишь Python, перезапускаешь контейнер, пересобирать образ каждый раз не нужно. Зависимости в образе, новый пакет в `requirements.txt` всё же требует `--build`.

Проверки:

```bash
curl -s http://127.0.0.1:8000/health
docker compose -f mock/docker-compose.yml exec api \
  curl -s http://proxmox-mock:8006/api2/json/nodes
docker compose -f mock/docker-compose.yml exec api \
  curl -s -X POST http://proxmox-mock:8006/mock/reset
```

В образе `api` curl может не быть (slim). Тогда с хоста, пока mock не проброшен наружу в этом compose, зайди в любой контейнер сети `proxmos-bot-demo` или добавь временный `ports` у `proxmox-mock`. Dev-compose как раз публикует mock на `127.0.0.1:8006` — см. ниже.

`/start` боту пиши в группе `ADMIN_CHAT_ID`.

### Только mock, без бота

Docker, вместе с Mongo, без api/bot — корневой `docker-compose.dev.yml`:

```bash
docker compose -f docker-compose.dev.yml up --build
# mock на 127.0.0.1:8006, mongo на 127.0.0.1:27017
```

Или голый Python:

```bash
cd mock
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python run.py
```

```bash
curl -s http://127.0.0.1:8006/api2/json/nodes
curl -s http://127.0.0.1:8006/api2/json/nodes/pve/qemu
curl -s http://127.0.0.1:8006/health
```

Рядом в `backend/.env.dev`: `PROXMOX_HOST=http://127.0.0.1:8006`. Это адрес **с ноутбука**. Из другого контейнера тот же mock — `http://proxmox-mock:8006`, не localhost.

### Зачем его не тащат на боевой PVE

На ноде уже слушает `pveproxy` на `8006`. Второй сервис на том же порту либо не встанет, либо ты начнёшь тыкать ботом в игрушечный кластер и думать, что выключил прод. Prod-compose (`docker-compose.prod.yml`) mock **не** содержит. `PROXMOX_HOST` там — `https://<IP-ноды>:8006`.

Если очень хочется гонять mock внутри LXC рядом с настоящим PVE — только на другом порту и с другим `PROXMOX_HOST`, и не на той копии `.env.prod`, которой пользуется боевой бот. Иначе одна перестановка env и кнопки полетят в фикстуру.

Shutdown в mock не гасит LXC. Shutdown в настоящем API гасит. Перед тем как радоваться зелёному `/health`, глянь, куда смотрит `PROXMOX_HOST` у запущенного `api`.

### Переменные самого mock

[`.env.example`](.env.example):

| Переменная | Дефолт | Зачем |
|------------|--------|--------|
| `MOCK_HOST` | `0.0.0.0` | bind |
| `MOCK_PORT` | `8006` | как у PVE, чтобы клиент не замечал подмены |
| `MOCK_ALLOW_RESET` | `1` | `0` прячет `POST /mock/reset` |

### HTTP

Совместимо с `backend/src/proxmox/client.py`.

| Метод | Путь | Ответ |
|-------|------|--------|
| GET | `/api2/json/nodes` | `[{"node":"pve","status":"online"}]` |
| GET | `/api2/json/nodes/pve/status` | CPU, RAM, disk, uptime, loadavg |
| GET | `/api2/json/nodes/pve/storage` | пулы used/total/avail |
| GET | `/api2/json/nodes/pve/rrddata?timeframe=hour` | точки RRD, включая temp дисков |
| GET | `/api2/json/nodes/pve/qemu` | VM |
| GET | `/api2/json/nodes/pve/lxc` | CT |
| POST | `/api2/json/nodes/pve/{qemu\|lxc}/{vmid}/status/{action}` | `start` `stop` `shutdown` `suspend` `resume` `reboot` |
| POST | `/api2/json/nodes/pve/status` | JSON `{"command":"shutdown"}` → uptime 0; `reboot` → uptime 120 |
| GET | `/health` | `{"status":"ok"}` |
| POST | `/mock/reset` | снова fixture, если разрешён reset |

Чужое имя ноды в пути — 404, маршруты собраны только для `pve`.

Метрики backend в demo, если в `.env.demo` выставлен Influx с токеном, всё равно пойдут в Influx, а не в эти RRD. Для офлайн-графиков оставь `INFLUX_TOKEN` пустым или поставь `METRICS_SOURCE=proxmox`: тогда backend возьмёт `rrddata` у mock.

### Сборка и тесты

```bash
docker build -f mock/Docker/Dockerfile.prod -t proxmos-mock ./mock

cd mock
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/ruff check . && .venv/bin/ruff format --check .
.venv/bin/python -m pytest -q
```

Образ: `python:3.12-slim`, fixture копируется внутрь, reset по умолчанию включён.

### Каталог

```
mock/
  app.py                 # маршруты
  state.py               # JSON и статусы
  run.py
  fixtures/cluster.json
  Docker/Dockerfile.prod
  docker-compose.yml     # mongo + mock + api + bot
  .env.example           # MOCK_*
  .env.proxmox.example   # PROXMOX_* для demo
  tests/
```

### Чего mock не обещает

- одна нода, без задач и кластера;
- без проверки токена;
- shutdown хоста не останавливает demo;
- это не замена unit-тестов backend на respx — это стенд, чтобы потыкать бота.
