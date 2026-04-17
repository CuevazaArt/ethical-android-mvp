# Observability Dashboard Guide — Prometheus + Grafana

**Purpose:** Instructions for operators to monitor kernel health, performance, and safety events via Prometheus + Grafana stack.

**Audience:** DevOps, platform engineers, and operators responsible for kernel runtime.

**Prerequisites:**
- `KERNEL_METRICS=1` enabled on kernel.
- Prometheus scraping kernel `/metrics` endpoint.
- Grafana connected to Prometheus data source.

---

## Quick Setup (Docker Compose)

### 1. Enable Metrics on Kernel

```bash
export KERNEL_METRICS=1
export KERNEL_LOG_JSON=1
docker-compose -f docker-compose.prodish.yml up -d
```

### 2. Verify Metrics Endpoint

```bash
curl http://localhost:8000/metrics | head -20
# Expected output: Prometheus text format (HELP / TYPE / samples)
```

### 3. Verify Prometheus Scrape

```bash
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.labels.job=="ethos-kernel")'
# Expected: kernel endpoint shows "health": "up"
```

### 4. Import Dashboard

- Open Grafana: `http://localhost:3000` (default login: `admin/admin`).
- Go to **Dashboards** → **+ Import** → paste JSON from [`deploy/grafana/ethos-kernel-overview.json`](../../deploy/grafana/ethos-kernel-overview.json).
- Select Prometheus data source.
- Dashboard appears on home.

---

## Dashboard Panels (Ethos Kernel Overview)

### Row 1: System Health

| Panel | Metric | What to Watch | Alert Threshold |
|-------|--------|---------------|------------------|
| **Uptime** | `ethos_kernel_process_seconds` (histogram) | Kernel has been running without restart | < 5 min = anomaly (check logs) |
| **Chat turns/sec** | `ethos_kernel_chat_turns_total` rate | Traffic volume; trends | > 100/sec = overload risk |
| **Avg turn latency** | `ethos_kernel_chat_turn_duration_seconds_bucket` (histogram quantile) | Response time (p50, p95, p99) | p95 > 5s = performance issue |
| **Memory usage** | `process_resident_memory_bytes` | RAM footprint | > 500 MB = possible leak |

### Row 2: Safety Gates

| Panel | Metric | What to Watch | Alert Threshold |
|-------|--------|---------------|------------------|
| **MalAbs blocks/min** | `ethos_kernel_malabs_blocks_total` rate | Safety gate activity | > 10/min = possible attack or misconfiguration |
| **Block reason distribution** | `ethos_kernel_malabs_blocks_total` by `reason` | Which categories block most | Spike in new reason = investigate |
| **Semantic embedding errors** | `ethos_kernel_embedding_errors_total` | Embedding service reliability | > 5 errors/min = embedding service down |
| **Safety block path** | `ethos_kernel_chat_turns_total` filtered by `path="safety_block"` | Safety path vs. all paths | Sudden spike = possible evasion attempt |

### Row 3: Decision Quality

| Panel | Metric | What to Watch | Alert Threshold |
|-------|--------|---------------|------------------|
| **Decision certainty** | `ethos_kernel_kernel_decisions_total` by `certainty` | High/med/low confidence split | > 20% low = high ambiguity in queries |
| **Blocked decisions** | `ethos_kernel_kernel_decisions_total` by `blocked` | Kernel-side blocks (no safety gate) | > 2% blocked = policy too strict or input poisoned |
| **LLM latency** | `ethos_kernel_llm_completion_seconds_bucket` by `operation` | Perception/communicate/narrate times | > 30s = LLM service degraded |
| **Perception circuit trips** | `ethos_kernel_perception_circuit_trips_total` | Metacognitive doubt activations | 1+ per hour = possible adversarial pressure |

### Row 4: Detailed Outcomes

| Panel | Metric | What to Watch | Alert Threshold |
|-------|--------|---------------|------------------|
| **Semantic gate outcomes** | `ethos_kernel_semantic_malabs_outcomes_total` by `outcome` | Embedding path breakdown | `embed_unavailable_defer` > 5% = embedding lag |
| **DAO operations** | `ethos_kernel_dao_ws_operations_total` by `operation` | Governance queue activity | `submit_draft` > 10/min = proposal spam |
| **Perception backend status** | `ethos_kernel_perception_circuit_trips_total` vs. up-time | Circuit breaker health | Trips without recovery = stress pattern |

---

## Alert Rules (Prometheus)

