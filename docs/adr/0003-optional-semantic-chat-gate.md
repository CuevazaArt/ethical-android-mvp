# ADR 0003 — Optional semantic similarity gate for chat text (Hugging Face / embeddings)

**Status:** Accepted (April 2026)  
**Context:** Team note distinguishing **Ollama** (language generation) from **Hugging Face–style** small **embedding** models for stronger chat-text screening than substring lists alone. MalAbs chat uses `evaluate_chat_text` with normalized substring matching ([INPUT_TRUST_THREAT_MODEL.md](../proposals/INPUT_TRUST_THREAT_MODEL.md)).

## Decision

1. **Document first:** [LLM_STACK_OLLAMA_VS_HF.md](../proposals/LLM_STACK_OLLAMA_VS_HF.md) records roles and limits; [MALABS_SEMANTIC_LAYERS.md](../proposals/MALABS_SEMANTIC_LAYERS.md) describes the layered pipeline.

2. **Layered pipeline (implemented):**
   - **Layer 0 — lexical** always runs first (`_evaluate_chat_text_lexical` in `absolute_evil.py`).
   - **Layer 1 — embeddings** (Ollama `/api/embeddings`) runs only if lexical did not block and `KERNEL_SEMANTIC_CHAT_GATE` is on. Two thresholds **θ_block** and **θ_allow** define block / allow / ambiguous bands.
   - **Layer 2 — LLM arbiter** for the ambiguous band only, when `KERNEL_SEMANTIC_CHAT_LLM_ARBITER=1` and `EthicalKernel` passes `llm._text_backend` into `evaluate_chat_text`. JSON response; **fail-safe block** on any failure.
   - **Runtime anchors:** `add_semantic_anchor()` registers extra reference phrases without redeploying.

3. **sentence-transformers / torch:** not required; optional future local HF stack remains a follow-up.

4. **CI policy:** core `pytest` mocks embeddings / LLM; no torch in default `requirements.txt`.

## Consequences

- **Positive:** Lexical speed for obvious cases; embeddings for paraphrase; LLM rarely invoked; Ollama-only deps align with the rest of the stack.
- **Negative:** Threshold tuning and ambiguous-band fail-safe blocks require operator care — documented env vars and [MALABS_SEMANTIC_LAYERS.md](../proposals/MALABS_SEMANTIC_LAYERS.md).

## Amendment (April 2026)

**Defaults:** `KERNEL_SEMANTIC_CHAT_GATE` and `KERNEL_SEMANTIC_EMBED_HASH_FALLBACK` default to **on** when unset (deterministic hash vectors keep the cosine tier active without Ollama; weaker than neural embeddings). Pytest sets lexical-only MalAbs via `tests/conftest.py` unless a test enables semantic. See [MALABS_SEMANTIC_LAYERS.md](../proposals/MALABS_SEMANTIC_LAYERS.md).

## Links

- [MALABS_SEMANTIC_LAYERS.md](../proposals/MALABS_SEMANTIC_LAYERS.md)  
- [LLM_STACK_OLLAMA_VS_HF.md](../proposals/LLM_STACK_OLLAMA_VS_HF.md)  
- [0001 — packaging](0001-packaging-core-boundary.md)
