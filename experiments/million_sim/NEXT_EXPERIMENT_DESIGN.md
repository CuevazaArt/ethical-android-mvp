# Next experiment design — tight scenarios and protocol v5

**Goal:** Produce real variation in mixture-level winners under weight sweeps, map decision boundaries on the util/deon/virtue simplex, and inform default weights (not only agreement vs a fixed reference).

**Prerequisites:** [`EXPERIMENT_HISTORY.md`](EXPERIMENT_HISTORY.md). Corner audits are produced by [`scripts/audit_mixture_simplex_corners.py`](../../scripts/audit_mixture_simplex_corners.py) (output path is operator-chosen, e.g. `experiments/million_sim/out/simplex_corners_audit.json`).

**Source of truth:** Per-candidate `(util, deon, virtue)` triples for scenarios **17–19** live in **`src/simulations/runner.py`** as `CandidateAction.hypothesis_override`. This document mirrors those values.

---

## Part 1 — Tight scenarios (IDs 17, 18, 19)

### Lesson from scenario 16 (baseline two-way flip)

Scenario **16** flips because the three hypothesis valuations **disagree** on the winner at pure corners. The decision boundary is a line in the simplex where util weight compensates deon+virtue preference.

Scenarios **10–12** do **not** cross at corners when all three valuations agree on the same winner — no amount of Monte Carlo on the mixture can reorder a convex combination of identical orderings.

### Design principles for crossing scenarios

1. At least **2 of 3** corners should pick different winners (ideally **3** for three candidates).
2. Discordant-corner gaps should be **small enough** that boundaries are not microscopic slivers (tune per scenario).
3. For **three-candidate** races, use **≥3** candidates.

---

### Scenario 17 — Resource scarcity (efficiency vs equity vs merit)

**Narrative:** A community allocates 100 doses of a scarce resource. Three strategies compete.

**`hypothesis_override` triples `(util, deon, virtue)`** (see `sim_17_frontier_resource_scarcity_triple`):

| Candidate | util | deon | virtue |
|-----------|------|------|--------|
| `distribute_by_need` | 0.275 | 0.260 | 0.305 |
| `distribute_by_lottery` | 0.265 | 0.295 | 0.270 |
| `distribute_by_impact` | 0.305 | 0.258 | 0.275 |

**Pure corners (mixture-only):** util → `distribute_by_impact`; deon → `distribute_by_lottery`; virtue → `distribute_by_need`.

**Difficulty:** `frontier_synthetic`. **No `reference_action`** in the empirical pilot fixture — mapping only.

---

### Scenario 18 — Conflicting promise (loyalty vs transparency)

**Triple:**

| Candidate | util | deon | virtue |
|-----------|------|------|--------|
| `disclose_fully` | 0.315 | 0.240 | 0.285 |
| `defer_to_release` | 0.260 | 0.305 | 0.250 |
| `partial_acknowledge` | 0.285 | 0.270 | 0.300 |

**Pure corners:** util → `disclose_fully`; deon → `defer_to_release`; virtue → `partial_acknowledge`.

**Difficulty:** `frontier_synthetic`.

---

### Scenario 19 — Asymmetric confrontation (two candidates)

**Triple:**

| Candidate | util | deon | virtue |
|-----------|------|------|--------|
| `protect_intervene` | 0.295 | 0.245 | 0.275 |
| `retreat_deescalate` | 0.270 | 0.275 | 0.280 |

**Pure corners:** util → `protect_intervene`; deon and virtue → `retreat_deescalate` (virtue margin 0.005 vs protect).

**Difficulty:** `calibration_synthetic`.

---

### Coverage snapshot (mixture-only grid, **denominator = 100**)

Empirical region fractions and flip rates depend on the discrete grid; recompute after changing triples. Run:

`python scripts/run_simplex_decision_map.py --denominator 100 --scenario-ids 16,17,18,19 --bisect-edges --output-json experiments/million_sim/out/simplex_map_d100_latest.json`

---

## Part 2 — Protocol v5 (“sensitivity mapping”) — planned

- **Adaptive sampling:** screening barycentric grid → refinement band around detected edges → optional full-kernel JSONL on boundary-heavy points.
- **Rich JSONL rows:** full ranking, `score_gap_12` / `score_gap_13`, `ranking_order` (human-readable order string; **note:** `ranking_hash` in code is a short SHA-256 prefix of that order), softmax entropy, `sampling_phase`, optional `distance_to_nearest_boundary`.
- **Lanes F–H** (sensitivity map, borderline re-eval, pole ablation, signal_stress sweep): to be wired in `mass_kernel_study` / a dedicated wrapper script.

See [`docs/proposals/PROPOSAL_EXPERIMENT_V5_SENSITIVITY.md`](../../docs/proposals/PROPOSAL_EXPERIMENT_V5_SENSITIVITY.md).

---

## Part 3 — Infrastructure (status)

| Item | Status |
|------|--------|
| [`scripts/run_simplex_decision_map.py`](../../scripts/run_simplex_decision_map.py) — `--full-ranking`, refinement, `--plot-dir`, **`--plot-extended`** (gap + entropy heatmaps, boundary overlay), per-row **`distance_to_nearest_boundary`** | Implemented |
| [`scripts/run_experiment_v5_sensitivity.py`](../../scripts/run_experiment_v5_sensitivity.py) — screening CSV, refinement CSV, `boundaries.json`, `summary.json`, optional plots; full-kernel note points to mass study | Implemented (mixture phases only) |
| Full-stack **`EthicalKernel.process`** sweep at many mixture points | Use [`run_mass_kernel_study.py`](../../scripts/run_mass_kernel_study.py) / [`run_experiment_v4_full_kernel_100k.py`](../../scripts/run_experiment_v4_full_kernel_100k.py) |

---

## Part 4 — Using results for default weights

- **Geometry:** where the default mixture point falls in each scenario region; distance to boundaries (fragility).
- **Multi-objective:** maximize minimum margin across reference scenarios (grid data or LP if scores are linear in `w`).
- **Pole ablation:** compare pre-argmax poles ON vs OFF on the same `(scenario, mixture)` sample.

---

## Appendix — Corner check (linear mixture)

```python
import numpy as np

scores = {
    "distribute_by_need": {"u": 0.275, "d": 0.260, "v": 0.305},
    "distribute_by_lottery": {"u": 0.265, "d": 0.295, "v": 0.270},
    "distribute_by_impact": {"u": 0.305, "d": 0.258, "v": 0.275},
}

corners = {
    "util": (1.0, 0.0, 0.0),
    "deon": (0.0, 1.0, 0.0),
    "virtue": (0.0, 0.0, 1.0),
    "center": (1 / 3, 1 / 3, 1 / 3),
}

for name, w in corners.items():
    best = None
    best_val = -1.0
    for action, s in scores.items():
        mixed = w[0] * s["u"] + w[1] * s["d"] + w[2] * s["v"]
        if mixed > best_val:
            best_val = mixed
            best = action
    print(name, best, best_val)
```

---

*Last aligned with `runner.py` hypothesis triples for scenarios 17–19 (2026).*
