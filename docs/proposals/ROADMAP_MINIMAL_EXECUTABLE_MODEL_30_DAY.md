# Roadmap — minimal executable model (30-day action plan)

**Purpose:** A **sequenced** checklist if the goal is a **smallest viable, operator-runnable** Ethos Kernel deployment in about **30 calendar days**. This is **not** a promise of scope completion; it orders work for **reproducibility**, **observability**, **safe upgrades**, and **non-expert onboarding**.

**Audience:** maintainers and integrators shipping a **single-node** lab or pilot (not certified production).

**Related:** [`ROADMAP_PRACTICAL_PHASES.md`](ROADMAP_PRACTICAL_PHASES.md) (longer horizon), [`WEAKNESSES_AND_BOTTLENECKS.md`](../WEAKNESSES_AND_BOTTLENECKS.md), [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md), [`src/runtime_profiles.py`](../../src/runtime_profiles.py).

---

## Baseline in this repository (April 2026)

| Area | What already exists |
|------|---------------------|
| **Containers** | [`Dockerfile`](../../Dockerfile), [`docker-compose.yml`](../../docker-compose.yml) — `app` + optional **`ollama`** profile (`--profile llm`). No dedicated **DB service** in compose today; SQLite is file-backed when configured. |
| **Health** | `GET /health` — process liveness. `GET /metrics` when `KERNEL_METRICS=1` — Prometheus counters/histograms including `ethos_kernel_chat_turns_total{path=...}` and `ethos_kernel_malabs_blocks_total` ([`src/observability/metrics.py`](../../src/observability/metrics.py)). |
| **Persistence** | JSON + SQLite adapters store **`KernelSnapshotV1`** as a **single JSON blob** in one row ([`src/persistence/sqlite_store.py`](../../src/persistence/sqlite_store.py)); **no** Alembic migration graph for narrative tables. |
| **Profiles** | Named bundles in `RUNTIME_PROFILES` (e.g. `situated_v8_lan_demo`, `lan_operational`). Operators today duplicate keys into compose or `.env`; **Hito 4** recommends a single **`ETHOS_RUNTIME_PROFILE`** applied at process start. |

---

## Hito 1 — Containerization (days 1–7)

**Goal:** One command brings up a **documented**, **version-pinned** stack: kernel + inference + durable volumes.

### Deliverables

1. **Compose hardening**  
   - Pin image digests or minor tags where feasible.  
   - Document **`llm` profile** (Ollama) and env wiring (`OLLAMA_BASE_URL`, `LLM_MODE`).  
   - Optional **named volume** for `KERNEL_CHECKPOINT_PATH` / SQLite file so restarts keep state.

2. **Optional DB service (if you split persistence)**  
   - If narrative or audit moves to a real DB later, add a `db` service and connection string — **out of scope** for blob SQLite MVP, but **scaffold** volume + healthcheck pattern now if pilots need Postgres.

3. **CI smoke**  
   - `docker compose build` (and optional `up` + `GET /health`) in CI or a scheduled workflow.

### Acceptance criteria

- [ ] Fresh clone → `docker compose up --build` → `/health` = `ok`.  
- [ ] With `--profile llm`, Ollama reachable from `app` at documented URL.  
- [ ] README or operator doc section points to compose as **canonical** local stack.

---

## Hito 2 — Health bridge / “ethical health” telemetry (days 8–14)

**Goal:** Operators see **more than ping**: ratios and counters that reflect **safety blocks vs successful dialogue** (and optionally latency).

### Current hooks

- `ethos_kernel_chat_turns_total{path="light"|"heavy"|"safety_block"|"kernel_block"|...}`  
- `ethos_kernel_malabs_blocks_total{reason=...}`  

From these, Grafana/Prometheus can compute **block rate** = blocks / (all turns) over a window.

### Deliverables

1. **`GET /health/ready` or extended `/health`** (optional)  
   - **Readiness:** Ollama reachable when `LLM_MODE=ollama` (cheap TCP or HTTP check; **do not** block on first model pull).  
   - **Degraded:** semantic gate on but embedding errors spiking — surface from existing embedding error counter or a small in-process window.

2. **Documented “ethical health” panel**  
   - Definition: e.g. `sum(rate(ethos_kernel_chat_turns_total{path=~"safety_block|kernel_block"}[5m])) / sum(rate(ethos_kernel_chat_turns_total[5m]))` — **label honestly** as “chat block fraction”, not moral truth.

