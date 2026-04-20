"""
Perception Signal Metadata: PerceptionPartialSignal and PerceptionLatencyVector.

These dataclasses bridge the Perceptive Lobe (async I/O) and Limbic Lobe (ethical judgment)
by encoding latency, confidence, and timeout state for Bayesian adjustment and DAO governance.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class PerceptionLatencyVector:
    """
    Encodes latency metrics that flow into Bayesian inference for confidence adjustment.

    The Limbic Lobe uses this to discount moral confidence when perception is slow or degraded.
    Example: If wall_time_ms > 400, the Bayesian posterior is shifted toward 0.5 (maximum uncertainty).
    """

    wall_time_ms: float
    """Real wall-clock time (ms) spent in Perceptive Lobe."""

    network_latency_est: float = 0.0
    """Estimated LLM API round-trip latency (ms). Helps distinguish network delay vs. computation."""

    is_degraded_mode: bool = False
    """True if LLM backend fell back to 'canned_safe' or 'fast_fail' policy."""

    llm_backend_policy: str = "default"
    """Policy applied: 'fast_fail', 'canned_safe', 'annotate_degraded', 'default'."""

    timeout_occurred: bool = False
    """True if a hard timeout (KERNEL_CHAT_TURN_TIMEOUT) interrupted perception."""

    def compute_confidence_discount(self) -> float:
        """
        Compute the discount factor to apply to Bayesian confidence.

        Returns:
            Float in [0.0, 1.0] representing confidence multiplier.
            - 1.0: full confidence, no discount (fast, clean perception)
            - 0.5: maximum discount (timeout or severe degradation)
        """
        if self.is_degraded_mode or self.timeout_occurred:
            return 0.5

        if self.wall_time_ms < 200:
            return 1.0  # Very fast, no discount
        elif self.wall_time_ms < 400:
            return 0.9  # Slight discount
        elif self.wall_time_ms < 500:
            return 0.75  # Moderate discount
        else:
            return 0.5  # Severe discount

    def serialize(self) -> Dict[str, Any]:
        """Serialize to dict for audit trail and RLHF feature extraction."""
        return {
            "wall_time_ms": self.wall_time_ms,
            "network_latency_est": self.network_latency_est,
            "is_degraded_mode": self.is_degraded_mode,
            "llm_backend_policy": self.llm_backend_policy,
            "timeout_occurred": self.timeout_occurred,
            "confidence_discount": self.compute_confidence_discount(),
        }


@dataclass
class PerceptionPartialSignal:
    """
    Signal emitted by Perceptive Lobe to indicate low-confidence or incomplete perception.

    Used by Limbic Lobe to decide whether to:
    1. Wait for complete perception
    2. Trigger DAO veto on incomplete context
    3. Register decision as "tentative" (Phase 1 of two-phase commit)
    """

    confidence: float
    """Perception confidence [0.0, 1.0]. Below 0.3 triggers fallback logic."""

    timeout_occurred: bool = False
    """True if asyncio.TimeoutError or httpx.TimeoutException occurred."""

    last_stable_frame: Dict[str, Any] = field(default_factory=dict)
    """Last successfully parsed perception state (visual/audio/sensor). Used as fallback."""

    urgency_override: bool = False
    """True if hardware state critical (temp > KERNEL_VITALITY_CRITICAL_TEMP, etc.)."""

    latency_vector: Optional[PerceptionLatencyVector] = None
    """Latency metadata for Bayesian adjustment."""

    error_msg: str = ""
    """Human-readable error or degradation reason."""

    def should_trigger_dao_veto(self, fallback_threshold: float = 0.3, enforce_on_degradation: bool = False) -> bool:
        """
        Decide if Limbic Lobe should trigger DAO veto despite incomplete perception.

        Args:
            fallback_threshold: Confidence threshold below which to consider veto.
            enforce_on_degradation: If True, veto on any degradation (timeout, low confidence).

        Returns:
            True if DAO veto should be registered immediately.
        """
        # E-stop (hardware critical) always triggers veto
        if self.urgency_override:
            return True

        # Timeout + degradation enforcement = veto
        if self.timeout_occurred and enforce_on_degradation:
            return True

        # Low confidence below fallback threshold
        if self.confidence < fallback_threshold:
            return enforce_on_degradation

        return False

    def is_complete(self) -> bool:
        """Returns True if perception completed successfully (no timeout, confidence > 0.5)."""
        return not self.timeout_occurred and self.confidence >= 0.5

    def serialize(self) -> Dict[str, Any]:
        """Serialize for audit trail and RLHF training."""
        result = {
            "confidence": self.confidence,
            "timeout_occurred": self.timeout_occurred,
            "urgency_override": self.urgency_override,
            "is_complete": self.is_complete(),
            "error_msg": self.error_msg,
        }
        if self.latency_vector:
            result["latency_metadata"] = self.latency_vector.serialize()
        return result
