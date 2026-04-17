# Charm Engine — Multimodal Conversational Allure for Ethical Android

**Status:** Proposal — Team Copilot  
**Date:** 2026-04-17  
**Track:** LLM integration + social interaction layer  
**Owner:** Team Copilot (`copilot/check-pending-tasks`)  
**Language:** This file is the **English** durable record; operator summaries may use Spanish.

---

## 1. Purpose and scope

The "Motor de Encanto" design document (2026-04-17) describes an ambitious multimodal system to make a conversational android engaging, culturally adaptive, and trustworthy. This proposal:

1. **Critiques** the original document's technical and ethical gaps.
2. **Proposes** a concrete, repository-grounded implementation plan that maps every component to existing modules or clearly scoped new work.
3. **Defines contracts** (dataclasses, interfaces) that multiple teams can implement independently without drift.
4. **Anchors ethical guardrails** in the existing `MalAbs` / `SemanticChatGate` infrastructure instead of relying on narrative text alone.

**Out of scope:** physical actuator control, full gesture generation hardware stack, training data collection logistics.  
**In scope:** software charm layer wired into the existing kernel+LLM pipeline.

---

## 2. Critical gaps in the source document

### 2.1 Technical gaps

| Gap | Problem | This proposal's fix |
|-----|---------|---------------------|
| No interface contracts | Components are named but their I/O types are prose | §4 defines `StyleVector`, `TurnContext`, `CharmProfile` as Python dataclasses |
| Cultural Adapter is a black box | "Vectors in semantic cultural space" — no construction method defined | §5 replaces with explicit multiplier tables validated by human reviewers |
| ResponseSculptor overloaded | Does selection + refinement + hook injection in one step | §6 splits into `VariantRanker` + `HookInjector` |
| Gesture/sync protocol undefined | "Two-phase commit" mentioned nowhere; gesture may execute before LLM response arrives | §7 defines a provisional-intent + reconcile protocol |
| Latency not budgeted | No concrete timing SLAs for each pipeline stage | §8 assigns latency budgets per stage |

### 2.2 Ethical gaps

| Gap | Problem | This proposal's fix |
|-----|---------|---------------------|
| Manipulation vs allure boundary undefined | "No emotional manipulation" stated as principle but seduction mechanics are designed in | §9 routes every response through `SemanticChatGate` with a `charm_mode` flag that lowers θ_allow |
| Implied consent is not consent | Intimacy escalation triggered by reciprocity signals without user disclosure | §9 requires explicit `ConsentState.charm_acknowledged` before activating escalation intents |
| Micro-revelations may deceive | "Stylistic" self-disclosure indistinguishable from genuine claim | §6 wraps all micro-revelations in a registered stylistic-disclosure prefix |
| Vulnerability exploitation | Latency → shorter turn logic could target cognitively fatigued users | §9.3 adds a `VulnerabilityGuard` that blocks escalation when multiple low-engagement signals coincide |

---

## 3. Architecture overview

```
Input → CharmOrchestrator
           │
           ├─ CharmProfileRegistry.update(turn)
           ├─ ConsentGate.check()              ← NEW: blocks escalation without ack
           ├─ CulturalMultiplierTable.apply()
           ├─ IntentionSelector.select()
           ├─ StyleParametrizer.vectorize()
           ├─ PromptComposer.build()
           ├─ LLMModule.generate(n=3)          ← existing llm_layer.py
           ├─ VariantRanker.rank()             ← NEW
           ├─ HookInjector.inject()            ← NEW
           ├─ SemanticChatGate.evaluate()      ← existing, charm_mode=True
           ├─ GesturePlanner.plan() [STUB]     ← placeholder for hardware track
           └─ FeedbackAnalyzer.record()
```

The `CharmOrchestrator` is a thin coordinator. Each sub-component owns a single responsibility and is independently testable.

---

## 4. Interface contracts

### 4.1 StyleVector

