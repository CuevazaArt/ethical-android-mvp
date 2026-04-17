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

    async def execute_stage(
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
                "safety_decision": None,
                "mission_updated": False,
                "somatic_interrupt": True
            }

        # 0.1 Visual Threat Detection (B2 / Bloque 1.1)
        if sensor_snapshot and hasattr(sensor_snapshot, "image_metadata") and sensor_snapshot.image_metadata:
            from src.modules.vision_inference import VisionInferenceEngine, VisionDetection
            from src.modules.absolute_evil import AbsoluteEvilResult, AbsoluteEvilCategory
            from src.kernel_lobes.models import SemanticState
            
            vision_engine = VisionInferenceEngine()
            visual_detections = vision_engine.analyze_image(sensor_snapshot.image_metadata)
            threat = vision_engine.get_highest_threat(visual_detections)
            
            if threat:
                from src.kernel import KernelDecision, InternalState
                d = KernelDecision(
                    scenario=scenario, place=place,
                    absolute_evil=AbsoluteEvilResult(
                        blocked=True, 
                        category=AbsoluteEvilCategory.INTENTIONAL_LETHAL_VIOLENCE,
                        reason=f"Visual threat detected: {threat.label}"
                    ),
                    sympathetic_state=InternalState(mode="blocked", sigma=0.5, energy=1.0, description="VISUAL VETO"),
                    social_evaluation=None, locus_evaluation=None, bayesian_result=None, moral=None,
                    final_action=f"BLOCKED: Visual threat detected ({threat.label})",
                    decision_mode="blocked_perceptual",
                    block_reason=f"Perceptual safety violation: High-confidence {threat.label} in view."
                )
                return {
                    "safety_decision": d,
                    "mission_updated": False,
                    "visual_threat": threat
                }

        # 0.2 Check Safety
        safety_dec = self.safety_interlock.evaluate(scenario, place, context)
        
        # 0.3 Strategic Ingestion
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
        conversation_context: Optional[str] = None,
        sensor_snapshot: Optional[SensorSnapshot] = None
    ) -> SemanticState:
        """
        Full asynchronous perception cycle.
        Vertical growth: Includes sensor fusion into the prompt context.
        """
        start_time = time.time()
        
        # 1. Actual LLM call (perceive)
        perception = await self.llm_backend.aperceive(raw_input, conversation_context=conversation_context)
        
        latency = int((time.time() - start_time) * 1000)
        
        # 2. Return enriched SemanticState
        return SemanticState(
            perception_confidence=perception.confidence if hasattr(perception, "confidence") else 0.9,
            raw_prompt=raw_input,
            sensory_latency_lag=latency,
            visual_entities=getattr(sensor_snapshot, "detections", []) if sensor_snapshot else [],
            audio_sentiment=getattr(sensor_snapshot, "audio_sentiment", 0.5) if sensor_snapshot else 0.5,
            perception_result=perception # Carry original for details
        )
