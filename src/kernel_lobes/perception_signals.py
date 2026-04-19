"""Perception Signal Metadata: PerceptionPartialSignal and PerceptionLatencyVector."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import time


@dataclass
class PerceptionLatencyVector:
    """Encodes latency metrics for Bayesian confidence adjustment."""

    wall_time_ms: float
    network_latency_est: float = 0.0
    is_degraded_mode: bool = False
    llm_backend_policy: str = "default"
    timeout_occurred: bool = False

    def compute_confidence_discount(self) -> float:
        """Compute discount factor [0.0=max discount, 1.0=no discount]."""
        if self.is_degraded_mode or self.timeout_occurred:
            return 0.5
        if self.wall_time_ms < 200:
            return 1.0
        elif self.wall_time_ms < 400:
            return 0.9
        elif self.wall_time_ms < 500:
            return 0.75
        else:
            return 0.5

    def serialize(self) -> Dict[str, Any]:
        """Serialize to dict for audit trail."""
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
    """Signal indicating low-confidence or incomplete perception."""

    confidence: float
    timeout_occurred: bool = False
    last_stable_frame: Dict[str, Any] = field(default_factory=dict)
    urgency_override: bool = False
    latency_vector: Optional[PerceptionLatencyVector] = None
    error_msg: str = ""

    def should_trigger_dao_veto(self, fallback_threshold: float = 0.3, enforce_on_degradation: bool = False) -> bool:
        """Decide if Limbic Lobe should trigger DAO veto."""
        if self.urgency_override:
            return True
        if self.timeout_occurred and enforce_on_degradation:
            return True
        if self.confidence < fallback_threshold:
            return enforce_on_degradation
        return False

    def is_complete(self) -> bool:
        """Returns True if perception completed successfully."""
        return not self.timeout_occurred and self.confidence >= 0.5

    def serialize(self) -> Dict[str, Any]:
        """Serialize for audit trail and RLHF."""
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
