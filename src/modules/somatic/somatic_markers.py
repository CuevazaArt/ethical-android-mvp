"""
Somatic ethical markers — learned sensor-pattern → cautious signal nudge (v10).

Quantizes :class:`SensorSnapshot` into a key; optional **negative** weight bumps
``risk`` / ``urgency`` slightly before ``process``. Does **not** bypass MalAbs.

See docs/proposals/README.md
"""
# Status: SCAFFOLD


import logging
import math
import os
import time

from src.modules.perception.sensor_contracts import SensorSnapshot

_log = logging.getLogger(__name__)


def somatic_markers_enabled() -> bool:
    """
    Check if somatic markers are enabled via environment variable.

    Returns:
        bool: True if enabled, False otherwise.
    """
    v = os.environ.get("KERNEL_SOMATIC_MARKERS", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def _clamp01(x: float) -> float:
    """
    Clamp a float value to the [0.0, 1.0] range.
    """
    try:
        val = float(x)
        if not math.isfinite(val):
            return 0.5
        return max(0.0, min(1.0, val))
    except (ValueError, TypeError):
        return 0.5


def quantize_snapshot(snapshot: SensorSnapshot | None) -> str | None:
    """
    Bucket coarse features from a sensor snapshot for use as dictionary keys.
    Stable across small noise.

    Args:
        snapshot (SensorSnapshot | None): The sensor snapshot to quantize.

    Returns:
        str | None: Quantized key string, or None if snapshot is empty.
    """
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
    """
    Stores pattern → negative association weight in [0, 1]; persisted in snapshot (Phase 2).
    """

    def __init__(self) -> None:
        self._negative_weights: dict[str, float] = {}

    def to_dict(self) -> dict[str, float]:
        return {k: float(v) for k, v in self._negative_weights.items()}

    def learn_negative_pattern(
        self,
        snapshot: SensorSnapshot | None,
        weight: float = 0.65,
    ) -> None:
        t0 = time.perf_counter()
        try:
            k = quantize_snapshot(snapshot)
            if not k:
                return
            w = _clamp01(weight)
            self._negative_weights[k] = max(self._negative_weights.get(k, 0.0), w)

            latency = (time.perf_counter() - t0) * 1000
            if latency > 1.0:
                _log.debug("SomaticMarkerStore: learn_negative_pattern latency = %.2fms", latency)
        except Exception as e:
            _log.error("SomaticMarkerStore: Failed to learn pattern: %s", e)

    def clear_pattern(self, key: str) -> None:
        """
        Remove a learned pattern from the store.

        Args:
            key (str): The quantized pattern key to remove.
        """
        self._negative_weights.pop(key, None)

    def replace_weights(self, weights: dict[str, float]) -> None:
        """
        Restore weights from a snapshot (checkpoint).

        Args:
            weights (dict[str, float]): Mapping of pattern keys to weights.
        """
        self._negative_weights = {k: _clamp01(v) for k, v in weights.items()}

    def get_weight(self, key: str) -> float:
        """Public access to learned weights for somatic nudging."""
        return float(self._negative_weights.get(key, 0.0))


def apply_somatic_nudges(
    signals: dict[str, float],
    snapshot: SensorSnapshot | None,
    store: SomaticMarkerStore,
) -> dict[str, float]:
    """
    Apply learned somatic nudges to the signals dictionary based on the current sensor snapshot.

    Args:
        signals (dict[str, float]): Input signals to adjust.
        snapshot (SensorSnapshot | None): Current sensor snapshot.
        store (SomaticMarkerStore): Store of learned negative patterns.

    Returns:
        dict[str, float]: Adjusted signals with nudges applied if a pattern matches.
    """
    if not somatic_markers_enabled():
        return signals
    k = quantize_snapshot(snapshot)
    if not k:
        return signals

    w = store.get_weight(k)
    if w <= 0:
        return signals

    out = dict(signals)
    out["risk"] = _clamp01(out.get("risk", 0.5) + 0.1 * w)
    out["urgency"] = _clamp01(out.get("urgency", 0.5) + 0.06 * w)
    out["calm"] = _clamp01(out.get("calm", 0.5) - 0.05 * w)
    return out
