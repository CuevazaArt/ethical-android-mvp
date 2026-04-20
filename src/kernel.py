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

        # Shared infrastructure
        from src.modules.absolute_evil import AbsoluteEvilDetector
        from src.modules.safety_interlock import SafetyInterlock
        from src.modules.strategy_engine import ExecutiveStrategist
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

        evil_detector = AbsoluteEvilDetector()
        llm = LLMModule()
        
        # Lobe 0: Thalamus Gateway
        self.thalamus = ThalamusLobe(bus=self.bus)

        # Lobe 1: Perceptive (Sensory Cortex)
        self.sensory_cortex = PerceptiveLobe(
            safety_interlock=SafetyInterlock(),
            strategist=ExecutiveStrategist(),
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
            llm=llm,
            bus=self.bus
        )

        # Lobe 4: Cerebellum (Bayesian/Memory)
        self.cerebellum = CerebellumLobe(
            bayesian=BayesianEngine(),
            strategist=ExecutiveStrategist(),
            memory=NarrativeMemory(),
            bus=self.bus
        )

        self._pending_reactions: dict[str, asyncio.Future] = {}

    async def start(self) -> None:
        """Awaken the Android's Nervous System."""
        self.bus.start()
        self.modulator.start(mode=self.mode)
        self.bus.subscribe(MotorCommandDispatch, self._on_motor_dispatch)
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
                "orientation": getattr(sensor_snapshot, "orientation", None)
            },
            priority=1
        )
        
        future = asyncio.get_running_loop().create_future()
        self._pending_reactions[pulse.pulse_id] = future

        await self.bus.publish(pulse)
        _log.info(f"EthosKernel: Injected raw stimulus {pulse.pulse_id}. Waiting for brain response...")

        try:
            dispatch_result = await asyncio.wait_for(future, timeout=25.0)
            return ChatTurnResult(
                response=VerbalResponse(
                    message=f"Distributed Brain Response: {getattr(dispatch_result, 'action_id', 'unknown')}", 
                    tone="neutral"
                ),
                path="nervous_bus",
                blocked=getattr(dispatch_result, "is_vetoed", False),
                block_reason="Vetoed by Prefrontal" if getattr(dispatch_result, "is_vetoed", False) else ""
            )
        except asyncio.TimeoutError:
            _log.error(f"EthosKernel: Response timeout for {pulse.pulse_id}.")
            return ChatTurnResult(
                response=VerbalResponse(message="Cognitive timeout.", tone="neutral"),
                path="timeout"
            )
        finally:
            self._pending_reactions.pop(pulse.pulse_id, None)

    async def _on_motor_dispatch(self, dispatch: MotorCommandDispatch):
        """Bridge volition back to the chat initiator."""
        ref_id = getattr(dispatch, "ref_pulse_id", None)
        # Search for the future that matches this stimulus (or any child stimulus)
        # In a fully distributed system we need a better trace_id, but pulse_id works for now.
        if ref_id in self._pending_reactions:
            f = self._pending_reactions[ref_id]
            if not f.done():
                f.set_result(dispatch)

    async def process_chat_turn_stream(self, text: str, **kwargs) -> AsyncGenerator[dict[str, Any], None]:
        result = await self.process_chat_turn_async(text, **kwargs)
        yield {"event_type": "turn_finished", "payload": {"result": result}}
