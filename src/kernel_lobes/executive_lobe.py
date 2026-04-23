from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Tuple

from src.kernel_lobes.models import EthicalSentence, ExecutiveStageResult, SemanticState

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
        absolute_evil: Optional["AbsoluteEvilDetector"] = None,
        motivation: Optional[MotivationEngine] = None,
        poles: Optional[EthicalPoles] = None,
        will: Optional[SigmoidWill] = None,
        reflection_engine: Optional[EthicalReflection] = None,
        salience_map: Optional[SalienceMap] = None,
        pad_archetypes: Optional[PADArchetypeEngine] = None,
    ) -> None:
        if absolute_evil is None:
            from src.modules.absolute_evil import AbsoluteEvilDetector

            absolute_evil = AbsoluteEvilDetector()
        self.absolute_evil = absolute_evil
        self.motivation = motivation
        self.poles = poles
        self.will = will
        self.reflection_engine = reflection_engine
        self.salience_map = salience_map
        self.pad_archetypes = pad_archetypes

    def execute_absolute_evil_stage(
        self,
        actions: list[CandidateAction],
        state: InternalState,
        social_eval: SocialEvaluation,
        locus_eval: LocusEvaluation,
        signals: dict[str, Any],
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

        # 2. Update and inject proactive motivations
        if self.motivation:
            self.motivation.update_drives({
                "social_tension": float(getattr(social_eval, "relational_tension", 0.0)),
                "uncertainty": float(signals.get("uncertainty", 0.0)), 
                "energy": float(state.energy)
            })
            for pa in self.motivation.get_proactive_actions():
                # Filter proactive actions too!
                if not self.absolute_evil.evaluate({"type": pa.name, "signals": set()}).blocked:
                    clean_actions.append(pa)

        return ExecutiveStageResult(
            clean_actions=clean_actions
        )

    def execute_decision_stage(
        self,
        bayes_result: EthicsMixtureResult,
        state: InternalState,
        social_eval: SocialEvaluation,
        locus_eval: LocusEvaluation,
        signals: dict[str, Any],
        context: str,
        meta_report: Any = None
    ) -> Tuple[Any, str, str, Any, Any, Any]:
        """
        Execute Stage 4: Decision, Will, Reflection, Salience and Affect.
        Extracted from kernel._run_decision_and_will_stage.
        """
        # 1. Ethical Poles Evaluation
        moral = self.poles.evaluate(bayes_result.chosen_action.name, context, {
            "risk": signals.get("risk", 0.0), 
            "benefit": max(0, bayes_result.expected_impact),
            "third_party_vulnerability": signals.get("vulnerability", 0.0), 
            "legality": signals.get("legality", 1.0)
        })

        # 2. Will Decision
        will_dec = self.will.decide(bayes_result.expected_impact, bayes_result.uncertainty)
        
        # 3. Decision Mode Finalization
        if state.mode == "sympathetic" and will_dec["mode"] != "gray_zone":
            final_mode = "D_fast"
        elif will_dec["mode"] == "gray_zone":
            final_mode = "gray_zone"
        else:
            final_mode = bayes_result.decision_mode

        # 4. Reflection
        reflection = self.reflection_engine.reflect(moral, bayes_result, will_dec)

        # 5. Salience
        curiosity = getattr(meta_report, "curiosity_weight", 0.0) if meta_report else 0.0
        salience = self.salience_map.compute(signals, state, social_eval, reflection, curiosity=curiosity)

        # 6. Affective Projection
        affect = self.pad_archetypes.project(state.sigma, moral.total_score, locus_eval)
        
        return moral, bayes_result.chosen_action.name, final_mode, affect, reflection, salience

    def judge_action_lethality(self, action_data: dict[str, Any]) -> bool:
        """Categorical veto helper."""
        return self.absolute_evil.evaluate(action_data).blocked

    def formulate_response(self, semantic_state: SemanticState, ethical_sentence: EthicalSentence) -> str:
        """V1.5 stack demo string (``CorpusCallosumOrchestrator`` / ``tests/test_kernel_lobes_stack``)."""
        if ethical_sentence.social_tension_locus > 0.4:
            return f"Response generated with tension={ethical_sentence.social_tension_locus:.2f}"
        return "Response generated (formal dialectic synthesis)"
