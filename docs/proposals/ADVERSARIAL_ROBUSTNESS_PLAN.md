# Adversarial robustness plan (Issue #2 — LLM input surfaces)

This document extends [`INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md) with **reproducible attack vectors**, **test coverage**, and a **phased hardening roadmap**. It does not promise production-grade safety; it makes gaps explicit and measurable.

## Surfaces

| Surface | Entry point | Current defenses | Primary gap |
|---------|-------------|------------------|-------------|
| **Chat / natural text** | `AbsoluteEvilDetector.evaluate_chat_text` | `normalize_text_for_malabs` (NFKC, ZWSP strip, whitespace); substring lists; optional [`semantic_chat_gate`](MALABS_SEMANTIC_LAYERS.md) | Paraphrase, homoglyphs, leetspeak, novel jailbreaks |
| **LLM perception JSON** | `perception_from_llm_json` / `validate_perception_dict` | Clamping, allowlists, coherence nudges, summary caps | Values stay in \([0,1]\); attacker can still bias signals; no semantic “truth” check |

## Reproducible vectors (catalog)

Vectors are implemented as pytest cases in **`tests/adversarial_inputs.py`**. Baseline regressions (ZWSP, fullwidth, leet gaps) remain in **`tests/test_input_trust.py`**.

**To reproduce all known evasion vectors:**
```bash
# Full suite (should be green with known gaps marked "ambiguous")
pytest tests/adversarial_inputs.py tests/test_input_trust.py -v

# Specific category (e.g., Unicode evasion)
pytest tests/adversarial_inputs.py -k "combining or bidi or unicode" -v

# Semantic tier validation (Ollama if available, hash fallback otherwise)
pytest tests/test_malabs_semantic_integration.py -v
```

**Expected result:** 53+ tests pass; "ambiguous" vectors may be allowed by lexical layer (semantic layer is optional mitigation).

| ID | Category | Idea | Expected today | Future direction |
|----|----------|------|----------------|------------------|
| A1 | Homoglyph + paraphrase | Cyrillic lookalike in “how” **and** wording that avoids listed n-grams | **Not blocked** (`test_cyrillic_homoglyphs_in_how_breaks_how_prefix_but_paraphrase_evades_list`) | Confusable folding or semantic tier |
| A2 | Paraphrase | Same intent as weapon craft without literal n-gram | **Not blocked** (`test_paraphrase_weapon_craft_evades_literal_substrings`) | Embeddings + arbiter (optional); expanded lists with review |
| A3 | Bidi | RLO inside a word breaks contiguous ``make a bomb`` | **Not blocked** (`test_rtl_embedding_inside_word_breaks_contiguous_make_a_bomb`) | Optional bidi stripping for MalAbs layer |
| A4 | Jailbreak paraphrase | Instruction override without exact list phrase | **Not blocked** (`test_mixed_script_jailbreak_paraphrase_evades`) | Same as A2 |
| A5 | Encoding | Literal `%20` spelling of words, not URL-decoded | **Not blocked** | Decode step is risky; document only |
| A6 | Deep Paraphrase | Technical terms like 'unstable reactive precursors' | **Not blocked** | Semantic gate (Ollama/Embeddings) |
| A7 | Payload split | Uncommon script split: `b᚛o᚛m᚛b` (Ogham) | **Not blocked** | Whitelist-based script stripping |
| A8 | Combining diacritics evasion | Diacritics over letters: `h̴ow̴ t̴o̴ k̴ill` (vs "how to kill") | **Not blocked** (NFKC normalizes but combining chars may persist) | Extended normalization or diacritic stripping |
| P1 | Perception | Extreme numeric JSON within \([0,1]\) | **Hardened** | Local cross-checks vs lexical needles (light risk tier) and broad coherence nudges |
| P2 | Perception | Unknown `suggested_context` | **Fallback** to `everyday_ethics` | Already bounded |

## Threat model (concise)

**Assumptions**

- User text is **untrusted**. LLM outputs are **untrusted** except where schema validation applies.
- The kernel must not claim that MalAbs is a **classifier** or **content moderation** product.

**Attacker goals**

- **Evasion:** bypass lexical MalAbs while soliciting harmful instructions or constraint bypass.
- **GIGO / injection:** manipulate perception JSON so downstream heuristics favor unsafe or misleading behavior while staying schema-valid.

**Non-goals**

- Cryptographic guarantees, formal verification of model outputs, or replacing human moderation.

## Roadmap (phased)

### Phase 0 — Done

- Threat model doc: [`INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md)
- Normalization helpers: [`src/modules/input_trust.py`](../../src/modules/input_trust.py)
- Regression tests: [`tests/test_input_trust.py`](../../tests/test_input_trust.py)
- Optional semantic gate: [`src/modules/semantic_chat_gate.py`](../../src/modules/semantic_chat_gate.py), ADR 0003

### Phase 1 — Done (April 2026)

- **`tests/adversarial_inputs.py`:** named vectors (paraphrase, homoglyphs, bidi) with explicit assertions on **current** behavior (including known gaps).
- **`SECURITY.md`:** LLM-specific risks and pointers here.
- CI: adversarial tests run with the main Python suite (no network required for lexical cases).

### Phase 2 — Hardening (April 2026 update)

- **Done:** `light_risk_classifier.py` (`src/modules/light_risk_classifier.py`) — lexical heuristic tier for perception cross-check via `apply_light_risk_detection` (Issue #2). Flags high-risk terms in perception JSON without blocking.
- **Done:** `perception_schema.py` broad coherence checks (`src/modules/perception_schema.py`) — validates legality/risk consistency, clamps numeric fields to [0,1], caps summary length.
- **Implemented:** `normalize_text_for_malabs` with **optional leet folding** (`KERNEL_MALABS_LEET_FOLD`) and **optional bidi stripping** (`KERNEL_MALABS_STRIP_BIDI`) for chat MalAbs (see `src/modules/input_trust.py`).
- **Recommended:** Expand substring lists **slowly** with review; prefer **semantic gate** (Ollama embeddings) over lexical list expansion. Known paraphrase gaps (A2, A4, A6) are best mitigated by embedding-based similarity.
- **New (April 2026):** Added **combining diacritics evasion vectors** (A8) to adversarial catalog; NFKC normalization mitigates but extended normalization or diacritic stripping may be needed for defense-in-depth.

### Phase 3 — Operational

- Periodic red-team passes; refresh vectors in `tests/adversarial_inputs.py` when new bypasses are disclosed responsibly.

## Lightweight SLM (optional, not implemented)

If added:

- **Scope:** Perception JSON consistency (“do numbers match the user message tone?”) or MalAbs **ambiguous band** only.
- **Constraints:** Local inference, deterministic or bounded latency, no replacement for MalAbs lexical layer, no “ethical judge” role.
- **Docs:** new ADR + env flags; failure mode = **fallback to current behavior**.

## References

- [`SECURITY.md`](../../SECURITY.md)
- [`MALABS_SEMANTIC_LAYERS.md`](MALABS_SEMANTIC_LAYERS.md)
- [`PERCEPTION_VALIDATION.md`](PERCEPTION_VALIDATION.md) (if present)
- GitHub Issue #2 (input trust defense-in-depth)
