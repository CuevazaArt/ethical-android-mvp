# Ollama vs Hugging Face — role in Ethos Kernel

Team **synthesis document** + alignment with code. Does not replace [INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md) or [CORE_DECISION_CHAIN.md](CORE_DECISION_CHAIN.md).

---

## Comparison table (summary)

| Feature | Hugging Face | Ollama |
|---------|-------------|--------|
| Nature | Platform + ecosystem (e.g., `transformers`, models on Hub) | Local runtime with HTTP API (`localhost:11434` typically) |
| AI types | Very broad (text, vision, audio, embeddings, etc.) | Mainly LLMs (text) and some multimodal models via Ollama |
| Memory / hardware | "Full" models tend to be heavy (GPU helpful depending on model) | **Quantized** models (e.g., GGUF), reasonable on PC/Mac without a datacenter |
| Typical integration | Python code (`transformers`, `sentence-transformers`, etc.) | HTTP client: already integrated in this repo via `OllamaCompletion` |

---

## How it applies to Ethos Kernel (two distinct layers)

### A) Ollama — **language** layer (already supported)

**Role:** translate text ↔ signals (`LLMModule.perceive`), generate verbal response, rich narrative, optional monologue — **without** deciding the final ethical action (the kernel does that).

**In code:** `src/modules/llm_backends.py` (`OllamaCompletion`), mode resolution with `LLM_MODE=ollama` / `USE_LOCAL_LLM`. See README LLM / chat section.

**Why it fits:** **local** execution, no mandatory paid API, useful for demos and privacy.

### B) Hugging Face / embeddings — **optional chat gate reinforcement** (future design)

**Proposed role (not a core substitute):** complement the **phrase lists** in `AbsoluteEvilDetector.evaluate_chat_text` with a **semantic similarity** signal against reference phrases (e.g., risk categories), in **milliseconds** and without generating long text.

**In code today:** MalAbs chat remains **substring + normalization** (`input_trust.normalize_text_for_malabs`). See [INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md) — paraphrase and indirect language remain a residual risk.

**Why HF fits conceptually:** small **embedding** models via `sentence-transformers` (or another lightweight stack) are suitable for **similarity-based classification**, not for "reasoning" about episode ethics (that remains kernel + structural MalAbs on actions).

**Explicit limits:**

- Does not replace the MalAbs veto on **actions** (`CandidateAction` + signals).
- Not "infallible moderation": thresholds, embedding model biases, and adaptive attacks require tests and governance (see [ADR 0003](adr/0003-optional-semantic-chat-gate.md)).

---

## Implementable value now vs next PR

| Deliverable | Status |
|-------------|--------|
| Ollama as perception/communication backend | **Implemented** — activate with environment variables documented in README |
| Code bridge for optional semantic gate | **Implemented (Ollama embeddings)** — `src/modules/semantic_chat_gate.py`; activate with `KERNEL_SEMANTIC_CHAT_GATE=1` |
| HF dependencies (`sentence-transformers`, etc.) | **Not** in CI — Ollama HTTP API (`/api/embeddings`) is used instead, same base as the LLM |
| Integration in `evaluate_chat_text` | **Done** — embedding → substring chain; thresholds via `KERNEL_SEMANTIC_CHAT_SIM_THRESHOLD` |

---

## Links

- [ADR 0003 — Semantic chat gate (optional, future)](adr/0003-optional-semantic-chat-gate.md)
- `src/modules/llm_backends.py`, `src/modules/llm_layer.py`
- `src/modules/absolute_evil.py` — `evaluate_chat_text`
- [PROPOSAL_EXPANDED_CAPABILITY_V9.md](PROPOSAL_EXPANDED_CAPABILITY_V9.md) (v9 context)
