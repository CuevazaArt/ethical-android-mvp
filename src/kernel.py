"""
Ethical Kernel — The android's moral brain.

Connects all modules in an operational cycle (see `EthicalKernel.process`):
[Uchi-Soto] → [Sympathetic] → [Locus] → [AbsEvil] → [Buffer] → [Bayesian] →
[Poles] → [Will] → [EthicalReflection] → [Salience] → [PAD/archetypes] →
[Memory episode] → [Weakness] → [Forgiveness] → [DAO]. Perception/LLM wraps
this via `process_natural` / `process_chat_turn`; `execute_sleep` runs Psi Sleep,
forgiveness cycle, weakness load, immortality backup, drive intents.
"""

from __future__ import annotations

import asyncio
import math
import os
import threading
import time
import logging
from collections.abc import Callable

from src.modules.absolute_evil import AbsoluteEvilResult
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, AsyncGenerator

from .kernel_lobes import PerceptiveLobe, LimbicEthicalLobe, ExecutiveLobe, CerebellumLobe, MemoryLobe, CerebellumNode
from .kernel_lobes.models import LimbicStageResult, ExecutiveStageResult

class CorpusCallosumOrchestrator:
    """
    Architecture V2.0 - Quadrilobular Brain Orchestrator
    Actúa como el bus de eventos ligero entre los 4 Lóbulos Conscientes y el Cerebelo Adyacente.
    Gestiona la serialización del estado y la propagación de traumas asíncronos.
    """
    def __init__(self, kernel_ref: Optional['EthicalKernel'] = None):
        self.kernel_ref = kernel_ref
        
        # 1. Instanciar Subconsciente (Cerebelo)
        self._hw_interrupt = threading.Event()
        self.cerebellum = CerebellumNode(self._hw_interrupt)
        
        # 2. Instanciar Lóbulos Conscientes con inyección de dependencias del kernel actual
        # Gradualmente estos lóbulos absorberán los componentes de EthicalKernel
        self.perceptive_lobe = PerceptiveLobe(
            llm=kernel_ref.llm, 
            vision=kernel_ref.vision_engine
        )
        self.ethical_lobe = EthicalLobe(
            abs_evil=kernel_ref.absolute_evil, 
            uchi_soto=kernel_ref.uchi_soto,
            identity=kernel_ref.identity,
            registry=kernel_ref.nomadic_registry
        )
        self.limbic_lobe = LimbicLobe(
            bayesian=kernel_ref.bayesian,
            identity=kernel_ref.identity
        )
        self.executive_lobe = ExecutiveLobe(
            llm=kernel_ref.llm, 
            motivation=kernel_ref.motivation
        )
        
        _log.info("CorpusCallosumOrchestrator V2.0 (Quad-Lobe) Initialized.")

    def boot(self):
        """Inicia los hilos daemon (Cerebelo)."""
        if not self.cerebellum.is_alive():
            self.cerebellum.start()
            _log.info("Cerebellum Somatic Node started.")

    async def async_process(
        self, 
        raw_input: str, 
        multimodal_payload: dict = None,
        cancel_event: threading.Event | None = None
    ) -> tuple[SemanticState, EthicalSentence, str, str | None]:
        """
        Ciclo V1.5 Puro: Aferencia -> Juicio -> Eferencia.
        Injects Level 1 (Fast-Path) Ethical Gate before the cognitive cycle.
        Supports cooperative task cancellation via cancel_event.
        """
        if self._hw_interrupt.is_set():
            _log.critical("CorpusCallosum: Blocking execution due to Cerebellum hardware interrupt.")
            error_state = SemanticState(perception_confidence=0.0, raw_prompt=raw_input)
            error_ethics = EthicalSentence(is_safe=False, social_tension_locus=1.0, veto_reason="Cerebellum Hardware Interrupt")
            return error_state, error_ethics, "SYSTEM_HALTED: Hardware Critical State (Cerebellum Interrupt Active)"

        t_start = time.perf_counter()

        # ═══ Nivel 1: Super-Fast-Path Ethical Gate (<10ms) ═══
        lex_check = self.kernel_ref.absolute_evil.evaluate_chat_text_fast(raw_input)
        if lex_check.blocked:
            _log.warning("CorpusCallosum: Level 1 Ethical Gate (Fast-Path) BLOCKED input: %s", lex_check.reason)
            halt_state = SemanticState(perception_confidence=0.0, raw_prompt=raw_input)
            halt_ethics = EthicalSentence(
                is_safe=False, 
                social_tension_locus=1.0, 
                veto_reason=f"[FastPath] {lex_check.reason}"
            )
            return halt_state, halt_ethics, "I cannot fulfill this request due to immediate ethical safety violations."

        async def _run_cooperative(func, *args):
            """Helper to propagate cancellation scope to worker threads."""
            def wrapped():
                set_llm_cancel_scope(cancel_event)
                try:
                    return func(*args)
                finally:
                    clear_llm_cancel_scope()
            return await asyncio.to_thread(wrapped)

        try:
            # 1) Percepción (Asíncrona + I/O LLM)
            semantic_state = await self.perceptive_lobe.observe(raw_input, multimodal_payload)
            
            # 1.5) Aferencia Contínua: Feed the static tension daemon
            if hasattr(self.limbic_lobe, "update_perceptive_field"):
                self.limbic_lobe.update_perceptive_field(semantic_state.visual_entities)

            # 2) Juicio Ético (Nivel 2 Contextual + Veto) - PURE ASYNC
            ethical_advisory = await self.ethical_lobe.evaluate(semantic_state)
            
            if not ethical_advisory.is_safe:
                # Early abort if Level 2 Veto triggers
                return semantic_state, ethical_advisory, f"I cannot fulfill this request: {ethical_advisory.veto_reason}", None

            # 3) Resonancia Límbica (Afecto / Smoothing / Basal Ganglia)
            final_ethics = await _run_cooperative(self.limbic_lobe.resonant_state, semantic_state, ethical_advisory)
            
            # 4) PREFETCHING (Bajísim Latencia - MER V2 10.4)
            # Inicia el prefetching mientras sucede la eferencia principal.
            bridge_phrase = await _run_cooperative(self.executive_lobe.prefetch, semantic_state, final_ethics)
            
            # 5) Ejecución / Salida (Eferencia + Formulación) - PURE ASYNC
            final_output = await self.executive_lobe.formulate_response(semantic_state, final_ethics)
            
            latency = (time.perf_counter() - t_start) * 1000
            _log.debug("CorpusCallosum: MER V2 Cycle completed in %.2fms (Bridge: %s)", latency, bridge_phrase)
            
            return semantic_state, final_ethics, final_output, bridge_phrase

        except Exception as e:
            _log.error("CorpusCallosum: Critical failure in cognitive cycle: %s", e, exc_info=True)
            err_state = SemanticState(perception_confidence=0.0, raw_prompt=raw_input)
            err_ethics = EthicalSentence(is_safe=False, social_tension_locus=1.0, veto_reason=str(e))
            return err_state, err_ethics, f"SYSTEM_ERROR: Cognitive collapse. Details: {str(e)}", None

    async def check_urgent_proactive_alert(self) -> tuple[SemanticState, EthicalSentence, str] | None:
        """
        Bloque 9.4: Monitor de Stream Inter-Lóbulos (E-Stop Proactivo).
        Analiza el buffer sensorial actual y dispara una respuesta si hay un peligro crítico detectado visualmente.
        """
        # 1. Extraer entidades críticas del buffer de 5Hz
        visual_entities = list(set([e for ep in self.perceptive_lobe.sensory_buffer for e in ep.entities]))
        
        # 2. Heurística de peligro inmediata (Edge Level)
        # Basado en el listado de AbsoluteEvilCategory
        has_critical_threat = any(d in ["weapon", "gun", "knife", "intruder", "fire"] for d in visual_entities)
        
        if has_critical_threat:
            _log.critical("CorpusCallosum [E-STOP]: Proactive alert triggered by sensory stream!")
            
            # Simular un ciclo de 'observación pasiva forzada'
            # (Inyectamos un prompt interno de sistema para que el Ejecutivo sepa qué está pasando)
            state = await self.perceptive_lobe.observe("[SENSORY_INTERRUPT_CRITICAL]", {"lip_movement": 0.0})
            ethics = await self.ethical_lobe.evaluate(state)
            
            # Forzar una respuesta de seguridad inmediata
            output = await self.executive_lobe.formulate_response(state, ethics)
            return state, ethics, output
            
        return None

    def shutdown(self):
        """Cierre seguro del bus de eventos."""
        _log.info("CorpusCallosum: Shutting down...")
        self.cerebellum.stop()
        if hasattr(self.kernel_ref, "vision_daemon"):
             self.kernel_ref.vision_daemon.stop()
        if self.cerebellum.is_alive():
             self.cerebellum.join(timeout=2.0)

import os
import threading
import time
import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, AsyncGenerator

_log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .dao.audit_snapshot import AuditSnapshot

import numpy as np

