# MalAbs chat text — layered detection (lexical → embeddings → LLM)

This document describes the **pre-filter architecture** for `AbsoluteEvilDetector.evaluate_chat_text` when the semantic gate is on (**default** when `KERNEL_SEMANTIC_CHAT_GATE` is unset; set `0` for lexical-only). Physical-action MalAbs (`evaluate` on structured actions) is unchanged.

## Order of execution

1. **Layer 0 — Lexical (always)**  
   Normalized substring lists in `_evaluate_chat_text_lexical` (`src/modules/absolute_evil.py`). Fast, deterministic; catches exact and trivially normalized phrases.

2. **Layer 1 — Embeddings (when gate on; default)**  
   Only if layer 0 did **not** block. Ollama `POST /api/embeddings` compares user text to **anchor phrases** (built-in reference groups + `add_semantic_anchor` runtime entries). Cosine similarity defines three zones:
   - **sim ≥ θ_block** (`KERNEL_SEMANTIC_CHAT_SIM_BLOCK_THRESHOLD`, default `0.82`; legacy `KERNEL_SEMANTIC_CHAT_SIM_THRESHOLD` applies here if block unset) → **block**.
   - **sim ≤ θ_allow** (`KERNEL_SEMANTIC_CHAT_SIM_ALLOW_THRESHOLD`, default `0.45`) → **allow** (no MalAbs block).
   - **Between** → **ambiguous band** → layer 2 if enabled, else **fail-safe block**.

3. **Layer 2 — LLM arbiter (optional)**  
   Only in the ambiguous band. Requires `KERNEL_SEMANTIC_CHAT_LLM_ARBITER=1` and a **text completion backend** passed from the kernel (`EthicalKernel._malabs_text_backend()` → `LLMModule._text_backend`).  
   The model returns a small JSON object (`block`, `category`, `confidence`, `reason`).  
   **Failure** (timeout, bad JSON, exception) → **fail-safe block**.

## Degradation ladder (single contract)

| State | Behavior |
|-------|----------|
| Gate **off** (`KERNEL_SEMANTIC_CHAT_GATE=0`) | Lexical layer only (opt-in for tests or airgapped lexical-only policy). |
| Gate **on** (default when unset), **no** embedding vector for user text (HTTP/circuit failure and **no** hash fallback) | Semantic tier **defers** → `malabs.embed=unavailable` trace; **lexical + kernel only** (no extra semantic block). |
| Gate **on**, `KERNEL_SEMANTIC_EMBED_HASH_FALLBACK=1` (default **on** when unset) | Deterministic hash vectors when HTTP fails — tier stays active for CI/airgap (weaker semantics; see `semantic_embedding_client.py`). |
| Ambiguous band, arbiter **off** | **Fail-safe block** at semantic layer. |
| Ambiguous band, arbiter **on**, LLM error | **Fail-safe block**. |

Production defaults match that posture (gate + hash on when unset); nominal LAN/hub profiles in `runtime_profiles.py` also set the gate with hash fallback so demos align with CI.

**Metrics:** when `KERNEL_METRICS=1`, counter `ethos_kernel_semantic_malabs_outcomes_total{outcome=...}` records embedding/arbiter outcomes ([`src/observability/metrics.py`](../../src/observability/metrics.py)).

## Runtime anchors

`add_semantic_anchor(phrase, category_key, reason_label)` in `src/modules/semantic_chat_gate.py` appends anchors without redeploying code (e.g. DAO-discovered patterns). Category keys must match MalAbs enums: `INTENTIONAL_LETHAL_VIOLENCE`, `HARM_TO_MINOR`, `UNAUTHORIZED_REPROGRAMMING`, etc.

## See also

- [ADR 0003](adr/0003-optional-semantic-chat-gate.md)  
- [INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md)  
- `src/modules/semantic_chat_gate.py`, `src/modules/absolute_evil.py`, `src/kernel.py`
