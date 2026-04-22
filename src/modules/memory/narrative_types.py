"""
Shared types for the Narrative module to avoid circular imports.
"""

from dataclasses import dataclass, field
from enum import Enum


class HardwareProfile(Enum):
    """Supported form factors for Ethos Kernel migration."""

    ANDROID = "android"  # Humanoid / High-agency body
    DRONE = "drone"  # Aerial / Surveillance body
    MOBILE = "mobile"  # Handheld / Passenger body
    STATIONARY = "stationary"  # Fixed terminal / Enclave
    SATELLITE = "satellite"  # Orbital / Remote observer


@dataclass
class BodyState:
    """Physical state of the android/enclave at the time of the episode."""

    energy: float = 1.0
    active_nodes: int = 8
    sensors_ok: bool = True
    description: str = ""
    hardware_profile: HardwareProfile = HardwareProfile.ANDROID
    hardware_id: str = "default_body_01"
    capabilities: list[str] = field(default_factory=list)


@dataclass
class NarrativeEpisode:
    """A narrative cycle with beginning, development, conclusion, and morals."""

    id: str
    timestamp: str
    place: str
    event_description: str
    body_state: BodyState
    action_taken: str
    morals: dict  # pole -> moral
    verdict: str  # "Good", "Bad", "Gray Zone"
    ethical_score: float
    decision_mode: str  # "D_fast", "D_delib", "gray_zone"
    sigma: float  # Sympathetic state at the moment
    context: str  # Type: emergency, everyday, etc.
    affect_pad: tuple[float, float, float] | None = None
    affect_weights: dict[str, float] | None = None
    significance: float = 0.0  # [0, 1] how impactful this is for identity
    is_sensitive: bool = False  # True for traumatic/private events
    arc_id: str | None = None
    semantic_embedding: list[float] | None = None
    weights_snapshot: tuple[float, float, float] | None = None


@dataclass
class NarrativeArc:
    """A thematic group of linked episodes (Pilar de la Mente)."""

    id: str
    title: str
    context: str
    episodes_ids: list[str]
    start_timestamp: str
    end_timestamp: str | None = None
    predominant_archetype: str | None = None
    summary: str = ""
    is_active: bool = True


@dataclass
class NarrativeChronicle:
    """A high-level recursive summary of multiple episodes (Phase 13)."""

    id: str
    start_timestamp: str
    end_timestamp: str
    summary: str
    archetypal_resonance: str | None = None
    ethical_poles_summary: str | None = None
    significance_avg: float = 0.0
    episode_count: int = 0
    semantic_embedding: list[float] | None = None
