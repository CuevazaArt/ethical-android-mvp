"""
Shared types for the Narrative module to avoid circular imports.
"""

from dataclasses import dataclass

@dataclass
class BodyState:
    """Physical state of the android at the time of the episode."""

    energy: float = 1.0
    active_nodes: int = 8
    sensors_ok: bool = True
    description: str = ""


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
