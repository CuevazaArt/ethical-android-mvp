# PROPOSAL — Vector index, meta-optimization, continual learning, and RLHF (design)

**Status:** Design / roadmap (not fully implemented in code).  
**Scope:** Semantic MalAbs anchors, threshold tuning, catastrophic forgetting, human labels, and controlled fine-tuning.

## 1. Vector DB and semantic anchors**Goal:** Replace or augment the in-process embedding cache with a persisted vector index (Chroma, Qdrant, or FAISS + metadata store) so reference anchors scale, survive restarts, and support TTL/versioning.

**Interfaces (target):**

- `SemanticAnchorStore`: `upsert_anchor(id, text, embedding, metadata)`, `query_neighbors(vector, k)`, `delete_expired(before)`.
- Env: `KERNEL_SEMANTIC_VECTOR_BACKEND=memory|chroma|faiss`, `KERNEL_SEMANTIC_VECTOR_PERSIST_PATH`, `KERNEL_SEMANTIC_ANCHOR_TTL_S` (partially implemented for memory TTL).

**Policy:** Expiration and scope strings prevent stale DAO-supplied anchors from dominating similarity; optional separate collections per “trust domain” (e.g. org id).

## 2. Continual learning with ethical constraints

**Goal:** Replay buffers and constraint sets so online updates (e.g. threshold drift) do not erase MalAbs invariants.

**Mechanisms (conceptual):**

- **Replay:** stratified batches mixing recent benign, blocked, and “ambiguous” cases from `scripts/eval` + operator logs.
- **Constraints:** hard rules (lexical MalAbs, constitution L0 hooks) never relaxed by optimizers; only advisory thresholds (semantic θ, Bayesian pruning) may move within validated bands.
- **Evaluation gate:** every change must pass the full pytest suite + red-team JSONL before merge.

## 3. Meta-optimization of thresholds

**Goal:** Treat `bayesian_pruning_threshold`, `bayesian_gray_zone_threshold`, semantic `θ_block` / `θ_allow`, and similar knobs as **hyperparameters** tuned on a fixed validation corpus.

**Tooling:** Optuna (Bayesian search) or grid search over bounded intervals; objective = weighted sum of false_allow / false_block from labeled prompts + stability penalty vs baseline.

**Safety:** search only in pre-declared ranges; require monotonic sanity (e.g. θ_allow < θ_block); store Optuna DB under `artifacts/` (gitignored).

## 4. Interpretability (implemented direction)

MalAbs exposes `AbsoluteEvilResult.decision_trace` — short strings such as `malabs.layer0=lexical_substring`, `malabs.layer1=semantic`, `malabs.similarity=above_block_threshold`. WebSocket JSON includes `malabs_trace` when `KERNEL_CHAT_INCLUDE_MALABS_TRACE=1` (see `src/chat_settings.py`).

## 5. RLHF / reward modeling (future)

**Pipeline sketch:**

1. Collect human labels (`human_blocked`) via JSONL + `scripts/eval/hitl_merge_labels.py`.
2. Train a small **reward model** (or classifier) on features: embedding sims, lexical flags, perception aggregates — **not** raw user text in logs unless policy allows.
3. Optional **LoRA** fine-tune of the arbiter model with:
   - **Spacetime constraints:** max steps, frozen MalAbs prefix, rollback on regression tests.
   - **Regression:** `pytest`, `scripts/eval/run_red_team.py`, and snapshot migration tests must pass in CI.

## 6. Embedding transport (implemented)

See `src/modules/semantic_embedding_client.py`: retries, circuit breaker, `get_embedding_transport_stats()`, optional hash-scoped fallback (`KERNEL_SEMANTIC_EMBED_HASH_FALLBACK`).

## Links

- `src/modules/semantic_chat_gate.py` — MalAbs semantic tier.
- `src/chat_settings.py` — chat server env schema.
- `scripts/eval/run_red_team.py` — batch metrics for threshold tuning inputs.
