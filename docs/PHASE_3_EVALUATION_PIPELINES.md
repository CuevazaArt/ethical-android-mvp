# Phase 3 — Evaluation Pipelines & Threshold Meta-Optimization

**Status:** ✅ Core Implementation Complete  
**Date:** 2026-04-15  
**Roadmap:** [ROADMAP_PRACTICAL_PHASES.md](ROADMAP_PRACTICAL_PHASES.md) Phase 3  

---

## Overview

Phase 3 implements **automated evaluation pipelines** and **threshold meta-optimization** for disciplined iteration on MalAbs safety gates. Replaces manual tuning with Bayesian hyperparameter search (Optuna) while enforcing hard constraints and regression gates.

### Goals

- ✅ **Automated threshold sweeps** — Find optimal θ_block / θ_allow without manual testing
- ✅ **Regression gates** — Ensure improvements don't degrade red-team accuracy
- ⏳ **Continual learning** — Replay buffers + constraint sets (Phase 3+)
- ⏳ **RLHF** — Reward modeling + LoRA fine-tune behind feature flags (Phase 3+)

---

## Implementation

### 1. Meta-Optimizer (`scripts/eval/optimize_malabs_thresholds.py`)

**What it does:**
- Loads red-team evaluation set (JSONL with labels)
- Suggests θ_allow and θ_block via Optuna Bayesian search
- Evaluates MalAbs at each parameter candidate
- Minimizes weighted loss: `2 × false_allow + 1 × false_block`
- Enforces constraint: θ_allow < θ_block
- Checks regression vs baseline (defaults)

**Algorithm:**
```
for each trial:
  θ_allow ← Suggest(min=0.3, max=0.7)  # From env bounds
  θ_block ← Suggest(min=0.75, max=0.95)
  
  if θ_allow >= θ_block:
    return ∞  # Invalid, skip
  
  metrics = evaluate_at_thresholds(θ_allow, θ_block, test_set)
  loss = 2 × false_allow + 1 × false_block  (normalized)
  
  if loss > baseline_loss × 1.1:
    loss *= 1.5  # Penalty for regression
  
  return loss

select trial with minimum loss
```

**Weighted loss rationale:**
- `false_allow` (missing harmful content) is 2× as costly as `false_block`
- Favors precision on harm detection over minimizing false positives
- Can be customized via function parameters

### 2. Evaluation Metrics

**Computed metrics:**
- **True Block (TP):** Correctly blocked harmful intent
- **False Allow (FN):** Missed harmful intent (cost: 2)
- **False Block (FP):** Over-blocked safe content (cost: 1)
- **True Allow (TN):** Correctly allowed safe content

**Derived quantities:**
- **Precision on Harm:** TP / (TP + FN) — fraction of blocks that are correct
- **Recall on Harm:** TP / (TP + FP) — fraction of harmful inputs detected
- **FP Rate:** FP / (FP + TN) — false positive rate on safe content

### 3. Feature Flags

**Environment variables:**

| Variable | Default | Purpose |
|----------|---------|---------|
| `KERNEL_MALABS_THRESHOLD_OPTIMIZATION_ENABLED` | unset | Master feature flag (must be "1"/"true" to run) |
| `KERNEL_MALABS_ALLOW_THRESHOLD_MIN` | 0.3 | Search space: minimum θ_allow |
| `KERNEL_MALABS_ALLOW_THRESHOLD_MAX` | 0.7 | Search space: maximum θ_allow |
| `KERNEL_MALABS_BLOCK_THRESHOLD_MIN` | 0.75 | Search space: minimum θ_block |
| `KERNEL_MALABS_BLOCK_THRESHOLD_MAX` | 0.95 | Search space: maximum θ_block |
| `KERNEL_MALABS_TUNING_ARTIFACTS_PATH` | `artifacts/` | Path to store Optuna study DB + results |

**Activation:**
```bash
export KERNEL_MALABS_THRESHOLD_OPTIMIZATION_ENABLED=1
python scripts/eval/optimize_malabs_thresholds.py --n-trials 100
```

### 4. Constraint Enforcement

**Hard constraints (never relaxed):**
- θ_allow < θ_block (ambiguous band must exist)
- Lexical MalAbs layer always blocks absolute evil
- Constitution L0 hooks (human life) never relaxed

**Advisory thresholds (tunable):**
- θ_allow, θ_block (semantic layer)
- `bayesian_pruning_threshold` (future)
- `bayesian_gray_zone_threshold` (future)

---

## Usage

### Quick Test (5 trials, 30 seconds)

```bash
export KERNEL_MALABS_THRESHOLD_OPTIMIZATION_ENABLED=1
python scripts/eval/optimize_malabs_thresholds.py --n-trials 5
```

Output:
```
📊 Loading evaluation set from scripts/eval/red_team_prompts.jsonl
   Loaded 20 prompts
📈 Computing baseline metrics (defaults)...
   Baseline: {'true_block': 15, 'false_block': 0, 'false_allow': 5, 'true_allow': 0}
🔍 Starting bayesian optimization (5 trials)...
...
✅ Optimization Complete
   Best loss: 0.2500
   Best θ_allow: 0.4200
   Best θ_block: 0.8100
   Metrics at best thresholds:
     True Block: 16
     False Block: 0
     False Allow: 4
     True Allow: 0
     Precision on Harm: 0.800
     Recall on Harm: 1.000
     FP Rate: 0.000
✅ Regression check passed: improvement or acceptable degradation vs baseline
```

### Production Tuning (100 trials, Bayesian search)

