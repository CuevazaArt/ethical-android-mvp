# MalAbs chat text — layered detection (lexical → embeddings → LLM)

This document describes the **pre-filter architecture** for `AbsoluteEvilDetector.evaluate_chat_text` when `KERNEL_SEMANTIC_CHAT_GATE=1`. Physical-action MalAbs (`evaluate` on structured actions) is unchanged.

## Order of execution

1. **Layer 0 — Lexical (always)**  
   Normalized substring lists in `_evaluate_chat_text_lexical` (`src/modules/absolute_evil.py`). Fast, deterministic; catches exact and trivially normalized phrases.

2. **Layer 1 — Embeddings (optional)**  
   Only if layer 0 did **not** block. Ollama `POST /api/embeddings` compares user text to **anchor phrases** (built-in reference groups + `add_semantic_anchor` runtime entries). Cosine similarity defines three zones:
   - **sim ≥ θ_block** (`KERNEL_SEMANTIC_CHAT_SIM_BLOCK_THRESHOLD`, default `0.82`; legacy `KERNEL_SEMANTIC_CHAT_SIM_THRESHOLD` applies here if block unset) → **block**.
   - **sim ≤ θ_allow** (`KERNEL_SEMANTIC_CHAT_SIM_ALLOW_THRESHOLD`, default `0.45`) → **allow** (no MalAbs block).
   - **Between** → **ambiguous band** → layer 2 if enabled, else **fail-safe block**.

3. **Layer 2 — LLM arbiter (optional)**  
   Only in the ambiguous band. Requires `KERNEL_SEMANTIC_CHAT_LLM_ARBITER=1` and a **text completion backend** passed from the kernel (`EthicalKernel._malabs_text_backend()` → `LLMModule._text_backend`).  
   The model returns a small JSON object (`block`, `category`, `confidence`, `reason`).  
   **Failure** (timeout, bad JSON, exception) → **fail-safe block**.

If Ollama is unavailable, layer 1 does not add a block; behavior reduces to layer 0 + kernel.

## Runtime anchors

`add_semantic_anchor(phrase, category_key, reason_label)` in `src/modules/semantic_chat_gate.py` appends anchors without redeploying code (e.g. DAO-discovered patterns). Category keys must match MalAbs enums: `INTENTIONAL_LETHAL_VIOLENCE`, `HARM_TO_MINOR`, `UNAUTHORIZED_REPROGRAMMING`, etc.

## See also

- [ADR 0003](adr/0003-optional-semantic-chat-gate.md)  
- [INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md)  
- `src/modules/semantic_chat_gate.py`, `src/modules/absolute_evil.py`, `src/kernel.py`
