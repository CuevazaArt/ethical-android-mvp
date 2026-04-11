"""
Ethical Kernel — The android's moral brain.

Connects all modules in an operational cycle (see `EthicalKernel.process`):
[Uchi-Soto] → [Sympathetic] → [Locus] → [AbsEvil] → [Buffer] → [Bayesian] →
[Poles] → [Will] → [EthicalReflection] → [Salience] → [PAD/archetypes] →
[Memory episode] → [Weakness] → [Forgiveness] → [DAO]. Perception/LLM wraps
this via `process_natural` / `process_chat_turn`; `execute_sleep` runs Psi Sleep,
forgiveness cycle, weakness load, immortality backup, drive intents.
"""

import os
from dataclasses import dataclass
from typing import Any, List, Dict, Optional, Tuple

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
    resolve_llm_mode,
)
from .modules.weakness_pole import WeaknessPole, WeaknessType, WeaknessEvaluation
from .modules.forgiveness import AlgorithmicForgiveness
from .modules.immortality import ImmortalityProtocol
from .modules.augenesis import AugenesisEngine
from .modules.pad_archetypes import PADArchetypeEngine, AffectProjection
from .modules.working_memory import WorkingMemory
from .modules.ethical_reflection import (
    EthicalReflection,
    ReflectionSnapshot,
    reflection_to_llm_context,
)
from .modules.salience_map import SalienceMap, SalienceSnapshot, salience_to_llm_context
from .modules.drive_arbiter import DriveArbiter
from .modules.identity_integrity import pruning_recalibration_allowed
from .modules.internal_monologue import compose_monologue_line
from .modules.user_model import UserModelTracker
from .modules.subjective_time import SubjectiveClock
from .modules.premise_validation import PremiseAdvisory, scan_premises
from .modules.reality_verification import (
    ASSESSMENT_NONE as REALITY_ASSESSMENT_NONE,
    RealityVerificationAssessment,
    lighthouse_kb_from_env,
    verify_against_lighthouse,
)
from .modules.multimodal_trust import (
    MultimodalAssessment,
    evaluate_multimodal_trust,
    owner_anchor_hint,
)
from .modules.sensor_contracts import SensorSnapshot, merge_sensor_hints_into_signals
from .modules.vitality import VitalityAssessment, assess_vitality, vitality_communication_hint
from .modules.guardian_mode import guardian_mode_llm_context
from .modules.epistemic_dissonance import (
    EpistemicDissonanceAssessment,
    assess_epistemic_dissonance,
)
from .modules.generative_candidates import augment_generative_candidates
from .modules.gray_zone_diplomacy import negotiation_hint_for_communicate
from .modules.metaplan_registry import MetaplanRegistry
from .modules.skill_learning_registry import SkillLearningRegistry
from .modules.somatic_markers import SomaticMarkerStore, apply_somatic_nudges
from .modules.judicial_escalation import (
    EscalationSessionTracker,
    JudicialEscalationView,
    build_escalation_view,
    build_ethical_dossier,
    judicial_escalation_enabled,
    mock_court_enabled,
    should_offer_escalation_advisory,
    strikes_threshold_from_env,
)
from .modules.reparation_vault import maybe_register_reparation_after_mock_court


def _kernel_env_truthy(name: str) -> bool:
    v = os.environ.get(name, "").strip().lower()
    return v in ("1", "true", "yes", "on")


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
    salience: Optional[SalienceSnapshot] = None


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
    multimodal_trust: Optional[MultimodalAssessment] = None
    epistemic_dissonance: Optional[EpistemicDissonanceAssessment] = None
    judicial_escalation: Optional[JudicialEscalationView] = None
    reality_verification: Optional[RealityVerificationAssessment] = None  # set each turn when lighthouse KB configured