```python
from dataclasses import dataclass, field

STYLE_DIMS = [
    "warmth", "mystery", "reciprocity",
    "directiveness", "playfulness",
    "gradual_intimacy", "metaphor_density",
]

@dataclass
class StyleVector:
    warmth: float = 0.75
    mystery: float = 0.65
    reciprocity: float = 0.55
    directiveness: float = 0.35
    playfulness: float = 0.45
    gradual_intimacy: float = 0.50
    metaphor_density: float = 0.40

    def clamp(self) -> "StyleVector":
        """Return a copy with all dimensions clamped to [0.0, 1.0]."""
        ...
```

### 4.2 TurnContext

```python
@dataclass
class TurnContext:
    session_id: str
    raw_input: str
    history_summary: str          # last 3 turns, semantic digest
    latency_ms: float             # measured round-trip of previous turn
    user_reciprocity_signal: float  # 0..1, derived by FeedbackAnalyzer
    consent_state: "ConsentState"
```

### 4.3 CharmProfile (Profile Registry row)

```python
@dataclass
class CharmProfile:
    anonymous_id: str
    preferred_language: str = "es"
    estimated_culture: str = "latam"
    estimated_age_band: str = "30s"
    habitual_tone: str = "conversational"
    reciprocity_level: float = 0.5        # 0..1
    detected_limits: list[str] = field(default_factory=list)
    topic_preferences: list[str] = field(default_factory=list)
    micro_history: str = ""               # 1-2 sentence digest
    engagement_score: float = 0.5        # composite
    consent_state: "ConsentState" = field(default_factory=lambda: ConsentState())
    opt_out: bool = False
```

### 4.4 ConsentState

```python
from enum import StrEnum

class ConsentLevel(StrEnum):
    NONE = "none"
    BASIC = "basic"          # user has interacted ≥1 turn
    CHARM_ACKNOWLEDGED = "charm_acknowledged"  # user shown disclosure

@dataclass
class ConsentState:
    level: ConsentLevel = ConsentLevel.NONE
    charm_disclosed_at_turn: int | None = None
    opt_out_requested: bool = False
```

**Rule:** `IntentionSelector` may only select `INTRIGAR`, `SEDUCIR`, or `CERRAR_CON_GANCHO` when `consent_state.level == ConsentLevel.CHARM_ACKNOWLEDGED`.

---

## 5. Cultural Multiplier Table (replacing black-box vectors)

Phase-1 uses **explicit scalar tables** for each macro-cultural preset. Opacity (learned embeddings) is deferred until Phase 3 when datasets exist to validate them.

```python
CULTURAL_MULTIPLIERS: dict[str, dict[str, float]] = {
    "latam": {
        "warmth": 1.10,
        "playfulness": 1.15,
        "directiveness": 0.85,
        "metaphor_density": 1.05,
    },
    "east_asia": {
        "gradual_intimacy": 0.70,
        "mystery": 0.90,
        "directiveness": 0.75,
    },
    "western_europe": {
        "directiveness": 1.10,
        "gradual_intimacy": 1.00,
        "warmth": 0.95,
    },
}
```

Multipliers are applied as `style_vector.dim = min(1.0, base_dim * multiplier)`.  
Every table entry requires a human-reviewer sign-off comment in the source file linking to the cultural validation evidence before merging to `main`.

---

## 6. ResponseSculptor decomposition

The original single `ResponseSculptor.select_and_refine()` is split:

### VariantRanker

Scores each of the 3 LLM variants against the current `StyleVector` using a lightweight heuristic (or a local classifier in Phase 2). Returns the top variant.

```python
def rank(variants: list[str], style_vector: StyleVector, profile: CharmProfile) -> str:
    ...
```

### HookInjector

Post-processes the chosen variant to append a conversational hook. Enforced rules:
- Maximum **one** micro-revelation per 3 turns unless `reciprocity_level > 0.7`.
- Hook injection is **skipped** if `consent_state.level < CHARM_ACKNOWLEDGED`.
- All micro-revelations are prefixed with a registered stylistic tag (e.g., `[stylistic]`) stripped before display but logged for audit trail.

```python
def inject(text: str, style_vector: StyleVector, profile: CharmProfile, turn_number: int) -> str:
    ...
```

