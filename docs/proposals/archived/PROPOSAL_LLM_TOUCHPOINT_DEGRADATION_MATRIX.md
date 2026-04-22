# LLM touchpoint degradation matrix (operator + contributor reference)

**Purpose:** One place to see **which env var wins** when multiple knobs exist, **what values** are valid per path, and **where** behavior is implemented. Use this when tuning staging vs production or when adding a new LLM call site.

**Code entry:** [`src/modules/llm_touchpoint_policies.py`](../../src/modules/llm_touchpoint_policies.py) (shared helpers), plus [`perception_backend_policy.py`](../../src/modules/perception_backend_policy.py), [`llm_verbal_backend_policy.py`](../../src/modules/llm_verbal_backend_policy.py), and [`llm_layer.py`](../../src/modules/llm_layer.py).

---

## Precedence rules (generic)

For each **touchpoint**, configuration is resolved in this order; **first valid value wins**.

| Order | Mechanism | Example |
|-------|-----------|---------|
| 1 | Per-touchpoint override | `KERNEL_LLM_TP_NARRATE_POLICY=canned_safe` |
| 2 | Family default (verbal JSON only) | `KERNEL_LLM_VERBAL_FAMILY_POLICY` applies to **communicate** and **narrate** when their `KERNEL_LLM_TP_*` key is unset |
| 3 | Legacy single key (backward compatible) | `KERNEL_PERCEPTION_BACKEND_POLICY`, `KERNEL_VERBAL_LLM_BACKEND_POLICY` |
| 4 | Built-in default | See table below |

**Invalid** values for a given touchpoint are **ignored** (treated as unset), so the next precedence level applies.

**Monologue** does not use the verbal family key; it uses `KERNEL_LLM_TP_MONOLOGUE_POLICY`, then `KERNEL_LLM_MONOLOGUE_BACKEND_POLICY`, then default.

---

## Touchpoint table

| Touchpoint | `KERNEL_LLM_TP_*` | Valid policies | Family / legacy fallbacks | Default | Observability |
|------------|--------------------|----------------|----------------------------|---------|----------------|
| Structured perception JSON | `KERNEL_LLM_TP_PERCEPTION_POLICY` | `template_local`, `fast_fail`, `session_banner` | `KERNEL_PERCEPTION_BACKEND_POLICY` | `template_local` | `perception.coercion_report`, `perception_observability`, optional `perception_backend_banner` |
| Communicate (decision → user JSON) | `KERNEL_LLM_TP_COMMUNICATE_POLICY` | `template_local`, `canned_safe` | `KERNEL_LLM_VERBAL_FAMILY_POLICY` → `KERNEL_VERBAL_LLM_BACKEND_POLICY` | `template_local` | `verbal_llm_observability.events[]` |
| Narrate (multipolar morals JSON) | `KERNEL_LLM_TP_NARRATE_POLICY` | `template_local`, `canned_safe` | same verbal chain as communicate | `template_local` | same |
| Monologue embellish (plain text, optional) | `KERNEL_LLM_TP_MONOLOGUE_POLICY` | `passthrough`, `annotate_degraded` | `KERNEL_LLM_MONOLOGUE_BACKEND_POLICY` | `passthrough` | same `events[]` (`touchpoint=monologue`) |

**Feature gate:** monologue LLM calls still require `KERNEL_LLM_MONOLOGUE=1` (existing). Policy only applies when that path runs with a generative backend.

---

## Splitting communicate vs narrate (flexible ops)

Example: **canned** narrate for dashboards, but **rich templates** for the spoken line:

```text
KERNEL_LLM_TP_NARRATE_POLICY=canned_safe
KERNEL_LLM_TP_COMMUNICATE_POLICY=template_local
```

Example: one knob for both verbal JSON paths:

```text
KERNEL_LLM_VERBAL_FAMILY_POLICY=canned_safe
```

Per-touchpoint keys **override** the family for that path only.

---

## Perception override without renaming legacy

```text
KERNEL_LLM_TP_PERCEPTION_POLICY=fast_fail
```

If set and valid, it overrides `KERNEL_PERCEPTION_BACKEND_POLICY` for the same process.

---

## Monologue operator modes

| Policy | On LLM failure or empty enrich |
|--------|--------------------------------|
| `passthrough` | Return the base monologue line only (historical default). |
| `annotate_degraded` | Append `| monologue_llm_degraded` or `| monologue_llm_skipped`; record a degradation event. |

---

## Embedding transport vs chat completion (operator mapping)

**Different surfaces:** MalAbs semantic embeddings use [`semantic_embedding_client.py`](../../src/modules/semantic_embedding_client.py) (HTTP to Ollama `/api/embeddings`, retries, circuit-style counters). Chat **perception** and **communicate/narrate** use [`llm_backends.py`](../../src/modules/llm_backends.py) `completion()` with [`PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`](PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md) policies and chat JSON diagnostics.

| Concern | Embeddings (MalAbs L1) | Completion JSON (perception / verbal) |
|---------|-------------------------|----------------------------------------|
| Failure visibility | `decision_trace` / `malabs.*` strings; Prometheus `ethos_kernel_embedding_errors_total` | `perception.coercion_report`, `verbal_llm_observability` |
| Policy env | `KERNEL_SEMANTIC_*`, hash fallback | `KERNEL_LLM_TP_*`, verbal family, legacy keys (this matrix) |
| Degradation | Hash fallback or lexical-only deferral (see [`MALABS_SEMANTIC_LAYERS.md`](MALABS_SEMANTIC_LAYERS.md)) | `template_local` / `fast_fail` / `canned_safe` paths |

A single unified env knob for **all** HTTP inference remains out of scope until operators ask for it (see [`WEAKNESSES_AND_BOTTLENECKS.md`](../WEAKNESSES_AND_BOTTLENECKS.md) §3).

---

## Related proposals

- [`PROPOSAL_LLM_INTEGRATION_TRACK.md`](PROPOSAL_LLM_INTEGRATION_TRACK.md) — gap register (embeddings vs completion, MalAbs, `process_natural`, generative candidates)
- [`PROPOSAL_PERCEPTION_BACKEND_DEGRADATION_POLICY.md`](PROPOSAL_PERCEPTION_BACKEND_DEGRADATION_POLICY.md)
- [`PROPOSAL_LLM_VERBAL_DEGRADATION_POLICY.md`](PROPOSAL_LLM_VERBAL_DEGRADATION_POLICY.md)
- [`PROPOSAL_PERCEPTION_OBSERVABILITY_CONTRACT.md`](PROPOSAL_PERCEPTION_OBSERVABILITY_CONTRACT.md)
- [`OPERATOR_QUICK_REF.md`](OPERATOR_QUICK_REF.md)

---

## Adding a new touchpoint (contributor checklist)

1. Add a stable slug and `KERNEL_LLM_TP_<SLUG>_POLICY` in `llm_touchpoint_policies.py` (document valid values).
2. Resolve policy at the LLM call site; record structured events on the same list used for chat observability when applicable.
3. Extend this matrix and [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md) if the key is operator-facing.
4. Add tests: precedence, invalid override ignored, and one happy-path default.
