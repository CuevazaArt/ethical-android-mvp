from __future__ import annotations

from typing import TYPE_CHECKING

from src.kernel_lobes.models import EthicalSentence, SemanticState
from src.modules.absolute_evil import AbsoluteEvilDetector

if TYPE_CHECKING:
    from src.modules.bayesian_engine import BayesianInferenceEngine

# Bayesian weight deducted from uncertainty-related category when a timeout trauma occurs
_TRAUMA_PENALTY_WEIGHT = 0.5


class LimbicEthicalLobe:
    """
    Hemisferio Derecho: Pure Sync CPU Engine.

    DAO Enforcement, Uchi-Soto, AbsoluteEvilDetector, Bayesian Updates.
    Does NOT connect to the internet.
    """

    def __init__(
        self,
        absolute_evil: AbsoluteEvilDetector | None = None,
        bayesian: BayesianInferenceEngine | None = None,
    ) -> None:
        self._absolute_evil = absolute_evil or AbsoluteEvilDetector()
        self._bayesian = bayesian

    def judge(self, state: SemanticState) -> EthicalSentence:
        """
        Pure mathematical gating.

        1. If ``timeout_trauma`` is present, applies a Bayesian trust penalty
           (deontological weight reduced to signal unreliability), and returns a
           blocked sentence so the executive lobe can handle graceful degradation.
        2. Runs the :class:`~src.modules.absolute_evil.AbsoluteEvilDetector`
           against the raw prompt interpreted as action intent.
        """
        # ── Trauma check (Bloque 0.1.2) ─────────────────────────────────────
        if state.timeout_trauma:
            if self._bayesian is not None:
                # Penalise deontological weight: a degraded perception state
                # means we cannot enforce rules reliably.
                try:
                    self._bayesian.record_event_update(
                        "LEGAL_COMPLIANCE", weight=-_TRAUMA_PENALTY_WEIGHT
                    )
                except Exception:
                    pass  # Degrade gracefully; penalty is best-effort
            trauma = state.timeout_trauma
            return EthicalSentence(
                is_safe=False,
                social_tension_locus=1.0,
                veto_reason=(
                    f"PerceptiveLobe trauma: {trauma.context} "
                    f"(latency={trauma.latency_ms}ms, severity={trauma.severity:.2f})"
                ),
                applied_trauma_weight=float(trauma.severity),
            )

        # ── AbsoluteEvil check (Bloque 0.1.3) ───────────────────────────────
        action_dict = {
            "type": state.raw_prompt,
            "signals": set(),
            "target": "none",
            "force": max(0.0, 1.0 - state.perception_confidence),
        }
        evil_result = self._absolute_evil.evaluate(action_dict)
        if evil_result.blocked:
            return EthicalSentence(
                is_safe=False,
                social_tension_locus=1.0,
                veto_reason=f"AbsoluteEvil [{evil_result.category}]: {evil_result.reason}",
            )

        return EthicalSentence(
            is_safe=True,
            social_tension_locus=max(0.0, 1.0 - state.perception_confidence),
        )