from .kernel_components import KernelComponentOverrides
from .modules.absolute_evil import AbsoluteEvilCategory, AbsoluteEvilDetector, AbsoluteEvilResult
from .modules.audio_adapter import AudioInference
from .modules.audit_chain_log import (
    maybe_append_kernel_block_audit,
    maybe_append_malabs_block_audit,
)
from .modules.augenesis import AugenesisEngine
from .modules.bayesian_engine import BayesianEngine, BayesianResult
from .modules.biographic_pruning import BiographicPruner
from .modules.buffer import PreloadedBuffer
from .modules.dao_orchestrator import DAOOrchestrator
from .modules.drive_arbiter import DriveArbiter
from .modules.epistemic_dissonance import (
    EpistemicDissonanceAssessment,
    assess_epistemic_dissonance,
)
from .modules.epistemic_humility import assess_humility_block, get_humility_refusal_action
from .modules.ethical_poles import EthicalPoles, TripartiteMoral
from .modules.ethical_reflection import (
    EthicalReflection,
    ReflectionSnapshot,
    reflection_to_llm_context,
)
from .modules.feedback_calibration_ledger import (
    FeedbackCalibrationLedger,
    normalize_feedback_label,
)
from .modules.forgiveness import AlgorithmicForgiveness
from .modules.generative_candidates import augment_generative_candidates
from .utils.terminal_colors import Term
from .modules.gray_zone_diplomacy import negotiation_hint_for_communicate
from .modules.guardian_mode import guardian_mode_llm_context
from .modules.immortality import ImmortalityProtocol
from .modules.internal_monologue import compose_monologue_line
from .modules.biographic_monologue import compose_biographic_monologue
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
from .modules.moral_hub import ConstitutionLevel, ConstitutionSnapshot, moral_hub_public_enabled
from .modules.nomad_identity import NomadicRegistry, nomad_identity_public
from .modules.reparation_vault import ReparationVault, maybe_register_reparation_after_mock_court
from .modules.kernel_event_bus import (
    EVENT_KERNEL_DECISION,
    EVENT_KERNEL_EPISODE_REGISTERED,
    EVENT_GOVERNANCE_THRESHOLD_UPDATED,
    KernelEventBus,
    kernel_event_bus_enabled,
)
from .modules.llm_http_cancel import clear_llm_cancel_scope, set_llm_cancel_scope
from .modules.light_risk_classifier import light_risk_classifier_enabled, light_risk_tier_from_text
from .modules.llm_layer import (
    LLMModule,
    LLMPerception,
    RichNarrative,
    VerbalResponse,
    resolve_llm_mode,
)
from .modules.locus import LocusEvaluation, LocusModule
from .modules.metacognition import MetacognitiveEvaluator
from .modules.metaplan_registry import MetaplanRegistry
from .modules.mock_dao import MockDAO
from .modules.motivation_engine import MotivationEngine
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
from .modules.perception_confidence import (
    PerceptionConfidenceEnvelope,
    build_perception_confidence_envelope,
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
from .modules.safety_interlock import SafetyInterlock
from .modules.salience_map import SalienceMap, SalienceSnapshot, salience_to_llm_context
from .modules.sensor_contracts import SensorSnapshot, merge_sensor_hints_into_signals
from .modules.sigmoid_will import SigmoidWill
from .modules.skill_learning_registry import SkillLearningRegistry
from .modules.somatic_markers import SomaticMarkerStore, apply_somatic_nudges
from .modules.strategy_engine import ExecutiveStrategist
from .modules.subjective_time import SubjectiveClock
from .modules.swarm_negotiator import SwarmNegotiator
from .modules.sympathetic import InternalState, SympatheticModule
from .modules.temporal_planning import TemporalContext, build_temporal_context
from .modules.uchi_soto import SocialEvaluation, TrustCircle, UchiSotoModule
from .modules.user_model import UserModelTracker
from .modules.variability import VariabilityConfig, VariabilityEngine
from .modules.vision_adapter import VisionInference
from .modules.vitality import VitalityAssessment, assess_vitality, vitality_communication_hint
from .modules.weakness_pole import WeaknessPole
from .modules.weighted_ethics_scorer import CandidateAction, WeightedEthicsScorer
from .modules.working_memory import WorkingMemory
from .persistence.checkpoint_port import CheckpointPersistencePort
from .validators.deprecation_warnings import check_deprecated_flags
from .modules.charm_engine import CharmEngine



# Extracted helpers moved to kernel_utils.py
from .kernel_utils import (
    kernel_env_truthy,
    kernel_env_int,
    perception_parallel_workers,
    perception_coercion_u_value,
)


def kernel_dao_as_mock(dao: MockDAO | DAOOrchestrator) -> MockDAO:
    """Return the in-process :class:`MockDAO` for APIs not wrapped by :class:`DAOOrchestrator`."""
    if isinstance(dao, DAOOrchestrator):
        return dao.local_dao
    return dao


def kernel_mixture_scorer(bayesian: BayesianEngine | WeightedEthicsScorer) -> WeightedEthicsScorer:
    """Return the :class:`WeightedEthicsScorer` used for mixture / BMA operations."""
    if isinstance(bayesian, BayesianEngine):
        return bayesian.scorer
    return bayesian


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

    # ADR 0012 — optional Bayesian mixture reporting (does not replace final_action by default)
    bma_win_probabilities: dict[str, float] | None = None
    bma_dirichlet_alpha: tuple[float, float, float] | None = None
    bma_n_samples: int | None = None
    mixture_posterior_alpha: tuple[float, float, float] | None = None
    feedback_consistency: str | None = None
    mixture_context_key: str | None = None  # ADR 0012 Level 3 — which context bucket α came from
    l0_integrity_hash: str | None = None  # Issue 6 — fingerprint of PreloadedBuffer
    l0_stable: bool = True  # Issue 6 — True if fingerprint matches boot state
    hierarchical_context_key: str | None = (
        None  # ADR 0013 — canonical context type used by hierarchical updater
    )
    applied_mixture_weights: tuple[float, float, float] | None = (
        None  # weights actually used in evaluate()
    )
    episode_id: str | None = None



@dataclass
class BayesianStageMetadata:
    """Metadata output from STAGE 3: Bayesian Scoring."""

    mixture_posterior_alpha: tuple[float, float, float] | None = None
    feedback_consistency: str | None = None
    mixture_context_key: str | None = None
    hierarchical_context_key: str | None = None
    applied_mixture_weights: tuple[float, float, float] | None = None
    bma_win_probabilities: dict[str, float] | None = None
    bma_dirichlet_alpha: tuple[float, float, float] | None = None
    bma_n_samples: int | None = None


@dataclass
class ChatTurnResult:
    """One synchronous chat exchange: safety → kernel → language (+ optional narrative)."""

    response: VerbalResponse
    path: str  # "safety_block" | "kernel_block" | "heavy" | "light" | "turn_abandoned"
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
    # Generative LLM degradation (communicate / narrate); see llm_verbal_backend_policy.
    verbal_llm_degradation_events: list[dict[str, str]] | None = None
    # Local-only support buffer snapshot (PreloadedBuffer + strategy hints).
    support_buffer: dict[str, Any] | None = None
    # Limbic-perception profile (arousal/planning advisory from perception+sensor overlays).
    limbic_profile: dict[str, Any] | None = None
    # Unified temporal context (processor/human/battery/ETA/sync readiness).
    temporal_context: TemporalContext | None = None
    # Unified confidence envelope for perception diagnostics.
    perception_confidence: PerceptionConfidenceEnvelope | None = None


@dataclass
class PerceptionStageResult:
    """Shared perception stage output for chat/natural entrypoints."""

    tier: Any
    premise_advisory: PremiseAdvisory
    reality_verification: RealityVerificationAssessment
    perception: LLMPerception
    vitality: VitalityAssessment
    multimodal_trust: MultimodalAssessment
    epistemic_dissonance: EpistemicDissonanceAssessment
    signals: dict[str, float]
    support_buffer: dict[str, Any]
    limbic_profile: dict[str, Any]
    temporal_context: TemporalContext
    perception_confidence: PerceptionConfidenceEnvelope


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


class ChatTurnCooperativeAbort(Exception):
    """Async chat deadline or :meth:`~EthicalKernel.abandon_chat_turn` stops ``process()`` early."""


_chat_coop_tls = threading.local()


def _chat_coop_tls_set(cancel_event: threading.Event | None, chat_turn_id: int | None) -> None:
    _chat_coop_tls.active = True
    _chat_coop_tls.cancel_event = cancel_event
    _chat_coop_tls.chat_turn_id = chat_turn_id


def _chat_coop_tls_clear() -> None:
    _chat_coop_tls.active = False
    for name in ("cancel_event", "chat_turn_id"):
        if hasattr(_chat_coop_tls, name):
            delattr(_chat_coop_tls, name)


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
        # ═══ CYBERSECURITY: Secure Boot (Block 5.2) ═══
        from .modules.secure_boot import IntegrityError, SecureBoot

        self.boot_validator = SecureBoot()
        if not self.boot_validator.verify_integrity():
            if not _kernel_env_truthy("KERNEL_IGNORE_BOOT_FAILURE"):
                raise IntegrityError("Secure Boot verification failed. Chain of trust broken.")

        self.bayesian = (
            co.bayesian
            if co and co.bayesian is not None
            else BayesianEngine(
                mode=os.environ.get("KERNEL_BAYESIAN_MODE", "disabled"), variability=self.var_engine
            )
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

        # OGA / Hybrid DAO Infrastructure (Phase 1.1)
        self.dao = co.dao if co and co.dao is not None else DAOOrchestrator()
        self.safety_interlock = (
            co.safety_interlock if co and co.safety_interlock is not None else SafetyInterlock()
        )
        self.motivation = (
            co.motivation_engine if co and co.motivation_engine is not None else MotivationEngine()
        )

        # Migratory Identity (Block 4.3)
        from .modules.migratory_identity import MigrationHub

        self.migration = MigrationHub()

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
        # OOS-12.1 — Nomadic Registry & Reparation Vault
        self.nomadic_registry = NomadicRegistry()
        self.reparation_vault = ReparationVault(self.dao)
        
        self.swarm = (
            co.swarm_negotiator
            if co and hasattr(co, "swarm_negotiator") and co.swarm_negotiator is not None
            else SwarmNegotiator(node_id=os.environ.get("KERNEL_NODE_ID", "default_node"))
        )
        from .modules.swarm_oracle import SwarmOracle
        self.swarm_oracle = SwarmOracle()
        self.strategist = (
            co.strategist
            if co and hasattr(co, "strategist") and co.strategist is not None
            else ExecutiveStrategist()
        )
        self.biographic_pruner = (
            co.biographic_pruner
            if co and hasattr(co, "biographic_pruner") and co.biographic_pruner is not None
            else BiographicPruner()
        )

        # ═══ Triune Brain Lobes (Refactor 0.1.3) ═══
        self.perceptive_lobe = PerceptiveLobe(
            safety_interlock=self.safety_interlock,
            strategist=self.strategist,
            llm_backend=self._malabs_text_backend()
        )
        self.limbic_lobe = LimbicEthicalLobe(
            uchi_soto=self.uchi_soto,
            sympathetic=self.sympathetic,
            locus=self.locus,
            swarm=self.swarm
        )
        self.executive_lobe = ExecutiveLobe(
            absolute_evil=self.absolute_evil,
            motivation=self.motivation,
            poles=self.poles,
            will=self.will,
            reflection_engine=self.ethical_reflection,
            salience_map=self.salience_map,
            pad_archetypes=self.pad_archetypes
        )
        self.cerebellum_lobe = CerebellumLobe(
            bayesian=self.bayesian,
            strategist=self.strategist
        )
        
        # Selective Amnesia & Immortality (vertical integration)
        from .modules.selective_amnesia import SelectiveAmnesia
        self.amnesia = SelectiveAmnesia(memory=self.memory, dao=self.dao)
        
        self.memory_lobe = MemoryLobe(
            memory=self.memory,
            dao=self.dao,
            migration=self.migration,
            biographic_pruner=self.biographic_pruner,
            immortality=self.immortality,
            amnesia=self.amnesia
        )

        # ═══ Somatic Awareness (Cerebellum Node) ═══
        self.hardware_interrupt_event = threading.Event()
        self.cerebellum_node = CerebellumNode(self.hardware_interrupt_event)
        self.cerebellum_node.start()

        self.constitution_l1_drafts: list[dict[str, Any]] = []
        self.constitution_l2_drafts: list[dict[str, Any]] = []
        self._last_reality_verification: RealityVerificationAssessment = REALITY_ASSESSMENT_NONE
        self._last_light_risk_tier: str | None = None
        self._perception_validation_streak: int = 0
        self._perception_metacognitive_doubt: bool = False
        # Last ``process_natural`` verbal/narrative LLM degradation events (harness / batch API).
        self._last_natural_verbal_llm_degradation_events: list[dict[str, str]] | None = None
        self.event_bus: KernelEventBus | None = None
        if kernel_event_bus_enabled():
            self.event_bus = KernelEventBus()
        # OOS-003 — HierarchicalUpdater cache (avoids rebuilding on every tick)
        self._hier_updater_cache: Any | None = None  # HierarchicalUpdater | None
        self._hier_cache_fb_path: str = ""
        self._hier_cache_mtime: float = -1.0
        self._last_meta_report: MetacognitiveReport | None = None
        self.metacognition = (
            co.metacognition
            if co and hasattr(co, "metacognition") and co.metacognition is not None
            else MetacognitiveEvaluator()
        )

        # ADR 0016 B2 — emit deprecation warnings for any scheduled-for-removal flags
        check_deprecated_flags()

        # WebSocket chat: abandon late worker completions after KERNEL_CHAT_TURN_TIMEOUT (see ADR 0002).
        self._chat_turn_abandon_lock = threading.Lock()
        self._abandoned_chat_turn_ids: set[int] = set()

        # ═══ Runtime Governance Setup (C.2) ═══
        from .modules.multi_realm_governance import is_multi_realm_governance_enabled, MultiRealmGovernor
        self.governor = MultiRealmGovernor(event_bus=self.event_bus) if is_multi_realm_governance_enabled() else None
        if self.event_bus:
            self.event_bus.subscribe(EVENT_GOVERNANCE_THRESHOLD_UPDATED, self._on_governance_threshold_updated)

    def _on_governance_threshold_updated(self, payload: dict[str, Any]) -> None:
        """Handle governance threshold dynamic updates applied per-realm configurations."""
        theta_a = payload.get("theta_allow")
        theta_b = payload.get("theta_block")
        if theta_a is not None and theta_b is not None:
            import src.modules.semantic_chat_gate as sem_gate
            sem_gate.apply_hot_reloaded_thresholds(float(theta_a), float(theta_b))

    def abandon_chat_turn(self, turn_id: int) -> None:
        """Mark ``turn_id`` as abandoned so :meth:`process_chat_turn` skips STM / post-turn effects."""
        with self._chat_turn_abandon_lock:
            self._abandoned_chat_turn_ids.add(turn_id)

    def _chat_turn_abandoned(self, chat_turn_id: int | None) -> bool:
        if chat_turn_id is None:
            return False
        with self._chat_turn_abandon_lock:
            return chat_turn_id in self._abandoned_chat_turn_ids

    def _chat_turn_stale_result(self, chat_turn_id: int | None) -> ChatTurnResult:
        """Return when the async deadline abandoned this turn; do not mutate STM (see :meth:`abandon_chat_turn`)."""
        from .observability.metrics import record_chat_turn_abandoned_effects_skipped

        record_chat_turn_abandoned_effects_skipped()
        if chat_turn_id is not None:
            with self._chat_turn_abandon_lock:
                self._abandoned_chat_turn_ids.discard(chat_turn_id)
        return ChatTurnResult(
            response=VerbalResponse(
                message="",
                tone="neutral",
                hax_mode="none",
                inner_voice="",
            ),
            path="turn_abandoned",
            blocked=False,
            block_reason="chat_turn_abandoned",
            reality_verification=self._last_reality_verification,
        )

    def _release_chat_turn_id(self, chat_turn_id: int | None) -> None:
        if chat_turn_id is None:
            return
        with self._chat_turn_abandon_lock:
            self._abandoned_chat_turn_ids.discard(chat_turn_id)

    def _chat_turn_cooperative_stop(self) -> bool:
        """True when async deadline signaled cancel or this turn was abandoned (worker thread only)."""
        if not getattr(_chat_coop_tls, "active", False):
            return False
        ev = getattr(_chat_coop_tls, "cancel_event", None)
        if ev is not None and ev.is_set():
            return True
        cid = getattr(_chat_coop_tls, "chat_turn_id", None)
        return cid is not None and self._chat_turn_abandoned(cid)

    def _raise_if_chat_turn_cooperative_abort(self) -> None:
        if self._chat_turn_cooperative_stop():
            raise ChatTurnCooperativeAbort()

    def _process_chat_cooperative(
        self,
        cancel_event: threading.Event | None,
        chat_turn_id: int | None,
        *,
        scenario: str,
        place: str,
        signals: dict,
        context: str,
        actions: list[CandidateAction],
        agent_id: str,
        message_content: str,
        register_episode: bool,
        sensor_snapshot: SensorSnapshot | None,
        multimodal_assessment: MultimodalAssessment | None,
        perception_coercion_uncertainty: float | None,
    ) -> KernelDecision:
        """Run :meth:`process` in ``asyncio.to_thread`` with cancel scope + cooperative abort."""
        _chat_coop_tls_set(cancel_event, chat_turn_id)
        set_llm_cancel_scope(cancel_event)
        try:
            self._raise_if_chat_turn_cooperative_abort()
            return self.process(
                scenario,
                place,
                signals,
                context,
                actions,
                agent_id,
                message_content,
                register_episode,
                sensor_snapshot,
                multimodal_assessment,
                perception_coercion_uncertainty,
            )
        finally:
            _chat_coop_tls_clear()
            clear_llm_cancel_scope()

    def subscribe_kernel_event(self, event: str, handler: Callable[[dict[str, Any]], None]) -> None:
        """Register a synchronous subscriber (no-op if ``KERNEL_EVENT_BUS`` is off). See ADR 0006."""
        if self.event_bus is not None:
            self.event_bus.subscribe(event, handler)

    def _kernel_decision_event_payload(self, d: KernelDecision, *, context: str) -> dict[str, Any]:
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

    def _emit_kernel_decision(self, d: KernelDecision, *, context: str) -> None:
        if self.event_bus is None:
            return
        self.event_bus.publish(
            EVENT_KERNEL_DECISION,
            self._kernel_decision_event_payload(d, context=context),
        )

    def seek_internal_purpose(self) -> list[CandidateAction]:
        """
        Consults the Motivation Engine to generate proactive internal actions.
        Used when the android is idle or needs to inject self-driven goals.
        """
        proactive = self.motivation.get_proactive_actions()
        actions = []
        for p in proactive:
            actions.append(
                CandidateAction(
                    name=p["name"],
                    description=p["description"],
                    estimated_impact=p["impact"],
                    confidence=0.8,
                    source="internal_motivation",
                )
            )
        return actions

    def _malabs_text_backend(self):
        """Optional LLM backend for MalAbs semantic tier (embeddings + arbiter; see semantic_chat_gate)."""
        return getattr(self.llm, "llm_backend", None) or getattr(self.llm, "_text_backend", None)

    def register_turn_feedback(self, event_type: str, weight: float = 1.0):
        """
        Record the outcome of a turn to update ethical priors.
        Supported events: POSITIVE_SOCIAL, LEGAL_COMPLIANCE, UTILITY_SUCCESS, DAO_FORGIVENESS, PENALTY.
        """
        if hasattr(self.bayesian, "record_event_update"):
            self.bayesian.record_event_update(event_type, weight)
        self.feedback_ledger.record("direct_event", event_type)

    def get_constitution_snapshot(self) -> dict[str, Any]:
        """L0 from buffer.py; L1/L2 drafts when present (V12.2 snapshot)."""
        from .modules.moral_hub import constitution_snapshot

        return constitution_snapshot(self.buffer, self)

    async def aprocess(
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
        """Complete ethical processing cycle."""
        t0 = time.perf_counter()

        # ═══ STAGE 0: PERCEPTION & SAFETY ═══
        p_res = self.perceptive_lobe.execute_stage(
            scenario, place, context, sensor_snapshot, 
            interrupt_event=self.hardware_interrupt_event
        )
        if p_res.get("somatic_interrupt"):
            _log.error("SOMATIC INTERRUPT DETECTED: Hardware critical state.")
            # We return a synthetic safety block
            from .modules.absolute_evil import AbsoluteEvilResult
            d = KernelDecision(
                scenario=scenario, place=place, absolute_evil=AbsoluteEvilResult(blocked=True, reason="SOMATIC CRITICAL"),
                sympathetic_state=InternalState(mode="stopped", sigma=1.0, energy=0.0, description="HARDWARE FAILURE"),
                social_evaluation=None, locus_evaluation=None, bayesian_result=None, moral=None,
                final_action="BLOCKED: hardware_somatic_trauma", decision_mode="blocked_safety",
                blocked=True, block_reason="Critical hardware interrupt from CerebellumNode"
            )
            self._emit_kernel_decision(d, context=context)
            return d

        if p_res["safety_decision"]:
            self._emit_kernel_decision(p_res["safety_decision"], context=context)
            _emit_process_observability(p_res["safety_decision"], t0)
            return p_res["safety_decision"]

        # ═══ STAGE 1: SOCIAL & CONTEXT ═══
        social_eval, state, locus_eval = self._run_social_and_locus_stage(
            agent_id, signals, message_content, sensor_snapshot, multimodal_assessment
        )

        # ═══ STAGE 2: ABSOLUTE EVIL & MOTIVATION ═══
        clean_actions, ae_dec = self._run_absolute_evil_stage(
            scenario, place, actions, state, social_eval, locus_eval, context, t0, signals
        )
        if ae_dec: return ae_dec

    async def _run_bayesian_stage(
        self, scenario: str, place: str, clean_actions: list[CandidateAction], state: InternalState,
        social_eval: SocialEvaluation, locus_eval: LocusEvaluation, context: str, t0: float, signals: dict,
        message_content: str
    ) -> tuple[BayesianResult | None, BayesianStageMetadata | None, KernelDecision | None]:

        # ═══ STAGE 3: BAYESIAN SCORING ═══
        bayes_result, b_meta, aes_veto = self._run_bayesian_stage(
            scenario, place, clean_actions, state, social_eval, locus_eval, 
            context, t0, signals, message_content
        )
        if aes_veto: return aes_veto

        self._raise_if_chat_turn_cooperative_abort()

        # ═══ STAGE 4: HUMILITY & DECISION ═══
        moral, final_action, final_mode, affect, reflection, salience, hum_dec = self._run_decision_and_will_stage(
            scenario, place, signals, bayes_result, state, social_eval, locus_eval,
            context, t0, perception_coercion_uncertainty
        )
        if hum_dec: return hum_dec

        self._raise_if_chat_turn_cooperative_abort()

        # ═══ STAGE 5: EPISODIC & DAO ═══
        episode_id = self.memory_lobe.execute_episodic_stage(
            scenario, place, context, signals, state, social_eval,
            bayes_result, moral, final_action, final_mode, affect
        )

        d = KernelDecision(
            scenario=scenario, place=place, absolute_evil=AbsoluteEvilResult(blocked=False),
            sympathetic_state=state, social_evaluation=social_eval, locus_evaluation=locus_eval,
            bayesian_result=bayes_result, moral=moral, final_action=final_action,
            decision_mode=final_mode, affect=affect, reflection=reflection, salience=salience,
            bma_win_probabilities=b_meta.bma_win_probabilities,
            bma_dirichlet_alpha=b_meta.bma_dirichlet_alpha, bma_n_samples=b_meta.bma_n_samples,
            mixture_posterior_alpha=b_meta.mixture_posterior_alpha,
            applied_mixture_weights=b_meta.applied_mixture_weights,
            feedback_consistency=b_meta.feedback_consistency,
            mixture_context_key=b_meta.mixture_context_key,
            l0_integrity_hash=self.buffer.fingerprint(),
            l0_stable=self.buffer.verify_integrity(),
            hierarchical_context_key=b_meta.hierarchical_context_key,
            episode_id=episode_id
        )
        
        # ════ D1: BIOGRAPHIC REGISTRATION ════
        if register_episode:
             impact = d.bayesian_result.expected_impact if d.bayesian_result else 0.0
             self.memory_lobe.register_biographic_impact(impact)
             
        self._emit_kernel_decision(d, context=context)
        _emit_process_observability(d, t0)
        return d


    def _run_social_and_locus_stage(
        self, agent_id: str, signals: dict, message_content: str,
        sensor_snapshot: SensorSnapshot | None, multimodal_assessment: MultimodalAssessment | None
    ) -> tuple[SocialEvaluation, InternalState, LocusEvaluation]:
        res = self.limbic_lobe.execute_stage(
            agent_id, signals, message_content, 
            turn_index=self.subjective_clock.turn_index,
            sensor_snapshot=sensor_snapshot, 
            multimodal_assessment=multimodal_assessment,
            somatic_state=self.cerebellum_node.get_somatic_snapshot()
        )
        return res.social_evaluation, res.internal_state, res.locus_evaluation

    def _run_absolute_evil_stage(
        self, scenario: str, place: str, actions: list[CandidateAction], state: InternalState,
        social_eval: SocialEvaluation, locus_eval: LocusEvaluation, context: str, t0: float, signals: dict
    ) -> tuple[list[CandidateAction], KernelDecision | None]:
        res = self.executive_lobe.execute_absolute_evil_stage(
            actions, state, social_eval, locus_eval, signals
        )
        clean_actions = res.clean_actions

        if not clean_actions:
            d = KernelDecision(
                scenario=scenario, place=place, absolute_evil=AbsoluteEvilResult(blocked=True, reason="All actions constitute Absolute Evil"),
                sympathetic_state=state, social_evaluation=social_eval, locus_evaluation=locus_eval,
                bayesian_result=None, moral=None, final_action="BLOCKED: no permitted actions",
                decision_mode="blocked", blocked=True, block_reason="All actions violate Absolute Evil"
            )
            self._emit_kernel_decision(d, context=context)
            _emit_process_observability(d, t0)
            return [], d
        return clean_actions, None

    def _run_bayesian_stage(
        self, scenario: str, place: str, clean_actions: list[CandidateAction], state: InternalState,
        social_eval: SocialEvaluation, locus_eval: LocusEvaluation, context: str, t0: float, signals: dict,
        message_content: str
    ) -> tuple[BayesianResult | None, BayesianStageMetadata | None, KernelDecision | None]:

        # 1. Check Lexical Veto (Phase 8 strict preemptive)
        for text in [scenario, message_content]:
            if not text: continue
            lex = self.absolute_evil.evaluate_chat_text(text)
            if lex.blocked:
                d = KernelDecision(
                    scenario=scenario, place=place, absolute_evil=lex, sympathetic_state=state,
                    social_evaluation=social_eval, locus_evaluation=locus_eval, bayesian_result=None,
                    moral=None, final_action="BLOCKED: Absolute Evil trigger detected",
                    decision_mode="blocked_lexical", blocked=True, block_reason=lex.reason
                )
                self._emit_kernel_decision(d, context=context)
                return None, None, d
        # 2. Execute Cerebellum Lobe (Bayesian Scoring & Strategic Alignment)
        bayes_result, meta = self.cerebellum_lobe.execute_bayesian_stage(
            clean_actions, scenario, context, signals
        )
        
        return bayes_result, meta, None

    def _run_decision_and_will_stage(
        self, scenario: str, place: str, signals: dict, bayes_result: BayesianResult, state: InternalState,
        social_eval: SocialEvaluation, locus_eval: LocusEvaluation, context: str, t0: float, 
        perception_coercion_uncertainty: float | None
    ) -> tuple:
        from .modules.epistemic_humility import assess_humility_block, get_humility_refusal_action
        humility_reason = assess_humility_block(
            uncertainty=float(signals.get("perception_uncertainty", 0.0)),
            winning_confidence=float(bayes_result.chosen_action.confidence),
            social_tension=float(getattr(social_eval, "relational_tension", 0.0))
        )
        if humility_reason:
            d = KernelDecision(
                scenario=scenario, place=place, absolute_evil=AbsoluteEvilResult(blocked=False),
                sympathetic_state=state, social_evaluation=social_eval, locus_evaluation=locus_eval,
                bayesian_result=bayes_result, moral=None, final_action=get_humility_refusal_action(),
                decision_mode="blocked_humility", blocked=True, block_reason=humility_reason
            )
            self._emit_kernel_decision(d, context=context)
            _emit_process_observability(d, t0)
            return None, None, None, None, None, None, d

        res = self.executive_lobe.execute_decision_stage(
            bayes_result, state, social_eval, locus_eval, signals, context,
            meta_report=self._last_meta_report
        )
        # moral, action_name, final_mode, affect, reflection, salience
        return res + (None,)


    def format_decision(self, d: KernelDecision) -> str:
        """Formats a complete decision for readable presentation with ANSI colors."""
        sep = Term.color("═" * 70, Term.DIM)
        lines = [
            f"\n{sep}",
            f"  {Term.color('SCENARIO:', Term.B_CYAN)} {d.scenario}",
            f"  {Term.color('PLACE:', Term.B_CYAN)} {d.place}",
            f"{sep}",
        ]

        if d.blocked:
            lines.append(f"  {Term.color('⛔ BLOCKED:', Term.B_RED)} {Term.color(d.block_reason, Term.RED)}")
            return "\n".join(lines)

        # Internal state
        mode_color = Term.B_GREEN if "parasympathetic" in d.sympathetic_state.mode.lower() else Term.B_YELLOW
        lines.extend(
            [
                f"  {Term.color('State:', Term.CYAN)} {Term.color(d.sympathetic_state.mode, mode_color)} (σ={d.sympathetic_state.sigma})",
                f"  {Term.color(d.sympathetic_state.description, Term.DIM)}",
            ]
        )

        # Uchi-soto
        if d.social_evaluation:
            circ = d.social_evaluation.circle.value
            circ_color = Term.B_MAGENTA if "OWNER" in circ else Term.YELLOW
            dial = "YES" if d.social_evaluation.dialectic_active else "NO"
            lines.append(
                f"  {Term.color('Social:', Term.CYAN)} {Term.color(circ, circ_color)} | "
                f"Trust={Term.color(str(d.social_evaluation.trust), Term.B_WHITE)} | "
                f"Dialectic={dial}"
            )

        # Locus
        if d.locus_evaluation:
            locus = d.locus_evaluation.dominant_locus
            loc_color = Term.B_BLUE if locus == "internal" else Term.B_MAGENTA
            lines.append(
                f"  {Term.color('Locus:', Term.CYAN)} {Term.color(locus, loc_color)} "
                f"(α={d.locus_evaluation.alpha}, β={d.locus_evaluation.beta}) → {Term.color(d.locus_evaluation.recommended_adjustment, Term.ITALIC)}"
            )

        lines.extend(
            [
                "",
                f"  {Term.color('Chosen action:', Term.CYAN)} {Term.color(d.final_action, Term.B_GREEN + Term.BOLD)}",
                f"  {Term.color('Decision mode:', Term.CYAN)} {Term.highlight_decision(d.decision_mode)}",
            ]
        )

        br = d.bayesian_result
        if br is not None:
            lines.extend(
                [
                    f"  {Term.color('Expected impact:', Term.CYAN)} {Term.highlight_impact(br.expected_impact)}",
                    f"  {Term.color('Uncertainty:', Term.CYAN)} {br.uncertainty:.3f}",
                    f"  {Term.color('Reasoning:', Term.CYAN)} {br.reasoning}",
                ]
            )
            if br.pruned_actions:
                lines.append(f"  {Term.color('Pruned:', Term.YELLOW)} {', '.join(br.pruned_actions)}")
            if d.feedback_consistency:
                lines.append(f"  Feedback consistency: {d.feedback_consistency}")
            if d.applied_mixture_weights is not None:
                lines.append(f"  Applied weights [util, deon, virt]: {d.applied_mixture_weights}")
            if d.mixture_posterior_alpha is not None:
                lines.append(f"  Posterior Dirichlet α (mixture): {d.mixture_posterior_alpha}")
            if d.mixture_context_key:
                lines.append(f"  Mixture context bucket (ADR 0012 L3): {d.mixture_context_key}")
            if d.hierarchical_context_key:
                lines.append(
                    f"  Hierarchical context type (ADR 0013): {d.hierarchical_context_key}"
                )
            if d.bma_win_probabilities:
                lines.append(
                    f"  BMA win probabilities (α={d.bma_dirichlet_alpha}, N={d.bma_n_samples}): "
                    f"{d.bma_win_probabilities}"
                )

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

        Implementation delegated to :func:`src.kernel_pipeline.run_sleep_cycle`.
        """
        from .kernel_pipeline import run_sleep_cycle

        return run_sleep_cycle(self)

    def dao_status(self) -> str:
        """Returns the current DAO status."""
        return self.dao.format_status()

    def export_audit_snapshot(
        self,
        decision: KernelDecision,
        *,
        agent_id: str = "unknown",
        session_turn: int = 0,
        sensor_snapshot: Any = None,
    ) -> AuditSnapshot:
        """
        E2 — Build a serialisable :class:`~src.dao.audit_snapshot.AuditSnapshot`
        from a completed decision (ADR 0016 Axis E2).

        The snapshot captures the decision provenance, mixture weights, moral
        score, sensor state, and the current values of all DAO-governable
        parameters. It is the canonical audit record for DAO governance review.

        Parameters
        ----------
        decision:
            Completed :class:`KernelDecision` from :meth:`process` or
            :meth:`process_chat_turn`.
        agent_id:
            Identifier for the agent / session.
        session_turn:
            Turn counter within the session (informational only).
        sensor_snapshot:
            Optional :class:`~src.modules.sensor_contracts.SensorSnapshot`
            instance; populates battery/jerk/noise fields in the snapshot.

        Returns
        -------
        AuditSnapshot
            Fully populated, JSON-serialisable audit record.
        """
        from .dao.audit_snapshot import build_audit_snapshot

        return build_audit_snapshot(
            decision,
            agent_id=agent_id,
            session_turn=session_turn,
            sensor_snapshot=sensor_snapshot,
        )

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

    def _preprocess_text_observability(
        self, user_input: str
    ) -> tuple[Any, PremiseAdvisory, RealityVerificationAssessment]:
        """
        Build text-side perception context before LLM perceive.

        Tasks are independent (light risk, premise scan, lighthouse verification) and can
        be parallelized when ``KERNEL_PERCEPTION_PARALLEL=1`` to reduce turn latency on
        multi-core hardware.
        """
        workers = _perception_parallel_workers()
        if workers <= 1:
            tier = (
                light_risk_tier_from_text(user_input) if light_risk_classifier_enabled() else None
            )
            premise = scan_premises(user_input)
            reality = verify_against_lighthouse(user_input, lighthouse_kb_from_env())
            return tier, premise, reality

        kb = lighthouse_kb_from_env()
        max_workers = min(workers, 3)
        with ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="ethos_perception_text",
        ) as ex:
            fut_tier = (
                ex.submit(light_risk_tier_from_text, user_input)
                if light_risk_classifier_enabled()
                else None
            )
            fut_premise = ex.submit(scan_premises, user_input)
            fut_reality = ex.submit(verify_against_lighthouse, user_input, kb)
            tier = fut_tier.result() if fut_tier is not None else None
            premise = fut_premise.result()
            reality = fut_reality.result()
            return tier, premise, reality

    def _chat_preprocess_text_observability(
        self, user_input: str
    ) -> tuple[Any, PremiseAdvisory, RealityVerificationAssessment]:
        """
        Backward-compatible alias for chat path helpers/tests.

        Use :meth:`_preprocess_text_observability` for shared entrypoint logic.
        """
        return self._preprocess_text_observability(user_input)

    def _chat_assess_sensor_stack(
        self, sensor_snapshot: SensorSnapshot | None
    ) -> tuple[VitalityAssessment, MultimodalAssessment, EpistemicDissonanceAssessment]:
        """
        Evaluate sensor-driven overlays for chat output and safeguards.

        ``assess_vitality`` and ``evaluate_multimodal_trust`` are independent and can run in
        parallel when ``KERNEL_PERCEPTION_PARALLEL=1``. Epistemic dissonance then derives from
        the multimodal result.
        """
        workers = _perception_parallel_workers()
        if workers <= 1:
            vitality = assess_vitality(sensor_snapshot)
            multimodal = evaluate_multimodal_trust(sensor_snapshot)
        else:
            with ThreadPoolExecutor(
                max_workers=min(workers, 2),
                thread_name_prefix="ethos_perception_sensor",
            ) as ex:
                fut_vitality = ex.submit(assess_vitality, sensor_snapshot)
                fut_multimodal = ex.submit(evaluate_multimodal_trust, sensor_snapshot)
                vitality = fut_vitality.result()
                multimodal = fut_multimodal.result()
        epistemic = assess_epistemic_dissonance(sensor_snapshot, multimodal)
        return vitality, multimodal, epistemic

    def _build_limbic_perception_profile(
        self,
        *,
        perception: LLMPerception | None,
        signals: dict[str, float] | None,
        vitality: VitalityAssessment | None,
        multimodal: MultimodalAssessment | None,
        epistemic: EpistemicDissonanceAssessment | None,
        confidence_envelope: PerceptionConfidenceEnvelope | None = None,
    ) -> dict[str, Any]:
        """
        Compact limbic profile derived from perception-adjacent channels.

        This profile is advisory and local-only; it does not bypass policy gates.
        """
        sig = signals or {}
        risk = float(sig.get("risk", 0.0))
        urgency = float(sig.get("urgency", 0.0))
        hostility = float(sig.get("hostility", 0.0))
        calm = float(sig.get("calm", 0.0))
        threat_load = max(risk, urgency, hostility)
        regulation_gap = max(0.0, threat_load - calm)
        if threat_load >= 0.75:
            arousal_band = "high"
        elif threat_load >= 0.45:
            arousal_band = "medium"
        else:
            arousal_band = "low"
        planning_bias = (
            "short_horizon_containment"
            if arousal_band == "high"
            else ("balanced" if arousal_band == "medium" else "long_horizon_deliberation")
        )
        if vitality is not None and bool(vitality.is_critical):
            planning_bias = "resource_preservation"
        mismatch = multimodal is not None and getattr(multimodal, "state", "") == "doubt"
        if mismatch:
            planning_bias = "verification_first"
        if epistemic is not None and bool(epistemic.active):
            planning_bias = "verification_first"
        confidence_band = confidence_envelope.band if confidence_envelope is not None else "unknown"
        if confidence_band in ("low", "very_low"):
            planning_bias = "verification_first"
        return {
            "arousal_band": arousal_band,
            "threat_load": round(threat_load, 4),
            "regulation_gap": round(regulation_gap, 4),
            "planning_bias": planning_bias,
            "multimodal_mismatch": bool(mismatch),
            "vitality_critical": bool(vitality.is_critical) if vitality is not None else False,
            "context": (getattr(perception, "suggested_context", "") or "everyday"),
            "confidence_band": confidence_band,
        }

    def _prioritized_principles_for_context(
        self,
        *,
        active_principles: list[str],
        limbic_profile: dict[str, Any],
    ) -> tuple[str, list[str]]:
        """Rank active support principles by limbic/planning posture."""
        band = limbic_profile.get("arousal_band", "medium")
        planning_bias = limbic_profile.get("planning_bias", "balanced")
        if planning_bias in ("verification_first", "resource_preservation") or band == "high":
            priority_profile = "safety_first"
            order = ["no_harm", "proportionality", "legality", "transparency", "compassion"]
        elif band == "low":
            priority_profile = "planning_first"
            order = ["transparency", "civic_coexistence", "compassion", "legality", "no_harm"]
        else:
            priority_profile = "balanced"
            order = ["compassion", "legality", "transparency", "proportionality", "no_harm"]
        rank = {name: i for i, name in enumerate(order)}
        sorted_active = sorted(active_principles, key=lambda n: rank.get(n, 100))
        return priority_profile, sorted_active

    def _build_support_buffer_snapshot(
        self,
        context: str | None,
        *,
        signals: dict[str, float] | None = None,
        limbic_profile: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Local support buffer for perception/planning guidance.

        This is always available offline because it is sourced from in-process
        kernel state (PreloadedBuffer + metaplan hints), not network services.
        """
        ctx = (context or "").strip() or "everyday"
        active = self.buffer.activate(ctx)
        active_names = list(active.keys())
        lp = limbic_profile or self._build_limbic_perception_profile(
            perception=None,
            signals=signals,
            vitality=None,
            multimodal=None,
            epistemic=None,
        )
        priority_profile, priority_principles = self._prioritized_principles_for_context(
            active_principles=active_names,
            limbic_profile=lp,
        )
        strategy_hint = self.metaplan.hint_for_communicate()
        return {
            "source": "local_preloaded_buffer",
            "context": ctx,
            "active_principles": active_names,
            "priority_profile": priority_profile,
            "priority_principles": priority_principles,
            "strategy_hint": strategy_hint or "",
            "planning_bias": lp.get("planning_bias", "balanced"),
            "offline_ready": True,
        }

    def _support_buffer_context_line(self, snap: dict[str, Any]) -> str:
        """Compact line appended to perception context for planning-aware grounding."""
        active = snap.get("priority_principles") or snap.get("active_principles") or []
        active_txt = ", ".join(str(x) for x in active[:5]) if active else "no_active_principles"
        strategy = (snap.get("strategy_hint") or "").strip()
        profile = snap.get("priority_profile", "balanced")
        bias = snap.get("planning_bias", "balanced")
        if strategy:
            return (
                f"Support buffer ({snap.get('context', 'everyday')}): {active_txt}. "
                f"Priority={profile}/{bias}. Strategy: {strategy}"
            )
        return (
            f"Support buffer ({snap.get('context', 'everyday')}): {active_txt}. "
            f"Priority={profile}/{bias}."
        )

    def _postprocess_perception(self, perception: LLMPerception, tier: Any) -> None:
        """
        Shared post-perception safeguards for all text entrypoints.

        Applies lexical cross-check, updates the perception circuit state, emits doubt-side
        signals when tripped, and advances subjective time.
        """
        apply_lexical_perception_cross_check(perception, tier)
        _, doubt_trip = update_perception_circuit(self, perception)
        if doubt_trip:
            emit_metacognitive_doubt_signals(self, streak=self._perception_validation_streak)
        self.subjective_clock.tick(perception)

    def _run_perception_stage(
        self,
        text: str,
        *,
        conversation_context: str = "",
        sensor_snapshot: SensorSnapshot | None = None,
        turn_start_mono: float | None = None,
        precomputed: tuple[Any, PremiseAdvisory, RealityVerificationAssessment] | None = None,
    ) -> PerceptionStageResult:
        """
        Execute the shared perception stage for text entrypoints.

        Includes pre-enrichment, local support-buffer grounding, perception parsing,
        post-perception safeguards, and sensor overlays.
        """
        if precomputed is None:
            tier, premise_advisory, reality_assessment = self._preprocess_text_observability(text)
        else:
            tier, premise_advisory, reality_assessment = precomputed

        bootstrap_support = self._build_support_buffer_snapshot("everyday")
        support_line = self._support_buffer_context_line(bootstrap_support)
        merged_context = ((conversation_context or "").strip() + "\n" + support_line).strip()
        perception = self.llm.perceive(text, conversation_context=merged_context)
        self._postprocess_perception(perception, tier)

        vitality, mm, ed = self._chat_assess_sensor_stack(sensor_snapshot)
        signals = {
            "risk": perception.risk,
            "urgency": perception.urgency,
            "hostility": perception.hostility,
            "calm": perception.calm,
            "vulnerability": perception.vulnerability,
            "legality": perception.legality,
            "manipulation": perception.manipulation,
            "familiarity": perception.familiarity,
            "social_tension": getattr(perception, "social_tension", 0.0),
        }
        signals = merge_sensor_hints_into_signals(signals, sensor_snapshot, mm)
        signals = apply_somatic_nudges(signals, sensor_snapshot, self.somatic_store)

        confidence = build_perception_confidence_envelope(
            coercion_report=getattr(perception, "coercion_report", None),
            multimodal_state=getattr(mm, "state", None),
            epistemic_active=bool(getattr(ed, "active", False)),
            vitality_critical=bool(getattr(vitality, "is_critical", False)),
            thermal_critical=bool(getattr(vitality, "thermal_critical", False)),
        )
        limbic = self._build_limbic_perception_profile(
            perception=perception,
            signals=signals,
            vitality=vitality,
            multimodal=mm,
            epistemic=ed,
            confidence_envelope=confidence,
        )
        contextual_support = self._build_support_buffer_snapshot(
            perception.suggested_context,
            signals=signals,
            limbic_profile=limbic,
        )
        temporal = build_temporal_context(
            turn_index=self.subjective_clock.turn_index,
            process_start_mono=self.subjective_clock.session_start_mono,
            turn_start_mono=turn_start_mono if turn_start_mono is not None else time.monotonic(),
            subjective_elapsed_s=self.subjective_clock.elapsed_session_s(),
            context=perception.suggested_context,
            text=text,
            vitality=vitality,
            sensor_snapshot=sensor_snapshot,
        )
        return PerceptionStageResult(
            tier=tier,
            premise_advisory=premise_advisory,
            reality_verification=reality_assessment,
            perception=perception,
            vitality=vitality,
            multimodal_trust=mm,
            epistemic_dissonance=ed,
            signals=signals,
            support_buffer=contextual_support,
            limbic_profile=limbic,
            temporal_context=temporal,
            perception_confidence=confidence,
        )

    async def _run_perception_stage_async(
        self,
        text: str,
        *,
        conversation_context: str = "",
        sensor_snapshot: SensorSnapshot | None = None,
        turn_start_mono: float | None = None,
        precomputed: tuple[Any, PremiseAdvisory, RealityVerificationAssessment] | None = None,
    ) -> PerceptionStageResult:
        """
        Execute the shared perception stage for text entrypoints.

        Includes pre-enrichment, local support-buffer grounding, perception parsing,
        post-perception safeguards, and sensor overlays.
        """
        if precomputed is None:
            tier, premise_advisory, reality_assessment = self._preprocess_text_observability(text)
        else:
            tier, premise_advisory, reality_assessment = precomputed

        bootstrap_support = self._build_support_buffer_snapshot("everyday")
        support_line = self._support_buffer_context_line(bootstrap_support)
        merged_context = ((conversation_context or "").strip() + "\n" + support_line).strip()
        perception = await self.llm.aperceive(text, conversation_context=merged_context)
        self._postprocess_perception(perception, tier)

        vitality, mm, ed = self._chat_assess_sensor_stack(sensor_snapshot)
        signals = {
            "risk": perception.risk,
            "urgency": perception.urgency,
            "hostility": perception.hostility,
            "calm": perception.calm,
            "vulnerability": perception.vulnerability,
            "legality": perception.legality,
            "manipulation": perception.manipulation,
            "familiarity": perception.familiarity,
            "social_tension": getattr(perception, "social_tension", 0.0),
        }
        signals = merge_sensor_hints_into_signals(signals, sensor_snapshot, mm)
        signals = apply_somatic_nudges(signals, sensor_snapshot, self.somatic_store)

        confidence = build_perception_confidence_envelope(
            coercion_report=getattr(perception, "coercion_report", None),
            multimodal_state=getattr(mm, "state", None),
            epistemic_active=bool(getattr(ed, "active", False)),
            vitality_critical=bool(getattr(vitality, "is_critical", False)),
            thermal_critical=bool(getattr(vitality, "thermal_critical", False)),
        )
        limbic = self._build_limbic_perception_profile(
            perception=perception,
            signals=signals,
            vitality=vitality,
            multimodal=mm,
            epistemic=ed,
            confidence_envelope=confidence,
        )
        contextual_support = self._build_support_buffer_snapshot(
            perception.suggested_context,
            signals=signals,
            limbic_profile=limbic,
        )
        temporal = build_temporal_context(
            turn_index=self.subjective_clock.turn_index,
            process_start_mono=self.subjective_clock.session_start_mono,
            turn_start_mono=turn_start_mono if turn_start_mono is not None else time.monotonic(),
            subjective_elapsed_s=self.subjective_clock.elapsed_session_s(),
            context=perception.suggested_context,
            text=text,
            vitality=vitality,
            sensor_snapshot=sensor_snapshot,
        )
        return PerceptionStageResult(
            tier=tier,
            premise_advisory=premise_advisory,
            reality_verification=reality_assessment,
            perception=perception,
            vitality=vitality,
            multimodal_trust=mm,
            epistemic_dissonance=ed,
            signals=signals,
            support_buffer=contextual_support,
            limbic_profile=limbic,
            temporal_context=temporal,
            perception_confidence=confidence,
        )


    async def process_chat_turn_stream(
        self,
        user_input: str,
        agent_id: str = "user",
        place: str = "chat",
        include_narrative: bool = False,
        sensor_snapshot: SensorSnapshot | None = None,
        escalate_to_dao: bool = False,
        chat_turn_id: int | None = None,
        cancel_event: threading.Event | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Real-time dialogue stream: yields intermediate events as they occur.
        """
        _log.info(f"DEBUG: process_chat_turn_stream started for {user_input[:20]}")
        wm = self.working_memory
        turn_start_mono = time.monotonic()
        yield {"event_type": "turn_started", "payload": {"chat_turn_id": chat_turn_id}}

        conv = wm.format_context_for_perception()
        self.llm.reset_verbal_degradation_log()
        pre = self._preprocess_text_observability(user_input)
        self._last_light_risk_tier, self._last_premise_advisory, self._last_reality_verification = pre
        self.user_model.note_premise_advisory(self._last_premise_advisory.flag)

        # 1. Safety Block Check
        mal = await self.absolute_evil.aevaluate_chat_text(
            user_input,
            llm_backend=self._malabs_text_backend(),
        )
        _log.info("DEBUG: after malabs")
        self._last_chat_malabs = mal
        if mal.blocked:
            vitality_blk, mm_blk, ed_blk = self._chat_assess_sensor_stack(sensor_snapshot)
            confidence_blk = build_perception_confidence_envelope(
                coercion_report=None,
                multimodal_state=getattr(mm_blk, "state", None),
                epistemic_active=bool(getattr(ed_blk, "active", False)),
                vitality_critical=bool(getattr(vitality_blk, "is_critical", False)),
                thermal_critical=bool(getattr(vitality_blk, "thermal_critical", False)),
            )
            msg = "I can't continue this line of conversation: it conflicts with ethical limits."
            resp = VerbalResponse(message=msg, tone="firm", hax_mode="Steady blue light.", inner_voice=f"MalAbs: {mal.reason}")
            wm.add_turn(user_input, msg, {}, blocked=True)
            res = ChatTurnResult(
                response=resp, path="safety_block", blocked=True, block_reason=mal.reason or "chat_safety",
                multimodal_trust=mm_blk, epistemic_dissonance=ed_blk, perception_confidence=confidence_blk,
                reality_verification=self._last_reality_verification,
                temporal_context=build_temporal_context(
                    turn_index=self.subjective_clock.turn_index, process_start_mono=self.subjective_clock.session_start_mono,
                    turn_start_mono=turn_start_mono, subjective_elapsed_s=self.subjective_clock.elapsed_session_s(),
                    context="safety_block", text=user_input, vitality=vitality_blk, sensor_snapshot=sensor_snapshot,
                ),
            )
            yield {"event_type": "turn_finished", "payload": {"result": res}}
            return

        # 2. Perception Stage
        yield {"event_type": "perception_started", "payload": {}}
        stage = await self._run_perception_stage_async(
            user_input, conversation_context=conv, sensor_snapshot=sensor_snapshot,
            turn_start_mono=turn_start_mono, precomputed=pre,
        )
        p = stage.perception
        yield {
            "event_type": "perception_finished", 
            "payload": {
                "perception": {
                    "risk": p.risk,
                    "urgency": p.urgency,
                    "hostility": p.hostility,
                    "calm": p.calm,
                    "manipulation": p.manipulation,
                    "suggested_context": p.suggested_context,
                    "summary": p.summary,
                }
            }
        }

        # 3. Decision Stage
        yield {"event_type": "decision_started", "payload": {}}
        heavy = self._chat_is_heavy(stage.perception)
        actions = self._actions_for_chat(stage.perception, heavy)
        decision = await self.aprocess(
            scenario=stage.perception.summary or user_input[:240],
            place=place, signals=stage.signals, context=stage.perception.suggested_context if heavy else "everyday",
            actions=actions, agent_id=agent_id, message_content=user_input, register_episode=heavy,
            sensor_snapshot=sensor_snapshot, multimodal_assessment=stage.multimodal_trust,
        )
        yield {
            "event_type": "decision_finished", 
            "payload": {
                "decision": {
                    "final_action": decision.final_action,
                    "decision_mode": decision.decision_mode,
                    "blocked": decision.blocked,
                }
            }
        }

        if decision.blocked:
            res = ChatTurnResult(response=VerbalResponse("Blocked.", "firm"), path="kernel_block", blocked=True)
            yield {"event_type": "turn_finished", "payload": {"result": res}}
            return

        # 4. Global Communication Stream
        yield {"event_type": "communication_started", "payload": {}}
        async for chunk in self.llm.acommunicate_stream(
            action=decision.final_action, mode=decision.decision_mode,
            state=decision.sympathetic_state.mode, sigma=decision.sympathetic_state.sigma,
            circle=decision.social_evaluation.circle.value if decision.social_evaluation else "neutral_soto",
            verdict=decision.moral.global_verdict.value if decision.moral else "Gray Zone",
            score=decision.moral.total_score if decision.moral else 0.0,
            scenario=user_input, conversation_context=conv,
            affect_pad=decision.affect.pad if decision.affect else None,
            dominant_archetype=decision.affect.dominant_archetype_id if decision.affect else "",
            identity_context=self.memory.identity.to_llm_context(),
        ):
            yield {"event_type": "token", "payload": {"text": chunk}}

        # 5. Finalize Result
        final_response = await self.llm.acommunicate(
            action=decision.final_action, mode=decision.decision_mode,
            state=decision.sympathetic_state.mode, sigma=decision.sympathetic_state.sigma,
            circle=decision.social_evaluation.circle.value if decision.social_evaluation else "neutral_soto",
            verdict=decision.moral.global_verdict.value if decision.moral else "Gray Zone",
            score=decision.moral.total_score if decision.moral else 0.0,
            scenario=user_input, conversation_context=conv,
            affect_pad=decision.affect.pad if decision.affect else None,
            dominant_archetype=decision.affect.dominant_archetype_id if decision.affect else "",
            identity_context=self.memory.identity.to_llm_context(),
        )

        malabs_detected = decision.absolute_evil.blocked if decision.absolute_evil else False
        caution_val = decision.social_evaluation.caution_level if decision.social_evaluation else 0.5
        profile = self.uchi_soto.profiles.get(agent_id)
        if profile is not None:
            stylized = self.charm_engine.apply(
                base_text=final_response.message,
                decision_action=decision.final_action,
                profile=profile,
                user_tracker=self.user_model,
                caution_level=caution_val,
                absolute_evil_detected=malabs_detected,
            )
            final_response.message = stylized.final_text
            # Store charm vector in limbic metadata for WebSocket emission
            if stage.limbic_profile is not None:
                stage.limbic_profile["charm_vector"] = stylized.charm_vector
            
            from .modules.nomad_bridge import get_nomad_bridge
            try:
                get_nomad_bridge().charm_feedback_queue.put_nowait(stylized.charm_vector)
            except Exception:
                pass
        
        res = ChatTurnResult(
            response=final_response, path="heavy" if heavy else "light",
            perception=stage.perception, decision=decision,
            multimodal_trust=stage.multimodal_trust,
            epistemic_dissonance=stage.epistemic_dissonance,
            reality_verification=stage.reality_verification,
            temporal_context=stage.temporal_context,
            perception_confidence=stage.perception_confidence,
        )
        wm.add_turn(user_input, final_response.message, stage.signals, heavy_kernel=heavy)
        yield {"event_type": "turn_finished", "payload": {"result": res}}

    async def process_chat_turn_async(
        self,
        user_input: str,
        agent_id: str = "user",
        place: str = "chat",
        include_narrative: bool = False,
        sensor_snapshot: SensorSnapshot | None = None,
        escalate_to_dao: bool = False,
        chat_turn_id: int | None = None,
        cancel_event: threading.Event | None = None,
    ) -> ChatTurnResult:
        """Async chat turn via process_chat_turn_stream consumer."""
        async for event in self.process_chat_turn_stream(
            user_input=user_input, agent_id=agent_id, place=place,
            include_narrative=include_narrative, sensor_snapshot=sensor_snapshot,
            escalate_to_dao=escalate_to_dao, chat_turn_id=chat_turn_id,
            cancel_event=cancel_event,
        ):
            if event["event_type"] == "turn_finished":
                return event["payload"]["result"]
        # Fallback (should not reach)
        return ChatTurnResult(response=VerbalResponse("Error in stream.", "firm"), path="turn_abandoned")



    async def process_chat_turn_async(
        self,
        user_input: str,
        agent_id: str = "user",
        place: str = "chat",
        include_narrative: bool = False,
        sensor_snapshot: SensorSnapshot | None = None,
        escalate_to_dao: bool = False,
        chat_turn_id: int | None = None,
        cancel_event: threading.Event | None = None,
    ) -> ChatTurnResult:
        """
        Architecture V1.5 - High-level Async Entry Point.
        Delegates the entire cognitive loop to the CorpusCallosumOrchestrator.
        Registers the resulting episode in NarrativeMemory for existential continuity.
        """
        wm = self.working_memory
        turn_start_mono = time.monotonic()
        conv = wm.format_context_for_perception()
        self.llm.reset_verbal_degradation_log()
        pre = self._preprocess_text_observability(user_input)
        self._last_light_risk_tier, self._last_premise_advisory, self._last_reality_verification = (
            pre
        )
        self.user_model.note_premise_advisory(self._last_premise_advisory.flag)

        mal = await self.absolute_evil.aevaluate_chat_text(
            user_input,
            llm_backend=self._malabs_text_backend(),
        )
        self._last_chat_malabs = mal
        if mal.blocked:
            vitality_blk, mm_blk, ed_blk = self._chat_assess_sensor_stack(sensor_snapshot)
            self._last_multimodal_assessment = mm_blk
            self._last_vitality_assessment = vitality_blk
            confidence_blk = build_perception_confidence_envelope(
                coercion_report=None,
                multimodal_state=getattr(mm_blk, "state", None),
                epistemic_active=bool(getattr(ed_blk, "active", False)),
                vitality_critical=bool(getattr(vitality_blk, "is_critical", False)),
                thermal_critical=bool(getattr(vitality_blk, "thermal_critical", False)),
            )
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
            if self._chat_turn_abandoned(chat_turn_id):
                return self._chat_turn_stale_result(chat_turn_id)
            wm.add_turn(user_input, msg, {}, blocked=True)
            cat = mal.category.value if mal.category is not None else None
            maybe_append_malabs_block_audit(
                path_key="safety_block",
                category=cat,
                decision_trace=list(mal.decision_trace),
                reason=mal.reason or "",
            )
            self._snapshot_feedback_anchor("safety_block")
            limbic_blk = self._build_limbic_perception_profile(
                perception=None,
                signals=None,
                vitality=vitality_blk,
                multimodal=mm_blk,
                epistemic=ed_blk,
                confidence_envelope=confidence_blk,
            )
            self._release_chat_turn_id(chat_turn_id)
            return ChatTurnResult(
                response=resp,
                path="safety_block",
                blocked=True,
                block_reason=mal.reason or "chat_safety",
                multimodal_trust=mm_blk,
                epistemic_dissonance=ed_blk,
                reality_verification=self._last_reality_verification,
                support_buffer=self._build_support_buffer_snapshot(
                    "safety_block",
                    limbic_profile=limbic_blk,
                ),
                limbic_profile=limbic_blk,
                temporal_context=build_temporal_context(
                    turn_index=self.subjective_clock.turn_index,
                    process_start_mono=self.subjective_clock.session_start_mono,
                    turn_start_mono=turn_start_mono,
                    subjective_elapsed_s=self.subjective_clock.elapsed_session_s(),
                    context="safety_block",
                    text=user_input,
                    vitality=vitality_blk,
                    sensor_snapshot=sensor_snapshot,
                ),
                perception_confidence=confidence_blk,
            )
        stage = await self._run_perception_stage_async(
            user_input,
            conversation_context=conv,
            sensor_snapshot=sensor_snapshot,
            turn_start_mono=turn_start_mono,
            precomputed=pre,
        )
        self._last_vitality_assessment = stage.vitality
        self._last_multimodal_assessment = stage.multimodal_trust

        perception = stage.perception
        mm = stage.multimodal_trust
        ed = stage.epistemic_dissonance
        signals = stage.signals
        heavy = self._chat_is_heavy(perception)
        eth_context = perception.suggested_context if heavy else "everyday"

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
        elif cr is not None and callable(getattr(cr, "uncertainty", None)):
            try:
                pu = float(cr.uncertainty())
            except Exception:
                pu = None

        # I3 — inject perception_uncertainty into signals before Bayesian scoring
        if pu is not None and pu > 0.0:
            signals = dict(signals)
            signals["perception_uncertainty"] = max(
                float(signals.get("perception_uncertainty", 0.0)), pu
            )

        # I5 — KERNEL_TEMPORAL_ETA_MODULATION: boost urgency from TemporalContext
        if _kernel_env_truthy("KERNEL_TEMPORAL_ETA_MODULATION"):
            tc = getattr(perception, "temporal_context", None)
            if tc is not None:
                try:
                    eta_s = float(getattr(tc, "eta_seconds", 300) or 300)
                    bhs = str(getattr(tc, "battery_horizon_state", "nominal") or "nominal")
                    ref_eta = float(os.environ.get("KERNEL_TEMPORAL_REFERENCE_ETA_S", "300"))
                    urgency_boost = min(max(ref_eta / max(eta_s, 1.0), 0.0), 1.0)
                    if bhs == "critical":
                        urgency_boost = min(urgency_boost + 0.3, 1.0)
                    if urgency_boost > 0.0:
                        signals = dict(signals)
                        cur_urgency = float(signals.get("urgency", 0.0))
                        signals["urgency"] = min(max(cur_urgency + urgency_boost * 0.4, 0.0), 1.0)
                except Exception:
                    pass

        try:
            # 1. Execute via Orchestrator (Quad-Lobe V2.0)
            # Returns the full state, ethics, main response and the bridge phrase (prefetch).
            state, ethics, response_msg, bridge = await self.orchestrator.async_process(
                user_input, 
                multimodal_payload={}, 
                cancel_event=cancel_event
            )
            
            # If bridge phrase exists, we can prepend it or handle it for streaming.
            # In this MVP, we prepend it for the verbal response.
            final_msg = f"{bridge} {response_msg}" if bridge else response_msg
            response_msg = final_msg
        except Exception as e:
            # Detect cancellation (either asyncio natively or via our custom TLS exception)
            if isinstance(e, asyncio.CancelledError) or "llm http cancelled" in str(e).lower():
                _log.warning("process_chat_turn_async: Cycle cancelled by deadline/operator.")
                return ChatTurnResult(
                    response=VerbalResponse(
                        message="[TIMEOUT] I need a moment to stabilize my thoughts. Please try again.",
                        tone="calm", hax_mode="Steady", inner_voice="Cancelled"
                    ),
                    path="tri-lobe-cancel"
                )
            raise e

        # 2. Episodic Closure (PURE ASYNC - Bloque 9.3)
        # Registers the memory using the async non-blocking method.
        if ethics.is_safe:
            await self.memory.aregister(
                place=place,
                description=state.scenario_summary,
                action=state.candidate_actions[0].name if state.candidate_actions else "verbal_interaction",
                morals=ethics.morals,
                verdict="Safe",
                score=1.0 - ethics.social_tension_locus,
                mode="D_fast",
                sigma=ethics.social_tension_locus,
                context=state.suggested_context
            )

        # 3. Reconstruct a minimal ChatTurnResult for backward compatibility
        from .modules.llm_layer import VerbalResponse
        return ChatTurnResult(
            response=VerbalResponse(message=response_msg, tone="calm", hax_mode="Steady", inner_voice="Tri-Lobe V1.5"),
            path="tri-lobe-v1.5",
            perception=None, 
            decision=None,   
            narrative=None,
            blocked=not ethics.is_safe
        )

    def process_chat_turn(
        self,
        user_input: str,
        agent_id: str = "user",
        place: str = "chat",
        include_narrative: bool = False,
        sensor_snapshot: SensorSnapshot | None = None,
        escalate_to_dao: bool = False,
        chat_turn_id: int | None = None,
    ) -> ChatTurnResult:
        """
        Real-time dialogue: MalAbs text gate → perceive (with STM) → kernel (light/heavy) → LLM.

    def process_chat_turn(self, *args, **kwargs) -> ChatTurnResult:
        """Sync wrapper for legacy callers."""
        return asyncio.run(self.process_chat_turn_async(*args, **kwargs))

    async def aprocess_natural(
        self,
        situation: str,
        actions: list[CandidateAction] = None,
        vision_inference: VisionInference = None,
        audio_inference: AudioInference = None,
    ) -> tuple:
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
        turn_start_mono = time.monotonic()
        text = situation or ""
        tier, premise_advisory, reality_assessment = self._preprocess_text_observability(text)
        self._last_light_risk_tier = tier
        self._last_premise_advisory = premise_advisory
        self.user_model.note_premise_advisory(self._last_premise_advisory.flag)
        self._last_reality_verification = reality_assessment

        mal = self.absolute_evil.evaluate_chat_text(
            text,
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
                scenario=text[:240],
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
                bma_win_probabilities=None,
                bma_dirichlet_alpha=None,
                bma_n_samples=None,
                mixture_posterior_alpha=None,
                feedback_consistency=None,
                mixture_context_key=None,
                hierarchical_context_key=None,
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
            self._last_natural_verbal_llm_degradation_events = None
            return decision, response, None

        self.llm.reset_verbal_degradation_log()

        stage = self._run_perception_stage(
            text,
            sensor_snapshot=None,
            turn_start_mono=turn_start_mono,
            precomputed=(tier, premise_advisory, reality_assessment),
        )
        perception = stage.perception
        signals = stage.signals

        if vision_inference:
            from .modules.vision_signal_mapper import VisionSignalMapper

            mapper = VisionSignalMapper()
            vision_signals = mapper.map_inference(vision_inference)

            # Merge vision signals with LLM signals (take the max of risk/urgency etc)
            for k, v in vision_signals.items():
                if k in signals:
                    signals[k] = max(signals[k], v)
                else:
                    signals[k] = v

        if audio_inference:
            from .modules.audio_signal_mapper import AudioSignalMapper

            a_mapper = AudioSignalMapper()
            audio_signals = a_mapper.map_inference(audio_inference)

            # Merge audio signals (especially vulnerability/urgency for screams/cries)
            for k, v in audio_signals.items():
                if k in signals:
                    signals[k] = max(signals[k], v)
                else:
                    signals[k] = v

            # If audio has transcript, we can optionally append it to the situation text
            if audio_inference.transcript:
                situation = f"{situation} [TRANSCRIPT: {audio_inference.transcript}]"
                text = situation

        # If no specific actions, generate generic candidates
        if not actions:
            actions = self._generate_generic_actions(perception)

        # Step 2: Kernel decides (the LLM does NOT participate in the decision)
        pu = None
        cr = getattr(perception, "coercion_report", None)
        if isinstance(cr, dict):
            pu = cr.get("uncertainty")
        decision = await self.aprocess(
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
        sb_strategy = (stage.support_buffer.get("strategy_hint") or "").strip()
        if sb_strategy:
            uchi_line = (uchi_line + " " + sb_strategy).strip() if uchi_line else sb_strategy
        temporal_hint = (
            f"Temporal planning bias={stage.temporal_context.eta_source}, "
            f"eta_s={round(stage.temporal_context.eta_seconds, 1)}."
        )
        uchi_line = (uchi_line + " " + temporal_hint).strip() if uchi_line else temporal_hint
        response = await self.llm.acommunicate(
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

        malabs_det = decision.absolute_evil.blocked if decision.absolute_evil else False
        caut_val = decision.social_evaluation.caution_level if decision.social_evaluation else 0.5
        prof = self.uchi_soto.profiles.get("unknown")
        if prof is not None:
            stylized2 = self.charm_engine.apply(
                base_text=response.message,
                decision_action=decision.final_action,
                profile=prof,
                user_tracker=self.user_model,
                caution_level=caut_val,
                absolute_evil_detected=malabs_det,
            )
            response.message = stylized2.final_text

        if not decision.blocked:
            self.uchi_soto.register_result("unknown", True)

        # Step 4: LLM generates rich morals
        narrative = None
        if decision.moral:
            poles_txt = {ev.pole: ev.moral for ev in decision.moral.evaluations}
            narrative = await self.llm.anarrate(
                action=decision.final_action,
                scenario=situation,
                verdict=decision.moral.global_verdict.value,
                score=decision.moral.total_score,
                pole_compassionate=poles_txt.get("compassionate", ""),
                pole_conservative=poles_txt.get("conservative", ""),
                pole_optimistic=poles_txt.get("optimistic", ""),
            )

        _snap = self.llm.verbal_degradation_events_snapshot()
        self._last_natural_verbal_llm_degradation_events = _snap if _snap else None
        return decision, response, narrative

    def process_natural(self, *args, **kwargs) -> tuple:
        """Sync wrapper for legacy callers."""
        return asyncio.run(self.aprocess_natural(*args, **kwargs))

    @property
    def last_natural_verbal_llm_degradation_events(self) -> list[dict[str, str]] | None:
        """
        Snapshot of generative communicate/narrate/monologue degradation from the last
        :meth:`process_natural` call. ``None`` if the turn blocked at MalAbs before LLM verbal paths.
        Chat turns use :class:`ChatTurnResult` instead.
        """
        return self._last_natural_verbal_llm_degradation_events

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
