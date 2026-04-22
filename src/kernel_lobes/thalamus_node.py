"""
Thalamus Node — Sensory routing and gatekeeping logic (Non-Async).
Component of the Phase 10.1 Sensory Fusion.

Provides the mathematical models for VVAD + VAD + IMU fusion,
detecting attentional focus and sensory dissonance.
"""

from __future__ import annotations

import logging
import math
import time
from dataclasses import dataclass, field
from typing import Any

_log = logging.getLogger(__name__)


def _finite_unit(x: Any, default: float = 0.0) -> float:
    """Clamp to [0, 1] after coercing to float; non-finite → ``default``."""

    try:
        v = float(x)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(v):
        return default
    return max(0.0, min(1.0, v))


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
    Biological model for sensory filtering and synchrony.

    Logic:
    - VVAD: Visual Voice Activity Detection (Presence + Lips).
    - VAD: Audio Voice Activity Detection (RMS / Confidence).
    - EMA: Exponential Moving Average for signal smoothing.
    """

    _SENSORY_BUFFER_MAX = 50

    def __init__(self, sensitivity: float = 0.5):
        self.sensitivity = sensitivity
        self.state = AttentionState()
        self.sensory_buffer: list[Any] = []
        self._audio_history: list[float] = []
        self._max_history = 10

        # EMA Smoothing state
        self._ema_facing = 0.0
        self._ema_presence = 0.0
        self._alpha = 0.3  # Smoothing factor (biological persistence)

    def ingest_telemetry(self, payload: dict[str, Any]):
        """Ingests IMU data to update attentional confidence."""
        orientation = payload.get("orientation")
        if orientation and isinstance(orientation, dict):
            # Common smartphone viewing angle (beta between 45 and 105 degrees)
            beta_raw = orientation.get("beta", 0)
            try:
                beta = float(beta_raw)
            except (TypeError, ValueError):
                beta = 0.0
            if not math.isfinite(beta):
                beta = 0.0
            target = 1.0 if (45 < beta < 105) else 0.0

            # Application of EMA for stability
            self._ema_facing = (self._alpha * target) + ((1.0 - self._alpha) * self._ema_facing)
            self.state.is_facing_user = self._ema_facing > 0.6

            if self.state.is_facing_user:
                self.state.confidence = min(1.0, self.state.confidence + 0.05)
            else:
                self.state.confidence = max(0.0, self.state.confidence - 0.02)

        self.state.last_update = time.time()

    def ingest_audio_signal(self, rms: float | None):
        """Processes audio volume spikes for VAD when raw RMS is available."""
        if rms is None:
            return
        try:
            r = float(rms)
        except (TypeError, ValueError):
            return
        if not math.isfinite(r):
            return
        self._audio_history.append(r)
        if len(self._audio_history) > self._max_history:
            self._audio_history.pop(0)

        avg_rms = (
            sum(self._audio_history) / len(self._audio_history) if self._audio_history else 0.0
        )
        if not math.isfinite(avg_rms):
            avg_rms = 0.0
        # Threshold: 150% of background average and minimum absolute floor
        if r > avg_rms * 1.5 and r > 0.03:
            self.state.is_user_speaking = True
            self.state.confidence = min(1.0, self.state.confidence + 0.1)
        else:
            self.state.is_user_speaking = False
            self.state.confidence = max(0.0, self.state.confidence - 0.05)

    def fuse_signals(
        self,
        vision_data: dict[str, Any] | None = None,
        audio_data: dict[str, Any] | None = None,
        environmental_stress: float = 0.0,
    ) -> dict[str, Any]:
        """
        Calculates focal address probability by crossing audio and vision.

        Expected keys (0.0 to 1.0):
            vision_data: [lip_movement, human_presence]
            audio_data:  [vad_confidence]
        """
        v = vision_data or {}
        a = audio_data or {}

        lip_mov = _finite_unit(v.get("lip_movement", 0.0), 0.0)
        presence = _finite_unit(v.get("human_presence", 0.0), 0.0)
        vad = _finite_unit(a.get("vad_confidence", 0.0), 0.0)
        stress = _finite_unit(environmental_stress, 0.0)

        # 1. Focal Address: requires cross-modal intersection
        # Tightly coupled VVAD + VAD
        _LIP_THR = 0.3
        _PRES_THR = 0.5
        _VAD_THR = 0.5
        is_focal = presence > _PRES_THR and lip_mov > _LIP_THR and vad > _VAD_THR

        # 2. Attention Locus (θ_att)
        if presence <= _PRES_THR:
            attention_locus = 0.0
        else:
            # Weighted mix: Lips provide highest address certainty, then VAD
            attention_locus = min(1.0, (lip_mov * 0.5) + (presence * 0.2) + (vad * 0.3))

        # 3. Sensory Dissonance (δ_tens)
        # High audio activity without visual confirmation in an active presence
        dissonance = 0.0
        if presence > _PRES_THR:
            dissonance = max(0.0, vad - lip_mov) * 0.5

        sensory_tension = min(1.0, dissonance + stress)

        # 4. State Updates (EMA)
        self._ema_presence = self._alpha * presence + (1.0 - self._alpha) * self._ema_presence
        self.state.is_user_present = self._ema_presence > _PRES_THR
        self.state.is_user_speaking = vad > _VAD_THR or lip_mov > _LIP_THR

        # Combined confidence from locus and posture
        self.state.confidence = round((attention_locus + self._ema_facing) / 2.0, 4)
        self.state.last_update = time.time()

        return {
            "is_focal_address": is_focal,
            "attention_locus": round(max(0.0, min(1.0, attention_locus)), 4),
            "sensory_tension": round(max(0.0, min(1.0, sensory_tension)), 4),
            "cross_modal_trust": 1.0 if is_focal else 0.4,
            "presence_confidence": round(self._ema_presence, 4),
        }

    def push_episode(self, episode: Any) -> None:
        """Maintenance of the ring buffer for recent sensory memory."""
        self.sensory_buffer.append(episode)
        if len(self.sensory_buffer) > self._SENSORY_BUFFER_MAX:
            self.sensory_buffer = self.sensory_buffer[-self._SENSORY_BUFFER_MAX :]

    def should_trigger_deliberation(self) -> bool:
        """Biological check: should the organism react?"""
        return self.state.is_user_speaking and (
            self.state.is_facing_user or self.state.confidence > 0.6
        )
