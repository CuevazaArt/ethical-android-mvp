"""
Unit tests for ThalamusNode (Bloque 10.1 — Sensory Fusion VVAD + VAD).

Verifies that fuse_signals() correctly classifies focal vs. background speech,
detects sensory dissonance, and integrates into SensorSnapshot via
merge_sensor_hints_into_signals.
"""

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel_lobes.thalamus_node import ThalamusNode
from src.kernel_lobes.models import SensoryEpisode
from src.modules.sensor_contracts import SensorSnapshot, merge_sensor_hints_into_signals


@pytest.fixture
def thalamus() -> ThalamusNode:
    return ThalamusNode()


# ── Core signal fusion ──────────────────────────────────────────────────────


def test_focal_address_detected_when_all_signals_high(thalamus: ThalamusNode):
    """Presence + lip movement + vad_confidence all above thresholds → focal address."""
    result = thalamus.fuse_signals(
        vision_data={"lip_movement": 0.8, "human_presence": 0.9},
        audio_data={"vad_confidence": 0.85},
    )
    assert result["is_focal_address"] is True
    assert result["attention_locus"] > 0.5
    assert result["cross_modal_trust"] == 1.0


def test_background_speech_when_no_presence(thalamus: ThalamusNode):
    """No visual presence → speech treated as background; focal flag False."""
    result = thalamus.fuse_signals(
        vision_data={"lip_movement": 0.0, "human_presence": 0.1},
        audio_data={"vad_confidence": 0.9},
    )
    assert result["is_focal_address"] is False
    assert result["attention_locus"] == 0.0  # no presence → no attention
    assert result["cross_modal_trust"] == 0.4


def test_background_speech_when_no_lip_movement(thalamus: ThalamusNode):
    """Presence detected but lips not moving → off-axis / background voice."""
    result = thalamus.fuse_signals(
        vision_data={"lip_movement": 0.1, "human_presence": 0.8},
        audio_data={"vad_confidence": 0.9},
    )
    assert result["is_focal_address"] is False
    assert result["cross_modal_trust"] == 0.4


def test_sensory_dissonance_high_vad_no_lips(thalamus: ThalamusNode):
    """High VAD but no visible lips → sensory dissonance contributes to tension."""
    result = thalamus.fuse_signals(
        vision_data={"lip_movement": 0.05, "human_presence": 0.8},
        audio_data={"vad_confidence": 0.95},
    )
    assert result["sensory_tension"] > 0.0


def test_no_tension_when_silent_and_empty_scene(thalamus: ThalamusNode):
    """No audio and no presence → zero tension and zero attention."""
    result = thalamus.fuse_signals(
        vision_data={"lip_movement": 0.0, "human_presence": 0.0},
        audio_data={"vad_confidence": 0.0},
    )
    assert result["attention_locus"] == 0.0
    assert result["sensory_tension"] == 0.0


def test_environmental_stress_added_to_tension(thalamus: ThalamusNode):
    """environmental_stress propagates into total sensory_tension."""
    quiet = thalamus.fuse_signals(
        vision_data={"lip_movement": 0.0, "human_presence": 0.0},
        audio_data={"vad_confidence": 0.0},
        environmental_stress=0.0,
    )
    noisy = thalamus.fuse_signals(
        vision_data={"lip_movement": 0.0, "human_presence": 0.0},
        audio_data={"vad_confidence": 0.0},
        environmental_stress=0.8,
    )
    assert noisy["sensory_tension"] > quiet["sensory_tension"]


def test_attention_locus_clamped_between_0_and_1(thalamus: ThalamusNode):
    """attention_locus output is always in [0, 1] regardless of input extremes."""
    result = thalamus.fuse_signals(
        vision_data={"lip_movement": 1.0, "human_presence": 1.0},
        audio_data={"vad_confidence": 1.0},
        environmental_stress=1.0,
    )
    assert 0.0 <= result["attention_locus"] <= 1.0
    assert 0.0 <= result["sensory_tension"] <= 1.0


def test_missing_vision_keys_default_to_zero(thalamus: ThalamusNode):
    """Missing dict keys fall back to 0.0 without raising KeyError."""
    result = thalamus.fuse_signals(
        vision_data={},
        audio_data={},
    )
    assert result["attention_locus"] == 0.0
    assert result["is_focal_address"] is False


# ── push_episode ring buffer ────────────────────────────────────────────────


def test_push_episode_stores_in_buffer(thalamus: ThalamusNode):
    ep = SensoryEpisode(origin="audio", entities=["human"], signals={"tension": 0.3})
    thalamus.push_episode(ep)
    assert len(thalamus.sensory_buffer) == 1
    assert thalamus.sensory_buffer[0].origin == "audio"


def test_push_episode_circular_buffer_caps_at_50(thalamus: ThalamusNode):
    for i in range(60):
        thalamus.push_episode(SensoryEpisode(origin="vision"))
    assert len(thalamus.sensory_buffer) <= 50


# ── SensorSnapshot integration ─────────────────────────────────────────────


def test_thalamus_tension_nudges_signals_via_merge():
    """High thalamus_tension in snapshot raises urgency and lowers calm."""
    snap = SensorSnapshot(thalamus_tension=0.8, thalamus_cross_modal_trust=1.0)
    signals = {"urgency": 0.5, "calm": 0.5}
    out = merge_sensor_hints_into_signals(signals, snap)
    assert out["urgency"] > 0.5
    assert out["calm"] < 0.5


def test_low_cross_modal_trust_dampens_urgency():
    """cross_modal_trust < 0.5 (background speech) slightly reduces urgency spike."""
    snap_focal = SensorSnapshot(
        thalamus_tension=0.6, thalamus_cross_modal_trust=1.0
    )
    snap_background = SensorSnapshot(
        thalamus_tension=0.6, thalamus_cross_modal_trust=0.3
    )
    base = {"urgency": 0.5, "calm": 0.5}
    focal_out = merge_sensor_hints_into_signals(dict(base), snap_focal)
    bg_out = merge_sensor_hints_into_signals(dict(base), snap_background)
    assert bg_out["urgency"] < focal_out["urgency"]


def test_high_thalamus_attention_raises_familiarity():
    """Confirmed focal interaction raises familiarity signal."""
    snap = SensorSnapshot(thalamus_attention=0.9, thalamus_cross_modal_trust=1.0)
    signals = {"familiarity": 0.4}
    out = merge_sensor_hints_into_signals(signals, snap)
    assert out["familiarity"] > 0.4


def test_thalamus_fields_not_applied_when_none():
    """None thalamus fields leave signals unchanged (no nudge applied)."""
    snap = SensorSnapshot(thalamus_tension=None, thalamus_attention=None)
    # audio_emergency slightly above zero to make snapshot non-empty without other nudges
    snap.audio_emergency = 0.1  # below threshold so no stress nudge
    signals = {"urgency": 0.5, "calm": 0.5, "familiarity": 0.5}
    out = merge_sensor_hints_into_signals(signals, snap)
    assert out["urgency"] == 0.5
    assert out["calm"] == 0.5
    assert out["familiarity"] == 0.5


def test_snapshot_is_empty_without_thalamus_fields():
    """SensorSnapshot with only thalamus fields unset is considered empty."""
    snap = SensorSnapshot()
    assert snap.is_empty() is True


def test_snapshot_not_empty_with_thalamus_tension():
    """SensorSnapshot with thalamus_tension set is NOT empty."""
    snap = SensorSnapshot(thalamus_tension=0.5)
    assert snap.is_empty() is False
