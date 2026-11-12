# Proxmox API Mock 🎭

Русская версия: [README.md](README.md)

A small FastAPI that pretends to be `pveproxy`. It exists so you can run the bot and the backend on a laptop, or in the demo compose, **when there is no real node around**. Do not put it on the live Proxmox box: that box already has a real `:8006`, and two “proxmoxes” on one port is a bad joke.

How the live stand is wired: [root README](../README.en.md).

### Who it feeds

| Who | How they connect |
|-----|------------------|
| **mock** | listens on `8006`, answers `{"data": ...}` like PVE |
| **backend** | `PROXMOX_HOST` points at the mock |
| **bot** | never sees PVE, only the backend |

Cluster state is in memory. Start/stop/pause mutate it. A process restart or `POST /mock/reset` loads [`fixtures/cluster.json`](fixtures/cluster.json) again. The `PVEAPIToken` header is **not** checked: any demo token is fine, as long as the backend sends one.

The node name is fixed: **`pve`**. Backend env for this stand uses `PROXMOX_NODE=pve`. There is no multi-node, no UPID, no tasks, no cluster.

“Shut down the host” and “reboot” only move the in-memory uptime and log a warning. Demo containers, Docker, and your laptop keep running. On a real PVE the same button cuts power. Do not mix up which `PROXMOX_HOST` the API is using.

Status transitions in `state.py` match the backend `ActionGuard`. Otherwise the API rejects the command before it ever reaches the mock, and the fixture looks broken.

### Fixture

[`fixtures/cluster.json`](fixtures/cluster.json):

- QEMU: 101 running, 102 stopped, 103 paused;
- LXC: 100 `bot-stack` (running), plus 110 and 111.

`100` exists for `PROTECTED_GUESTS=lxc:100`: the backend returns 403 and the mock never hears about it. That is how the demo checks that the remote cannot stop “itself”.

### Bring up the whole demo stack

From the **repository root**. There is no `.env.demo.example` in the tree — create `.env.demo` (it is gitignored):

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

Compose adds `PROXMOX_*` from [`mock/.env.proxmox.example`](.env.proxmox.example): host `http://proxmox-mock:8006`, token `demo@pam!demo` / `demo`, node `pve`, SSL off. For your own values: `cp .env.proxmox.example .env.proxmox` and point the `api` service `env_file` at it instead of the example.

```bash
docker compose -f mock/docker-compose.yml up --build
```

From `mock/` the same command is `docker compose up --build`.

Services: `mongo`, `proxmox-mock`, `api` (port `127.0.0.1:8000`), `bot`. `api` and `bot` mount the source tree read-only — edit Python, restart the container, you do not rebuild every time. Dependencies live in the image; a new line in `requirements.txt` still needs `--build`.

Checks:

```bash
curl -s http://127.0.0.1:8000/health
docker compose -f mock/docker-compose.yml exec api \
  curl -s http://proxmox-mock:8006/api2/json/nodes
docker compose -f mock/docker-compose.yml exec api \
  curl -s -X POST http://proxmox-mock:8006/mock/reset
```

The `api` image may not contain curl (slim). The mock is not published on the host by this compose file. Use another container on the `proxmos-bot-demo` network, or add a temporary `ports` entry on `proxmox-mock`. The dev compose file does publish the mock on `127.0.0.1:8006` — see below.

Send the bot `/start` in the `ADMIN_CHAT_ID` group.

### Mock only, no bot

Docker, with Mongo, without api/bot — root `docker-compose.dev.yml`:

```bash
docker compose -f docker-compose.dev.yml up --build
# mock on 127.0.0.1:8006, mongo on 127.0.0.1:27017
```

Or plain Python:

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

Next to that, `backend/.env.dev` wants `PROXMOX_HOST=http://127.0.0.1:8006`. That address is for the **laptop**. From another container the same mock is `http://proxmox-mock:8006`, not localhost.

### Why it does not belong on a live PVE

The node already runs `pveproxy` on `8006`. A second service on that port either fails to bind, or you start clicking the bot against a toy cluster while believing you shut down prod. The prod compose file (`docker-compose.prod.yml`) does **not** include the mock. `PROXMOX_HOST` there is `https://<node-ip>:8006`.

If you really want the mock inside an LXC next to a real PVE, use another port and another `PROXMOX_HOST`, and do not reuse the `.env.prod` the live bot uses. One swapped env file and the buttons hit the fixture.

Shutdown in the mock does not stop the LXC. Shutdown against the real API does. Before you trust a green `/health`, look at the running `api` container’s `PROXMOX_HOST`.

### The mock’s own variables

[`.env.example`](.env.example):

| Variable | Default | Why |
|----------|---------|-----|
| `MOCK_HOST` | `0.0.0.0` | bind |
| `MOCK_PORT` | `8006` | same as PVE, so the client does not notice the swap |
| `MOCK_ALLOW_RESET` | `1` | `0` hides `POST /mock/reset` |

### HTTP

Compatible with `backend/src/proxmox/client.py`.

| Method | Path | Body |
|--------|------|------|
| GET | `/api2/json/nodes` | `[{"node":"pve","status":"online"}]` |
| GET | `/api2/json/nodes/pve/status` | CPU, RAM, disk, uptime, loadavg |
| GET | `/api2/json/nodes/pve/storage` | pools used/total/avail |
| GET | `/api2/json/nodes/pve/rrddata?timeframe=hour` | RRD points, including per-disk temp |
| GET | `/api2/json/nodes/pve/qemu` | VMs |
| GET | `/api2/json/nodes/pve/lxc` | CTs |
| POST | `/api2/json/nodes/pve/{qemu\|lxc}/{vmid}/status/{action}` | `start` `stop` `shutdown` `suspend` `resume` `reboot` |
| POST | `/api2/json/nodes/pve/status` | JSON `{"command":"shutdown"}` → uptime 0; `reboot` → uptime 120 |
| GET | `/health` | `{"status":"ok"}` |
| POST | `/mock/reset` | fixture again, when reset is allowed |

Any other node name in the path is a 404; the routes are built only for `pve`.

If `.env.demo` points metrics at Influx with a token, the backend still queries Influx instead of this RRD. For offline charts leave `INFLUX_TOKEN` empty or set `METRICS_SOURCE=proxmox`: the backend will then read `rrddata` from the mock.

### Build and tests

```bash
docker build -f mock/Docker/Dockerfile.prod -t proxmos-mock ./mock

cd mock
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/ruff check . && .venv/bin/ruff format --check .
.venv/bin/python -m pytest -q
```

Image: `python:3.12-slim`, the fixture is copied in, reset is on by default.

### Layout

```
mock/
  app.py                 # routes
  state.py               # JSON and statuses
  run.py
  fixtures/cluster.json
  Docker/Dockerfile.prod
  docker-compose.yml     # mongo + mock + api + bot
  .env.example           # MOCK_*
  .env.proxmox.example   # PROXMOX_* for demo
  tests/
```

### What the mock does not promise

- one node, no tasks, no cluster;
- no token check;
- host shutdown does not stop the demo;
- it does not replace backend unit tests on respx — it is a stand for clicking the bot.
