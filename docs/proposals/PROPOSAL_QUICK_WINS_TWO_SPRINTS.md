# Quick wins — next two sprints (infrastructure hardening)

**Status:** **landed** (April 2026) — strict-by-default env validation, lab profiles on `warn`, perception circuit + metacognitive doubt, `ethos-runtime` script, starter Prometheus alert rules.  
**Audience:** maintainers prioritizing resilience and operability over new “theater” modules (affective/weakness UX layers that do not change `final_action` without explicit design).

## Strategic conclusion

The codebase has reached **solid technical maturity** on the core decision chain (MalAbs → perception bounds → mixture scorer → action). The next frontier is **not** adding more decorative emotional modules, but **hardening infrastructure** so the kernel is **autonomous and resilient** under hardware faults, bad LLM payloads, and adversarial input (injection / jailbreak pressure). This document turns that direction into **scoped, testable** increments.

---

## 1. Strict env validation by default (non-lab profiles)

**Delivered:** Unset `KERNEL_ENV_VALIDATION` now resolves to **`strict`** in [`kernel_public_env.py`](../../src/validators/kernel_public_env.py). **Lab** bundles (`perception_hardening_lab`, `perception_adv_consensus_lab`, `phase2_event_bus_lab`, `untrusted_chat_input`) inject **`KERNEL_ENV_VALIDATION=warn`**. **Pytest** sets `KERNEL_ENV_VALIDATION=warn` via [`tests/conftest.py`](../../tests/conftest.py) before imports so `chat_server` load does not require a perfect host shell.

**Acceptance:** `validate_kernel_env()` raises on violation when strict; `collect_env_violations()` unchanged; docs in [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md).

**Pointers:** [`src/validators/env_policy.py`](../../src/validators/env_policy.py), [`src/validators/kernel_public_env.py`](../../src/validators/kernel_public_env.py), Issue **#7** in [`CRITIQUE_ROADMAP_ISSUES.md`](CRITIQUE_ROADMAP_ISSUES.md).

---

## 2. Perception “circuit breaker” → metacognitive doubt + maximum-caution tone

**Delivered:** [`perception_circuit.py`](../../src/modules/perception_circuit.py) — streak on stressed `coercion_report` turns; after **more than two** consecutive stressed turns, **`HubAudit:metacognitive_doubt`**, counter **`ethos_kernel_perception_circuit_trips_total`**, WebSocket **`metacognitive_doubt`**, `communicate` mode forced to **`gray_zone`**, and an English caution hint. Disable with **`KERNEL_PERCEPTION_CIRCUIT=0`** (default on). Does not bypass MalAbs or alter `final_action`.

**Acceptance:** [`tests/test_perception_circuit.py`](../../tests/test_perception_circuit.py); JSON field documented via `chat_server` payload.

---

## 3. Official console entry points (`pyproject.toml`)

**Intent:** Make the installable package **executable like a standard Python app**, not only `python -m src.chat_server`.

**Delivered:** [`pyproject.toml`](../../pyproject.toml) **`ethos-runtime = "src.chat_server:main"`** (requires **`[runtime]`** extra for FastAPI/uvicorn). Bind host/port still from env / `chat_settings`.

**Acceptance:** `pip install -e ".[runtime]"` then run `ethos-runtime`.

---

## 4. Prometheus / Grafana — MalAbs spike alerts

**Intent:** When **`ethos_kernel_malabs_blocks_total`** (label `reason`, e.g. chat path classifications) **increases faster than X per minute**, fire an operator alert — possible **injection / jailbreak / abuse** surge (not a definitive verdict; tune thresholds per deployment).

**Delivered:** [`deploy/prometheus/ethos_kernel_alerts.yml`](../../deploy/prometheus/ethos_kernel_alerts.yml) — aggregated MalAbs rate, `safety_block` rate, perception circuit trips. [`deploy/grafana/README.md`](../../deploy/grafana/README.md) links the file for Prometheus `rule_files`.

**Acceptance:** Tune thresholds per deployment; false positives possible on legitimate safety stops.

**Pointers:** [`src/observability/metrics.py`](../../src/observability/metrics.py) (`record_malabs_block`).

---

## Tracking

| Item | Status |
|------|--------|
| Strict validation defaults | Done (lab + pytest exceptions documented) |
| Perception circuit breaker | Done |
| `ethos-runtime` entry point | Done |
| MalAbs rate alerts | Starter rules in `deploy/prometheus/` |

Cross-link from [`PLAN_IMMEDIATE_TWO_WEEKS.md`](PLAN_IMMEDIATE_TWO_WEEKS.md).

## See also

- [PLAN_IMMEDIATE_TWO_WEEKS.md](PLAN_IMMEDIATE_TWO_WEEKS.md)  
- [PROPOSAL_CORE_IMPLEMENTATION_GAP_PHASED_REMEDIATION.md](PROPOSAL_CORE_IMPLEMENTATION_GAP_PHASED_REMEDIATION.md)  
- [ADR 0002 — async orchestration](../adr/0002-async-orchestration-future.md)  
- [ADR 0008 — observability](../adr/0008-runtime-observability-prometheus-and-logs.md)  
- [WEAKNESSES_AND_BOTTLENECKS.md](../WEAKNESSES_AND_BOTTLENECKS.md)
