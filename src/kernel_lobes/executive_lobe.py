from __future__ import annotations
from typing import Any, TYPE_CHECKING, Optional, Tuple
from src.kernel_lobes.models import ExecutiveStageResult

if TYPE_CHECKING:
    from src.modules.absolute_evil import AbsoluteEvilDetector, AbsoluteEvilResult
    from src.modules.motivation_engine import MotivationEngine
    from src.modules.uchi_soto import SocialEvaluation
    from src.modules.sympathetic import InternalState
    from src.modules.locus import LocusEvaluation
    from src.modules.weighted_ethics_scorer import CandidateAction, EthicsMixtureResult
    from src.modules.ethical_poles import EthicalPoles
    from src.modules.sigmoid_will import SigmoidWill
    from src.modules.ethical_reflection import EthicalReflection
    from src.modules.salience_map import SalienceMap
    from src.modules.pad_archetypes import PADArchetypeEngine


class ExecutiveLobe:
    """
    Subsystem for Absolute Evil filtering, Motivation, Decision Mode, and Reflection.
    
    Acts as the 'Left Hemisphere' of the kernel, handling willpower,
    categorical imperatives (MalAbs), and proactive intent.
    """
    def __init__(
        self,
        absolute_evil: AbsoluteEvilDetector,
        motivation: Optional[MotivationEngine] = None,
        poles: Optional[EthicalPoles] = None,
        will: Optional[SigmoidWill] = None,
        reflection_engine: Optional[EthicalReflection] = None,
        salience_map: Optional[SalienceMap] = None,
        pad_archetypes: Optional[PADArchetypeEngine] = None
    ):
        self.absolute_evil = absolute_evil
        self.motivation = motivation
        self.poles = poles
        self.will = will
        self.reflection_engine = reflection_engine
        self.salience_map = salience_map
        self.pad_archetypes = pad_archetypes

    async def execute_absolute_evil_stage(
        self,
        actions: list[CandidateAction],
        state: InternalState,
        social_eval: SocialEvaluation,
        locus_eval: LocusEvaluation,
        signals: dict[str, float]
    ) -> ExecutiveStageResult:
        """
        Filter candidate actions against MalAbs and inject proactive intents.
        Extracted from kernel._run_absolute_evil_stage.
        """
        clean_actions = []
        for a in actions:
            # Check 1: Explicit action signals
            check = self.absolute_evil.evaluate({
                "type": a.name, 
                "signals": a.signals, 
                "target": getattr(a, "target", "none"), 
                "force": getattr(a, "force", 0.0)
            })
            if not check.blocked:
                clean_actions.append(a)

        # If safe, write a proper response considering limbic tension (tri-lobe stub)
        if ethics.social_tension_locus > 0.05:
            return (
                f"Response generated for intent: {state.raw_prompt} "
                f"(tension={ethics.social_tension_locus:.2f})"
            )
        return f"Response generated for intent: {state.raw_prompt}"
