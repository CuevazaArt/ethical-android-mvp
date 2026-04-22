"""
Bloque 9.2: Persistent Threat Tracking and Limbic Tension Escalation.

Tracks sustained threat duration and triggers escalating limbic tension
when perception hazard persists (>1s mild, >3s medium, >5s high).

Integration chain:
  PerceptionPartialSignal.timeout_occurred OR confidence_low_sustained
  → PersistentThreatTracker.update_threat_load()
  → LimbicLobe.escalate_threat_tension()
  → relational_tension modulation
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class ThreatEscalationState:
    """Current threat escalation level and timing."""

    threat_level: int = 0  # 0=none, 1=mild (1s+), 2=medium (3s+), 3=high (5s+)
    first_threat_detected_at: float | None = None
    threat_duration_sec: float = 0.0
    last_update_at: float = field(default_factory=time.time)
    escalation_events: list[tuple[float, int]] = field(default_factory=list)  # (time, level)


class PersistentThreatTracker:
    """
    Tracks sustained threat duration and escalates limbic tension accordingly.

    Threat presence must persist for durations to trigger escalations:
    - 1 second: mild escalation (relational_tension += 0.05)
    - 3 seconds: medium escalation (relational_tension += 0.15)
    - 5 seconds: high escalation (relational_tension += 0.30)
    """

    def __init__(self):
        """Initialize threat tracker."""
        self.state = ThreatEscalationState()
        self.threat_load: float = 0.0
        self.confidence_low_count: int = 0  # Track consecutive low-confidence frames

    def update_threat_load(self, threat_load: float, confidence: float = 0.5) -> int:
        """
        Update threat load and track persistent threat duration.

        Args:
            threat_load: Perception threat score [0, 1] (0=safe, 1=maximum hazard)
            confidence: Perception confidence [0, 1]

        Returns:
            escalation_level: 0=none, 1=mild, 2=medium, 3=high
        """
        now = time.time()
        self.threat_load = threat_load

        # Track low confidence as a threat signal
        if confidence < 0.3:
            self.confidence_low_count += 1
        else:
            self.confidence_low_count = 0

        is_threat_present = threat_load > 0.1 or self.confidence_low_count > 3

        # Initialize threat start time if threat just detected
        if is_threat_present and self.state.first_threat_detected_at is None:
            self.state.first_threat_detected_at = now
            self.state.threat_level = 0

        # Clear threat if no longer present
        if not is_threat_present:
            if self.state.first_threat_detected_at is not None:
                self.state.threat_level = 0
                self.state.first_threat_detected_at = None
                self.state.threat_duration_sec = 0.0
            self.confidence_low_count = 0
            return 0

        # Calculate threat duration
        if self.state.first_threat_detected_at is not None:
            self.state.threat_duration_sec = now - self.state.first_threat_detected_at

        # Determine escalation level based on duration
        new_level = 0
        if self.state.threat_duration_sec >= 5.0:
            new_level = 3  # High escalation
        elif self.state.threat_duration_sec >= 3.0:
            new_level = 2  # Medium escalation
        elif self.state.threat_duration_sec >= 1.0:
            new_level = 1  # Mild escalation

        # Record escalation event if level changed
        if new_level != self.state.threat_level:
            self.state.escalation_events.append((now, new_level))
            self.state.threat_level = new_level

        self.state.last_update_at = now
        return new_level

    def get_limbic_tension_delta(self) -> float:
        """
        Calculate relational_tension adjustment based on current escalation.

        Returns:
            Tension delta to add to limbic_lobe.relational_tension
            - 0.0: no threat
            - 0.05: mild escalation (1s+)
            - 0.15: medium escalation (3s+)
            - 0.30: high escalation (5s+)
        """
        if self.state.threat_level == 0:
            return 0.0
        elif self.state.threat_level == 1:
            return 0.05
        elif self.state.threat_level == 2:
            return 0.15
        else:  # level 3
            return 0.30

    def reset(self):
        """Reset threat tracker to clean state."""
        self.state = ThreatEscalationState()
        self.threat_load = 0.0
        self.confidence_low_count = 0

    def get_state(self) -> ThreatEscalationState:
        """Get current threat escalation state (for diagnostics/testing)."""
        return self.state
