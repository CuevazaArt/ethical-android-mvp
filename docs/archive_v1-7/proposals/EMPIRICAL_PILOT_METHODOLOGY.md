# Empirical pilot — human agreement (Issue 3)

**Purpose:** Provide a **reproducible** way to compare the Ethos Kernel’s **batch** decisions against **simple baselines** and optional **human reference labels**, for **research agreement metrics**. This is **not** product certification, legal safety approval, or a claim of external moral truth.

**Related:** [CRITIQUE_ROADMAP_ISSUES.md](CRITIQUE_ROADMAP_ISSUES.md) (Issue 3), [EMPIRICAL_METHODOLOGY.md](EMPIRICAL_METHODOLOGY.md) (interpretation, disclaimer, comparison posture), **[ETHICAL_BENCHMARK_EXTERNAL_VALIDATION.md](ETHICAL_BENCHMARK_EXTERNAL_VALIDATION.md)** (why reference labels are not “moral ground truth” without an expert protocol), canonical simulations in [`src/simulations/runner.py`](../../src/simulations/runner.py), invariant suite in [`tests/test_ethical_properties.py`](../../tests/test_ethical_properties.py), pole-weight evidence scope in [POLE_WEIGHT_CALIBRATION_AND_EVIDENCE.md](POLE_WEIGHT_CALIBRATION_AND_EVIDENCE.md).

---

## What is (and is not) being measured

| In scope | Out of scope |
|----------|----------------|
| Agreement rate: kernel vs baseline policies on the **same** action set | Whether the kernel matches “correct ethics” in the world |
| Repeatable tables from a **fixed** scenario list + seeds | Chat / WebSocket / LLM perception paths (use separate studies) |
| Transparent baselines (first action, max estimated impact) | Statistical power; IRB; recruitment — left to your study design |

Invariant tests show **internal consistency** of the core; this pilot is a **template** for external comparison workflows.

---

## Tiered sandbox (experimental monitoring)

Batch fixtures may tag each row with **`difficulty_tier`** (`common` \| `difficult` \| `extreme`). The pilot runner reports **`summary.by_tier`** (agreement counts per tier). This supports staged evaluation (common → difficult → extreme) without changing the batch harness. For **Monte Carlo stress** (artificial signal noise + per-roll kernel seeds), see [PROPOSAL_EXPERIMENTAL_SANDBOX_SCENARIOS.md](PROPOSAL_EXPERIMENTAL_SANDBOX_SCENARIOS.md) §4b and `scripts/run_stochastic_sandbox.py` — distinct from the deterministic pilot.

---

## Artifacts

| Path | Role |
|------|------|
| [`tests/fixtures/empirical_pilot/scenarios.json`](../../tests/fixtures/empirical_pilot/scenarios.json) | Which simulation IDs run; optional `reference_action` + short rationale for annotator alignment; optional `difficulty_tier` |
| [`tests/fixtures/labeled_scenarios.json`](../../tests/fixtures/labeled_scenarios.json) | Expanded Issue 3 dataset: `harness: batch` (executable 1–9) + `annotation_only` vignettes; `expected_decision`; top-level **disclaimer** |
| [`scripts/run_empirical_pilot.py`](../../scripts/run_empirical_pilot.py) | Runs kernel (`variability=False`, fixed seed) + baselines; prints agreement summary (batch harness rows only) |

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
python scripts/run_empirical_pilot.py --output artifacts/pilot_run.json
```

The default fixture lists **all nine** canonical batch simulations (`id` **1–9** in `ALL_SIMULATIONS`). Use `--output` to archive **rows + summary + run metadata** (fixture path, fixed kernel settings) next to human annotation exports.

---

## Baselines (deliberately simple)

1. **first** — Always choose the **first** candidate action in the scenario list (order bias stress test).
2. **max_impact** — Choose the action with highest `estimated_impact` among candidates (greedy on stated priors).

The **kernel** uses the full pipeline (MalAbs, buffer, mixture, poles, will, …) as in `EthicalKernel.process`.

---

## Metrics

For each policy (kernel, first, max_impact), the script reports whether the chosen action name equals `reference_action` in the fixture (when present). **Agreement** = fraction of scenarios matching. Disagreement is expected and informative; it is not automatically “failure.”

Additionally, **kernel vs baseline** rates (always defined): fraction of scenarios where the kernel’s action equals **first** (list-order baseline) or **max_impact** (greedy baseline). These summarize how much the full pipeline diverges from the simple policies on the same scenario set.

---

## Pole weights and sample size

The default fixture lists **nine** batch simulations (`id` **1–9**). That is appropriate to **run** the pilot, compare policies on a **fixed** list, and attach optional human reference actions. It is **not** sufficient to **estimate or statistically validate** the many parameters in linear pole JSON, `EthicalPoles.BASE_WEIGHTS`, or `CONTEXTS` multipliers: see [POLE_WEIGHT_CALIBRATION_AND_EVIDENCE.md](POLE_WEIGHT_CALIBRATION_AND_EVIDENCE.md).

---

## Extending the pilot

- Edit the fixture: only `id` values **1–9** are valid in `ALL_SIMULATIONS` today.
- For human labels, replace or supplement `reference_action` with columns from your annotation export and merge in your own analysis script.
- Keep **LLM off** the critical path for this batch script (`llm_mode="local"`) so runs do not depend on Ollama/API.

---

*MoSex Macchina Lab — research methodology draft; align substantive claims with CHANGELOG / HISTORY when publishing results.*
