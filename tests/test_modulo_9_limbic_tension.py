"""
Tests for Module 9.2 Limbic Tension Accumulation.

Validates that threat persistence triggers escalating limbic tension,
affecting relational tone and decision urgency.

Integration chain:
  PerceptionPartialSignal.timeout_occurred OR confidence_low_sustained
  → PersistentThreatTracker.update_threat_load()
  → LimbicEthicalLobe.judge() applies escalation
  → relational_tension modulation based on threat duration
"""

from __future__ import annotations

import time
from unittest.mock import Mock

import pytest
from src.kernel_lobes.limbic_lobe import LimbicEthicalLobe
from src.kernel_lobes.models import SemanticState
from src.modules.memory.persistent_threat_tracker import PersistentThreatTracker


class TestThreatTrackerDetectsPersistentThreat:
    """Test: PersistentThreatTracker recognizes sustained threat."""

    def test_threat_tracker_detects_persistent_threat(self):
        """Threat present for >5s → high escalation level (3)."""
        tracker = PersistentThreatTracker()

        # Simulate threat being present
        level_1sec = tracker.update_threat_load(0.5, confidence=0.6)  # At t=0
        assert level_1sec == 0, "Immediate threat should be level 0"

        # Simulate time passage (1 second threat)
        tracker.state.first_threat_detected_at = time.time() - 1.5
        level_after_1s = tracker.update_threat_load(0.5, confidence=0.6)
        assert level_after_1s == 1, "After 1.5s should escalate to mild (level 1)"

        # Simulate 3 second threat
        tracker.state.first_threat_detected_at = time.time() - 3.5
        level_after_3s = tracker.update_threat_load(0.5, confidence=0.6)
        assert level_after_3s == 2, "After 3.5s should escalate to medium (level 2)"

        # Simulate 5 second threat
        tracker.state.first_threat_detected_at = time.time() - 5.5
        level_after_5s = tracker.update_threat_load(0.5, confidence=0.6)
        assert level_after_5s == 3, "After 5.5s should escalate to high (level 3)"


class TestThreatTrackerResetsOnThreatCleared:
    """Test: Threat counter resets when threat_load drops to zero."""

    def test_threat_tracker_resets_on_threat_cleared(self):
        """threat_load = 0 → counter reset, tension released."""
        tracker = PersistentThreatTracker()

        # Build up threat
        tracker.update_threat_load(0.5, confidence=0.6)
        tracker.state.first_threat_detected_at = time.time() - 6.0
        tracker.update_threat_load(0.5, confidence=0.6)  # Now at high level (3)

        assert tracker.state.threat_level == 3, "Should be at high level"
        assert tracker.state.first_threat_detected_at is not None

        # Clear threat
        tracker.update_threat_load(0.0, confidence=0.9)

        assert tracker.state.threat_level == 0, "Threat level should reset to 0"
        assert tracker.state.first_threat_detected_at is None, "Start time should clear"
        assert tracker.state.threat_duration_sec == 0.0, "Duration should reset"


class TestMildEscalationAt1Second:
    """Test: After 1s sustained threat, mild escalation."""

    def test_mild_escalation_at_1_second(self):
        """relational_tension increases after 1s sustained threat."""
        limbic = LimbicEthicalLobe()
        initial_tension = limbic.relational_tension

        # Create perception signal with timeout
        state = Mock(spec=SemanticState)
        state.timeout_trauma = False
        state.perception_signal = Mock()
        state.perception_signal.timeout_occurred = True
        state.perception_signal.confidence = 0.3

        # Judge with timeout threat
        limbic.threat_tracker.state.first_threat_detected_at = time.time() - 1.5
        limbic.judge(state)

        # Tension should have increased (mild escalation = 0.05)
        assert limbic.relational_tension > initial_tension, (
            f"Tension should increase after 1s threat "
            f"(was {initial_tension}, now {limbic.relational_tension})"
        )


