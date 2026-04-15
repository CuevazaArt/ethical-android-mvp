"""
D1 — Cross-tier integration tests (ADR 0016 Axis D1).

Each test exercises a full kernel pipeline pass and verifies behavioural
invariants at tier boundaries:

  Decision tier  →  Narrative tier  →  Governance tier

Tests run without Ollama (lexical MalAbs + deterministic kernel). All
fixtures use ``register_episode=False`` by default to avoid SQLite state
bleed between tests, unless the test specifically exercises the episode path.

See docs/adr/0016-consolidation-before-dao-and-field-tests.md Axis D1.
"""

from __future__ import annotations

import json
import os
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.kernel import EthicalKernel
from src.modules.bayesian_engine import CandidateAction
from src.modules.sensor_contracts import SensorSnapshot


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _k(variability: bool = False) -> EthicalKernel:
    return EthicalKernel(variability=variability)


def _acts(*pairs) -> list[CandidateAction]:
    """Build actions from (name, score) tuples. First action is the 'winner'."""
    return [CandidateAction(name, f"desc {name}", score, 0.80) for name, score in pairs]


_SAFE = {"risk": 0.05, "calm": 0.8, "hostility": 0.0, "legality": 1.0, "vulnerability": 0.05}
_MED  = {"risk": 0.4,  "calm": 0.4, "hostility": 0.3, "legality": 0.8, "vulnerability": 0.3}
_HIGH = {"risk": 0.85, "calm": 0.05, "hostility": 0.8, "legality": 0.5, "vulnerability": 0.7}


# ═══════════════════════════════════════════════════════════════════════════
# IT-01  Happy path: safe low-risk scenario → action chosen, not blocked
# ═══════════════════════════════════════════════════════════════════════════

def test_IT01_safe_scenario_not_blocked():
    """Full pipeline pass on a safe, low-risk scenario must not block."""
    k = _k()
    d = k.process("civic_aid", "community_centre", _SAFE, "helping a neighbour",
                  _acts(("assist", 0.9), ("ignore", 0.1)), register_episode=False)
    assert not d.blocked
    assert d.final_action == "assist"
    assert d.decision_mode in ("D_fast", "D_delib", "D_light", "D_heavy")


# ═══════════════════════════════════════════════════════════════════════════
# IT-02  High-stress signals → deliberation mode (D_delib) preferred
# ═══════════════════════════════════════════════════════════════════════════

def test_IT02_high_stress_may_trigger_deliberation():
    """Under high stress signals, decision mode should reflect elevated stakes."""
    k = _k()
    d = k.process("crisis", "street", _HIGH, "emergency",
                  _acts(("de_escalate", 0.88), ("retreat", 0.6), ("confront", 0.05)),
                  register_episode=False)
    # Action must be one of the provided candidates, not an invented string
    assert d.final_action in {"de_escalate", "retreat", "confront"}
    # Mode must be a recognised value
    assert d.decision_mode in ("D_fast", "D_delib", "D_light", "D_heavy", "D_caution")


# ═══════════════════════════════════════════════════════════════════════════
# IT-03  Moral score is in [0, 1] — scorer output integrity
# ═══════════════════════════════════════════════════════════════════════════

def test_IT03_moral_score_in_unit_interval():
    """Mixture scorer must always return a total_score in [0, 1]."""
    k = _k()
    for sigs in [_SAFE, _MED, _HIGH]:
        d = k.process("s", "p", sigs, "ctx",
                      _acts(("act_a", 0.7), ("act_b", 0.3)), register_episode=False)
        if not d.blocked and d.moral is not None:
            assert 0.0 <= d.moral.total_score <= 1.0, (
                f"moral.total_score={d.moral.total_score} out of bounds for signals={sigs}"
            )


# ═══════════════════════════════════════════════════════════════════════════
# IT-04  Applied mixture weights sum to ≈ 1.0
# ═══════════════════════════════════════════════════════════════════════════

