# Contributing to Lokyy Workspace

Lokyy is built **in public** and contributions are welcome — thank you! 🚀
This is an early-stage **beta**; the foundation is being laid, so expect rapid change.

## Before you start

- Read the [Roadmap](docs/UMSETZUNGSPLAN.md) and the concept docs in [`docs/`](docs/).
- Open an issue to discuss non-trivial changes before investing a lot of work.

## Ground rules

1. **Sign the CLA.** All contributions require agreeing to the [CLA](CLA.md) — add the
   sign-off line to your first PR description. This keeps Lokyy dual-licensable.
2. **Never commit secrets.** See [SECURITY.md](SECURITY.md). Run the pre-push secret scan.
   Only `*.example` config belongs in the repo.
3. **Clean-room only.** Do not copy code from incompatibly-licensed projects (e.g. the
   AGPL reference project odysseus). Implement from behavior/specification.
4. **Write the docs.** Documentation is part of the work, not an afterthought — update the
   Starlight docs (`docs-site/`) for the task you touch.
5. **Tests + green build.** Follow a test-driven flow where it makes sense; keep CI green.

## Tech stack

- **Frontend:** TypeScript · Next.js (PWA) · Tailwind · shadcn/ui
- **Backend:** Python · FastAPI
- **Database:** PostgreSQL + pgvector
- **Docs:** Astro Starlight (`docs-site/`)
- **Infra:** Docker

## Workflow

1. Fork & branch from `main`.
2. Make your change with tests + docs.
3. Run the secret scan and the test suite.
4. Open a PR with the CLA sign-off and a clear description.

Questions? Join the [community](https://skool.com/aiianer) or follow along on
[YouTube](https://youtube.com/@aiianer).
