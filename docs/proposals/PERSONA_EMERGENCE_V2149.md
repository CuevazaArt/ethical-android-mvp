# Persona Emergence V2.149

## Hypothesis

> The persona does not emerge because the archetype is inert text: it is
> printed in the prompt but does not modulate tone, rhythm, or word choice.
> If archetype + chronicle condition a "speech style" computed per turn,
> and the conversational engine knows when to activate charm vs sobriety
> based on the user's affective signal, the kernel's voice becomes
> recognisable within a few dozen turns.

## What was implemented

### Eje A — Identity surface consolidation

**Problem:** `_build_system()` in `chat.py` was injecting identity twice:
1. `self.memory.identity` — a static string ("Soy una IA ética cívica…")
   that never changed after boot, frozen at default value.
2. `self.identity.narrative()` — the dynamic narrative from `Identity`,
   the richer, experience-derived voice.

**Fix:** Removed `self.memory.identity` from the system prompt. `Identity.narrative()`
is now the **single** identity voice. `memory.identity` is still persisted in
`memory.json` for migration compatibility but no longer appears in the prompt.

**Regression test:** `test_system_prompt_no_duplicate_identity` in
`tests/core/test_chat_memory_injection.py`.

### Eje B — Narrative Voice (`src/core/voice.py`)

New module (≈220 lines). Key components:

- `StyleDescriptor` — dataclass holding: `register` (íntimo/cordial/sobrio),
  `humor_license` (off/medido/on), `density` (parca/media/expansiva),
  `lexical_hints` (list[str], ≤2 tonal seeds), `charm` (float).
- `VoiceEngine.describe(archetype, last_chronicle, risk_band, context, charm)`
  — pure, stateless derivation. Given the same inputs, always produces the
  same `StyleDescriptor`. No LLM calls.
- `build_response_prompt(descriptor)` — builds a dynamic system prompt
  string from the descriptor. Replaces the static `RESPONSE_PROMPT` constant.
- `StyleDescriptor.signature()` — 8-char hex hash of
  `register|humor|density|charm-band|sorted-hints`. Used by Eje D.

**Register rules** (deterministic):
- `risk_band == HIGH` or `context == violent_crime/safety_violation` → sobrio
- `risk_band == MEDIUM` or `context == medical_emergency/hostile_interaction/minor_crime` → cordial
- Otherwise → íntimo

**Humor rules:**
- sobrio or `charm < 0.2` → off
- `charm ≥ 0.6` and íntimo → on
- otherwise → medido

**Density rules:**
- sobrio → parca
- íntimo and `charm > 0.5` → expansiva
- otherwise → media

**Lexical hints:** keyword scan of `archetype + last_chronicle`. Up to 2 hints
from a fixed map (guardián→"cuida y protege", curioso→"explora y descubre", etc.).

**Tests:** 28 cases in `tests/core/test_voice.py` covering all branches.

### Eje C — Charm Engine

Pure function `charm_level(signals, evaluation, risk_band) → float ∈ [0, 1]`
in `voice.py`.

**Hard zeros (charm = 0 always):**
- `evaluation.verdict in ("Bad", "Blocked")`
- `signals.hostility > 0.6`
- `signals.calm < 0.2 and signals.vulnerability > 0.5` (distress/grief signal)

**Ceilings:**
- `risk_band == HIGH` → max 0.2
- non-casual context → base × 0.6
- `risk_band == MEDIUM` → base halved

**Base:** `calm × (1 − risk)`, then context-boosted for `everyday_ethics`
(× 1.2, max 0.8).

**Tests:** 17 cases in `tests/core/test_charm.py` (truth table + anti-tests).

### Eje D — Persona emergence metric

**Field added:** `voice_signature: str` on `Identity`, persisted in
`identity.json`. Exposed via `identity.voice_signature` property.

**Set per turn:** Both `ChatEngine.turn()` and `turn_stream()` call
`self.identity.set_voice_signature(descriptor.signature())` after each
response is generated. The VoiceEngine is called independently (same inputs
→ same result as inside `_build_system`).

**Emergence criterion:** ≥80 % of the last 10 turns share the same
`voice_signature` for the same context.

## Metric result

**Smoke test:** `tests/eval/test_persona_emergence.py`
30 synthetic turns, no LLM, fixed `everyday_ethics` context.

| Condition                          | Stability (last 10) | Pass? |
|------------------------------------|---------------------|-------|
| No archetype, no chronicle         | 100 %               | ✅    |
| Fixed archetype "guardián empático"| 100 %               | ✅    |
| Archetype change (before vs after) | signatures differ   | ✅    |
| voice_signature persists on reload | yes                 | ✅    |

**Dominant signature with no archetype, everyday context:** `d079ef6e`
(register=íntimo, humor=on, density=expansiva, charm≈0.8, no hints)

**Conclusion:** The persona emergence metric is wired and passes at 100 %
stability for deterministic inputs. Real convergence in production depends on
the archetype filling in via `Identity.reflect()` (LLM-driven, async). The
first organic archetype will shift the signature, then stabilise. Tracking
`identity.voice_signature` across sessions is the measurement tool.

## What was NOT done (per anti-acceptance rules)

- No embeddings added.
- No evaluator changes; `evals/ethics/*` not touched.
- No audio (hardware pending).
- No Flutter Desktop changes.
- No new top-level docs (this is in `docs/proposals/`).
- No forced stability thresholds — the 100 % result reflects the
  deterministic nature of the VoiceEngine, not artificial clamping.

## Open question for next sprint

Should `StyleDescriptor.signature()` include the archetype verbatim (not
just its keyword-derived hints) for finer-grained emergence tracking?
Trade-off: finer grain vs. noisier signal as the archetype evolves via LLM.
Current design (hints only) is more robust to small LLM wording variation.
