"""
Thalamus Node — Sensory routing and gatekeeping.
Part of the Phase 10.1 Sensory Fusion (VVAD + VAD).

Pre-filters raw sensor streams to determine attentional focus 
before the Perceptive Lobe performs high-cost inference.

Responsibility: Antigravity + Team Cursor.
"""

from __future__ import annotations
import time
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List

from src.kernel_lobes.models import SensoryEpisode
from src.modules.sensor_contracts import SensorSnapshot

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
    - VVAD: Visual Voice Activity Detection (Presence + Lips).
    - VAD: Audio Voice Activity Detection (RMS / Confidence).
    - Posture: IMU alpha/beta/gamma check (Orientation).
    """

    _SENSORY_BUFFER_MAX = 50

    def __init__(self, sensitivity: float = 0.5):
        self.sensitivity = sensitivity
        self.state = AttentionState()
        self.sensory_buffer: List[SensoryEpisode] = []
        self._audio_history: list[float] = []
        self._max_history = 10
        
        # Phase 14: EMA Smoothing
        self._ema_facing = 0.0
        self._ema_presence = 0.0
        self._alpha = 0.3 # Smoothing factor

        # Phase 10.1: Sensory episode ring buffer
        self.sensory_buffer: list = []

    def ingest_telemetry(self, payload: dict[str, Any]):
        """Ingests IMU and Battery data to update attentional confidence (Antigravity)."""
        orientation = payload.get("orientation")
        if orientation:
            # Logic: If phone is tilted towards a common 'viewing' angle (e.g. beta 60-90)
            beta = orientation.get("beta", 0)
            target = 1.0 if (45 < beta < 105) else 0.0
            
            # Application of EMA
            self._ema_facing = (self._alpha * target) + ((1.0 - self._alpha) * self._ema_facing)
            self.state.is_facing_user = self._ema_facing > 0.6
            
            if self.state.is_facing_user:
                self.state.confidence = min(1.0, self.state.confidence + 0.05)
            else:
                self.state.confidence = max(0.0, self.state.confidence - 0.02)
        
        self.state.last_update = time.time()

    def ingest_audio_signal(self, rms: float | None):
        """Processes audio volume spikes for VAD."""
        if rms is None:
            return
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

    def fuse_signals(self, 
                     vision_data: Dict[str, Any], 
                     audio_data: Dict[str, Any],
                     environmental_stress: float = 0.0) -> Dict[str, Any]:
        """
        Calculates focal address probability by crossing audio and vision (Copilot).
        Improves VAD reliability using Lip Reading/Presence verification.
        """
        # 1. VVAD (Visual Voice Activity Detection)
        lip_movement = float(vision_data.get("lip_movement", 0.0))
        presence = float(vision_data.get("human_presence", 0.0))
        
        # 2. VAD (Audio Voice Activity Detection)
        vad_confidence = float(audio_data.get("vad_confidence", 0.0))
        
        # 3. Fusión Multimodal (Anti-Spoofing & Attention)
        voice_focal_match = (presence > 0.5 and lip_movement > 0.3 and vad_confidence > 0.5)
        
        attention_locus = 0.0
        if presence > 0.5:
            # Proportion of speech vs lip sync
            attention_locus = (vad_confidence * 0.7) + (lip_movement * 0.3)
        
        # 4. Social Tension Calculation
        sensory_dissonance = 0.0
        if vad_confidence > 0.8 and lip_movement < 0.2:
             sensory_dissonance = 0.4 # Background speaker / invisible threat

        total_tension = (environmental_stress * 0.5) + (sensory_dissonance * 0.5)

        # Update core state
        self.state.is_user_present = presence > 0.5
        self.state.is_user_speaking = vad_confidence > 0.5
        self.state.confidence = round(0.7 * attention_locus + 0.3 * self.state.confidence, 4)

        return {
            "attention_locus": round(attention_locus, 3),
            "presence_confidence": round(presence, 3),
            "is_focal_address": voice_focal_match,
            "sensory_tension": round(total_tension, 3),
            "cross_modal_trust": 1.0 if voice_focal_match else 0.4
        }

    def push_episode(self, episode: SensoryEpisode):
        """Maintains the circular buffer for sensory history (Copilot)."""
        self.sensory_buffer.append(episode)
        if len(self.sensory_buffer) > 50:
            self.sensory_buffer.pop(0)

    def should_trigger_deliberation(self) -> bool:
        """Determines if the current sensory state warrants a full kernel tick."""
        if self.state.is_user_speaking and (self.state.is_facing_user or self.state.confidence > 0.7):
            return True
        return False

    def fuse_sensory_stream(self, snapshot: SensorSnapshot) -> dict[str, Any]:
        """
        Main fusion entry point for Phase 10.1.
        Merges vision (VVAD) and audio signals to determine attention locus.
        """
        if not snapshot.image_metadata:
            _log.debug("thalamus: skipping fusion, missing image_metadata")
            return {}

        # 1. Vision Logic (VVAD)
        lip_mov = float(snapshot.image_metadata.get("lip_movement", 0.0))
        presence = float(snapshot.image_metadata.get("human_presence", 0.0))
        
        # 2. Audio Logic (VAD)
        audio_spike = float(snapshot.audio_emergency or 0.0)
        
        # 3. Decision Logic: Attention Locus (θ_att)
        attention_locus = (lip_mov * 0.5) + (presence * 0.3) + (audio_spike * 0.2)
        
        # 4. Sensory Tension (δ_tens)
        ambient = float(snapshot.ambient_noise or 0.0)
        sensory_tension = max(0.0, audio_spike - ambient)
        
        # 5. Multimodal Trust (Anti-Spoofing)
        voice_focal_match = (presence > 0.5 and lip_mov > 0.3 and audio_spike > 0.4)
        cross_modal_trust = 1.0 if voice_focal_match else 0.4

        # 6. EMA for Presence
        self._ema_presence = (self._alpha * presence) + ((1.0 - self._alpha) * self._ema_presence)

        # Update internal state
        self.state.is_user_present = self._ema_presence > 0.5
        self.state.is_user_speaking = audio_spike > 0.3 or lip_mov > 0.4
        self.state.confidence = round((attention_locus + self._ema_facing) / 2.0, 4)
        self.state.last_update = time.time()
        
        return {
            "attention_locus": round(attention_locus, 4),
            "sensory_tension": round(sensory_tension, 4),
            "cross_modal_trust": cross_modal_trust,
            "user_activity": "speaking" if self.state.is_user_speaking else "quiet",
            "is_user_present": self.state.is_user_present
        }

    def fuse_signals(
        self,
        vision_data: Dict[str, Any] | None = None,
        audio_data: Dict[str, Any] | None = None,
        environmental_stress: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Fuse raw vision + audio dicts to produce attention and trust signals.

        Expected keys (all optional, default 0.0):
            vision_data: ``lip_movement`` [0-1], ``human_presence`` [0-1]
            audio_data:  ``vad_confidence`` [0-1]

        Returns a dict with:
            is_focal_address   bool   — True when presence + lip + vad all exceed thresholds
            attention_locus    float  — [0, 1] weighted fusion
            sensory_tension    float  — [0, 1] dissonance + environmental stress
            cross_modal_trust  float  — 1.0 if focal, 0.4 if background
        """
        v = vision_data or {}
        a = audio_data or {}

        lip_mov = float(v.get("lip_movement", 0.0))
        presence = float(v.get("human_presence", 0.0))
        vad = float(a.get("vad_confidence", 0.0))

        # Focal address: all three channels must exceed thresholds
        _LIP_THR = 0.3
        _PRES_THR = 0.5
        _VAD_THR = 0.5
        is_focal = presence > _PRES_THR and lip_mov > _LIP_THR and vad > _VAD_THR

        # Attention locus: only meaningful when presence is detected
        if presence <= _PRES_THR:
            attention_locus = 0.0
        else:
            attention_locus = min(1.0, (lip_mov * 0.4) + (presence * 0.3) + (vad * 0.3))

        # Sensory dissonance: high VAD without lip movement or presence
        if presence > _PRES_THR:
            dissonance = max(0.0, vad - lip_mov) * presence
        else:
            dissonance = 0.0

        sensory_tension = min(1.0, dissonance + float(environmental_stress))

        cross_modal_trust = 1.0 if is_focal else 0.4

        # EMA update
        self._ema_presence = self._alpha * presence + (1.0 - self._alpha) * self._ema_presence
        self.state.is_user_present = self._ema_presence > _PRES_THR
        self.state.is_user_speaking = vad > _VAD_THR or lip_mov > _LIP_THR
        self.state.confidence = round((attention_locus + self._ema_facing) / 2.0, 4)
        self.state.last_update = time.time()

        return {
            "is_focal_address": is_focal,
            "attention_locus": round(max(0.0, min(1.0, attention_locus)), 4),
            "sensory_tension": round(max(0.0, min(1.0, sensory_tension)), 4),
            "cross_modal_trust": cross_modal_trust,
        }

    def push_episode(self, episode: Any) -> None:
        """Append a sensory episode to the ring buffer (capped at _SENSORY_BUFFER_MAX)."""
        self.sensory_buffer.append(episode)
        if len(self.sensory_buffer) > self._SENSORY_BUFFER_MAX:
            self.sensory_buffer = self.sensory_buffer[-self._SENSORY_BUFFER_MAX:]

    def get_sensory_summary(self) -> dict[str, Any]:
        """Provides a filtered summary for the Perceptive Lobe."""
        return {
            "attention_confidence": round(self.state.confidence, 4),
            "user_activity": "speaking" if self.state.is_user_speaking else "quiet",
            "posture": "focused" if self.state.is_facing_user else "away",
            "situated_priority": 1.0 if self.should_trigger_deliberation() else 0.2
        }
