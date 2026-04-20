"""
Ethos Kernel V13.0 — The Distributed Neural Architecture.

This is NO LONGER a monolithic God Class. 
It is the 'Body' that orchestrates the 4 Mnemonic Lobes via the Corpus Callosum.
"""

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
from src.kernel_lobes.models import SensorySpike, MotorCommandDispatch
from src.modules.llm_layer import VerbalResponse

_log = logging.getLogger(__name__)

@dataclass
class ChatTurnResult:
    """Standard container for the chat server."""
    response: VerbalResponse
    path: str = "distributed_distributed"
    blocked: bool = False
    block_reason: str = ""

class ChatTurnCooperativeAbort(Exception):
    pass

class EthosKernel:
    """
    The Distributed Android Brain.
    Wrapper for the 4 Mnemonic Lobes connected by a multithreaded EventBus.
    """
    def __init__(self, mode: str = "office_2"):
        # 1. Initialize the Nervous System (The Multi-Bus)
        self.bus = CorpusCallosum()
        self.modulator = BusModulator(self.bus)
        self.bus.modulator = self.modulator
        self.mode = mode

        # 2. Initialize the 4 Mnemonic Organs (Lobes)
        # We handle dependencies (LLMs, Detectors) here or via dependency injection
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

        # Shared infrastructure for the lobes
        evil_detector = AbsoluteEvilDetector()
        llm = LLMModule()
        
        # Lobe 1: Córtex Sensorial
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

        # Lobe 2: Sistema Límbico
        self.limbic_system = LimbicEthicalLobe(bus=self.bus)

        # Lobe 3: Córtex Prefrontal
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

        # Lobe 4: Cerebelo Auxiliar
        self.cerebellum = CerebellumLobe(
            bayesian=BayesianEngine(),
            strategist=ExecutiveStrategist(),
            memory=NarrativeMemory(),
            bus=self.bus
        )

        self._pending_reactions: dict[str, asyncio.Future] = {}

    async def start(self) -> None:
        """
        Awaken the Android's Nervous System.
        Starts the event bus and the modulator, and subscribes the kernel
        to motor commands to bridge back to the chat interface.
        """
        self.bus.start()
        self.modulator.start(mode=self.mode)
        
        # Subscribe the kernel to the MotorCommandDispatch to fulfill futures
        self.bus.subscribe(MotorCommandDispatch, self._on_motor_dispatch)
        
        _log.info("EthosKernel: The distributed brain is AWAKE.")

    async def stop(self) -> None:
        """
        Shut down the biological cycle.
        Gracefully stops the bus and throttling modulator.
        """
        await self.bus.stop()
        await self.modulator.stop()
        _log.info("EthosKernel: The distributed brain is SLEEPING.")

    async def process_chat_turn_async(
        self, 
        text: str, 
        agent_id: str = "user",
        place: str = "chat",
        include_narrative: bool = False,
        sensor_snapshot: Any = None,
        escalate_to_dao: bool = False,
        chat_turn_id: int | None = None,
        cancel_event: Any = None
    ) -> ChatTurnResult:
        """
        Asynchronous Chat Entry Point.
        Injects a SensorySpike and waits for the Prefrontal Cortex to dispatch a Volition.
        """
        spike = SensorySpike(
            payload={
                "text": text, 
                "agent_id": agent_id, 
                "place": place, 
                "sensor_snapshot": sensor_snapshot
            },
            priority=1
        )
        
        # Create a promise for this specific pulse
        future = asyncio.get_running_loop().create_future()
        self._pending_reactions[spike.pulse_id] = future

        # Trigger the nervous system
        await self.bus.publish(spike)
        _log.info(f"EthosKernel: Stimulus {spike.pulse_id} and waiting for convergence...")

        # Wait for the Prefrontal Cortex to finish (with a safety timeout)
        try:
            dispatch_result = await asyncio.wait_for(future, timeout=30.0)
            return ChatTurnResult(
                response=VerbalResponse(
                    message=f"Distributed Action: {getattr(dispatch_result, 'action_id', 'unknown')} (Vetoed: {getattr(dispatch_result, 'is_vetoed', False)})...", 
                    tone="neutral"
                ),
                path="nervous_bus",
                blocked=getattr(dispatch_result, "is_vetoed", False),
                block_reason="Vetoed by Prefrontal Cortex" if getattr(dispatch_result, "is_vetoed", False) else ""
            )
        except asyncio.TimeoutError:
            _log.error(f"EthosKernel: Distributed timeout for stimulus {spike.pulse_id}.")
            return ChatTurnResult(
                response=VerbalResponse(message="System timeout in nervous bus.", tone="neutral"),
                path="timeout"
            )
        finally:
            self._pending_reactions.pop(spike.pulse_id, None)

    async def process_chat_turn_stream(
        self,
        text: str,
        **kwargs
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Bridge support for streaming UI."""
        result = await self.process_chat_turn_async(text, **kwargs)
        yield {
            "event_type": "turn_finished",
            "payload": {"result": result}
        }

    async def _on_motor_dispatch(self, dispatch: MotorCommandDispatch):
        """Callback for when the Prefrontal Cortex issues a command."""
        pulse_id = getattr(dispatch, "ref_pulse_id", None)
        if pulse_id in self._pending_reactions:
            future = self._pending_reactions[pulse_id]
            if not future.done():
                future.set_result(dispatch)
        else:
            # Fallback for old/unlinked dispatches
            if self._pending_reactions:
                pid = list(self._pending_reactions.keys())[0]
                future = self._pending_reactions[pid]
                if not future.done():
                    future.set_result(dispatch)

# Legacy Alias
EthicalKernel = EthosKernel
