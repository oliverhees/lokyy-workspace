<p align="center">
  <img src="assets/brand/lokyy-logo.png" alt="Lokyy" width="120">
</p>

<h1 align="center">lokyy workspace</h1>

<p align="center">
  <strong>Das self-hosted KI-Betriebssystem für Selbstständige und KMU — Datenschutz zuerst, made in Germany.</strong>
</p>

<p align="center">
  <a href="README.md">🇬🇧 English</a> &nbsp;·&nbsp; 🇩🇪 Deutsch
</p>

<p align="center">
  <a href="#lizenz"><img src="https://img.shields.io/badge/license-AGPL--3.0-blue.svg" alt="License: AGPL-3.0"></a>
  <img src="https://img.shields.io/badge/status-beta-orange.svg" alt="Status: Beta">
  <img src="https://img.shields.io/badge/build%20in%20public-%F0%9F%9A%80-22D3EE.svg" alt="Build in Public">
  <img src="https://img.shields.io/badge/PRs-willkommen-2563EB.svg" alt="PRs willkommen">
  <br>
  <img src="https://img.shields.io/badge/Python-FastAPI-009688.svg" alt="Python / FastAPI">
  <img src="https://img.shields.io/badge/TypeScript-Next.js-000000.svg" alt="TypeScript / Next.js">
  <img src="https://img.shields.io/badge/PostgreSQL-pgvector-336791.svg" alt="PostgreSQL + pgvector">
  <img src="https://img.shields.io/badge/Docker-self--hosted-2496ED.svg" alt="Docker">
</p>

<p align="center">
  <a href="https://aiianer.de">🌐 Website</a> ·
  <a href="https://youtube.com/@aiianer">▶️ YouTube</a> ·
  <a href="https://skool.com/aiianer">👥 Community</a> ·
  <a href="docs/UMSETZUNGSPLAN.md">🗺️ Roadmap</a>
</p>

<p align="center">
  <img src="docs/mockups/lokyy-dashboard-dark.png" alt="Lokyy Workspace — Dashboard" width="860">
</p>

---

> ⚠️ **Beta · Build in Public.** Lokyy steckt in aktiver, früher Entwicklung. Wir bauen es offen — jeder Meilenstein, jeder Commit und jede Entscheidung passiert öffentlich. Begleite uns, gib Feedback und gestalte mit. Erwarte raue Kanten; das Fundament wird gerade gelegt.

## Was ist Lokyy?

**Lokyy Workspace** ist nicht nur ein weiteres KI-Chat-Tool — es ist ein self-hosted **KI-Betriebssystem**: die zentrale Plattform, über die du deine gesamte KI-gestützte Arbeit betreibst. Ein **selbstlernender Agent**, Projekte, Dateien, automatisierte Workflows und Skills laufen darin zusammen wie Programme auf einem Betriebssystem — **komplett lokal auf deinem Rechner** oder **auf deinem eigenen Server**.

Eine eigenständige Clean-Room-Implementierung, gebaut für den **deutschen / europäischen Markt**: DSGVO-by-default, EU-Hosting, deutsche Provider, echte E-Signaturen — volle Datensouveränität.

## ✨ Features

- 🧠 **Selbstlernender Agent** — lernt dich über die Zeit kennen (Telos, `Soul.md`/`User.md`, Memory), hält den Kontext sauber durch Retrieval statt Müll.
- 🤝 **Multi-Agent-Orchestrierung** — ein Orchestrator, der Sub-Agenten callt und parallelisiert.
- ⚡ **Workflows & Skill-Verkettung** — verkettete, zeitgesteuerte, vollautomatische Abläufe mit Artefakten + Notifications.
- ◆ **Artefakt-Panel** — live gerenderte Visualisierungen, Diagramme, PDFs und Code (sandboxed), wie bei Claude.
- 🗂️ **Projekte, Dateibaum & nativer Editor** — arbeite direkt im System an deinen Dateien.
- 🛡️ **Daten-Anonymisierung** — optionale PII-Entfernung (deutsche Muster), bevor etwas ein Cloud-Modell erreicht.
- 🔐 **Datenschutz by design** — lokale Modelle, Verschlüsselung at rest/in transit, echte kryptografische (PAdES) Signaturen.
- 🔄 **Lokal ⇆ Server-Sync** — drei Modi (offline / hybrid / remote), offline-fähige PWA, geteilte Team-Workspaces.
- 📬 **Produktiv-Suite** — Mail, Kalender/Kontakte, Dokumente, Notizen — mit deutschen Providern (mailbox.org, Posteo, Nextcloud …).

