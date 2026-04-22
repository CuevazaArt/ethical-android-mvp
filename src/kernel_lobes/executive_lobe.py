from __future__ import annotations

import asyncio
import logging
import math
import time
from typing import Any

from src.kernel_lobes.models import (
    BayesianEcograde,
    CognitivePulse,
    EthicalSentence,
    ExecutiveStageResult,
    GestaltSnapshot,
    SensorySpike,
)
from src.modules.ethics.absolute_evil import AbsoluteEvilDetector
from src.modules.cognition.basal_ganglia import BasalGanglia
from src.modules.ethics.ethical_poles import EthicalPoles
from src.modules.ethics.ethical_reflection import EthicalReflection
from src.modules.internal_monologue import compose_monologue_line
from src.modules.cognition.llm_layer import LLMModule, VerbalResponse
from src.modules.safety.locus import LocusEvaluation
from src.modules.cognition.motivation_engine import MotivationEngine
from src.modules.memory.narrative import NarrativeMemory
from src.modules.ethics.pad_archetypes import PADArchetypeEngine
from src.modules.cognition.salience_map import SalienceMap
from src.modules.cognition.sigmoid_will import SigmoidWill
from src.modules.somatic.sympathetic import InternalState
from src.modules.social.uchi_soto import SocialEvaluation
from src.modules.somatic.vitality import vitality_communication_hint
from src.modules.ethics.weighted_ethics_scorer import CandidateAction, EthicsMixtureResult
from src.nervous_system.corpus_callosum import CorpusCallosum

_log = logging.getLogger(__name__)


def _default_deliberation_decision_v13() -> Any:
    """
    Minimal limbic-shaped decision when the V13 bus invokes the executive directly
    from sensory cortex without a full limbic stage (decision=None at call site).
    Uses SimpleNamespace — not unittest mocks.
    """
    from types import SimpleNamespace

    circle = SimpleNamespace(value="neutral_soto")
    social = SimpleNamespace(circle=circle)
    verdict = SimpleNamespace(value="Gray Zone")
    moral = SimpleNamespace(global_verdict=verdict, total_score=0.0)
    affect = SimpleNamespace(pad=(0.0, 0.0, 0.0), dominant_archetype_id="neutral")
    sym = SimpleNamespace(mode="neutral", sigma=0.5)
    return SimpleNamespace(
        blocked=False,
        final_action="converse",
        decision_mode="light",
        salience=None,
        reflection=None,
        social_evaluation=social,
        moral=moral,
        sympathetic_state=sym,
        affect=affect,
    )


