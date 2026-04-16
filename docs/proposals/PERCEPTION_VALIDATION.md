# Perception JSON — validation and fallback

LLM output for `LLMModule.perceive` is untrusted. The pipeline uses **three layers** in `src/modules/perception_schema.py` and a **routing fix** in `src/modules/llm_layer.py`.

## 1. Per-field coercion + Pydantic

- Each scalar (`risk`, `urgency`, …) is passed through `_coerce_field`: non-numeric or non-finite values fall back to **contextual defaults** in `PERCEPTION_FIELD_DEFAULTS` (not a single global default for every field).
- Validated by `_LLMPerceptionPayload` (bounds [0, 1], types).
- If the whole model still fails validation, the payload resets to defaults while **preserving** the sanitized `summary` when possible.
- `suggested_context` must be a known label in `CONTEXTS`; otherwise `everyday_ethics`.

## 2. Cross-field coherence (`apply_signal_coherence`)

After Pydantic:

- **High hostility + high calm** — calm is nudged down (GIGO guard).
- **Very high risk + high calm** — calm is capped (physically inconsistent in this kernel’s model).

## 3. Fallback routing (`perceive`)

- The **LLM user** prompt may include `Prior conversation…` + `Current message` for model coherence.
- **Local heuristics** (`_perceive_local`) run only on the **current** `situation` string, not the full STM-prefixed block — so keywords from old turns do not skew signals for the present message.
- If JSON is missing or `perception_from_llm_json` raises, the kernel falls back to `_perceive_local(situation)` with the same rule.

## See also

- [`INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md)  
- `src/modules/perception_schema.py`, `src/modules/llm_layer.py`