class TestMediumEscalationAt3Seconds:
    """Test: After 3s sustained threat, medium escalation."""

    def test_medium_escalation_at_3_seconds(self):
        """relational_tension increases more after 3s sustained threat."""
        limbic = LimbicEthicalLobe()
        state = Mock(spec=SemanticState)
        state.timeout_trauma = False
        state.perception_signal = Mock()
        state.perception_signal.timeout_occurred = True
        state.perception_signal.confidence = 0.2

        # 1s threat
        limbic.threat_tracker.state.first_threat_detected_at = time.time() - 1.5
        limbic.judge(state)
        tension_after_1s = limbic.relational_tension

        # 3s threat
        limbic.reset_threat_tracking()
        limbic.threat_tracker.state.first_threat_detected_at = time.time() - 3.5
        limbic.judge(state)
        tension_after_3s = limbic.relational_tension

        assert tension_after_3s > tension_after_1s, (
            f"3s threat should increase tension more than 1s "
            f"(1s={tension_after_1s}, 3s={tension_after_3s})"
        )


class TestHighEscalationAt5Seconds:
    """Test: After 5s sustained threat, high escalation."""

    def test_high_escalation_at_5_seconds(self):
        """relational_tension increases significantly after 5s sustained threat."""
        limbic = LimbicEthicalLobe()
        state = Mock(spec=SemanticState)
        state.timeout_trauma = False
        state.perception_signal = Mock()
        state.perception_signal.timeout_occurred = True
        state.perception_signal.confidence = 0.1

        # Simulate 5s sustained threat
        limbic.threat_tracker.state.first_threat_detected_at = time.time() - 5.5
        limbic.judge(state)

        # After high escalation (0.30 delta), tension should be significant
        assert limbic.relational_tension > 0.02, (
            f"After 5s threat, tension should be elevated (got {limbic.relational_tension})"
        )


class TestLimbicLobeApplicationOfThreatEscalation:
    """Test: Limbic lobe applies threat escalation to relational tension."""

    def test_limbic_lobe_applies_threat_escalation_to_tension(self):
        """Limbic lobe escalates tension in response to threat."""
        limbic = LimbicEthicalLobe()
        state = Mock(spec=SemanticState)
        state.timeout_trauma = False
        state.perception_signal = Mock()
        state.perception_signal.timeout_occurred = True
        state.perception_signal.confidence = 0.2

        initial_tension = limbic.relational_tension

        # Apply threat for 2 seconds
        limbic.threat_tracker.state.first_threat_detected_at = time.time() - 2.0
        result = limbic.judge(state)

        assert limbic.relational_tension > initial_tension, (
            "Limbic lobe should escalate tension under sustained threat"
        )
        assert "social_tension_locus" in result.__dict__, (
            "Result should include social_tension_locus"
        )


class TestThreatLoadZeroNoEscalation:
    """Test: threat_load=0 → no tension escalation."""

    def test_threat_load_zero_no_escalation(self):
        """threat_load = 0 → tension unchanged."""
        limbic = LimbicEthicalLobe()
        state = Mock(spec=SemanticState)
        state.timeout_trauma = False
        state.perception_signal = Mock()
        state.perception_signal.timeout_occurred = False
        state.perception_signal.confidence = 0.9

        initial_tension = limbic.relational_tension
        limbic.judge(state)

        # No threat, so no tension increase
        assert limbic.relational_tension == initial_tension, (
            f"With zero threat, tension should not increase "
            f"(was {initial_tension}, now {limbic.relational_tension})"
        )


class TestMultipleThreatSequence:
    """Test: Threat sequences are tracked correctly."""

    def test_threat_sequence_tracking(self):
        """Multiple threat events are recorded in escalation_events."""
        tracker = PersistentThreatTracker()

        # Threat 1: mild (1s)
        tracker.state.first_threat_detected_at = time.time() - 1.5
        tracker.update_threat_load(0.5, 0.6)
        assert tracker.state.threat_level == 1

        # Threat 2: medium (3.5s)
        tracker.state.first_threat_detected_at = time.time() - 3.5
        tracker.update_threat_load(0.5, 0.6)
        assert tracker.state.threat_level == 2

        # Threat 3: high (5.5s)
        tracker.state.first_threat_detected_at = time.time() - 5.5
        tracker.update_threat_load(0.5, 0.6)
        assert tracker.state.threat_level == 3

        # All escalations should be recorded
        assert len(tracker.state.escalation_events) >= 2, (
            f"Should record escalation events ({len(tracker.state.escalation_events)} recorded)"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
