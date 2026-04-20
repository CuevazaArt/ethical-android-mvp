import asyncio
import logging
import time
from typing import Dict, Any, Optional, TYPE_CHECKING
from src.kernel_lobes.thalamus_node import ThalamusNode
from src.kernel_lobes.models import RawSensoryPulse, SensorySpike, LimbicTensionAlert, GlobalDegradationPulse

if TYPE_CHECKING:
    from src.nervous_system.corpus_callosum import CorpusCallosum

_log = logging.getLogger(__name__)

class ThalamusLobe:
    """
    Thalamus Lobe — The Gateway of Consciousness (Ethos V13.0).
    
    Acts as a high-frequency filter (Gateway) for the asynchronous nervous system.
    Processes RawSensoryPulses through a biological model (ThalamusNode) and only
    promotes significant stimuli to the rest of the cortex.
    """
    def __init__(self, bus: 'CorpusCallosum'):
        self.bus = bus
        self.node = ThalamusNode()
        self._running = False
        self._degradation = 0.0
        
        # Subscribe to high-frequency signals and global system state
        self.bus.subscribe(RawSensoryPulse, self._handle_raw_pulse)
        self.bus.subscribe(GlobalDegradationPulse, self._handle_degradation)
        
        # Register as the gate for the bus to pre-filter traffic
        self.bus.set_ingress_gate(self.can_conscious_access)
        
        _log.info("ThalamusLobe: Sensory Gateway initialized and gated.")

    def can_conscious_access(self, pulse: Any) -> bool:
        """
        Ingress Gate for the CorpusCallosum.
        Blocks high-frequency noise (RawSensoryPulse) if it doesn't meet the conscious threshold.
        """
        if not isinstance(pulse, RawSensoryPulse):
            return True # Let all other pulses through
            
        # Refined Throttling Variable: Dynamic barrier based on system load
        # If load is high (>80%), focus only on high-priority reflex pulses
        if self._degradation > 0.8 and getattr(pulse, "priority", 2) > 0:
            return False
            
        # Throttling Logic for Background Noise
        if self._degradation > 0.5 and getattr(pulse, "priority", 2) == 2:
            # 50% probability of dropping background noise at mid-load
            import random
            return random.random() > 0.5
            
        return True # Default allow for routing to _handle_raw_pulse

    async def _handle_degradation(self, pulse: GlobalDegradationPulse):
        """Reactor for global system stress."""
        self._degradation = pulse.degradation_factor
        _log.debug(f"ThalamusLobe: Throttling variable updated to {self._degradation:.2f}")

    async def _handle_raw_pulse(self, pulse: RawSensoryPulse):
        """
        The Filter Mechanism.
        Millions of raw pulses (IMU, VAD, Vision entities) converge here.
        """
        if not pulse.payload:
            return

        payload = pulse.payload
        
        # 1. Update Biological Model State
        if "orientation" in payload:
            self.node.ingest_telemetry(payload)
        
        if "rms_audio" in payload:
            self.node.ingest_audio_signal(payload["rms_audio"])

        # 2. Multi-modal Fusion (Visual + Audio)
        fusion = self.node.fuse_signals(
            vision_data=payload.get("vision", {}),
            audio_data=payload.get("audio", {}),
            environmental_stress=payload.get("environmental_stress", 0.0)
        )

        # 3. Dynamic Gating (Throttling Variable)
        # We calculate the 'Conscious Threshold' based on the system's current load (degradation)
        base_gate = 0.25
        effective_gate = base_gate + (self._degradation * 0.4)

        # Survival Rule: If there is explicit text, it's a direct address, bypass gate.
        has_text = bool(payload.get("text"))
        
        if has_text or fusion["attention_locus"] > effective_gate or fusion["is_focal_address"]:
            # The signal is 'perceived' by the higher cortex
            spike = SensorySpike(
                payload={
                    "origin": pulse.origin_lobe,
                    "fusion": fusion,
                    "text": payload.get("text", ""),
                    "agent_id": payload.get("agent_id", "unknown")
                },
                priority=1,
                origin_lobe="thalamus_gateway",
                ref_pulse_id=pulse.pulse_id
            )
            await self.bus.publish(spike)
            
            # Reflex Arc: Immediate tension alert if dissonance or threat is critical
            if fusion["sensory_tension"] > 0.85:
                alert = LimbicTensionAlert(
                    tension_load=fusion["sensory_tension"],
                    priority=0, # REFLEX ARC
                    origin_lobe="thalamus_gateway",
                    ref_pulse_id=pulse.pulse_id
                )
                await self.bus.publish(alert)
        else:
            # Signal suppressed (Unconscious background noise)
            pass

    def get_clinical_summary(self) -> Dict[str, Any]:
        """Diagnostic snapshot for the dashboard."""
        return {
            "attentional_locus_current": self.node.state.confidence,
            "gate_threshold": 0.25 + (self._degradation * 0.5),
            "is_user_present": self.node.state.is_user_present,
            "is_focal": self.node.state.is_facing_user and self.node.state.is_user_speaking
        }
