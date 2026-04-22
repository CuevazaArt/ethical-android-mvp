# Proposal: static weight sensitivity sweep (poles + mixture)

**Purpose:** Run **mass batch simulations** while **centering** tunable static weights and **sweeping** them in both directions — producing a **broad synthetic dataset** for transparency, plots, and discussion with reviewers who question the fixed **weighted mixture** (ADR 0009). This does **not** replace DAO calibration or real-world field trials; it narrows the **design space** explored in silico.

**Related:** [POLE_WEIGHT_CALIBRATION_AND_EVIDENCE.md](POLE_WEIGHT_CALIBRATION_AND_EVIDENCE.md), [ADR 0009](../adr/0009-ethical-mixture-scorer-naming.md), [PROPOSAL_EXPERIMENTAL_SANDBOX_SCENARIOS.md](PROPOSAL_EXPERIMENTAL_SANDBOX_SCENARIOS.md), [PROPOSAL_MILLION_SIM_EXPERIMENT.md](PROPOSAL_MILLION_SIM_EXPERIMENT.md) (N≥10⁶ design), `scripts/run_stochastic_sandbox.py`.

---

## 1. What is centered

| Parameter | Center | Spectrum |
|-----------|--------|----------|
| **Pole base weights** (`EthicalPoles.base_weights`) | **0.5** each (compassionate / conservative / optimistic) — matches in-repo defaults | Independently per axis, clipped to **[0.05, 0.95]** |
| **Ethical mixture weights** (`WeightedEthicsScorer.hypothesis_weights`) | **(1/3, 1/3, 1/3)** — uniform simplex center | Perturbed on the **probability simplex** (renormalized), not the default `[0.4, 0.35, 0.25]` |

Using **(1/3, 1/3, 1/3)** for mixture sweeps is intentional: it is the **symmetric** center of the hypothesis blend. Comparing against the shipped default is a separate analysis (overlay default as a marker in plots).

---

## 2. Sweep geometries (`SweepMode`)

- **axes**: vary **one** dimension at a time (others at center) — cheap, interpretable “skeptic” curves.
- **grid**: full factorial of `steps` points per axis — **explodes** as `steps³`; use small `steps` or `both` only with caps.
- **random**: `samples` draws — **Monte Carlo** over the box (poles) or Gaussian noise on the simplex (mixture).

---

## 3. Runner

**Script:** [`scripts/run_weight_sweep_batch.py`](../../scripts/run_weight_sweep_batch.py)

**Library:** [`src/sandbox/weight_sweep.py`](../../src/sandbox/weight_sweep.py)

**Examples:**

```bash
# Pole-only axes sweep (15 configs × 9 scenarios = 135 runs with default steps=5)
python scripts/run_weight_sweep_batch.py --target poles --mode axes --steps 5 --amplitude 0.35 --output artifacts/pole_axes.json

# Mixture random cloud near 1/3 center
python scripts/run_weight_sweep_batch.py --target mixture --mode random --samples 120 --mixture-amplitude 0.12 --output artifacts/mixture_random.json --csv artifacts/mixture_random.csv

# Cartesian product — only after checking counts; script enforces --max-total-runs
python scripts/run_weight_sweep_batch.py --target both --mode axes --steps 5 --amplitude 0.25 --mixture-amplitude 0.1 --max-total-runs 20000 --output artifacts/combo_sweep.json
```

**Artifact JSON:** `runs[]` rows include `scenario_id`, `final_action`, `decision_mode`, optional `pole_*` / `mixture_*` columns, `agree_reference`, `config_index`. **`meta.summary`** includes `agreement_rate` vs reference labels and **unique_final_actions** across the grid.

**CSV:** optional `--csv` for notebooks (matplotlib, Vega, etc.).

---

## 4. Interpretation (honest)

- **Agreement rate** vs maintainer `reference_action` will **move** when weights move — that is **expected**; the point is to **map sensitivity**, not to maximize agreement.
- **“Bayes skeptics”** should read ADR 0009: the mixture is **not** posterior inference; this sweep is **hyperparameter stress**, not evidence of external moral truth.
- **Operational DAO / field trials** remain the path to **institutional** weight choices; this repo exports **reproducible synthetic** tables for **pre-field** design review.

---

## 5. Future work

- Stratify by `difficulty_tier` in post-processing (join on `scenario_id`).
- Export **Parquet** or **SQLite** for very large sweeps.
- Optional: pin `KERNEL_POLE_LINEAR_CONFIG` path in metadata for full pole-linearity sweeps.

---

*MoSex Macchina Lab — transparency through exhaustive synthetic sweeps, not a substitute for human validation.*
