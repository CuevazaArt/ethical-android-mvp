"""
Migratory Identity Service (Block 4.3: C5).
Handles the transition between different hardware bodies while preserving narrative continuity.
"""
# Status: SCAFFOLD

from __future__ import annotations

import logging

from src.modules.memory.narrative_types import BodyState, HardwareProfile

_log = logging.getLogger(__name__)


class BodyRegistry:
    """Registry of known hardware profiles and their capabilities."""

    @staticmethod
    def get_capabilities(profile: HardwareProfile) -> list[str]:
        if profile == HardwareProfile.ANDROID:
            return ["vision", "audio", "tactile", "locomotion_bipedal", "voice_synth"]
        elif profile == HardwareProfile.DRONE:
            return ["vision_ir", "audio_ultra", "locomotion_aerial", "lidar"]
        elif profile == HardwareProfile.MOBILE:
            return ["vision_2d", "audio", "gps", "accelerometer"]
        elif profile == HardwareProfile.STATIONARY:
            return ["vision_static", "audio", "network_monitor"]
        elif profile == HardwareProfile.SATELLITE:
            return ["vision_hyperspectral", "orbital_telemetry"]
        return []


def create_body_state(
    profile: HardwareProfile, hardware_id: str, energy: float = 1.0, description: str = ""
) -> BodyState:
    """Factory to create a BodyState with the correct capabilities for a profile."""
    return BodyState(
        energy=energy,
        hardware_profile=profile,
        hardware_id=hardware_id,
        capabilities=BodyRegistry.get_capabilities(profile),
        description=description,
    )


class MigrationHub:
    """Coordinates the soul-to-body binding process."""

    def __init__(self, current_body: BodyState | None = None):
        if current_body:
            self.current_body = current_body
        else:
            self.current_body = create_body_state(HardwareProfile.ANDROID, "boot_body_01")

    def migrate_to(self, new_profile: HardwareProfile, new_id: str):
        """Transitions the kernel to a new physical form factor."""
        # Preserve energy levels if migrating 'alive' (simulated)
        prev_energy = self.current_body.energy

        self.current_body = create_body_state(
            profile=new_profile,
            hardware_id=new_id,
            energy=prev_energy,
            description=f"Migrated from {self.current_body.hardware_profile.value} ({self.current_body.hardware_id})",
        )
        _log.info("Kernel successfully bound to %s body (ID: %s)", new_profile.value, new_id)
        return self.current_body
