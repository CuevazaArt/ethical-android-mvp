"""
Thalamus Node — Sensory routing and gatekeeping.
Part of the Phase 10.1 Sensory Fusion (VVAD + VAD).

Pre-filters raw sensor streams to determine attentional focus 
before the Perceptive Lobe performs high-cost inference.
"""

from __future__ import annotations
import time
import logging
from dataclasses import dataclass, field
from typing import Any

_log = logging.getLogger(__name__)

@dataclass
class AttentionState:
    """Current attentional focus of the kernel."""
    is_user_present: bool = False
    is_user_speaking: bool = False
    is_facing_user: bool = False
    confidence: float = 0.0
    last_update: float = field(default_factory=time.time)

class ThalamusNode:
    """
    Acts as a sensory filter and synchronizer.
    
    Logic:
    - VVAD: Voice Activity + Video Presence.
    - Posture: IMU alpha/beta/gamma check.
    """
    def __init__(self, sensitivity: float = 0.5):
        self.sensitivity = sensitivity
        self.state = AttentionState()
        self._audio_history: list[float] = []
        self._max_history = 10

    def ingest_telemetry(self, payload: dict[str, Any]):
        """Ingests IMU and Battery data to update attentional confidence."""
        orientation = payload.get("orientation")
        if orientation:
            # Logic: If phone is tilted towards a common 'viewing' angle (e.g. beta 60-90)
            # we assume the user is looking at or addressing the device.
            beta = orientation.get("beta", 0)
            if 45 < beta < 105:
                self.state.is_facing_user = True
                self.state.confidence = min(1.0, self.state.confidence + 0.1)
            else:
                self.state.is_facing_user = False
                self.state.confidence = max(0.0, self.state.confidence - 0.05)
        
        self.state.last_update = time.time()

    def ingest_audio_signal(self, rms: float):
        """Processes audio volume spikes for VAD."""
        self._audio_history.append(rms)
        if len(self._audio_history) > self._max_history:
            self._audio_history.pop(0)
            
        avg_rms = sum(self._audio_history) / len(self._audio_history)
        if rms > avg_rms * 1.5 and rms > 0.05: # Threshold for 'speaking'
            self.state.is_user_speaking = True
            self.state.confidence = min(1.0, self.state.confidence + 0.2)
        else:
            self.state.is_user_speaking = False
            self.state.confidence = max(0.0, self.state.confidence - 0.1)

    def should_trigger_deliberation(self) -> bool:
        """Determines if the current sensory state warrants a full kernel tick."""
        # Simple AND/OR gate for situated importance
        if self.state.is_user_speaking and (self.state.is_facing_user or self.state.confidence > 0.7):
            return True
        return False

    def get_sensory_summary(self) -> dict[str, Any]:
        """Provides a filtered summary for the Perceptive Lobe."""
        return {
            "attention_confidence": round(self.state.confidence, 4),
            "user_activity": "speaking" if self.state.is_user_speaking else "quiet",
            "posture": "focused" if self.state.is_facing_user else "away",
            "situated_priority": 1.0 if self.should_trigger_deliberation() else 0.2
        }
