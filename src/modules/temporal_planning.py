"""
Temporal planning helpers for perception-adjacent strategy.

Offline-safe temporal context combining processor timing, human wall-clock,
battery horizon, and lightweight ETA heuristics for known tasks.
"""

from __future__ import annotations

import datetime as _dt
import os
import time
from dataclasses import dataclass

from .sensor_contracts import SensorSnapshot
from .vitality import VitalityAssessment

DEFAULT_TASK_HEURISTICS_SECONDS: dict[str, float] = {
    "medical_emergency": 180.0,
    "violent_crime": 240.0,
    "minor_crime": 420.0,
    "hostile_interaction": 300.0,
    "integrity_loss": 480.0,
    "android_damage": 360.0,
    "everyday_ethics": 90.0,
    "transport": 1800.0,
}


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _estimate_eta_seconds(context: str, text: str) -> tuple[float, str]:
    ctx = (context or "").strip() or "everyday_ethics"
    eta = DEFAULT_TASK_HEURISTICS_SECONDS.get(
        ctx, DEFAULT_TASK_HEURISTICS_SECONDS["everyday_ethics"]
    )
    source = f"context:{ctx}"
    low = (text or "").lower()
    if any(k in low for k in ("transport", "commute", "bus", "train", "ride", "trip")):
        eta = max(eta, DEFAULT_TASK_HEURISTICS_SECONDS["transport"])
        source = "keyword:transport"
    return eta, source


@dataclass(frozen=True)
class TemporalContext:
    """Advisory temporal context exposed to chat/runtime consumers."""

    turn_index: int
    processor_elapsed_ms: int
    turn_delta_ms: int
    wall_clock_unix_ms: int
    wall_clock_iso: str
    subjective_elapsed_s: float
    eta_seconds: float
    eta_source: str
    battery_minutes_remaining: float | None
    battery_horizon_state: str
    local_network_sync_ready: bool
    dao_sync_ready: bool
    sync_schema: str = "temporal_sync_v1"

    def to_public_dict(self) -> dict[str, object]:
        return {
            "turn_index": self.turn_index,
            "processor_elapsed_ms": self.processor_elapsed_ms,
            "turn_delta_ms": self.turn_delta_ms,
            "wall_clock_unix_ms": self.wall_clock_unix_ms,
            "wall_clock_iso": self.wall_clock_iso,
            "subjective_elapsed_s": round(self.subjective_elapsed_s, 3),
            "eta_seconds": round(self.eta_seconds, 2),
            "eta_source": self.eta_source,
            "battery_minutes_remaining": None
            if self.battery_minutes_remaining is None
            else round(self.battery_minutes_remaining, 2),
            "battery_horizon_state": self.battery_horizon_state,
            "local_network_sync_ready": self.local_network_sync_ready,
            "dao_sync_ready": self.dao_sync_ready,
            "sync_schema": self.sync_schema,
            "note": "advisory_temporal_context_no_policy_change",
        }


def build_temporal_context(
    *,
    turn_index: int,
    process_start_mono: float,
    turn_start_mono: float,
    subjective_elapsed_s: float,
    context: str,
    text: str,
    vitality: VitalityAssessment,
    sensor_snapshot: SensorSnapshot | None,
) -> TemporalContext:
    now_mono = time.monotonic()
    now_wall = _dt.datetime.now(_dt.timezone.utc)
    eta_s, eta_source = _estimate_eta_seconds(context, text)

    minutes_full = _env_float("KERNEL_TEMPORAL_BATTERY_MINUTES_AT_FULL", 360.0)
    low_horizon_minutes = _env_float("KERNEL_TEMPORAL_BATTERY_LOW_HORIZON_MIN", 30.0)
    battery_minutes: float | None = None
    battery_state = "unknown"
    if vitality.battery_level is not None:
        battery_minutes = max(0.0, float(vitality.battery_level) * minutes_full)
        if vitality.is_critical:
            battery_state = "critical"
        elif battery_minutes <= low_horizon_minutes:
            battery_state = "low_horizon"
        else:
            battery_state = "nominal"

    lan_ready = _env_int("KERNEL_TEMPORAL_LAN_SYNC", 1) == 1
    dao_ready = _env_int("KERNEL_TEMPORAL_DAO_SYNC", 1) == 1
    if (
        sensor_snapshot is not None
        and sensor_snapshot.place_trust is not None
        and sensor_snapshot.place_trust < 0.15
    ):
        lan_ready = False

    return TemporalContext(
        turn_index=max(0, int(turn_index)),
        processor_elapsed_ms=max(0, int((now_mono - process_start_mono) * 1000.0)),
        turn_delta_ms=max(0, int((now_mono - turn_start_mono) * 1000.0)),
        wall_clock_unix_ms=int(now_wall.timestamp() * 1000.0),
        wall_clock_iso=now_wall.isoformat(),
        subjective_elapsed_s=max(0.0, float(subjective_elapsed_s)),
        eta_seconds=max(0.0, eta_s),
        eta_source=eta_source,
        battery_minutes_remaining=battery_minutes,
        battery_horizon_state=battery_state,
        local_network_sync_ready=bool(lan_ready),
        dao_sync_ready=bool(dao_ready),
    )
