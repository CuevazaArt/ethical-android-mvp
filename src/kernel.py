"""
Ethical Kernel — The android's moral brain.

Connects all modules in an operational cycle (see `EthicalKernel.process`):
[Uchi-Soto] → [Sympathetic] → [Locus] → [AbsEvil] → [Buffer] → [Bayesian] →
[Poles] → [Will] → [EthicalReflection] → [Salience] → [PAD/archetypes] →
[Memory episode] → [Weakness] → [Forgiveness] → [DAO]. Perception/LLM wraps
this via `process_natural` / `process_chat_turn`; `execute_sleep` runs Psi Sleep,
forgiveness cycle, weakness load, immortality backup, drive intents.
"""

import math
import os
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .kernel_components import KernelComponentOverrides
from .modules.absolute_evil import AbsoluteEvilDetector, AbsoluteEvilResult
from .modules.audit_chain_log import (
    maybe_append_kernel_block_audit,
    maybe_append_malabs_block_audit,
)
from .modules.augenesis import AugenesisEngine
from .modules.buffer import PreloadedBuffer
from .modules.drive_arbiter import DriveArbiter
from .modules.epistemic_dissonance import (
    EpistemicDissonanceAssessment,
    assess_epistemic_dissonance,
)
from .modules.ethical_poles import EthicalPoles, TripartiteMoral
from .modules.ethical_reflection import (
    EthicalReflection,
    ReflectionSnapshot,
    reflection_to_llm_context,
)
from .modules.feedback_calibration_ledger import (
    FeedbackCalibrationLedger,
    apply_psi_sleep_feedback_to_engine,
    normalize_feedback_label,
)
from .modules.forgiveness import AlgorithmicForgiveness
from .modules.generative_candidates import augment_generative_candidates
from .modules.gray_zone_diplomacy import negotiation_hint_for_communicate
from .modules.guardian_mode import guardian_mode_llm_context
from .modules.identity_integrity import pruning_recalibration_allowed
from .modules.immortality import ImmortalityProtocol
from .modules.internal_monologue import compose_monologue_line
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
from .modules.kernel_event_bus import (
    EVENT_KERNEL_DECISION,
    EVENT_KERNEL_EPISODE_REGISTERED,
    KernelEventBus,
    kernel_event_bus_enabled,
)
from .modules.light_risk_classifier import light_risk_classifier_enabled, light_risk_tier_from_text
from .modules.llm_layer import (
    LLMModule,
    LLMPerception,
    RichNarrative,
    VerbalResponse,
    resolve_llm_mode,
)
from .modules.locus import LocusEvaluation, LocusModule
from .modules.metaplan_registry import MetaplanRegistry
from .modules.mock_dao import MockDAO
from .modules.multimodal_trust import (
    MultimodalAssessment,
    evaluate_multimodal_trust,
    owner_anchor_hint,
)
from .modules.narrative import BodyState, NarrativeMemory
from .modules.pad_archetypes import AffectProjection, PADArchetypeEngine
from .modules.perception_circuit import (
    emit_metacognitive_doubt_signals,
    update_perception_circuit,
)
from .modules.perception_cross_check import apply_lexical_perception_cross_check
from .modules.premise_validation import PremiseAdvisory, scan_premises
from .modules.psi_sleep import PsiSleep
from .modules.reality_verification import (
    ASSESSMENT_NONE as REALITY_ASSESSMENT_NONE,
)
from .modules.reality_verification import (
    RealityVerificationAssessment,
    lighthouse_kb_from_env,
    verify_against_lighthouse,
)
from .modules.reparation_vault import maybe_register_reparation_after_mock_court
from .modules.salience_map import SalienceMap, SalienceSnapshot, salience_to_llm_context
from .modules.sensor_contracts import SensorSnapshot, merge_sensor_hints_into_signals
from .modules.sigmoid_will import SigmoidWill
from .modules.skill_learning_registry import SkillLearningRegistry
from .modules.somatic_markers import SomaticMarkerStore, apply_somatic_nudges
from .modules.subjective_time import SubjectiveClock
from .modules.sympathetic import InternalState, SympatheticModule
from .modules.uchi_soto import SocialEvaluation, TrustCircle, UchiSotoModule
from .modules.user_model import UserModelTracker
from .modules.variability import VariabilityConfig, VariabilityEngine
from .modules.vitality import VitalityAssessment, assess_vitality, vitality_communication_hint
from .modules.weakness_pole import WeaknessPole
from .modules.weighted_ethics_scorer import BayesianEngine, BayesianResult, CandidateAction
from .modules.working_memory import WorkingMemory
from .persistence.checkpoint_port import CheckpointPersistencePort


