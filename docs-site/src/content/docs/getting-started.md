---
title: Erste Schritte
description: Lokyy Workspace lokal aufsetzen.
---

:::caution[In Entwicklung]
Das Docker-Setup landet mit Meilenstein **M0**. Diese Seite wächst mit dem Projekt.
:::

## Voraussetzungen (geplant)

- Docker & Docker Compose
- (optional) ein lokales LLM via Ollama/vLLM/llama.cpp

## Schnellstart (geplant)

```bash
git clone https://github.com/oliverhees/lokyy-workspace.git
cd lokyy-workspace
cp .env.example .env
docker compose up -d --build
```

:::tip[Ports]
Das Backend läuft standardmäßig auf **http://localhost:8008** (über `APP_PORT` in der `.env`
änderbar, falls 8008 belegt ist). Die **Datenbank ist nur intern** im Compose-Netz erreichbar
(kein Host-Port) — das vermeidet Konflikte und hält den DB-Port nicht offen. Für direkten
DB-Zugriff: `docker compose exec db psql -U lokyy`.
:::

## Mitmachen

Beiträge sind willkommen — siehe `CONTRIBUTING.md` und `CLA.md` im Repo. Niemals Secrets committen (`SECURITY.md`).
