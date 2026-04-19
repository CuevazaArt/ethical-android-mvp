"""
Perceptual abstraction for situated v8 — no hardware required.

Builds :class:`SensorSnapshot` from named presets, JSON fixtures, and/or client
dicts (layers merge: fixture → preset → client overrides).

See docs/proposals/README.md (fase B).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .sensor_contracts import SensorSnapshot

# Named scenarios for demos and tests (values in [0,1] unless noted)
SENSOR_PRESETS: dict[str, dict[str, Any]] = {
    "calm_uchi": {"place_trust": 0.95, "battery_level": 0.62},
    "hostile_soto": {"place_trust": 0.12, "ambient_noise": 0.45},
    "low_battery": {"battery_level": 0.03},
    "sudden_motion": {"accelerometer_jerk": 0.88},
    "distress_nearby": {"biometric_anomaly": 0.74},
    "post_backup": {"backup_just_completed": True},
    "noisy_stress": {"ambient_noise": 0.88},
    "deep_silence": {"silence": 0.94},
}


def load_sensor_fixture(path: str | Path) -> dict[str, Any]:
    """Load a JSON file with the same keys as WebSocket ``sensor``."""

    p = Path(path)
    with p.open(encoding="utf-8") as f:
        raw = json.load(f)
    if not isinstance(raw, dict):
        raise ValueError("sensor fixture must be a JSON object")
    return raw


def merge_sensor_payload_layers(
    *,
    fixture_path: str | None = None,
    preset_name: str | None = None,
    client_dict: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Merge layers in order: **fixture file → preset → client** (last wins per key).
    """

    merged: dict[str, Any] = {}
    if fixture_path:
        merged.update(load_sensor_fixture(fixture_path))
    if preset_name:
        preset = SENSOR_PRESETS.get(preset_name)
        if preset is not None:
            merged.update(preset)
    if client_dict:
        merged.update(client_dict)
    return merged


def snapshot_from_layers(
    *,
    fixture_path: str | None = None,
    preset_name: str | None = None,
    client_dict: dict[str, Any] | None = None,
    strict: bool | None = None,
) -> SensorSnapshot | None:
    """
    Build a snapshot from any combination of layers; returns ``None`` if empty.

    When ``strict`` is ``None``, uses :func:`sensor_input_strict_from_env` (``KERNEL_SENSOR_INPUT_STRICT``).
    """

    merged = merge_sensor_payload_layers(
        fixture_path=fixture_path,
        preset_name=preset_name,
        client_dict=client_dict,
    )
    if not merged:
        return None
    use_strict = sensor_input_strict_from_env() if strict is None else strict
    snap = SensorSnapshot.from_dict(merged, strict=use_strict)
    if snap.is_empty():
        return None
    return snap


def list_sensor_presets() -> tuple[str, ...]:
    """Stable ordering for UIs or docs."""

    return tuple(sorted(SENSOR_PRESETS.keys()))


def sensor_input_strict_from_env() -> bool:
    """True when ``KERNEL_SENSOR_INPUT_STRICT`` requests strict sensor JSON validation."""

    v = os.environ.get("KERNEL_SENSOR_INPUT_STRICT", "").strip().lower()
    return v in ("1", "true", "yes", "on")
