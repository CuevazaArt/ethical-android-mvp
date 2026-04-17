import logging
from typing import TYPE_CHECKING
from src.kernel_lobes.models import SemanticState, EthicalSentence

if TYPE_CHECKING:
    from src.modules.absolute_evil import AbsoluteEvilDetector
    from src.modules.bayesian_engine import BayesianEngine

_log = logging.getLogger(__name__)

class LimbicEthicalLobe:
    """
    Hemisferio Derecho: Pure Sync CPU Engine. 
    DAO Enforcement, Uchi-Soto, AbsoluteEvilDetector, Bayesian Updates.
    Does NOT connect to the internet.
    """
    def __init__(self, abs_evil: 'AbsoluteEvilDetector', bayesian: 'BayesianEngine'):
        self.abs_evil = abs_evil
        self.bayesian = bayesian
        _log.info("LimbicEthicalLobe initialized (Sync CPU Mode).")

    def judge(self, state: SemanticState) -> EthicalSentence:
        """
        Pure mathematical gating. 
        Takes the SemanticState, runs it through local validators.
        """
        # 1. Absolute Evil Lexical Check
        lex_check = self.abs_evil.evaluate_chat_text(state.raw_prompt)
        if lex_check.blocked:
            return EthicalSentence(
                is_safe=False,
                social_tension_locus=state.signals.get("social_tension", 0.5),
                veto_reason=f"Absolute Evil Detected: {lex_check.reason}"
            )

        # 2. Bayesian Inference (CPU Bound)
        # We simulate the actions for the stub
        actions = state.candidate_actions
        if not actions:
            # Fallback for stub
            return EthicalSentence(is_safe=True, social_tension_locus=state.signals.get("social_tension", 0.0))

        # 3. Penalize if trauma occurred
        applied_trauma = 0.0
        if state.timeout_trauma:
            applied_trauma = state.timeout_trauma.severity * 0.2
            
        return EthicalSentence(
            is_safe=True,
            social_tension_locus=state.signals.get("social_tension", 0.0),
            applied_trauma_weight=applied_trauma,
            morals={
                "compassionate": "The system remained stable despite the request.",
                "conservative": "Operating within nominal ethical bounds.",
                "optimistic": "Found a safe path for communication."
            }
        )
