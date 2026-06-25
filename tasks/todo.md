# Todo — Lokyy Workspace (Stand 2026-06-25)

## ✅ Phase F — App-Fundament & Shell — fertig + QA-Gate bestanden
- [x] **F1** Auth end-to-end (Login/Registrierung/2FA/Logout, geschützte Routen)
- [x] **F1.1** Dedizierte Dev-Postgres (Docker, Host-Port 5435)
- [x] **F2** App-Shell + Navigation (Sidebar/Topbar/(app)-Routing)
- [x] **F3** Settings-Framework (UserSettings + Settings-Seite) · **F3.1** Tab-Navigation + schlankere Buttons
- [x] **F4** Modell-Verwaltung (verschlüsselte Keys) · **F4.1** LiteLLM-Multi-Provider · **F4.2** Modell-Discovery
- [x] **F5** Chat echt + Sessions + Sidebar · **F5.1** Phasen-Indikator + Metadaten · **F5.2** Eingabeleiste (Modell-Wahl + Aktions-Vorschau)
- [x] 🚩 **QA-Gate bestanden** (SSRF/Auth/Härtung gefixt, 93 Tests)

## ✅ M2 — Lernender Agent — feature-komplett (QA-Gate ausstehend)
- [x] **M2.1** Kontext-Layer (Soul + Nutzerprofil + Context-Assembler → System-Prompt)
- [x] **M2.2** Memory (pgvector, pluggable Embeddings lokal/Cloud, semantischer Recall)
- [x] **M2.3** Self-Improvement (Fakten aus Gesprächen → Memory)
- [x] **M2.4** Telos (Mission/Ziele/Challenges im Kontext)
- [ ] 🚩 **QA-Gate für M2** (Security/Scoping bei Memory+Context, Prompt-Injection beim Fakten-Extrahieren, Coverage)

## Offene Folge-Tasks (Backlog aus QA-Gate F)
- [ ] Rate-Limiting (Auth) · DSGVO (Audit-Log/Löschung) · Re-Auth+Passwort-HIBP · Chat-UI-Robustheit (AbortController)

## Nächste Meilensteine
- [ ] M3 Projekte/Dateien/Editor (schaltet „+"-Menü, Sidebar-Projekte, „In Projekt arbeiten")
- [ ] M4 Workflows/Multi-Agent (+ Agent-Mode/YOLO, Skills) · M5 DSGVO/eIDAS · M6 Produktiv-Suite · M7 Sync/Team · M8 Brand/Launch
- [ ] Dashboard als Startseite nach Login (nach M-Features mit echten Daten)

**Nächster konkreter Start:** QA-Gate für M2, dann M3.
**Tests:** 105 grün · **Git:** alles committet + gepusht (oliverhees/lokyy-workspace).
