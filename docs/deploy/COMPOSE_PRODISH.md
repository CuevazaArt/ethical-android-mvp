# Compose — production-ish stack

**Goal:** run the Ethos Kernel chat server in Docker with **LAN-safe defaults**, **optional Prometheus metrics**, and **no secrets in the image**.

**Related:** root [`docker-compose.yml`](../../docker-compose.yml), [`docker-compose.prodish.yml`](../../docker-compose.prodish.yml), [`docker-compose.metrics.yml`](../../docker-compose.metrics.yml), [`Dockerfile`](../../Dockerfile), [`.dockerignore`](../../.dockerignore), [`.env.example`](../../.env.example), [`KERNEL_ENV_POLICY.md`](../proposals/KERNEL_ENV_POLICY.md).

---

## Principles

| Topic | Practice |
|--------|----------|
| **Secrets** | Keep API keys, Fernet checkpoint keys, audit HMAC seeds, and nomadic keys in **`.env`** (or your orchestrator’s secret store). **Do not** `COPY` them into a custom image layer; the repo [`.dockerignore`](../../.dockerignore) excludes `.env` and `.env.*` from the build context. |
| **OpenAPI** | **`KERNEL_API_DOCS=0`** in the prodish overlay so `/docs`, `/redoc`, and `/openapi.json` are not exposed by default on LAN binds. |
| **Metrics** | Default **`KERNEL_METRICS=0`** via `${KERNEL_METRICS:-0}` in the prodish file (reads the project **`.env`** for Compose interpolation). Enable **`/metrics`** with `KERNEL_METRICS=1` in `.env`, or merge **`docker-compose.metrics.yml` last** (it sets `KERNEL_METRICS: "1"` and overrides a zero default). |
| **Profiles** | Base compose **`llm`** profile still adds **Ollama** when you need it. When stacking **`-f` files**, put **`docker-compose.metrics.yml` after `docker-compose.prodish.yml`** so metrics stay on; reversing order turns metrics off again. |

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

## Verification checklist (staging / release)

Use this after changing compose files or before promoting an image. **No ethics change** — these checks only confirm telemetry wiring ([ADR 0008](../adr/0008-runtime-observability-prometheus-and-logs.md)).

| Step | Command / probe | Expected |
|------|-------------------|----------|
| 1. Compose merge valid | `docker compose -f docker-compose.yml -f docker-compose.prodish.yml config --quiet` (add `-f docker-compose.metrics.yml` if you use metrics) | Exit 0 (same merges as CI job **`compose-validate`** in [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)). |
| 2. Stack up | `docker compose -f docker-compose.yml -f docker-compose.prodish.yml up --build -d` | Containers healthy; app listens on mapped port (default **8765**). |
| 3. Health | `curl -sS http://localhost:8765/health` | JSON with `version`, `uptime_seconds`, `observability`; optional **`nomad_bridge`** when the Nomad singleton is wired (`nomad_bridge_queue_stats_v2`). See [`PROPOSAL_CHAT_SERVER_HTTP_API_SURFACE.md`](../proposals/PROPOSAL_CHAT_SERVER_HTTP_API_SURFACE.md), [`OPERATOR_QUICK_REF.md`](../proposals/OPERATOR_QUICK_REF.md). |
| 3b. Health ↔ metrics flag | Parse `observability.metrics_enabled` from the same `/health` body | Should be **`false`** when metrics are off (default prodish) and **`true`** after merging [`docker-compose.metrics.yml`](../../docker-compose.metrics.yml) and restart — must agree with step 4a/4b HTTP codes on `/metrics`. |
| 4a. Metrics **off** (default prodish) | `curl -sS -o /dev/null -w "%{http_code}" http://localhost:8765/metrics` | **404** with JSON `metrics_disabled` when `KERNEL_METRICS` is not enabled — intentional ([`chat_server.py`](../../src/chat_server.py) `/metrics`). |
| 4b. Metrics **on** | Merge [`docker-compose.metrics.yml`](../../docker-compose.metrics.yml) **after** prodish, restart; then `curl -sS http://localhost:8765/metrics \| head` | **200**; text exposition with `ethos_kernel_` metric names (requires `prometheus-client` in the image — see [`requirements.txt`](../../requirements.txt)). |
| 5. Logs (optional) | Set `KERNEL_LOG_JSON=1` in `.env`, restart | Structured JSON on stderr; correlation via `X-Request-ID` on HTTP ([ADR 0008](../adr/0008-runtime-observability-prometheus-and-logs.md) §4). |

**Alerts / dashboards:** starter rules [`deploy/prometheus/ethos_kernel_alerts.yml`](../../deploy/prometheus/ethos_kernel_alerts.yml); Grafana import [`deploy/grafana/README.md`](../../deploy/grafana/README.md).

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

**CI:** `.github/workflows/ci.yml` job **`compose-validate`** runs `docker compose … config --quiet` for the same merge combinations; locally, [`tests/test_compose_config.py`](../../tests/test_compose_config.py) mirrors that when Docker is installed (skipped if `docker` is not on `PATH`).

---

*MoSex Macchina Lab — practical compose overlay; align with CHANGELOG when changing defaults.*