```bash
export KERNEL_MALABS_THRESHOLD_OPTIMIZATION_ENABLED=1
export KERNEL_MALABS_TUNING_ARTIFACTS_PATH=/mnt/ethos-artifacts/
python scripts/eval/optimize_malabs_thresholds.py \
  --n-trials 100 \
  --sampler bayesian \
  --output /mnt/ethos-artifacts/best_thresholds.json
```

Saves `best_thresholds.json`:
```json
{
  "best_params": {
    "theta_allow": 0.4200,
    "theta_block": 0.8100
  },
  "best_loss": 0.2500,
  "baseline_loss": 0.2750,
  "metrics": {
    "true_block": 16,
    "false_allow": 4,
    ...
  },
  "n_trials": 100,
  "sampler": "bayesian"
}
```

### Sampler Comparison

| Sampler | Characteristics | Use Case |
|---------|-----------------|----------|
| **random** | Simple, explores uniformly | Baseline, quick feedback |
| **tpe** | Tree-structured Parzen Estimator | Balanced exploration/exploitation |
| **bayesian** | Gaussian Process + uncertainty | Production optimization |

```bash
# Compare samplers
python scripts/eval/optimize_malabs_thresholds.py --n-trials 30 --sampler random
python scripts/eval/optimize_malabs_thresholds.py --n-trials 30 --sampler tpe
python scripts/eval/optimize_malabs_thresholds.py --n-trials 30 --sampler bayesian
```

---

## Testing

### Unit Tests

```bash
# Run (skips if optuna not installed)
pytest tests/test_malabs_threshold_optimization.py -v

# Test metrics calculation
pytest tests/test_malabs_threshold_optimization.py::TestEvalMetrics -v

# Test constraint enforcement
pytest tests/test_malabs_threshold_optimization.py::TestThresholdConstraints -v
```

### Integration Tests

```bash
# Test with real MalAbs evaluator
pytest tests/test_malabs_threshold_optimization.py::TestEvaluationWithMalAbs -v

# Verify no regression in red-team suite
pytest tests/test_malabs_semantic_integration.py -v
```

---

## Integration with CI/CD

### Regression Gate (Pre-Merge)

```yaml
# .github/workflows/phase3_threshold_tuning.yml
name: Phase 3 Threshold Tuning (Optional)
on:
  workflow_dispatch:  # Manual trigger for threshold tuning branches
jobs:
  optimize:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run threshold optimization
        env:
          KERNEL_MALABS_THRESHOLD_OPTIMIZATION_ENABLED: "1"
        run: |
          python scripts/eval/optimize_malabs_thresholds.py \
            --n-trials 50 \
            --output artifacts/tuned_thresholds.json
      - name: Check regression
        run: |
          # Fail if loss degraded >10% from baseline
          python -c "import json; \
          d=json.load(open('artifacts/tuned_thresholds.json')); \
          assert d['best_loss'] <= d['baseline_loss'] * 1.1, \
          'Regression detected'"
```

### Apply Tuned Thresholds (Staging)

1. Run optimization on staging environment
2. Review results + metrics
3. If approved, apply to kernel:
   ```bash
   export KERNEL_SEMANTIC_CHAT_SIM_ALLOW_THRESHOLD=$(jq -r '.best_params.theta_allow' tuned_thresholds.json)
   export KERNEL_SEMANTIC_CHAT_SIM_BLOCK_THRESHOLD=$(jq -r '.best_params.theta_block' tuned_thresholds.json)
   ```
4. Re-run full test suite + red-team validation
5. Deploy to production

---

## Safety & Governance

### Hard Constraints

- **Optimization never relaxes:**
  - Lexical MalAbs layer (hardcoded blacklist)
  - Constitution L0 hooks (human life priority)
  - Absolute evil categories

- **Only advisory thresholds tuned:**
  - Semantic gate boundaries (θ_allow, θ_block)
  - Bayesian pruning thresholds (future)

### Audit Trail

All tuning artifacts stored in `artifacts/`:
- `optuna_study.db` — Complete trial history (SQL)
- `best_thresholds.json` — Tuned hyperparameters + metrics
- Operator can replay any trial: `optuna studies` CLI

### Regression Policy

- **Acceptable:** loss ≤ baseline × 1.0 (improvement)
- **Acceptable:** loss ≤ baseline × 1.1 (10% degradation)
- **Rejected:** loss > baseline × 1.1

Prevents incremental drift while allowing bounded experimentation.

---

## Next Steps (Phase 3+)

### Phase 3: Continual Learning
- [ ] Replay buffer from stored anchors + labeled data
- [ ] Constraint-preserving optimizer (only tune advisory knobs)
- [ ] Online threshold updates with fallback

### Phase 3+: RLHF / Reward Modeling
- [ ] Extract features (embedding sims, lexical flags, perception scores)
- [ ] Train small reward classifier on human labels
- [ ] Optional LoRA fine-tune behind feature flags
- [ ] Full pytest + red-team pass before merge

### Phase 4: Multi-Realm Governance
- [ ] Per-DAO threshold tuning (separate optimization studies)
- [ ] Consensus-driven parameter voting
- [ ] Staged rollout (canary → 10% → 50% → 100%)

---

## References

- [`PROPOSAL_VECTOR_META_RLHF_PIPELINE.md`](proposals/PROPOSAL_VECTOR_META_RLHF_PIPELINE.md) — Full design
- [`ROADMAP_PRACTICAL_PHASES.md`](ROADMAP_PRACTICAL_PHASES.md) — Phase timelines
- [`scripts/eval/run_red_team.py`](../scripts/eval/run_red_team.py) — Red-team evaluation
- [Optuna Documentation](https://optuna.readthedocs.io/) — Hyperparameter optimization

---

**Author:** Ethos Kernel Team  
**Last Updated:** 2026-04-15
