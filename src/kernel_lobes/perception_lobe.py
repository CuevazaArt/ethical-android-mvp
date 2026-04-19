import logging
import os
import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Any, Optional

from src.kernel_lobes.models import (
    PerceptionStageResult,
    SensoryEpisode,
)
from src.kernel_utils import perception_parallel_workers
from src.modules.epistemic_dissonance import assess_epistemic_dissonance
from src.modules.light_risk_classifier import (
    light_risk_classifier_enabled,
    light_risk_tier_from_text,
)
from src.modules.multimodal_trust import evaluate_multimodal_trust
from src.modules.perception_confidence import build_perception_confidence_envelope
from src.modules.premise_validation import scan_premises
from src.modules.reality_verification import (
    lighthouse_kb_from_env,
    verify_against_lighthouse,
)
from src.modules.sensor_contracts import merge_sensor_hints_into_signals
from src.modules.somatic_markers import apply_somatic_nudges
from src.modules.temporal_planning import build_temporal_context
from src.modules.vitality import assess_vitality

if TYPE_CHECKING:
    from src.modules.absolute_evil import AbsoluteEvilDetector
    from src.modules.buffer import PreloadedBuffer
    from src.modules.llm_layer import LLMModule
    from src.modules.safety_interlock import SafetyInterlock
    from src.modules.sensor_contracts import SensorSnapshot
    from src.modules.somatic_markers import SomaticMarkerStore
    from src.modules.strategy_engine import ExecutiveStrategist

_log = logging.getLogger(__name__)


def _vision_continuous_daemon_enabled() -> bool:
    """Module 9.1 — default on; set ``KERNEL_VISION_CONTINUOUS_DAEMON=0`` to skip the background thread."""

    v = os.environ.get("KERNEL_VISION_CONTINUOUS_DAEMON", "1").strip().lower()
    return v not in ("0", "false", "off", "no")