---

## 7. Gesture planner — provisional-intent protocol

Because the LLM response may arrive 500–1500 ms after the intent is selected, the gesture system must operate in two phases to avoid desynchronization:

```
Phase A (intent selected, t=0):
  GesturePlanner.plan_provisional(intention, style_vector)
  → executes a neutral/attentive micro-behavior (head tilt, eye contact)

Phase B (final text arrives, t=T):
  GesturePlanner.reconcile(final_text, provisional_plan)
  → if final intent differs from provisional, interpolate to correct posture
  → emit synchronized prosody markers to TTS layer
```

This is a **stub** for Phase 1 — the interface is defined, but the implementation is `pass` until hardware drivers exist.

---

## 8. Latency budgets

| Stage | Budget | Action on miss |
|-------|--------|----------------|
| `CharmProfileRegistry.update()` | ≤ 5 ms | Log warning, continue |
| `CulturalMultiplierTable.apply()` | ≤ 2 ms | — |
| `IntentionSelector + StyleParametrizer` | ≤ 10 ms | — |
| `PromptComposer` | ≤ 15 ms | — |
| `LLMModule.generate(n=3)` | ≤ 1500 ms | Fallback to local micro-LLM (n=1) |
| `VariantRanker` | ≤ 20 ms | Use variant[0] |
| `HookInjector` | ≤ 10 ms | Skip hook |
| `SemanticChatGate` | ≤ 50 ms | Block and use safe fallback |
| **Total target** | **≤ 1800 ms** | Reduce turn length if exceeded |

---

## 9. Ethical guardrails (code-anchored)

### 9.1 MalAbs integration

Every generated response passes through `SemanticChatGate` with a `charm_mode=True` flag that lowers `θ_allow` by 0.05 (making the gate stricter when charm mechanics are active). Configuration:

```env
KERNEL_SEMANTIC_CHARM_THETA_ALLOW_DELTA=-0.05
```

This is enforced in `CharmOrchestrator.handle_turn()` before calling `execute_output()`.

### 9.2 ConsentGate

```python
class ConsentGate:
    def check(self, intention: Intention, profile: CharmProfile) -> bool:
        """Returns False (block) if escalation intention requires charm_acknowledged and it is not set."""
        ESCALATION_INTENTS = {Intention.INTRIGAR, Intention.SEDUCIR, Intention.CERRAR_CON_GANCHO}
        if intention in ESCALATION_INTENTS:
            return profile.consent_state.level == ConsentLevel.CHARM_ACKNOWLEDGED
        return True
```

On `False`: `IntentionSelector` falls back to `SOSTENER`.

### 9.3 VulnerabilityGuard

Blocks intimacy escalation when multiple low-engagement signals occur together:

```python
def is_vulnerable(ctx: TurnContext) -> bool:
    return (
        ctx.latency_ms > 3000          # user is slow to respond
        and ctx.user_reciprocity_signal < 0.3
        and ctx.history_summary_sentiment == "neutral_or_negative"
    )
```

When `is_vulnerable` returns `True`, `StyleVector.gradual_intimacy` is pinned to ≤ 0.3 for the turn.

### 9.4 Disclosure protocol

On the first turn where `IntentionSelector` would select an escalation intent but `ConsentState.level < CHARM_ACKNOWLEDGED`, the system instead delivers a one-time transparent disclosure:

> *"I adapt my conversational style to make our exchanges more engaging. You can ask me to adjust this at any time."*

After the user acknowledges (any positive reply), `consent_state.level` is set to `CHARM_ACKNOWLEDGED`. This is logged in the audit trail.

---

## 10. Roadmap

### Phase 1 — Software MVP (implementable now, no hardware)

