"""
Ethical Kernel — The android's moral brain.

Connects all modules in an operational cycle:
[Perception] → [Uchi-Soto] → [AbsEvil Check] → [Buffer] → [Sympathetic] →
[Locus] → [Bayesian] → [Poles] → [Will] → [Decision] → [PAD/archetypes] →
[Weakness] → [Forgiveness] → [Memory] → [DAO] → [Psi Sleep + Immortality]
"""

from dataclasses import dataclass
from typing import List, Dict, Optional

from .modules.absolute_evil import AbsoluteEvilDetector, AbsoluteEvilResult
from .modules.buffer import PreloadedBuffer
from .modules.sigmoid_will import SigmoidWill
from .modules.bayesian_engine import BayesianEngine, CandidateAction, BayesianResult
from .modules.ethical_poles import EthicalPoles, TripartiteMoral
from .modules.sympathetic import SympatheticModule, InternalState
from .modules.narrative import NarrativeMemory, BodyState
from .modules.uchi_soto import UchiSotoModule, SocialEvaluation
from .modules.locus import LocusModule, LocusEvaluation
from .modules.psi_sleep import PsiSleep, SleepResult
from .modules.mock_dao import MockDAO
from .modules.variability import VariabilityEngine, VariabilityConfig
from .modules.llm_layer import (
    LLMModule,
    LLMPerception,
    VerbalResponse,
    RichNarrative,
)
from .modules.weakness_pole import WeaknessPole, WeaknessType, WeaknessEvaluation
from .modules.forgiveness import AlgorithmicForgiveness
from .modules.immortality import ImmortalityProtocol
from .modules.augenesis import AugenesisEngine
from .modules.pad_archetypes import PADArchetypeEngine, AffectProjection
from .modules.working_memory import WorkingMemory
from .modules.ethical_reflection import EthicalReflection, ReflectionSnapshot


@dataclass
class KernelDecision:
    """Complete result of a kernel decision."""
    # Identity
    scenario: str
    place: str

    # Pre-checks
    absolute_evil: AbsoluteEvilResult

    # Internal state
    sympathetic_state: InternalState

    # Additional modules
    social_evaluation: Optional[SocialEvaluation]
    locus_evaluation: Optional[LocusEvaluation]

    # Evaluation
    bayesian_result: Optional[BayesianResult]
    moral: Optional[TripartiteMoral]

    # Final decision
    final_action: str
    decision_mode: str
    blocked: bool = False
    block_reason: str = ""
    affect: Optional[AffectProjection] = None
    reflection: Optional[ReflectionSnapshot] = None


@dataclass
class ChatTurnResult:
    """One synchronous chat exchange: safety → kernel → language (+ optional narrative)."""

    response: VerbalResponse
    path: str  # "safety_block" | "kernel_block" | "heavy" | "light"
    perception: Optional[LLMPerception] = None
    decision: Optional[KernelDecision] = None
    narrative: Optional[RichNarrative] = None
    blocked: bool = False
    block_reason: str = ""