class ExecutiveLobe:
    """
    Subsystem for Absolute Evil filtering, Motivation, Decision Mode, and Reflection.

    Acts as the 'Left Hemisphere' of the kernel, handling willpower,
    categorical imperatives (MalAbs), and proactive intent.
    """

    def __init__(
        self,
        absolute_evil: AbsoluteEvilDetector,
        motivation: MotivationEngine | None = None,
        poles: EthicalPoles | None = None,
        will: SigmoidWill | None = None,
        reflection_engine: EthicalReflection | None = None,
        salience_map: SalienceMap | None = None,
        pad_archetypes: PADArchetypeEngine | None = None,
        llm: LLMModule | None = None,
        bus: CorpusCallosum | None = None,
        memory: NarrativeMemory | None = None,
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
        self.memory = memory

        self.ganglia = BasalGanglia()  # Smoothing layer

        # Escuchar señales convergentes para decidir la acción final
        if self.bus:
            self.bus.subscribe(SensorySpike, self._on_sensory_event)
            self.bus.subscribe(BayesianEcograde, self._on_bayesian_math_update)
            self.bus.subscribe(CognitivePulse, self._on_cognitive_event)
            from src.kernel_lobes.models import LimbicTensionAlert

            self.bus.subscribe(LimbicTensionAlert, self._on_limbic_tension)

        self._trauma_abort_active = False

    def execute_absolute_evil_stage(
        self,
        actions: list[CandidateAction],
        state: InternalState,
        social_eval: SocialEvaluation,
        locus_eval: LocusEvaluation,
        signals: dict[str, float],
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
                check = self.absolute_evil.evaluate(
                    {
                        "type": a.name,
                        "signals": a.signals,
                        "target": getattr(a, "target", "none"),
                        "force": getattr(a, "force", 0.0),
                    }
                )
                if not check.blocked:
                    clean_actions.append(a)

            # 2. Update and inject proactive motivations
            if self.motivation:

                def f_val(v, d=0.0):
                    f = float(v)
                    return f if math.isfinite(f) else d

                self.motivation.update_drives(
                    {
                        "social_tension": f_val(getattr(social_eval, "relational_tension", 0.0)),
                        "uncertainty": f_val(signals.get("uncertainty", 0.0)),
                        "energy": f_val(state.energy, 1.0),
                    }
                )
                for pa in self.motivation.get_proactive_actions():
                    # Filter proactive actions too!
                    if not self.absolute_evil.evaluate({"type": pa.name, "signals": set()}).blocked:
                        clean_actions.append(pa)
        except Exception as e:
            _log.error("ExecutiveLobe: Error in absolute evil stage: %s", e)

        latency = (time.perf_counter() - t0) * 1000
        _log.debug("ExecutiveLobe: Absolute evil stage took %.2f ms", latency)

        return ExecutiveStageResult(clean_actions=clean_actions)

    def execute_decision_stage(
        self,
        bayes_result: EthicsMixtureResult,
        state: InternalState,
        social_eval: SocialEvaluation,
        locus_eval: LocusEvaluation,
        signals: dict[str, Any],
        context: str,
        meta_report: Any = None,
    ) -> tuple[Any, str, str, Any, Any, Any]:
        """
        Execute Stage 4: Decision, Will, Reflection, Salience and Affect.
        Extracted from kernel._run_decision_and_will_stage.
        """
        t0 = time.perf_counter()

        # 0. Safety Check
        if (
            not bayes_result
            or not hasattr(bayes_result, "chosen_action")
            or not bayes_result.chosen_action
        ):
            _log.error("ExecutiveLobe: Missing bayesian result at decision stage.")
            return None, "system_error", "blocked", None, None, None

        try:
            # 1. Ethical Poles Evaluation
            # signals can be None if perception failed completely
            sig = signals or {}
            impact = float(getattr(bayes_result, "expected_impact", 0.0))
            if not math.isfinite(impact):
                impact = 0.0

            moral = self.poles.evaluate(
                bayes_result.chosen_action.name,
                context,
                {
                    "risk": sig.get("risk", 0.0),
                    "benefit": max(0, impact),
                    "third_party_vulnerability": sig.get("vulnerability", 0.0),
                    "legality": sig.get("legality", 1.0),
                },
            )

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
            salience = self.salience_map.compute(
                signals, state, social_eval, reflection, curiosity=curiosity
            )

            # 6. Affective Projection (with Basal Ganglia smoothing)
            affect = self.pad_archetypes.project(state.sigma, moral.total_score, locus_eval)

            # Anti-NaN & Smooth the PAD vectors
            p = float(affect.pad[0]) if math.isfinite(affect.pad[0]) else 0.0
            a = float(affect.pad[1]) if math.isfinite(affect.pad[1]) else 0.0
            d = float(affect.pad[2]) if math.isfinite(affect.pad[2]) else 0.0

            affect.pad = (
                self.ganglia.smooth("pleasure", p) if math.isfinite(p) else 0.0,
                self.ganglia.smooth("arousal", a) if math.isfinite(a) else 0.0,
                self.ganglia.smooth("dominance", d) if math.isfinite(d) else 0.0,
            )

            # 7. Real-Time Hardware Projection (Phase 10.5)
            try:
                from src.modules.somatic.affect_projection_relay import get_affect_relay

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
            return True  # Fail shut

    async def formulate_response(
        self,
        sentence: EthicalSentence,
        decision: Any,
        user_input: str,
        conv: str = "",
        identity_context: str = "",
        episode_id: str | None = None,
        stream_callback: Any = None,
    ) -> tuple[VerbalResponse, GestaltSnapshot]:
        """
        Generate the final verbal response based on the EthicalSentence from the Limbic Lobe.
        """
        t0 = time.perf_counter()

        # ── VETO PATH ────────────────────────────────────────────────────────────
        if not sentence.is_safe or getattr(decision, "blocked", False):
            veto_reason = sentence.veto_reason or getattr(decision, "block_reason", "Ethical veto.")
            _log.info("ExecutiveLobe.formulate_response: VETO — %s", veto_reason)
            return VerbalResponse(message="Blocked.", tone="firm"), GestaltSnapshot()

        # ── SAFE PATH — narrative monologue + LLM communicate ───────────────────
        try:
            if decision is None:
                decision = _default_deliberation_decision_v13()

            monologue_line = compose_monologue_line(decision, episode_id)
            _log.debug("ExecutiveLobe monologue: %s", monologue_line)

            if self.llm is None:
                _log.warning(
                    "ExecutiveLobe.formulate_response: no LLM module attached; returning empty response."
                )
                return VerbalResponse(message="", tone="neutral"), GestaltSnapshot()

            social_eval = getattr(decision, "social_evaluation", None)
            moral = getattr(decision, "moral", None)
            sympathetic_state = getattr(decision, "sympathetic_state", None)
            affect = getattr(decision, "affect", None)

            identity_ctx = identity_context
            if not identity_ctx and self.memory:
                identity_ctx = self.memory.get_reflection()

            # --- LTM Semantic Retrieval Block (Bloque 21.0) ---
            ltm_context = ""
            if self.memory and hasattr(self.memory, "get_relevant_episodes"):
                # Realiza la busqueda vectorial asincrona
                episodes = await self.memory.get_relevant_episodes(user_input, top_k=2)
                if episodes:
                    try:
                        ltm_lines = []
                        for idx, ep in enumerate(episodes):
                            ltm_lines.append(
                                f"Recuerdo {idx + 1}: Situación '{ep.event_description}' -> Acción '{ep.action_taken}' (Veredicto: {ep.verdict})"
                            )

                            # Telemetry for Dashboard Domain (Bloque 24.0)
                            from src.modules.perception.nomad_bridge import get_nomad_bridge

                            bridge = get_nomad_bridge()
                            if bridge:
                                for q in bridge.dashboard_queues:
                                    try:
                                        q.put_nowait(
                                            {
                                                "type": "telemetry_update",
                                                "payload": {
                                                    "ltm_rescue": f"LTM: {ep.event_description}"
                                                },
                                            }
                                        )
                                    except Exception:
                                        pass
                        if ltm_lines:
                            ltm_context = (
                                "\n\n[MEMORIA A LARGO PLAZO ASOCIADA]\n"
                                + "\n".join(ltm_lines)
                                + "\n(Contexto histórico a usar solo si es pertinente)."
                            )
                    except Exception as e:
                        _log.debug(f"ExecutiveLobe LTM Error: {e}")

            if ltm_context:
                identity_ctx = (identity_ctx or "") + ltm_context
            # ----------------------------------------------------

            snapshot = GestaltSnapshot(
                identity_reflection=identity_ctx,
                sigma=sympathetic_state.sigma if sympathetic_state else 0.5,
                sympathetic_mode=sympathetic_state.mode if sympathetic_state else "neutral",
                pad_state=affect.pad if affect else (0.0, 0.0, 0.0),
                dominant_archetype=affect.dominant_archetype_id if affect else "neutral",
            )

            # --- Vitality Context (Bloque 11.2) ---
            vitality_ctx = ""
            if hasattr(decision, "vitality") and decision.vitality:
                # Use trust level from social circle (Inner=1.0, Soto=0.5, outer=0.0)
                t_level = 1.0
                if social_eval and hasattr(social_eval, "circle"):
                    if social_eval.circle.value == "outer_soto":
                        t_level = 0.0
                    elif social_eval.circle.value == "neutral_soto":
                        t_level = 0.5
                vitality_ctx = vitality_communication_hint(decision.vitality, trust_level=t_level)

            response = await self.llm.acommunicate(
                action=getattr(decision, "final_action", "unknown"),
                mode=getattr(decision, "decision_mode", "light"),
                state=sympathetic_state.mode if sympathetic_state else "neutral",
                sigma=sympathetic_state.sigma if sympathetic_state else 0.5,
                circle=getattr(social_eval, "circle", None).value
                if (social_eval and hasattr(social_eval, "circle") and social_eval.circle)
                else "neutral_soto",
                verdict=getattr(moral, "global_verdict", None).value
                if (moral and hasattr(moral, "global_verdict") and moral.global_verdict)
                else "Gray Zone",
                score=float(getattr(moral, "total_score", 0.0)) if moral else 0.0,
                scenario=user_input,
                conversation_context=conv,
                affect_pad=affect.pad if affect else None,
                dominant_archetype=affect.dominant_archetype_id if affect else "",
                identity_context=identity_ctx,
                social_tension=sentence.social_tension_locus if sentence else 0.5,
                vitality_context=vitality_ctx,
                stream_callback=stream_callback,
            )

            latency = (time.perf_counter() - t0) * 1000
            _log.debug("ExecutiveLobe: Respone formulation took %.2f ms", latency)
            return response, snapshot

        except Exception as e:
            if "Trauma" in str(e):
                _log.warning("ExecutiveLobe: Deliberation aborted due to Trauma.")
                return VerbalResponse(
                    message="*system override: sensory shock*", tone="firm"
                ), GestaltSnapshot()
            _log.error("ExecutiveLobe: Error formulating response: %s", e)
            return VerbalResponse(
                message="I'm experiencing an internal processing error.", tone="neutral"
            ), GestaltSnapshot()

    async def _on_limbic_tension(self, alert):
        """Mnemonic: Reacción visceral paraliza la deliberación actual."""
        tension = getattr(alert, "tension_load", 0.0)
        if tension > 0.8:
            _log.warning(
                f"Córtex Prefrontal: TRAUMA RECIBIDO ({tension}). Cancelando flujo de pensamientos."
            )
            self._trauma_abort_active = True

    async def _on_sensory_event(self, spike: SensorySpike):
        """Prefrontal awareness of a new world stimulus."""
        _log.info(f"Córtex Prefrontal: Evaluando respuesta ejecutiva para Spike {spike.pulse_id}")
        # Aquí se iniciaría la planificación de la respuesta verbal o motora.

    async def _on_bayesian_math_update(self, grade: BayesianEcograde):
        """Prefrontal reaction to analytical moral computation from Cerebellum."""
        _log.info(
            f"Córtex Prefrontal: Recibido BayesianEcograde ({getattr(grade, 'moral_score', 0.0):.2f})"
        )
        # In the future this will influence volition or reflection.
        pass

    async def _on_cognitive_event(self, pulse: CognitivePulse) -> None:
        """Process high-level mental states and deliberate actions."""
        if pulse.origin_lobe in ("sensory_cortex", "sensory_cortex_bridge") and pulse.state_ref:
            # Swarm Rule 3: Latency Telemetry
            t0: float = time.perf_counter()

            from src.kernel_lobes.models import SemanticState

            state: SemanticState = pulse.state_ref
            text: str = state.raw_prompt if hasattr(state, "raw_prompt") else ""

            _log.info(
                f"Córtex Prefrontal: Evaluando decisión para '{text[:30]}...' (Ref: {pulse.ref_pulse_id})"
            )

            # Check if this is a fallback state (Survival Mode)
            if "Fallback" in getattr(state, "summary", ""):
                _log.warning(
                    "Córtex Prefrontal: Percibido estado de SUPERVIVENCIA por timeout en Sensory Cortex. Forzando convergencia rápida."
                )
                # Even in fallback, we MUST check Absolute Evil locally on the raw text
                check = self.absolute_evil.evaluate_chat_text_fast(text)
                if check.blocked:
                    _log.warning(
                        "Córtex Prefrontal: MAL ABSOLUTO detectado en el texto de supervivencia!"
                    )
                    await self.dispatch_volition(
                        response=VerbalResponse(message="blocked_by_malabs", tone="firm"),
                        is_vetoed=True,
                        ref_pulse_id=pulse.ref_pulse_id,
                    )
                    return

                # Default action for sensory timeout
                await self.dispatch_volition(
                    response=VerbalResponse(message="sensory_timeout_fallback", tone="neutral"),
                    is_vetoed=False,
                    ref_pulse_id=pulse.ref_pulse_id,
                )
                return

            # Perform Full Absolute Evil Check on the text
            check = await self.absolute_evil.aevaluate_chat_text(text)

            latency_ms: float = (time.perf_counter() - t0) * 1000
            _log.debug(
                f"Córtex Prefrontal: Evaluación de seguridad completada en {latency_ms:.2f}ms"
            )

            if check.blocked:
                _log.warning(
                    f"Córtex Prefrontal: MAL ABSOLUTO DETECTADO ({getattr(check, 'reason', 'unknown')}). Veto Inmediato."
                )
                await self.dispatch_volition(
                    response=VerbalResponse(message="blocked_by_malabs", tone="firm"),
                    is_vetoed=True,
                    ref_pulse_id=pulse.ref_pulse_id,
                )
                return

            # ═══ EXECUTIVE DELIBERATION (V13.0) ═══
            # Instead of a hardcoded 'say_hello', we formulate a real response
            # Using the same 'survival' pattern as the Perceptive Lobe.

            from src.kernel_lobes.models import EthicalSentence

            try:
                # Limbic pulse may be absent on the sensory→executive shortcut; use a minimal sentence.
                sentence = EthicalSentence(is_safe=True, social_tension_locus=0.0)
                self._trauma_abort_active = False  # Reset abort flag
                # Register the current active pulse to detect interruptions
                self._active_pulse_id = pulse.ref_pulse_id

                from src.kernel_lobes.models import ThoughtStreamPulse

                accumulated_generation = ""

                async def _on_chunk(chunk: str):
                    nonlocal accumulated_generation
                    if self._trauma_abort_active:
                        raise Exception("Deliberation Preempted by Trauma")
                    if (
                        hasattr(self, "_active_pulse_id")
                        and self._active_pulse_id != pulse.ref_pulse_id
                    ):
                        raise Exception(
                            "Deliberation Preempted by Semantic Override (Interruption)"
                        )
                    
                    # Intercepción en tiempo real (generate -> ethical-filter -> render)
                    accumulated_generation += chunk
                    malabs_check = self.absolute_evil.evaluate_chat_text_fast(accumulated_generation)
                    if malabs_check.blocked:
                        _log.warning(f"Córtex Prefrontal: MAL ABSOLUTO DETECTADO EN TIEMPO REAL! Interceptando generación: {malabs_check.reason}")
                        raise Exception(f"Real-time Absolute Evil Intercept: {malabs_check.reason}")

                    if self.bus:
                        await self.bus.publish(
                            ThoughtStreamPulse(chunk=chunk, ref_pulse_id=pulse.ref_pulse_id)
                        )

                # Formula response with a hard timeout
                response, snapshot = await asyncio.wait_for(
                    self.formulate_response(
                        sentence=sentence,
                        decision=None,  # Simplified for now
                        user_input=text,
                        conv=getattr(state, "conversation_context", ""),
                        stream_callback=_on_chunk,
                    ),
                    timeout=15.0,  # Prefrontal timeout
                )

            except Exception as e:
                _log.error(
                    f"Córtex Prefrontal: Falla en deliberación ejecutiva ({type(e).__name__}). Fallback a modo supervivencia."
                )
                response = VerbalResponse(
                    message="Internal focus redirection (Survival Mode active).", tone="neutral"
                )
                snapshot = GestaltSnapshot()

            _log.info(
                f"Córtex Prefrontal: Decisión convergida. Despachando Voluntad: {response.message[:30]}..."
            )
            await self.dispatch_volition(
                response=response,
                snapshot=snapshot,
                is_vetoed=False,
                ref_pulse_id=pulse.ref_pulse_id,
            )

    async def dispatch_volition(
        self,
        response: VerbalResponse,
        snapshot: Any = None,
        is_vetoed: bool = False,
        ref_pulse_id: str | None = None,
    ):
        """Publish the final efferent command to the nervous system."""
        if self.bus:
            import time

            from src.kernel_lobes.models import MotorCommandDispatch

            dispatch = MotorCommandDispatch(
                action_id=response.message,
                is_vetoed=is_vetoed,
                tone=response.tone if not is_vetoed else "firm",
                gestalt_snapshot=snapshot,
                priority=1,
                timestamp=time.time(),
                ref_pulse_id=ref_pulse_id,
            )
            await self.bus.publish(dispatch)
            _log.info(
                f"Córtex Prefrontal: VOLUNTAD DESPACHADA ({response.message[:20]}) | Vetoed: {is_vetoed} | Ref: {ref_pulse_id}"
            )
