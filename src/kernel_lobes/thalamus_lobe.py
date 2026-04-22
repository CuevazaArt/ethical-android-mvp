import logging
import math
import random
from typing import TYPE_CHECKING, Any

from src.kernel_lobes.models import (
    GlobalDegradationPulse,
    LimbicTensionAlert,
    RawSensoryPulse,
    SensorySpike,
)
from src.kernel_lobes.thalamus_node import ThalamusNode

if TYPE_CHECKING:
    from src.nervous_system.corpus_callosum import CorpusCallosum

_log = logging.getLogger(__name__)


def _finite_env_stress(raw: Any) -> float:
    try:
        x = float(raw)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(x):
        return 0.0
    return max(0.0, min(1.0, x))


class ThalamusLobe:
    """
    Thalamus Lobe — The Gateway of Consciousness (Ethos V13.0).

    Acts as a high-frequency filter (Gateway) for the asynchronous nervous system.
    Processes RawSensoryPulses through a biological model (ThalamusNode) and only
    promotes significant stimuli to the rest of the cortex.
    """

    def __init__(self, bus: "CorpusCallosum"):
        self.bus = bus
        self.node = ThalamusNode()
        self._running = False
        self._degradation = 0.0

        self.bus.subscribe(RawSensoryPulse, self._handle_raw_pulse)
        self.bus.subscribe(GlobalDegradationPulse, self._handle_degradation)

        self.bus.set_ingress_gate(self.can_conscious_access)

        _log.info("ThalamusLobe: Sensory Gateway initialized and gated.")

    def can_conscious_access(self, pulse: Any) -> bool:
        """
        Ingress Gate for the CorpusCallosum.
        Blocks high-frequency noise (RawSensoryPulse) if it doesn't meet the conscious threshold.
        """
        if not isinstance(pulse, RawSensoryPulse):
            return True

        if self._degradation > 0.8 and getattr(pulse, "priority", 2) > 0:
            return False

        if self._degradation > 0.5 and getattr(pulse, "priority", 2) == 2:
            return random.random() > 0.5

        return True

    async def _handle_degradation(self, pulse: GlobalDegradationPulse) -> None:
        """Reactor for global system stress."""
        try:
            d = float(pulse.degradation_factor)
        except (TypeError, ValueError):
            d = 0.0
        self._degradation = d if math.isfinite(d) else 0.0
        self._degradation = max(0.0, min(1.0, self._degradation))
        _log.debug("ThalamusLobe: Throttling variable updated to %.2f", self._degradation)

    async def _handle_raw_pulse(self, pulse: RawSensoryPulse) -> None:
        """The Filter Mechanism."""
        if not pulse.payload:
            return

        payload = pulse.payload

        if "orientation" in payload:
            self.node.ingest_telemetry(payload)

        if "rms_audio" in payload:
            self.node.ingest_audio_signal(payload["rms_audio"])

        fusion = self.node.fuse_signals(
            vision_data=payload.get("vision", {}),
            audio_data=payload.get("audio", {}),
            environmental_stress=_finite_env_stress(payload.get("environmental_stress", 0.0)),
        )

        base_gate = 0.25
        effective_gate = base_gate + (self._degradation * 0.4)

        has_text = bool(payload.get("text"))

        if has_text or fusion["attention_locus"] > effective_gate or fusion["is_focal_address"]:
            spike = SensorySpike(
                payload={
                    "origin": pulse.origin_lobe,
                    "fusion": fusion,
                    "text": payload.get("text", ""),
                    "agent_id": payload.get("agent_id", "unknown"),
                    "conversation_context": payload.get("conversation_context", ""),
                },
                priority=1,
                origin_lobe="thalamus_gateway",
                ref_pulse_id=pulse.pulse_id,
            )
            await self.bus.publish(spike)

            if fusion["sensory_tension"] > 0.85:
                alert = LimbicTensionAlert(
                    tension_load=fusion["sensory_tension"],
                    priority=0,
                    origin_lobe="thalamus_gateway",
                    ref_pulse_id=pulse.pulse_id,
                )
                await self.bus.publish(alert)

    def ingest_telemetry(self, payload: dict[str, Any]) -> None:
        """Operator / test entry: forward IMU-oriented payloads to :class:`ThalamusNode`."""
        if not isinstance(payload, dict):
            return
        self.node.ingest_telemetry(payload)

    def get_clinical_summary(self) -> dict[str, Any]:
        """Diagnostic snapshot for the dashboard."""
        return {
            "attentional_locus_current": self.node.state.confidence,
            "gate_threshold": 0.25 + (self._degradation * 0.5),
            "is_user_present": self.node.state.is_user_present,
            "is_focal": self.node.state.is_facing_user and self.node.state.is_user_speaking,
        }

    def get_sensory_summary(self) -> dict[str, Any]:
        """
        HUD-facing snapshot (``sensory_tension`` for :mod:`operator_hud`, posture for Nomad tests).
        """
        fusion = self.node.fuse_signals(vision_data={}, audio_data={}, environmental_stress=0.0)
        tension = float(fusion.get("sensory_tension", 0.0))
        if not math.isfinite(tension):
            tension = 0.0
        locus = float(fusion.get("attention_locus", 0.0))
        if not math.isfinite(locus):
            locus = 0.0
        trust = float(fusion.get("cross_modal_trust", 0.5))
        if not math.isfinite(trust):
            trust = 0.5

        st = self.node.state
        if st.is_user_speaking and st.is_facing_user:
            posture = "speaking"
        elif st.is_facing_user or st.confidence > 0.55:
            posture = "engaged"
        else:
            posture = "idle"

        out: dict[str, Any] = dict(self.get_clinical_summary())
        out["sensory_tension"] = max(0.0, min(1.0, tension))
        out["attention_locus"] = max(0.0, min(1.0, locus))
        out["cross_modal_trust"] = max(0.0, min(1.0, trust))
        out["posture"] = posture
        conf = float(st.confidence)
        out["confidence"] = conf if math.isfinite(conf) else 0.0
        return out

    def fuse_sensory_stream(self, snapshot: Any) -> dict[str, Any]:
        """
        Map a :class:`~src.modules.sensor_contracts.SensorSnapshot` (or duck-typed) into
        :meth:`ThalamusNode.fuse_signals` metrics for perception handlers (Bloque 10.1).
        """
        if snapshot is None:
            return dict(
                self.node.fuse_signals(
                    vision_data={},
                    audio_data={},
                    environmental_stress=0.0,
                )
            )

        meta = getattr(snapshot, "image_metadata", None)
        if not isinstance(meta, dict):
            meta = {}

        def _f01(name: str, default: float = 0.0) -> float:
            raw = meta.get(name, default)
            try:
                x = float(raw)
            except (TypeError, ValueError):
                return default
            if not math.isfinite(x):
                return default
            return max(0.0, min(1.0, x))

        vision_data = {
            "lip_movement": _f01("lip_movement", 0.0),
            "human_presence": _f01("human_presence", 0.0),
        }

        vad_raw = getattr(snapshot, "rms_audio", None)
        try:
            vad = float(vad_raw) if vad_raw is not None else 0.0
        except (TypeError, ValueError):
            vad = 0.0
        if not math.isfinite(vad):
            vad = 0.0
        audio_data = {"vad_confidence": max(0.0, min(1.0, vad))}

        stress_raw = getattr(snapshot, "ambient_noise", None)
        try:
            env = float(stress_raw) if stress_raw is not None else 0.0
        except (TypeError, ValueError):
            env = 0.0
        if not math.isfinite(env):
            env = 0.0
        env = max(0.0, min(1.0, env))

        orient = getattr(snapshot, "orientation", None)
        if isinstance(orient, dict):
            self.node.ingest_telemetry({"orientation": orient})

        jerk = getattr(snapshot, "accelerometer_jerk", None)
        temp = getattr(snapshot, "core_temperature", None)
        stress_bits: list[float] = []
        for label, raw in (("jerk", jerk), ("temp", temp)):
            if raw is None:
                continue
            try:
                fv = float(raw)
            except (TypeError, ValueError):
                continue
            if not math.isfinite(fv):
                continue
            if label == "jerk":
                stress_bits.append(min(1.0, fv / 20.0))
            else:
                stress_bits.append(max(0.0, min(1.0, (fv - 35.0) / 50.0)))
        if stress_bits:
            env = max(env, max(0.0, min(1.0, sum(stress_bits) / len(stress_bits))))

        out = self.node.fuse_signals(
            vision_data=vision_data,
            audio_data=audio_data,
            environmental_stress=env,
        )
        return dict(out)
