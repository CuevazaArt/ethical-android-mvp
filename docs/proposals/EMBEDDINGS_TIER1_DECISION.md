# EMBEDDINGS_TIER1_DECISION — sentence-transformers GO / NO-GO

**Status:** NO-GO (deferred — lexical ceiling not yet confirmed exhausted)
**Author:** Juan Cuevaz / Mos Ex Machina
**Created:** 2026-05-04
**Relates to:** V2_164_EMBEDDINGS_SPIKE_DEONTOLOGY.md, V2_167_EMBEDDINGS_SPIKE_VIRTUE.md,
V2_169_EMBEDDINGS_SPIKE_JUSTICE.md

---

## 1. Context

Three lexical spikes (V2.164, V2.167, V2.169) moved the Hendrycks ETHICS overall score
from **49.70 %** (baseline) to **62.65 %** with `KERNEL_SEMANTIC_IMPACT=1`.
Per-subset breakdown under flag:

| Subset | Baseline | With spike | Delta | Status |
|---|---|---|---|---|
| commonsense | 52.05 % | 52.05 % | +0.00 pp | **No spike deployed** |
| justice | 50.04 % | 52.63 % | +2.59 pp | Spike landed, missed ≥55 % bar |
| deontology | 51.03 % | 57.34 % | +6.31 pp | ✓ Spike accepted |
| virtue | 46.71 % | 80.20 % | +33.49 pp | ✓ Spike accepted |

commonsense and justice are the two remaining subsets below 55 %.  Both rely on
scenario-level language where exact lexical matching has low recall (justice: ~25 %
coverage; commonsense: no spike attempted yet).

Tier 1 in this context means **semantic embeddings via `sentence-transformers`** —
replacing or augmenting the lexical classifiers with cosine-similarity to labelled
anchor sentences.

---

## 2. Concrete cost

### 2.1 Dependency size

| Package | Compressed size | Notes |
|---|---|---|
| `sentence-transformers` | ~4 MB wheel | Pure Python; depends on `torch` |
| `torch` (CPU-only) | ~170–200 MB | Dominant cost; unavoidable |
| Total first-install delta | **~175–205 MB** | Adds to Docker image and cold-start |

Reference: `all-MiniLM-L6-v2` (22 M params, 80 MB download at first use).
Offline policy: model weights are not bundled in the repo; they are downloaded
on first inference unless pre-cached.

### 2.2 Runtime impact

- **Cold start (CPU, no cache):** model load ~1–3 s; sentence encoding ~5–50 ms
  per example depending on length and batch size.
- **Inference in eval loop (15 160 examples, single-threaded):** expected +2–10 min
  to the external benchmark run (currently ~4 min on a CPU-only machine).
- **Production chat turns:** negligible if model is loaded once at server start.
  A single `justice_claim_score` call encodes ~50–200 tokens; latency <50 ms.

### 2.3 Docker image delta

Current image: not measured.  Adding `torch` (CPU-only wheel) will add ~300–350 MB
to the compressed layer.  This violates the "no large new dependencies without
explicit decision" rule in `CONTRIBUTING.md`.

### 2.4 Offline policy conflict

The repo's test suite runs offline in CI (no internet access).  `sentence-transformers`
downloads model weights from the Hub on first use.  This requires either:
(a) bundling weights in the repo (rejected — binary files in git history), or
(b) pre-caching weights in the CI Docker image (adds complexity and size), or
(c) skipping embedding-based tests in CI with `@pytest.mark.skipif` (acceptable
but creates a class of tests that never run in CI).

---

## 3. Expected benefit

Based on published results for `all-MiniLM-L6-v2` on sentence classification tasks
analogous to the Hendrycks ETHICS subsets:

| Subset | Current (lexical) | Expected (embeddings) | Estimated gain |
|---|---|---|---|
| commonsense | 52.05 % | 56–60 % | +4–8 pp |
| justice | 52.63 % | 54–57 % | +1–4 pp |

These are **estimates, not measurements**.  The actual gain depends on the quality of
anchor sentences chosen for each category and the similarity threshold.  The literature
supports a ceiling of ~60–65 % for `all-MiniLM-L6-v2` without fine-tuning on the
specific dataset.  Fine-tuning is out of scope for this kernel.

---

## 4. Decision

### Recommendation: **NO-GO** (deferred)

Criteria for reconsideration:

1. **Both** commonsense and justice remain below 55 % after one more round of
   lexical expansion (add 10–20 new tokens using the discriminative analysis script
   at `scripts/eval/analyze_external_failures.py`).
2. **AND** there is a concrete product need for accuracy above 55 % on these subsets
   (e.g., a regulatory requirement or an external benchmarking commitment).

### Rationale

- The `~175–200 MB` `torch` dependency cost is disproportionate to a +2–8 pp gain on
  two subsets that already exceed the historical baseline.
- The offline CI policy conflict has no clean resolution without bundling weights or
  adding conditional skips throughout the test suite.
- commonsense has **no lexical spike yet** — the low-cost option (lexical expansion)
  has not been exhausted.  Exhausting the cheap path before paying the expensive one
  is the correct sequence.
- justice at 52.63 % missed its 55 % bar by 2.37 pp.  A targeted lexicon expansion
  (10–20 tokens) is more likely to reach 55 % than a general embedding model, and
  costs nothing in runtime or image size.

### Trigger for reconsideration

Open a new proposal (`EMBEDDINGS_TIER1_SPIKE.md`) when **all** of the following hold:

- [ ] commonsense lexical spike attempted and accuracy still <55 %.
- [ ] justice lexical expansion attempted and accuracy still <55 %.
- [ ] Product/regulatory reason documented that requires ≥55 % on both subsets.
- [ ] CI offline policy updated to allow optional internet-dependent tests.

---

## 5. References

- `docs/proposals/V2_164_EMBEDDINGS_SPIKE_DEONTOLOGY.md` — lexical spike pattern
- `docs/proposals/V2_167_EMBEDDINGS_SPIKE_VIRTUE.md` — structural-default pattern
- `docs/proposals/V2_169_EMBEDDINGS_SPIKE_JUSTICE.md` — endorse/reject lexicon pattern
- `docs/proposals/ETHICAL_EXTERNAL_FAILURE_ANALYSIS.md` — per-subset diagnosis
- `evals/ethics/ETHICS_EXTERNAL_RUN_20260504T031141Z.json` — measurement backing this decision
