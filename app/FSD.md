# FSD import rules

- Slice folder names under `entities/`, `features/`, `widgets/`, `pages/` use **camelCase** (e.g. `accessGate`, `guestDetail`, `appShell`).
- Allowed: `pages` → `widgets` → `features` → `entities` → `shared`
- Forbidden: `entities` → `features`, `shared` → upper layers
- Client code must not import `$lib/server/*` (server-only BFF)
- Public API of a slice: export via slice `index.ts`
