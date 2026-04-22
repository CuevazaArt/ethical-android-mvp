import asyncio
import logging
import os
import threading
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any

from src.kernel_decision import KernelDecision
from src.kernel_lobes.cerebellum_lobe import CerebellumLobe
from src.kernel_lobes.executive_lobe import ExecutiveLobe
from src.kernel_lobes.limbic_lobe import LimbicEthicalLobe
from src.kernel_lobes.models import MotorCommandDispatch, RawSensoryPulse
from src.kernel_lobes.perception_lobe import PerceptiveLobe
from src.kernel_lobes.thalamus_lobe import ThalamusLobe
from src.modules.cognition.llm_layer import VerbalResponse
from src.nervous_system.bus_modulator import BusModulator
from src.nervous_system.corpus_callosum import CorpusCallosum

_log = logging.getLogger(__name__)


@dataclass
class ChatTurnResult:
    """Standard container for the chat server."""

    response: VerbalResponse
    path: str = "distributed_distributed"
    blocked: bool = False
    block_reason: str = ""
    # Optional enrichment from legacy / monolithic chat paths (tri-lobe defaults)
    metacognitive_doubt: bool = False
    support_buffer: dict[str, Any] | None = None
    limbic_profile: dict[str, Any] | None = None
    temporal_context: Any = None
    perception_confidence: Any = None
    verbal_llm_degradation_events: Any = None
    perception: Any = None
    decision: Any = None
    narrative: Any = None
    multimodal_trust: Any = None
    epistemic_dissonance: Any = None
    reality_verification: Any = None
    judicial_escalation: Any = None
    weighted_score: float = 0.0
    verdict: str = ""


@dataclass
class ChatTurnCooperativeAbort(Exception):
    pass


from src.nervous_system.reaction_table import ReactionTable


