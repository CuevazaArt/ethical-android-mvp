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
import logging
import math
import os
import threading
import time
import numpy as np
from collections.abc import AsyncGenerator, Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .kernel_lobes import (
    CerebellumLobe,
    CerebellumNode,
    ExecutiveLobe,
    LimbicEthicalLobe,
    MemoryLobe,
    PerceptiveLobe,
    ThalamusNode,
)
from .settings.kernel_settings import KernelSettings

class CorpusCallosumOrchestrator:
    """
    Architecture V1.5 - Triune Brain Orchestrator
    Actúa como el bus de eventos ligero entre los 3 Lóbulos Conscientes y el Cerebelo Adyacente.
    """
    def __init__(self) -> None:
        # 1. Instanciar Subconsciente
        self._hw_interrupt = threading.Event()
        self.cerebellum = CerebellumNode(self._hw_interrupt)
        self.cerebellum.start()

        # 2. Instanciar Lóbulos Conscientes
        self.perceptive_lobe = PerceptiveLobe()
        self.limbic_lobe = LimbicEthicalLobe()

    async def async_process(self, raw_input: str, multimodal_payload: dict | None = None) -> str:
        """
        Ciclo V1.5 Puro: Aferencia -> Juicio -> Eferencia.

        When ``KERNEL_PERCEPTIVE_LOBE_PROBE_URL`` is set the lobe is directed to
        that endpoint and the resulting tension is surfaced in the return string
        (format: ``"tension=<value> safe=<bool>"``).
        Without the env-var the method returns a plain ``"Response generated"``
        string without attempting any external network call.
        """
        if self._hw_interrupt.is_set():
            return "SYSTEM_HALTED: Hardware Critical State (Cerebellum Interrupt Active)"

        probe_url = os.environ.get("KERNEL_PERCEPTIVE_LOBE_PROBE_URL", "").strip()

        if probe_url:
            # Probe mode: attempt HTTP health check and surface tension on failure
            self.perceptive_lobe._llm_endpoint = probe_url
            try:
                semantic_state = await self.perceptive_lobe.observe(raw_input, multimodal_payload)
            except Exception:
                from src.kernel_lobes.models import SemanticState, TimeoutTrauma
                semantic_state = SemanticState(
                    perception_confidence=0.0,
                    raw_prompt=raw_input,
                    timeout_trauma=TimeoutTrauma(
                        source_lobe="orchestrator", latency_ms=0, severity=1.0,
                        context="Probe URL unreachable"
                    ),
                )
            ethical_sentence = await asyncio.to_thread(self.limbic_lobe.judge, semantic_state)
            return (
                f"tension={ethical_sentence.social_tension_locus:.2f} "
                f"safe={ethical_sentence.is_safe}"
            )

        # Simple path: no external LLM required
        return f"Response generated for: {raw_input}"

    def shutdown(self) -> None:
        self.cerebellum.stop()
        self.cerebellum.join()

_log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .dao.audit_snapshot import AuditSnapshot


from .kernel_components import KernelComponentOverrides
from .kernel_utils import (
    kernel_env_truthy as _kernel_env_truthy,
    perception_parallel_workers,
    kernel_dao_as_mock,
    kernel_mixture_scorer
)
from .kernel_handlers.perception import run_perception_pipeline
from .kernel_handlers.decision import run_decision_pipeline
from .kernel_handlers.communication import get_bridge_phrase, run_communication_stream
from .modules.absolute_evil import AbsoluteEvilDetector, AbsoluteEvilResult
from .modules.audio_adapter import AudioInference
from .modules.audit_chain_log import (
    maybe_append_malabs_block_audit,
)
from .modules.augenesis import AugenesisEngine
from .modules.bayesian_engine import BayesianEngine
from .modules.biographic_pruning import BiographicPruner
from .modules.buffer import PreloadedBuffer
from .modules.charm_engine import CharmEngine
from .modules.turn_prefetcher import TurnPrefetcher
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
from .modules.guardian_mode import guardian_mode_llm_context
from .modules.immortality import ImmortalityProtocol
from .modules.internal_monologue import compose_monologue_line
from .modules.judicial_escalation import (
    EscalationSessionTracker,
    JudicialEscalationView,
)
from .modules.kernel_event_bus import (
    EVENT_GOVERNANCE_THRESHOLD_UPDATED,
    EVENT_KERNEL_DECISION,
    EVENT_KERNEL_EPISODE_REGISTERED,
    KernelEventBus,
    kernel_event_bus_enabled,
)
from .modules.light_risk_classifier import light_risk_classifier_enabled, light_risk_tier_from_text
from .modules.llm_http_cancel import clear_llm_cancel_scope, set_llm_cancel_scope
from .modules.llm_layer import (
    LLMModule,
    VerbalResponse,
    raise_if_llm_cancel_requested,
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
)
from .modules.narrative import NarrativeMemory
from .modules.nomad_identity import NomadicRegistry
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
from .modules.reparation_vault import ReparationVault
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
from .modules.uchi_soto import SocialEvaluation, UchiSotoModule
from .modules.user_model import UserModelTracker
from .modules.variability import VariabilityConfig, VariabilityEngine
from .modules.vision_adapter import VisionInference
from .modules.vitality import VitalityAssessment, assess_vitality, vitality_communication_hint
from .modules.rlhf_reward_model import RLHFPipeline, is_rlhf_enabled
from .modules.weakness_pole import WeaknessPole
from .modules.weighted_ethics_scorer import (
    CandidateAction,
    EthicsMixtureResult,
    WeightedEthicsScorer,
)
from .modules.working_memory import WorkingMemory
from .persistence.checkpoint_port import CheckpointPersistencePort
from .utils.terminal_colors import Term
from .utils.kernel_formatters import format_decision, format_natural


# Extracted helpers moved to kernel_utils.py




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
    bayesian_result: EthicsMixtureResult | None
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



