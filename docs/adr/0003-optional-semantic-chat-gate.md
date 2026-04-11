# ADR 0003 — Optional semantic similarity gate for chat text (Hugging Face / embeddings)

**Status:** Proposed (April 2026)  
**Context:** Team note distinguishing **Ollama** (language generation) from **Hugging Face–style** small **embedding** models for stronger chat-text screening than substring lists alone. MalAbs today uses `evaluate_chat_text` with normalized substring matching ([INPUT_TRUST_THREAT_MODEL.md](../INPUT_TRUST_THREAT_MODEL.md)).

## Decision

1. **Document first:** [LLM_STACK_OLLAMA_VS_HF.md](../LLM_STACK_OLLAMA_VS_HF.md) records roles and limits.
2. **Extension point in code:** `src/modules/semantic_chat_gate.py` exposes `evaluate_semantic_chat_gate` → `None` until implemented; **no** change to default behavior when `KERNEL_SEMANTIC_CHAT_GATE` is unset/off.
3. **Future implementation (out of scope for this ADR):** optional `sentence-transformers` (or equivalent) loaded only when env + explicit dependency install; compare user text embeddings to a **small, auditable** set of reference phrases per category; combine with existing substring MalAbs as **defense-in-depth**, not replacement for kernel ethics.
4. **CI policy:** core `pytest` + `requirements.txt` stays **without** torch/sentence-transformers until a follow-up PR adds an **optional** extra in `pyproject.toml` and a dedicated job or marker.

## Consequences

- **Positive:** Clear place for “HF eyes” without conflating generation (Ollama) and classification (embeddings).
- **Negative:** Risk of false positives/opacity if thresholds are not documented — mitigated by tests and conservative defaults when implemented.

## Links

- [LLM_STACK_OLLAMA_VS_HF.md](../LLM_STACK_OLLAMA_VS_HF.md)  
- [0001 — packaging](0001-packaging-core-boundary.md)