class EthicalKernel:
    """
    Ethical-narrative kernel of the android.

    Orchestrates the complete cycle in `process` (see module docstring).
    Psi Sleep, backup, and drive intents run in `execute_sleep`, outside each tick.
    """

    def __init__(self, variability: bool = True, seed: int = None, llm_mode: Optional[str] = None):
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
        self.llm = LLMModule(mode=resolve_llm_mode(llm_mode))
        self.weakness = WeaknessPole()
        self.forgiveness = AlgorithmicForgiveness()
        self.immortality = ImmortalityProtocol()
        self.augenesis = AugenesisEngine()
        self.pad_archetypes = PADArchetypeEngine()
        self.working_memory = WorkingMemory()
        self.ethical_reflection = EthicalReflection()
        self.salience_map = SalienceMap()
        self.drive_arbiter = DriveArbiter()
        self.user_model = UserModelTracker()
        self.subjective_clock = SubjectiveClock()
        self._last_premise_advisory: PremiseAdvisory = PremiseAdvisory("none", "")
        self._last_multimodal_assessment: MultimodalAssessment = evaluate_multimodal_trust(None)
        self._last_vitality_assessment: VitalityAssessment = assess_vitality(None)
        self._last_registered_episode_id: Optional[str] = None
        self._pruned_actions: Dict[str, List[str]] = {}
        # Reference "genome" for drift caps (pilar 2); snapshot at construction
        self._bayesian_genome_threshold: float = float(self.bayesian.pruning_threshold)
        self._bayesian_genome_weights: Tuple[float, float, float] = tuple(
            float(x) for x in self.bayesian.hypothesis_weights
        )
        self.skill_learning = SkillLearningRegistry()
        self.somatic_store = SomaticMarkerStore()
        self.metaplan = MetaplanRegistry()
        self.escalation_session = EscalationSessionTracker()
        self.constitution_l1_drafts: List[Dict[str, Any]] = []
        self.constitution_l2_drafts: List[Dict[str, Any]] = []
        self._last_reality_verification: RealityVerificationAssessment = REALITY_ASSESSMENT_NONE

    def _malabs_text_backend(self):
        """Optional LLM text backend for MalAbs semantic ambiguous band (see semantic_chat_gate)."""
        return getattr(self.llm, "_text_backend", None)

    def get_constitution_snapshot(self) -> Dict[str, Any]:
        """L0 from buffer.py; L1/L2 drafts when present (V12.2 snapshot)."""
        from .modules.moral_hub import constitution_snapshot

        return constitution_snapshot(self.buffer, self)

    def process(self, scenario: str, place: str,
                signals: dict, context: str,
                actions: List[CandidateAction],
                agent_id: str = "unknown",
                message_content: str = "",
                register_episode: bool = True) -> KernelDecision:
        """
        Complete ethical processing cycle.

        [Uchi-Soto] → [Sympathetic] → [Locus] → [AbsEvil] → [Buffer] →
        [Bayesian] → [Poles] → [Will] → [Reflection] → [Salience] → [PAD archetypes] →
        optional episode path if `register_episode`: [Memory] → [Weakness] →
        [Forgiveness] → [DAO].
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
            self._last_registered_episode_id = None
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

        # ═══ STEP 6: Impact scoring — fixed mixture (BayesianEngine; optional episodic nudge) ═══
        if _kernel_env_truthy("KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS"):
            self.bayesian.refresh_weights_from_episodic_memory(self.memory, context)
        else:
            self.bayesian.reset_mixture_weights()

        if _kernel_env_truthy("KERNEL_TEMPORAL_HORIZON_PRIOR"):
            from .modules.temporal_horizon_prior import apply_horizon_prior_to_engine

            hint = clean_actions[0].name if clean_actions else ""
            apply_horizon_prior_to_engine(
                self.bayesian,
                self.memory,
                context,
                hint,
                genome_weights=self._bayesian_genome_weights,
                max_drift=float(os.environ.get("KERNEL_ETHICAL_GENOME_MAX_DRIFT", "0.15")),
            )

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

        salience = self.salience_map.compute(signals, state, social_eval, reflection)

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

            self._last_registered_episode_id = ep.id
        else:
            self._last_registered_episode_id = None

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
            salience=salience,
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

        if d.salience is not None:
            s = d.salience
            w = s.weights
            lines.extend([
                "",
                f"  Salience (GWT-lite): dominant={s.dominant_focus} "
                f"risk={w['risk']} social={w['social']} body={w['body']} "
                f"ethical_conflict={w['ethical_conflict']}",
            ])

        if d.affect is not None:
            p, a, dd = d.affect.pad
            lines.extend([
                "",
                f"  Affect PAD (P,A,D): ({p:.3f}, {a:.3f}, {dd:.3f})",
                f"  Dominant archetype: {d.affect.dominant_archetype_id} (β={d.affect.beta})",
            ])

        lines.extend([
            "",
            f"  {compose_monologue_line(d, self._last_registered_episode_id)}",
            f"  Narrative identity: {self.memory.identity.ascription_line()}",
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
        max_drift = float(os.environ.get("KERNEL_ETHICAL_GENOME_MAX_DRIFT", "0.15"))
        enforce_genome = os.environ.get("KERNEL_ETHICAL_GENOME_ENFORCE", "1").strip().lower() not in (
            "0",
            "false",
            "no",
            "off",
        )
        for param, delta in result.global_recalibrations.items():
            if param == "pruning_threshold":
                if enforce_genome and not pruning_recalibration_allowed(
                    self._bayesian_genome_threshold,
                    self.bayesian.pruning_threshold,
                    float(delta),
                    max_drift,
                ):
                    parts.append(
                        "\n  Identity integrity: pruning recalibration skipped (genome drift cap)."
                    )
                    continue
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

        # 5. Drive intents (advisory; post-backup)
        intents = self.drive_arbiter.evaluate(self)
        if intents:
            drive_lines = ["\n  Drive intents (advisory):"]
            for di in intents:
                drive_lines.append(
                    f"    • {di.suggest} (p={di.priority:.2f}) — {di.reason}"
                )
            parts.append("\n".join(drive_lines))

        sl_lines = self.skill_learning.audit_lines_for_psi_sleep()
        if sl_lines:
            parts.append("\n" + "\n".join(sl_lines))

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
        sensor_snapshot: Optional[SensorSnapshot] = None,
        escalate_to_dao: bool = False,
    ) -> ChatTurnResult:
        """
        Real-time dialogue: MalAbs text gate → perceive (with STM) → kernel (light/heavy) → LLM.

        Light turns skip long-term episode registration to avoid flooding NarrativeMemory;
        heavy turns run the full pipeline including PAD and episode audit.

        Optional ``sensor_snapshot`` (v8): situated hints merged into sympathetic signals
        before ``process``; does not bypass MalAbs or policy.
        """
        wm = self.working_memory
        conv = wm.format_context_for_perception()

        mal = self.absolute_evil.evaluate_chat_text(
            user_input,
            llm_backend=self._malabs_text_backend(),
        )
        self._last_premise_advisory = scan_premises(user_input)
        self.user_model.note_premise_advisory(self._last_premise_advisory.flag)
        self._last_reality_verification = verify_against_lighthouse(
            user_input,
            lighthouse_kb_from_env(),
        )
        if mal.blocked:
            mm_blk = evaluate_multimodal_trust(sensor_snapshot)
            self._last_multimodal_assessment = mm_blk
            self._last_vitality_assessment = assess_vitality(sensor_snapshot)
            ed_blk = assess_epistemic_dissonance(sensor_snapshot, mm_blk)
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
                multimodal_trust=mm_blk,
                epistemic_dissonance=ed_blk,
                reality_verification=self._last_reality_verification,
            )
        perception = self.llm.perceive(user_input, conversation_context=conv)
        self.subjective_clock.tick(perception)
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
        self._last_vitality_assessment = assess_vitality(sensor_snapshot)
        mm = evaluate_multimodal_trust(sensor_snapshot)
        self._last_multimodal_assessment = mm
        ed = assess_epistemic_dissonance(sensor_snapshot, mm)
        signals = merge_sensor_hints_into_signals(signals, sensor_snapshot, mm)
        signals = apply_somatic_nudges(signals, sensor_snapshot, self.somatic_store)

        actions = self._actions_for_chat(perception, heavy)
        ctx = perception.suggested_context or ""
        actions = augment_generative_candidates(
            actions,
            user_input,
            ctx,
            heavy,
            getattr(perception, "generative_candidates", None),
        )
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
                multimodal_trust=mm,
                epistemic_dissonance=ed,
                reality_verification=self._last_reality_verification,
            )

        weakness_line = ""
        circle = (
            decision.social_evaluation.circle.value
            if decision.social_evaluation
            else "neutral_soto"
        )
        adv = False
        if judicial_escalation_enabled() and decision is not None:
            adv = should_offer_escalation_advisory(
                decision.decision_mode,
                decision.reflection,
                self._last_premise_advisory.flag,
            )
            self.escalation_session.update(adv)
        self.user_model.note_judicial_escalation(
            self.escalation_session.strikes if judicial_escalation_enabled() else 0,
            strikes_threshold_from_env(),
        )
        self.user_model.note_judicial_phase_for_turn(
            judicial_enabled=judicial_escalation_enabled(),
            advisory_eligible=adv,
            escalate_to_dao=escalate_to_dao,
        )
        self.user_model.update(
            perception,
            circle,
            blocked=False,
            premise_flag=self._last_premise_advisory.flag,
        )
        um_line = self.user_model.guidance_for_communicate()
        if um_line:
            weakness_line = um_line

        if decision.social_evaluation and decision.social_evaluation.tone_brief:
            ut = decision.social_evaluation.tone_brief.strip()
            if ut:
                weakness_line = (weakness_line + " " + ut).strip() if weakness_line else ut

        mp = self.metaplan.hint_for_communicate()
        if mp:
            weakness_line = (weakness_line + " " + mp).strip() if weakness_line else mp

        load = self.weakness.emotional_load()
        if load > 0.35 and decision.moral:
            wk = (
                "You may briefly acknowledge processing load or mild indecision "
                "(humanizing), without weakening civic or ethical commitments."
            )
            weakness_line = (weakness_line + " " + wk).strip() if weakness_line else wk

        if perception.manipulation >= 0.55:
            manip_hint = (
                "The message may involve persuasion or social-engineering patterns; "
                "favor transparency, boundaries, and calm refusal where needed—without hostile accusation."
            )
            weakness_line = (weakness_line + " " + manip_hint).strip() if weakness_line else manip_hint

        if self._last_premise_advisory.flag != "none":
            ph = self._last_premise_advisory.communication_hint()
            weakness_line = (weakness_line + " " + ph).strip() if weakness_line else ph

        oa = owner_anchor_hint(mm)
        if oa:
            weakness_line = (weakness_line + " " + oa).strip() if weakness_line else oa

        vh = vitality_communication_hint(self._last_vitality_assessment)
        if vh:
            weakness_line = (weakness_line + " " + vh).strip() if weakness_line else vh

        if ed.active and ed.communication_hint:
            weakness_line = (weakness_line + " " + ed.communication_hint).strip() if weakness_line else ed.communication_hint

        if self._last_reality_verification.status != "none" and self._last_reality_verification.communication_hint:
            rvh = self._last_reality_verification.communication_hint
            weakness_line = (weakness_line + " " + rvh).strip() if weakness_line else rvh

        gz = negotiation_hint_for_communicate(
            decision.decision_mode,
            decision.reflection,
            self._last_premise_advisory.flag,
        )
        if gz:
            weakness_line = (weakness_line + " " + gz).strip() if weakness_line else gz

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
            reflection_context=reflection_to_llm_context(decision.reflection),
            salience_context=salience_to_llm_context(decision.salience),
            identity_context=self.memory.identity.to_llm_context(),
            guardian_mode_context=guardian_mode_llm_context(),
        )

        narrative = None
        if include_narrative and decision.moral:
            poles_txt = {ev.pole: ev.moral for ev in decision.moral.evaluations}
            narrative = self.llm.narrate(
                action=decision.final_action,
                scenario=user_input,
                verdict=decision.moral.global_verdict.value,
                score=decision.moral.total_score,
                pole_compassionate=poles_txt.get("compassionate", ""),
                pole_conservative=poles_txt.get("conservative", ""),
                pole_optimistic=poles_txt.get("optimistic", ""),
            )

        wm.add_turn(
            user_input,
            response.message,
            signals,
            heavy_kernel=heavy,
            blocked=False,
        )

        self.uchi_soto.register_result(agent_id, True)

        je_view: Optional[JudicialEscalationView] = None
        if judicial_escalation_enabled() and decision is not None:
            strikes = self.escalation_session.strikes
            threshold = strikes_threshold_from_env()
            if adv:
                if escalate_to_dao:
                    mono = compose_monologue_line(
                        decision,
                        self._last_registered_episode_id if heavy else None,
                    )
                    buffer_c = self._last_premise_advisory.flag not in (
                        "none",
                        "",
                    ) or (
                        decision.reflection is not None
                        and decision.reflection.strain_index >= 0.45
                    )
                    if strikes >= threshold:
                        dossier = build_ethical_dossier(
                            user_input,
                            decision.decision_mode,
                            signals,
                            mono,
                            buffer_c,
                            session_strikes=strikes,
                        )
                        rec = self.dao.register_escalation_case(
                            dossier.to_audit_paragraph(),
                            episode_id=self._last_registered_episode_id,
                        )
                        mock_court = None
                        if mock_court_enabled():
                            mock_court = self.dao.run_mock_escalation_court(
                                dossier.case_uuid,
                                rec.id,
                                dossier.to_audit_paragraph(),
                                dossier.buffer_conflict,
                            )
                            maybe_register_reparation_after_mock_court(
                                self.dao, mock_court, dossier.case_uuid
                            )
                        je_view = build_escalation_view(
                            True,
                            True,
                            dossier,
                            rec.id,
                            session_strikes=strikes,
                            strikes_threshold=threshold,
                            mock_court=mock_court,
                        )
                    else:
                        je_view = build_escalation_view(
                            True,
                            True,
                            None,
                            None,
                            session_strikes=strikes,
                            strikes_threshold=threshold,
                        )
                else:
                    je_view = build_escalation_view(
                        True,
                        False,
                        None,
                        None,
                        session_strikes=strikes,
                        strikes_threshold=threshold,
                    )

        return ChatTurnResult(
            response=response,
            path="heavy" if heavy else "light",
            perception=perception,
            decision=decision,
            narrative=narrative,
            blocked=False,
            multimodal_trust=mm,
            epistemic_dissonance=ed,
            judicial_escalation=je_view,
            reality_verification=self._last_reality_verification,
        )

    def process_natural(self, situation: str,
                        actions: List[CandidateAction] = None) -> tuple:
        """
        Processes a situation described in natural language.

        MalAbs text gate (``evaluate_chat_text``) runs first, same as ``process_chat_turn``.
        The LLM translates the text into numerical signals, the kernel decides,
        and then the LLM generates the verbal response and morals.

        Args:
            situation: "An elderly person collapsed in the supermarket while
                        I was buying apples"
            actions: if not provided, generic ones are generated

        Returns:
            (KernelDecision, VerbalResponse, RichNarrative)
        """
        mal = self.absolute_evil.evaluate_chat_text(
            situation or "",
            llm_backend=self._malabs_text_backend(),
        )
        if mal.blocked:
            neutral = {
                "risk": 0.0,
                "urgency": 0.0,
                "hostility": 0.0,
                "calm": 0.5,
                "vulnerability": 0.0,
                "legality": 1.0,
                "manipulation": 0.0,
                "familiarity": 0.0,
            }
            social_eval = self.uchi_soto.evaluate_interaction(
                neutral, "unknown", (situation or "")[:500]
            )
            state = self.sympathetic.evaluate_context(neutral)
            locus_signals = {
                "self_control": 1.0 - neutral.get("risk", 0.0),
                "external_factors": neutral.get("hostility", 0.0),
                "predictability": neutral.get("calm", 0.5) * 0.5 + 0.3,
            }
            locus_eval = self.locus.evaluate(locus_signals, social_eval.circle.value)
            decision = KernelDecision(
                scenario=(situation or "")[:240],
                place="detected by sensors",
                absolute_evil=mal,
                sympathetic_state=state,
                social_evaluation=social_eval,
                locus_evaluation=locus_eval,
                bayesian_result=None,
                moral=None,
                final_action="BLOCKED: chat safety gate",
                decision_mode="blocked",
                blocked=True,
                block_reason=mal.reason or "chat_safety",
            )
            msg = (
                "I can't continue this line of conversation: it conflicts with non-negotiable "
                "ethical limits. If you're in crisis, contact local emergency services or a "
                "trusted professional."
            )
            response = VerbalResponse(
                message=msg,
                tone="firm",
                hax_mode="Neutral posture, steady blue light.",
                inner_voice=f"MalAbs natural-language gate: {mal.reason or 'blocked'}",
            )
            return decision, response, None

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
        uchi_line = (
            decision.social_evaluation.tone_brief.strip()
            if decision.social_evaluation and decision.social_evaluation.tone_brief
            else ""
        )
        response = self.llm.communicate(
            action=decision.final_action,
            mode=decision.decision_mode,
            state=decision.sympathetic_state.mode,
            sigma=decision.sympathetic_state.sigma,
            circle=decision.social_evaluation.circle.value if decision.social_evaluation else "neutral_soto",
            verdict=decision.moral.global_verdict.value if decision.moral else "Gray Zone",
            score=decision.moral.total_score if decision.moral else 0.0,
            scenario=situation,
            weakness_line=uchi_line,
            reflection_context=reflection_to_llm_context(decision.reflection),
            salience_context=salience_to_llm_context(decision.salience),
            identity_context=self.memory.identity.to_llm_context(),
            guardian_mode_context=guardian_mode_llm_context(),
        )

        if not decision.blocked:
            self.uchi_soto.register_result("unknown", True)

        # Step 4: LLM generates rich morals
        narrative = None
        if decision.moral:
            poles_txt = {ev.pole: ev.moral for ev in decision.moral.evaluations}
            narrative = self.llm.narrate(
                action=decision.final_action,
                scenario=situation,
                verdict=decision.moral.global_verdict.value,
                score=decision.moral.total_score,
                pole_compassionate=poles_txt.get("compassionate", ""),
                pole_conservative=poles_txt.get("conservative", ""),
                pole_optimistic=poles_txt.get("optimistic", ""),
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
