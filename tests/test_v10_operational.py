"""v10 operational layer: diplomacy, skills, somatic markers, metaplan."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.ethical_reflection import ReflectionSnapshot
from src.modules.gray_zone_diplomacy import negotiation_hint_for_communicate
from src.modules.metaplan_registry import MetaplanRegistry
from src.modules.sensor_contracts import SensorSnapshot
from src.modules.skill_learning_registry import SkillLearningRegistry
from src.modules.somatic_markers import (
    SomaticMarkerStore,
    apply_somatic_nudges,
    quantize_snapshot,
    somatic_markers_enabled,
)


def test_diplomacy_gray_zone_hint():
    r = ReflectionSnapshot(
        pole_spread=0.2,
        pole_scores=(0.5, 0.5, 0.5),
        conflict_level="low",
        strain_index=0.1,
        will_mode="gray_zone",
        uncertainty=0.2,
        note="",
    )
    h = negotiation_hint_for_communicate("gray_zone", r, "none")
    assert h
    assert "negotiated" in h.lower() or "tension" in h.lower()


def test_diplomacy_off(monkeypatch):
    monkeypatch.setenv("KERNEL_GRAY_ZONE_DIPLOMACY", "0")
    r = ReflectionSnapshot(
        pole_spread=0.2,
        pole_scores=(0.5, 0.5, 0.5),
        conflict_level="low",
        strain_index=0.1,
        will_mode="x",
        uncertainty=0.2,
        note="",
    )
    assert negotiation_hint_for_communicate("gray_zone", r, "none") == ""


def test_diplomacy_high_strain():
    r = ReflectionSnapshot(
        pole_spread=1.2,
        pole_scores=(0.1, 0.9, 0.5),
        conflict_level="high",
        strain_index=0.55,
        will_mode="D_fast",
        uncertainty=0.5,
        note="",
    )
    h = negotiation_hint_for_communicate("D_delib", r, "none")
    assert h


def test_skill_registry_audit():
    reg = SkillLearningRegistry()
    reg.request_ticket("OAuth scope X", "Protect owner data when calling API Y")
    lines = reg.audit_lines_for_psi_sleep()
    assert any("pending" in ln for ln in lines)
    tid = reg.pending()[0].id
    assert reg.approve(tid)
    assert not reg.pending()


def test_metaplan_hint():
    m = MetaplanRegistry()
    assert m.hint_for_communicate() == ""
    m.add_goal("Improve financial stability", priority=0.8)
    h = m.hint_for_communicate()
    assert "financial" in h.lower() or "Long-horizon" in h


def test_somatic_nudge_after_learn():
    store = SomaticMarkerStore()
    snap = SensorSnapshot.from_dict(
        {"audio_emergency": 0.9, "place_trust": 0.2, "accelerometer_jerk": 0.1}
    )
    k = quantize_snapshot(snap)
    assert k
    store.learn_negative_pattern(snap, weight=0.8)
    base = {"risk": 0.3, "urgency": 0.4, "calm": 0.6}
    out = apply_somatic_nudges(base, snap, store)
    assert out["risk"] >= base["risk"]


def test_somatic_disabled(monkeypatch):
    monkeypatch.setenv("KERNEL_SOMATIC_MARKERS", "0")
    assert somatic_markers_enabled() is False