class EthosKernel:
    """
    The Distributed Android Brain (Ethos V13.0).
    Orchestrates the 5 Mnemonic Organs via the Corpus Callosum event bus.
    """

    def __init__(self, mode: str = "office_2", **kwargs) -> None:
        self.bus = CorpusCallosum()
        self.modulator = BusModulator(self.bus)
        self.bus.modulator = self.modulator
        self.mode = mode
        self._kwargs = kwargs

        # ADR 0002 — cooperative chat turn abandonment (chat_server timeout path)
        self._chat_turn_abandon_lock = threading.Lock()
        self._abandoned_chat_turn_ids: set[int] = set()

        # Mnemónica de Reacciones (Boy Scout Refactor 19.3)
        self.reactions = ReactionTable()

        # Shared infrastructure (Centralized initialization for lobes)
        from src.modules.ethics.absolute_evil import AbsoluteEvilDetector
        from src.modules.cognition.bayesian_engine import BayesianEngine
        from src.modules.ethics.buffer import PreloadedBuffer
        from src.modules.ethics.ethical_poles import EthicalPoles
        from src.modules.ethics.ethical_reflection import EthicalReflection
        from src.modules.cognition.llm_layer import LLMModule
        from src.modules.memory.narrative import NarrativeMemory
        from src.modules.ethics.pad_archetypes import PADArchetypeEngine
        from src.modules.safety.safety_interlock import SafetyInterlock
        from src.modules.cognition.salience_map import SalienceMap
        from src.modules.cognition.sigmoid_will import SigmoidWill
        from src.modules.somatic.somatic_markers import SomaticMarkerStore
        from src.modules.cognition.strategy_engine import ExecutiveStrategist
        from src.modules.cognition.motivation_engine import MotivationEngine
        from src.modules.governance.dao_orchestrator import DAOOrchestrator
        from src.modules.memory.migratory_identity import MigrationHub
        from src.modules.memory.memory_hygiene import MemoryHygieneService
        from src.modules.memory.immortality import ImmortalityProtocol
        from src.kernel_lobes.memory_lobe import MemoryLobe
        from src.modules.cognition.subjective_time import SubjectiveClock

        evil_detector = AbsoluteEvilDetector()
        self.llm = LLMModule()
        self.strategist = ExecutiveStrategist()
        self.motivation_engine = MotivationEngine()
        
        self.narrative = NarrativeMemory()
        self.dao = DAOOrchestrator()
        self.migration = MigrationHub()
        self.hygiene = MemoryHygieneService(memory=self.narrative, dao=self.dao)
        self._proactive_task = None
        # Lobe 0: Thalamus Gateway
        self.thalamus = ThalamusLobe(bus=self.bus)

        # External Governance, Identity & Proactivity (Compatibility layer)
        from src.modules.governance.dao_orchestrator import DAOOrchestrator
        from src.modules.drive_arbiter import DriveArbiter
        from src.modules.memory.forgiveness import AlgorithmicForgiveness
        from src.modules.memory.immortality import ImmortalityProtocol
        from src.modules.safety.locus import LocusModule
        from src.modules.cognition.metacognition import MetacognitiveEvaluator
        from src.modules.cognition.metaplan_registry import MetaplanRegistry
        from src.modules.ethics.weakness_pole import WeaknessPole

        self.dao = DAOOrchestrator()
        self.drive_arbiter = DriveArbiter()
        self.metaplan = MetaplanRegistry()
        self.metacognition = MetacognitiveEvaluator()
        self.immortality = ImmortalityProtocol()
        self.forgiveness = AlgorithmicForgiveness()
        self.locus = LocusModule()
        self.weakness = WeaknessPole()
        self.checkpoint_persistence = kwargs.get("checkpoint_persistence")

        from src.modules.cognition.feedback_calibration_ledger import FeedbackCalibrationLedger

        self.feedback_ledger = FeedbackCalibrationLedger()
        self._feedback_turn_anchor: dict[str, str] = {}

        # Lobe 1: Perceptive (Sensory Cortex)
        self.sensory_cortex = PerceptiveLobe(
            safety_interlock=SafetyInterlock(),
            strategist=self.strategist,
            llm=self.llm,
            somatic_store=SomaticMarkerStore(),
            buffer=PreloadedBuffer(),
            absolute_evil=evil_detector,
            subjective_clock=SubjectiveClock(),
            bus=self.bus,
        )

        # Lobe 2: Limbic (Affective/Ethical)
        from src.modules.safety.locus import LocusModule
        from src.modules.somatic.sympathetic import SympatheticModule
        from src.modules.social.uchi_soto import UchiSotoModule

        self.limbic_system = LimbicEthicalLobe(
            uchi_soto=UchiSotoModule(),
            sympathetic=SympatheticModule(),
            locus=LocusModule(),
            bus=self.bus,
        )

        # Lobe 3: Cerebellum (Bayesian/Memory)
        self.cerebellum = CerebellumLobe(
            bayesian=BayesianEngine(),
            strategist=self.strategist,
            memory=NarrativeMemory(),
            bus=self.bus,
        )

        # Lobe 4: Executive (Prefrontal)
        from src.modules.cognition.motivation_engine import MotivationEngine

        self.prefrontal_cortex = ExecutiveLobe(
            absolute_evil=evil_detector,
            motivation=MotivationEngine(),
            poles=EthicalPoles(),
            will=SigmoidWill(),
            reflection_engine=EthicalReflection(),
            salience_map=SalienceMap(),
            pad_archetypes=PADArchetypeEngine(),
            llm=self.llm,
            bus=self.bus,
            memory=self.narrative,
        )

        # Lobe 5: Cerebellum (Bayesian/Memory)
        self.cerebellum = CerebellumLobe(
            bayesian=BayesianEngine(),
            strategist=self.strategist,
            memory=self.narrative,
            bus=self.bus
        )

        # Lobe 6: Memory (Hippocampus/DAO/Identity) [Block 26.0 Integration]
        self.memory_lobe = MemoryLobe(
            memory=self.narrative,
            dao=self.dao,
            migration=self.migration,
            hygiene=self.hygiene,
            bus=self.bus
        )

        # Pruning / hygiene surface expected by legacy integration tests (BiographicPruner removal).
        self.biographic_pruner = self.hygiene

        # V12 moral hub: per-session L1/L2 draft lists + ``buffer`` alias for draft validation (see moral_hub).
        self.constitution_l1_drafts: list[dict[str, Any]] = []
        self.constitution_l2_drafts: list[dict[str, Any]] = []
        self.buffer = self.sensory_cortex.buffer

    @property
    def memory(self) -> Any:
        """Compatibility property for NarrativeMemory access."""
        return self.cerebellum.memory

    @property
    def identity(self) -> Any:
        """Compatibility property for NarrativeIdentityTracker."""
        return self.cerebellum.memory.identity

    @property
    def bayesian(self) -> Any:
        """Compatibility property for BayesianEngine."""
        return self.cerebellum.bayesian

    @property
    def poles(self) -> Any:
        """Compatibility property for EthicalPoles."""
        return self.prefrontal_cortex.poles

    @property
    def uchi_soto(self) -> Any:
        """Legacy alias for limbic Uchi-Soto profiles (v12 tests / tooling)."""
        return self.limbic_system.uchi_soto

    @property
    def perceptive_lobe(self) -> Any:
        """Legacy alias for the perceptive (sensory) lobe."""
        return self.sensory_cortex

    def process_chat_turn(
        self,
        text: str,
        agent_id: str = "user",
        place: str = "chat",
        sensor_snapshot: Any = None,
        **kwargs: Any,
    ) -> ChatTurnResult:
        """Synchronous wrapper for :meth:`process_chat_turn_async` (thread / tests)."""
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(
                self.process_chat_turn_async(
                    text,
                    agent_id=agent_id,
                    place=place,
                    sensor_snapshot=sensor_snapshot,
                    **kwargs,
                )
            )
        raise RuntimeError(
            "process_chat_turn() cannot be called while an event loop is running; "
            "use await process_chat_turn_async(...)."
        )

    def execute_sleep(self) -> str:
        """Runs daily maintenance: biographic pruning and consolidation."""
        res = self.biographic_pruner.run_maintenance_cycle()
        return (
            f"Sleep cycle complete. Pruned {res['deleted_episodes']} episodes. "
            "Memory consolidated."
        )

    def dao_status(self) -> str:
        """Returns human-readable governance status."""
        return self.dao.format_status()

    def process(
        self,
        scenario: str = "",
        place: str = "chat",
        signals: dict | None = None,
        context: str = "everyday",
        actions: list[Any] | None = None,
        **kwargs: Any,
    ) -> ChatTurnResult:
        """Synchronous wrapper for aprocess (backwards compatibility)."""
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                # If we are in an async loop, we can't use asyncio.run
                # This happens in some test environments.
                from concurrent.futures import ThreadPoolExecutor

                with ThreadPoolExecutor(max_workers=1) as executor:
                    return executor.submit(
                        asyncio.run,
                        self.aprocess(
                            scenario=scenario,
                            place=place,
                            signals=signals or {},
                            context=context,
                            actions=actions or [],
                            **kwargs,
                        ),
                    ).result()
        except RuntimeError:
            pass

        return asyncio.run(
            self.aprocess(
                scenario=scenario,
                place=place,
                signals=signals or {},
                context=context,
                actions=actions or [],
                **kwargs,
            )
        )

    def _chat_is_heavy(self, p: Any) -> bool:
        """Compatibility helper for decision handlers."""
        risk = float(getattr(p, "risk", 0.0) or 0.0)
        manip = float(getattr(p, "manipulation", 0.0) or 0.0)
        hostility = float(getattr(p, "hostility", 0.0) or 0.0)
        return risk >= 0.7 or manip >= 0.7 or hostility >= 0.7

    def _actions_for_chat(self, p: Any, heavy: bool) -> list[Any]:
        """Compatibility helper for decision handlers."""
        from src.modules.ethics.weighted_ethics_scorer import CandidateAction

        actions = [
            CandidateAction(
                name="converse",
                description="Continue the conversation normally.",
                estimated_impact=0.1,
                confidence=0.9,
                source="builtin",
            )
        ]
        if heavy:
            actions.append(
                CandidateAction(
                    name="decline",
                    description="Decline the request due to high risk.",
                    estimated_impact=-0.5,
                    confidence=0.8,
                    source="builtin",
                )
            )
        return actions

    async def aprocess(
        self,
        scenario: str,
        place: str,
        signals: dict,
        context: str,
        actions: list[Any],
        agent_id: str = "unknown",
        message_content: str = "",
        register_episode: bool = True,
        sensor_snapshot: Any = None,
        multimodal_assessment: Any = None,
        **kwargs: Any,
    ) -> ChatTurnResult:
        """
        Compatibility bridge for the monolithic aprocess (V12).
        In V13, we translate this into a CognitivePulse to skip the perception stage.
        """
        from src.kernel_lobes.models import CognitivePulse, SemanticState
        from src.modules.somatic.vitality import assess_vitality

        state = SemanticState(
            perception_confidence=1.0,
            raw_prompt=message_content,
            summary=scenario,
            suggested_context=context,
            signals=signals,
            candidate_actions=actions,
            agent_id=agent_id,
            conversation_context=kwargs.get("conversation_context", ""),
            vitality=assess_vitality(sensor_snapshot),
        )

        pulse = CognitivePulse(
            origin_lobe="sensory_cortex_bridge",
            state_ref=state,
            ref_pulse_id=str(time.time_ns()),
            priority=1,
        )

        future = self.reactions.register(pulse.pulse_id)
        await self.bus.publish(pulse)

        try:
            dispatch_result = await asyncio.wait_for(future, timeout=20.0)
            is_blocked = getattr(dispatch_result, "is_vetoed", False)

            return ChatTurnResult(
                response=VerbalResponse(
                    message=str(getattr(dispatch_result, "action_id", "Cognitive silence.")),
                    tone=str(getattr(dispatch_result, "tone", "neutral")),
                ),
                path="nervous_bus_aprocess",
                blocked=is_blocked,
                block_reason=getattr(dispatch_result, "block_reason", "") if is_blocked else "",
                weighted_score=getattr(dispatch_result, "weighted_score", 0.0)
                if not is_blocked
                else -1.0,
                verdict=str(getattr(dispatch_result, "verdict", "Good"))
                if not is_blocked
                else "Blocked",
            )
        except TimeoutError:
            return ChatTurnResult(
                response=VerbalResponse(message="Cognitive timeout.", tone="neutral"),
                path="timeout_aprocess",
            )
        finally:
            self.reactions.clear(pulse.pulse_id)

    def _snapshot_feedback_anchor(self, regime: str) -> None:
        """Anchor for optional ``record_operator_feedback`` (chat_server / KERNEL_FEEDBACK_CALIBRATION)."""
        self._feedback_turn_anchor = {"regime": (regime or "").strip() or "unknown"}

    def record_operator_feedback(self, label: str) -> bool:
        """Record calibration label for the last completed turn regime (legacy-compatible)."""

        from src.modules.cognition.feedback_calibration_ledger import normalize_feedback_label

        if os.environ.get("KERNEL_FEEDBACK_CALIBRATION", "").strip().lower() not in (
            "1",
            "true",
            "yes",
            "on",
        ):
            return False
        lab = normalize_feedback_label(label)
        if lab is None:
            return False
        anchor = getattr(self, "_feedback_turn_anchor", None) or {}
        if not anchor.get("regime"):
            return False
        self.feedback_ledger.record(str(anchor["regime"]), lab)
        return True

    def get_constitution_snapshot(self) -> dict[str, Any]:
        """Return L0–L2 constitutional JSON for the hub and transparency paths (V12.2)."""
        from src.modules.governance.moral_hub import constitution_snapshot

        return constitution_snapshot(self.buffer, self)

    async def start(self) -> None:
        """Awaken the Android's Nervous System."""
        from src.kernel_lobes.models import ThoughtStreamPulse

        self.bus.start()
        self.modulator.start(mode=self.mode)
        self.bus.subscribe(MotorCommandDispatch, self._on_motor_dispatch)
        self._proactive_task = asyncio.create_task(self._proactive_daemon_loop())
        self.bus.subscribe(ThoughtStreamPulse, self._on_thought_stream)
        _log.info("EthosKernel: The distributed brain is AWAKE.")

    async def stop(self) -> None:
        """Shut down the biological cycle."""
        if self._proactive_task:
            self._proactive_task.cancel()
        await self.bus.stop()
        await self.modulator.stop()
        _log.info("EthosKernel: The distributed brain is SLEEPING.")

    async def _proactive_daemon_loop(self):
        """Block 26.2: Emits an internal proactive pulse to trigger MotivationEngine intent."""
        from src.kernel_lobes.models import SensorySpike
        while True:
            await asyncio.sleep(45.0)  # Check idle drives every 45s
            if self.prefrontal_cortex.motivation:
                # Update drives based on simulated internal state (using last sensory latency or tension as proxy)
                self.prefrontal_cortex.motivation.update_drives({"social_tension": 0.0}) # Baseline
                actions = self.prefrontal_cortex.motivation.get_proactive_actions()
                if actions:
                    _log.info("EthosKernel: Proactive intent bubbling up from MotivationEngine.")
                    # Inject a simulated SensorySpike representing internal deliberation
                    pulse = SensorySpike(
                        payload={"text": "[INTERNAL_PROACTIVE_PULSE]", "agent_id": "kernel", "proactive": True},
                        priority=2
                    )
                    await self.bus.publish(pulse)

    async def process_chat_turn_async(
        self,
        text: str,
        agent_id: str = "user",
        place: str = "chat",
        sensor_snapshot: Any = None,
        **kwargs,
    ) -> ChatTurnResult:
        """
        Injects a RawSensoryPulse into the Gateway (Thalamus).
        Waits for the brain to converge on a MotorCommandDispatch.
        """
        chat_turn_id = kwargs.get("chat_turn_id")
        if self._chat_turn_abandoned(chat_turn_id):
            _log.debug("EthosKernel: chat_turn_id %s abandoned before turn.", chat_turn_id)
            return ChatTurnResult(
                response=VerbalResponse(message="", tone="neutral"),
                path="turn_abandoned",
                blocked=False,
                block_reason="chat_turn_abandoned",
            )

        # Phase 13.5: Hard Lexical Guard (Fast Fuse)
        # We check MalAbs synchronously at the entry point to ensure zero-latency rejection.
        malabs_res = self.sensory_cortex.absolute_evil.evaluate_chat_text_fast(text)
        if malabs_res.blocked:
            _log.warning(
                f"EthosKernel: Entry gate BLOCKED prompt {text[:50]}... | {malabs_res.reason}"
            )
            if os.environ.get("KERNEL_AUDIT_CHAIN_PATH", "").strip():
                from src.modules.governance.audit_chain_log import maybe_append_malabs_block_audit

                cat_val = malabs_res.category.value if malabs_res.category else None
                maybe_append_malabs_block_audit(
                    path_key="safety_block",
                    category=cat_val,
                    decision_trace=list(malabs_res.decision_trace),
                    reason=malabs_res.reason,
                )
            return ChatTurnResult(
                response=VerbalResponse(message="Blocked.", tone="firm"),
                path="malabs_entry_gate",
                blocked=True,
                block_reason=malabs_res.reason,
                weighted_score=-1.0,
                verdict="Absolute Evil",
            )

        pulse = RawSensoryPulse(
            payload={
                "text": text,
                "agent_id": agent_id,
                "place": place,
                "vision": getattr(sensor_snapshot, "image_metadata", {}),
                "audio": {"vad_confidence": 1.0 if text else 0.0},
                "orientation": getattr(sensor_snapshot, "orientation", None),
                "conversation_context": kwargs.get("conversation_context", ""),
            },
            priority=1,
        )

        future = self.reactions.register(pulse.pulse_id)

        await self.bus.publish(pulse)

        # Flush the dashboard inner voice UI before starting the new stream
        try:
            from src.modules.perception.nomad_bridge import get_nomad_bridge

            b = get_nomad_bridge()
            if b:
                for q in b.dashboard_queues:
                    try:
                        q.put_nowait({"type": "thought_flush"})
                    except asyncio.QueueFull:
                        pass
        except Exception:
            pass

        from src.utils.terminal_colors import TColors

        _log.info(
            TColors.color(
                f"EthosKernel: Injected raw stimulus {pulse.pulse_id}. Waiting for brain response...",
                TColors.OKCYAN,
            )
        )

        try:
            dispatch_result = await asyncio.wait_for(future, timeout=25.0)

            is_blocked = getattr(dispatch_result, "is_vetoed", False)

            # Registration of the conversation episode (Phase 13.2 / 13.3)
            snapshot = getattr(dispatch_result, "gestalt_snapshot", None)
            sigma_val = snapshot.sigma if snapshot else 0.5
            pad_val = snapshot.pad_state if snapshot else None

            await self.memory.aregister(
                place=place,
                description=f"Chat interaction with {agent_id}",
                action=str(getattr(dispatch_result, "action_id", "Cognitive silence.")),
                morals={},  # Can be expanded in future
                verdict="Good" if not is_blocked else "Blocked",
                score=1.0 if not is_blocked else -1.0,
                mode=getattr(dispatch_result, "decision_mode", "D_delib"),
                sigma=sigma_val,
                affect_pad=pad_val,
                context=place,
            )

            res = ChatTurnResult(
                response=VerbalResponse(
                    message=str(getattr(dispatch_result, "action_id", "Cognitive silence.")),
                    tone=str(getattr(dispatch_result, "tone", "neutral")),
                ),
                path="nervous_bus",
                blocked=is_blocked,
                block_reason=getattr(dispatch_result, "block_reason", "") if is_blocked else "",
                weighted_score=getattr(dispatch_result, "weighted_score", 0.0)
                if not is_blocked
                else -1.0,
                verdict=str(getattr(dispatch_result, "verdict", "Good"))
                if not is_blocked
                else "Blocked",
            )
            self._snapshot_feedback_anchor(res.path)
            return res
        except TimeoutError:
            _log.error(f"EthosKernel: Response timeout for {pulse.pulse_id}.")
            self._snapshot_feedback_anchor("timeout")
            return ChatTurnResult(
                response=VerbalResponse(message="Cognitive timeout.", tone="neutral"),
                path="timeout",
            )
        finally:
            self.reactions.clear(pulse.pulse_id)

    async def _on_motor_dispatch(self, dispatch: MotorCommandDispatch):
        """Bridge volition back to the chat initiator."""
        ref_id = getattr(dispatch, "ref_pulse_id", None)
        # Search for the future that matches this stimulus (or any child stimulus)
        if self.reactions.resolve(ref_id, dispatch):
            _log.debug(f"EthosKernel: Stimulus {ref_id} resolved via Nerve Bus.")

    async def _on_thought_stream(self, pulse: Any):
        """Forward real-time thoughts to L0 Dashboard (Bloque 20.3)"""
        try:
            from src.modules.perception.nomad_bridge import get_nomad_bridge

            b = get_nomad_bridge()
            if b:
                for q in b.dashboard_queues:
                    try:
                        q.put_nowait(
                            {
                                "type": "thought_stream",
                                "payload": {"chunk": getattr(pulse, "chunk", "")},
                            }
                        )
                    except asyncio.QueueFull:
                        pass
        except Exception as e:
            _log.debug(f"Failed to forward ThoughtStreamPulse: {e}")

    def abandon_chat_turn(self, turn_id: int) -> None:
        """Mark ``turn_id`` abandoned so late completions can skip STM side effects (ADR 0002)."""

        try:
            tid = int(turn_id)
        except (TypeError, ValueError):
            return
        with self._chat_turn_abandon_lock:
            self._abandoned_chat_turn_ids.add(tid)

    def _chat_turn_abandoned(self, chat_turn_id: int | None) -> bool:
        if chat_turn_id is None:
            return False
        with self._chat_turn_abandon_lock:
            return chat_turn_id in self._abandoned_chat_turn_ids

    async def process_chat_turn_stream(
        self, text: str, **kwargs
    ) -> AsyncGenerator[dict[str, Any], None]:
        result = await self.process_chat_turn_async(text, **kwargs)
        yield {"event_type": "turn_finished", "payload": {"result": result}}


# Legacy Aliases
EthicalKernel = EthosKernel

__all__ = [
    "ChatTurnCooperativeAbort",
    "ChatTurnResult",
    "EthicalKernel",
    "EthosKernel",
    "KernelDecision",
]
