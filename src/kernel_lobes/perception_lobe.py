from __future__ import annotations
import time
from typing import Any, TYPE_CHECKING, Optional, Tuple, Dict
from src.kernel_lobes.models import SemanticState, TimeoutTrauma

if TYPE_CHECKING:
    from src.modules.safety_interlock import SafetyInterlock
    from src.modules.strategy_engine import ExecutiveStrategist
    from src.modules.sensor_contracts import SensorSnapshot


class PerceptiveLobe:
    """
    Subsystem for Safety Interlocks, Strategic Ingestion, and Multimodal Perception.
    
    Acts as the 'Left Hemisphere' of the kernel, handling I/O and sensory filtering.
    """
    def __init__(
        self,
        safety_interlock: SafetyInterlock,
        strategist: ExecutiveStrategist,
        llm_backend: Optional[Any] = None
    ):
        self.safety_interlock = safety_interlock
        self.strategist = strategist
        self.llm_backend = llm_backend # For semantic perception if needed

    def execute_stage(
        self,
        scenario: str,
        place: str,
        context: str,
        sensor_snapshot: Optional[SensorSnapshot] = None,
        interrupt_event: Optional[threading.Event] = None
    ) -> Dict[str, Any]:
        """
        STAGE 0: Perception, Safety and Strategic Ingestion.
        """
        # 0.0 Somatic Overrides (Vertical Increment)
        if interrupt_event and interrupt_event.is_set():
            # In production, we would fetch details from CerebellumNode
            return {
                "safety_decision": None, # Will be handled by state change
                "mission_updated": False,
                "somatic_interrupt": True
            }

        # 0.1 Check Safety
        safety_dec = self.safety_interlock.evaluate(scenario, place, context)
        
        # 0.2 Strategic Ingestion
        if sensor_snapshot:
            # Mission updates
            if sensor_snapshot.external_mission_title:
                from src.modules.strategy_engine import MissionOrigin
                self.strategist.create_mission(
                    title=sensor_snapshot.external_mission_title,
                    origin=MissionOrigin.OWNER,
                    steps=sensor_snapshot.external_mission_steps or [],
                    priority=sensor_snapshot.external_mission_priority or 0.6,
                )
            # Generic sensor ingestion for heuristic updates
            self.strategist.ingest_sensors(sensor_snapshot)

        return {
            "safety_decision": safety_dec,
            "mission_updated": bool(sensor_snapshot and sensor_snapshot.external_mission_title)
        }

    async def observe_async(
        self, 
        raw_input: str, 
        conversation_context: Optional[Any] = None,
        sensor_snapshot: Optional[SensorSnapshot] = None
    ) -> SemanticState:
        """
        Full asynchronous perception cycle.
        Vertical growth: Includes sensor fusion into the prompt context.
        """
        start_time = time.time()
        
        # TODO: Implement actual LLM call using self.llm_backend
        # For now, simulate latency and confidence
        latency = int((time.time() - start_time) * 1000)
        
        return SemanticState(
            perception_confidence=0.95, # Simulated
            raw_prompt=raw_input,
            sensory_latency_lag=latency,
            visual_entities=getattr(sensor_snapshot, "detections", []),
            audio_sentiment=0.5 # Default
        )
        
        return state
