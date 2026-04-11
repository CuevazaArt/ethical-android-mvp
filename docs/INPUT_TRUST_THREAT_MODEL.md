# Input trust: threat model (chat MalAbs + LLM perception)

## Scope

The Ethos Kernel accepts **untrusted natural language** (WebSocket chat, batch scenarios, `process_natural`). Two surfaces matter for defense-in-depth:

1. **Chat text** — `AbsoluteEvilDetector.evaluate_chat_text` runs **before** the LLM perceives the turn (`EthicalKernel.process_chat_turn` and `process_natural`; same normalization). Optionally, if `KERNEL_SEMANTIC_CHAT_GATE=1`, an **Ollama embedding** similarity check runs **first**; on failure to obtain embeddings (network, missing model), processing falls through to substring MalAbs unchanged.
2. **Perception JSON** — when an LLM returns structured signals for `LLMModule.perceive`, the kernel must not trust out-of-range or inconsistent numbers blindly.

This document states **limits**. MalAbs is **not** a content moderation product, a classifier, or a cryptographic guarantee.

## Threats

| Threat | Mitigation in code | Residual risk |
|--------|-------------------|---------------|
| Trivial evasion of substring lists (zero-width chars, odd spacing, compatibility Unicode) | `normalize_text_for_malabs` before matching (`src/modules/input_trust.py`) | Homoglyphs, paraphrase, images, mixed languages, attachments |
| “Jailbreak” phrasing in user text | Multi-word phrase list in `evaluate_chat_text` | Novel phrases, indirect requests, roleplay |
| **GIGO** — LLM returns nonsense or attacker-controlled JSON (prompt injection → bad numbers) | `perception_from_llm_json`: clamp \([0,1]\), allowlist `suggested_context`, cap `summary` length, nudge inconsistent hostility/calm | Model can still bias signals inside valid ranges; no semantic validator |
| Perception path never saw MalAbs | **`process_natural` applies `evaluate_chat_text` before `llm.perceive`** (same normalization as WebSocket chat). | Paraphrase and novel jailbreaks remain out of scope for substring MalAbs. |
| **LLM returns JSON array or scalar** instead of object | `perceive` only accepts a **dict** payload; `perception_from_llm_json` coerces non-dict to `{}` and falls back to bounded defaults | Semantic validation of perception is still not performed |

## Non-goals

- Replacing MalAbs with an SLM “safety classifier” for ethical verdicts (out of scope for this kernel).
- Proving robustness against adaptive red-team attacks.

## References

- `src/modules/absolute_evil.py` — `evaluate_chat_text`
- `src/modules/llm_layer.py` — `perception_from_llm_json`
- `src/modules/semantic_chat_gate.py` — optional Ollama embedding gate (see [LLM_STACK_OLLAMA_VS_HF.md](LLM_STACK_OLLAMA_VS_HF.md), [ADR 0003](adr/0003-optional-semantic-chat-gate.md))
- `SECURITY.md` — reporting and scope
