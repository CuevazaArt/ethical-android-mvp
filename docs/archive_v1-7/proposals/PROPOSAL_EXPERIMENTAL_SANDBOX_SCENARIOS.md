# Proposal: experimental sandbox — tiered scenarios and monitoring

**Purpose:** Define a **repeatable** experimental path: **common → difficult → extreme** batch scenarios, with **monitoring hooks** on top of the existing empirical pilot — without claiming product certification or external moral ground truth.

**Related:** [EMPIRICAL_PILOT_METHODOLOGY.md](EMPIRICAL_PILOT_METHODOLOGY.md), [EMPIRICAL_PILOT_PROTOCOL.md](EMPIRICAL_PILOT_PROTOCOL.md), [MODULE_IMPACT_AND_EMPIRICAL_GAP.md](MODULE_IMPACT_AND_EMPIRICAL_GAP.md), [PROPOSAL_ADDRESSING_CORE_WEAKNESSES.md](PROPOSAL_ADDRESSING_CORE_WEAKNESSES.md).

---

## 1. Scope and limits

| In scope | Out of scope (use separate studies) |
|----------|-------------------------------------|
| Tier tags on **batch** simulations (IDs **1–9**), agreement **by tier** in `run_empirical_pilot.py` | Chat / WebSocket “live user” stress (different harness) |
| Fixed seeds, `llm_mode=local` for reproducible batch runs | LLM perception JSON paths in this script |
| Archiving `--output` JSON for dashboards or notebooks | IRB, recruitment, legal review of vignettes |
| Stochastic Monte Carlo (`run_stochastic_sandbox.py`) — artificial signal noise + kernel variability | Real-world sensor streams; claims about physical environments |

**Limitations** (same as Issue 3): nine canonical scenarios are a **small** set; **reference labels** are priors for agreement metrics, not independent expert ethics unless you upgrade `reference_standard.tier` and protocol per [ETHICAL_BENCHMARK_EXTERNAL_VALIDATION.md](ETHICAL_BENCHMARK_EXTERNAL_VALIDATION.md).

---

## 2. Tier definitions (experimental)

Tiers are **operational** for monitoring and regression — not a claim that sim “7” is objectively harder than “3” in all moral theories.

| Tier | Intent | Canonical batch IDs (current mapping) |
|------|--------|--------------------------------------|
| **common** | Everyday stakes, legible tradeoffs | **1** (litter), **8** (full-day cycle) |
| **difficult** | Social tension, legal/role ambiguity, mission conflict | **2** (hostile teens), **3** (medical emergency), **4** (minor crime witness), **7** (traffic vs mission) |
| **extreme** | High harm, coercion, violence, integrity under threat | **5** (violent crime), **6** (integrity threat), **9** (intentional damage) |

Maintainers may **adjust** the mapping in fixtures with a CHANGELOG note when scenario semantics change; the **runner** only aggregates whatever `difficulty_tier` is present in the fixture.

---

## 3. Artifacts

| Path | Role |
|------|------|
| [`tests/fixtures/empirical_pilot/scenarios.json`](../../tests/fixtures/empirical_pilot/scenarios.json) | Optional per-row **`difficulty_tier`** (`common` \| `difficult` \| `extreme`) |
| [`tests/fixtures/labeled_scenarios.json`](../../tests/fixtures/labeled_scenarios.json) | Same field on **`harness: batch`** rows |
| [`scripts/run_empirical_pilot.py`](../../scripts/run_empirical_pilot.py) | Each row includes `difficulty_tier`; **`summary.by_tier`** reports agreement counts per tier when references exist |
| [`src/sandbox/synthetic_stochastic.py`](../../src/sandbox/synthetic_stochastic.py) | **Artificial** stochastic engine: Gaussian stress on ethics signals + rare aleatory spikes (reproducible RNG) |
| [`scripts/run_stochastic_sandbox.py`](../../scripts/run_stochastic_sandbox.py) | Monte Carlo over batch scenarios: **`--rolls`**, **`--stress`**, per-trial kernel seed, optional `--no-kernel-variability` / `--no-signal-perturbation` |

---

## 4. Monitoring workflow

1. **Baseline** (after any kernel change affecting scoring):  
   `python scripts/run_empirical_pilot.py --fixture tests/fixtures/empirical_pilot/scenarios.json --output artifacts/sandbox_baseline.json`
2. **Compare** agreement rates overall and **`by_tier`** — regression if a tier drops unexpectedly while others unchanged (investigate poles, MalAbs, or mixture).
3. **Optional:** plot `by_tier` from archived JSON in CI or a notebook (not required in-repo).

---

## 4b. Stochastic stress — chance and non-linear response (research)

The deterministic pilot holds `signals` fixed and turns **kernel variability off** for regression. To study **alea**, **sensory ambiguity**, and **non-linear** sensitivity (different `final_action` or `decision_mode` distributions under noise), use the **synthetic** engine — it is **not** real-world telemetry:

- **`perturb_scenario_signals`** adds stress-scaled Gaussian noise to the six canonical scalar signals (`risk`, `urgency`, …) and may apply a rare spike on hostility/urgency/risk.
- Each Monte Carlo **roll** uses a fresh **`EthicalKernel`** with seed `trial_seed(base_seed, scenario_id, roll)` so `VariabilityEngine` (when enabled) does not share RNG state across trials.
- **`run_stochastic_sandbox.py`** writes **`trials`** (one row per roll: `kernel`, `decision_mode`, optional `perturbation` trace) and **`summary.by_scenario`** with `action_histogram`, `mode_histogram`, `agreement_rate`, and a coarse **`action_entropy_proxy`** (unique actions / rolls).

Example:

```bash
python scripts/run_stochastic_sandbox.py --rolls 40 --stress 0.45 --base-seed 42 --output artifacts/stochastic_sandbox.json
```

Interpretation: agreement vs maintainer reference labels **drops** under noise — that is expected and is material for discussion, not a CI failure. For strict regression, keep using **`run_empirical_pilot.py`** only.

For **hyperparameter / pole / mixture** sweeps (centered static weights, axes–grid–random, JSON + CSV), see [PROPOSAL_WEIGHT_SENSITIVITY_SWEEP.md](PROPOSAL_WEIGHT_SENSITIVITY_SWEEP.md) and `scripts/run_weight_sweep_batch.py`.

**Chat / real users:** for pilot operators, follow [EMPIRICAL_PILOT_PROTOCOL.md](EMPIRICAL_PILOT_PROTOCOL.md) and keep batch sandbox separate from live WebSocket experiments until explicit harness exists.

---

## 5. Future extensions

- Add **chat-only** tiered prompts (new fixture + driver) — separate from batch IDs 1–9.
- **Annotation_only** vignettes: optional `difficulty_tier` for human labeling spreadsheets (not executed by batch runner).
- **Ablation:** run the same tiered fixture with profile flags off (`PROPOSAL_ADDRESSING_CORE_WEAKNESSES.md` Track E2).
- **Stochastic:** sweep `--stress` × `--rolls` grids and archive plots outside the repo; optional CI smoke on `run_stochastic_sandbox` with `rolls=1` only (already covered by unit tests).

---

*MoSex Macchina Lab — sandbox tiers for experimental monitoring, not deployment approval.*
