# FSD import rules

- Allowed: `pages` → `widgets` → `features` → `entities` → `shared`
- Forbidden: `entities` → `features`, `shared` → upper layers
- Client code must not import `$lib/server/*` (server-only BFF)
- Public API of a slice: export via slice `index.ts`
