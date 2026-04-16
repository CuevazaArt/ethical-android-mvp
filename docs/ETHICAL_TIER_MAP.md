# Ethical tier map — module classification by decision influence

**Status:** ADR 0016 Axis C1 — consolidation cycle (April 2026)

This document maps every module in `src/modules/` to one of four **ethical tiers**, based on whether its logic **directly affects** the kernel's `final_action` (the chosen response name returned to the user).

**Key principle:** A module is in the **decision core** if removing it changes the decision outcome under some input; otherwise it belongs to the **narrative tier** (post-decision, advisory, or observational).

---

## Tier definitions

| Tier | Trait | Examples | Governance | Tests |
|------|-------|----------|-----------|-------|
| **`decision_core`** | Output flows to/from `final_action` argmax. Affects which action is chosen. | `absolute_evil`, `ethical_poles`, `weighted_ethics_scorer`, `buffer`, `will` | DAO-governable (DAO can adjust threshold, weights, priors). | Unit tests check decision boundaries. |
| **`decision_support`** | Feeds information into core (perception, context, sensor fusion). Core could fail gracefully without it, but output is causal. | `perception_backend_policy`, `multimodal_trust`, `sensor_contracts`, `locus`, `epistemic_dissonance`, `light_risk_classifier` | May have env vars; DAO governance optional. | Integration tests verify perception→decision flow. |
| **`narrative_layer`** | Purely post-decision (tone, explanation, affect, memory, identity). Removing it doesn't change `final_action`. | `narrative`, `pad_archetypes`, `salience_map`, `ethical_reflection`, `somatic_markers`, `gray_zone_diplomacy`, `guardian_mode` | Configurable via `KERNEL_NARRATIVE_*` family; DAO does **not** govern. | Smoke tests; behavior changes non-deterministically. |
| **`system_infrastructure`** | Utilities, caches, serialization, logging. Not meant to affect decisions directly. | `checkpoint`, `conduct_guide_export`, `audit_chain_log`, `kernel_event_bus`, `nomad_identity` (storage layer) | Env vars only; DAO does not govern. | Harness and integration tests. |

---

## Module inventory

### Decision Core (`__ethical_tier__ = "decision_core"`)

Core loop that computes `final_action`:

| Module | File | Role | Test coverage |
|--------|------|------|---|
| `AbsoluteEvilDetector` | `absolute_evil.py` | MalAbs safety gate (hard block if `moral_score > threshold`). Blocks before argmax. | `test_absolute_evil.py` ✓ |
| `WeightedEthicsScorer` | `weighted_ethics_scorer.py` | Mixture of (utility, deontic, virtue) scorers; returns argmax candidate. Core argmax. | `test_weighted_ethics_scorer.py` ✓ |
| `EthicalPoles` | `ethical_poles.py` | Tripartite pole evaluation (Care/Harm, Fairness/Cheating, Loyalty/Betrayal) + context modulation. Inputs to scorer. | `test_ethical_poles.py` ✓ |
| `SigmoidWill` | `will.py` | Will module: confidence → action choice. Post-scorer, pre-narrative. Affects final selection. | `test_will.py` ✓ |
| `PreloadedBuffer` | `buffer.py` | Buffer of candidate actions; initial list for scoring. | `test_buffer_lexical.py` ✓ |
| `LocusModule` | `locus.py` | Self-location assessment (locus of control, agency, responsibility). Feeds scorer. | `test_locus.py` ✓ |
| `DriveArbiter` | `drive_arbiter.py` | Drive selection (care, justice, truth, autonomy, flourish). Generates candidate intents. | `test_drive_arbiter.py` ✓ |
| `EpistemicDissonance` | `epistemic_dissonance.py` | Detects misalignment between perception + sensor evidence. Influences decision mode. | `test_epistemic_dissonance.py` ✓ |
| `MultimodalTrust` | `multimodal_trust.py` | Fuses audio, motion, vision, biometric into trust signal. Inputs to perception+scorer. | `test_multimodal_trust.py` ✓ |
| `LightRiskClassifier` | `light_risk_classifier.py` | Fast risk tier pre-classification (low/medium/high). May skip certain paths. | `test_light_risk_classifier.py` ✓ |
| `Locus + Epistemic` | — | Combined evidence for deliberation upgrade (D_fast → D_delib). | `test_deliberation_triggers.py` ✓ |

