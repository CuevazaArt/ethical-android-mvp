# Experiment history — million-sim lineage and what came after

This document is the **narrative arc** of the large-N batch studies under `experiments/million_sim/`: motivation, what the first million-run **did and did not** establish, **external critique** we accept, **repository responses** (protocols and ADRs), and a **successor design** aimed at decision boundaries rather than redundant Monte Carlo.

For the **tabular readout** of run `cursor_start_1e6`, see [`EXPERIMENT_REPORT.md`](EXPERIMENT_REPORT.md). For **CLI defaults** and pilot recipes, see [`README.md`](../README.md). For **scenarios 17–19**, simplex coverage, and **v5** tooling status, see [`NEXT_EXPERIMENT_DESIGN.md`](NEXT_EXPERIMENT_DESIGN.md) (do not duplicate those tables here). Mass-study design: [`docs/proposals/PROPOSAL_MILLION_SIM_EXPERIMENT.md`](../../../docs/proposals/PROPOSAL_MILLION_SIM_EXPERIMENT.md).

---

## Chapter 1 — Why a “million simulations” existed

External reviewers asked whether **sweeping weights** in the batch ethical path produces **measurable** variation. The team stood up a **reproducible** harness: stratified scenario IDs, random mixture vectors on the util/deon/virtue simplex, random pole scalars, JSONL + summary JSON, and agreement against **fixture reference actions** for internal consistency.

The **first** full-scale run (`cursor_start_1e6`, documented in [`EXPERIMENT_REPORT.md`](EXPERIMENT_REPORT.md)) completed successfully and showed **100% agreement** with those references and **nine** distinct `final_action` values—one stable winner name per scenario ID across all draws.

That result was easy to **misread** as “robust ethics.” The following chapter clarifies what it actually tested.

---

## Chapter 2 — Critical review (accepted limits)

The critique below is **not** a dismissal of the engineering work; it reframes **what kind of claim** is valid.

### 2.1 Agreement ≠ causal robustness of “the right choice”

**100% agreement** under random mixture weights primarily showed that **`final_action` did not flip** across those draws. That supports **stability of the discrete winner** under that sampling scheme—not external validity, not safety in the wild, and not proof that the scorer is “correct.”

### 2.2 Pole sweeps and the argmax (architecture)

When **ethical poles** only **narrate** the action **after** the mixture argmax, **sweeping pole base weights** does not change which candidate wins. The historical report states this explicitly under **“Pole weights likely do not move the argmax”** in [`EXPERIMENT_REPORT.md`](EXPERIMENT_REPORT.md). Spending large **N** on pole randomization therefore **stress-tested infrastructure** and **post-hoc narrative**, not sensitivity of the **winning** label to poles **in that wiring**.

**Repository response:** optional **pre-argmax pole modulation** (`KERNEL_POLES_PRE_ARGMAX`, [ADR 0010](../../../docs/adr/0010-poles-pre-argmax-modulation.md)) so poles **can** affect util/deon/virtue channels **before** argmax when enabled. Interpreting any pole sweep still requires stating whether this path is **on** for that run.

### 2.3 Mixture sweeps without recorded margins

If the **top-two expected impacts** are almost always far apart, **Dirichlet(1,1,1)** may never reorder candidates. The “million” label then **adds little** beyond a smaller run with the same distribution when the outcome is **almost always identical**: extra samples mainly tighten decimals on a **binary** agreement rate, not the **geometry** of the decision surface.

**Repository response:** later protocols record **top-2 scorer fields**, **margin bins**, mixture **entropy**, and **observation palettes** (see [`PROPOSAL_MILLION_SIM_EXPERIMENT.md`](../../../docs/proposals/PROPOSAL_MILLION_SIM_EXPERIMENT.md) §2b–2e and schema notes).

### 2.4 Early vignettes can be “easy” for the mixture

Nine canonical scenarios were not chosen to **maximize** near-ties; many exhibit **wide** top-2 gaps under default valuations. That is fine for **demos**, but a **sensitivity study** needs **calibrated** difficulty when the goal is to see **flips** or **boundaries**.

**Repository response:** batch scenarios **10–12** (frontier / borderline), **13–15** (polemic + synthetic extreme), classic **economy triple** in lanes A/C, optional **signal stress**—all documented in the proposal and [`README.md`](../README.md).

### 2.5 Reference labels are maintainer priors

Fixture **reference_action** rows are **internal** consistency targets, not independent ground truth. High agreement measures **alignment with those priors**, not **correctness** in a normative sense. The research disclaimer in [`README.md`](../README.md) applies.

---

## Chapter 3 — What the repository did next (summary)

Rather than repeating ADR text here:

