from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Deque
from collections import deque
import time

@dataclass
class SensoryEpisode:
    """A single frame of continuous perception (Vision, Audio, Hardware)."""
    timestamp: float = field(default_factory=time.time)
    origin: str = "vision" # "vision", "audio", "somatic"
    entities: List[str] = field(default_factory=list) # ["human", "weapon", etc]
    signals: Dict[str, float] = field(default_factory=dict) # {"tension": 0.4}
    raw_data_ref: Optional[str] = None # Link to shared memory or file if heavy


@dataclass
class TimeoutTrauma:
    """Record of a cooperative timeout or sensory crash to punish the Bayesian model."""
    source_lobe: str
    latency_ms: int
    severity: float = 1.0
    context: str = "Network Unreachable / API Timeout"

@dataclass
class SemanticState:
    """Raw, unjudged semantic interpretation from the Perceptive Lobe."""
    perception_confidence: float
    raw_prompt: str
    scenario_summary: str
    suggested_context: str
    signals: Dict[str, float] = field(default_factory=dict)
    candidate_actions: list[Any] = field(default_factory=list)
    visual_entities: list[str] = field(default_factory=list)
    audio_sentiment: float = 0.5
    sensory_latency_lag: int = 0
    timeout_trauma: Optional[TimeoutTrauma] = None

@dataclass
class EthicalSentence:
    """The absolute, unshakeable boolean decision from the Limbic Lobe."""
    is_safe: bool
    social_tension_locus: float  # 0.0 to 1.0 (0=Chill, 1=Terrified)
    veto_reason: Optional[str] = None
    dao_consensus_hash: Optional[str] = None
    applied_trauma_weight: float = 0.0
    social_posture: str = "" # Tone/Attitude advisory for the Executive Lobe
    risk_vector: Dict[str, float] = field(default_factory=dict) # Fine-grained risk scores
    morals: Dict[str, str] = field(default_factory=dict)
