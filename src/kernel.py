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
    def __init__(self, mode: str = "office_2"):
        self.bus = CorpusCallosum()
        self.modulator = BusModulator(self.bus)
        self.bus.modulator = self.modulator
        self.mode = mode

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
        from src.modules.motivation_engine import MotivationEngine
        from src.modules.dao_orchestrator import DAOOrchestrator
        from src.modules.migratory_identity import MigrationHub
        from src.modules.biographic_pruning import BiographicPruner
        from src.modules.immortality import ImmortalityProtocol
        from src.modules.selective_amnesia import SelectiveAmnesia
        from src.kernel_lobes.memory_lobe import MemoryLobe

        evil_detector = AbsoluteEvilDetector()
        llm = LLMModule()
        strategist = ExecutiveStrategist()
        motivation_engine = MotivationEngine()
        
        narrative = NarrativeMemory()
        dao = DAOOrchestrator()
        migration = MigrationHub()
        amnesia = SelectiveAmnesia(memory=narrative, dao=dao)
        
        # Lobe 0: Thalamus Gateway
        self.thalamus = ThalamusLobe(bus=self.bus)

        # Lobe 1: Perceptive (Sensory Cortex)
        self.sensory_cortex = PerceptiveLobe(
            safety_interlock=SafetyInterlock(),
            strategist=strategist,
            llm=llm,
            somatic_store=SomaticMarkerStore(),
            buffer=PreloadedBuffer(),
            absolute_evil=evil_detector,
            subjective_clock=SubjectiveClock(),
            bus=self.bus
        )

        # Lobe 2: Limbic (Affective/Ethical)
        self.limbic_system = LimbicEthicalLobe(bus=self.bus)

        # Lobe 3: Executive (Prefrontal)
        self.prefrontal_cortex = ExecutiveLobe(
            absolute_evil=evil_detector,
            poles=EthicalPoles(),
            will=SigmoidWill(),
            reflection_engine=EthicalReflection(),
            salience_map=SalienceMap(),
            pad_archetypes=PADArchetypeEngine(),
            motivation=motivation_engine,
            llm=llm,
            bus=self.bus
        )

        # Lobe 4: Cerebellum (Bayesian/Memory)
        self.cerebellum = CerebellumLobe(
            bayesian=BayesianEngine(),
            strategist=strategist,
            memory=narrative,
            bus=self.bus
        )
        
        # Lobe 5: Memory (Hippocampus/DAO/Identity) [Block 26.0 Integration]
        self.memory_lobe = MemoryLobe(
            memory=narrative,
            dao=dao,
            migration=migration,
            biographic_pruner=BiographicPruner(),
            immortality=ImmortalityProtocol(),
            amnesia=amnesia,
            llm=llm,
            bus=self.bus
        )
        
        self._proactive_task = None

    async def start(self) -> None:
        """Awaken the Android's Nervous System."""
        self.bus.start()
        self.modulator.start(mode=self.mode)
        self.bus.subscribe(MotorCommandDispatch, self._on_motor_dispatch)
        self._proactive_task = asyncio.create_task(self._proactive_daemon_loop())
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
                "orientation": getattr(sensor_snapshot, "orientation", None)
            },
            priority=1
        )
        
        future = self.reactions.register(pulse.pulse_id)

        await self.bus.publish(pulse)
        from src.utils.terminal_colors import TColors
        _log.info(TColors.color(f"EthosKernel: Injected raw stimulus {pulse.pulse_id}. Waiting for brain response...", TColors.OKCYAN))

        try:
            dispatch_result = await asyncio.wait_for(future, timeout=25.0)
            from src.utils.terminal_colors import color_verdict
            
            is_blocked = getattr(dispatch_result, "is_vetoed", False)
            status_tag = color_verdict("BLOCKED") if is_blocked else color_verdict("PASS")
            
            return ChatTurnResult(
                response=VerbalResponse(
                    message=f"Distributed Brain Response: {getattr(dispatch_result, 'action_id', 'unknown')}", 
                    tone="neutral"
                ),
                path="nervous_bus",
                blocked=is_blocked,
                block_reason=f"[{status_tag}] Vetoed by Prefrontal" if is_blocked else ""
            )
        except asyncio.TimeoutError:
            _log.error(f"EthosKernel: Response timeout for {pulse.pulse_id}.")
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

    async def process_chat_turn_stream(self, text: str, **kwargs) -> AsyncGenerator[dict[str, Any], None]:
        result = await self.process_chat_turn_async(text, **kwargs)
        yield {"event_type": "turn_finished", "payload": {"result": result}}

# Legacy Aliases
EthicalKernel = EthosKernel
KernelDecision = ChatTurnResult
