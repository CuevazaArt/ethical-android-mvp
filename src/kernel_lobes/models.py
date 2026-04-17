from dataclasses import dataclass, field
from typing import Dict, Any, Optional

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
    timeout_trauma: Optional[TimeoutTrauma] = None

@dataclass
class EthicalSentence:
    """The absolute, unshakeable boolean decision from the Limbic Lobe."""
    is_safe: bool
    social_tension_locus: float  # 0.0 to 1.0 (0=Chill, 1=Terrified)
    veto_reason: Optional[str] = None
    dao_consensus_hash: Optional[str] = None
    applied_trauma_weight: float = 0.0
@dataclass
class LimbicStageResult:
    """Consolidated result from the Limbic Lobe (Social, State, Locus)."""
    social_evaluation: Any
    internal_state: Any
    locus_evaluation: Any

@dataclass
class ExecutiveStageResult:
    """Consolidated result from the Executive Lobe."""
    clean_actions: list[Any]
    decision: Optional[Any] = None

@dataclass
class BayesianStageMetadata:
    """Metadata output from STAGE 3: Bayesian Scoring."""
    mixture_posterior_alpha: Optional[tuple[float, float, float]] = None
    feedback_consistency: Optional[str] = None
    mixture_context_key: Optional[str] = None
    hierarchical_context_key: Optional[str] = None
    applied_mixture_weights: Optional[tuple[float, float, float]] = None
    bma_win_probabilities: Optional[dict[str, float]] = None
    bma_dirichlet_alpha: Optional[tuple[float, float, float]] = None
    bma_n_samples: Optional[int] = None
