# Backend 🐍 — the only process that actually talks to Proxmox

Русская версия: [README.md](README.md)

FastAPI, holding the PVE token, a Mongo allow-list of trusted chats, and Influx when Influx feels like being up. The bot and the Mini App talk only to this service. `:8006` is this process’s problem, which is how you sleep at night.

The full stand, the screenshots, and the LXC setup: [root README](../README.en.md).

### Why there is only one of these

Every `/api2/json/...` call lives in `src/proxmox/client.py`. The header is always:

```
Authorization: PVEAPIToken={PROXMOX_TOKEN_ID}={PROXMOX_TOKEN_SECRET}
```

HTTP timeout is 30s. A PVE status ≥ 400 or an `errors` field becomes `ProxmoxError`, and the outside world sees HTTP **502** with the text. A Telegram message that says “Proxmox HTTP 403” is more useful than a silent no.

On startup (`lifespan` in `src/api/app.py`):

1. Connect to Mongo, unique index on `(user_id, chat_id)`, collection `admins`.
2. Upsert two pairs: `(ADMIN_USER_ID, ADMIN_CHAT_ID)` and `(ADMIN_USER_ID, MINI_APP_CHAT_ID)`.
3. Proxmox client, `ActionGuard` from `PROTECTED_GUESTS`, inventory / metrics / power services.

Pairs already stored for someone else are **not** deactivated on startup. Change an id, restart, and the new pair appears; set the old document to `active: false` in Mongo or it keeps working.

### Who may call the API

Every route except `GET /health` expects three headers:

| Header | Meaning |
|--------|---------|
| `X-Bot-Token` | shared secret `BOT_API_TOKEN` (bot and BFF) |
| `X-Telegram-User-Id` | Telegram user id |
| `X-Telegram-Chat-Id` | chat id of the chat where the button was pressed or the Mini App was opened |

No `admins` document with `active: true` for that pair → **403**. That is the whole auth model. There is no public “add admin” route.

### HTTP

| Method | Path | What it does |
|--------|------|----------------|
| GET | `/health` | `{"status":"ok"}`, no token |
| GET | `/access` | 204 when the pair is active |
| GET | `/summary` | node summary + guests |
| GET | `/node` | node status |
| GET | `/guests?kind=qemu\|lxc` | list |
| GET | `/guests/{kind}/{vmid}` | one guest, 404 if missing |
| POST | `/guests/{kind}/{vmid}/{action}` | guest power |
| POST | `/node/shutdown` | `command=shutdown` on the node |
| POST | `/node/reboot` | `command=reboot` on the node |
| GET | `/node/metrics` | last-hour charts + storage |
| GET | `/node/health` | uptime and disks ≥ 90% |

`action`: `start`, `stop`, `shutdown`, `suspend`, `resume`, `reboot`.

The guard (`src/services/guard.py`) rejects before calling PVE:

- guest listed in `PROTECTED_GUESTS` → **403** `Guest is protected`;
- `start` when already running, `stop`/`shutdown` when already stopped → 200 and an “already in this state” message, no PVE call;
- `suspend` / `reboot` when not `running`, `resume` when not `paused`, `start` from `paused` → **400**.

Protection syntax: `lxc:100,qemu:105`. A chunk without a number is skipped.

Host shutdown does **not** consult `PROTECTED_GUESTS`. A protected LXC still dies with the node when that node is its hypervisor. Read it this way: the guard saves you from clicking “stop” on the remote’s container, not from the server power button.

### Proxmox from this side of the cable

`PROXMOX_HOST` is the base URL without `/api2/json`; the client appends that. In prod, from inside the container, it is the node’s LAN address, for example `https://192.168.1.10:8006`.

- `127.0.0.1:8006` inside the `api` container is empty. `pveproxy` listens on the node, not in the app container.
- On a laptop, `http://127.0.0.1:8006` is the mock. That is what dev expects.
- In the demo compose file the host is `http://proxmox-mock:8006` (the service name).
- Self-signed cert on an IP: `PROXMOX_VERIFY_SSL=false`. Otherwise httpx fails the handshake before any API call.
- The PVE firewall must allow TCP 8006 from the machine that runs compose (the LXC). Docker SNATs, so PVE sees the LXC address, not the bridge subnet.
- Empty `PROXMOX_NODE`: `GET /nodes`, and if there is exactly one node, use it. Otherwise you get an error and must set the name from the UI (`pve`). The name is cached for the process lifetime.
- VE 9 returns `memory.used/total`, `rootfs`, and `cpuinfo.cpus` instead of flat `mem` / `maxmem` / `disk`. `normalize_node_status_raw` maps that back before `NodeStatus` is built.

Token and privileges are in the [root README](../README.en.md) prod section. Short version: id like `user@pam!name`, ACL on the **token** (privilege separation), privileges `Sys.Audit`, `Sys.PowerMgmt`, `VM.Audit`, `VM.PowerMgmt`, `Datastore.Audit`. Without `Sys.PowerMgmt`, lists work and node shutdown comes back as PVE 403, which we surface as 502.

### Metrics

`NodeMetricsService`:

