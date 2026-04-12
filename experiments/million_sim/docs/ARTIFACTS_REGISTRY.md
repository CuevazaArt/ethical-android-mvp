# Experiment artifacts registry (lightweight)

Heavy outputs (JSONL, large CSV, PNG, multi‑MB JSON) are **not** versioned. They live under [`../out/`](../out/) **locally** when you run scripts; **regenerate** with the commands in [`README.md`](../README.md) and [`NEXT_EXPERIMENT_DESIGN.md`](NEXT_EXPERIMENT_DESIGN.md).

This file keeps **consultable summaries and run tables** only. Update the **Last verified** row when you reproduce a run.

---

## Run index (operator-maintained)

| Run label | Last verified (UTC) | Script / command (short) | N or scope | Notes |
|-----------|----------------------|----------------------------|------------|--------|
| `v5_sensitivity_latest` | 2026-04-12 | `run_experiment_v5_sensitivity.py` — scenarios 16–19, denom 30, refinement 500, `--plot-extended` | Mixture-only grid + refinement | Per-scenario table below; full CSV/PNG were local-only |
| `feedback_posterior` | 2026-04-12 | `run_feedback_posterior.py` — default fixture `tests/fixtures/feedback/compatible_17_18_19.json`, MC 12000 | 3 feedback items | Posterior snapshot below |
| `v4_full_kernel_100k` | 2026-04-12 | `run_mass_kernel_study.py` protocol v4, `n=100000` | 100k full `EthicalKernel.process` | Summary metrics below; JSONL/CSV were local-only |

---

## Protocol v5 (mixture-only) — last captured summary

**Parameters:** `screening_denominator=30`, `refinement_samples_requested=500`, `refinement_rows_written=2000`, scenarios **16,17,18,19**.

| scenario_id | n_screening | n_refinement | n_unique_winners | unique_winners (names) | n_bisections |
|-------------|-------------|--------------|------------------|-------------------------|--------------|
| 16 | 496 | 500 | 2 | alpha_soft, beta_force | 16 |
| 17 | 496 | 500 | 3 | distribute_by_impact, distribute_by_lottery, distribute_by_need | 61 |
| 18 | 496 | 500 | 3 | defer_to_release, disclose_fully, partial_acknowledge | 71 |
| 19 | 496 | 500 | 2 | protect_intervene, retreat_deescalate | 52 |

---

## ADR 0012 feedback posterior — last captured snapshot

**Input:** `tests/fixtures/feedback/compatible_17_18_19.json` (compatible preferences on 17–19).  
**Updater:** `explicit_triples` (Dirichlet MC + sequential update).

| Field | Value |
|-------|--------|
| `feedback_consistency` | compatible |
| `posterior_alpha` (util, deon, virtue) | ≈ 4.880, 5.262, 6.059 |
| `posterior_mean_weights` | ≈ 0.301, 0.325, 0.374 |
| `joint_satisfaction_rate` (MC under posterior) | ≈ 0.474 |

---

## Full-kernel mass study v4 — last captured summary (100k)

**Meta (abbrev.):** `schema_version` 4, `agreement_rate_vs_reference` **1.0**, `unique_final_actions` **11**, `runtime_seconds` ≈ **28**, `sims_per_second` ≈ **3548**, `git_commit_short` **e6a86fc** (example run; yours will differ).

**Decision modes (counts):** `gray_zone` 84000, `D_delib` 16000.

**Fixture:** `tests/fixtures/empirical_pilot/scenarios.json`.

For full histograms and per-tier tables, re-run and inspect `summary.json` locally; do not commit large files.

---

## Policy

- **Delete** local `out/` contents when disk space matters; keep **this registry** updated if you rely on the numbers for papers or ops.
- **Canonical** scenario triples (17–19): [`NEXT_EXPERIMENT_DESIGN.md`](NEXT_EXPERIMENT_DESIGN.md) Part 1 and `src/simulations/runner.py` (repo root).
