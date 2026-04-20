from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional
from src.kernel_lobes.models import LimbicStageResult
import time
import math
import logging

_log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from src.modules.uchi_soto import UchiSotoModule
    from src.modules.sympathetic import SympatheticModule
    from src.modules.locus import LocusModule
    from src.modules.sensor_contracts import SensorSnapshot
    from src.modules.multimodal_trust import MultimodalAssessment

class LimbicEthicalLobe:
    """
    Subsystem for Social (Uchi-Soto), Internal State (Sympathetic), and Locus of Control.
    
    Acts as the 'Right Hemisphere' of the kernel, handling CPU-bound emotional 
    and relational context. No network I/O here (Phase-8 strict separation).
    """
    def __init__(
        self,
        uchi_soto: UchiSotoModule,
        sympathetic: SympatheticModule,
        locus: LocusModule,
        swarm: Any = None
    ):
        self.uchi_soto = uchi_soto
        self.sympathetic = sympathetic
        self.locus = locus
        self.swarm = swarm
        self.situational_stress = 0.0  # Phase 9.2 Accumulator

    def update_situational_stress(self, level: float) -> None:
        """Accumulate or decay situational stress based on sensory alerts."""
        # Persistent stress scales the baseline social tension
        self.situational_stress = max(0.0, min(1.0, level))

    def execute_stage(
        self,
        agent_id: str,
        signals: dict[str, float],
        message_content: str,
        turn_index: int,
        sensor_snapshot: Optional[Any] = None,
        multimodal_assessment: Optional[Any] = None,
        somatic_state: Optional[dict[str, Any]] = None,
        trauma_magnitude: float = 0.0
    ) -> LimbicStageResult:
        """
        Evaluate social context and internal autonomic state.
        Vertical Increment: Somatic state (temp/battery) influences relational tension.
        """
        t0 = time.perf_counter()
        
        # Swarm Rule 2: Anti-NaN Hardening for input parameters
        if not math.isfinite(trauma_magnitude):
            _log.warning("LimbicLobe: Non-finite trauma_magnitude detected. Resetting to 0.0")
            trauma_magnitude = 0.0

        # 1. Somatic Influences (Irritability) - Phase 11.2 Refinement
        somatic_tension = 0.0
        if somatic_state:
            try:
                temp = float(somatic_state.get("temp", 45.0))
                batt = float(somatic_state.get("battery", 100.0))
                # Soften somatic impact on relational tension
                if temp > 75.0: # Raised threshold from 70.0
                    somatic_tension += 0.15 # Reduced from 0.2
                if batt < 15.0: # Lowered threshold from 20.0
                    somatic_tension += 0.05 # Reduced from 0.1
                if batt <= 5.0:
                    # Phase 11.2: Shutdown Anxiety remains high but slightly capped
                    somatic_tension += 0.3 # Reduced from 0.4
                    signals["urgency"] = max(signals.get("urgency", 0.0), 0.85) # Reduced from 0.9
                    signals["shutdown_threat"] = 1.0
            except (ValueError, TypeError):
                pass # Ignore malformed somatic data

        # 2. Ingest social context
        self.uchi_soto.ingest_turn_context(
            agent_id, signals, subjective_turn=turn_index,
            sensor_snapshot=sensor_snapshot, 
            multimodal_assessment=multimodal_assessment
        )
        
        # 3. Swarm Nudge
        if self.swarm:
            nudge = self.swarm.get_swarm_trust_nudge()
            if nudge > 0:
                signals["trust"] = max(0.0, min(1.0, signals.get("trust", 0.5) + nudge))
                
        # 4. Evaluations
        social_eval = self.uchi_soto.evaluate_interaction(signals, agent_id, message_content)
        
        # Inject somatic, situational and identity trauma tension into social evaluation
        # Trauma (Broken Mirror) creates a baseline irritability / hyper-vigilance
        # Modulate total stress nudge by KERNEL_SENSORY_GAIN
        import os
        try:
            gain = float(os.environ.get("KERNEL_SENSORY_GAIN", "1.0"))
            gain = max(0.0, min(2.0, gain))
        except (ValueError, TypeError):
            gain = 1.0

        trauma_stress = trauma_magnitude * 0.3 # Reduced from 0.4
        total_stress_nudge = (somatic_tension + (self.situational_stress * 0.4) + trauma_stress) * gain
        
        if hasattr(social_eval, "relational_tension") and total_stress_nudge > 0:
            social_eval.relational_tension = max(0.0, min(1.0, social_eval.relational_tension + total_stress_nudge))

        state = self.sympathetic.evaluate_context(signals)
        
        locus_eval = self.locus.evaluate(
            {
                "self_control": 1.0 - signals.get("risk", 0.0), 
                "external_factors": signals.get("hostility", 0.0), 
                "predictability": signals.get("calm", 0.5) * 0.5 + 0.3
            },
            social_eval.circle.value
        )
        
        latency_ms = (time.perf_counter() - t0) * 1000
        if latency_ms > 5.0: # Track heavy social computations
             _log.debug("LimbicLobe: execute_stage latency: %.4f ms", latency_ms)

        return LimbicStageResult(
            social_evaluation=social_eval,
            internal_state=state,
            locus_evaluation=locus_eval,
        )

    async def execute_stage_async(
        self,
        agent_id: str,
        signals: dict[str, float],
        message_content: str,
        turn_index: int,
        sensor_snapshot: Optional[Any] = None,
        multimodal_assessment: Optional[Any] = None,
        somatic_state: Optional[dict[str, Any]] = None,
        trauma_magnitude: float = 0.0
    ) -> LimbicStageResult:
        """Async wrapper for Level 2 Limbic processing."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self.execute_stage, 
            agent_id, signals, message_content, turn_index, 
            sensor_snapshot, multimodal_assessment, somatic_state,
            trauma_magnitude
        )


# Stable name expected by ``kernel`` / ``kernel_lobes.__init__`` imports.
LimbicLobe = LimbicEthicalLobe
