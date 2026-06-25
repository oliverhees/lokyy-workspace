# Lokyy Workspace — Frontend

TypeScript · **Next.js 16** (App Router, **bun**) · Tailwind v4 · next-intl (i18n) · PWA.

## Status (M0)

- ✅ Next.js scaffold with brand theme (Cyan→Blue gradient, dark/light) — see `app/globals.css`
- ✅ **Connection switch** Local/Remote (configurable backend URL + live health check) — `lib/connection.ts`, `components/ConnectionSwitch.tsx`
- ✅ **i18n base architecture** (next-intl, DE default + EN, cookie-based) — `messages/*.json`, no hardcoded UI strings
- ✅ PWA manifest

## Develop

```bash
cd frontend
bun install
bun run dev          # http://localhost:3000 (or: bun run dev -p 3008)
bun run build        # production build
```

Backend URL via env: `NEXT_PUBLIC_API_BASE_URL` (local, default http://localhost:8008),
`NEXT_PUBLIC_SERVER_URL` (remote, optional — enables the Remote switch).

## i18n

UI strings live in `messages/de.json` (default) and `messages/en.json`. Add a key to both,
use `useTranslations("namespace")`. Language switches via the `locale` cookie (DE/EN switcher).

## Design

Brand gradient Cyan `#22D3EE` → Blue `#2563EB`, Slate neutrals, Inter. Mockups: `../docs/mockups/`.
