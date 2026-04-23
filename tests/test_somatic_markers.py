"""Somatic markers — finite quantization and signal nudges (EXPERIMENTAL path)."""

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.sensor_contracts import SensorSnapshot
from src.modules.somatic_markers import (
    SomaticMarkerStore,
    _clamp01,
    _coarse_bucket,
    apply_somatic_nudges,
    quantize_snapshot,
    somatic_markers_enabled,
)


def test_clamp01_rejects_non_finite() -> None:
    assert _clamp01(float("nan")) == 0.0
    assert _clamp01(float("inf")) == 0.0
    assert _clamp01(1.5) == 1.0
    assert _clamp01(-0.1) == 0.0


def test_coarse_bucket_rejects_non_finite() -> None:
    assert _coarse_bucket(float("nan")) is None
    assert _coarse_bucket(None) is None
    assert _coarse_bucket(0.0) == 0
    assert _coarse_bucket(1.0) == 5


def test_quantize_omits_nan_component() -> None:
    snap = SensorSnapshot(
        audio_emergency=float("nan"),
        place_trust=0.5,
    )
    q = quantize_snapshot(snap)
    assert q is not None
    assert "a" not in (q or "")
    assert "p" in q


def test_apply_somatic_nudges_sanitizes_incoming_signals(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SOMATIC_MARKERS", "1")
    store = SomaticMarkerStore()
    snap = SensorSnapshot(place_trust=0.5)
    k = quantize_snapshot(snap)
    assert k
    store._negative_weights[k] = 0.5
    base = {"risk": float("nan"), "urgency": 0.5, "calm": 0.5}
    out = apply_somatic_nudges(base, snap, store)
    assert somatic_markers_enabled() is True
    assert math.isfinite(out["risk"])
    assert 0.0 <= out["risk"] <= 1.0
