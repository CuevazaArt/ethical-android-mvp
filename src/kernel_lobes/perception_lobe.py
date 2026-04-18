import time
import threading
import logging
import os
from typing import Any, TYPE_CHECKING, Optional, Tuple, Dict
from concurrent.futures import ThreadPoolExecutor

from src.kernel_lobes.models import SemanticState, TimeoutTrauma, PerceptionStageResult
from src.modules.vitality import assess_vitality
from src.modules.multimodal_trust import evaluate_multimodal_trust
from src.modules.epistemic_dissonance import assess_epistemic_dissonance
from src.kernel_utils import perception_parallel_workers
from src.modules.sensor_contracts import merge_sensor_hints_into_signals
from src.modules.somatic_markers import apply_somatic_nudges
from src.modules.perception_confidence import build_perception_confidence_envelope
from src.modules.temporal_planning import build_temporal_context
from src.modules.light_risk_classifier import (
    light_risk_classifier_enabled,
    light_risk_tier_from_text,
)
from src.modules.premise_validation import scan_premises
from src.modules.reality_verification import (
    verify_against_lighthouse,
    lighthouse_kb_from_env,
)

if TYPE_CHECKING:
    from src.modules.safety_interlock import SafetyInterlock
    from src.modules.strategy_engine import ExecutiveStrategist
    from src.modules.sensor_contracts import SensorSnapshot
    from src.modules.llm_layer import LLMModule
    from src.modules.somatic_markers import SomaticMarkerStore
    from src.modules.buffer import PreloadedBuffer
    from src.modules.absolute_evil import AbsoluteEvilDetector

_log = logging.getLogger(__name__)


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
        subjective_clock: Any # SubjectiveClock
    ):
        self.safety_interlock = safety_interlock
        self.strategist = strategist
        self.llm = llm
        self.somatic_store = somatic_store
        self.buffer = buffer
        self.absolute_evil = absolute_evil
        self.subjective_clock = subjective_clock

    def execute_stage(
        self,
        scenario: str,
        place: str,
        context: str,
        sensor_snapshot: Optional["SensorSnapshot"] = None,
        interrupt_event: Optional[threading.Event] = None
    ) -> Dict[str, Any]:
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
            "mission_updated": bool(sensor_snapshot and getattr(sensor_snapshot, "external_mission_title", None))
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
        turn_start_mono: Optional[float] = None,
        precomputed: Optional[tuple] = None
    ) -> PerceptionStageResult:
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
            perception_confidence=confidence
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
        return self.buffer.get_snapshot(context, kernel=None, signals=signals, limbic_profile=limbic_profile)

    def _support_buffer_context_line(self, snapshot: dict) -> str:
        principles = snapshot.get("active_principles", [])
        if not principles: return ""
        return f"[CONTEXT: {snapshot.get('context', 'everyday')}] Principles: {', '.join(principles)}"

    async def run_perception_stage_async(
        self,
        text: str,
        conversation_context: str = "",
        sensor_snapshot: Optional["SensorSnapshot"] = None,
        turn_start_mono: Optional[float] = None,
        precomputed: Optional[tuple] = None
    ) -> PerceptionStageResult:
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
            perception_confidence=confidence
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