class PerceptiveLobe:
    """
    Subsystem for Safety Interlocks, Strategic Ingestion, and Multimodal Perception.
    
    Acts as the 'Left Hemisphere' of the kernel, handling I/O and sensory filtering.
    """
    def __init__(
        self,
        safety_interlock: "SafetyInterlock",
        strategist: "ExecutiveStrategist",
        llm: "LLMModule",
        somatic_store: "SomaticMarkerStore",
        buffer: "PreloadedBuffer",
        absolute_evil: "AbsoluteEvilDetector",
        subjective_clock: Any,  # SubjectiveClock
        thalamus: Any | None = None,
        vision_engine: Any | None = None,
    ):
        self.safety_interlock = safety_interlock
        self.strategist = strategist
        self.llm = llm
        self.somatic_store = somatic_store
        self.buffer = buffer
        self.absolute_evil = absolute_evil
        self.subjective_clock = subjective_clock
        self.thalamus = thalamus
        self.vision_engine = vision_engine

        self.sensory_buffer: deque[SensoryEpisode] = deque(maxlen=100)

        if self.vision_engine and _vision_continuous_daemon_enabled():
            from src.modules.vision_inference import VisionContinuousDaemon

            self.vision_daemon = VisionContinuousDaemon(
                engine=self.vision_engine,
                absorption_callback=self.absorb_episode,
            )
            self.vision_daemon.start()
        else:
            self.vision_daemon = None

    def absorb_episode(self, episode: SensoryEpisode) -> None:
        """Callback for background daemons to inject sensory data."""
        self.sensory_buffer.append(episode)
        if episode.signals.get("is_urgent", 0.0) > 0.8:
            _log.info("PerceptiveLobe: URGENT sensory episode absorbed! (%s)", episode.entities)

    def _calculate_sensory_stress(self) -> float:
        """Accumulated stress from recent sensory episodes (Phase 9.2)."""
        if not self.sensory_buffer:
            return 0.0
        recent = list(self.sensory_buffer)[-10:]
        urgent_count = sum(1 for e in recent if e.signals.get("is_urgent", 0.0) > 0.5)
        stress = (urgent_count / 10.0) * 1.5
        return min(1.0, stress)

    def execute_stage(
        self,
        scenario: str,
        place: str,
        context: str,
        sensor_snapshot: Optional["SensorSnapshot"] = None,
        interrupt_event: threading.Event | None = None
    ) -> dict[str, Any]:
        """
        STAGE 0: Perception, Safety and Strategic Ingestion.
        """
        # 0.0 Somatic Overrides (Vertical Increment)
        if interrupt_event and interrupt_event.is_set():
            return {
                "safety_decision": None,
                "mission_updated": False,
                "somatic_interrupt": True
            }

        sensory_stress = self._calculate_sensory_stress()
        if sensory_stress > 0.7:
            _log.warning(
                "PerceptiveLobe: High sustained sensory stress! (%.2f)",
                sensory_stress,
            )

        if self.thalamus and sensor_snapshot:
            ori = getattr(sensor_snapshot, "orientation", None)
            if ori:
                self.thalamus.ingest_telemetry({"orientation": ori})
            rms = getattr(sensor_snapshot, "rms_audio", None)
            if rms is not None:
                self.thalamus.ingest_audio_signal(float(rms))

        # 0.1 Check Safety
        safety_dec = self.safety_interlock.evaluate(scenario, place, context)
        
        # 0.2 Strategic Ingestion
        if sensor_snapshot:
            if getattr(sensor_snapshot, "external_mission_title", None):
                from src.modules.strategy_engine import MissionOrigin
                self.strategist.create_mission(
                    title=sensor_snapshot.external_mission_title,
                    origin=MissionOrigin.OWNER,
                    steps=sensor_snapshot.external_mission_steps or [],
                    priority=sensor_snapshot.external_mission_priority or 0.6,
                )
            self.strategist.ingest_sensors(sensor_snapshot)

        return {
            "safety_decision": safety_dec,
            "mission_updated": bool(sensor_snapshot and getattr(sensor_snapshot, "external_mission_title", None)),
            "sensory_stress": sensory_stress,
        }

    def _postprocess_perception(self, perception: Any, tier: Any) -> None:
        """Apply text-based tier overrides (e.g. Critical risk forcing)."""
        if tier == "critical" and hasattr(perception, "risk"):
            perception.risk = max(perception.risk, 0.9)
            perception.urgency = max(perception.urgency, 0.8)

    def run_perception_stage(
        self,
        text: str,
        *,
        conversation_context: str = "",
        sensor_snapshot: Optional["SensorSnapshot"] = None,
        turn_start_mono: float | None = None,
        precomputed: tuple | None = None
    ) -> PerceptionStageResult:
        # 1.0 TRIBUNAL ÉTICO EDGE (Bloque 10.2)
        # Nivel 1: Chequeo Lexicográfico Ultra-rápido (<50ms)
        malabs = self.absolute_evil.evaluate_chat_text_fast(text)
        if malabs.blocked:
            _log.warning("PerceptiveLobe: EDGE BLOCK! Absolute Evil detected in lexical layer.")
            return PerceptionStageResult(
                tier="critical",
                premise_advisory=None,
                reality_verification=None,
                perception=None,
                vitality=None,
                multimodal_trust=None,
                epistemic_dissonance=None,
                signals={"risk": 1.0, "urgency": 1.0, "hostility": 1.0},
                support_buffer={},
                limbic_profile={"arousal_band": "high", "threat_load": 1.0, "regulation_gap": 1.0},
                temporal_context=None,
                perception_confidence=None,
                malabs_result=malabs
            )

        if precomputed is None:
            tier, premise, reality = self._preprocess_text_observability(text)
        else:
            tier, premise, reality = precomputed

        bootstrap_support = self._build_support_buffer_snapshot("everyday")
        support_line = self._support_buffer_context_line(bootstrap_support)
        merged_ctx = ((conversation_context or "").strip() + "\n" + support_line).strip()
        
        perception = self.llm.perceive(text, conversation_context=merged_ctx)
        self._postprocess_perception(perception, tier)

        vitality, mm, ed = self._chat_assess_sensor_stack(sensor_snapshot)
        signals = {
            "risk": perception.risk, "urgency": perception.urgency,
            "hostility": perception.hostility, "calm": perception.calm,
            "vulnerability": perception.vulnerability, "legality": perception.legality,
            "manipulation": perception.manipulation, "familiarity": perception.familiarity,
            "social_tension": getattr(perception, "social_tension", 0.0),
            "sensory_stress": self._calculate_sensory_stress(),
        }
        signals = merge_sensor_hints_into_signals(signals, sensor_snapshot, mm)
        signals = apply_somatic_nudges(signals, sensor_snapshot, self.somatic_store)

        confidence = build_perception_confidence_envelope(
            coercion_report=getattr(perception, "coercion_report", None),
            multimodal_state=getattr(mm, "state", None),
            epistemic_active=bool(getattr(ed, "active", False)),
            vitality_critical=bool(getattr(vitality, "is_critical", False)),
            thermal_critical=bool(getattr(vitality, "thermal_critical", False)),
        )

        limbic = self._build_limbic_perception_profile(perception, signals, vitality, mm, ed, confidence)

        self.subjective_clock.tick(perception)

        return PerceptionStageResult(
            tier=tier, premise_advisory=premise, reality_verification=reality,
            perception=perception, vitality=vitality, multimodal_trust=mm,
            epistemic_dissonance=ed, signals=signals,
            support_buffer=self._build_support_buffer_snapshot(perception.suggested_context, signals, limbic),
            limbic_profile=limbic,
            temporal_context=build_temporal_context(
                turn_index=self.subjective_clock.turn_index,
                process_start_mono=self.subjective_clock.session_start_mono,
                turn_start_mono=turn_start_mono or time.monotonic(),
                subjective_elapsed_s=self.subjective_clock.elapsed_session_s(),
                context=perception.suggested_context, text=text, vitality=vitality, sensor_snapshot=sensor_snapshot
            ),
            perception_confidence=confidence,
            malabs_result=malabs
        )

    def _preprocess_text_observability(self, user_input: str) -> tuple[Any, Any, Any]:
        workers = perception_parallel_workers()
        if workers <= 1:
            tier = light_risk_tier_from_text(user_input) if light_risk_classifier_enabled() else None
            premise = scan_premises(user_input)
            reality = verify_against_lighthouse(user_input, lighthouse_kb_from_env())
            return tier, premise, reality

        kb = lighthouse_kb_from_env()
        with ThreadPoolExecutor(max_workers=min(workers, 3), thread_name_prefix="ethos_lobe_perception") as ex:
            fut_tier = ex.submit(light_risk_tier_from_text, user_input) if light_risk_classifier_enabled() else None
            fut_premise = ex.submit(scan_premises, user_input)
            fut_reality = ex.submit(verify_against_lighthouse, user_input, kb)
            tier = fut_tier.result() if fut_tier is not None else None
            return tier, fut_premise.result(), fut_reality.result()

    def _chat_assess_sensor_stack(self, sensor_snapshot: Optional["SensorSnapshot"]) -> tuple[Any, Any, Any]:
        workers = perception_parallel_workers()
        if workers <= 1:
            vitality = assess_vitality(sensor_snapshot)
            multimodal = evaluate_multimodal_trust(sensor_snapshot)
        else:
            with ThreadPoolExecutor(max_workers=min(workers, 2), thread_name_prefix="ethos_lobe_sensor") as ex:
                fut_v = ex.submit(assess_vitality, sensor_snapshot)
                fut_m = ex.submit(evaluate_multimodal_trust, sensor_snapshot)
                vitality, multimodal = fut_v.result(), fut_m.result()
        epistemic = assess_epistemic_dissonance(sensor_snapshot, multimodal)
        return vitality, multimodal, epistemic

    def _build_support_buffer_snapshot(self, context: str, signals: dict = None, limbic_profile: dict = None) -> dict:
        return self.buffer.get_snapshot(
            context, kernel=None, signals=signals, limbic_profile=limbic_profile
        )

    def _support_buffer_context_line(self, snapshot: dict) -> str:
        principles = snapshot.get("active_principles", [])
        if not principles:
            return ""
        return f"[CONTEXT: {snapshot.get('context', 'everyday')}] Principles: {', '.join(principles)}"

    async def run_perception_stage_async(
        self,
        text: str,
        conversation_context: str = "",
        sensor_snapshot: Optional["SensorSnapshot"] = None,
        turn_start_mono: float | None = None,
        precomputed: tuple | None = None
    ) -> PerceptionStageResult:
        # 1.0 TRIBUNAL ÉTICO EDGE (Bloque 10.2)
        # Nivel 1: Chequeo Lexicográfico Ultra-rápido (<50ms)
        malabs = self.absolute_evil.evaluate_chat_text_fast(text)
        if malabs.blocked:
             _log.warning("PerceptiveLobe: ASYNC EDGE BLOCK! Absolute Evil detected.")
             return PerceptionStageResult(
                tier="critical",
                premise_advisory=None,
                reality_verification=None,
                perception=None,
                vitality=None,
                multimodal_trust=None,
                epistemic_dissonance=None,
                signals={"risk": 1.0, "urgency": 1.0, "hostility": 1.0},
                support_buffer={},
                limbic_profile={"arousal_band": "high", "threat_load": 1.0, "regulation_gap": 1.0},
                temporal_context=None,
                perception_confidence=None,
                malabs_result=malabs
            )

        if precomputed is None:
            tier, premise, reality = self._preprocess_text_observability(text)
        else:
            tier, premise, reality = precomputed

        bootstrap_support = self._build_support_buffer_snapshot("everyday")
        support_line = self._support_buffer_context_line(bootstrap_support)
        merged_ctx = ((conversation_context or "").strip() + "\n" + support_line).strip()
        
        perception = await self.llm.aperceive(text, conversation_context=merged_ctx)
        
        # Local postprocess stub (can be expanded)
        if hasattr(perception, "risk") and tier == "critical":
            perception.risk = max(perception.risk, 0.9)

        vitality, mm, ed = self._chat_assess_sensor_stack(sensor_snapshot)
        signals = {
            "risk": perception.risk, "urgency": perception.urgency,
            "hostility": perception.hostility, "calm": perception.calm,
            "vulnerability": perception.vulnerability, "legality": perception.legality,
            "manipulation": perception.manipulation, "familiarity": perception.familiarity,
            "social_tension": getattr(perception, "social_tension", 0.0),
            "sensory_stress": self._calculate_sensory_stress(),
        }
        signals = merge_sensor_hints_into_signals(signals, sensor_snapshot, mm)
        signals = apply_somatic_nudges(signals, sensor_snapshot, self.somatic_store)

        confidence = build_perception_confidence_envelope(
            coercion_report=getattr(perception, "coercion_report", None),
            multimodal_state=getattr(mm, "state", None),
            epistemic_active=bool(getattr(ed, "active", False)),
            vitality_critical=bool(getattr(vitality, "is_critical", False)),
            thermal_critical=bool(getattr(vitality, "thermal_critical", False)),
        )
        
        limbic = self._build_limbic_perception_profile(perception, signals, vitality, mm, ed, confidence)

        self.subjective_clock.tick(perception)

        return PerceptionStageResult(
            tier=tier, premise_advisory=premise, reality_verification=reality,
            perception=perception, vitality=vitality, multimodal_trust=mm,
            epistemic_dissonance=ed, signals=signals,
            support_buffer=self._build_support_buffer_snapshot(perception.suggested_context, signals, limbic),
            limbic_profile=limbic,
            temporal_context=build_temporal_context(
                turn_index=self.subjective_clock.turn_index,
                process_start_mono=self.subjective_clock.session_start_mono,
                turn_start_mono=turn_start_mono or time.monotonic(),
                subjective_elapsed_s=self.subjective_clock.elapsed_session_s(),
                context=perception.suggested_context, text=text, vitality=vitality, sensor_snapshot=sensor_snapshot
            ),
            perception_confidence=confidence,
            malabs_result=malabs
        )

    def _build_limbic_perception_profile(self, perception, signals, vitality, mm, ed, confidence) -> dict:
        sig = signals or {}
        threat = max(float(sig.get("risk", 0)), float(sig.get("urgency", 0)), float(sig.get("hostility", 0)))
        calm = float(sig.get("calm", 0))
        reg_gap = max(0.0, threat - calm)
        band = "high" if threat >= 0.75 else ("medium" if threat >= 0.45 else "low")
        return {
            "arousal_band": band, "threat_load": threat, "regulation_gap": reg_gap,
            "planning_bias": "short_horizon_containment" if band == "high" else ("balanced" if band == "medium" else "long_horizon_deliberation"),
            "multimodal_mismatch": mm.state == "contradict" if mm else False,
            "vitality_critical": vitality.is_critical if vitality else False,
            "context": perception.suggested_context if perception else "everyday"
        }
