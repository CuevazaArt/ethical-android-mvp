# Deploy notes

- **Production-ish Docker Compose:** [COMPOSE_PRODISH.md](COMPOSE_PRODISH.md) — merge files, metrics opt-in, secrets in `.env` only.
- **Staging verification:** same doc — *Verification checklist* (`/health`, `/metrics` 200 vs 404 when metrics off, compose `config` parity with CI).
