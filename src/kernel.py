import asyncio
import logging
import os
from typing import Optional, Any, AsyncGenerator
from dataclasses import dataclass

from src.nervous_system.corpus_callosum import CorpusCallosum
from src.nervous_system.bus_modulator import BusModulator
from src.kernel_lobes.perception_lobe import PerceptiveLobe
from src.kernel_lobes.limbic_lobe import LimbicEthicalLobe
from src.kernel_lobes.executive_lobe import ExecutiveLobe
from src.kernel_lobes.cerebellum_lobe import CerebellumLobe
from src.kernel_lobes.thalamus_lobe import ThalamusLobe
from src.kernel_lobes.models import RawSensoryPulse, MotorCommandDispatch
from src.modules.llm_layer import VerbalResponse

_log = logging.getLogger(__name__)

@dataclass
class ChatTurnResult:
    """Standard container for the chat server."""
    response: VerbalResponse
    path: str = "distributed_distributed"
    blocked: bool = False
    block_reason: str = ""

@dataclass
class ChatTurnCooperativeAbort(Exception):
    pass

from src.nervous_system.reaction_table import ReactionTable

class EthosKernel:
    """
    The Distributed Android Brain (Ethos V13.0).
    Orchestrates the 5 Mnemonic Organs via the Corpus Callosum event bus.
    """
    def __init__(self, mode: str = "office_2", **kwargs):
        self.bus = CorpusCallosum()
        self.modulator = BusModulator(self.bus)
        self.bus.modulator = self.modulator
        self.mode = mode
        self._kwargs = kwargs

        # Mnemónica de Reacciones (Boy Scout Refactor 19.3)
        self.reactions = ReactionTable()

        # Shared infrastructure (Centralized initialization for lobes)
        from src.modules.absolute_evil import AbsoluteEvilDetector
        from src.modules.safety_interlock import SafetyInterlock
        from src.modules.llm_layer import LLMModule
        from src.modules.somatic_markers import SomaticMarkerStore
        from src.modules.buffer import PreloadedBuffer
        from src.modules.subjective_time import SubjectiveClock
        from src.modules.bayesian_engine import BayesianEngine
        from src.modules.narrative import NarrativeMemory
        from src.modules.ethical_poles import EthicalPoles
        from src.modules.sigmoid_will import SigmoidWill
        from src.modules.ethical_reflection import EthicalReflection
        from src.modules.salience_map import SalienceMap
        from src.modules.pad_archetypes import PADArchetypeEngine
        from src.modules.strategy_engine import ExecutiveStrategist

        evil_detector = AbsoluteEvilDetector()
        self.llm = LLMModule()
        self.strategist = ExecutiveStrategist()
        
        # Lobe 0: Thalamus Gateway
        self.thalamus = ThalamusLobe(bus=self.bus)

        # External Governance, Identity & Proactivity (Compatibility layer)
        from src.modules.dao_orchestrator import DAOOrchestrator
        from src.modules.drive_arbiter import DriveArbiter
        from src.modules.metaplan_registry import MetaplanRegistry
        from src.modules.metacognition import MetacognitiveEvaluator
        from src.modules.immortality import ImmortalityProtocol
        from src.modules.forgiveness import AlgorithmicForgiveness
        from src.modules.locus import LocusModule
        from src.modules.weakness_pole import WeaknessPole

        self.dao = DAOOrchestrator()
        self.drive_arbiter = DriveArbiter()
        self.metaplan = MetaplanRegistry()
        self.metacognition = MetacognitiveEvaluator()
        self.immortality = ImmortalityProtocol()
        self.forgiveness = AlgorithmicForgiveness()
        self.locus = LocusModule()
        self.weakness = WeaknessPole()
        self.checkpoint_persistence = kwargs.get("checkpoint_persistence")

        from src.modules.feedback_calibration_ledger import FeedbackCalibrationLedger

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
            bus=self.bus
        )

        # Lobe 2: Limbic (Affective/Ethical)
        from src.modules.sympathetic import SympatheticModule
        from src.modules.uchi_soto import UchiSotoModule
        from src.modules.locus import LocusModule
        self.limbic_system = LimbicEthicalLobe(
            uchi_soto=UchiSotoModule(),
            sympathetic=SympatheticModule(),
            locus=LocusModule(),
            bus=self.bus
        )

        # Lobe 3: Cerebellum (Bayesian/Memory)
        self.cerebellum = CerebellumLobe(
            bayesian=BayesianEngine(),
            strategist=self.strategist,
            memory=NarrativeMemory(),
            bus=self.bus
        )

        # Lobe 4: Executive (Prefrontal)
        from src.modules.motivation_engine import MotivationEngine
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
            memory=self.memory # Added memory link
        )

    @property
    def memory(self):
        """Compatibility property for NarrativeMemory access."""
        return self.cerebellum.memory

    @property
    def identity(self):
        """Compatibility property for NarrativeIdentityTracker."""
        return self.cerebellum.memory.identity

    @property
    def bayesian(self):
        """Compatibility property for BayesianEngine."""
        return self.cerebellum.bayesian

    @property
    def poles(self):
        """Compatibility property for EthicalPoles."""
        return self.prefrontal_cortex.poles

    def _snapshot_feedback_anchor(self, regime: str) -> None:
        """Anchor for optional ``record_operator_feedback`` (chat_server / KERNEL_FEEDBACK_CALIBRATION)."""
        self._feedback_turn_anchor = {"regime": (regime or "").strip() or "unknown"}

    def record_operator_feedback(self, label: str) -> bool:
        """Record calibration label for the last completed turn regime (legacy-compatible)."""
        import os

        from src.modules.feedback_calibration_ledger import normalize_feedback_label

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

    async def start(self) -> None:
        """Awaken the Android's Nervous System."""
        from src.kernel_lobes.models import ThoughtStreamPulse
        self.bus.start()
        self.modulator.start(mode=self.mode)
        self.bus.subscribe(MotorCommandDispatch, self._on_motor_dispatch)
        self.bus.subscribe(ThoughtStreamPulse, self._on_thought_stream)
        _log.info("EthosKernel: The distributed brain is AWAKE.")

    async def stop(self) -> None:
        """Shut down the biological cycle."""
        await self.bus.stop()
        await self.modulator.stop()
        _log.info("EthosKernel: The distributed brain is SLEEPING.")

    async def process_chat_turn_async(
        self, 
        text: str, 
        agent_id: str = "user",
        place: str = "chat",
        sensor_snapshot: Any = None,
        **kwargs
    ) -> ChatTurnResult:
        """
        Injects a RawSensoryPulse into the Gateway (Thalamus).
        Waits for the brain to converge on a MotorCommandDispatch.
        """
        # We wrap the chat into a raw pulse to go through the uniform filtering path
        pulse = RawSensoryPulse(
            payload={
                "text": text, 
                "agent_id": agent_id, 
                "place": place, 
                "vision": getattr(sensor_snapshot, "image_metadata", {}),
                "audio": {"vad_confidence": 1.0 if text else 0.0},
                "orientation": getattr(sensor_snapshot, "orientation", None),
                "conversation_context": kwargs.get("conversation_context", "")
            },
            priority=1
        )
        
        future = self.reactions.register(pulse.pulse_id)

        await self.bus.publish(pulse)
        
        # Flush the dashboard inner voice UI before starting the new stream
        try:
            from src.modules.nomad_bridge import get_nomad_bridge
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
        _log.info(TColors.color(f"EthosKernel: Injected raw stimulus {pulse.pulse_id}. Waiting for brain response...", TColors.OKCYAN))

        try:
            dispatch_result = await asyncio.wait_for(future, timeout=25.0)
            from src.utils.terminal_colors import color_verdict
            
            is_blocked = getattr(dispatch_result, "is_vetoed", False)
            status_tag = color_verdict("BLOCKED") if is_blocked else color_verdict("PASS")
            
            # Registration of the conversation episode (Phase 13.2 / 13.3)
            snapshot = getattr(dispatch_result, 'gestalt_snapshot', None)
            sigma_val = snapshot.sigma if snapshot else 0.5
            pad_val = snapshot.pad_state if snapshot else None

            await self.memory.aregister(
                place=place,
                description=f"Chat interaction with {agent_id}",
                action=str(getattr(dispatch_result, 'action_id', 'Cognitive silence.')),
                morals={}, # Can be expanded in future
                verdict="Good" if not is_blocked else "Blocked",
                score=1.0 if not is_blocked else -1.0,
                mode=getattr(dispatch_result, 'decision_mode', 'D_delib'),
                sigma=sigma_val,
                affect_pad=pad_val,
                context=place
            )

            res = ChatTurnResult(
                response=VerbalResponse(
                    message=str(getattr(dispatch_result, 'action_id', 'Cognitive silence.')), 
                    tone=str(getattr(dispatch_result, 'tone', 'neutral'))
                ),
                path="nervous_bus",
                blocked=is_blocked,
                block_reason=getattr(dispatch_result, 'block_reason', "") if is_blocked else ""
            )
            self._snapshot_feedback_anchor(res.path)
            return res
        except asyncio.TimeoutError:
            _log.error(f"EthosKernel: Response timeout for {pulse.pulse_id}.")
            self._snapshot_feedback_anchor("timeout")
            return ChatTurnResult(
                response=VerbalResponse(message="Cognitive timeout.", tone="neutral"),
                path="timeout"
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
            from src.modules.nomad_bridge import get_nomad_bridge
            b = get_nomad_bridge()
            if b:
                for q in b.dashboard_queues:
                    try:
                        q.put_nowait({"type": "thought_stream", "payload": {"chunk": getattr(pulse, "chunk", "")}})
                    except asyncio.QueueFull:
                        pass
        except Exception as e:
            _log.debug(f"Failed to forward ThoughtStreamPulse: {e}")
    async def process_chat_turn_stream(self, text: str, **kwargs) -> AsyncGenerator[dict[str, Any], None]:
        result = await self.process_chat_turn_async(text, **kwargs)
        yield {"event_type": "turn_finished", "payload": {"result": result}}

# Legacy Aliases
EthicalKernel = EthosKernel
KernelDecision = ChatTurnResult