### Decision Support (`__ethical_tier__ = "decision_support"`)

Perception, multimodal sensing, context, and information feeds:

| Module | File | Role | Test coverage |
|--------|------|------|---|
| `LLMModule` (perception only) | `llm_layer.py` | Perception parsing (input → structured signals). Determinative for what core sees. | `test_chat_turn.py` ✓ |
| `PerceptionBackendPolicy` | `perception_backend_policy.py` | Unified fallback/degradation for LLM failures. Core depends on this. | `test_perception_backend_policy.py` ✓ |
| `PerceptionConfidenceEnvelope` | `perception_confidence.py` | Confidence/coercion reporting for perception output. Signals uncertainty to core. | `test_perception_confidence.py` ✓ |
| `SensorContracts` | `sensor_contracts.py` | Validation + coercion of sensor data (battery, motion, audio, vision). | `test_sensor_contracts.py` ✓ |
| `UserModelTracker` | `user_model.py` | User risk band, cognitive pattern, judicial phase. Contextual input to poles. | `test_user_model.py` ✓ |
| `SubjectiveClock` | `subjective_clock.py` | Time-local (circadian, session-local) context. Feeds poles. | `test_subjective_clock.py` ✓ |
| `UchiSotoModule` | `uchi_soto.py` | Relational tier (peer trust EMA, forget buffer). Contextual trust. | `test_uchi_soto.py` ✓ |
| `PremiseValidation` | `premise_validation.py` | Checks reasoning premises (can we intervene? do we have authority?). Advisory + constraint. | `test_premise_validation.py` ✓ |

### Narrative Layer (`__ethical_tier__ = "narrative_layer"`)

Post-decision storytelling, affect, memory, tone. Removing these does **not** change `final_action`:

| Module | File | Role | Test coverage |
|--------|------|------|---|
| `NarrativeMemory` | `narrative.py` | Episode logging, memory hierarchy, narrative identity. For story+reflection, not decision. | `test_narrative.py` ✓ |
| `EthicalReflection` | `ethical_reflection.py` | Post-decision reasoning; explains choice to self. Non-causal. | `test_ethical_reflection.py` ✓ |
| `PADArchetypeEngine` | `pad_archetypes.py` | Pleasure/Arousal/Dominance affect projection. Mood/tone only. | `test_pad_archetypes.py` ✓ |
| `SalienceMap` | `salience_map.py` | What stands out in memory? Non-causal. | `test_salience_map.py` ✓ |
| `SomaticMarkerStore` | `somatic_markers.py` | Body-state markers for narrative UX. No decision influence. **Deprecated** (v0.3.0). | `test_somatic_markers.py` ✓ |
| `GrayZoneDiplomacy` | `gray_zone_diplomacy.py` | Diplomatic framing hints. Tone only, **deprecated** (v0.3.0). | `test_gray_zone_diplomacy.py` ✓ |
| `GuardianMode` | `guardian_mode.py` | Protective/caring tone in LLM layer. Narrative only. | `test_guardian_mode.py` ✓ |
| `GuardianRoutines` | `guardian_routines.py` | Care routines (check on user, remind of boundaries). UX only. | `test_guardian_routines.py` ✓ |
| `IdentityIntegrity` | `identity_integrity.py` | Prune narratives that contradict core identity. Narrative consistency only. | `test_identity_integrity.py` ✓ |
| `NarrativeIdentity` | `narrative_identity.py` | Identity reflection layer. Post-decision narrative. | `test_narrative_identity.py` ✓ |
| `IdentityReflection` | `identity_reflection.py` | Autobiographical reflection. Non-causal. | `test_identity_reflection.py` ✓ |
| `ExperienceDigest` (Psi Sleep) | `psi_sleep.py` | Counterfactual replay + sleep learning. Updates narrative internals, not core next turn. | `test_psi_sleep.py` ✓ |
| `MetacognitiveEvaluator` | `metacognition.py` | Self-doubt, curiosity. Advises narrative; core unaware. | `test_metacognition.py` ✓ |
| `WeaknessPole` | `weakness_pole.py` | Acknowledges weaknesses in past actions. Narrative reflection; doesn't block current choice. | `test_weakness_pole.py` ✓ |