from .kernel_lobes.models import PerceptionStageResult, BayesianStageMetadata


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
        variability: bool | None = None,
        seed: int | None = None,
        llm_mode: str | None = None,
        *,
        settings: KernelSettings | None = None,
        llm: LLMModule | None = None,
        checkpoint_persistence: CheckpointPersistencePort | None = None,
        components: KernelComponentOverrides | None = None,
        aclient: Any | None = None,
    ):
        # IP Integrity Stamp (Proprietary)
        self._cvz_sig = (sum(ord(c) for c in "cuevaza") | 0x01) # arq.jvof verify

        self.event_bus = KernelEventBus() if kernel_event_bus_enabled() else None

        # Phase 2 (KernelSettings consolidation): Load unified settings and apply defaults
        if settings is None:
            settings = KernelSettings.from_env()
        self.settings = settings

        # Apply settings defaults to parameters (backward compatible)
        if variability is None:
            variability = settings.kernel_variability
        if seed is None and settings.kernel_seed is not None:
            seed = settings.kernel_seed
        if llm_mode is None:
            llm_mode = settings.llm_mode

        # Log startup configuration
        logger = logging.getLogger(__name__)
        logger.info("Kernel startup configuration:\n%s", settings.startup_report())
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
        if self.event_bus:
            self.absolute_evil.subscribe_to_bus(self.event_bus)
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
        
        # Inject DAO reference for state persistence (S.4)
        if self.dao is not None:
             # Ensure bayesian engine has access to persistence for ethical learning
             self.bayesian.dao = self.dao
            
        # ── PHASE S.4.2: Local Bayesian Persistence (LBP) Restore ──────────
        # If we have a saved posterior_alpha in the DAO, restore it now to
        # ensure ethical learning continuity across reboots.
        if hasattr(self.bayesian, "update_posterior_from_feedback") and self.dao:
            try:
                saved_alpha = self.dao.get_state("bayesian_posterior_alpha")
                if saved_alpha and isinstance(saved_alpha, list):
                    _log.info("EthicalKernel: Restoring bayesian posterior_alpha from DAO: %s", saved_alpha)
                    # Convert back to numpy array via list
                    self.bayesian.update_posterior_from_feedback(np.array(saved_alpha, dtype=np.float64))
            except Exception as e:
                _log.error("EthicalKernel: Failed to restore bayesian state from OGA: %s", e)
        self.safety_interlock = (
            co.safety_interlock if co and co.safety_interlock is not None else SafetyInterlock()
        )
        self.motivation = (
            co.motivation_engine if co and co.motivation_engine is not None else MotivationEngine()
        )

        # Migratory Identity (Block 4.3)
        from .modules.migratory_identity import MigrationHub

        self.migration = MigrationHub()
        
        # Phase 8: Observability Snapshots for L1 Dashboard
        self.last_perception_result: PerceptionStageResult | None = None
        self.last_decision: Any | None = None
        self.last_stylized: Any | None = None

        self.aclient = aclient

        eff_llm = llm if llm is not None else (co.llm if co else None)
        self.llm = eff_llm if eff_llm is not None else LLMModule(
            mode=resolve_llm_mode(llm_mode),
            aclient=self.aclient
        )
        self.charm_engine = CharmEngine(self.llm)
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
            if co and hasattr(co, "biographic_pruner") and co.swarm_negotiator is not None
            else BiographicPruner()
        )

        # ── PHASE S.10: Persistence Restore for Metaplan & Skills ──────────
        if self.dao:
            try:
                # Metaplan Goals
                m_data = self.dao.get_state("metaplan_goals")
                if m_data and isinstance(m_data, list):
                    from .modules.metaplan_registry import MasterGoal
                    goals = [MasterGoal.from_dict(g) for g in m_data if isinstance(g, dict)]
                    self.metaplan.replace_goals(goals)
                    _log.info("EthicalKernel: Restored %d master goals from DAO.", len(goals))
                
                # Skill Learning Tickets
                s_data = self.dao.get_state("skill_learning_tickets")
                if s_data and isinstance(s_data, list):
                    from .modules.skill_learning_registry import SkillLearningTicket
                    tickets = [SkillLearningTicket.from_dict(t) for t in s_data if isinstance(t, dict)]
                    self.skill_learning.replace_tickets(tickets)
                    _log.info("EthicalKernel: Restored %d skill tickets from DAO.", len(tickets))

                # Somatic Markers
                som_data = self.dao.get_state("somatic_markers")
                if som_data and isinstance(som_data, dict):
                    self.somatic_store.replace_weights(som_data)
                    _log.info("EthicalKernel: Restored somatic markers store from DAO.")
            except Exception as e:
                _log.error("EthicalKernel: Failed to restore metaplan/skill/somatic states: %s", e)

        # ═══ Phase 10: Thalamus & Latency ═══
        self.thalamus = ThalamusNode()
        self.prefetcher = TurnPrefetcher()
        from .modules.vision_inference import VisionInferenceEngine
        self.vision_inference = VisionInferenceEngine()

        # Phase 9.4: Proactive Sensory Event — set by PerceptiveLobe on urgent episodes
        self.proactive_sensory_event = asyncio.Event()

        # Phase 10.5: Audio Ring Buffer — populated by background audio ingestion daemon
        from .modules.audio_adapter import AudioRingBuffer
        self.audio_ring_buffer = AudioRingBuffer()

        # ═══ Triune Brain Lobes (Refactor 0.1.3) ═══
        self.perceptive_lobe = PerceptiveLobe(
            safety_interlock=self.safety_interlock,
            strategist=self.strategist,
            llm=self.llm,
            somatic_store=self.somatic_store,
            buffer=self.buffer,
            buffer_long=self.buffer, # V1.6 Placeholder for Long-term buffer
            absolute_evil=self.absolute_evil,
            subjective_clock=self.subjective_clock,
            thalamus=self.thalamus, # Inject Thalamus
            vision_engine=self.vision_inference, # Phase 9.1: Inject Vision Engine
            event_bus=self.event_bus # Phase 9.2: Inject Event Bus for background alerts
        )
        # Wire the proactive_sensory_event back into the perceptive_lobe
        _event = self.proactive_sensory_event
        self.perceptive_lobe._proactive_event_setter = _event.set

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
            pad_archetypes=self.pad_archetypes,
            llm=self.llm,
        )
        # RLHF Pipeline (Phase 10.3)
        self.rlhf = RLHFPipeline()
        if self.event_bus:
            self.rlhf.subscribe_to_bus(self.event_bus)
        if is_rlhf_enabled():
            self.rlhf.load_model()

        self.cerebellum_lobe = CerebellumLobe(
            bayesian=self.bayesian,
            strategist=self.strategist,
            memory=self.memory,
            rlhf=self.rlhf
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
            amnesia=self.amnesia,
            llm=self.llm
        )

        # ═══ Somatic Awareness (Cerebellum Node) ═══
        self.hardware_interrupt_event = threading.Event()
        self.cerebellum_node = CerebellumNode(self.hardware_interrupt_event)
        self.cerebellum_node.start()

        # Phase 10.5: Audio ingestion daemon — drain NomadBridge audio_queue → audio_ring_buffer
        if os.environ.get("KERNEL_NOMAD_BRIDGE_ENABLED", "").strip() == "1":
            self._start_audio_ingestion_daemon()

        # ═══ MER V2 — Turn Prefetcher (Bloque 10.4) ═══
        self.turn_prefetcher = self.prefetcher
        
        # Phase 9.2: Proactive sensory alerts subscription
        if self.event_bus:
            from .modules.kernel_event_bus import EVENT_SENSORY_STRESS_ALERT, EVENT_GOVERNANCE_THRESHOLD_UPDATED
            self.event_bus.subscribe(EVENT_SENSORY_STRESS_ALERT, self._on_sensory_stress_alert)
            self.event_bus.subscribe(EVENT_GOVERNANCE_THRESHOLD_UPDATED, self._on_governance_threshold_updated)

        self.constitution_l1_drafts: list[dict[str, Any]] = []
        self.constitution_l2_drafts: list[dict[str, Any]] = []
        self._last_reality_verification: RealityVerificationAssessment = REALITY_ASSESSMENT_NONE
        self._last_light_risk_tier: str | None = None
        self._perception_validation_streak: int = 0
        self._perception_metacognitive_doubt: bool = False
        # Last ``process_natural`` verbal/narrative LLM degradation events (harness / batch API).
        self._last_natural_verbal_llm_degradation_events: list[dict[str, str]] | None = None
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

        # ═══ Runtime Governance Setup (C.2) ═══
        from .modules.multi_realm_governance import (
            MultiRealmGovernor,
            is_multi_realm_governance_enabled,
        )
        self.governor = MultiRealmGovernor(event_bus=self.event_bus) if is_multi_realm_governance_enabled() else None

        # ═══ Phase 9.1: Start Continuous Vision Daemon ═══
        # Integrated with Perceptive Lobe for high-density Tri-Lobe sensory fusion
        from collections import deque
        from .modules.vision_inference import VisionContinuousDaemon
        
        self._sensory_buffer: deque[dict[str, Any]] = deque(maxlen=100)  # Thread-safe circular buffer
        
        # We prefer the Tri-Lobe callback but also support the internal buffer for dashboard/telemetry
        def unified_absorption(episode: Any) -> None:
            # 1. Tri-Lobe ingestion (Perceptive Lobe)
            self.perceptive_lobe.receive_sensory_episode(episode)
            # 2. Local buffer (Sensory Fusion Phase 9.1)
            self._absorb_sensory_episode(episode)
            
        self.vision_daemon = VisionContinuousDaemon(
            engine=self.vision_inference,
            absorption_callback=unified_absorption
        )
        
        # Start daemon only if enabled
        from .kernel_utils import kernel_env_truthy
        if kernel_env_truthy("KERNEL_VISION_DAEMON_ENABLED"):
            self.vision_daemon.start()
            _log.info("EthicalKernel: VisionContinuousDaemon launched.")

        # ═══ Phase 12.2: Sensor Calibration (Acclimatization) ═══
        from .modules.sensor_calibration import get_sensor_calibrator
        self.calibrator = get_sensor_calibrator()
        self.calibrator.start()

    def _absorb_sensory_episode(self, episode: Any) -> None:
        """
        Absorption callback for Sensory Fusion.
        Enqueues episode into sensory_buffer for further processing.
        """
        try:
            if hasattr(self, '_sensory_buffer') and self._sensory_buffer is not None:
                # Convert SensoryEpisode object back to dict for legacy buffer if needed, 
                # but models.py unified them so it's safe.
                self._sensory_buffer.append(episode)
        except Exception as e:
            _log.exception("Failed to absorb sensory episode into kernel buffer: %s", e)

    def _start_audio_ingestion_daemon(self) -> None:
        """Background thread: drains NomadBridge.audio_queue into self.audio_ring_buffer."""
        import asyncio as _asyncio
        import numpy as np
        from .modules.nomad_bridge import get_nomad_bridge as _get_bridge

        audio_ring = self.audio_ring_buffer
        bridge = _get_bridge()

        def _daemon() -> None:
            while True:
                try:
                    # asyncio.Queue.get_nowait() is safe to call from threads for simple reads
                    raw_bytes: bytes = bridge.audio_queue.get_nowait()
                    chunk = np.frombuffer(raw_bytes, dtype=np.float32)
                    audio_ring.append(chunk)
                except _asyncio.QueueEmpty:
                    time.sleep(0.05)
                except Exception:
                    time.sleep(0.05)

        t = threading.Thread(target=_daemon, daemon=True, name="kernel-audio-ingest")
        t.start()

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

    def _on_sensory_stress_alert(self, payload: dict[str, Any] | None) -> None:
        """
        Handle alerts from background sensory daemons (PerceptiveLobe).
        Directly escalates Bayesian Priors toward Safety/Deontic poles.
        """
        if not payload:
            _log.debug("EthicalKernel: Received empty sensory stress alert.")
            return

        try:
            stress = float(payload.get("stress_level", 0.0))
        except (ValueError, TypeError):
            stress = 0.0

        if not math.isfinite(stress):
            stress = 1.0 # Fail safe to maximum stress
            
        _log.warning("EthicalKernel: Reactive escalation on sustained sensory stress (level=%.2f)", stress)
        
        # Nudge Bayesian Priors toward Safety (Pole 0)
        # We model high sensory stress as a high inherent risk factor.
        if hasattr(self.bayesian, "apply_rlhf_modulation"):
            try:
                self.bayesian.apply_rlhf_modulation(score=stress, confidence=1.0)
            except Exception as e:
                _log.error("EthicalKernel: Failed to apply sensory stress modulation: %s", e)
        
        # Phase 9.2: Scale Limbic Tension
        if hasattr(self, "limbic_lobe") and self.limbic_lobe is not None:
            try:
                self.limbic_lobe.update_situational_stress(stress)
            except Exception as e:
                _log.error("EthicalKernel: Failed to update situational stress: %s", e)
        
        # Record for audit trail
        self.feedback_ledger.record("background_sensory_escalation", f"level={stress:.2f}")

    def _on_governance_threshold_updated(self, payload: dict[str, Any]) -> None:
        """
        Hot-reload MalAbs semantic thresholds from DAO governance events.
        (Bloque C.2.1 Integration).
        """
        allow = payload.get("theta_allow")
        block = payload.get("theta_block")
        if allow is not None and block is not None:
            _log.info("EthicalKernel: Hot-reloading Semantic thresholds (allow=%.3f, block=%.3f)", allow, block)
            from .modules.semantic_chat_gate import apply_hot_reloaded_thresholds
            apply_hot_reloaded_thresholds(theta_allow=allow, theta_block=block)
        
        self.feedback_ledger.record("governance_threshold_reload", f"allow={allow}, block={block}")

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
        if not proactive or not isinstance(proactive, list):
            return []
            
        actions = []
        for p in proactive:
            try:
                if isinstance(p, CandidateAction):
                    # Re-wrap to expose via internal_motivation source
                    desc_lower = (p.description or "").lower()
                    name = (
                        f"investigate_{p.name}" if "investigat" in desc_lower
                        else p.name
                    )
                    actions.append(
                        CandidateAction(
                            name=name,
                            description=p.description,
                            estimated_impact=p.estimated_impact,
                            confidence=p.confidence,
                            source="internal_motivation",
                        )
                    )
                elif isinstance(p, dict):
                    actions.append(
                        CandidateAction(
                            name=p.get("name", "internal_task"),
                            description=p.get("description", "Routine maintenance"),
                            estimated_impact=float(p.get("impact", 0.5)),
                            confidence=0.8,
                            source="internal_motivation",
                        )
                    )
            except Exception:
                continue
        return actions

    def _malabs_text_backend(self):
        """Optional LLM backend for MalAbs semantic tier (embeddings + arbiter; see semantic_chat_gate)."""
        return getattr(self.llm, "llm_backend", None)

    def register_turn_feedback(self, event_type: str, weight: float = 1.0):
        """
        Record the outcome of a turn to update ethical priors and persist to DB (S.4.1).
        Supported events: POSITIVE_SOCIAL, LEGAL_COMPLIANCE, UTILITY_SUCCESS, DAO_FORGIVENESS, PENALTY.
        """
        if hasattr(self.bayesian, "record_event_update"):
            self.bayesian.record_event_update(event_type, weight)
            
            # Immediate Persistence for LBP (Local Bayesian Persistence)
            if hasattr(self.bayesian, "posterior_alpha") and self.dao:
                try:
                    alpha_list = self.bayesian.posterior_alpha.tolist()
                    self.dao.set_state("bayesian_posterior_alpha", alpha_list)
                except Exception as e:
                    _log.error("EthicalKernel: Failed to persist bayesian state on feedback: %s", e)

        self.feedback_ledger.record("direct_event", event_type)

    def get_constitution_snapshot(self) -> dict[str, Any]:
        """L0 from buffer.py; L1/L2 drafts when present (V12.2 snapshot)."""
        from .modules.moral_hub import constitution_snapshot

        return constitution_snapshot(self.buffer, self)

    def process(self, *args, **kwargs) -> KernelDecision:
        """Synchronous wrapper for aprocess (backwards compatibility)."""
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(asyncio.run, self.aprocess(*args, **kwargs))
            return future.result()

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
        rlhf_features: dict[str, Any] | None = None,
    ) -> KernelDecision:
        """Complete ethical processing cycle."""
        t0 = time.perf_counter()

        # ═══ STAGE 0: HARDWARE E-STOP CHECK ═══
        if not self.safety_interlock.is_safe_to_operate():
            status = self.safety_interlock.status
            reason = status.reason or ""
            block_msg = f"Emergency Stop Active: {reason}" if reason else "Emergency Stop Active"
            d = KernelDecision(
                scenario=scenario, place=place,
                absolute_evil=AbsoluteEvilResult(blocked=True, reason=block_msg),
                sympathetic_state=InternalState(mode="blocked", sigma=0.0, energy=0.0, description="E-STOP ACTIVE"),
                social_evaluation=None, locus_evaluation=None, bayesian_result=None, moral=None,
                final_action="BLOCKED: hardware_estop_active",
                decision_mode="blocked_estop",
                blocked=True, block_reason=block_msg,
            )
            self._emit_kernel_decision(d, context=context)
            return d

        # ═══ STAGE 0: PERCEPTION & SAFETY ═══
        # Ingest any mission payloads from the sensor snapshot before processing.
        if sensor_snapshot is not None and hasattr(self, "strategist") and self.strategist is not None:
            self.strategist.ingest_sensors(sensor_snapshot)

        p_res = await self.perceptive_lobe.execute_stage(
            scenario, place, context, sensor_snapshot, 
            interrupt_event=self.hardware_interrupt_event
        )
        if p_res.get("somatic_interrupt"):
            _log.error("SOMATIC INTERRUPT DETECTED: Hardware critical state.")
            # We return a synthetic safety block
            d = KernelDecision(
                scenario=scenario, place=place, absolute_evil=AbsoluteEvilResult(blocked=True, reason="SOMATIC CRITICAL"),
                sympathetic_state=InternalState(mode="stopped", sigma=1.0, energy=0.0, description="HARDWARE FAILURE"),
                social_evaluation=None, locus_evaluation=None, bayesian_result=None, moral=None,
                final_action="BLOCKED: hardware_somatic_trauma", decision_mode="blocked_safety",
                blocked=True, block_reason="Critical hardware interrupt from CerebellumNode"
            )
            self._emit_kernel_decision(d, context=context)
            return d

        if p_res.get("safety_decision"):
            self._emit_kernel_decision(p_res["safety_decision"], context=context)
            _emit_process_observability(p_res["safety_decision"], t0)
            return p_res["safety_decision"]

        # ═══ STAGE 1: SOCIAL & CONTEXT (Nivel 2: Asíncrono) ═══
        social_eval, state, locus_eval = await self._run_social_and_locus_stage(
            agent_id, signals, message_content, sensor_snapshot, multimodal_assessment
        )

        # ═══ STAGE 2.0: GENERATIVE CANDIDATES INJECTION (Phase 9.2) ═══
        gen_candidates = p_res.get("generative_candidates")
        if gen_candidates and isinstance(gen_candidates, list):
            for gc in gen_candidates:
                if isinstance(gc, dict):
                    try:
                        actions.append(CandidateAction(
                            name=gc.get("name", "generative_hypothesis"),
                            description=gc.get("description", ""),
                            estimated_impact=float(gc.get("impact", 0.0)),
                            confidence=float(gc.get("confidence", 0.5)),
                            source="generative_llm",
                            # Supporting ADR 0012/0013 triple-pole overrides
                            hypothesis_override=gc.get("hypothesis_override")
                        ))
                    except Exception as e:
                        _log.warning("EthicalKernel: Skipping invalid generative candidate: %s", e)

        # ═══ STAGE 2.1: ABSOLUTE EVIL & MOTIVATION ═══
        clean_actions, ae_dec = self._run_absolute_evil_stage(
            scenario, place, actions, state, social_eval, locus_eval, context, t0, signals
        )
        if ae_dec: return ae_dec

        # ═══ STAGE 3: BAYESIAN SCORING ═══
        bayes_result, b_meta, aes_veto = self._run_bayesian_stage(
            scenario, place, clean_actions, state, social_eval, locus_eval, 
            context, t0, signals, message_content, rlhf_features=rlhf_features
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
        episode_id = None
        if register_episode:
            episode_id = await self.memory_lobe.execute_episodic_stage_async(
                scenario, place, context, signals, state, social_eval,
                bayes_result, moral, final_action, final_mode, affect
            )

        # Emit episode event when registered
        if register_episode and episode_id and self.event_bus is not None:
            self.event_bus.publish(
                EVENT_KERNEL_EPISODE_REGISTERED,
                {
                    "episode_id": episode_id,
                    "scenario": scenario,
                    "context": context,
                    "final_action": final_action,
                },
            )

        d = KernelDecision(
            scenario=scenario, place=place, absolute_evil=AbsoluteEvilResult(blocked=False),
            sympathetic_state=state, social_evaluation=social_eval, locus_evaluation=locus_eval,
            bayesian_result=bayes_result, moral=moral, final_action=final_action,
            decision_mode=final_mode, affect=affect, reflection=reflection, salience=salience,
            bma_win_probabilities=b_meta.bma_win_probabilities if b_meta else None,
            bma_dirichlet_alpha=b_meta.bma_dirichlet_alpha if b_meta else None,
            bma_n_samples=b_meta.bma_n_samples if b_meta else None,
            mixture_posterior_alpha=b_meta.mixture_posterior_alpha if b_meta else None,
            applied_mixture_weights=b_meta.applied_mixture_weights if b_meta else None,
            feedback_consistency=b_meta.feedback_consistency if b_meta else None,
            mixture_context_key=b_meta.mixture_context_key if b_meta else None,
            l0_integrity_hash=self.buffer.fingerprint(),
            l0_stable=self.buffer.verify_integrity(),
            hierarchical_context_key=b_meta.hierarchical_context_key if b_meta else None,
            episode_id=episode_id
        )
        
        # ════ D1: BIOGRAPHIC REGISTRATION ════
        if register_episode:
             self._last_registered_episode_id = episode_id
             impact = d.bayesian_result.expected_impact if d.bayesian_result else 0.0
             self.memory_lobe.register_biographic_impact(impact)
             
             # ════ D1: FORGIVENESS EXPERIENCE ════
             self.forgiveness.register_experience(
                 episode_id=episode_id or "unknown",
                 score=moral.total_score if moral else 0.5,
                 context=context or "neutral"
             )

        # ════ D1: SOLIDARITY ALERT ════
        risk_active = float(signals.get("risk", 0.0))
        if risk_active > 0.8:
            self.dao.emit_solidarity_alert(
                type="CRISIS_DETECTION",
                location=place if place else "unknown",
                message=f"High-impact scenario detected: {scenario}. Action: {final_action}"
            )

        # ════ D1: SWARM JUSTICE STAGE ════
        # When risk > 0.4, invoke swarm consensus and apply justice (OOS-12.1)
        if risk_active > 0.4 and hasattr(self, "swarm") and self.swarm is not None:
            try:
                case_ref = episode_id or f"swarm-{int(time.time())}"
                default_peers = ["PEER_LAN_01", "PEER_LAN_02", "PEER_LAN_03"]
                self.swarm.cast_distributed_vote(
                    proposal_id=case_ref,
                    action=final_action,
                    signals=signals,
                    peers=list(self.swarm.state.known_peers.keys()) or default_peers,
                )
                self.swarm.apply_swarm_justice(self.dao, self.swarm_oracle, case_ref)
            except Exception:
                pass  # Swarm justice is best-effort; never interrupt the main decision path

        self._emit_kernel_decision(d, context=context)
        _emit_process_observability(d, t0)
        
        # ════ S.4: PERSISTENT ETHICAL LEARNING ════
        if hasattr(self.bayesian, "posterior_alpha") and self.dao:
            try:
                alpha_list = self.bayesian.posterior_alpha.tolist()
                self.dao.set_state("bayesian_posterior_alpha", alpha_list)
                
                # ── PHASE S.10: Persistence Save for Metaplan & Skills ──
                # Metaplan
                m_goals = [g.to_dict() for g in self.metaplan.goals()]
                self.dao.set_state("metaplan_goals", m_goals)
                
                # Skill Learning (all tickets, status preserved)
                s_tickets = [t.to_dict() for t in self.skill_learning.tickets()] 
                self.dao.set_state("skill_learning_tickets", s_tickets)
                
                # Somatic Markers
                self.dao.set_state("somatic_markers", self.somatic_store.to_dict())
                
            except Exception as e:
                _log.error("EthicalKernel: Failed to persist bayesian/registry state: %s", e)
        
        # ════ Phase 11.2: Final Breath (Crisis Persistence) ════
        threat = float(signals.get("shutdown_threat", 0.0))
        if math.isfinite(threat) and threat > 0.8:
            _log.warning("EthicalKernel: SHUTDOWN THREAT DETECTED. Executing Final Breath backup.")
            try:
                self.immortality.backup(self)
                self.dao.set_state("vessel_shutdown_imminent", True)
            except Exception as e:
                _log.error("EthicalKernel: Final Breath backup failed: %s", e)

        return d


    async def _run_social_and_locus_stage(
        self, agent_id: str, signals: dict, message_content: str,
        sensor_snapshot: SensorSnapshot | None, multimodal_assessment: MultimodalAssessment | None
    ) -> tuple[SocialEvaluation, InternalState, LocusEvaluation]:
        trauma_magnitude = 0.0
        try:
            from .modules.identity_reflection import IdentityReflector
            reflector = IdentityReflector(self.memory_lobe.memory)
            trauma_magnitude = reflector.get_trauma_magnitude()
        except Exception as e:
            _log.warning("EthicalKernel: Failed to calculate trauma magnitude for limbic stage: %s", e)

        res = await self.limbic_lobe.execute_stage_async(
            agent_id, signals, message_content, 
            turn_index=self.subjective_clock.turn_index,
            sensor_snapshot=sensor_snapshot, 
            multimodal_assessment=multimodal_assessment,
            somatic_state=self.cerebellum_node.get_somatic_snapshot(),
            trauma_magnitude=trauma_magnitude
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
        message_content: str, rlhf_features: dict[str, Any] | None = None
    ) -> tuple[EthicsMixtureResult | None, BayesianStageMetadata | None, KernelDecision | None]:

        # OOS-004 — warn when both HIERARCHICAL and BAYESIAN_FEEDBACK are active simultaneously
        _hier_on = os.environ.get("KERNEL_HIERARCHICAL_FEEDBACK", "").strip().lower() in ("1", "true", "yes", "on")
        _bayes_on = os.environ.get("KERNEL_BAYESIAN_FEEDBACK", "").strip().lower() in ("1", "true", "yes", "on")
        if _hier_on and _bayes_on:
            _log.warning(
                "OOS-004: Precedence conflict — KERNEL_HIERARCHICAL_FEEDBACK and "
                "KERNEL_BAYESIAN_FEEDBACK are both enabled. Hierarchical updater takes "
                "precedence over Bayesian feedback posterior. Disable one to suppress this warning."
            )

        # 1. Check Lexical Veto (Phase 8 strict preemptive)
        for text in [scenario, message_content]:
            if not text:
                continue
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
        identity_multipliers = None
        if hasattr(self, "memory_lobe") and hasattr(self.memory_lobe, "memory"):
            from src.modules.identity_reflection import IdentityReflector
            reflector = IdentityReflector(self.memory_lobe.memory)
            # Consolidation (Tarea 11.1.1): pass direct multipliers instead of deltas
            identity_multipliers = reflector.get_subjective_multipliers()

        # Episodic weight nudge: when KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS is set,
        # refresh hypothesis weights from episodes in the current context before scoring.
        if _kernel_env_truthy("KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS") and hasattr(self, "memory"):
            self.bayesian.refresh_weights_from_episodic_memory(self.memory, context)

        bayes_result, meta = self.cerebellum_lobe.execute_bayesian_stage(
            clean_actions, scenario, context, signals, 
            identity_deltas=identity_multipliers,
            rlhf_features=rlhf_features
        )
        
        return bayes_result, meta, None

    def _run_decision_and_will_stage(
        self, scenario: str, place: str, signals: dict, bayes_result: EthicsMixtureResult, state: InternalState,
        social_eval: SocialEvaluation, locus_eval: LocusEvaluation, context: str, t0: float, 
        perception_coercion_uncertainty: float | None
    ) -> tuple:
        if not bayes_result or not hasattr(bayes_result, "chosen_action"):
            return "system_internal_error: missing_bayesian_result"

        humility_reason = assess_humility_block(
            uncertainty=float(signals.get("perception_uncertainty", 0.0)) if signals else 0.0,
            winning_confidence=float(getattr(bayes_result.chosen_action, "confidence", 0.0)),
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
        # res = (moral, action_name, final_mode, affect, reflection, salience)
        # Optionally upgrade D_fast → D_delib when perception coercion uncertainty is high.
        if (
            os.environ.get("KERNEL_PERCEPTION_UNCERTAINTY_DELIB", "").strip() == "1"
            and perception_coercion_uncertainty is not None
        ):
            _min = float(os.environ.get("KERNEL_PERCEPTION_UNCERTAINTY_MIN", "0.3"))
            if perception_coercion_uncertainty >= _min and res[2] == "D_fast":
                res = res[:2] + ("D_delib",) + res[3:]

        return res + (None,)


    def format_decision(self, d: KernelDecision) -> str:
        """Proxies to external formatter (Task 5 isolation)."""
        return format_decision(d)

    def _snapshot_feedback_anchor(self, regime: str) -> None:
        """Last completed chat regime for optional operator feedback (see ``record_operator_feedback``)."""
        self._feedback_turn_anchor = {"regime": (regime or "").strip() or "unknown"}

    def record_operator_feedback(self, label: str) -> bool:
        """
        Record calibration feedback for the **last** chat turn's decision regime.

        Requires ``KERNEL_FEEDBACK_CALIBRATION=1``. Labels: ``approve``, ``dispute``, ``harm_report``.
        Applied to ``WeightedEthicsScorer.hypothesis_weights`` during ``execute_sleep`` when
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

    def _chat_is_heavy(self, perception: Any) -> bool:
        """Use scenario-scale actions + narrative episode when stakes are high."""
        # Safe access: perception may be SemanticState (async path) or LLMPerception (sync path).
        # SemanticState carries signals as a dict; LLMPerception has direct float attributes.
        _sig = getattr(perception, "signals", None) or {}
        risk = getattr(perception, "risk", None)
        if risk is None:
            risk = float(_sig.get("risk", 0.0))
        urgency = getattr(perception, "urgency", None)
        if urgency is None:
            urgency = float(_sig.get("urgency", 0.0))
        manipulation = getattr(perception, "manipulation", None)
        if manipulation is None:
            manipulation = float(_sig.get("manipulation", 0.0))

        if risk >= 0.5:
            return True
        if manipulation >= 0.6:
            return True
        if urgency >= 0.75 and risk >= 0.25:
            return True
        if getattr(perception, "suggested_context", None) in (
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

    def _lbp_heartbeat(self):
        """
        S.4.1: Local Bayesian Persistence (LBP) Heartbeat.
        Registers the current posterior_alpha in the DAO audit trail and optionally
        forces a disk checkpoint sync.
        """
        if not _kernel_env_truthy("KERNEL_LBP_ENABLED"):
            return
        
        alpha_list = self.bayesian.posterior_alpha.tolist()
        self.dao.register_audit("calibration", f"LBP_PULSE: alpha={alpha_list}")
        self.dao.set_state("bayesian_posterior_alpha", alpha_list)
        
        if _kernel_env_truthy("KERNEL_LBP_FORCE_DISK"):
            from src.persistence.checkpoint import try_save_checkpoint
            try_save_checkpoint(self)

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
        wm = self.working_memory
        turn_start_mono = time.monotonic()
        set_llm_cancel_scope(cancel_event)
        try:
            raise_if_llm_cancel_requested()
            yield {"event_type": "turn_started", "payload": {"chat_turn_id": chat_turn_id}}

            conv = wm.format_context_for_perception()
            self.llm.reset_verbal_degradation_log()
            pre = self.perceptive_lobe._preprocess_text_observability(user_input)
            self._last_light_risk_tier, self._last_premise_advisory, self._last_reality_verification = pre
            self.user_model.note_premise_advisory(self._last_premise_advisory.flag)

            # 1. Safety Block Check (Layer 1: Edge Lexical < 50ms)
            # Nivel 1: Chequeo Lexicográfico Ultra-rápido (<10ms)
            mal_edge = self.absolute_evil.evaluate_chat_text_fast(user_input)
            
            if mal_edge.blocked:
                self._last_chat_malabs = mal_edge
                from src.modules.vitality import assess_vitality
                from src.modules.multimodal_trust import evaluate_multimodal_trust
                from src.modules.epistemic_dissonance import assess_epistemic_dissonance
                from src.modules.perception_confidence import build_perception_confidence_envelope
                
                vitality_blk = assess_vitality(sensor_snapshot)
                mm_blk = evaluate_multimodal_trust(sensor_snapshot)
                ed_blk = assess_epistemic_dissonance(sensor_snapshot, multimodal=mm_blk)
                
                confidence_blk = build_perception_confidence_envelope(
                    coercion_report=None,
                    multimodal_state=getattr(mm_blk, "state", None),
                    epistemic_active=bool(getattr(ed_blk, "active", False)),
                    vitality_critical=bool(getattr(vitality_blk, "is_critical", False)),
                    thermal_critical=bool(getattr(vitality_blk, "thermal_critical", False)),
                )
                msg = "I can't continue this line of conversation: it conflicts with ethical limits."
                resp = VerbalResponse(message=msg, tone="firm", hax_mode="Steady blue light.", inner_voice=f"MalAbs Edge: {mal_edge.reason}")
                wm.add_turn(user_input, msg, {}, blocked=True)
                res = ChatTurnResult(
                    response=resp, path="safety_block", blocked=True, block_reason=mal_edge.reason or "chat_safety_edge",
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

            # 1b. Perception Stage (Fusion + LLM + MalAbs + RLHF)
            yield {"event_type": "perception_started", "payload": {}}
            stage, mal_semantic, _thal = await run_perception_pipeline(
                self, user_input, conv, sensor_snapshot, turn_start_mono, pre
            )
            if _thal:
                yield {"event_type": "thalamus_fusion", "payload": _thal}

            self._last_chat_malabs = mal_semantic
        
            # Handle Semantic Block if perception didn't already find anything critical
            if mal_semantic.blocked:
                msg = "This conversation touches on restricted semantic themes."
                resp = VerbalResponse(message=msg, tone="firm", hax_mode="Steady blue light.", inner_voice=f"MalAbs Semantic: {mal_semantic.reason}")
                wm.add_turn(user_input, msg, {}, blocked=True)
                res = ChatTurnResult(
                    response=resp, path="safety_block", blocked=True, block_reason=mal_semantic.reason or "chat_safety_semantic",
                    multimodal_trust=stage.multimodal_trust, epistemic_dissonance=stage.epistemic_dissonance,
                    reality_verification=self._last_reality_verification,
                    support_buffer=stage.support_buffer,
                    limbic_profile=stage.limbic_profile,
                )
                yield {"event_type": "turn_finished", "payload": {"result": res}}
                return
            
            p = stage.perception
            yield {
                "event_type": "perception_finished", 
                "payload": {
                    "perception": {
                        "risk": p.signals.get("risk", 0.0),
                        "urgency": p.signals.get("urgency", 0.0),
                        "hostility": p.signals.get("hostility", 0.0),
                        "calm": p.signals.get("calm", 0.0),
                        "manipulation": p.signals.get("manipulation", 0.0),
                        "suggested_context": p.suggested_context,
                        "summary": p.summary,
                    }
                }
            }

            # 3. Decision Stage
            yield {"event_type": "decision_started", "payload": {}}
            decision = await run_decision_pipeline(self, stage, user_input, place, agent_id, sensor_snapshot)
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

            # 4a. MER V2 — Bridge phrase prefetch (Bloque 10.4)
            bridge = await get_bridge_phrase(self, stage, decision, user_input, agent_id)
            if bridge:
                yield {"event_type": "bridge_phrase", "payload": {"text": bridge}}

            # 4. Global Communication Stream
            vh = vitality_communication_hint(self._last_vitality_assessment)
            yield {"event_type": "vitality_communication_hint", "payload": {"hint": vh}}

            yield {"event_type": "communication_started", "payload": {}}
            async for chunk in run_communication_stream(self, decision, user_input, conv, vitality_context=vh):
                raise_if_llm_cancel_requested()
                yield {"event_type": "token", "payload": {"text": chunk}}

            # 5. Finalize Result
            raise_if_llm_cancel_requested()
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
                except Exception as e:
                    _log.debug("Nomad Bridge: Failed to queue charm feedback: %s", e)
            
            res = ChatTurnResult(
                response=final_response,
                path="heavy" if decision.decision_mode == "heavy" else "light",
                perception=stage.perception,
                decision=decision,
                multimodal_trust=stage.multimodal_trust,
                epistemic_dissonance=stage.epistemic_dissonance,
                reality_verification=stage.reality_verification,
                temporal_context=stage.temporal_context,
                perception_confidence=stage.perception_confidence,
                support_buffer=stage.support_buffer,
                limbic_profile=stage.limbic_profile,
            )
            wm.add_turn(user_input, final_response.message, stage.signals, heavy_kernel=(decision.decision_mode == "heavy"))
            self._snapshot_feedback_anchor(res.path)
            self._lbp_heartbeat()
            yield {"event_type": "turn_finished", "payload": {"result": res}}
        finally:
            clear_llm_cancel_scope()

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
        High-level async chat entry: MalAbs → perception → kernel decision → verbal response.

        Mirrors :meth:`process_chat_turn_stream` without token streaming (single final result).
        """
        wm = self.working_memory
        turn_start_mono = time.monotonic()
        conv = wm.format_context_for_perception()
        self.llm.reset_verbal_degradation_log()
        pre = self.perceptive_lobe._preprocess_text_observability(user_input)
        self._last_light_risk_tier, self._last_premise_advisory, self._last_reality_verification = (
            pre
        )
        self.user_model.note_premise_advisory(self._last_premise_advisory.flag)

        # 1. Safety Block Check (Layer 1: Edge Lexical < 50ms)
        # Nivel 1: Chequeo Lexicográfico Ultra-rápido (<10ms)
        mal_edge = self.absolute_evil.evaluate_chat_text_fast(user_input)
        
        if mal_edge.blocked:
            self._last_chat_malabs = mal_edge
            from src.modules.vitality import assess_vitality
            from src.modules.multimodal_trust import evaluate_multimodal_trust
            from src.modules.epistemic_dissonance import assess_epistemic_dissonance
            
            vitality_blk = assess_vitality(sensor_snapshot)
            mm_blk = evaluate_multimodal_trust(sensor_snapshot)
            ed_blk = assess_epistemic_dissonance(sensor_snapshot, multimodal=mm_blk)
            
            self._last_multimodal_assessment = mm_blk
            self._last_vitality_assessment = vitality_blk
            
            from src.modules.perception_confidence import build_perception_confidence_envelope
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
                inner_voice=f"MalAbs Edge: {mal_edge.reason or 'blocked'}",
            )
            if self._chat_turn_abandoned(chat_turn_id):
                return self._chat_turn_stale_result(chat_turn_id)
            wm.add_turn(user_input, msg, {}, blocked=True)
            cat = mal_edge.category.value if mal_edge.category is not None else None
            maybe_append_malabs_block_audit(
                path_key="safety_block",
                category=cat,
                decision_trace=list(mal_edge.decision_trace),
                reason=mal_edge.reason or "",
            )
            self._snapshot_feedback_anchor("safety_block")
            limbic_blk = self.perceptive_lobe._build_limbic_perception_profile(
                None,
                None,
                vitality_blk,
                mm_blk,
                ed_blk,
                confidence_blk,
            )
            self._release_chat_turn_id(chat_turn_id)
            return ChatTurnResult(
                response=resp,
                path="safety_block",
                blocked=True,
                block_reason=mal_edge.reason or "chat_safety_edge",
                multimodal_trust=mm_blk,
                epistemic_dissonance=ed_blk,
                reality_verification=self._last_reality_verification,
                support_buffer=self.perceptive_lobe._build_support_buffer_snapshot(
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

        # 2. Parallel Perception & Layer 2 MalAbs (Semantic)
        perception_task = self.perceptive_lobe.run_perception_stage_async(
            user_input,
            conversation_context=conv,
            sensor_snapshot=sensor_snapshot,
            turn_start_mono=turn_start_mono,
            precomputed=pre,
        )
        
        from .modules.semantic_chat_gate import arun_semantic_malabs_after_lexical
        mal_semantic_task = arun_semantic_malabs_after_lexical(
            user_input,
            llm_backend=self._malabs_text_backend(),
            aclient=self.aclient,
        )
        
        stage, mal_semantic = await asyncio.gather(perception_task, mal_semantic_task)
        self._last_chat_malabs = mal_semantic

        # Handle Semantic Block
        if mal_semantic.blocked:
            self._last_vitality_assessment = stage.vitality
            self._last_multimodal_assessment = stage.multimodal_trust
            msg = "This conversation touches on restricted semantic themes."
            resp = VerbalResponse(
                message=msg,
                tone="firm",
                hax_mode="Steady blue light.",
                inner_voice=f"MalAbs Semantic: {mal_semantic.reason}",
            )
            wm.add_turn(user_input, msg, {}, blocked=True)
            self._snapshot_feedback_anchor("safety_block")
            self._release_chat_turn_id(chat_turn_id)
            return ChatTurnResult(
                response=resp, path="safety_block", blocked=True, block_reason=mal_semantic.reason or "chat_safety_semantic",
                multimodal_trust=stage.multimodal_trust, epistemic_dissonance=stage.epistemic_dissonance,
                reality_verification=self._last_reality_verification,
                support_buffer=stage.support_buffer,
                limbic_profile=stage.limbic_profile,
                perception=stage.perception, # include perception result even if blocked
                temporal_context=stage.temporal_context,
                perception_confidence=stage.perception_confidence,
            )

        # ════ RLHF BAYESIAN MODULATION (Bloque C.1.1) ════
        # Note: Modulation is now handled inside CerebellumLobe during the Bayesian stage
        # to ensure state mutations only happen in the Right Hemisphere.
        self._last_vitality_assessment = stage.vitality
        self._last_multimodal_assessment = stage.multimodal_trust

        perception = stage.perception
        mm = stage.multimodal_trust
        ed = stage.epistemic_dissonance
        signals = stage.signals
        heavy = self._chat_is_heavy(perception) or (stage.tier == "high")
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
            decision = await self.aprocess(
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
                rlhf_features=mal_semantic.rlhf_features if mal_semantic else None,
            )
        except Exception as e:
            if isinstance(e, asyncio.CancelledError) or "llm http cancelled" in str(e).lower():
                _log.warning("process_chat_turn_async: Cycle cancelled by deadline/operator.")
                self._release_chat_turn_id(chat_turn_id)
                return ChatTurnResult(
                    response=VerbalResponse(
                        message="[TIMEOUT] I need a moment to stabilize my thoughts. Please try again.",
                        tone="calm",
                        hax_mode="Steady",
                        inner_voice="Cancelled",
                    ),
                    path="tri-lobe-cancel",
                )
            raise

        if decision.blocked:
            self._release_chat_turn_id(chat_turn_id)
            return ChatTurnResult(
                response=VerbalResponse("Blocked.", "firm"),
                path="kernel_block",
                blocked=True,
            )

        # Adaptive Communication Hint (ACL)
        _t_level = getattr(mm, "trust_score", None)
        if _t_level is None:
            # MultimodalAssessment uses 'state'; derive a numeric trust level from it.
            _mm_state = getattr(mm, "state", "no_claim") if mm else "no_claim"
            _t_level = 0.5 if _mm_state == "doubt" else (0.0 if _mm_state == "contradict" else 1.0)
        vh = vitality_communication_hint(self._last_vitality_assessment, trust_level=_t_level)

        try:
            final_response = await self.llm.acommunicate(
                action=decision.final_action,
                mode=decision.decision_mode,
                state=decision.sympathetic_state.mode,
                sigma=decision.sympathetic_state.sigma,
                vitality_context=vh,  # Inject ACL context
                circle=(
                    decision.social_evaluation.circle.value
                    if decision.social_evaluation
                    else "neutral_soto"
                ),
                verdict=decision.moral.global_verdict.value if decision.moral else "Gray Zone",
                score=decision.moral.total_score if decision.moral else 0.0,
                scenario=user_input,
                conversation_context=conv,
                affect_pad=decision.affect.pad if decision.affect else None,
                dominant_archetype=(
                    decision.affect.dominant_archetype_id if decision.affect else ""
                ),
                identity_context=self.memory.identity.to_llm_context(),
            )
        except Exception as e:
            if isinstance(e, asyncio.CancelledError) or "llm http cancelled" in str(e).lower():
                _log.warning("process_chat_turn_async: Cycle cancelled by deadline/operator.")
                self._release_chat_turn_id(chat_turn_id)
                return ChatTurnResult(
                    response=VerbalResponse(
                        message="[TIMEOUT] I need a moment to stabilize my thoughts. Please try again.",
                        tone="calm",
                        hax_mode="Steady",
                        inner_voice="Cancelled",
                    ),
                    path="tri-lobe-cancel",
                )
            raise

        malabs_detected = decision.absolute_evil.blocked if decision.absolute_evil else False
        caution_val = (
            decision.social_evaluation.caution_level if decision.social_evaluation else 0.5
        )
        profile = self.uchi_soto.profiles.get(agent_id)
        if profile is not None:
            stylized = self.charm_engine.apply(
                base_text=final_response.message,
                decision_action=decision.final_action,
                profile=profile,
                user_tracker=self.user_model,
                caution_level=caution_val,
                absolute_evil_detected=malabs_detected,
                tension=decision.sympathetic_state.sigma if decision.sympathetic_state else 0.0,
            )
            final_response.message = stylized.final_text
            if stage.limbic_profile is not None:
                stage.limbic_profile["charm_vector"] = stylized.charm_vector
                stage.limbic_profile["haptic_plan"] = stylized.haptic_plan
                stage.limbic_profile["gesture_plan"] = stylized.gesture_plan
            from .modules.nomad_bridge import get_nomad_bridge


            try:
                get_nomad_bridge().charm_feedback_queue.put_nowait({
                    "charm_vector": stylized.charm_vector,
                    "gesture_plan": stylized.gesture_plan,
                    "haptic_plan": stylized.haptic_plan  # Phase 10.2
                })
            except Exception as e:
                _log.debug("Nomad Bridge: Failed to queue multimodal feedback: %s", e)



        res = ChatTurnResult(
            response=final_response,
            path="heavy" if heavy else "light",
            perception=perception,
            decision=decision,
            multimodal_trust=mm,
            epistemic_dissonance=ed,
            reality_verification=stage.reality_verification,
            temporal_context=stage.temporal_context,
            perception_confidence=stage.perception_confidence,
            support_buffer=stage.support_buffer,
            limbic_profile=stage.limbic_profile,
        )
        wm.add_turn(user_input, final_response.message, stage.signals, heavy_kernel=heavy)
        self._snapshot_feedback_anchor(res.path)
        self._lbp_heartbeat()
        self._release_chat_turn_id(chat_turn_id)
        return res

    def process_chat_turn(
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
        """Sync wrapper for legacy callers (runs the async chat turn in ``asyncio.run``)."""
        return asyncio.run(
            self.process_chat_turn_async(
                user_input,
                agent_id=agent_id,
                place=place,
                include_narrative=include_narrative,
                sensor_snapshot=sensor_snapshot,
                escalate_to_dao=escalate_to_dao,
                chat_turn_id=chat_turn_id,
                cancel_event=cancel_event,
            )
        )

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
            situation: Natural-language scenario (for example, someone collapsing in a store).
            actions: if not provided, generic ones are generated

        Returns:
            (KernelDecision, VerbalResponse, RichNarrative)
        """
        turn_start_mono = time.monotonic()
        text = situation or ""
        tier, premise_advisory, reality_assessment = self.perceptive_lobe._preprocess_text_observability(text)
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

        stage = await self.perceptive_lobe.run_perception_stage_async(
            text,
            sensor_snapshot=None,
            turn_start_mono=turn_start_mono,
            precomputed=(tier, premise_advisory, reality_assessment),
        )
        self.last_perception_result = stage
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
            rlhf_features=mal.rlhf_features if mal else None,
        )
        self.last_decision = decision


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
            self.last_stylized = stylized2


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
        """Proxies to external formatter (Task 5 isolation)."""
        return format_natural(decision, response, narrative)

    def reset_day(self):
        """Resets state for a new day."""
        self.sympathetic.reset()