3. **Optional JSON summary**  
   - e.g. `GET /health/ethics` behind `KERNEL_API_DOCS` or a dedicated flag returning **only aggregates** (no PII) for load balancers that cannot scrape Prometheus.

### Acceptance criteria

- [ ] Runbook lists **which metrics** prove “too many blocks” vs “service down”.  
- [ ] No new endpoint exposes user text.  
- [ ] Dashboard JSON or Grafana starter committed under `docs/` or `deploy/` (your choice).

---

## Hito 3 — Robust persistence / migrations (days 15–21)

**Goal:** Upgrading the kernel **does not brick** stored narrative or checkpoints.

### Reality check

Today’s SQLite path is **one-row JSON blob** versioned by **`KernelSnapshotV1`** schema and validation ([`snapshot_validate.py`](../../src/persistence/snapshot_validate.py)). “Migration” often means **serde + apply_snapshot** compatibility, not SQL DDL migrations.

### Deliverables

1. **Version policy**  
   - Document **forward-compatible** snapshot fields and `CHANGELOG` rules when breaking serde.  
   - Automated test: load **golden fixtures** from previous schema revision (if you bump `schema_version`).

2. **If/when relational narrative tables appear**  
   - Introduce **Alembic** (or equivalent) with migrations checked into `alembic/versions/`.  
   - Startup hook: `alembic upgrade head` in entrypoint or documented operator step.

3. **Backup story**  
   - Document **file-level backup** for SQLite + Fernet checkpoints; optional pre-upgrade copy in script.

### Acceptance criteria

- [ ] Upgrade procedure is **one page** in operator docs.  
- [ ] CI runs migration or snapshot round-trip tests.  
- [ ] No silent data loss on unknown fields — validate and reject with a clear error.

---

## Hito 4 — Operator manual + single env “profile” (days 22–30)

**Goal:** A **non-developer** can start the service with **minimal** configuration, using **named profiles** as the mental model.

### Deliverables

1. **Single entrypoint variable**  
   - **`ETHOS_RUNTIME_PROFILE`** is applied when importing [`chat_server`](../../src/chat_server.py) / [`python -m src.runtime`](../../src/runtime/__main__.py): merges [`RUNTIME_PROFILES`](../../src/runtime_profiles.py) into `os.environ` (unset/empty keys only). `/health` and `/` echo the active profile name when set.

2. **Operator manual (English)**  
   - One PDF or `docs/OPERATOR_MANUAL_MINIMAL.md`: prerequisites, compose up, profile list, “what each profile turns on”, link to [`OPERATOR_QUICK_REF.md`](OPERATOR_QUICK_REF.md), security warnings ([`SECURITY.md`](../../SECURITY.md)), and **where metrics live**.

3. **“Happy path” script**  
   - Optional: `scripts/run_profile.sh` / `run_profile.ps1` setting `ETHOS_RUNTIME_PROFILE` + `docker compose up`.

### Acceptance criteria

- [x] Single profile var at startup (`ETHOS_RUNTIME_PROFILE`).  
- [ ] New user path: install Docker → copy `.env.example` → set **one profile var** → up (documented end-to-end).  
- [ ] Table of profiles mirrors `PROFILE_DESCRIPTIONS` with **risk notes** (LAN bind, semantic gate, etc.).  
- [ ] Support contact / issue link for false blocks ([`TRANSPARENCY_AND_LIMITS.md`](../TRANSPARENCY_AND_LIMITS.md)).

---

## Suggested calendar (summary)

| Week | Hito | Theme |
|------|------|--------|
| 1 | 1 | Compose + volumes + CI image build |
| 2 | 2 | Ethical / block-rate telemetry + readiness |
| 3 | 3 | Snapshot & migration policy (+ Alembic if SQL tables) |
| 4 | 4 | Operator manual + single-var profile activation |

---

## Out of scope for this 30-day slice

- On-chain governance, multi-tenant isolation, formal verification.  
- Full RLHF / vector DB production paths — see [`ROADMAP_PRACTICAL_PHASES.md`](ROADMAP_PRACTICAL_PHASES.md).  
- Replacing heuristic MalAbs with a certified content policy.

---

*MoSex Macchina Lab — minimal executable model roadmap.*