Starter alert rules live in [`deploy/prometheus/ethos_kernel_alerts.yml`](../../deploy/prometheus/ethos_kernel_alerts.yml). Load as `rule_files` in Prometheus config:

```yaml
# prometheus.yml
rule_files:
  - 'ethos_kernel_alerts.yml'
```

### Key Alerts

| Alert Name | Condition | Impact | Action |
|------------|-----------|--------|--------|
| `KernelMalabsBlockRateHigh` | `rate(ethos_kernel_malabs_blocks_total[5m]) > 0.1` (1/10s) | Possible injection/jailbreak attack OR misconfigured thresholds | Check logs; review recent inputs; tune thresholds if benign |
| `KernelSafetyBlockRateHigh` | `rate(ethos_kernel_chat_turns_total{path="safety_block"}[5m]) > 0.05` | Many turns being blocked; possible adversarial campaign | Alert incident response; collect logs |
| `KernelPerceptionCircuitTrips` | `increase(ethos_kernel_perception_circuit_trips_total[5m]) > 0` | Metacognitive doubt triggered (coercion streak detected) | Review query patterns; check for manipulation attempts |
| `KernelEmbeddingErrorRate` | `rate(ethos_kernel_embedding_errors_total[5m]) / rate(ethos_kernel_semantic_malabs_outcomes_total[5m]) > 0.1` | Embedding service failing or slow | Restart embedding service; check connectivity |
| `KernelLLMLatencyP99High` | `histogram_quantile(0.99, rate(ethos_kernel_llm_completion_seconds_bucket[5m])) > 30` | LLM service is slow | Check LLM service health; consider scaling |

**Tuning:** Alert thresholds depend on your deployment's normal traffic. Start with defaults and adjust based on 1–2 weeks of baseline data.

---

## Custom Queries (PromQL Examples)

### Safety Metrics

```promql
# Block rate in last 1 hour (blocks per minute)
rate(ethos_kernel_malabs_blocks_total[1h]) * 60

# Top 5 block reasons
topk(5, sum(ethos_kernel_malabs_blocks_total) by (reason))

# Safety path vs. total turns (%)
(ethos_kernel_chat_turns_total{path="safety_block"} / on() group_left() ethos_kernel_chat_turns_total) * 100
```

### Performance Metrics

```promql
# 95th percentile turn latency
histogram_quantile(0.95, rate(ethos_kernel_chat_turn_duration_seconds_bucket[5m]))

# Kernel process time (excluding I/O)
histogram_quantile(0.50, rate(ethos_kernel_kernel_process_seconds_bucket[5m]))

# Concurrent turns (estimated from queue depth — if available)
# Note: no native metric; infer from latency increase
```

### Governance Metrics

```promql
# DAO proposal submissions per hour
rate(ethos_kernel_dao_ws_operations_total{operation="submit_draft"}[1h]) * 3600

# Governance escalations (tied to circuit trips)
ethos_kernel_perception_circuit_trips_total
```

### Availability

```promql
# Uptime (if metric resets on restart)
time() - ethos_kernel_process_seconds_bucket{le="+Inf"}

# Health check status (1 = healthy; 0 = unhealthy)
# Inferred from scrape success rate
count(up{job="ethos-kernel"})
```

---

## Dashboard Drill-Down Workflow

### Scenario 1: Sudden MalAbs Block Spike

**Observation:** `KernelMalabsBlockRateHigh` alert fires.

**Drill-down:**

1. **Quick check:** Open "MalAbs blocks/min" panel on Ethos Kernel Overview dashboard.
2. **Time filter:** Isolate the spike (e.g., 14:00–14:05 UTC).
3. **Reason breakdown:** Click "Block reason distribution" → identify which reason (e.g., `VIOLENCE_INSTRUCTIONS` or semantic gate).
4. **Cross-check safety path:** Look at "Safety block path" panel → confirm it's the same spike.
5. **Inspect logs:** 
   ```bash
   docker-compose logs chat_server --since 2026-04-15T14:00:00Z --until 2026-04-15T14:05:00Z | grep -i malabs
   ```
6. **Action:**
   - If reason is legitimate safety block (e.g., user testing) → acknowledge and continue.
   - If unknown reason → escalate to security team; review input corpus.

### Scenario 2: High Turn Latency

**Observation:** `KernelLLMLatencyP99High` alert fires; p99 > 30s.

**Drill-down:**

1. **Check LLM latency:** "LLM latency by operation" panel → identify which operation (perception/communicate/narrate).
2. **Check LLM service health:**
   ```bash
   docker-compose logs ollama | grep error
   curl http://localhost:11434/api/tags  # Ollama health
   ```