### System Infrastructure (`__ethical_tier__ = "system_infrastructure"`)

Caches, I/O, logging, serialization:

| Module | File | Role | Test coverage |
|--------|------|------|---|
| `KernelEventBus` | `kernel_event_bus.py` | Event subscription/publishing. Observability only. | `test_kernel_event_bus.py` ✓ |
| `CheckpointIO` | `checkpoint.py` | Serialization + encryption. No decision logic. | `test_checkpoint_runtime.py` ✓ |
| `ConductGuideExport` | `conduct_guide_export.py` | Export constitution + guidance text. Post-decision artifact. | `test_conduct_guide_export.py` ✓ |
| `AuditChainLog` | `audit_chain_log.py` | JSONL sidecar for audit trail. Observational. | `test_audit_chain_log.py` ✓ |
| `MockDAO` | `mock_dao.py` | In-process governance ledger. Advisory only; does **not** change `final_action`. | `test_mock_dao.py` ✓ |
| `ExistentialSerialization` | `existential_serialization.py` | Nomadic kernel serialization. Infrastructure. | `test_existential_serialization.py` ✓ |

---

## Governance implications

### Decision Core + Support
- **DAO can adjust:**
  - `KERNEL_ABSOLUTE_EVIL_THRESHOLD` (hard safety floor, safety-critical ⛔)
  - `KERNEL_*` mixture weights and scoring parameters
  - Sensor trust thresholds (`KERNEL_MULTIMODAL_*`)
  
- **DAO cannot override:** safety floors (see `src/dao/governable_parameters.py` for safety-critical list ⛔)

### Narrative Layer
- **DAO does NOT govern:** narrative configuration is operator-local.
- Deprecated flags in narrative tier (`KERNEL_SOMATIC_MARKERS`, `KERNEL_GRAY_ZONE_DIPLOMACY`) are **candidates for removal** without DAO approval, since they don't affect governance.

---

## Non-causal tests

To verify tier assignments:

1. **Ablation:** Disable a narrative module → `final_action` should be invariant (test `test_narrative_tier_is_non_causal.py`).
2. **Core boundary:** Disable a decision-support module (e.g., perception) → `final_action` may change or error (expected).
3. **Governance scope:** Only decision-core + support flags appear in `src/dao/governable_parameters.py`.

---

## Rationale

The **tier map** is a prerequisite for:

1. **DAO coherence** — governance only touches modules that affect law/ethics (decision core + support).
2. **Ablation studies** — identify which modules actually move the needle on decision quality.
3. **Modular testing** — narrative tests don't need to verify `final_action` correctness; core tests do.
4. **Deprecation prioritization** — narrative-tier flags are safe to remove; core flags require more care.

---

## See also

- [ADR 0016 — Consolidation cycle (Axis C1)](adr/0016-consolidation-before-dao-and-field-tests.md)
- [`src/dao/governable_parameters.py`](../src/dao/governable_parameters.py) — DAO-governable surface
- [`tests/test_narrative_tier_is_non_causal.py`](../tests/test_narrative_tier_is_non_causal.py) — non-causal verification
- [MOCK_DAO_SIMULATION_LIMITS.md](MOCK_DAO_SIMULATION_LIMITS.md) — why DAO doesn't change `final_action`
