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
    significance: float = 0.0  # [0, 1] how impactful this is for identity
    is_sensitive: bool = False  # True for traumatic/private events
    arc_id: str | None = None
    semantic_embedding: list[float] | None = None


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