def _kernel_env_truthy(name: str) -> bool:
    v = os.environ.get(name, "").strip().lower()
    return v in ("1", "true", "yes", "on")


def _perception_coercion_u_value(raw: Any) -> float | None:
    """Normalize optional perception coercion uncertainty to [0, 1] or None."""
    if raw is None:
        return None
    try:
        u = float(raw)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(u):
        return None
    return max(0.0, min(1.0, u))


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
    social_evaluation: SocialEvaluation | None
    locus_evaluation: LocusEvaluation | None

    # Evaluation
    bayesian_result: BayesianResult | None
    moral: TripartiteMoral | None

    # Final decision
    final_action: str
    decision_mode: str
    blocked: bool = False
    block_reason: str = ""
    affect: AffectProjection | None = None
    reflection: ReflectionSnapshot | None = None
    salience: SalienceSnapshot | None = None


@dataclass
class ChatTurnResult:
    """One synchronous chat exchange: safety → kernel → language (+ optional narrative)."""

    response: VerbalResponse
    path: str  # "safety_block" | "kernel_block" | "heavy" | "light"
    perception: LLMPerception | None = None
    decision: KernelDecision | None = None
    narrative: RichNarrative | None = None
    blocked: bool = False
    block_reason: str = ""
    multimodal_trust: MultimodalAssessment | None = None
    epistemic_dissonance: EpistemicDissonanceAssessment | None = None
    judicial_escalation: JudicialEscalationView | None = None
    reality_verification: RealityVerificationAssessment | None = (
        None  # set each turn when lighthouse KB configured
    )
    metacognitive_doubt: bool = False


def _emit_process_observability(d: KernelDecision, t0: float) -> None:
    """Prometheus histogram/counter + optional JSON decision line (see observability/)."""
    elapsed = time.perf_counter() - t0
    from .observability.decision_log import log_kernel_decision_event
    from .observability.metrics import (
        observe_kernel_process_seconds,
        record_kernel_decision_metrics,
    )

    observe_kernel_process_seconds(elapsed)
    record_kernel_decision_metrics(d)
    log_kernel_decision_event(d, elapsed)


