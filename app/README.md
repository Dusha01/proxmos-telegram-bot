# Proxmox Mini App (Telegram WebApp)

SvelteKit 5 + FSD (`src/lib/*`) + BFF (`src/lib/server` + `src/routes/api`).

## Architecture

- **UI:** `entities` / `features` / `widgets` / `pages` — see [FSD.md](./FSD.md)
- **BFF:** validates `Authorization: tma <initData>`, then **backend `/access`** (те же пары `(user_id, chat_id)`, что и у бота)
- **Dev browser:** `Authorization: dev` when `APP_ENV=dev` with `DEV_ADMIN_USER_ID` + `DEV_MINI_APP_CHAT_ID`

## Trusted chats (with backend)

| Channel | Env chat id |
|---------|-------------|
| Bot in ops group | `ADMIN_CHAT_ID` |
| Mini App | `MINI_APP_CHAT_ID` |

Same `ADMIN_USER_ID` in backend; Mongo holds two `(user_id, chat_id)` rows.

## Setup

```bash
cp .env.example .env
# TELEGRAM_BOT_TOKEN, BOT_API_TOKEN, API_BASE_URL
# DEV_ADMIN_USER_ID + DEV_MINI_APP_CHAT_ID for browser dev
# Private vars must be listed in src/env.ts (SvelteKit 3)
npm install
```

Run backend + mongo + mock, then:

```bash
npm run dev
```

Open http://localhost:5173 — uses dev auth (`DEV_MINI_APP_CHAT_ID` as chat).

## Telegram / BotFather

1. Deploy mini app over **HTTPS** (prod: `web` service on port 3000 behind TLS).
2. BotFather: domain + `WEBAPP_URL` in bot env.
3. Open Mini App from chat **`MINI_APP_CHAT_ID`** (e.g. private chat). Not from the bot ops group.

## Scripts

- `npm run dev` — Vite dev server + BFF routes
- `npm run build` / `npm run preview` — production Node adapter
- `npm run check` — svelte-check
- `npm test` — initData + auth unit tests

## API routes (BFF)

| Route | Description |
|-------|-------------|
| GET `/api/me` | Access check |
| GET `/api/guests?kind=qemu\|lxc` | Guest list |
| GET `/api/guests/:kind/:vmid` | Guest card |
| POST `/api/guests/:kind/:vmid/:action` | Power action + status poll |

Power actions: `start`, `stop`, `shutdown`, `reboot`, `suspend`, `resume`.

## Docker prod

Root `.env.prod`: `MINI_APP_CHAT_ID` for api + web (same value), plus tokens.

```bash
docker compose -f docker-compose.prod.yml up -d --build web
```
