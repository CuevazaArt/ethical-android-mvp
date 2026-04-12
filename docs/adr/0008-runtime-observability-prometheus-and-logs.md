# ADR 0008 — Runtime observability (Prometheus metrics + structured logs)

**Status:** Accepted (April 2026)  
**Context:** Operators need measurable latency, block rates, and DAO-side activity without turning the research kernel into a black box. LAN deployments also need optional log correlation without committing secrets.

## Decision

1. **Opt-in Prometheus** — Expose `GET /metrics` when [`KERNEL_METRICS=1`](../../.env.example); default **off** (same posture as hiding OpenAPI on LAN). Implementation: [`src/observability/metrics.py`](../../src/observability/metrics.py), registration in app lifespan [`src/chat_server.py`](../../src/chat_server.py). Requires [`prometheus-client`](../../requirements.txt) at runtime.
2. **Metric names** — Use the `ethos_kernel_*` prefix; document the full catalog in [`OPERATOR_QUICK_REF.md`](../proposals/OPERATOR_QUICK_REF.md#observability-metrics-and-logs) (histograms and counters with label names).
3. **Structured JSON logs** — Optional stderr JSON lines when [`KERNEL_LOG_JSON=1`](../../.env.example); level from [`KERNEL_LOG_LEVEL`](../../.env.example) (default `INFO`). Formatter in [`src/observability/logging_setup.py`](../../src/observability/logging_setup.py).
4. **Request correlation** — HTTP: propagate [`X-Request-ID`](../../src/observability/middleware.py); WebSocket: generate a new id per inbound message via [`request_id` context](../../src/observability/context.py) so JSON logs can include `request_id` when present.
5. **Kernel decision metrics** — When `KERNEL_METRICS=1`, `ethos_kernel_kernel_decisions_total` and `ethos_kernel_kernel_process_seconds` record each completed `EthicalKernel.process` (bounded label cardinality on the counter).
6. **Decision JSON lines** — When `KERNEL_LOG_JSON=1`, optional `KERNEL_LOG_DECISION_EVENTS` (default on) emits one machine-readable JSON line per `process` via [`decision_log.py`](../../src/observability/decision_log.py).
7. **Health JSON** — `GET /health` includes `version`, `uptime_seconds`, and an `observability` object for probes and dashboards.
8. **No ethics change** — Metrics and logs are telemetry only; they do not alter MalAbs, Bayesian scoring, or `final_action`.

## Consequences

- **Positive:** Scrapable SLO signals; grep-friendly JSON in log aggregators; correlatable sessions without a proprietary APM.
- **Negative:** Extra dependencies and label cardinality discipline (keep `operation` / `path` / `reason` values bounded as implemented).

## Links

- [`OPERATOR_QUICK_REF.md`](../proposals/OPERATOR_QUICK_REF.md#observability-metrics-and-logs) — env flags + metric names  
- [`README.md`](../../README.md) — Docker / observability paragraph  
- [`scripts/loadtest/ws_stress.py`](../../scripts/loadtest/ws_stress.py) — optional WebSocket load smoke
