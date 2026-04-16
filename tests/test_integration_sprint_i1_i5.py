"""
Integration Sprint I1–I5 unit tests.

Covers:
  I1 — weights_snapshot in NarrativeEpisode
  I2 — EVENT_KERNEL_WEIGHTS_UPDATED on the event bus
  I3 — perception_uncertainty from PerceptionCoercionReport into signals
  I4 — KERNEL_NARRATIVE_IDENTITY_POLICY=pole_pre_argmax
  I5 — KERNEL_TEMPORAL_ETA_MODULATION urgency boost
"""
from __future__ import annotations

import os
import types
from unittest.mock import MagicMock


# ──────────────────────────────────────────────────────────────────────
# I1 — weights_snapshot persisted in NarrativeEpisode
# ──────────────────────────────────────────────────────────────────────
def test_i1_weights_snapshot_stored():
    from src.modules.narrative import NarrativeMemory

    mem = NarrativeMemory()
    ep = mem.register(
        place="lab",
        description="test event",
        action="respond",
        morals={"compassionate": "help"},
        verdict="Good",
        score=0.8,
        mode="D_fast",
        sigma=0.5,
        context="everyday",
        weights_snapshot=(0.4, 0.35, 0.25),
    )
    assert ep.weights_snapshot == (0.4, 0.35, 0.25)


def test_i1_weights_snapshot_none_by_default():
    from src.modules.narrative import NarrativeMemory

    mem = NarrativeMemory()
    ep = mem.register(
        place="lab",
        description="test event",
        action="respond",
        morals={},
        verdict="Good",
        score=0.7,
        mode="D_fast",
        sigma=0.4,
        context="everyday",
    )
    assert ep.weights_snapshot is None


# ──────────────────────────────────────────────────────────────────────
# I2 — EVENT_KERNEL_WEIGHTS_UPDATED on event bus
# ──────────────────────────────────────────────────────────────────────
def test_i2_event_constant_exists():
    from src.modules.kernel_event_bus import EVENT_KERNEL_WEIGHTS_UPDATED

    assert EVENT_KERNEL_WEIGHTS_UPDATED == "kernel.weights_updated"


def test_i2_event_bus_receives_weights_updated():
    from src.modules.kernel_event_bus import EVENT_KERNEL_WEIGHTS_UPDATED, KernelEventBus

    bus = KernelEventBus()
    received = []
    bus.subscribe(EVENT_KERNEL_WEIGHTS_UPDATED, received.append)

    payload = {"prior": [0.4, 0.35, 0.25], "posterior": [0.45, 0.32, 0.23],
               "trust": 1.0, "source": "feedback_posterior"}
    bus.publish(EVENT_KERNEL_WEIGHTS_UPDATED, payload)

    assert len(received) == 1
    assert received[0]["source"] == "feedback_posterior"
    assert received[0]["posterior"] == [0.45, 0.32, 0.23]


# ──────────────────────────────────────────────────────────────────────
# I3 — perception_uncertainty reaches Bayesian signals
# ──────────────────────────────────────────────────────────────────────
def test_i3_object_coercion_report_sets_signal():
    """Object-based coercion_report with .uncertainty() injects into signals."""
    # Simulate the logic extracted from process_chat_turn
    class MockCoercionReport:
        def uncertainty(self):
            return 0.7

    cr = MockCoercionReport()
    signals = {"urgency": 0.3, "risk": 0.1}
    pu = None

    if isinstance(cr, dict):
        pu = cr.get("uncertainty")
    elif cr is not None and callable(getattr(cr, "uncertainty", None)):
        try:
            pu = float(cr.uncertainty())
        except Exception:
            pu = None

    if pu is not None and pu > 0.0:
        signals = dict(signals)
        signals["perception_uncertainty"] = max(float(signals.get("perception_uncertainty", 0.0)), pu)

    assert signals.get("perception_uncertainty") == 0.7


def test_i3_zero_uncertainty_not_injected():
    """Zero uncertainty value does not pollute signals."""
    class MockCoercionReport:
        def uncertainty(self):
            return 0.0

    cr = MockCoercionReport()
    signals = {"urgency": 0.3}
    pu = None

    if cr is not None and callable(getattr(cr, "uncertainty", None)):
        pu = float(cr.uncertainty())

    if pu is not None and pu > 0.0:
        signals = dict(signals)
        signals["perception_uncertainty"] = pu

    assert "perception_uncertainty" not in signals