- `METRICS_SOURCE=influx` **and** both `INFLUX_URL` and `INFLUX_TOKEN` set → Flux against `/api/v2/query` (timeout `INFLUX_QUERY_TIMEOUT`, default 15s). Storage and the live node status still come from PVE.
- otherwise → `rrddata?timeframe=hour` on the node. The Grafana link is omitted in that mode.

Queries filter on tag `host` equal to `INFLUX_HOST_TAG`, else `PROXMOX_NODE`, else the literal `pve`. The UI node name and the Telegraf hostname often differ (`pve` vs `dusha` in the example env). Empty charts with a healthy Influx start with that tag.

Bucket `proxmox`: `cpustat` / `memory` with `object=nodes`. Bucket `hardware`: CPU temperature (`coretemp_package_id_0`) and disks (`temp` + `smart_device`). Telegraf example so two NVMe drives do not collapse into one `nvme_composite`: [`docs/telegraf-disk-temperature.example.conf`](../docs/telegraf-disk-temperature.example.conf). SMART runs on the hypervisor; the bot LXC does not see the node’s disks.

Influx down while it is the configured source → **502** on `/node/metrics`. There is no silent RRD fallback. Fallback happens only when the token is empty and the client is never created.

`/node/health` uses the same metrics and adds warnings: uptime ≤ 0, any storage or the root disk ≥ 90%.

### Environment

`src/core/env_loader.py` picks the file: `ENV_FILE`, else `.env.dev`, else `.env.prod` next to the package. In Docker prod everything arrives from the root `.env.prod` via `env_file`; a file inside the image is optional. Unknown keys are ignored (`extra=ignore`).

| Variable | Example / default | Why |
|----------|-------------------|-----|
| `APP_ENV` | `dev` \| `prod` | DEBUG logs only in dev |
| `BOT_API_TOKEN` | long random string | `X-Bot-Token` |
| `ADMIN_USER_ID` | Telegram user | the trusted person |
| `ADMIN_CHAT_ID` | group id, often `-100…` | the bot |
| `MINI_APP_CHAT_ID` | usually the same user id | Mini App |
| `ADMIN_NAME` | may be empty | label stored in Mongo |
| `MONGO_URL` | `mongodb://mongo:27017` | service name in prod; `127.0.0.1` locally |
| `MONGO_DB` | `proxmos_bot_prod` | database name |
| `PROXMOX_HOST` | `https://192.168.1.10:8006` | `pveproxy` |
| `PROXMOX_TOKEN_ID` | `bot@pam!telegram` | |
| `PROXMOX_TOKEN_SECRET` | token secret | |
| `PROXMOX_NODE` | empty or `pve` | one node per process |
| `PROXMOX_VERIFY_SSL` | `false` | self-signed IP |
| `PROTECTED_GUESTS` | `lxc:100` | comma-separated |
| `METRICS_SOURCE` | `influx` \| `proxmox` | |
| `INFLUX_URL` | `http://192.168.1.148:8086` | reachable from the container, not the LXC localhost if Influx is elsewhere |
| `INFLUX_ORG` | `homelab` | |
| `INFLUX_TOKEN` | | empty → RRD |
| `INFLUX_HOST_TAG` | `dusha` | `host` tag |
| `INFLUX_BUCKET_PROXMOX` | `proxmox` | |
| `INFLUX_BUCKET_HARDWARE` | `hardware` | |
| `INFLUX_QUERY_TIMEOUT` | `15` | seconds |
| `GRAFANA_NODE_DASHBOARD_URL` | | passed through as a link |

Templates: [`backend/.env.dev.example`](.env.dev.example), root [`.env.prod.example`](../.env.prod.example).

Mongo in the prod compose file has **no auth and no published port**. Do not publish `27017` onto the LAN “just in case”. The data set is small, but it is still the list of chats the bot obeys.

### Run

Locally (from `backend/`, with `.env.dev` beside it):

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
# or: uv sync
python run.py
```

Listens on `API_HOST` / `API_PORT` (`0.0.0.0:8000`). Reload only when `APP_ENV=dev` **and** `API_RELOAD=1`.

Prod image: `Docker/Dockerfile.prod`, `python:3.12-slim`, `PYTHONPATH=/app/src`, command `python run.py`. The `api` service in `docker-compose.prod.yml` depends on `mongo` and publishes no host port. Logs: `docker compose -f docker-compose.prod.yml logs -f api`.

### Tests

```bash
cd backend
python -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/ruff check . && .venv/bin/ruff format --check .
.venv/bin/python -m pytest -q
```

Unit tests stub Proxmox (respx and fixtures). A live stand without PVE is [`mock/`](../mock/README.en.md), not a replacement for pytest.

### Layout

```
backend/
  run.py
  src/api/app.py            # routes
  src/core/settings.py
  src/db/repositories/      # admins
  src/proxmox/client.py     # /api2/json
  src/proxmox/models.py
  src/services/guard.py     # protection and status transitions
  src/services/power.py
  src/services/inventory.py
  src/services/node_metrics.py
  src/services/influx_metrics.py
  src/influx/queries.py     # Flux
  Docker/Dockerfile.prod
  tests/
```
