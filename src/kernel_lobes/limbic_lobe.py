from src.kernel_lobes.models import SemanticState, EthicalSentence
from src.modules.persistent_threat_tracker import PersistentThreatTracker


class LimbicEthicalLobe:
    """
    Hemisferio Derecho: Pure Sync CPU Engine.
    DAO Enforcement, Uchi-Soto, AbsoluteEvilDetector, Bayesian Updates.
    Does NOT connect to the internet.

    Bloque 9.2: Persistent Threat Tracking + Limbic Tension Escalation
    - Tracks sustained perception hazards (timeout, low confidence >5s)
    - Auto-escalates relational_tension without explicit text input
    - Tension levels: mild (1s) → medium (3s) → high (5s)
    """
    def __init__(self):
        # TODO(Claude): Migrate AbsoluteEvilDetector, MultiRealmGovernance here
        self.threat_tracker = PersistentThreatTracker()
        self.relational_tension: float = 0.0

    def judge(self, state: SemanticState) -> EthicalSentence:
        """
        Pure mathematical gating.
        Takes the SemanticState, runs it through local validators.

        Bloque 9.2: Escalates relational_tension on persistent threats.
        """
        if state.timeout_trauma:
            # TODO: Add penalty to Bayesian Trust if Trauma occurred
            pass

        # Bloque 9.2: Update threat tracking from perception signals
        threat_load = 0.0
        confidence = 0.5

        if hasattr(state, 'perception_signal') and state.perception_signal:
            # If perception timed out or low confidence, treat as threat
            threat_load = 0.5 if state.perception_signal.timeout_occurred else 0.0
            confidence = state.perception_signal.confidence if hasattr(state.perception_signal, 'confidence') else 0.5

        # Update threat tracker and get escalation level
        escalation_level = self.threat_tracker.update_threat_load(threat_load, confidence)

        # Apply tension modulation based on escalation
        tension_delta = self.threat_tracker.get_limbic_tension_delta()
        self.relational_tension = max(0.0, min(1.0, self.relational_tension + tension_delta * 0.1))

        # Stub logic
        return EthicalSentence(
            is_safe=True,
            social_tension_locus=self.relational_tension
        )

    def reset_threat_tracking(self):
        """Reset threat tracker for clean state (used in testing/restart)."""
        self.threat_tracker.reset()
        self.relational_tension = 0.0