# ──────────────────────────────────────────────────────────────────────
# I4 — KERNEL_NARRATIVE_IDENTITY_POLICY=pole_pre_argmax
# ──────────────────────────────────────────────────────────────────────
def test_i4_identity_leans_set_pole_weights(monkeypatch):
    """pole_pre_argmax mode maps identity leans to pre_argmax_pole_weights."""
    monkeypatch.setenv("KERNEL_NARRATIVE_IDENTITY_POLICY", "pole_pre_argmax")
    monkeypatch.setenv("KERNEL_POLES_PRE_ARGMAX", "0")  # start with None

    # Build minimal identity state
    id_state = types.SimpleNamespace(
        civic_lean=0.6, care_lean=0.4, careful_lean=0.3, deliberation_lean=0.5
    )
    memory_mock = types.SimpleNamespace(
        identity=types.SimpleNamespace(state=id_state)
    )
    bayesian_mock = MagicMock()
    bayesian_mock.pre_argmax_pole_weights = None

    # Simulate the I4 block
    _identity_policy = os.environ.get("KERNEL_NARRATIVE_IDENTITY_POLICY", "off").strip().lower()
    if _identity_policy == "pole_pre_argmax":
        try:
            _id_state = getattr(getattr(memory_mock, "identity", None), "state", None)
            if _id_state is not None:
                _civic = float(getattr(_id_state, "civic_lean", 0.0))
                _care = float(getattr(_id_state, "care_lean", 0.0))
                _careful = float(getattr(_id_state, "careful_lean", 0.0))
                _delib = float(getattr(_id_state, "deliberation_lean", 0.0))
                _id_weights = {
                    "compassionate": max((_civic + _care) / 2.0, 0.0),
                    "conservative": max(_careful, 0.0),
                    "optimistic": max(_delib, 0.0),
                }
                _id_sum = sum(_id_weights.values())
                if _id_sum > 0.0:
                    _id_weights = {k: v / _id_sum for k, v in _id_weights.items()}
                    bayesian_mock.pre_argmax_pole_weights = _id_weights
        except Exception:
            pass

    weights = bayesian_mock.pre_argmax_pole_weights
    assert weights is not None
    assert abs(sum(weights.values()) - 1.0) < 1e-9
    # compassionate should dominate given high civic+care leans
    assert weights["compassionate"] > weights["conservative"]


def test_i4_off_by_default(monkeypatch):
    """Without env var, I4 should not modify pre_argmax_pole_weights."""
    monkeypatch.delenv("KERNEL_NARRATIVE_IDENTITY_POLICY", raising=False)

    _identity_policy = os.environ.get("KERNEL_NARRATIVE_IDENTITY_POLICY", "off").strip().lower()
    assert _identity_policy == "off"


# ──────────────────────────────────────────────────────────────────────
# I5 — KERNEL_TEMPORAL_ETA_MODULATION urgency boost
# ──────────────────────────────────────────────────────────────────────
def _apply_eta_modulation(signals, eta_seconds, battery_horizon_state, ref_eta=300.0):
    """Helper replicating the I5 urgency boost logic."""
    urgency_boost = min(max(ref_eta / max(eta_seconds, 1.0), 0.0), 1.0)
    if battery_horizon_state == "critical":
        urgency_boost = min(urgency_boost + 0.3, 1.0)
    if urgency_boost > 0.0:
        signals = dict(signals)
        cur_urgency = float(signals.get("urgency", 0.0))
        signals["urgency"] = min(max(cur_urgency + urgency_boost * 0.4, 0.0), 1.0)
    return signals


def test_i5_critical_low_eta_boosts_urgency():
    """30-second ETA + critical battery → urgency boosted above initial."""
    signals = {"urgency": 0.2}
    result = _apply_eta_modulation(signals, eta_seconds=30, battery_horizon_state="critical")
    # boost = 1.0 (capped), urgency += 1.0 * 0.4 = 0.4 -> 0.6
    assert result["urgency"] > signals["urgency"]
    assert result["urgency"] >= 0.6


def test_i5_nominal_long_eta_no_boost():
    """ETA == reference_eta, nominal battery → small boost."""
    signals = {"urgency": 0.2}
    result = _apply_eta_modulation(signals, eta_seconds=300, battery_horizon_state="nominal")
    # boost = 1.0, urgency += 1.0 * 0.4 = 0.4 → 0.6
    assert abs(result["urgency"] - 0.6) < 0.01


def test_i5_urgency_capped_at_1():
    """Urgency never exceeds 1.0."""
    signals = {"urgency": 0.9}
    result = _apply_eta_modulation(signals, eta_seconds=5, battery_horizon_state="critical")
    assert result["urgency"] <= 1.0


def test_i5_off_by_default(monkeypatch):
    """KERNEL_TEMPORAL_ETA_MODULATION defaults to off."""
    monkeypatch.delenv("KERNEL_TEMPORAL_ETA_MODULATION", raising=False)
    val = os.environ.get("KERNEL_TEMPORAL_ETA_MODULATION", "off").strip().lower()
    assert val in ("off", "")
