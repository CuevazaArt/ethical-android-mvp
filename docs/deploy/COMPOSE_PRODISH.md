# Compose — production-ish stack

**Goal:** run the Ethos Kernel chat server in Docker with **LAN-safe defaults**, **optional Prometheus metrics**, and **no secrets in the image**.

**Related:** root [`docker-compose.yml`](../../docker-compose.yml), [`docker-compose.prodish.yml`](../../docker-compose.prodish.yml), [`docker-compose.metrics.yml`](../../docker-compose.metrics.yml), [`Dockerfile`](../../Dockerfile), [`.dockerignore`](../../.dockerignore), [`.env.example`](../../.env.example), [`KERNEL_ENV_POLICY.md`](../proposals/KERNEL_ENV_POLICY.md).

---

## Principles

| Topic | Practice |
|--------|----------|
| **Secrets** | Keep API keys, Fernet checkpoint keys, audit HMAC seeds, and nomadic keys in **`.env`** (or your orchestrator’s secret store). **Do not** `COPY` them into a custom image layer; the repo [`.dockerignore`](../../.dockerignore) excludes `.env` and `.env.*` from the build context. |
| **OpenAPI** | **`KERNEL_API_DOCS=0`** in the prodish overlay so `/docs`, `/redoc`, and `/openapi.json` are not exposed by default on LAN binds. |
| **Metrics** | **`KERNEL_METRICS=0`** in the prodish overlay. Enable scraping with a second merge file or set `KERNEL_METRICS=1` in `.env`. |
| **Profiles** | Base compose **`llm`** profile still adds **Ollama** when you need it; combine with `-f` merges in any order that keeps `services.app` defined once. |

---

## Quick start

From the repository root:

```bash
cp .env.example .env
# Edit .env for your deployment (see .env.example comments).

docker compose -f docker-compose.yml -f docker-compose.prodish.yml up --build
```

Health: `http://localhost:8765/health`  
WebSocket: `ws://localhost:8765/ws/chat`

---

## Optional: Prometheus `/metrics`

```bash
docker compose -f docker-compose.yml -f docker-compose.prodish.yml -f docker-compose.metrics.yml up --build
```

Scrape `http://localhost:8765/metrics` (same host/port as the app). See [`README.md`](../../README.md) (Docker / observability) for what counters exist.

---

## Optional: Ollama sidecar

```bash
docker compose -f docker-compose.yml -f docker-compose.prodish.yml --profile llm up --build
```

Set in `.env` (not in the image), for example:

- `LLM_MODE=ollama`
- `USE_LOCAL_LLM=1`
- `OLLAMA_BASE_URL=http://ollama:11434`

---

## Runtime profile bundle

Optional one-shot operator bundles (unset keys only; explicit env wins): **`ETHOS_RUNTIME_PROFILE`** — see [`src/runtime_profiles.py`](../../src/runtime_profiles.py) and [`RUNTIME_PROFILES_OPERATOR_TABLE.md`](../proposals/RUNTIME_PROFILES_OPERATOR_TABLE.md). Set in `.env` if desired (e.g. `lan_operational` for fewer narrative telemetry fields in JSON).

---

## What this is not

- Not a hardened **production** certification: no TLS termination, secrets rotation, or multi-tenant isolation is implied here — see [`PRODUCTION_HARDENING_ROADMAP.md`](../proposals/PRODUCTION_HARDENING_ROADMAP.md).
- Not a substitute for your org’s image scanning, registry policies, and runtime admission controls.

---

*MoSex Macchina Lab — practical compose overlay; align with CHANGELOG when changing defaults.*
