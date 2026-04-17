from __future__ import annotations

from src.kernel_lobes.models import EthicalSentence, SemanticState


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


class LimbicEthicalLobe:
    """
    Hemisferio Derecho: Pure Sync CPU Engine.
    DAO Enforcement, Uchi-Soto, AbsoluteEvilDetector, Bayesian Updates.
    Does NOT connect to the internet.
    """

    def __init__(self):
        # TODO(Claude): Migrate AbsoluteEvilDetector, MultiRealmGovernance here
        pass

    def judge(self, state: SemanticState) -> EthicalSentence:
        """
        Pure mathematical gating.
        Takes the SemanticState, runs it through local validators.
        """
        applied = 0.0
        tension = 0.0
        if state.timeout_trauma is not None:
            tt = state.timeout_trauma
            sev = _clamp01(tt.severity)
            conf = _clamp01(state.perception_confidence)
            # Cooperative I/O failure increases limbic load without veto (stub stack).
            applied = sev * 0.25
            tension = _clamp01(0.55 * sev + 0.45 * (1.0 - conf))
        return EthicalSentence(
            is_safe=True,
            social_tension_locus=tension,
            applied_trauma_weight=applied,
        )
