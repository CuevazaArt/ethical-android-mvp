# Ollama vs Hugging Face — role in Ethos Kernel

Team **synthesis** document aligned with the code. It does not replace [INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md) or [CORE_DECISION_CHAIN.md](CORE_DECISION_CHAIN.md).

---

## Comparison (summary)

| Aspect | Hugging Face | Ollama |
|--------|----------------|--------|
| Nature | Platform + ecosystem (e.g. `transformers`, models on the Hub) | Local runtime with HTTP API (`localhost:11434` typical) |
| AI scope | Very broad (text, vision, audio, embeddings, …) | Mostly LLMs (text) and some multimodal models via Ollama |
| Memory / hardware | “Full” models are often heavy (GPU helps by model) | **Quantized** models (e.g. GGUF), reasonable on PC/Mac without a datacenter |
| Typical integration | Python (`transformers`, `sentence-transformers`, …) | HTTP client: already integrated here via `OllamaCompletion` |

---

## How this applies to Ethos Kernel (two distinct layers)

### A) Ollama — **language** layer (supported)

**Role:** map text ↔ signals (`LLMModule.perceive`), verbal reply, rich narrative, optional monologue — **without** choosing the final ethical action (the kernel does).

**In code:** `src/modules/llm_backends.py` (`OllamaCompletion`), mode resolution with `LLM_MODE=ollama` / `USE_LOCAL_LLM`. See README LLM / chat section.

**Why it fits:** **local** execution, no paid API required, good for demos and privacy.

### B) Hugging Face / embeddings — **optional reinforcement for the chat gate** (future-facing design)

**Proposed role (not a core substitute):** complement the **phrase lists** in `AbsoluteEvilDetector.evaluate_chat_text` with a **semantic similarity** signal against reference phrases (e.g. risk categories), in **milliseconds** without generating long text.

**In code today:** MalAbs chat remains **substring + normalization** (`input_trust.normalize_text_for_malabs`). See [INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md) — paraphrase and indirect language remain residual risk.

**Why HF fits conceptually:** small **embedding** models via `sentence-transformers` (or another light stack) suit **similarity classification**, not “thinking through” episode ethics (that stays kernel + structural MalAbs on actions).

**Explicit limits:**

- Does not replace MalAbs veto on **actions** (`CandidateAction` + signals).
- Not “infallible moderation”: thresholds, embedding-model bias, and adaptive attacks need tests and governance (see [ADR 0003](../adr/0003-optional-semantic-chat-gate.md)).

---

## Deliverable value now vs next PR

| Deliverable | Status |
|-------------|--------|
| Ollama as perception / communication backend | **Implemented** — enable with env vars documented in README |
| Code path for optional semantic gate | **Implemented (Ollama embeddings)** — `src/modules/semantic_chat_gate.py`; enable with `KERNEL_SEMANTIC_CHAT_GATE=1` |
| HF deps (`sentence-transformers`, etc.) | **Not** in CI — uses Ollama HTTP API (`/api/embeddings`), same stack as the LLM |
| Integration in `evaluate_chat_text` | **Done** — embedding chain → substring; thresholds via `KERNEL_SEMANTIC_CHAT_SIM_THRESHOLD` |

---

## Links

- [ADR 0003 — Semantic chat gate (optional)](../adr/0003-optional-semantic-chat-gate.md)  
- `src/modules/llm_backends.py`, `src/modules/llm_layer.py`  
- `src/modules/absolute_evil.py` — `evaluate_chat_text`  
- [PROPOSAL_EXPANDED_CAPABILITY_V9.md](PROPOSAL_EXPANDED_CAPABILITY_V9.md) (v9 context)
