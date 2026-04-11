# Input trust: threat model (chat MalAbs + LLM perception)

## Scope

The Ethos Kernel accepts **untrusted natural language** (WebSocket chat, batch scenarios, `process_natural`). Two surfaces matter for defense-in-depth:

1. **Chat text** — `AbsoluteEvilDetector.evaluate_chat_text` runs **before** the LLM perceives the turn (`EthicalKernel.process_chat_turn` and `process_natural`; same normalization). **Order:** **lexical** substring MalAbs first; if `KERNEL_SEMANTIC_CHAT_GATE=1` and lexical did not block, **Ollama embeddings** (θ_block / θ_allow) and optionally an **LLM arbiter** for the ambiguous band — see [`MALABS_SEMANTIC_LAYERS.md`](MALABS_SEMANTIC_LAYERS.md). If Ollama is unavailable, only lexical applies.
2. **Perception JSON** — when an LLM returns structured signals for `LLMModule.perceive`, the kernel must not trust out-of-range or inconsistent numbers blindly. Validation pipeline: **Pydantic + per-field defaults + cross-field coherence**; local fallback uses the **current message only** for keyword heuristics (`docs/proposals/PERCEPTION_VALIDATION.md`).

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

## Advisory telemetry (user model, judicial tone, homeostasis)

Several WebSocket JSON fields are **UX / LLM tone hints** or **operator visibility** — they are **not** security boundaries and **do not** bypass MalAbs, the buffer, or Bayesian action selection.

| Field family | Role | Trust note |
|--------------|------|------------|
| `user_model` | Heuristic labels (`cognitive_pattern`, `risk_band`, `judicial_phase`, streaks) and checkpoint-round-trip aggregates | **Not** a clinical or forensic assessment; labels are rule-based from perception + session state. |
| `judicial_escalation` | Session strikes, dossier readiness, optional mock tribunal output | Advisory; DAO/mock flows are **off-chain demo** unless integrated elsewhere. |
| `affective_homeostasis`, `experience_digest`, `monologue` | Narrative / PAD-style color | Same: tone and audit narrative, not policy veto. |

For field lists and persistence keys, see [USER_MODEL_ENRICHMENT.md](USER_MODEL_ENRICHMENT.md) and the WebSocket section in [README](README.md).

## References

- `src/modules/absolute_evil.py` — `evaluate_chat_text`
- `src/modules/llm_layer.py` — `perception_from_llm_json`
- `src/modules/semantic_chat_gate.py` — optional Ollama embedding gate + LLM arbiter + `add_semantic_anchor` (see [MALABS_SEMANTIC_LAYERS.md](MALABS_SEMANTIC_LAYERS.md), [LLM_STACK_OLLAMA_VS_HF.md](LLM_STACK_OLLAMA_VS_HF.md), [ADR 0003](adr/0003-optional-semantic-chat-gate.md))
- `SECURITY.md` — reporting and scope