## 🇩🇪 Warum Lokyy (für den deutschen Markt)

Datensouveränität als erstklassiges Feature: **DSGVO-by-default**, EU-Hosting, deutsche LLM-/Provider-Unterstützung, volle deutsche Lokalisierung, echte **eIDAS-taugliche** Signaturen und Barrierefreiheit (BFSG). Gebaut für Selbstständige und KMU, die Kundendaten nicht in US-Clouds geben dürfen.

## 🧱 Tech-Stack

| Schicht | Technologie |
|---------|-------------|
| Frontend | TypeScript · Next.js (PWA) · Tailwind · shadcn/ui |
| Backend | Python · FastAPI |
| Datenbank | PostgreSQL + pgvector |
| Infra | Docker (Image-Paritaet lokal/Server) |
| LLM | modell-agnostisch — lokal (Ollama/vLLM/llama.cpp) + Cloud (Anthropic, OpenAI, Mistral-EU, Aleph Alpha …) |

## 🚀 Schnellstart

> Kommt bald — das Fundament wird gerade gebaut. Das Docker-Setup landet mit dem ersten Meilenstein (M0).

```bash
git clone https://github.com/oliverhees/lokyy-workspace.git
cd lokyy-workspace
cp .env.example .env
docker compose up -d --build   # (verfügbar sobald M0 fertig ist)
```

## 🗺️ Roadmap

Gebaut in Meilensteinen M0–M8. Volle Details in [`ROADMAP.md`](ROADMAP.md).

- 🟦 **M0 — Fundament & Setup** *(in Arbeit)*
- ⬜ **M1 — Agent-Kern**
- ⬜ **M2 — Selbstlernender Agent** — *MVP-Killer-Feature*
- ⬜ M3 — Projekte, Dateibaum, Editor, Artefakte
- ⬜ M4 — Workflows & Multi-Agent
- ⬜ M5 — Datenschutz & Sicherheit
- ⬜ M6 — Produktiv-Suite
- ⬜ M7 — Sync & Team
- ⬜ M8 — Brand, Politur & Launch

## 📣 Build in Public

Wir bauen Lokyy komplett offen. Verfolge den Weg, stell Fragen und mach mit:

- 🌐 **Website:** https://aiianer.de
- ▶️ **YouTube:** https://youtube.com/@aiianer
- 👥 **Community:** https://skool.com/aiianer

## 🤝 Mitwirken

Beiträge sind willkommen! Da Lokyy dual-lizenzierbar ist (siehe unten), erfordern alle Beiträge die Unterzeichnung unseres **CLA** (siehe [`CLA.md`](CLA.md)). Starte mit der Roadmap und einem Issue.

## 📜 Lizenz

Lizenziert unter **AGPL-3.0-or-later** — siehe [`LICENSE`](LICENSE). Beiträge werden unter einem **CLA** angenommen, das spätere Dual-Lizenzierung erlaubt, sodass Lokyy offen bleiben **und** kommerziell angeboten werden kann. Das Copyright liegt vollständig beim Projekt (Clean-Room-Implementierung — kein Fremdcode übernommen).

## ⭐ Star History

<a href="https://star-history.com/#oliverhees/lokyy-workspace&Date">
  <img src="https://api.star-history.com/svg?repos=oliverhees/lokyy-workspace&type=Date" alt="Star History Chart" width="600">
</a>