3. **Check kernel queue:**
   ```bash
   curl http://localhost:8000/health | jq '.chat_bridge.kernel_chat_turn_timeout_seconds'
   ```
4. **Action:**
   - If LLM service is down/slow → restart or scale.
   - If queue backing up → increase `KERNEL_CHAT_THREADPOOL_WORKERS` (if configured).

### Scenario 3: Perception Circuit Trips

**Observation:** `ethos_kernel_perception_circuit_trips_total` increments (metacognitive doubt activation).

**Drill-down:**

1. **Timestamp:** Note when counter incremented (1-2s precision from last known increase).
2. **User session:** Find corresponding chat turn in logs:
   ```bash
   docker-compose logs chat_server | grep -A 5 "metacognitive_doubt"
   ```
3. **Coercion pattern:** Check `coercion_report` in WebSocket response; identify stress indicators (repeated requests, emotional appeals, etc.).
4. **Action:**
   - If pattern is suspicious (adversarial) → flag session; review query history.
   - If pattern is legitimate (user frustrated) → human operator may intervene to help.

---

## Log Integration (Structured JSON Logs)

When `KERNEL_LOG_JSON=1`, logs appear as newline-delimited JSON. Combine with dashboard for deeper insights:

```bash
# Example log line (one per line in stderr)
{"timestamp":"2026-04-15T21:53:00.123Z","level":"INFO","event":"chat_turn_complete","turn_index":42,"path":"heavy","latency_ms":1234,"malabs_blocks":0}
```

### Aggregating Logs + Metrics

Use **Loki** (Prometheus-compatible logging) to correlate:

1. **Parse JSON logs** into Loki.
2. **Link to metrics** via `turn_index` or `request_id`.
3. **Query example:**
   ```logql
   {job="ethos-kernel"} | json | path="safety_block" | line_format "{{.request_id}}"
   ```

---

## Common Operational Checks

| Check | Command | Expected |
|-------|---------|----------|
| Is kernel scraping metrics? | `curl http://localhost:8000/metrics \| wc -l` | > 50 lines |
| Is Prometheus ingesting? | `curl http://localhost:9090/api/v1/query?query=up{job%3D%22ethos-kernel%22}` | `"value":[1, "1"]` (health = 1) |
| Is Grafana dashboard loading? | Open `http://localhost:3000/d/<uid>` | Panels render; no 500 errors |
| Are alerts firing? | Check Prometheus Alerts tab: `http://localhost:9090/alerts` | Configured rules appear |
| Are logs being written? | `docker-compose logs chat_server \| head -5` | Recent timestamps |

---

## Troubleshooting

| Issue | Diagnostic | Fix |
|-------|-----------|-----|
| **No metrics in Prometheus** | `curl http://localhost:8000/metrics` returns 503 or error | Kernel not built with `prometheus_client` or metrics disabled; check `KERNEL_METRICS=1` |
| **Dashboard panels blank** | Data source test fails in Grafana | Prometheus URL wrong or not accessible; check Network tab in browser |
| **Alerts never fire** | Prometheus Alerts tab empty | Rules not loaded; verify `rule_files` in `prometheus.yml` |
| **High false-positive rate on alerts** | Alert fires on normal traffic | Thresholds too sensitive; adjust `for: 5m` or threshold value in `ethos_kernel_alerts.yml` |
| **Logs not structured JSON** | `docker-compose logs` shows plain text | `KERNEL_LOG_JSON=1` not set; restart kernel with env var |

---

## Best Practices

1. **Baseline your metrics:** Run for 1–2 weeks in staging; document normal ranges (p50, p95 latency, typical block rate, etc.).
2. **Tune alerts incrementally:** Start with high thresholds; gradually lower as you understand normal behavior.
3. **Correlate logs + metrics:** When an alert fires, cross-check logs for context (e.g., which inputs caused the spike).
4. **Archive historical data:** Prometheus default retention is 15 days; consider longer retention for post-mortem analysis.
5. **Use Grafana annotations:** Mark deployments, config changes, or incidents directly on dashboard for context.

---

## See Also

- [Prometheus documentation](https://prometheus.io/docs/)
- [Grafana documentation](https://grafana.com/docs/)
- [`OPERATOR_QUICK_REF.md`](OPERATOR_QUICK_REF.md) — observability section.
- [`deploy/prometheus/ethos_kernel_alerts.yml`](../../deploy/prometheus/ethos_kernel_alerts.yml) — alert rules.
- [`deploy/grafana/README.md`](../../deploy/grafana/README.md) — dashboard setup.