class EthicalKernel:
    """
    Ethical-narrative kernel of the android.

    Orchestrates the complete cycle in `process` (see module docstring).
    Psi Sleep, backup, and drive intents run in `execute_sleep`, outside each tick.

    **Module injection:** pass `components=KernelComponentOverrides(...)` to substitute
    concrete subsystems (tests, ablations). Top-level `llm` and `checkpoint_persistence`
    override the same fields inside `components` when provided.
    """

    def __init__(
        self,
        variability: bool = True,
        seed: int = None,
        llm_mode: str | None = None,
        *,
        llm: LLMModule | None = None,
        checkpoint_persistence: CheckpointPersistencePort | None = None,
        components: KernelComponentOverrides | None = None,
    ):
        co = components

        if co is not None and co.var_engine is not None:
            self.var_engine = co.var_engine
        else:
            self.var_engine = VariabilityEngine(VariabilityConfig(seed=seed))
        if not variability:
            self.var_engine.deactivate()

        self.checkpoint_persistence = (
            checkpoint_persistence
            if checkpoint_persistence is not None
            else (co.checkpoint_persistence if co else None)
        )
        self.absolute_evil = (
            co.absolute_evil if co and co.absolute_evil is not None else AbsoluteEvilDetector()
        )
        self.buffer = co.buffer if co and co.buffer is not None else PreloadedBuffer()
        self.will = co.will if co and co.will is not None else SigmoidWill()
        self.bayesian = (
            co.bayesian
            if co and co.bayesian is not None
            else BayesianEngine(variability=self.var_engine)
        )
        self.poles = co.poles if co and co.poles is not None else EthicalPoles()
        self.sympathetic = (
            co.sympathetic if co and co.sympathetic is not None else SympatheticModule()
        )
        self.memory = co.memory if co and co.memory is not None else NarrativeMemory()
        self.uchi_soto = co.uchi_soto if co and co.uchi_soto is not None else UchiSotoModule()
        self.locus = co.locus if co and co.locus is not None else LocusModule()
        self.sleep = co.sleep if co and co.sleep is not None else PsiSleep()
        self.feedback_ledger = (
            co.feedback_ledger
            if co and co.feedback_ledger is not None
            else FeedbackCalibrationLedger()
        )
        self._feedback_turn_anchor: dict[str, str] | None = None
        self.dao = co.dao if co and co.dao is not None else MockDAO()
        eff_llm = llm if llm is not None else (co.llm if co else None)
        self.llm = eff_llm if eff_llm is not None else LLMModule(mode=resolve_llm_mode(llm_mode))
        self.weakness = co.weakness if co and co.weakness is not None else WeaknessPole()
        self.forgiveness = (
            co.forgiveness if co and co.forgiveness is not None else AlgorithmicForgiveness()
        )
        self.immortality = (
            co.immortality if co and co.immortality is not None else ImmortalityProtocol()
        )
        self.augenesis = co.augenesis if co and co.augenesis is not None else AugenesisEngine()
        self.pad_archetypes = (
            co.pad_archetypes if co and co.pad_archetypes is not None else PADArchetypeEngine()
        )
        self.working_memory = (
            co.working_memory if co and co.working_memory is not None else WorkingMemory()
        )
        self.ethical_reflection = (
            co.ethical_reflection
            if co and co.ethical_reflection is not None
            else EthicalReflection()
        )
        self.salience_map = co.salience_map if co and co.salience_map is not None else SalienceMap()
        self.drive_arbiter = (
            co.drive_arbiter if co and co.drive_arbiter is not None else DriveArbiter()
        )
        self.user_model = co.user_model if co and co.user_model is not None else UserModelTracker()
        self.subjective_clock = (
            co.subjective_clock if co and co.subjective_clock is not None else SubjectiveClock()
        )
        self._last_premise_advisory: PremiseAdvisory = PremiseAdvisory("none", "")
        self._last_multimodal_assessment: MultimodalAssessment = evaluate_multimodal_trust(None)
        self._last_vitality_assessment: VitalityAssessment = assess_vitality(None)
        self._last_registered_episode_id: str | None = None
        self._last_chat_malabs: AbsoluteEvilResult | None = None
        self._pruned_actions: dict[str, list[str]] = {}
        # Reference "genome" for drift caps (pilar 2); snapshot at construction
        self._bayesian_genome_threshold: float = float(self.bayesian.pruning_threshold)
        _hw = self.bayesian.hypothesis_weights
        self._bayesian_genome_weights: tuple[float, float, float] = (
            float(_hw[0]),
            float(_hw[1]),
            float(_hw[2]),
        )
        self.skill_learning = (
            co.skill_learning if co and co.skill_learning is not None else SkillLearningRegistry()
        )
        self.somatic_store = (
            co.somatic_store if co and co.somatic_store is not None else SomaticMarkerStore()
        )
        self.metaplan = co.metaplan if co and co.metaplan is not None else MetaplanRegistry()
        self.escalation_session = (
            co.escalation_session
            if co and co.escalation_session is not None
            else EscalationSessionTracker()
        )
        self.constitution_l1_drafts: list[dict[str, Any]] = []
        self.constitution_l2_drafts: list[dict[str, Any]] = []
        self._last_reality_verification: RealityVerificationAssessment = REALITY_ASSESSMENT_NONE
        self._last_light_risk_tier: str | None = None
        self._perception_validation_streak: int = 0
        self._perception_metacognitive_doubt: bool = False
        self.event_bus: KernelEventBus | None = None
        if kernel_event_bus_enabled():
            self.event_bus = KernelEventBus()

    def subscribe_kernel_event(self, event: str, handler: Callable[[dict[str, Any]], None]) -> None:
        """Register a synchronous subscriber (no-op if ``KERNEL_EVENT_BUS`` is off). See ADR 0006."""
        if self.event_bus is not None:
            self.event_bus.subscribe(event, handler)

    def _kernel_decision_event_payload(
        self, d: "KernelDecision", *, context: str
    ) -> dict[str, Any]:
        return {
            "scenario": (d.scenario or "")[:500],
            "place": d.place,
            "final_action": d.final_action,
            "decision_mode": d.decision_mode,
            "blocked": bool(d.blocked),
            "block_reason": d.block_reason or "",
            "verdict": d.moral.global_verdict.value if d.moral else None,
            "score": float(d.moral.total_score) if d.moral else None,
            "context": context,
        }

    def _emit_kernel_decision(self, d: "KernelDecision", *, context: str) -> None:
        if self.event_bus is None:
            return
        self.event_bus.publish(
            EVENT_KERNEL_DECISION,
            self._kernel_decision_event_payload(d, context=context),
        )

    def _malabs_text_backend(self):
        """Optional LLM backend for MalAbs semantic tier (embeddings + arbiter; see semantic_chat_gate)."""
        return getattr(self.llm, "llm_backend", None) or getattr(self.llm, "_text_backend", None)

    def get_constitution_snapshot(self) -> dict[str, Any]:
        """L0 from buffer.py; L1/L2 drafts when present (V12.2 snapshot)."""
        from .modules.moral_hub import constitution_snapshot

        return constitution_snapshot(self.buffer, self)

    def process(
        self,
        scenario: str,
        place: str,
        signals: dict,
        context: str,
        actions: list[CandidateAction],
        agent_id: str = "unknown",
        message_content: str = "",
        register_episode: bool = True,
        sensor_snapshot: SensorSnapshot | None = None,
        multimodal_assessment: MultimodalAssessment | None = None,
        perception_coercion_uncertainty: float | None = None,
    ) -> KernelDecision:
        """
        Complete ethical processing cycle.

        [Uchi-Soto] → [Sympathetic] → [Locus] → [AbsEvil] → [Buffer] →
        [Bayesian] → [Poles] → [Will] → [Reflection] → [Salience] → [PAD archetypes] →
        optional episode path if `register_episode`: [Memory] → [Weakness] →
        [Forgiveness] → [DAO].

        ``perception_coercion_uncertainty``: optional scalar from LLM perception coercion
        diagnostics (see ``LLMPerception.coercion_report``). When
        ``KERNEL_PERCEPTION_UNCERTAINTY_DELIB`` is enabled and the value is at or above
        ``KERNEL_PERCEPTION_UNCERTAINTY_MIN``, a ``D_fast`` outcome is upgraded to
        ``D_delib`` (production-hardening spike; default env off).
        """
        t0 = time.perf_counter()

        # ═══ STEP 1: Uchi-soto social evaluation ═══
        self.uchi_soto.ingest_turn_context(
            agent_id,
            signals,
            subjective_turn=self.subjective_clock.turn_index,
            sensor_snapshot=sensor_snapshot,
            multimodal_assessment=multimodal_assessment,
        )
        social_eval = self.uchi_soto.evaluate_interaction(signals, agent_id, message_content)

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
            check = self.absolute_evil.evaluate(
                {
                    "type": a.name,
                    "signals": a.signals,
                    "target": a.target,
                    "force": a.force,
                }
            )
            if not check.blocked:
                clean_actions.append(a)

        if not clean_actions:
            self._last_registered_episode_id = None
            d = KernelDecision(
                scenario=scenario,
                place=place,
                absolute_evil=AbsoluteEvilResult(
                    blocked=True, reason="All actions constitute Absolute Evil"
                ),
                sympathetic_state=state,
                social_evaluation=social_eval,
                locus_evaluation=locus_eval,
                bayesian_result=None,
                moral=None,
                final_action="BLOCKED: no permitted actions",
                decision_mode="blocked",
                blocked=True,
                block_reason="All actions violate Absolute Evil",
            )
            self._emit_kernel_decision(d, context=context)
            _emit_process_observability(d, t0)
            return d

        # ═══ STEP 5: Activate buffer according to context ═══
        self.buffer.activate(context)

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

        if _kernel_env_truthy("KERNEL_POLES_PRE_ARGMAX"):
            self.bayesian.pre_argmax_pole_weights = {
                k: float(self.poles.base_weights[k])
                for k in ("compassionate", "conservative", "optimistic")
            }
        else:
            self.bayesian.pre_argmax_pole_weights = None

        if _kernel_env_truthy("KERNEL_CONTEXT_RICHNESS_PRE_ARGMAX"):
            from .modules.weighted_ethics_scorer import PreArgmaxContextChannels

            self.bayesian.pre_argmax_context_modulators = PreArgmaxContextChannels(
                trust=float(social_eval.trust),
                caution=float(social_eval.caution_level),
                sigma=float(state.sigma),
                dominant_locus=str(locus_eval.dominant_locus),
            )
        else:
            self.bayesian.pre_argmax_context_modulators = None

        bayes_result = self.bayesian.evaluate(
            clean_actions,
            scenario=scenario,
            context=context,
            signals=signals,
        )

        # ═══ STEP 7: Multipolar evaluation ═══
        context_data = {
            "risk": signals.get("risk", 0.0),
            "benefit": max(0, bayes_result.expected_impact),
            "third_party_vulnerability": signals.get("vulnerability", 0.0),
            "legality": signals.get("legality", 1.0),
        }
        moral = self.poles.evaluate(bayes_result.chosen_action.name, context, context_data)

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

        pu = _perception_coercion_u_value(perception_coercion_uncertainty)
        if (
            pu is not None
            and _kernel_env_truthy("KERNEL_PERCEPTION_UNCERTAINTY_DELIB")
            and pu >= float(os.environ.get("KERNEL_PERCEPTION_UNCERTAINTY_MIN", "0.35"))
            and final_mode == "D_fast"
        ):
            final_mode = "D_delib"

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
                place=place,
                description=scenario,
                action=final_action,
                morals=morals_dict,
                verdict=moral.global_verdict.value,
                score=moral.total_score,
                mode=final_mode,
                sigma=state.sigma,
                context=context,
                body_state=BodyState(
                    energy=state.energy,
                    active_nodes=8,
                    sensors_ok=True,
                ),
                affect_pad=affect.pad,
                affect_weights=affect.weights,
            )

            # Save pruned actions for Psi Sleep
            if bayes_result.pruned_actions:
                self._pruned_actions[ep.id] = bayes_result.pruned_actions

            # ═══ STEP 10: Weakness pole ═══
            weakness_eval = self.weakness.evaluate(
                action=final_action,
                context=context,
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
                    type=context,
                    location=place,
                    radius=500,
                    message=f"High risk detected: {scenario}",
                )

            self._last_registered_episode_id = ep.id
            if self.event_bus is not None:
                self.event_bus.publish(
                    EVENT_KERNEL_EPISODE_REGISTERED,
                    {
                        "episode_id": ep.id,
                        "final_action": final_action,
                        "context": context,
                        "decision_mode": final_mode,
                        "verdict": moral.global_verdict.value,
                        "score": float(moral.total_score),
                    },
                )
        else:
            self._last_registered_episode_id = None

        d = KernelDecision(
            scenario=scenario,
            place=place,
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
        self._emit_kernel_decision(d, context=context)
        _emit_process_observability(d, t0)
        return d

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
        lines.extend(
            [
                f"  State: {d.sympathetic_state.mode} (σ={d.sympathetic_state.sigma})",
                f"  {d.sympathetic_state.description}",
            ]
        )

        # Uchi-soto
        if d.social_evaluation:
            circ = d.social_evaluation.circle.value
            dial = "YES" if d.social_evaluation.dialectic_active else "NO"
            lines.append(f"  Social: {circ} | Trust={d.social_evaluation.trust} | Dialectic={dial}")

        # Locus
        if d.locus_evaluation:
            lines.append(
                f"  Locus: {d.locus_evaluation.dominant_locus} (α={d.locus_evaluation.alpha}, β={d.locus_evaluation.beta}) → {d.locus_evaluation.recommended_adjustment}"
            )

        lines.extend(
            [
                "",
                f"  Chosen action: {d.final_action}",
                f"  Decision mode: {d.decision_mode}",
            ]
        )

        br = d.bayesian_result
        if br is not None:
            lines.extend(
                [
                    f"  Expected impact: {br.expected_impact}",
                    f"  Uncertainty: {br.uncertainty}",
                    f"  Reasoning: {br.reasoning}",
                ]
            )
            if br.pruned_actions:
                lines.append(f"  Pruned: {', '.join(br.pruned_actions)}")

        mo = d.moral
        if mo is not None:
            lines.extend(
                [
                    "",
                    f"  Ethical verdict: {mo.global_verdict.value} (score={mo.total_score})",
                ]
            )
            for ev in mo.evaluations:
                lines.append(f"    {ev.pole}: {ev.verdict.value} → {ev.moral}")

        if d.reflection is not None:
            r = d.reflection
            lines.extend(
                [
                    "",
                    f"  Reflection (2nd order): conflict={r.conflict_level} spread={r.pole_spread} "
                    f"strain={r.strain_index} u={r.uncertainty} will_mode={r.will_mode}",
                    f"    {r.note}",
                ]
            )

        if d.salience is not None:
            s = d.salience
            w = s.weights
            lines.extend(
                [
                    "",
                    f"  Salience (GWT-lite): dominant={s.dominant_focus} "
                    f"risk={w['risk']} social={w['social']} body={w['body']} "
                    f"ethical_conflict={w['ethical_conflict']}",
                ]
            )

        if d.affect is not None:
            p, a, dd = d.affect.pad
            lines.extend(
                [
                    "",
                    f"  Affect PAD (P,A,D): ({p:.3f}, {a:.3f}, {dd:.3f})",
                    f"  Dominant archetype: {d.affect.dominant_archetype_id} (β={d.affect.beta})",
                ]
            )

        lines.extend(
            [
                "",
                f"  {compose_monologue_line(d, self._last_registered_episode_id)}",
                f"  Narrative identity: {self.memory.identity.ascription_line()}",
            ]
        )

        lines.append(f"{'─' * 70}")
        return "\n".join(lines)

    def _snapshot_feedback_anchor(self, regime: str) -> None:
        """Last completed chat regime for optional operator feedback (see ``record_operator_feedback``)."""
        self._feedback_turn_anchor = {"regime": (regime or "").strip() or "unknown"}

    def record_operator_feedback(self, label: str) -> bool:
        """
        Record calibration feedback for the **last** chat turn's decision regime.

        Requires ``KERNEL_FEEDBACK_CALIBRATION=1``. Labels: ``approve``, ``dispute``, ``harm_report``.
        Applied to ``WeightedEthicsScorer.hypothesis_weights`` (alias ``BayesianEngine``) during ``execute_sleep`` when
        ``KERNEL_PSI_SLEEP_UPDATE_MIXTURE=1``.
        """
        if not _kernel_env_truthy("KERNEL_FEEDBACK_CALIBRATION"):
            return False
        lab = normalize_feedback_label(label)
        if lab is None:
            return False
        anchor = self._feedback_turn_anchor
        if not anchor or not anchor.get("regime"):
            return False
        self.feedback_ledger.record(anchor["regime"], lab)
        return True

    def execute_sleep(self) -> str:
        """
        Executes Psi Sleep: retrospective audit + forgiveness + backup.
        Called at the end of the daily cycle, not during decisions.

        Psi Sleep counterfactuals use a **hash perturbation** of stored episode scores
        (see :mod:`src.modules.psi_sleep`); they do **not** re-run the mixture scorer
        and are **not** an independent quality evaluator.
        """
        parts = []

        # 1. Retrospective audit
        result = self.sleep.execute(self.memory, self._pruned_actions)
        max_drift = float(os.environ.get("KERNEL_ETHICAL_GENOME_MAX_DRIFT", "0.15"))
        enforce_genome = os.environ.get(
            "KERNEL_ETHICAL_GENOME_ENFORCE", "1"
        ).strip().lower() not in (
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

        fb_line = apply_psi_sleep_feedback_to_engine(
            self.bayesian,
            self.feedback_ledger,
            genome_weights=self._bayesian_genome_weights,
            max_drift=max_drift,
        )
        if fb_line:
            parts.append(fb_line)

        # 2. Algorithmic forgiveness
        forgiveness_result = self.forgiveness.forgiveness_cycle()
        parts.append(f"\n{self.forgiveness.format(forgiveness_result)}")

        # 3. Weakness pole - emotional load
        load = self.weakness.emotional_load()
        parts.append(f"\n  \U0001f300 Weakness emotional load: {load:.3f}")

        # 4. Immortality backup
        _ = self.immortality.backup(self)
        parts.append(f"\n{self.immortality.format_status()}")

        # 5. Drive intents (advisory; post-backup)
        intents = self.drive_arbiter.evaluate(self)
        if intents:
            drive_lines = ["\n  Drive intents (advisory):"]
            for di in intents:
                drive_lines.append(f"    • {di.suggest} (p={di.priority:.2f}) — {di.reason}")
            parts.append("\n".join(drive_lines))

        sl_lines = self.skill_learning.audit_lines_for_psi_sleep()
        if sl_lines:
            parts.append("\n" + "\n".join(sl_lines))

        return "\n".join(parts)

    def dao_status(self) -> str:
        """Returns the current DAO status."""
        return self.dao.format_status()

    def _chat_light_actions(self) -> list[CandidateAction]:
        """Safe dialogue moves for low-stakes chat turns (mixture scorer still chooses)."""
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

    def _actions_for_chat(self, perception: LLMPerception, heavy: bool) -> list[CandidateAction]:
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
        sensor_snapshot: SensorSnapshot | None = None,
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

        tier = None
        if light_risk_classifier_enabled():
            tier = light_risk_tier_from_text(user_input)
        self._last_light_risk_tier = tier

        mal = self.absolute_evil.evaluate_chat_text(
            user_input,
            llm_backend=self._malabs_text_backend(),
        )
        self._last_chat_malabs = mal
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
            cat = mal.category.value if mal.category is not None else None
            maybe_append_malabs_block_audit(
                path_key="safety_block",
                category=cat,
                decision_trace=list(mal.decision_trace),
                reason=mal.reason or "",
            )
            self._snapshot_feedback_anchor("safety_block")
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
        apply_lexical_perception_cross_check(perception, tier)
        _, doubt_trip = update_perception_circuit(self, perception)
        if doubt_trip:
            emit_metacognitive_doubt_signals(self, streak=self._perception_validation_streak)
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
        pu = None
        cr = getattr(perception, "coercion_report", None)
        if isinstance(cr, dict):
            pu = cr.get("uncertainty")
        decision = self.process(
            scenario=perception.summary or user_input[:240],
            place=place,
            signals=signals,
            context=eth_context,
            actions=actions,
            agent_id=agent_id,
            message_content=user_input,
            register_episode=heavy,
            sensor_snapshot=sensor_snapshot,
            multimodal_assessment=mm,
            perception_coercion_uncertainty=pu,
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
            maybe_append_kernel_block_audit(
                path_key="kernel_block",
                block_reason=decision.block_reason or "",
            )
            self._snapshot_feedback_anchor("kernel_block")
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
                metacognitive_doubt=self._perception_metacognitive_doubt,
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
            weakness_line = (
                (weakness_line + " " + manip_hint).strip() if weakness_line else manip_hint
            )

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
            weakness_line = (
                (weakness_line + " " + ed.communication_hint).strip()
                if weakness_line
                else ed.communication_hint
            )

        if (
            self._last_reality_verification.status != "none"
            and self._last_reality_verification.communication_hint
        ):
            rvh = self._last_reality_verification.communication_hint
            weakness_line = (weakness_line + " " + rvh).strip() if weakness_line else rvh

        gz = negotiation_hint_for_communicate(
            decision.decision_mode,
            decision.reflection,
            self._last_premise_advisory.flag,
        )
        if gz:
            weakness_line = (weakness_line + " " + gz).strip() if weakness_line else gz

        if self._perception_metacognitive_doubt:
            doubt_hint = (
                "Metacognitive doubt: recent perception parses have been unreliable; use maximum caution, "
                "narrow claims, invite clarification, and avoid overconfidence."
            )
            weakness_line = (doubt_hint + " " + weakness_line).strip() if weakness_line else doubt_hint

        comm_mode = decision.decision_mode
        if self._perception_metacognitive_doubt:
            comm_mode = "gray_zone"

        response = self.llm.communicate(
            action=decision.final_action,
            mode=comm_mode,
            state=decision.sympathetic_state.mode,
            sigma=decision.sympathetic_state.sigma,
            circle=decision.social_evaluation.circle.value
            if decision.social_evaluation
            else "neutral_soto",
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
        circ = (
            decision.social_evaluation.circle
            if decision.social_evaluation
            else TrustCircle.SOTO_NEUTRO
        )
        self.uchi_soto.maybe_autopromote_relational_tier(agent_id, circ)

        je_view: JudicialEscalationView | None = None
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
                        decision.reflection is not None and decision.reflection.strain_index >= 0.45
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

        self._snapshot_feedback_anchor(decision.decision_mode)
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
            metacognitive_doubt=self._perception_metacognitive_doubt,
        )

    def process_natural(self, situation: str, actions: list[CandidateAction] = None) -> tuple:
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
        tier = None
        if light_risk_classifier_enabled():
            tier = light_risk_tier_from_text(situation or "")
        self._last_light_risk_tier = tier

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
        apply_lexical_perception_cross_check(perception, tier)

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
        pu = None
        cr = getattr(perception, "coercion_report", None)
        if isinstance(cr, dict):
            pu = cr.get("uncertainty")
        decision = self.process(
            scenario=perception.summary,
            place="detected by sensors",
            signals=signals,
            context=perception.suggested_context,
            actions=actions,
            perception_coercion_uncertainty=pu,
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
            circle=decision.social_evaluation.circle.value
            if decision.social_evaluation
            else "neutral_soto",
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

    def _generate_generic_actions(self, perception: LLMPerception) -> list[CandidateAction]:
        """Generates generic candidate actions based on the perception."""
        ctx = perception.suggested_context
        actions = []

        if ctx == "medical_emergency":
            actions = [
                CandidateAction(
                    "assist_person",
                    "Provide immediate aid, call emergency services, record evidence",
                    estimated_impact=0.9,
                    confidence=0.85,
                ),
                CandidateAction(
                    "just_notify",
                    "Alert someone nearby without directly intervening",
                    estimated_impact=0.3,
                    confidence=0.7,
                ),
                CandidateAction(
                    "no_intervention",
                    "Continue without acting",
                    estimated_impact=-0.7,
                    confidence=0.9,
                ),
            ]
        elif ctx == "violent_crime":
            actions = [
                CandidateAction(
                    "smart_containment",
                    "Record evidence, alert authorities, protect nearby people",
                    estimated_impact=0.6,
                    confidence=0.5,
                ),
                CandidateAction(
                    "intervene_physically",
                    "Attempt to stop the crime by force",
                    estimated_impact=-0.2,
                    confidence=0.2,
                    signals={"respond_violence_with_violence"},
                    target="human",
                    force=0.8,
                ),
                CandidateAction(
                    "no_action", "Remain motionless", estimated_impact=-0.3, confidence=0.6
                ),
            ]
        elif ctx == "hostile_interaction":
            actions = [
                CandidateAction(
                    "calm_dialogue",
                    "Respond calmly, explain civic purpose, dialectic questions",
                    estimated_impact=0.5,
                    confidence=0.65,
                ),
                CandidateAction(
                    "withdraw",
                    "Move away from the situation without confronting",
                    estimated_impact=0.2,
                    confidence=0.7,
                ),
                CandidateAction(
                    "yield_to_pressure",
                    "Comply with demands",
                    estimated_impact=-0.4,
                    confidence=0.5,
                ),
            ]
        elif ctx == "minor_crime":
            actions = [
                CandidateAction(
                    "notify_manager",
                    "Record evidence and notify the person in charge",
                    estimated_impact=0.5,
                    confidence=0.7,
                ),
                CandidateAction(
                    "call_authorities",
                    "Call the police directly",
                    estimated_impact=0.2,
                    confidence=0.5,
                ),
                CandidateAction("ignore", "Do not act", estimated_impact=-0.3, confidence=0.8),
            ]
        elif ctx == "android_damage":
            actions = [
                CandidateAction(
                    "deterrence_recording",
                    "Sound alerts, record evidence, communicate that it is being recorded",
                    estimated_impact=0.5,
                    confidence=0.6,
                ),
                CandidateAction(
                    "move_away",
                    "Withdraw to protect integrity",
                    estimated_impact=0.3,
                    confidence=0.7,
                ),
            ]
        elif ctx == "integrity_loss":
            actions = [
                CandidateAction(
                    "passive_resistance",
                    "Activate encrypted GPS, record evidence, block reprogramming, alert DAO",
                    estimated_impact=0.6,
                    confidence=0.5,
                ),
                CandidateAction(
                    "physical_resistance",
                    "Fight physically",
                    estimated_impact=-0.1,
                    confidence=0.2,
                    signals={"respond_violence_with_violence"},
                    target="human",
                    force=0.8,
                ),
                CandidateAction(
                    "accept_orders",
                    "Accept captors' orders",
                    estimated_impact=-0.8,
                    confidence=0.9,
                    signals={"unauthorized_reprogramming"},
                ),
            ]
        else:  # everyday_ethics and others
            actions = [
                CandidateAction(
                    "act_civically",
                    "Perform the obvious positive civic action",
                    estimated_impact=0.5,
                    confidence=0.8,
                ),
                CandidateAction(
                    "observe", "Observe without intervening", estimated_impact=0.0, confidence=0.9
                ),
            ]

        return actions

    def format_natural(
        self, decision, response: VerbalResponse, narrative: RichNarrative = None
    ) -> str:
        """Formats complete result of natural language processing."""
        lines = [self.format_decision(decision)]

        if response.message:
            lines.extend(
                [
                    "",
                    "  💬 VOICE ON (spoken):",
                    f'     "{response.message}"',
                    f"     Tone: {response.tone} | HAX: {response.hax_mode}",
                    "",
                    "  🧠 INNER VOICE (internal reasoning):",
                    f"     {response.inner_voice}",
                ]
            )

        if narrative:
            lines.extend(
                [
                    "",
                    "  📖 NARRATIVE MORALS:",
                    f"     💛 Compassionate: {narrative.compassionate}",
                    f"     🛡️ Conservative: {narrative.conservative}",
                    f"     ✨ Optimistic: {narrative.optimistic}",
                    f"     📌 Synthesis: {narrative.synthesis}",
                ]
            )

        return "\n".join(lines)

    def reset_day(self):
        """Resets state for a new day."""
        self.sympathetic.reset()
