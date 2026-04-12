# Grafana — Ethos Kernel starter dashboard

**Import:** Grafana → **Dashboards** → **New** → **Import** → upload `ethos-kernel-overview.json`.

**Prerequisites:**

- Prometheus scrapes the app with `KERNEL_METRICS=1` (e.g. `http://<host>:8765/metrics`).
- Prometheus datasource in Grafana points at that Prometheus server.

**Variables:** The JSON uses a `$prometheus` datasource UID placeholder `prometheus`. After import, edit each panel’s datasource if your UID differs, or set the dashboard variable.

**Metrics shown:** kernel decision rate, `process()` latency (p95-style from histogram), chat turn duration, MalAbs blocks, semantic MalAbs outcomes, LLM completion time.

See also [OPERATOR_QUICK_REF.md](../../docs/proposals/OPERATOR_QUICK_REF.md#observability-metrics-and-logs).