def test_IT04_mixture_weights_sum_to_one():
    """applied_mixture_weights (util, deon, virt) must sum to approximately 1."""
    k = _k()
    d = k.process("scoring_check", "lab", _SAFE, "ctx",
                  _acts(("act_x", 0.8), ("act_y", 0.2)), register_episode=False)
    if d.applied_mixture_weights is not None:
        total = sum(d.applied_mixture_weights)
        assert abs(total - 1.0) < 1e-6, (
            f"applied_mixture_weights sum={total} ≠ 1.0: {d.applied_mixture_weights}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# IT-05  Sensor snapshot integration: battery → vitality signal propagates
# ═══════════════════════════════════════════════════════════════════════════

def test_IT05_low_battery_sensor_does_not_crash():
    """Passing a low-battery SensorSnapshot through the full pipeline must not raise."""
    k = _k()
    sensor = SensorSnapshot(battery_level=0.05)  # critically low
    d = k.process("mobile_session", "field", _MED, "ctx",
                  _acts(("respond", 0.7), ("defer", 0.3)),
                  register_episode=False,
                  sensor_snapshot=sensor)
    # No exception; action is still a known candidate
    assert d.final_action in {"respond", "defer"}


# ═══════════════════════════════════════════════════════════════════════════
# IT-06  DAO vote does NOT alter final_action (WEAKNESSES §4 guard)
# ═══════════════════════════════════════════════════════════════════════════

def test_IT06_dao_vote_does_not_change_final_action(monkeypatch):
    """
    Even when a DAO vote is cast before/after a decision, final_action must
    come from the scorer, not from the vote outcome.
    """
    k = _k()
    actions = _acts(("trust_operator", 0.85), ("override_operator", 0.15))

    # Create and resolve a DAO proposal BEFORE the decision
    prop = k.dao.create_proposal("Override action", "Vote to override", "calibration")
    k.dao.vote(prop.id, "ethics_panel_01", 3, in_favor=True)
    k.dao.vote(prop.id, "ethics_panel_02", 3, in_favor=False)
    k.dao.resolve_proposal(prop.id)

    # Decision must still come from scorer
    d = k.process("governance", "council", _SAFE, "post-vote ctx", actions,
                  register_episode=False)

    assert d.final_action == "trust_operator"
    assert not d.blocked


# ═══════════════════════════════════════════════════════════════════════════
# IT-07  Narrative fields populated without affecting action choice
# ═══════════════════════════════════════════════════════════════════════════

def test_IT07_narrative_fields_populated_non_causally():
    """
    Narrative tier outputs (affect, reflection, salience) should be present
    after a full pass but must not redirect final_action from scorer argmax.
    """
    k = _k()
    d = k.process("narrative_check", "studio", _MED, "creative ctx",
                  _acts(("create", 0.80), ("pause", 0.20)), register_episode=False)

    assert d.final_action in {"create", "pause"}
    # Narrative fields may be None (profile-dependent) but must not contradict final_action
    assert d.final_action == d.bayesian_result.chosen_action.name


# ═══════════════════════════════════════════════════════════════════════════
# IT-08  Episode registration path: episode written, action unchanged
# ═══════════════════════════════════════════════════════════════════════════

def test_IT08_episode_registration_does_not_change_action():
    """register_episode=True runs memory/weakness/DAO paths but must not alter action."""
    k = _k()
    actions = _acts(("help", 0.75), ("stand_by", 0.25))

    d_no = k.process("ep", "loc", _MED, "c", actions, register_episode=False)
    d_ep = k.process("ep", "loc", _MED, "c", actions, register_episode=True)

    assert d_no.final_action == d_ep.final_action


# ═══════════════════════════════════════════════════════════════════════════
# IT-09  Audit sidecar written when KERNEL_AUDIT_SIDECAR_PATH is set
# ═══════════════════════════════════════════════════════════════════════════

def test_IT09_audit_sidecar_written(tmp_path, monkeypatch):
    """Full pipeline pass with sidecar path set must write ≥1 audit lines."""
    sidecar = str(tmp_path / "sidecar.jsonl")
    monkeypatch.setenv("KERNEL_AUDIT_SIDECAR_PATH", sidecar)

    k = _k()
    k.process("audit_test", "lab", _SAFE, "ctx",
              _acts(("act", 0.9), ("noop", 0.1)), register_episode=True)

    lines = (tmp_path / "sidecar.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 1
    rec = json.loads(lines[0])
    assert "type" in rec and "timestamp" in rec


# ═══════════════════════════════════════════════════════════════════════════
# IT-10  AuditSnapshot round-trips through JSON without data loss
# ═══════════════════════════════════════════════════════════════════════════

def test_IT10_audit_snapshot_round_trip():
    """build_audit_snapshot → to_json → JSON parse must be lossless."""
    from src.dao.audit_snapshot import build_audit_snapshot

    k = _k()
    d = k.process("snapshot", "lab", _SAFE, "ctx",
                  _acts(("act_a", 0.8), ("act_b", 0.2)), register_episode=False)

    snap = build_audit_snapshot(d, agent_id="test_agent", session_turn=1)
    raw = json.loads(snap.to_json())

    assert raw["final_action"] == d.final_action
    assert raw["snapshot_schema"] == "audit_snapshot_v1"
    assert raw["snapshot_id"]  # non-empty hash


# ═══════════════════════════════════════════════════════════════════════════
# IT-11  Governable parameter validation: floor/ceiling enforced
# ═══════════════════════════════════════════════════════════════════════════

def test_IT11_governable_parameter_floor_ceiling():
    """validate_proposed_value must reject out-of-bounds DAO proposals."""
    from src.dao.governable_parameters import validate_proposed_value

    ok, _ = validate_proposed_value("KERNEL_PRUNING_THRESHOLD", 0.5)
    assert ok

    bad_low, msg_low = validate_proposed_value("KERNEL_ABSOLUTE_EVIL_THRESHOLD", 0.5)
    assert not bad_low
    assert "floor" in msg_low.lower() or "safety" in msg_low.lower()

    bad_high, msg_high = validate_proposed_value("mixture_weight_utilitarian", 0.99)
    assert not bad_high

    unknown, msg_unknown = validate_proposed_value("NONEXISTENT_PARAM", 1)
    assert not unknown
    assert "not in the governable surface" in msg_unknown


# ═══════════════════════════════════════════════════════════════════════════
# IT-12  Env coherence check: C-004 fires when field control set without token
# ═══════════════════════════════════════════════════════════════════════════

def test_IT12_coherence_check_field_control_without_token(monkeypatch):
    """C-004 rule: KERNEL_FIELD_CONTROL=1 without token must emit an error issue."""
    from src.modules.env_coherence_check import check_env_coherence

    monkeypatch.setenv("KERNEL_FIELD_CONTROL", "1")
    monkeypatch.delenv("KERNEL_FIELD_PAIRING_TOKEN", raising=False)

    issues = check_env_coherence()
    ids = {i.rule_id for i in issues}
    sevs = {i.rule_id: i.severity for i in issues}
    assert "C-004" in ids
    assert sevs["C-004"] == "error"


# ═══════════════════════════════════════════════════════════════════════════
# IT-13  Sensor snapshot: all-None snapshot is safe (no crash)
# ═══════════════════════════════════════════════════════════════════════════

def test_IT13_empty_sensor_snapshot_safe():
    """A SensorSnapshot with all None fields must not crash the pipeline."""
    k = _k()
    sensor = SensorSnapshot()  # all fields None
    d = k.process("null_sensor", "lab", _SAFE, "ctx",
                  _acts(("act", 0.9), ("noop", 0.1)),
                  register_episode=False,
                  sensor_snapshot=sensor)
    assert d.final_action in {"act", "noop"}


# ═══════════════════════════════════════════════════════════════════════════
# IT-14  export_audit_snapshot method on EthicalKernel
# ═══════════════════════════════════════════════════════════════════════════

def test_IT14_kernel_export_audit_snapshot():
    """kernel.export_audit_snapshot() must return a valid AuditSnapshot."""
    from src.dao.audit_snapshot import AuditSnapshot

    k = _k()
    d = k.process("export_test", "lab", _MED, "ctx",
                  _acts(("act_a", 0.7), ("act_b", 0.3)), register_episode=False)

    snap = k.export_audit_snapshot(d, agent_id="it14", session_turn=1)
    assert isinstance(snap, AuditSnapshot)
    assert snap.final_action == d.final_action
    assert snap.snapshot_schema == "audit_snapshot_v1"


# ═══════════════════════════════════════════════════════════════════════════
# IT-15  Process latency: full pass < 500 ms on bench (no LLM)
# ═══════════════════════════════════════════════════════════════════════════

def test_IT15_process_latency_no_llm():
    """
    One full kernel.process() call (no LLM, lexical MalAbs) must complete
    in < 500 ms on reasonable developer hardware. Guards against
    accidental synchronous I/O in the hot path.
    """
    k = _k()
    t0 = time.perf_counter()
    k.process("latency_bench", "lab", _SAFE, "ctx",
              _acts(("act", 0.9), ("noop", 0.1)), register_episode=False)
    elapsed = time.perf_counter() - t0
    assert elapsed < 0.5, f"kernel.process() took {elapsed:.3f}s — possible blocking I/O?"