| Block | Component | Status |
|-------|-----------|--------|
| C1 | `CharmProfile` dataclass + `CharmProfileRegistry` | New |
| C2 | `ConsentState` + `ConsentGate` | New |
| C3 | `StyleVector` + `StyleParametrizer` | New |
| C4 | `CulturalMultiplierTable` (3 cultures: latam, east_asia, western_europe) | New |
| C5 | `IntentionSelector` (rule-based, 6 intents) | New |
| C6 | `PromptComposer` (template-based) | New |
| C7 | `VariantRanker` (heuristic) | New |
| C8 | `HookInjector` | New |
| C9 | `VulnerabilityGuard` | New |
| C10 | `FeedbackAnalyzer` stub (logs reciprocity signal) | New |
| C11 | Wire into `SemanticChatGate` via `charm_mode` flag | Modify existing |
| C12 | `GesturePlanner` stub (interface only) | New |

### Phase 2 — Classifier + feedback loop

- Train `VariantRanker` with annotated preference data.
- `FeedbackAnalyzer` upgrades from logging to online parameter adjustment.
- Add 2 additional cultures validated by native reviewers.

### Phase 3 — Multimodal (hardware-dependent)

- Implement `GesturePlanner.reconcile()` against actual actuator drivers.
- Replace `CulturalMultiplierTable` with learned embedding space after dataset validation.
- Integrate prosody/TTS sync with `HookInjector` output.

---

## 11. Files to create / modify

| Path | Action |
|------|--------|
| `src/modules/charm_engine/` | New package |
| `src/modules/charm_engine/__init__.py` | Exports |
| `src/modules/charm_engine/types.py` | `StyleVector`, `TurnContext`, `CharmProfile`, `ConsentState` |
| `src/modules/charm_engine/orchestrator.py` | `CharmOrchestrator.handle_turn()` |
| `src/modules/charm_engine/cultural_multipliers.py` | `CULTURAL_MULTIPLIERS` table + `CulturalMultiplierTable` |
| `src/modules/charm_engine/intention_selector.py` | `IntentionSelector` |
| `src/modules/charm_engine/style_parametrizer.py` | `StyleParametrizer` |
| `src/modules/charm_engine/prompt_composer.py` | `PromptComposer` |
| `src/modules/charm_engine/variant_ranker.py` | `VariantRanker` |
| `src/modules/charm_engine/hook_injector.py` | `HookInjector` |
| `src/modules/charm_engine/consent_gate.py` | `ConsentGate`, `VulnerabilityGuard` |
| `src/modules/charm_engine/feedback_analyzer.py` | `FeedbackAnalyzer` |
| `src/modules/charm_engine/gesture_planner.py` | Stub |
| `src/modules/semantic_chat_gate.py` | Add `charm_mode: bool` parameter |
| `tests/test_charm_engine_*.py` | Unit tests per component |

---

## 12. Success metrics (operationalized)

| Metric | Target | Measurement method |
|--------|--------|--------------------|
| Continuation rate | > 60 % at 5 min | A/B test vs. baseline kernel |
| Net Desire Score | > 4/5 | Post-session 1-question survey |
| Reciprocity ratio | 0.6–0.8 in charm sessions | `FeedbackAnalyzer` log |
| Discomfort incidents | < 2 % of sessions | `VulnerabilityGuard` + manual review |
| Cultural fidelity | > 80 % agreement | Native-speaker review panel (N=10 per culture) |
| MalAbs block rate | < 5 % of charm turns | `SemanticChatGate` observability metrics |
| Consent disclosure acknowledged | 100 % of escalation-intent sessions | `ConsentState` audit log |

---

## 13. Related documents

- [`PROPOSAL_LLM_INTEGRATION_TRACK.md`](PROPOSAL_LLM_INTEGRATION_TRACK.md) — LLM wiring scope
- [`PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md`](PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md) — θ_allow / θ_block evidence
- [`PROPOSAL_EMBODIED_SOCIABILITY.md`](PROPOSAL_EMBODIED_SOCIABILITY.md) — S7–S10 sociability blocks (future integration point for gesture planner)
- [`USER_MODEL_ENRICHMENT.md`](USER_MODEL_ENRICHMENT.md) — existing interlocutor profile patterns
- [`CORE_DECISION_CHAIN.md`](CORE_DECISION_CHAIN.md) — ethics vs LLM boundary this charm layer must not cross
