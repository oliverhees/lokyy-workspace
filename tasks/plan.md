# Umgeplante Roadmap — Fundament-first (App-Shell zuerst)

> **Korrektur der Reihenfolge.** Bisher: Feature-Bausteine ohne nutzbare App-Hülle.
> Neu (Olivers Vorgabe): erst die tragende Anwendung (Login → Shell → Settings →
> echte Modell-Anbindung → Chat), dann Features. Vertikale Slices statt horizontaler Layer.
> Status dieses Dokuments: **Vorschlag zur Freigabe.** Nichts in Plane angelegt.

## Was steht (Fundament-Bausteine, bleiben gültig)
- M0: Repo/Docker/PostgreSQL+pgvector/**Backend-Auth** (argon2/2FA/Tokens)/CI
- M1: LLM-Layer (modell-agnostisch), Agent-Loop, Tool-System+Policy, Tool-Selektion, Sandbox, Chat-UI-Seite, /chat (Echo)
- → Das sind **Bausteine**. Es fehlt die **App, die sie nutzbar macht.**

## Abhängigkeitsgraph (linear, jede Phase = vertikaler Durchstich)
```
F1 Auth-UI  →  F2 App-Shell  →  F3 Settings-Framework  →  F4 Modell-Verwaltung  →  F5 Chat echt+Sessions
   (nutzt        (geschützte      (Settings-Seite          (Endpoints/Keys in        (Agent-Loop gegen
    Auth-BE)      Routen)          + Persistenz)            Settings, verschlüsselt)   echtes Modell)
                                                                                          ↓
                                                              M2 Lernender Agent (jetzt erlebbar) → M3 … M8
```

---

## NEUE PHASE: F — App-Fundament & Shell (vor den Feature-Meilensteinen)

### F1 — Auth end-to-end (Frontend)
Login/Registrierung/2FA/Logout-UI gegen das bestehende Auth-Backend; eingeloggt bleiben; geschützte Routen.
- **AC:** Registrieren → einloggen → Reload bleibt eingeloggt (`/auth/me`) → Logout. 2FA-Schritt wenn aktiv. Nicht-eingeloggt → Redirect auf /login.
- **Verify:** Sichtprüfung (Chrome): kompletter Flow register→login→geschützte Seite→logout; Backend-Tests für Flows existieren.

### F2 — App-Shell + Navigation
Authentifizierte Layout-Hülle: Sidebar (Menüpunkte), Topbar (User-Menü, Connection-Switch, Sprache), Routing-Gruppe `(app)`.
- **AC:** Eingeloggte Nutzer sehen die Shell mit Navigation; Menüpunkte routen; Logout im User-Menü. Features werden hier eingehängt.
- **Verify:** Sichtprüfung: Shell rendert, Navigation funktioniert, Brand/Light-Dark/i18n.

### F3 — Settings-Framework
Zentrale Einstellungen, über die alles läuft. Backend: `UserSettings`-Persistenz + API. Frontend: Settings-Seite mit Sektionen (Profil, Sprache/Theme, Verbindung lokal/server).
- **AC:** Einstellungen speichern + bleiben nach Reload; Sektionen erweiterbar.
- **Verify:** Backend-Tests (Settings-CRUD owner-scoped) + Sichtprüfung.

### F4 — Modell-Verwaltung (modell-agnostisch) in Settings
`ModelEndpoint`-Modell (base_url, model, **api_key verschlüsselt**) + CRUD-API; Settings-Sektion „Modelle".
- **AC:** Endpoint anlegen/bearbeiten/löschen; Key verschlüsselt at rest (nie im Klartext zurück); Default-Modell wählbar.
- **Verify:** Backend-Tests (CRUD, Verschlüsselung, owner-scope) + Sichtprüfung.

### F5 — Chat echt + Sessions + Sidebar
`/chat` nutzt den **echten Agent-Loop** (Tools + Selektor) gegen das in F4 konfigurierte Modell; Sessions persistieren (`ChatSession`/`ChatMessage`); Sidebar mit Konversationsliste (neu/wechseln/löschen); Chat in die Shell integriert.
- **AC:** Eingeloggter Nutzer wählt Modell → chattet → echte Antwort (kein Echo) → Session bleibt nach Reload, in Sidebar wählbar.
- **Verify:** Backend-Tests (Sessions-CRUD, /chat mit gemocktem LLM) + **E2E-Sichtprüfung** mit echtem (oder lokalem) Modell.

**🚩 Checkpoint nach F5:** Vollwertige, benutzbare App (Login → Shell → Settings/Modell → echter Chat mit Verlauf). **Erst hier startet QA-Gate-Pass, dann die Feature-Meilensteine.**

---

## Feature-Meilensteine (bestehend, neu eingeordnet — NACH F)
- **M2 — Lernender Agent** (jetzt erlebbar): Telos, Soul.md/User.md, Memory, Context Assembler, Self-Improvement — lernt aus den echten, persistierten Gesprächen.
- **M3** Projekte/Dateibaum/Editor/Artefakte · **M4** Workflows/Multi-Agent · **M5** DSGVO/Sicherheit (Anonymisierung, eIDAS) · **M6** Produktiv-Suite · **M7** Sync/Team · **M8** Brand/Launch.

## Plane-Umsetzung (bei Freigabe)
Neues Modul **„F — App-Fundament & Shell"** mit Tasks F1–F5, einsortiert **vor** dem bestehenden M2. M2–M8 bleiben inhaltlich, rücken in der Reihenfolge dahinter. **Nächster Start: F1 (Auth-UI).**
