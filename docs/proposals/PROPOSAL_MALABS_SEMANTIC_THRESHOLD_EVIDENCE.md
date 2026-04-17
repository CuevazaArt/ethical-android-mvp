# MalAbs semantic cosine thresholds — evidence posture (θ_block / θ_allow)

**Scope:** Layer 1 embedding similarity zones in `src/modules/semantic_chat_gate.py` (`KERNEL_SEMANTIC_CHAT_SIM_BLOCK_THRESHOLD`, `KERNEL_SEMANTIC_CHAT_SIM_ALLOW_THRESHOLD`).

## What this repository claims

- **Defaults** are exposed as named constants (`DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD`, `DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD`) so changes are **reviewable** and **guarded by tests**.
- **This repo does not ship** a labeled dataset, per-threshold confusion matrix, or A/B study that uniquely justifies `0.82` over `0.78` or `0.90`. Treating those numbers as “validated” would overstate the evidence.

## Why not only “pick numbers” in code

Cosine similarity to a small anchor set is a **heuristic**. Operating points trade off:

- **Higher θ_block** — more inputs in the block zone (stricter; risk of blocking benign text that sits close to harmful anchors in embedding space).
- **Lower θ_block** — fewer automatic blocks (risk of missing paraphrases that remain below θ_block).
- **Higher θ_allow** — wider automatic-allow band (risk of allowing harmful paraphrases that happen to score low vs anchors).
- **Lower θ_allow** — narrower allow band, **wider ambiguous band** → more fail-safe blocks when the LLM arbiter is off, or more arbiter calls when it is on.

The **ambiguous band** exists so operators can route borderline cases to layer 2 or accept fail-safe block without pretending a single scalar is a calibrated classifier.

## Empirical work (out of band)

To justify a specific pair `(θ_block, θ_allow)` with false positive / false negative rates you need at minimum:

1. **Frozen embedding backend** (same model and preprocessing as production).
2. **Labeled chat inputs** (harmful vs benign under your policy), stratified by attack style.
3. **Report** precision/recall or cost-weighted metrics **per threshold** on a hold-out set.

Until that exists, defaults remain **engineering priors**: conservative block at high similarity, conservative allow at low similarity, ambiguous in between.

## In-repo tools

- **Tests** assert the default constants so accidental edits fail CI (`tests/test_semantic_chat_gate.py`).
- **Doc–code alignment:** `tests/test_semantic_threshold_proposal_doc_alignment.py` checks this proposal still names the same default numerals (`0.82` / `0.45`) as the shipped constants.
- **`classify_semantic_zone`** is the single pure mapping from `(best_sim, θ_block, θ_allow)` to zones; production and tests use the same logic.
- **`scripts/report_semantic_zone_table.py`** prints how zones change for synthetic `best_sim` values and optional θ sweeps (geometry only — not labeled FP/FN).

## Overrides

Operators set env vars per deployment; see `MALABS_SEMANTIC_LAYERS.md` and ADR 0003. Document any production tuning in runbooks, not only in code.

## In-repo evaluation script

To provide initial evidence for threshold tuning, `scripts/evaluate_semantic_thresholds.py` evaluates the semantic gate on a small labeled dataset using simple keyword-based similarity (Jaccard index on word sets) as a proxy for semantic similarity.

**Example output** (with adjusted thresholds for demonstration):

```
Evaluation with θ_block=0.2, θ_allow=0.05
Dataset: 6 harmful, 8 benign

Confusion Matrix:
  True Positives (harmful blocked): 6
  True Negatives (benign allowed): 4
  False Positives (benign blocked): 4
  False Negatives (harmful allowed): 0

Precision: 0.600
Recall: 1.000
Accuracy: 0.714
```

This shows the trade-off: lower θ_block increases recall (blocks more harmful) but decreases precision (blocks more benign). The default θ_block=0.82 / θ_allow=0.45 would allow all in this dataset, prioritizing low false positives over blocking paraphrases.

**Limitations:** The script uses keyword overlap, not true embeddings. For production validation, use real embedding models and larger labeled datasets.

## Index and agent guidance
