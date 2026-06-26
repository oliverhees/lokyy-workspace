---
title: M3 — Projekte, Dateien, Editor
description: Voller In-System-Arbeitsplatz — echte Ordner, Projekte, Dateibaum, Editor, Artefakte.
sidebar:
  order: 4
---

**Ziel:** ein voller Arbeitsplatz im System — Projekte als echte Ordner, Dateibaum,
nativer Editor, Artefakt-Panel. Vertikale Slices, jeder für sich erlebbar.

## Architektur-Entscheidung: echtes Dateisystem

Datei-**Inhalte** liegen im **echten Dateisystem**, nicht in der DB. Grund ist die
Produktvision: Der Agent soll später echte Tools ausführen (ffmpeg, Code, Dateien
erzeugen) — das geht nur gegen echte Pfade, nicht gegen DB-Blobs. Die DB hält nur
**Metadaten** (Projekte, Kontext-Zuordnung). Der Verzeichnisbaum liest das FS direkt.

- **Workspace = echter Wurzelordner** (`<storage_root>/<workspace_id>/`). Jeder User
  hat von Anfang an einen eigenen (Default „Mein Workspace", umbenennbar). Geteilte
  Ordner kommen erst beim Verbinden mit einem anderen System hinzu (M7-Sync).
- **Projekt = Unterordner + zugewiesener Kontext.** Alles Erstellte landet im Ordner.
- **Sicherheit auf zwei Ebenen:** (1) Pfad-Scoping ab Tag 1 (M3.0), (2) die schwere
  Tool-Ausführungs-Sandbox bewusst auf die Agent-Runtime-Stufe (M4) geschoben.
  Betriebsmodell: alles in Docker/Sandbox, tiefgreifende Aktionen brauchen Bestätigung.

## Tasks

- **M3.0 — Workspace-FS-Fundament** ✅
  `WorkspaceFS` (`app/core/workspace_fs.py`): sichere Pfad-Auflösung. `resolve(workspace_id,
  rel_path)` garantiert, dass jeder Pfad innerhalb von `<root>/<workspace_id>/` bleibt —
  abgewehrt werden `..`-Traversal, absolute Pfade, **Symlink-Escapes**, Null-Bytes und
  ungültige Workspace-IDs (Mechanik: `Path.resolve()` + `is_relative_to`-Check). Storage-Root
  als typisiertes Setting (`workspace_storage_root`, in Docker ein gemountetes Volume).
  **Verifiziert:** 10 Escape-Tests → 117 Tests gesamt grün. Reines Backend-Fundament (kein UI).
- **M3.1 — Projekte-Primitiv** — `Project`-Entity + echter Unterordner, CRUD-API, Sidebar.
- **M3.2 — Verzeichnisbaum + Datei-Operationen** — Baum liest das FS, Datei/Ordner-Ops.
- **M3.3 — Nativer Editor** — CodeMirror, echte Dateien editieren/speichern.
- **M3.4 — Projekt-Kontext-Bindung** — Chat „im Projekt" nutzt projektgebundenen Kontext (M2).
- **M3.5 — Artefakt-Panel** — Live-Render in sandboxed iframe.
