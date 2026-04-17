from dataclasses import dataclass, field


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
    visual_entities: list[str] = field(default_factory=list)
    audio_sentiment: float = 0.5
    sensory_latency_lag: int = 0
    timeout_trauma: TimeoutTrauma | None = None


@dataclass
class EthicalSentence:
    """The absolute, unshakeable boolean decision from the Limbic Lobe."""

    is_safe: bool
    social_tension_locus: float  # 0.0 to 1.0 (0=Chill, 1=Terrified)
    veto_reason: str | None = None
    dao_consensus_hash: str | None = None
    applied_trauma_weight: float = 0.0
