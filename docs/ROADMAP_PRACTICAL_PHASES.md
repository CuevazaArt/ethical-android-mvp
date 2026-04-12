# Practical engineering roadmap (example phases)

Example sequencing for teams shipping Ethos Kernel–based runtimes. Adjust timelines to your capacity.

**Tight 30-day operator slice:** [`docs/proposals/ROADMAP_MINIMAL_EXECUTABLE_MODEL_30_DAY.md`](proposals/ROADMAP_MINIMAL_EXECUTABLE_MODEL_30_DAY.md) (compose, ethical telemetry, persistence policy, operator manual).

## Phase 0 — Immediate (foundation)

**Goal:** trustworthy baseline for contributors and CI.

- [x] CI workflow (tests on supported Python versions).
- [x] Pre-commit (lint/format/secrets baseline where configured).
- [x] `.env.example` with core vars documented.
- [x] README: clone, venv, `pip install -r requirements.txt`, run tests, run chat server locally.
- [x] Docs: `SECURITY.md`, kernel env policy, governance data/audit/transparency docs.

**Exit criteria:** green CI on `main`; new developer can run chat + tests in &lt; 30 minutes.

## Phase 1 — Next sprint (integration)

**Goal:** reproducible runtime and LLM abstraction.

- [x] LLM adapter layer (`LLMBackend`) + mock for tests.
- [x] Broaden integration tests: FastAPI lifespan, WebSocket happy path + MalAbs block (`tests/test_chat_server.py`: context-manager lifespan, `test_websocket_malabs_safety_block`).
- [x] Docker + Compose assets (iterate as needed).
- [x] Document “production-ish” compose profile (metrics optional, no secrets in image) — [`docs/deploy/COMPOSE_PRODISH.md`](deploy/COMPOSE_PRODISH.md), [`docker-compose.prodish.yml`](../docker-compose.prodish.yml), [`docker-compose.metrics.yml`](../docker-compose.metrics.yml), [`.dockerignore`](../.dockerignore).

**Exit criteria:** one-command local stack; WebSocket smoke in CI (optional job if flaky).

## Phase 2 — 4–8 weeks (observability + safety metrics)

**Goal:** measure behavior, not only pass/fail tests.

- [x] Prometheus metrics scaffold (`KERNEL_METRICS`).
- [x] Grafana starter dashboard (import JSON) — [`deploy/grafana/ethos-kernel-overview.json`](../deploy/grafana/ethos-kernel-overview.json), [`deploy/grafana/README.md`](../deploy/grafana/README.md).
- [x] Red-team / eval JSONL + runner (`scripts/eval/`).
- [ ] Vector DB for semantic anchors (Chroma/FAISS) — see [PROPOSAL_VECTOR_META_RLHF_PIPELINE.md](proposals/PROPOSAL_VECTOR_META_RLHF_PIPELINE.md).

**Exit criteria:** dashboard shows MalAbs blocks, latency, embedding errors; adversarial suite runs in CI weekly or on-demand.

## Phase 3 — 3+ months (evaluation pipelines + controlled ML)

**Goal:** disciplined iteration without eroding hard constraints.

- Automated eval pipelines (threshold sweeps, regression gates).
- RLHF / fine-tune **only** behind feature flags, with full pytest + red-team pass before merge.
- Staging environment with audit chain + log retention policy signed off.
- External audit or third-party review of data policy and transparency docs.

**Exit criteria:** signed-off runbook for promotion staging → prod; audit chain verification script in CI or release checklist.

## Related

- [PRODUCTION_HARDENING_ROADMAP.md](proposals/PRODUCTION_HARDENING_ROADMAP.md)
- [CRITIQUE_ROADMAP_ISSUES.md](proposals/CRITIQUE_ROADMAP_ISSUES.md)
- [PROPOSAL_CORE_IMPLEMENTATION_GAP_PHASED_REMEDIATION.md](proposals/PROPOSAL_CORE_IMPLEMENTATION_GAP_PHASED_REMEDIATION.md) — phased core vs. governance backlog (issues 1–7)
