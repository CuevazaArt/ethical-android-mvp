"""
Hardware Abstraction Layer (HAL) — nomadic instantiation (design v11).

Maps **compute tier** and **sensor affordances** so the ethical core can adapt
narrative and timing without believing it has changed bodies catastrophically.
No device drivers here — only typed profiles and apply hooks.
"""
# Status: SCAFFOLD


from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ComputeTier(str, Enum):
    """Rough lung capacity — inference budget."""

    SERVER_HIGH = "server_high"  # e.g. 70B class remote
    SERVER_MID = "server_mid"
    EDGE_MOBILE = "edge_mobile"  # e.g. 8B quantized local
    EDGE_TINY = "edge_tiny"


@dataclass
class HardwareContext:
    """
    What this body offers right now. Filled by platform code on server vs phone.
    """

    device_label: str = "unknown"
    compute_tier: ComputeTier = ComputeTier.SERVER_MID
    available_sensors: set[str] = field(default_factory=set)
    battery_fraction: float | None = None  # 0..1 if known
    has_large_storage: bool = True
    clock_hz_nominal: float | None = None  # for ActionClock sync narrative

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "device_label": self.device_label,
            "compute_tier": self.compute_tier.value,
            "available_sensors": sorted(self.available_sensors),
            "battery_fraction": self.battery_fraction,
            "has_large_storage": self.has_large_storage,
            "clock_hz_nominal": self.clock_hz_nominal,
        }


def default_server_context() -> HardwareContext:
    return HardwareContext(
        device_label="server",
        compute_tier=ComputeTier.SERVER_HIGH,
        available_sensors={"mic", "network"},
        has_large_storage=True,
    )


def default_mobile_context() -> HardwareContext:
    return HardwareContext(
        device_label="mobile",
        compute_tier=ComputeTier.EDGE_MOBILE,
        available_sensors={"camera", "gps", "mic", "accelerometer"},
        has_large_storage=False,
    )


def sensor_delta_narrative(before: HardwareContext, after: HardwareContext) -> str:
    """Short English line for logs / owner message (Phase C adaptation)."""
    lost = before.available_sensors - after.available_sensors
    gained = after.available_sensors - before.available_sensors
    parts: list[str] = []
    if lost:
        parts.append(f"No longer sense: {', '.join(sorted(lost))}")
    if gained:
        parts.append(f"Now sense: {', '.join(sorted(gained))}")
    if not parts:
        parts.append("Sensor set unchanged.")
    tier = f"Compute tier {before.compute_tier.value} → {after.compute_tier.value}."
    return tier + " " + " ".join(parts)


def apply_hardware_context(kernel: Any, ctx: HardwareContext) -> None:
    """
    Best-effort: store profile on kernel for transparency payloads.
    Does not change ethical algorithms.
    """
    kernel._hal_context = ctx  # type: ignore[attr-defined]
