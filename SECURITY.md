# Security Policy

Lokyy Workspace is a self-hosted AI operating system with privileged local capabilities.
Treat it like an admin console — do not run it as a public, unauthenticated service.

## ⚠️ Never commit secrets (Build in Public)

This is a public, build-in-public repository. **No secrets, ever**, in versioned files:

- API keys, tokens, passwords, credentials → only via `.env` / environment, never committed.
- `.env` is git-ignored. Only `.env.example` (with placeholder values) belongs in the repo.
- Do not commit: real `.env`, databases, `data/`, logs, uploads, generated media, backups,
  auth/session files, password hashes, model/provider tokens, or personal documents.

### Pre-push secret scan

Before any push, run:

```bash
git status --short
git check-ignore -v .env
git grep -nIE "(sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{20,}|xox[baprs]-|Bearer [A-Za-z0-9._~+/-]{20,}|plane_api_[A-Za-z0-9]+)" -- . ':!*.example'
```

If anything matches outside `*.example`, **stop** and remove it before pushing. Rotate any
key that ever appeared in a commit, log, screenshot, or shared chat.

## Deployment Guidance

- Keep authentication enabled for any network-accessible deployment.
- Use HTTPS (via a trusted reverse proxy) when exposing beyond localhost; put the app behind
  a private access layer (Cloudflare Access, Tailscale, VPN) where possible.
- Keep internal services (PostgreSQL, local model servers, etc.) internal-only.
- Encrypt secrets at rest; use strong admin passwords and 2FA.

## Reporting a Vulnerability

Please report vulnerabilities privately via GitHub Security Advisories, or open a minimal
issue that does not disclose exploit details. We will respond as fast as we can — this is an
early-stage beta built in public.
