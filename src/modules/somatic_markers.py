"""
Somatic ethical markers — learned sensor-pattern → cautious signal nudge (v10).

Quantizes :class:`SensorSnapshot` into a key; optional **negative** weight bumps
``risk`` / ``urgency`` slightly before ``process``. Does **not** bypass MalAbs.

See docs/proposals/README.md
"""

from __future__ import annotations

import os

from .sensor_contracts import SensorSnapshot


def somatic_markers_enabled() -> bool:
    v = os.environ.get("KERNEL_SOMATIC_MARKERS", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def quantize_snapshot(snapshot: SensorSnapshot | None) -> str | None:
    """Bucket coarse features for dictionary keys (stable across small noise)."""
    if snapshot is None or snapshot.is_empty():
        return None
    parts = []
    if snapshot.audio_emergency is not None:
        parts.append(f"a{min(5, int(snapshot.audio_emergency * 6))}")
    if snapshot.place_trust is not None:
        parts.append(f"p{min(5, int(snapshot.place_trust * 6))}")
    if snapshot.accelerometer_jerk is not None:
        parts.append(f"j{min(5, int(snapshot.accelerometer_jerk * 6))}")
    if snapshot.vision_emergency is not None:
        parts.append(f"v{min(5, int(snapshot.vision_emergency * 6))}")
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
        k = quantize_snapshot(snapshot)
        if not k:
            return
        w = _clamp01(weight)
        self._negative_weights[k] = max(self._negative_weights.get(k, 0.0), w)

    def clear_pattern(self, key: str) -> None:
        self._negative_weights.pop(key, None)

    def replace_weights(self, weights: dict[str, float]) -> None:
        """Restore from snapshot (checkpoint)."""
        self._negative_weights = {k: _clamp01(v) for k, v in weights.items()}


def apply_somatic_nudges(
    signals: dict[str, float],
    snapshot: SensorSnapshot | None,
    store: SomaticMarkerStore,
) -> dict[str, float]:
    if not somatic_markers_enabled():
        return signals
    k = quantize_snapshot(snapshot)
    if not k or k not in store._negative_weights:
        return signals
    w = store._negative_weights[k]
    out = dict(signals)
    out["risk"] = _clamp01(out.get("risk", 0.5) + 0.1 * w)
    out["urgency"] = _clamp01(out.get("urgency", 0.5) + 0.06 * w)
    out["calm"] = _clamp01(out.get("calm", 0.5) - 0.05 * w)
    return out
