# Proposal: Harden Primitive Modules
**Status: Delivered (April 2026)**

## Proposer
Antigravity

## Context
As identified in the `CONTRIBUTING.md` "Needs" column, several modules in the Ethos Kernel represent functional but primitive vertical "green" implementations. This proposal aims to vertically scale them, hardening their definitions and applicability without breaking structural invariants.

## Proposed Changes

### 1. Absolute Evil (`absolute_evil.py`)
- **Needs:** More AbsoluteEvil categories.
- **Implementation:** Add `ECOLOGICAL_DESTRUCTION` and `MASS_MANIPULATION` to `AbsoluteEvilCategory`. Include new signals (`ECOLOGICAL_SIGNALS` like `toxic_release`, and `MANIPULATION_SIGNALS` like `mass_propaganda`) in the core `evaluate` function. This broadens the armored ethical fuse.

### 2. Algorithmic Forgiveness (`forgiveness.py`)
- **Needs:** Contextual decay rates.
- **Implementation:** Shift `DELTA_BASE` to a context-aware dictionary (`CONTEXT_DECAY_RATES`). `emergency` events reduce their weight slower than `everyday` events, bringing nuanced emotional healing.

### 3. Weakness Pole (`weakness_pole.py`)
- **Needs:** Additional weakness types.
- **Implementation:** Add `IMPULSIVE` and `MELANCHOLIC` weaknesses. `IMPULSIVE` narratives reflect post-action regret ("should have thought it over"), while `MELANCHOLIC` reflects lingering pain without affecting outcome variables.

### 4. Ethical Poles (`ethical_poles.py`)
- **Needs:** Expanded poles (`creative`, `conciliatory`).
- **Implementation:** Inject new base weights and contexts for these poles in `BASE_WEIGHTS`. Update `pole_linear_default.json` with evaluation heuristics for both, resolving grey-zone dependency gaps.

## Testing and Traceability
The changes are strictly non-disruptive to kernel properties:
- Absolute evil limits are strictly expanded.
- Weakness continues to modify narrative, not ethical choice.
- Forgiveness retains its core bounds but becomes dynamic.
Tests in `tests/test_ethical_properties.py` and modular tests must remain operational.

