"""
Somatic Adapter Contract — Interface for Body State and Proprioception.

This module defines the structures for internal sensing: IMU (balance), 
Joint encoders (posture), and Motor current (effort/pain).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SomaticState:
    """Snapshot of the android's physical state."""
    # Orientation: (pitch, roll, yaw) in degrees
    orientation: tuple[float, float, float] = (0.0, 0.0, 0.0)
    
    # Acceleration: (x, y, z) in m/s^2
    acceleration: tuple[float, float, float] = (0.0, 0.0, 0.0)
    
    # Joint positions: dict mapping joint_id -> angle/position
    joint_positions: dict[str, float] = field(default_factory=dict)
    
    # Motor torque/effort: dict mapping joint_id -> normalized effort [0, 1]
    motor_effort: dict[str, float] = field(default_factory=dict)
    
    # Battery and thermal state
    battery_level: float = 1.0
    temperature: float = 25.0
    
    timestamp: float = 0.0


@dataclass
class SomaticInference:
    """Ethical interpretation of the somatic state."""
    is_falling: bool = False
    is_obstructed: bool = False
    physical_fatigue: float = 0.0  # [0, 1]
    stability_score: float = 1.0   # [0, 1]
    autonomy_threat: float = 0.0   # [0, 1] (low battery, high heat)


class SomaticAdapter(ABC):
    """
    Abstract base class for somatic sensing (Proprioception).
    """

    @abstractmethod
    def read_state(self) -> SomaticState:
        """Poll the physical sensors or hardware bridge."""
        pass

    @abstractmethod
    def infer(self, state: SomaticState) -> SomaticInference:
        """Translate raw telemetry into ethical/operational signals."""
        pass