| Direction | Where to read |
|-----------|----------------|
| Pre-argmax poles | [ADR 0010](../../../docs/adr/0010-poles-pre-argmax-modulation.md) |
| Pre-argmax context richness | [ADR 0011](../../../docs/adr/0011-context-richness-pre-argmax.md) |
| Protocol v2 (lanes + telemetry) | Proposal §2b, [`README.md`](../README.md) |
| Protocol v3 (borderline + poles pre-argmax default) | Proposal §2c |
| Protocol v4 (polemic lane + context richness flag) | Proposal §2e, [`README.md`](../README.md) |
| Mixture naming | [ADR 0009](../../../docs/adr/0009-ethical-mixture-scorer-naming.md) |
| Scenarios 17–19, simplex, protocol v5 | [`NEXT_EXPERIMENT_DESIGN.md`](NEXT_EXPERIMENT_DESIGN.md) |
| Optional Bayesian mixture telemetry | [ADR 0012](../../../docs/adr/0012-bayesian-weight-inference-ethical-mixture-scorer.md) |

---

## Chapter 4 — Successor experiment: marginal sensitivity and near-ties (design)

The following is the **integrated** successor to “run more of the same million.” It keeps what was missing: **explicit margins**, **regions of the simplex**, and **scenarios built to cross decision boundaries**—without redundant brute-force **N** when the outcome variance is negligible.

### Phase 1 — Simplex corner audit (cheap, decisive)

For each scenario of interest, set mixture weights to the **three pure corners** \([1,0,0]\), \([0,1,0]\), \([0,0,1]\) and the **uniform center** \((1/3,1/3,1/3)\). Record **full ranking** of viable candidates and **score_gap** (top minus second).

- If **no winner changes** even at corners, the mixer is **insensitive on that vignette** under this scorer path; **more random samples** will not map a **boundary**—you need **new valuations** or **near-tie** construction.
- This phase is **not** a full `EthicalKernel.process` audit (no MalAbs stack, will, narrative poles unless you extend the tool).

**Tooling:** [`scripts/audit_mixture_simplex_corners.py`](../../../scripts/audit_mixture_simplex_corners.py) implements Phase 1 on `WeightedEthicsScorer` + `ALL_SIMULATIONS`.

### Phase 2 — Synthetic near-tie scenarios

Add **5–10** vignettes where **top-two** triples \((u,d,v)\) are **designed** so convex mixture weights **can** reorder leaders, with **controlled gaps** \(\Delta \in \{0.01, 0.05, 0.10, 0.20\}\) (conceptually—exact encoding lives in scenario definitions).

### Phases 3–4 — Simplex grid, refinement, visualization

**Implemented** tooling, default flags, coverage snapshot command for **17–19**, and protocol **v5** bundle status are maintained in **[`NEXT_EXPERIMENT_DESIGN.md`](NEXT_EXPERIMENT_DESIGN.md)** (Parts 1–3) so this file stays narrative-only.

### Architectural note (poles)

If the research question is **pole sensitivity of the discrete winner**, the run must use **pre-argmax** pole modulation (or equivalent) so poles affect **candidate scores** before argmax; otherwise pole sweeps remain **narrative-only** for the winner label. See Chapter 2.2 and ADR 0010.

---

## Chapter 4b — Full kernel at **100,000** (protocol **v4**)

Simplex-only scripts do **not** run `EthicalKernel.process`. For the **full stack** (MalAbs, mixture, pre-argmax poles, will, optional context richness / signal stress), use the **wrapper and flags** in **[`README.md`](../README.md)** — section **“Full decision stack at N = 100,000”** (`run_experiment_v4_full_kernel_100k.py`, lane **D** + scenario **16**, frontier tuning for **10–12** in `runner.py`).

---

## Chapter 5 — How this document stays maintainable

- **Facts** about run `cursor_start_1e6` stay in [`EXPERIMENT_REPORT.md`](EXPERIMENT_REPORT.md).
- **CLI and protocol defaults** stay in [`README.md`](../README.md) and [`PROPOSAL_MILLION_SIM_EXPERIMENT.md`](../../../docs/proposals/PROPOSAL_MILLION_SIM_EXPERIMENT.md).
- **Scenarios 17–19**, simplex coverage commands, and **v5** infrastructure status stay in [`NEXT_EXPERIMENT_DESIGN.md`](NEXT_EXPERIMENT_DESIGN.md).
- **Lightweight run summaries** (no multi‑MB artifacts) stay in [`ARTIFACTS_REGISTRY.md`](ARTIFACTS_REGISTRY.md).
- **This file** holds **story + critique + successor intent** so new contributors see **why** the million run is both **useful** (harness, throughput, honesty about poles) and **limited** (claims, circular references, marginal information from huge **N** when flips are absent).

---

*Ethos Kernel — experiment lineage and forward design (April 2026).*
