# Roadmap — Lokyy Workspace

> 🚧 **Build in Public · Beta.** This roadmap is live and evolves as we build. Milestones are
> tracked publicly. The **MVP** (M0–M2) delivers the self-learning agent — our first
> public-facing moment.

Status: ⬜ planned · 🟦 in progress · ✅ done

## MVP

### M0 — Foundation & Setup 🟦
Runnable skeleton: backend + frontend + DB + auth in Docker, public on GitHub from day one.
- ✅ Monorepo + License (AGPL-3.0 + CLA), README, secret hygiene, public repo
- ✅ Docker Compose: FastAPI + PostgreSQL + pgvector (runnable stack, pytest green)
- ⬜ DB foundation + owner/org scoping
- ⬜ Auth: sessions, 2FA, API tokens
- ⬜ Next.js PWA skeleton + connection switch
- ⬜ CI + test scaffold

### M1 — Agent Core ⬜
Working chat agent with tools, model-agnostic (multi-provider LLM, agent loop, tool system,
RAG tool selection, sandbox for shell/code, chat UI).

### M2 — Self-Learning Agent (MVP killer feature) ⬜
Agent that knows the user and keeps context clean: Workspace primitive, Telos + Soul.md/User.md,
Memory (pgvector), Context Assembler, self-improvement loop.

## Beyond MVP

- **M3 — Projects, file tree, editor, artifacts** ⬜ — full in-system workspace + artifact panel.
- **M4 — Workflows & multi-agent** ⬜ — workflow/step engine, orchestrator, skill chaining, scheduler.
- **M5 — Privacy & security** ⬜ — data anonymization (German PII), cryptographic (PAdES) signatures, hardening.
- **M6 — Productivity suite** ⬜ — email, calendar/contacts, documents, notes (German providers).
- **M7 — Sync & team** ⬜ — local⇆server sync, 3 modes, shared workspaces + merge, multi-tenant, PWA.
- **M8 — Brand, polish & launch** ⬜ — branding, onboarding, accessibility (BFSG), launch.

---

Follow the build: [Website](https://aiianer.de) · [YouTube](https://youtube.com/@aiianer) · [Community](https://skool.com/aiianer)
