from __future__ import annotations
import logging
import time
import math
from typing import TYPE_CHECKING, Any, Optional, Tuple, Deque

from src.kernel_lobes.models import (
    ExecutiveStageResult, 
    EthicalSentence, 
    SensoryEpisode,
    SensorySpike,
    BayesianEcograde,
    MotorCommandDispatch,
    CognitivePulse
)
from src.modules.turn_prefetcher import TurnPrefetcher
from src.modules.basal_ganglia import BasalGanglia
from src.modules.llm_layer import VerbalResponse, LLMModule
from src.modules.internal_monologue import compose_monologue_line

if TYPE_CHECKING:
    from src.nervous_system.corpus_callosum import CorpusCallosum
    from src.modules.absolute_evil import AbsoluteEvilDetector
    from src.modules.ethical_poles import EthicalPoles
    from src.modules.ethical_reflection import EthicalReflection
    from src.modules.salience_map import SalienceMap
    from src.modules.pad_archetypes import PADArchetypeEngine

_log = logging.getLogger(__name__)


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
        bus: Optional[CorpusCallosum] = None,
    ):
        self.absolute_evil = absolute_evil
        self.motivation = motivation
        self.poles = poles
        self.will = will
        self.reflection_engine = reflection_engine
        self.salience_map = salience_map
        self.pad_archetypes = pad_archetypes
        self.llm = llm
        self.bus = bus
        
        self.ganglia = BasalGanglia() # Smoothing layer

        # Escuchar señales convergentes para decidir la acción final
        if self.bus:
            self.bus.subscribe(SensorySpike, self._on_sensory_event)
            self.bus.subscribe(BayesianEcograde, self._on_bayesian_math_update)
            self.bus.subscribe(CognitivePulse, self._on_cognitive_event)

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
        t0 = time.perf_counter()
        clean_actions = []
        try:
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
                def f_val(v, d=0.0):
                    f = float(v)
                    return f if math.isfinite(f) else d

                self.motivation.update_drives({
                    "social_tension": f_val(getattr(social_eval, "relational_tension", 0.0)),
                    "uncertainty": f_val(signals.get("uncertainty", 0.0)), 
                    "energy": f_val(state.energy, 1.0)
                })
                for pa in self.motivation.get_proactive_actions():
                    # Filter proactive actions too!
                    if not self.absolute_evil.evaluate({"type": pa.name, "signals": set()}).blocked:
                        clean_actions.append(pa)
        except Exception as e:
            _log.error("ExecutiveLobe: Error in absolute evil stage: %s", e)
        
        latency = (time.perf_counter() - t0) * 1000
        _log.debug("ExecutiveLobe: Absolute evil stage took %.2f ms", latency)
        
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
        t0 = time.perf_counter()
        
        # 0. Safety Check
        if not bayes_result or not hasattr(bayes_result, "chosen_action") or not bayes_result.chosen_action:
            _log.error("ExecutiveLobe: Missing bayesian result at decision stage.")
            return None, "system_error", "blocked", None, None, None

        try:
            # 1. Ethical Poles Evaluation
            # signals can be None if perception failed completely
            sig = signals or {}
            impact = float(getattr(bayes_result, "expected_impact", 0.0))
            if not math.isfinite(impact):
                impact = 0.0
                
            moral = self.poles.evaluate(bayes_result.chosen_action.name, context, {
                "risk": sig.get("risk", 0.0), 
                "benefit": max(0, impact),
                "third_party_vulnerability": sig.get("vulnerability", 0.0), 
                "legality": sig.get("legality", 1.0)
            })

            # 2. Will Decision
            uncertainty = float(getattr(bayes_result, "uncertainty", 0.0))
            if not math.isfinite(uncertainty):
                uncertainty = 0.5
            will_dec = self.will.decide(impact, uncertainty)
            
            # 3. Decision Mode Finalization (Phase 11.2 Shutdown Anxiety aligned)
            if getattr(bayes_result, "decision_mode", "") == "D_emergency":
                final_mode = "D_emergency"
            elif state.mode == "sympathetic" and will_dec.get("mode") != "gray_zone":
                final_mode = "D_fast"
            elif will_dec.get("mode") == "gray_zone":
                final_mode = "gray_zone"
            else:
                final_mode = getattr(bayes_result, "decision_mode", "D_delib")

            # 4. Reflection
            reflection = self.reflection_engine.reflect(moral, bayes_result, will_dec)

            # 5. Salience
            curiosity = float(getattr(meta_report, "curiosity_weight", 0.0)) if meta_report else 0.0
            if not math.isfinite(curiosity):
                curiosity = 0.0
            salience = self.salience_map.compute(signals, state, social_eval, reflection, curiosity=curiosity)

            # 6. Affective Projection (with Basal Ganglia smoothing)
            affect = self.pad_archetypes.project(state.sigma, moral.total_score, locus_eval)
            
            # Anti-NaN & Smooth the PAD vectors
            p = float(affect.pad[0]) if math.isfinite(affect.pad[0]) else 0.0
            a = float(affect.pad[1]) if math.isfinite(affect.pad[1]) else 0.0
            d = float(affect.pad[2]) if math.isfinite(affect.pad[2]) else 0.0
            
            affect.pad = (
                self.ganglia.smooth("pleasure", p),
                self.ganglia.smooth("arousal", a),
                self.ganglia.smooth("dominance", d)
            )
            
            # 7. Real-Time Hardware Projection (Phase 10.5)
            try:
                from src.modules.affect_projection_relay import get_affect_relay
                get_affect_relay().transmit(affect)
            except Exception as re_err:
                _log.error("ExecutiveLobe: Affective relay failed: %s", re_err)
                
            latency = (time.perf_counter() - t0) * 1000
            _log.debug("ExecutiveLobe: Decision stage took %.2f ms", latency)
                
            return moral, bayes_result.chosen_action.name, final_mode, affect, reflection, salience
            
        except Exception as e:
            _log.error("ExecutiveLobe: Critical error in decision stage: %s", e)
            return None, "stage_fault", "blocked", None, None, None

    def judge_action_lethality(self, action_data: dict[str, Any]) -> bool:
        """Categorical veto helper."""
        try:
            return self.absolute_evil.evaluate(action_data).blocked
        except Exception:
            return True # Fail shut

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
        """
        t0 = time.perf_counter()
        
        # ── VETO PATH ────────────────────────────────────────────────────────────
        if not sentence.is_safe or getattr(decision, "blocked", False):
            veto_reason = sentence.veto_reason or getattr(decision, "block_reason", "Ethical veto.")
            _log.info("ExecutiveLobe.formulate_response: VETO — %s", veto_reason)
            return VerbalResponse(message="Blocked.", tone="firm")

        # ── SAFE PATH — narrative monologue + LLM communicate ───────────────────
        try:
            monologue_line = compose_monologue_line(decision, episode_id)
            _log.debug("ExecutiveLobe monologue: %s", monologue_line)

            if self.llm is None:
                _log.warning("ExecutiveLobe.formulate_response: no LLM module attached; returning empty response.")
                return VerbalResponse(message="", tone="neutral")

            social_eval = getattr(decision, "social_evaluation", None)
            moral = getattr(decision, "moral", None)
            sympathetic_state = getattr(decision, "sympathetic_state", None)
            affect = getattr(decision, "affect", None)

            if not decision:
                _log.error("ExecutiveLobe: Missing decision object in formulate_response.")
                return VerbalResponse(message="I'm experiencing an internal processing error.", tone="neutral")

            response = await self.llm.acommunicate(
                action=getattr(decision, "final_action", "unknown"),
                mode=getattr(decision, "decision_mode", "light"),
                state=sympathetic_state.mode if sympathetic_state else "neutral",
                sigma=sympathetic_state.sigma if sympathetic_state else 0.5,
                circle=getattr(social_eval, "circle", None).value if (social_eval and hasattr(social_eval, "circle") and social_eval.circle) else "neutral_soto",
                verdict=getattr(moral, "global_verdict", None).value if (moral and hasattr(moral, "global_verdict") and moral.global_verdict) else "Gray Zone",
                score=float(getattr(moral, "total_score", 0.0)) if moral else 0.0,
                scenario=user_input,
                conversation_context=conv,
                affect_pad=affect.pad if affect else None,
                dominant_archetype=affect.dominant_archetype_id if affect else "",
                identity_context=identity_context,
            )
            
            latency = (time.perf_counter() - t0) * 1000
            _log.debug("ExecutiveLobe: Respone formulation took %.2f ms", latency)
            return response
            
        except Exception as e:
            _log.error("ExecutiveLobe: Error formulating response: %s", e)
    async def _on_sensory_event(self, spike: SensorySpike):
        """Prefrontal awareness of a new world stimulus."""
        _log.info(f"Córtex Prefrontal: Evaluando respuesta ejecutiva para Spike {spike.pulse_id}")
        # Aquí se iniciaría la planificación de la respuesta verbal o motora.

    async def _on_bayesian_math_update(self, grade: BayesianEcograde):
        """Prefrontal reaction to analytical moral computation from Cerebellum."""
        _log.info(f"Córtex Prefrontal: Recibido BayesianEcograde ({getattr(grade, 'moral_score', 0.0):.2f})")
        # In the future this will influence volition or reflection.
        pass
    async def _on_cognitive_event(self, pulse: CognitivePulse) -> None:
        """Process high-level mental states and deliberate actions."""
        if pulse.origin_lobe == "sensory_cortex" and pulse.state_ref:
            _log.info(f"Córtex Prefrontal: Evaluando decisión para la observación del Spike {pulse.ref_pulse_id}")
            
            # Swarm Rule 3: Latency Telemetry
            t0: float = time.perf_counter()
            
            # Perform Absolute Evil Check on the text
            from src.kernel_lobes.models import SemanticState
            state: SemanticState = pulse.state_ref
            text: str = state.raw_prompt if hasattr(state, "raw_prompt") else ""
            
            check = await self.absolute_evil.aevaluate_chat_text(text)
            
            latency_ms: float = (time.perf_counter() - t0) * 1000
            _log.debug(f"Córtex Prefrontal: Evaluación de seguridad completada en {latency_ms:.2f}ms")
            
            if check.blocked:
                _log.warning(f"Córtex Prefrontal: MAL ABSOLUTO DETECTADO ({getattr(check, 'reason', 'unknown')}). Veto Inmediato.")
                await self.dispatch_volition(action_id="blocked_by_malabs", is_vetoed=True, ref_pulse_id=pulse.ref_pulse_id)
                return
            
            _log.info("Córtex Prefrontal: Convergencia de seguridad lograda. Despachando Voluntad...")
            await self.dispatch_volition(action_id="say_hello", is_vetoed=False, ref_pulse_id=pulse.ref_pulse_id)

    async def dispatch_volition(self, action_id: str, is_vetoed: bool = False, ref_pulse_id: str | None = None):
        """Publish the final efferent command to the nervous system."""
        if self.bus:
            import time
            dispatch = MotorCommandDispatch(
                action_id=action_id,
                is_vetoed=is_vetoed,
                priority=1,
                timestamp=time.time(),
                ref_pulse_id=ref_pulse_id
            )
            await self.bus.publish(dispatch)
            _log.info(f"Córtex Prefrontal: VOLUNTAD DESPACHADA ({action_id}) | Vetoed: {is_vetoed} | Ref: {ref_pulse_id}")
