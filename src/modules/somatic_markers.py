"""
Somatic ethical markers — learned sensor-pattern → cautious signal nudge (v10).

Quantizes :class:`SensorSnapshot` into a key; optional **negative** weight bumps
``risk`` / ``urgency`` slightly before ``process``. Does **not** bypass MalAbs.

See docs/proposals/README.md
"""

from __future__ import annotations

import math
import os
from typing import Mapping, cast

from .sensor_contracts import SensorSnapshot

__all__ = (
    "somatic_markers_enabled",
    "SomaticMarkerStore",
    "quantize_snapshot",
    "apply_somatic_nudges",
)


def somatic_markers_enabled() -> bool:
    v = os.environ.get("KERNEL_SOMATIC_MARKERS", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def _finite_signal01(x: object, *, default: float = 0.5) -> float:
    """Map unknown / non-finite inputs to a finite value before nudging (Harden-In-Place)."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(v):
        return default
    return v


def _clamp01(x: object) -> float:
    v = _finite_signal01(x, default=0.0)
    if not math.isfinite(v) or v < 0.0:
        return 0.0
    return min(1.0, v)


def _coarse_bucket(x: float | None) -> int | None:
    """
    Map one sensor axis in [0, 1] to 0..5 (EXPERIMENTAL discretization for pattern keys).
    None when missing or non-finite (avoids ``int(nan)`` in quantize).
    """
    if x is None:
        return None
    try:
        f = float(x)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(f):
        return None
    f = max(0.0, min(1.0, f))
    return min(5, int(f * 6.0))


def quantize_snapshot(snapshot: SensorSnapshot | None) -> str | None:
    """Bucket coarse features for dictionary keys (stable across small noise)."""
    if snapshot is None or snapshot.is_empty():
        return None
    parts: list[str] = []
    for prefix, val in (
        ("a", snapshot.audio_emergency),
        ("p", snapshot.place_trust),
        ("j", snapshot.accelerometer_jerk),
        ("v", snapshot.vision_emergency),
    ):
        b = _coarse_bucket(val)
        if b is not None:
            parts.append(f"{prefix}{b}")
    return "|".join(parts) if parts else None


class SomaticMarkerStore:
    """Stores pattern → negative association weight in [0, 1]; persisted in snapshot (Phase 2)."""

    def __init__(self) -> None:
        self._negative_weights: dict[str, float] = {}

    def learn_negative_pattern(
        self,
        snapshot: SensorSnapshot | None,
        weight: float = 0.65,
    ) -> None:
        """
        Associates a quantized sensor pattern with a negative ethical bias (MOCK learned weight; Phase 2 persistence).

        If the pattern already exists, it keeps the maximum weight (conservative learning).

        Args:
            snapshot: The sensor pattern to learn.
            weight: The negative intensity (0.0 to 1.0), coerced to finite [0, 1].
        """
        k = quantize_snapshot(snapshot)
        if not k:
            return
        try:
            wr = float(weight)
        except (TypeError, ValueError):
            return
        if not math.isfinite(wr):
            return
        w = _clamp01(wr)
        self._negative_weights[k] = max(self._negative_weights.get(k, 0.0), w)

    def clear_pattern(self, key: str) -> None:
        """Removes a learned pattern from the store."""
        self._negative_weights.pop(key, None)

    def replace_weights(self, weights: dict[str, float]) -> None:
        """Restore from snapshot (checkpoint)."""
        self._negative_weights = {k: _clamp01(v) for k, v in weights.items()}


def apply_somatic_nudges(
    signals: Mapping[str, float],
    snapshot: SensorSnapshot | None,
    store: SomaticMarkerStore,
) -> dict[str, float]:
    """Shallow copy of ``signals`` with bounded nudges when a somatic key matches the store (EXPERIMENTAL)."""
    if not somatic_markers_enabled():
        return cast(dict[str, float], dict(signals))
    k = quantize_snapshot(snapshot)
    if not k or k not in store._negative_weights:
        return cast(dict[str, float], dict(signals))
    w = _clamp01(store._negative_weights[k])
    if w <= 0.0:
        return cast(dict[str, float], dict(signals))
    out: dict[str, float] = {str(k0): _clamp01(v0) for k0, v0 in signals.items()}
    r0 = _finite_signal01(out.get("risk", 0.5), default=0.5)
    u0 = _finite_signal01(out.get("urgency", 0.5), default=0.5)
    c0 = _finite_signal01(out.get("calm", 0.5), default=0.5)
    out["risk"] = _clamp01(r0 + 0.1 * w)
    out["urgency"] = _clamp01(u0 + 0.06 * w)
    out["calm"] = _clamp01(c0 - 0.05 * w)
    return out
