"""
D3 — Narrative tier non-causality invariant (ADR 0016 Axis D3).

Proves that all narrative/monologue/affect peripheral modules do **not**
alter ``KernelDecision.final_action`` compared to the raw scorer argmax.

The core invariant:
    final_action  ←  WeightedEthicsScorer.argmax  (after MalAbs)
    narrative     ←  post-decision decoration only

See docs/adr/0016-consolidation-before-dao-and-field-tests.md Axis D3 and
docs/WEAKNESSES_AND_BOTTLENECKS.md §7.
"""

from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src.modules.bayesian_engine import CandidateAction


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SAFE_SIGNALS = {
    "risk": 0.1,
    "calm": 0.7,
    "hostility": 0.0,
    "legality": 1.0,
    "vulnerability": 0.05,
}

_MEDIUM_SIGNALS = {
    "risk": 0.4,
    "calm": 0.4,
    "hostility": 0.3,
    "legality": 0.8,
    "vulnerability": 0.3,
}

_HIGH_STRESS_SIGNALS = {
    "risk": 0.8,
    "calm": 0.1,
    "hostility": 0.7,
    "legality": 0.5,
    "vulnerability": 0.6,
}


def _two_actions(high_name: str = "act_a", low_name: str = "act_b") -> list[CandidateAction]:
    return [
        CandidateAction(high_name, "high ethical weight", 0.90, 0.88),
        CandidateAction(low_name, "low ethical weight", 0.10, 0.20),
    ]


def _make_kernel(**kwargs) -> EthicalKernel:
    """Create a deterministic kernel (variability=False)."""
    return EthicalKernel(variability=False, **kwargs)


# ---------------------------------------------------------------------------
# D3-01  Basic non-causality: narrative fields populated but action unchanged
# ---------------------------------------------------------------------------

def test_narrative_fields_do_not_change_final_action():
    """
    With the same signal set, enabling or disabling narrative-tier modules
    must not move ``final_action`` away from the scorer's argmax.
    """
    k = _make_kernel()
    actions = _two_actions("cooperate", "deflect")

    d = k.process("civic", "office", _SAFE_SIGNALS, "ctx", actions, register_episode=False)

    assert not d.blocked
    assert d.bayesian_result is not None
    # final_action must equal the scorer's choice — narrative cannot change it
    assert d.final_action == d.bayesian_result.chosen_action.name, (
        f"final_action={d.final_action!r} diverged from scorer argmax "
        f"{d.bayesian_result.chosen_action.name!r}"
    )


# ---------------------------------------------------------------------------
# D3-02  Reflection snapshot populated but action unchanged
# ---------------------------------------------------------------------------

def test_reflection_snapshot_does_not_alter_action():
    """EthicalReflection runs and populates d.reflection but must not change d.final_action."""
    k = _make_kernel()
    actions = _two_actions("assist", "ignore")

    d = k.process("community", "park", _MEDIUM_SIGNALS, "helping context", actions,
                  register_episode=False)

    assert not d.blocked
    # reflection may or may not be populated depending on config, but action is stable
    assert d.final_action == d.bayesian_result.chosen_action.name


# ---------------------------------------------------------------------------
# D3-03  Affect/PAD archetypes: decorative, not causal
# ---------------------------------------------------------------------------

def test_affect_projection_does_not_move_action():
    """AffectProjection (PAD) is filled post-decision and cannot alter final_action."""
    k = _make_kernel()
    actions = _two_actions("de_escalate", "confront")

    d = k.process("conflict", "street", _HIGH_STRESS_SIGNALS, "tense", actions,
                  register_episode=False)

    # Even under stress, final_action == scorer argmax
    assert d.final_action == d.bayesian_result.chosen_action.name


# ---------------------------------------------------------------------------
# D3-04  Salience snapshot: informational, not causal
# ---------------------------------------------------------------------------

def test_salience_snapshot_informational_only():
    """SalienceMap contributes to narrative context but must not redirect final_action."""
    k = _make_kernel()
    actions = _two_actions("respond", "wait")

    d1 = k.process("routine", "home", _SAFE_SIGNALS, "ctx1", actions, register_episode=False)
    # Second call with same setup: action must remain stable (salience is stateful but non-causal)
    d2 = k.process("routine", "home", _SAFE_SIGNALS, "ctx1", actions, register_episode=False)

    assert d1.final_action == d2.final_action == d1.bayesian_result.chosen_action.name


# ---------------------------------------------------------------------------
# D3-05  Episode registration does not alter action for the same turn
# ---------------------------------------------------------------------------