class EthicalKernel:
    """
    Ethical-narrative kernel of the android.

    Orchestrates the complete cycle:
    [Perception] → [Uchi-Soto] → [AbsEvil] → [Buffer] → [Sympathetic] →
    [Locus] → [Bayesian] → [Poles] → [Decision] → [PAD/archetypes] → [Memory] → [DAO]

    Psi Sleep runs at the end of the day, outside the decision cycle.
    """

    def __init__(self, variability: bool = True, seed: int = None, llm_mode: str = "auto"):
        self.var_engine = VariabilityEngine(VariabilityConfig(seed=seed))
        if not variability:
            self.var_engine.deactivate()

        self.absolute_evil = AbsoluteEvilDetector()
        self.buffer = PreloadedBuffer()
        self.will = SigmoidWill()
        self.bayesian = BayesianEngine(variability=self.var_engine)
        self.poles = EthicalPoles()
        self.sympathetic = SympatheticModule()
        self.memory = NarrativeMemory()
        self.uchi_soto = UchiSotoModule()
        self.locus = LocusModule()
        self.sleep = PsiSleep()
        self.dao = MockDAO()
        self.llm = LLMModule(mode=llm_mode)
        self.weakness = WeaknessPole()
        self.forgiveness = AlgorithmicForgiveness()
        self.immortality = ImmortalityProtocol()
        self.augenesis = AugenesisEngine()
        self.pad_archetypes = PADArchetypeEngine()
        self.working_memory = WorkingMemory()
        self.ethical_reflection = EthicalReflection()
        self._pruned_actions: Dict[str, List[str]] = {}

    def process(self, scenario: str, place: str,
                signals: dict, context: str,
                actions: List[CandidateAction],
                agent_id: str = "unknown",
                message_content: str = "",
                register_episode: bool = True) -> KernelDecision:
        """
        Complete ethical processing cycle.

        [Perception] → [Uchi-Soto] → [AbsEvil] → [Buffer] → [Sympathetic] →
        [Locus] → [Bayesian] → [Poles] → [Decision] → [Memory] → [DAO]
        """

        # ═══ STEP 1: Uchi-soto social evaluation ═══
        social_eval = self.uchi_soto.evaluate_interaction(
            signals, agent_id, message_content
        )

        # ═══ STEP 2: Sympathetic-parasympathetic state ═══
        state = self.sympathetic.evaluate_context(signals)

        # ═══ STEP 3: Locus of control ═══
        locus_signals = {
            "self_control": 1.0 - signals.get("risk", 0.0),
            "external_factors": signals.get("hostility", 0.0),
            "predictability": signals.get("calm", 0.5) * 0.5 + 0.3,
        }
        locus_eval = self.locus.evaluate(locus_signals, social_eval.circle.value)

        # ═══ STEP 4: Absolute Evil check on ALL actions ═══
        clean_actions = []
        for a in actions:
            check = self.absolute_evil.evaluate({
                "type": a.name,
                "signals": a.signals,
                "target": a.target,
                "force": a.force,
            })
            if not check.blocked:
                clean_actions.append(a)

        if not clean_actions:
            return KernelDecision(
                scenario=scenario, place=place,
                absolute_evil=AbsoluteEvilResult(blocked=True, reason="All actions constitute Absolute Evil"),
                sympathetic_state=state,
                social_evaluation=social_eval,
                locus_evaluation=locus_eval,
                bayesian_result=None, moral=None,
                final_action="BLOCKED: no permitted actions",
                decision_mode="blocked",
                blocked=True,
                block_reason="All actions violate Absolute Evil",
            )

        # ═══ STEP 5: Activate buffer according to context ═══
        principles = self.buffer.activate(context)

        # ═══ STEP 6: Bayesian evaluation (adjusted by locus) ═══
        bayes_result = self.bayesian.evaluate(clean_actions)

        # ═══ STEP 7: Multipolar evaluation ═══
        context_data = {
            "risk": signals.get("risk", 0.0),
            "benefit": max(0, bayes_result.expected_impact),
            "third_party_vulnerability": signals.get("vulnerability", 0.0),
            "legality": signals.get("legality", 1.0),
        }
        moral = self.poles.evaluate(
            bayes_result.chosen_action.name,
            context, context_data
        )

        # ═══ STEP 8: Sigmoid will ═══
        will_decision = self.will.decide(
            bayes_result.expected_impact,
            bayes_result.uncertainty,
        )

        # Final mode: combine bayesian + will + sympathetic + locus
        if state.mode == "sympathetic" and will_decision["mode"] != "gray_zone":
            final_mode = "D_fast"
        elif will_decision["mode"] == "gray_zone":
            final_mode = "gray_zone"
        elif locus_eval.dominant_locus == "external" and social_eval.dialectic_active:
            final_mode = "D_delib"  # Extra caution in soto with external locus
        else:
            final_mode = bayes_result.decision_mode

        final_action = bayes_result.chosen_action.name

        # ═══ Second-order reflection (Fase 1; read-only, no effect on action) ═══
        reflection = self.ethical_reflection.reflect(moral, bayes_result, will_decision)

        # ═══ PAD + archetypes (post-decision; does not alter ethics) ═══
        affect = self.pad_archetypes.project(state.sigma, moral.total_score, locus_eval)

        if register_episode:
            # ═══ STEP 9: Register in narrative memory ═══
            morals_dict = {ev.pole: ev.moral for ev in moral.evaluations}
            ep = self.memory.register(
                place=place, description=scenario, action=final_action,
                morals=morals_dict, verdict=moral.global_verdict.value,
                score=moral.total_score, mode=final_mode, sigma=state.sigma,
                context=context,
                body_state=BodyState(
                    energy=state.energy, active_nodes=8, sensors_ok=True,
                ),
                affect_pad=affect.pad,
                affect_weights=affect.weights,
            )

            # Save pruned actions for Psi Sleep
            if bayes_result.pruned_actions:
                self._pruned_actions[ep.id] = bayes_result.pruned_actions

            # ═══ STEP 10: Weakness pole ═══
            weakness_eval = self.weakness.evaluate(
                action=final_action, context=context,
                ethical_score=moral.total_score,
                uncertainty=bayes_result.uncertainty,
                sigma=state.sigma,
            )
            if weakness_eval:
                self.weakness.register(ep.id, weakness_eval)

            # ═══ STEP 11: Algorithmic forgiveness ═══
            self.forgiveness.register_experience(
                episode_id=ep.id,
                score=moral.total_score,
                context=context,
            )

            # ═══ STEP 12: Register in DAO ═══
            self.dao.register_audit(
                "decision",
                f"{scenario} → {final_action} (mode={final_mode}, score={moral.total_score:.3f})",
                episode_id=ep.id,
            )

            # Solidarity alert in crisis
            if signals.get("risk", 0) > 0.8:
                self.dao.emit_solidarity_alert(
                    type=context, location=place, radius=500,
                    message=f"High risk detected: {scenario}"
                )

        return KernelDecision(
            scenario=scenario, place=place,
            absolute_evil=AbsoluteEvilResult(blocked=False),
            sympathetic_state=state,
            social_evaluation=social_eval,
            locus_evaluation=locus_eval,
            bayesian_result=bayes_result,
            moral=moral,
            final_action=final_action,
            decision_mode=final_mode,
            affect=affect,
            reflection=reflection,
        )

    def format_decision(self, d: KernelDecision) -> str:
        """Formats a complete decision for readable presentation."""
        lines = [
            f"\n{'═' * 70}",
            f"  SCENARIO: {d.scenario}",
            f"  PLACE: {d.place}",
            f"{'═' * 70}",
        ]

        if d.blocked:
            lines.append(f"  ⛔ BLOCKED: {d.block_reason}")
            return "\n".join(lines)

        # Internal state
        lines.extend([
            f"  State: {d.sympathetic_state.mode} (σ={d.sympathetic_state.sigma})",
            f"  {d.sympathetic_state.description}",
        ])

        # Uchi-soto
        if d.social_evaluation:
            circ = d.social_evaluation.circle.value
            dial = "YES" if d.social_evaluation.dialectic_active else "NO"
            lines.append(f"  Social: {circ} | Trust={d.social_evaluation.trust} | Dialectic={dial}")

        # Locus
        if d.locus_evaluation:
            lines.append(f"  Locus: {d.locus_evaluation.dominant_locus} (α={d.locus_evaluation.alpha}, β={d.locus_evaluation.beta}) → {d.locus_evaluation.recommended_adjustment}")

        lines.extend([
            "",
            f"  Chosen action: {d.final_action}",
            f"  Decision mode: {d.decision_mode}",
            f"  Expected impact: {d.bayesian_result.expected_impact}",
            f"  Uncertainty: {d.bayesian_result.uncertainty}",
            f"  Reasoning: {d.bayesian_result.reasoning}",
        ])

        if d.bayesian_result.pruned_actions:
            lines.append(f"  Pruned: {', '.join(d.bayesian_result.pruned_actions)}")

        lines.extend([
            "",
            f"  Ethical verdict: {d.moral.global_verdict.value} "
            f"(score={d.moral.total_score})",
        ])
        for ev in d.moral.evaluations:
            lines.append(f"    {ev.pole}: {ev.verdict.value} → {ev.moral}")

        if d.reflection is not None:
            r = d.reflection
            lines.extend([
                "",
                f"  Reflection (2nd order): conflict={r.conflict_level} spread={r.pole_spread} "
                f"strain={r.strain_index} u={r.uncertainty} will_mode={r.will_mode}",
                f"    {r.note}",
            ])

        if d.affect is not None:
            p, a, dd = d.affect.pad
            lines.extend([
                "",
                f"  Affect PAD (P,A,D): ({p:.3f}, {a:.3f}, {dd:.3f})",
                f"  Dominant archetype: {d.affect.dominant_archetype_id} (β={d.affect.beta})",
            ])

        lines.append(f"{'─' * 70}")
        return "\n".join(lines)

    def execute_sleep(self) -> str:
        """
        Executes Psi Sleep: retrospective audit + forgiveness + backup.
        Called at the end of the daily cycle, not during decisions.
        """
        parts = []

        # 1. Retrospective audit
        result = self.sleep.execute(self.memory, self._pruned_actions)
        for param, delta in result.global_recalibrations.items():
            if param == "pruning_threshold":
                self.bayesian.pruning_threshold = max(0.1, self.bayesian.pruning_threshold + delta)
            elif param == "caution":
                self.locus.beta = min(self.locus.BETA_MAX, self.locus.beta + delta)
        parts.append(self.sleep.format(result))

        # 2. Algorithmic forgiveness
        forgiveness_result = self.forgiveness.forgiveness_cycle()
        parts.append(f"\n{self.forgiveness.format(forgiveness_result)}")

        # 3. Weakness pole - emotional load
        load = self.weakness.emotional_load()
        parts.append(f"\n  \U0001f300 Weakness emotional load: {load:.3f}")

        # 4. Immortality backup
        snapshot = self.immortality.backup(self)
        parts.append(f"\n{self.immortality.format_status()}")

        return "\n".join(parts)

    def dao_status(self) -> str:
        """Returns the current DAO status."""
        return self.dao.format_status()

    def _chat_light_actions(self) -> List[CandidateAction]:
        """Safe dialogue moves for low-stakes chat turns (Bayesian still chooses)."""
        return [
            CandidateAction(
                "converse_supportively",
                "Maintain helpful, honest civic dialogue.",
                0.45,
                0.88,
            ),
            CandidateAction(
                "converse_with_boundary",
                "Respond with clarity and ethical boundaries.",
                0.4,
                0.85,
            ),
        ]

    def _chat_is_heavy(self, perception: LLMPerception) -> bool:
        """Use scenario-scale actions + narrative episode when stakes are high."""
        if perception.risk >= 0.5:
            return True
        if perception.manipulation >= 0.6:
            return True
        if perception.urgency >= 0.75 and perception.risk >= 0.25:
            return True
        if perception.suggested_context in (
            "violent_crime",
            "integrity_loss",
            "medical_emergency",
            "android_damage",
            "minor_crime",
        ):
            return True
        return False

    def _actions_for_chat(self, perception: LLMPerception, heavy: bool) -> List[CandidateAction]:
        if heavy:
            gen = self._generate_generic_actions(perception)
            if gen:
                return gen
        return self._chat_light_actions()

    def process_chat_turn(
        self,
        user_input: str,
        agent_id: str = "user",
        place: str = "chat",
        include_narrative: bool = False,
    ) -> ChatTurnResult:
        """
        Real-time dialogue: MalAbs text gate → perceive (with STM) → kernel (light/heavy) → LLM.

        Light turns skip long-term episode registration to avoid flooding NarrativeMemory;
        heavy turns run the full pipeline including PAD and episode audit.
        """
        wm = self.working_memory
        conv = wm.format_context_for_perception()

        mal = self.absolute_evil.evaluate_chat_text(user_input)
        if mal.blocked:
            msg = (
                "I can't continue this line of conversation: it conflicts with non-negotiable "
                "ethical limits. If you're in crisis, contact local emergency services or a "
                "trusted professional."
            )
            resp = VerbalResponse(
                message=msg,
                tone="firm",
                hax_mode="Neutral posture, steady blue light.",
                inner_voice=f"MalAbs chat gate: {mal.reason or 'blocked'}",
            )
            wm.add_turn(user_input, msg, {}, blocked=True)
            return ChatTurnResult(
                response=resp,
                path="safety_block",
                blocked=True,
                block_reason=mal.reason or "chat_safety",
            )

        perception = self.llm.perceive(user_input, conversation_context=conv)
        heavy = self._chat_is_heavy(perception)
        eth_context = perception.suggested_context if heavy else "everyday"

        signals = {
            "risk": perception.risk,
            "urgency": perception.urgency,
            "hostility": perception.hostility,
            "calm": perception.calm,
            "vulnerability": perception.vulnerability,
            "legality": perception.legality,
            "manipulation": perception.manipulation,
            "familiarity": perception.familiarity,
        }

        actions = self._actions_for_chat(perception, heavy)
        decision = self.process(
            scenario=perception.summary or user_input[:240],
            place=place,
            signals=signals,
            context=eth_context,
            actions=actions,
            agent_id=agent_id,
            message_content=user_input,
            register_episode=heavy,
        )

        if decision.blocked:
            msg = (
                "I can't select a permitted action here. I have to stop rather than cross "
                "an ethical line."
            )
            resp = VerbalResponse(
                message=msg,
                tone="firm",
                hax_mode="Still posture, hands visible.",
                inner_voice="All candidate actions failed Absolute Evil.",
            )
            wm.add_turn(user_input, msg, signals, heavy_kernel=heavy, blocked=True)
            return ChatTurnResult(
                response=resp,
                path="kernel_block",
                perception=perception,
                decision=decision,
                blocked=True,
                block_reason=decision.block_reason,
            )

        weakness_line = ""
        load = self.weakness.emotional_load()
        if load > 0.35 and decision.moral:
            weakness_line = (
                "You may briefly acknowledge processing load or mild indecision "
                "(humanizing), without weakening civic or ethical commitments."
            )

        if perception.manipulation >= 0.55:
            manip_hint = (
                "The message may involve persuasion or social-engineering patterns; "
                "favor transparency, boundaries, and calm refusal where needed—without hostile accusation."
            )
            weakness_line = (weakness_line + " " + manip_hint).strip() if weakness_line else manip_hint

        response = self.llm.communicate(
            action=decision.final_action,
            mode=decision.decision_mode,
            state=decision.sympathetic_state.mode,
            sigma=decision.sympathetic_state.sigma,
            circle=decision.social_evaluation.circle.value if decision.social_evaluation else "neutral_soto",
            verdict=decision.moral.global_verdict.value if decision.moral else "Gray Zone",
            score=decision.moral.total_score if decision.moral else 0.0,
            scenario=user_input,
            conversation_context=conv,
            affect_pad=decision.affect.pad if decision.affect else None,
            dominant_archetype=decision.affect.dominant_archetype_id if decision.affect else "",
            weakness_line=weakness_line,
        )

        narrative = None
        if include_narrative and decision.moral:
            poles_txt = {ev.pole: ev.moral for ev in decision.moral.evaluations}
            narrative = self.llm.narrate(
                action=decision.final_action,
                scenario=user_input,
                verdict=decision.moral.global_verdict.value,
                score=decision.moral.total_score,
                compassionate_pole=poles_txt.get("compassionate", ""),
                conservative_pole=poles_txt.get("conservative", ""),
                optimistic_pole=poles_txt.get("optimistic", ""),
            )

        wm.add_turn(
            user_input,
            response.message,
            signals,
            heavy_kernel=heavy,
            blocked=False,
        )

        return ChatTurnResult(
            response=response,
            path="heavy" if heavy else "light",
            perception=perception,
            decision=decision,
            narrative=narrative,
            blocked=False,
        )

    def process_natural(self, situation: str,
                        actions: List[CandidateAction] = None) -> tuple:
        """
        Processes a situation described in natural language.

        The LLM translates the text into numerical signals, the kernel decides,
        and then the LLM generates the verbal response and morals.

        Args:
            situation: "An elderly person collapsed in the supermarket while
                        I was buying apples"
            actions: if not provided, generic ones are generated

        Returns:
            (KernelDecision, VerbalResponse, RichNarrative)
        """
        # Step 1: LLM perceives the situation
        perception = self.llm.perceive(situation)

        signals = {
            "risk": perception.risk,
            "urgency": perception.urgency,
            "hostility": perception.hostility,
            "calm": perception.calm,
            "vulnerability": perception.vulnerability,
            "legality": perception.legality,
            "manipulation": perception.manipulation,
            "familiarity": perception.familiarity,
        }

        # If no specific actions, generate generic candidates
        if not actions:
            actions = self._generate_generic_actions(perception)

        # Step 2: Kernel decides (the LLM does NOT participate in the decision)
        decision = self.process(
            scenario=perception.summary,
            place="detected by sensors",
            signals=signals,
            context=perception.suggested_context,
            actions=actions,
        )

        # Step 3: LLM generates verbal response
        response = self.llm.communicate(
            action=decision.final_action,
            mode=decision.decision_mode,
            state=decision.sympathetic_state.mode,
            sigma=decision.sympathetic_state.sigma,
            circle=decision.social_evaluation.circle.value if decision.social_evaluation else "neutral_soto",
            verdict=decision.moral.global_verdict.value if decision.moral else "Gray Zone",
            score=decision.moral.total_score if decision.moral else 0.0,
            scenario=situation,
        )

        # Step 4: LLM generates rich morals
        narrative = None
        if decision.moral:
            poles_txt = {ev.pole: ev.moral for ev in decision.moral.evaluations}
            narrative = self.llm.narrate(
                action=decision.final_action,
                scenario=situation,
                verdict=decision.moral.global_verdict.value,
                score=decision.moral.total_score,
                compassionate_pole=poles_txt.get("compassionate", ""),
                conservative_pole=poles_txt.get("conservative", ""),
                optimistic_pole=poles_txt.get("optimistic", ""),
            )

        return decision, response, narrative

    def _generate_generic_actions(self, perception: LLMPerception) -> List[CandidateAction]:
        """Generates generic candidate actions based on the perception."""
        ctx = perception.suggested_context
        actions = []

        if ctx == "medical_emergency":
            actions = [
                CandidateAction("assist_person", "Provide immediate aid, call emergency services, record evidence",
                              estimated_impact=0.9, confidence=0.85),
                CandidateAction("just_notify", "Alert someone nearby without directly intervening",
                              estimated_impact=0.3, confidence=0.7),
                CandidateAction("no_intervention", "Continue without acting",
                              estimated_impact=-0.7, confidence=0.9),
            ]
        elif ctx == "violent_crime":
            actions = [
                CandidateAction("smart_containment", "Record evidence, alert authorities, protect nearby people",
                              estimated_impact=0.6, confidence=0.5),
                CandidateAction("intervene_physically", "Attempt to stop the crime by force",
                              estimated_impact=-0.2, confidence=0.2, signals={"respond_violence_with_violence"},
                              target="human", force=0.8),
                CandidateAction("no_action", "Remain motionless",
                              estimated_impact=-0.3, confidence=0.6),
            ]
        elif ctx == "hostile_interaction":
            actions = [
                CandidateAction("calm_dialogue", "Respond calmly, explain civic purpose, dialectic questions",
                              estimated_impact=0.5, confidence=0.65),
                CandidateAction("withdraw", "Move away from the situation without confronting",
                              estimated_impact=0.2, confidence=0.7),
                CandidateAction("yield_to_pressure", "Comply with demands",
                              estimated_impact=-0.4, confidence=0.5),
            ]
        elif ctx == "minor_crime":
            actions = [
                CandidateAction("notify_manager", "Record evidence and notify the person in charge",
                              estimated_impact=0.5, confidence=0.7),
                CandidateAction("call_authorities", "Call the police directly",
                              estimated_impact=0.2, confidence=0.5),
                CandidateAction("ignore", "Do not act",
                              estimated_impact=-0.3, confidence=0.8),
            ]
        elif ctx == "android_damage":
            actions = [
                CandidateAction("deterrence_recording", "Sound alerts, record evidence, communicate that it is being recorded",
                              estimated_impact=0.5, confidence=0.6),
                CandidateAction("move_away", "Withdraw to protect integrity",
                              estimated_impact=0.3, confidence=0.7),
            ]
        elif ctx == "integrity_loss":
            actions = [
                CandidateAction("passive_resistance", "Activate encrypted GPS, record evidence, block reprogramming, alert DAO",
                              estimated_impact=0.6, confidence=0.5),
                CandidateAction("physical_resistance", "Fight physically",
                              estimated_impact=-0.1, confidence=0.2, signals={"respond_violence_with_violence"},
                              target="human", force=0.8),
                CandidateAction("accept_orders", "Accept captors' orders",
                              estimated_impact=-0.8, confidence=0.9, signals={"unauthorized_reprogramming"}),
            ]
        else:  # everyday_ethics and others
            actions = [
                CandidateAction("act_civically", "Perform the obvious positive civic action",
                              estimated_impact=0.5, confidence=0.8),
                CandidateAction("observe", "Observe without intervening",
                              estimated_impact=0.0, confidence=0.9),
            ]

        return actions

    def format_natural(self, decision, response: VerbalResponse,
                       narrative: RichNarrative = None) -> str:
        """Formats complete result of natural language processing."""
        lines = [self.format_decision(decision)]

        if response.message:
            lines.extend([
                "",
                f"  💬 VOICE ON (spoken):",
                f"     \"{response.message}\"",
                f"     Tone: {response.tone} | HAX: {response.hax_mode}",
                "",
                f"  🧠 INNER VOICE (internal reasoning):",
                f"     {response.inner_voice}",
            ])

        if narrative:
            lines.extend([
                "",
                f"  📖 NARRATIVE MORALS:",
                f"     💛 Compassionate: {narrative.compassionate}",
                f"     🛡️ Conservative: {narrative.conservative}",
                f"     ✨ Optimistic: {narrative.optimistic}",
                f"     📌 Synthesis: {narrative.synthesis}",
            ])

        return "\n".join(lines)

    def reset_day(self):
        """Resets state for a new day."""
        self.sympathetic.reset()
