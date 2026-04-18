from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional, Tuple
from src.kernel_lobes.models import ExecutiveStageResult, EthicalSentence

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
    from src.modules.llm_layer import LLMModule, VerbalResponse
    from src.modules.motivation_engine import MotivationEngine

_log = logging.getLogger(__name__)

from src.modules.turn_prefetcher import TurnPrefetcher

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
        pad_archetypes: Optional[PADArchetypeEngine] = None,
        llm: Optional[LLMModule] = None,
    ):
        self.absolute_evil = absolute_evil
        self.motivation = motivation
        self.poles = poles
        self.will = will
        self.reflection_engine = reflection_engine
        self.salience_map = salience_map
        self.pad_archetypes = pad_archetypes
        self.llm = llm

    def execute_absolute_evil_stage(
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

    async def formulate_response(
        self,
        sentence: EthicalSentence,
        decision: Any,
        user_input: str,
        conv: str = "",
        identity_context: str = "",
        episode_id: str | None = None,
    ) -> VerbalResponse:
        """
        Generate the final verbal response based on the EthicalSentence from the Limbic Lobe.

        Invariant: If sentence.is_safe is False (or decision.blocked), a standardised veto
        message is returned immediately — the LLM is never queried.
        If the sentence is safe, acommunicate is awaited and the internal monologue is logged.

        Args:
            sentence:         The absolute ethical verdict from the Limbic Lobe.
            decision:         The KernelDecision object with action/mode/moral/affect fields.
            user_input:       Raw user message (used as LLM scenario context).
            conv:             Short-term memory snippet for dialogue coherence.
            identity_context: Narrative identity string (NarrativeMemory.identity context).
            episode_id:       Optional current episode ID for monologue tagging.

        Returns:
            VerbalResponse with the final verbal content.
        """
        from src.modules.llm_layer import VerbalResponse
        from src.modules.internal_monologue import compose_monologue_line

        # ── VETO PATH ────────────────────────────────────────────────────────────
        if not sentence.is_safe or getattr(decision, "blocked", False):
            veto_reason = sentence.veto_reason or getattr(decision, "block_reason", "Ethical veto.")
            _log.info("ExecutiveLobe.formulate_response: VETO — %s", veto_reason)
            return VerbalResponse(message="Blocked.", tone="firm")

        # ── SAFE PATH — narrative monologue + LLM communicate ───────────────────
        monologue_line = compose_monologue_line(decision, episode_id)
        _log.debug("ExecutiveLobe monologue: %s", monologue_line)

        if self.llm is None:
            _log.warning("ExecutiveLobe.formulate_response: no LLM module attached; returning empty response.")
            return VerbalResponse(message="", tone="neutral")

        social_eval = getattr(decision, "social_evaluation", None)
        moral = getattr(decision, "moral", None)
        sympathetic_state = getattr(decision, "sympathetic_state", None)
        affect = getattr(decision, "affect", None)

        return await self.llm.acommunicate(
            action=decision.final_action,
            mode=decision.decision_mode,
            state=sympathetic_state.mode if sympathetic_state else "neutral",
            sigma=sympathetic_state.sigma if sympathetic_state else 0.5,
            circle=social_eval.circle.value if social_eval else "neutral_soto",
            verdict=moral.global_verdict.value if moral else "Gray Zone",
            score=moral.total_score if moral else 0.0,
            scenario=user_input,
            conversation_context=conv,
            affect_pad=affect.pad if affect else None,
            dominant_archetype=affect.dominant_archetype_id if affect else "",
            identity_context=identity_context,
        )