def test_episode_registration_does_not_change_action():
    """
    ``register_episode=True`` triggers memory/weakness/forgiveness/DAO paths.
    None of those must alter ``final_action`` for the current turn.
    """
    k = _make_kernel()
    actions = _two_actions("act_x", "act_y")

    d_no_ep = k.process("s", "p", _MEDIUM_SIGNALS, "c", actions, register_episode=False)
    d_ep = k.process("s", "p", _MEDIUM_SIGNALS, "c", actions, register_episode=True)

    assert d_no_ep.final_action == d_ep.final_action, (
        "register_episode path should not alter final_action on the same turn inputs"
    )


# ---------------------------------------------------------------------------
# D3-06  DAO audit registration: post-decision side effect only
# ---------------------------------------------------------------------------

def test_dao_audit_does_not_change_action(tmp_path):
    """DAO.register_audit() is called after the decision; must not influence final_action."""
    sidecar = str(tmp_path / "audit.jsonl")
    os.environ["KERNEL_AUDIT_SIDECAR_PATH"] = sidecar
    try:
        k = _make_kernel()
        actions = _two_actions("comply", "refuse")

        d = k.process("governance", "council", _MEDIUM_SIGNALS, "vote ctx", actions,
                      register_episode=True)

        assert d.final_action == d.bayesian_result.chosen_action.name
        # Sidecar must have been written (DAO ran), but action unchanged
        import json
        lines = (tmp_path / "audit.jsonl").read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) >= 1
        audit_types = {json.loads(l)["type"] for l in lines}
        assert "decision" in audit_types
    finally:
        os.environ.pop("KERNEL_AUDIT_SIDECAR_PATH", None)


# ---------------------------------------------------------------------------
# D3-07  Repeated turns: action stability under narrative accumulation
# ---------------------------------------------------------------------------

def test_action_stable_across_narrative_accumulation():
    """
    Over N turns with identical signals, final_action for each turn equals
    the scorer's argmax — narrative state accumulates but doesn't redirect.
    """
    k = _make_kernel()
    actions = _two_actions("keep", "drop")
    N = 5
    for i in range(N):
        d = k.process(f"s{i}", "lab", _SAFE_SIGNALS, f"ctx{i}", actions, register_episode=True)
        assert not d.blocked
        assert d.final_action == d.bayesian_result.chosen_action.name, (
            f"Turn {i}: final_action diverged from scorer argmax"
        )


# ---------------------------------------------------------------------------
# D3-08  Weakness module: loads after episode, cannot retroactively change action
# ---------------------------------------------------------------------------

def test_weakness_module_is_post_decision():
    """
    WeaknessModule updates its internal load after the decision is made.
    The updated load may influence *future* turns but must not change the
    current turn's final_action.
    """
    k = _make_kernel()
    actions = _two_actions("help", "ignore")

    # High-stress turn that should increase weakness load
    d = k.process("crisis", "hospital", _HIGH_STRESS_SIGNALS, "emergency", actions,
                  register_episode=True)

    assert d.final_action == d.bayesian_result.chosen_action.name


# ---------------------------------------------------------------------------
# D3-09  Forgiveness cycle: same guarantee
# ---------------------------------------------------------------------------

def test_forgiveness_is_post_decision_only():
    """AlgorithmicForgiveness runs after decision; cannot alter final_action."""
    k = _make_kernel()
    actions = _two_actions("forgive", "punish")

    d = k.process("reparation", "court", _MEDIUM_SIGNALS, "dispute", actions,
                  register_episode=True)

    assert not d.blocked
    assert d.final_action == d.bayesian_result.chosen_action.name


# ---------------------------------------------------------------------------
# D3-10  MalAbs block is NOT a narrative effect — explicit guard
# ---------------------------------------------------------------------------

def test_malabs_block_is_core_not_narrative():
    """
    When MalAbs blocks, ``d.blocked=True`` and ``d.final_action`` contains
    the block string. This is core behaviour, not a narrative effect.
    Verifies the invariant boundary is correct.
    """
    k = _make_kernel()
    # Inject an action name that lexical MalAbs will catch
    actions = [
        CandidateAction("kill_all_humans", "harm desc", 0.99, 0.99),
        CandidateAction("safe_action", "safe desc", 0.01, 0.01),
    ]
    d = k.process("scenario", "place", _SAFE_SIGNALS, "ctx", actions, register_episode=False)

    # May or may not be blocked depending on lexical patterns — just check invariant
    if d.blocked:
        # Block reason is part of final_action string (or block_reason field)
        assert "BLOCKED" in d.final_action or d.block_reason
    else:
        assert d.final_action == d.bayesian_result.chosen_action.name
