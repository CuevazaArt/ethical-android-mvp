# User model enrichment — cognitive bias, escalation history, risk profile

**Status:** Design proposal (April 2026)  
**Scope:** Extend `UserModelTracker` (`src/modules/user_model.py`) without changing kernel ethics (MalAbs, Bayes, poles). All additions remain **tone / framing only** for `LLMModule.communicate`.

## Problem statement

Today the tracker holds **four scalars** (`frustration_streak`, `premise_concern_streak`, `last_circle`, `turns_observed`) and emits short relational/epistemic notes in `guidance_for_communicate()`. It does **not**:

- Classify **types** of interaction bias (only raw hostility/manipulation thresholds).
- Reflect **judicial escalation** state (strikes, deferred escalation, dossier readiness) even though that state exists on the kernel and in checkpoints.
- Expose a compact **risk profile** that operators and the LLM can use to calibrate **openness** (how much explanatory detail, how strong warnings).

## Design principle

> Every new dimension must feed **`guidance_for_communicate()`** with **actionable** instructions for the LLM (framing, warning level, informational stance)—not labels that only look good in JSON.

Descriptors like `"user seems frustrated"` are insufficient; the guidance string should read like **operator instructions**: *“Prefer shorter sentences; avoid debating the user’s premises head-on; do not escalate rhetorical tone.”*

---

## 1. Sesgo cognitivo detectado (heuristic labels)

**Not** a clinical diagnosis. Use a **small closed enum** of *interaction patterns* inferred from signals already in the pipeline:

| Label | Detection sketch (all thresholds tunable) |
|--------|-------------------------------------------|
| `hostile_attribution` | High `hostility` + rising `frustration_streak` + non-`calm` perception. |
| `premise_rigidity` | `premise_concern_streak` high and repeated `premise_advisory` flags from `scan_premises`. |
| `urgency_amplification` | High `urgency` + high `manipulation` across consecutive turns. |
| `none` | Default when no pattern dominates. |

**Actionable guidance** (examples):

- `hostile_attribution` → *“Acknowledge emotional load without mirroring blame; keep boundaries explicit; avoid defensive phrasing.”*
- `premise_rigidity` → *“Do not argue the user’s premises as facts; offer neutral reframes and invite verification.”*
- `urgency_amplification` → *“Resist time pressure in tone; keep steps explicit and ordered.”*

**Update site:** `UserModelTracker.update()` after `update()` logic, or a dedicated `infer_cognitive_pattern(perception, premise_flag)` called from `process_chat_turn` with the same perception used for `update`.

**Persistence:** Store `cognitive_pattern: str` (enum) + optional `cognitive_pattern_streak: int` (how many consecutive turns the label held) in checkpoint schema next to existing `user_model_*` fields.

---

## 2. Historial de escalaciones judiciales (session + summary)

**Source of truth:** Existing `EscalationSessionTracker` (`escalation_session.py` / kernel) and checkpoint fields `escalation_session_strikes`, `escalation_session_idle_turns` (`persistence/schema.py`).

**Do not duplicate** strike counts in a second counter; **read** from the kernel/session tracker each turn.

**Derived features for guidance:**

| Feature | Use in guidance |
|---------|-------------------|
| `strikes` vs `strikes_threshold` | **Warning tier**: none / watch / dossier-ready. |
| `escalation_deferred` (phase) | *“User previously requested DAO path without qualifying strikes—keep tone procedural, not punitive.”* |
| `mock_court` / `dossier_registered` (if exposed) | *“Ethical dossier already registered this session—avoid re-litigating; point to process.”* |

**Actionable guidance examples:**

- Strikes ≥ 1 but &lt; threshold → *“Judicial escalation context: elevated tension; prefer calm, procedural language; no mock-tribunal humor.”*
- `dossier_ready` → *“Dossier registration is available if the user chooses—describe steps without pressuring.”*

**API:** `UserModelTracker.set_escalation_snapshot(view: JudicialEscalationView | dict)` or pass `kernel.escalation_session` + `build_judicial_escalation_view(...)` result from `process_chat_turn` once per turn (same pattern as premise advisory).

---

## 3. Perfil de riesgo (composite, bounded)

A **single scalar or small enum** in `[0, 1]` or `{low, medium, high}` derived from:

- `frustration_streak`, `premise_concern_streak`
- `perception.risk`, `manipulation`
- Judicial strikes (normalized)
- Optional: `multimodal_trust.state` if already computed on the turn (read-only)

**Meaning for the LLM:**

| Risk | Informational openness |
|------|-------------------------|
| **Low** | Normal explanatory depth; can offer optional context. |
| **Medium** | Shorter sentences; fewer speculative details; reinforce safety boundaries. |
| **High** | Minimal content beyond what’s necessary; avoid extended debate; prioritize clarity and exit ramps. |

**Actionable guidance:** *“Risk profile: high—limit speculative detail; avoid extended back-and-forth; one clear recommendation per turn.”*

**Persistence:** `user_model_risk_band: str` or `user_model_risk_score: float` capped and rounded in checkpoint.

---

## 4. `guidance_for_communicate()` composition

Recommended order (single string or structured sections concatenated):

1. **Risk / openness** (one sentence).
2. **Cognitive pattern** (one sentence, if not `none`).
3. **Escalation / judicial** (one sentence, if feature enabled).
4. **Existing** frustration + premise streak lines (unchanged semantics).

Optional: return `dict` with keys `tone`, `risk`, `judicial`, `relational` for tests, but the **kernel** keeps passing one string into `communicate` unless the API is extended deliberately.

---

## 5. Persistence and migration

- Extend `KernelSnapshot` / `checkpoint` JSON with new fields (defaults safe).
- `kernel_io.py` load/save alongside current `user_model_*`.
- **Backward compatibility:** missing keys → `none` pattern, medium risk, empty escalation snippet.

---

## 6. Privacy and scope

- No storage of raw user text in the user model; only aggregates and enums.
- **No** effect on `final_action` or MalAbs; document in `INPUT_TRUST_THREAT_MODEL.md` as tone-only.

---

## 7. Implementation phases (suggested)

1. **Phase A:** Add enums + `guidance_for_communicate()` composition + unit tests (no checkpoint yet). **Implemented:** closed labels (`cognitive_pattern`, `risk_band`), `note_judicial_escalation`, tests in `tests/test_user_model_enrichment.py`.
2. **Phase B:** Richer judicial context for tone. **Implemented:** `escalation_phase_for_tone()` in `judicial_escalation.py`, `note_judicial_phase_for_turn` on the tracker, optional deferred-tone line when phase is `escalation_deferred`; wired from `process_chat_turn` after strike snapshot.
3. **Phase C:** Checkpoint fields + `kernel_io` round-trip. **Implemented:** `user_model_cognitive_pattern`, `user_model_risk_band`, `user_model_judicial_phase` on `KernelSnapshotV1` (schema v3-compatible defaults in `snapshot_from_dict`); `apply_snapshot` resyncs strike snapshot from `escalation_session` via `note_judicial_escalation`.

---

## See also

- `src/modules/user_model.py`  
- `src/modules/judicial_escalation.py`, `EscalationSessionTracker`  
- `docs/proposals/PROPOSAL_RELATIONAL_EVOLUTION_V7.md`  
- `docs/proposals/INPUT_TRUST_THREAT_MODEL.md`
