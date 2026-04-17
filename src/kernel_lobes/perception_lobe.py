import asyncio
import time
import logging
from typing import TYPE_CHECKING, List, Deque
from collections import deque

if TYPE_CHECKING:
    from src.modules.llm_layer import LLMModule
    from src.modules.vision_inference import VisionInferenceEngine

from src.kernel_lobes.thalamus_node import ThalamusNode
from src.kernel_lobes.models import SemanticState, TimeoutTrauma, SensoryEpisode

_log = logging.getLogger(__name__)

class PerceptiveLobe:
    """
    Subsystem for Safety Interlocks, Strategic Ingestion, and Multimodal Perception.
    
    Acts as the 'Left Hemisphere' of the kernel, handling I/O and sensory filtering.
    """
    def __init__(self, llm: 'LLMModule', vision: 'VisionInferenceEngine' = None):
        self.llm = llm
        self.vision = vision
        self.thalamus = ThalamusNode()
        # Buffer de percepción continua (V1.6 Nomadismo)
        # 50 slots = ~10 segundos de memoria sensorial a 5Hz
        self.sensory_buffer: Deque[SensoryEpisode] = deque(maxlen=50)
        _log.info("PerceptiveLobe initialized with Thalamus-Fusion (VVAD).")

    def absorb(self, episode: SensoryEpisode):
        """
        Punto de entrada para el Nomadismo Perceptivo (Streaming).
        Llamado por los Daemons de Visión/Audio continuamente.
        """
        self.sensory_buffer.append(episode)
        # Loggear solo si hay entidades críticas
        if any(e in ["weapon", "human_unauthorized"] for e in episode.entities):
            _log.warning(f"PerceptiveLobe: Critical visual stimulus absorbed: {episode.entities}")

    async def execute_stage(
        self,
        scenario: str,
        place: str,
        context: str,
        sensor_snapshot: Optional[SensorSnapshot] = None,
        interrupt_event: Optional[threading.Event] = None
    ) -> Dict[str, Any]:
        """
        Takes raw input, queries LLMs via API with strict timeouts.
        Returns a SemanticState with the numeric signals for the Ethical Lobe.
        """
        start_time = time.perf_counter()
        
        # 1. LLM Perception (Asíncrono)
        # TODO: Implementar el wrapper httpx.AsyncClient aquí si fuera necesario
        # Por ahora usamos aperceive que ya es asíncrono.
        perception = await self.llm.aperceive(raw_input)
        
        # 2. Vision/Multimodal enrichment (Module 9 - Buffer integration)
        visual_entities = list(set([e for ep in self.sensory_buffer for e in ep.entities]))
        
        # 2.5) Thalamus Fusion (MER V2 10.1)
        # We fuse LLM metadata (multimodal_payload) with our live buffer
        vision_input = {"human_presence": 1.0 if "human" in visual_entities else 0.0, "lip_movement": multimodal_payload.get("lip_movement", 0.0) if multimodal_payload else 0.0}
        audio_input = {"vad_confidence": 0.8, "amplitude": 0.5, "is_speech": True} # Default baseline if no raw audio
        
        fused = self.thalamus.fuse_signals(vision_input, audio_input)
        
        latency = int((time.perf_counter() - start_time) * 1000)
        
        # 3. Build SemanticState
        state = SemanticState(
            perception_confidence=1.0 - (perception.coercion_report.get("uncertainty", 0.0) if perception.coercion_report else 0.0),
            raw_prompt=raw_input,
            scenario_summary=perception.summary,
            suggested_context=perception.suggested_context,
            signals={
                "risk": perception.risk,
                "urgency": perception.urgency,
                "hostility": perception.hostility,
                "vulnerability": perception.vulnerability,
                "legality": perception.legality,
                "social_tension": max(perception.social_tension, fused.get("sensory_tension", 0.0)),
                "mystery_index": 1.0 - fused.get("attention_locus", 0.5) # Attention reduces mystery
            },
            candidate_actions=perception.generative_candidates or [],
            visual_entities=list(set(visual_entities)),
            sensory_latency_lag=latency
        )
        
        return state
