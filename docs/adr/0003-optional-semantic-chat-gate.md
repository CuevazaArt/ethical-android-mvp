# ADR 0003 — Optional semantic similarity gate for chat text (Hugging Face / embeddings)

**Status:** Accepted (April 2026)  
**Context:** Team note distinguishing **Ollama** (language generation) from **Hugging Face–style** small **embedding** models for stronger chat-text screening than substring lists alone. MalAbs today uses `evaluate_chat_text` with normalized substring matching ([INPUT_TRUST_THREAT_MODEL.md](../INPUT_TRUST_THREAT_MODEL.md)).

## Decision

1. **Document first:** [LLM_STACK_OLLAMA_VS_HF.md](../LLM_STACK_OLLAMA_VS_HF.md) records roles and limits.
2. **Implementation:** `src/modules/semantic_chat_gate.py` calls Ollama `POST /api/embeddings` when `KERNEL_SEMANTIC_CHAT_GATE` is on, compares cosine similarity to a small reference phrase list, then **`evaluate_chat_text`** applies substring MalAbs if the semantic layer does not block. **Default** (`KERNEL_SEMANTIC_CHAT_GATE` unset/off): unchanged behavior — no HTTP to Ollama for embeddings.
3. **sentence-transformers / torch:** not required for this path; optional future local HF stack remains a possible follow-up with an extra dependency group.
4. **CI policy:** core `pytest` + `requirements.txt` stays **without** torch/sentence-transformers; tests mock embeddings.

## Consequences

- **Positive:** “HF eyes”-style screening without conflating generation (Ollama chat) and classification (embeddings); degrades safely to substring MalAbs if Ollama is down.
- **Negative:** False positives/opacity if thresholds are wrong — mitigated by conservative default threshold, tests, and documented tuning env vars.

## Links

- [LLM_STACK_OLLAMA_VS_HF.md](../LLM_STACK_OLLAMA_VS_HF.md)  
- [0001 — packaging](0001-packaging-core-boundary.md)
