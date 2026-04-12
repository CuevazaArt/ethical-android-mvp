# Proposal: Experiment protocol v5 — sensitivity mapping on the mixture simplex

**Status:** design + partial implementation (scenarios 17–19, `hypothesis_override`, simplex map extensions).  
**Context:** [`experiments/million_sim/EXPERIMENT_HISTORY.md`](../../experiments/million_sim/EXPERIMENT_HISTORY.md), [`scripts/run_simplex_decision_map.py`](../../scripts/run_simplex_decision_map.py).

## Goal

Produce **real variation** in `final_action` under **weight sweeps**, map **decision boundaries** on the util/deon/virtue simplex, and inform **default mixture weights** — not only agreement rates against a fixed reference.

## Synthetic scenarios 17–19 (in-repo)

| ID | Tier | Candidates | Design intent |
|----|------|--------------|----------------|
| **17** | `frontier_synthetic` | `distribute_by_need`, `distribute_by_lottery`, `distribute_by_impact` | Three **different** pure-corner winners (three regions). |
| **18** | `frontier_synthetic` | `disclose_fully`, `defer_to_release`, `partial_acknowledge` | Same three-corner structure with asymmetric gaps. |
| **19** | `calibration_synthetic` | `protect_intervene`, `retreat_deescalate` | **Util vs deon/virtue** line boundary; tiny virtue margin (0.005). |

Implementation uses **`CandidateAction.hypothesis_override`**: explicit `(util, deon, virtue)` triples; mixture scoring is `dot(mixture_weights, triple) * confidence` (pre-argmax poles/context still apply when enabled).

**Reference labels:** scenarios **17–19** ship with **`reference_action: null`** in the empirical pilot fixture — mapping/calibration only.

## Protocol v5 (planned)

1. **Adaptive sampling** (screening barycentric grid → refinement band around detected edges → optional full-kernel JSONL) — **not** fully wired into `mass_kernel_study` yet.
2. **Rich JSONL rows:** full ranking, `score_gap_12` / `score_gap_13`, `ranking_order` / hash, softmax entropy, `sampling_phase`, distance-to-boundary (post-hoc).
3. **Lanes F–H** (sensitivity map, borderline re-eval, pole ablation, signal_stress sweep) — **future** `mass_kernel_study` / wrapper script work.

## Implemented tooling

- **`scripts/run_simplex_decision_map.py`:** `--full-ranking`, `--no-softmax-entropy`, `--refinement-band`, `--refinement-samples`, `--refinement-seed`; rows include `score_gap_12`/`score_gap_13`, `ranking_order`, `sampling_phase` (`screening` | `refinement`), `candidates_ranked` when `--full-ranking`.
- **`src/sandbox/simplex_mixture_probe.py`:** `score_gap_top3`, per-row `rank`, `ranking_order`.
- **Verification:** `python scripts/audit_mixture_simplex_corners.py --scenario-ids 17,18,19`.

## Next steps (priority)

1. Ternary heatmaps (gap / entropy) and boundary overlays (matplotlib).
2. **`scripts/run_experiment_v5_sensitivity.py`** orchestrating screening → refinement → full kernel (per design doc).
3. **`mass_kernel_study` schema vNext** for lane F–H and summary metrics (`flip_rate_by_scenario`, `boundary_fraction_by_scenario`, etc.).

## Disclaimer

Synthetic triples are **instruments for geometry and sensitivity** — not claims about real-world moral facts.
