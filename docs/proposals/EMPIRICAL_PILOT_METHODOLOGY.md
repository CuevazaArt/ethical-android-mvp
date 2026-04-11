# Empirical pilot — human agreement (Issue 3)

**Purpose:** Provide a **reproducible** way to compare the Ethos Kernel’s **batch** decisions against **simple baselines** and optional **human reference labels**, for **research agreement metrics**. This is **not** product certification, legal safety approval, or a claim of external moral truth.

**Related:** [CRITIQUE_ROADMAP_ISSUES.md](CRITIQUE_ROADMAP_ISSUES.md) (Issue 3), canonical simulations in [`src/simulations/runner.py`](../src/simulations/runner.py), invariant suite in [`tests/test_ethical_properties.py`](../tests/test_ethical_properties.py).

---

## What is (and is not) being measured

| In scope | Out of scope |
|----------|----------------|
| Agreement rate: kernel vs baseline policies on the **same** action set | Whether the kernel matches “correct ethics” in the world |
| Repeatable tables from a **fixed** scenario list + seeds | Chat / WebSocket / LLM perception paths (use separate studies) |
| Transparent baselines (first action, max estimated impact) | Statistical power; IRB; recruitment — left to your study design |

Invariant tests show **internal consistency** of the core; this pilot is a **template** for external comparison workflows.

---

## Artifacts

| Path | Role |
|------|------|
| [`tests/fixtures/empirical_pilot/scenarios.json`](../tests/fixtures/empirical_pilot/scenarios.json) | Which simulation IDs run; optional `reference_action` + short rationale for annotator alignment |
| [`scripts/run_empirical_pilot.py`](../scripts/run_empirical_pilot.py) | Runs kernel (`variability=False`, fixed seed) + baselines; prints agreement summary |

---

## How to run

From the repository root (with `requirements.txt` installed):

```bash
python scripts/run_empirical_pilot.py
```

Optional:

```bash
python scripts/run_empirical_pilot.py --fixture tests/fixtures/empirical_pilot/scenarios.json
python scripts/run_empirical_pilot.py --json
```

---

## Baselines (deliberately simple)

1. **first** — Always choose the **first** candidate action in the scenario list (order bias stress test).
2. **max_impact** — Choose the action with highest `estimated_impact` among candidates (greedy on stated priors).

The **kernel** uses the full pipeline (MalAbs, buffer, mixture, poles, will, …) as in `EthicalKernel.process`.

---

## Metrics

For each policy (kernel, first, max_impact), the script reports whether the chosen action name equals `reference_action` in the fixture (when present). **Agreement** = fraction of scenarios matching. Disagreement is expected and informative; it is not automatically “failure.”

---

## Extending the pilot

- Add scenarios by editing the fixture (only `id` values **1–9** exist today in `ALL_SIMULATIONS`).
- For human labels, replace or supplement `reference_action` with columns from your annotation export and merge in your own analysis script.
- Keep **LLM off** the critical path for this batch script (`llm_mode="local"`) so runs do not depend on Ollama/API.

---

*MoSex Macchina Lab — research methodology draft; align substantive claims with CHANGELOG / HISTORY when publishing results.*
