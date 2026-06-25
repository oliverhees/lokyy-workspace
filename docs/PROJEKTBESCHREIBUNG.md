# Lokyy Workspace — Projektbeschreibung

> Marke: **Lokyy** (Schreibweise: „lokyy"). Produkt: **Lokyy Workspace**.
> Status: Planungsphase abgeschlossen, vor Umsetzung. Build in Public.

## Was ist Lokyy Workspace?
Lokyy Workspace ist ein **self-hosted KI-Betriebssystem für Selbstständige und KMU in
Deutschland** — die **zentrale Plattform, über die man seine gesamte KI-gestützte Arbeit
betreibt**. Ein lernender KI-Agent, Projekte und Dateien, automatisierte Workflows und
erweiterbare Skills laufen darin zusammen wie Programme auf einem Betriebssystem: sensible
Daten **DSGVO-konform**, wahlweise **komplett lokal auf dem eigenen Rechner** oder **auf dem
eigenen Server**. Nicht ein KI-Tool unter vielen, sondern das **Betriebssystem für die
KI-gestützte Arbeit**.

Es ist eine eigenständige **Clean-Room-Reimplementierung** (inspiriert vom Open-Source-Projekt
odysseus, jedoch **kein Fork** — eigener Code, eigene Lizenz, voller Eigenbesitz).

## Das Problem
Selbstständige und kleine Unternehmen wollen KI nutzen, dürfen aber Mandanten-, Kunden- und
Geschäftsdaten nicht einfach in US-Cloud-Dienste geben. Bestehende KI-Tools sind entweder
Cloud-gebunden (Datenschutzrisiko), zu komplex (für Entwickler gebaut) oder bieten keinen
durchgehenden Arbeits-Workspace. Es fehlt eine Lösung, die **Datensouveränität, einfache
Bedienung und echte Produktivität** verbindet.

## Zielgruppe
Selbstständige, Freelancer, kleine und mittlere Unternehmen im deutschsprachigen Raum —
inklusive Anwendungsfälle mit erhöhtem Datenschutzbedarf (Beratung, Kanzleien, Agenturen,
Handwerk mit Kundendaten, Gesundheits-/Finanznähe).

## Die Lösung — Kernversprechen
- **Datensouveränität:** läuft lokal oder auf dem eigenen Server. Daten bleiben beim Nutzer.
- **DSGVO-by-default:** zuschaltbare Daten-Anonymisierung vor jedem Cloud-LLM-Versand; lokale Modelle möglich.
- **Lernender Agent:** kennt den Nutzer über Zeit (Telos, Soul.md/User.md, Memory) und verbessert sich.
- **Voller Workspace:** Projekte, Dateibaum, nativer Editor, Live-Artefakte, Workflows.
- **Lokal ↔ Server umschaltbar + synchron:** zu Hause lokal arbeiten, unterwegs per PWA, alles synchronisiert.
- **Teamfähig:** geteilte Workspaces für Mitarbeiter (Firmen-Setup, Multi-Tenant).

## Kernfeatures
1. **Lernender KI-Agent** — Kontext-/Lern-Layer (Telos nach Miessler, Soul.md/User.md, Memory), retrieval-basiert (kein Kontext-Müll), selbstverbessernd. **(MVP-Killer-Feature #1)**
2. **Multi-Agent / Orchestrator** — ein Orchestrator-Agent callt und parallelisiert Sub-Agenten.
3. **Workflows & Skill-Verkettung** — verkettete, zeitgesteuerte, vollautomatische Abläufe; Ergebnis als Artefakt + Notification.
4. **Artefakt-Panel** — Live-Rendering (Visualisierungen, Diagramme, PDF, Code, Tabellen) in sicherer Sandbox, wie bei Claude.
5. **Projekte, Dateibaum & nativer Editor** — Projekte mit zugewiesenem Ordner, ein-/ausblendbarer Verzeichnisbaum, direkte Datei-Bearbeitung im System.
6. **Daten-Anonymisierung** — zuschaltbarer PII-Schutz (deutsche Muster) vor LLM-Versand, global oder pro Chat.
7. **Wissens-Layer** — RAG/Memory auf PostgreSQL + pgvector.
8. **Produktiv-Suite** — Chat, Dokumente, E-Mail, Kalender/Kontakte (deutsche Provider via Standard-Protokolle), Notizen/Tasks.
9. **Kryptografische Signatur** — echte PAdES/FES-Signatur (statt bloßem Bild-Stempel); QES später via QTSP.
10. **Lokal/Server-Sync + geteilte Workspaces** — drei Betriebsmodi, Offline-fähig, Team-Merge.

## Differenzierung gegenüber bestehenden Lösungen (insb. odysseus)
- **Deutscher Markt zuerst:** DSGVO-by-default, EU-Hosting, deutsche Provider, volle DE-Lokalisierung (odysseus ist EN, teils JP-Reste).
- **Daten-Anonymisierungs-Layer** — eigenes, besseres System mit deutschen PII-Mustern.
- **Echte kryptografische Signatur** (odysseus: nur Bild-Stempel).
- **Lokal↔Server-Sync + geteilte Team-Workspaces** (odysseus: Einzel-Instanz).
- **Moderne Architektur:** TypeScript/Next.js-PWA + Python/FastAPI, PostgreSQL+pgvector, modular (odysseus: Vanilla-JS, 4.000-Zeilen-Dateien, SQLite-default).
- **Echtes Sandboxing** der Code-/Shell-Tools (odysseus: bekannte Lücke).
- **Artefakt-Panel + nativer Datei-Editor mit Projekt-Ordnern.**

## Architektur (Kurzüberblick)
- **Frontend:** TypeScript / Next.js (PWA), Tailwind + shadcn/ui.
- **Backend:** Python / FastAPI.
- **Datenbank:** PostgreSQL + pgvector.
- **Deployment:** Docker (Image-Parität lokal/Server).
- **4 Kern-Primitive:** Workspace · Agent-/Workflow-Runtime · Kontext-/Lern-Layer · Sync-Layer.
- Technische Tiefe: siehe `docs/KONZEPT.md`.

## Betriebsmodelle
- **Nur lokal** (keine Server nötig).
- **Hybrid** (lokal arbeiten, mit eigenem Server synchronisieren, PWA unterwegs).
- **Nur remote** (alles auf dem Server).
- **Firmen-Setup:** Organisation → Mitarbeiter → geteilte Workspaces (Multi-Tenant).

## Geschäftsmodell
Open Source (Build in Public) als Fundament + **kommerzielle Dienstleistung**: Installation,
Einrichtung und Managed-Hosting beim Kunden („wir setzen es auf dem Firmenserver auf").
Später optional: kommerzielle Lizenzen / Hosting-Angebote.

## Lizenz
**AGPL-3.0 + CLA** (Contributor License Agreement). Offen und Copyleft-geschützt, durch das CLA
zugleich **später kommerziell vertreibbar** (Dual-License). Copyright vollständig bei uns
(Clean-Room — kein übernommener Fremdcode).

## Status & nächster Schritt
Konzept- und Architekturphase abgeschlossen (dieses Dokument + `docs/KONZEPT.md`).
Nächster Schritt: strukturierter Umsetzungsplan (Meilensteine + Tasks) zur Review — **erst nach
ausdrücklicher Freigabe** wird er in Plane (Single Source of Truth) angelegt.
