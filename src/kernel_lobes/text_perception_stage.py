"""
Text perception stage (Plan 0.1.3 — desmonolitización de ``kernel.py``).

Orchestrates pre-enrichment, ``LLMModule.perceive`` / ``aperceive``, post-perception safeguards,
sensor overlays, limbic snapshot, support buffer, and temporal context. Lives next to other
kernel-lobe policy modules so :class:`~src.kernel.EthicalKernel` stays a coordinator.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from ..modules.perception_confidence import build_perception_confidence_envelope
from ..modules.premise_validation import PremiseAdvisory
from ..modules.reality_verification import RealityVerificationAssessment
from ..modules.sensor_contracts import SensorSnapshot, merge_sensor_hints_into_signals
from ..modules.somatic_markers import apply_somatic_nudges
from ..modules.temporal_planning import build_temporal_context
from .perception_signals_policy import base_signals_from_llm_perception

if TYPE_CHECKING:
    from src.kernel import PerceptionStageResult


class TextPerceptionStageRunner:
    """Runs the shared sync/async perception pipeline against an :class:`~src.kernel.EthicalKernel`."""

    __slots__ = ("_kernel",)

    def __init__(self, kernel: Any) -> None:
        self._kernel = kernel

    def run_sync(
        self,
        text: str,
        *,
        conversation_context: str = "",
        sensor_snapshot: SensorSnapshot | None = None,
        turn_start_mono: float | None = None,
        precomputed: tuple[Any, PremiseAdvisory, RealityVerificationAssessment] | None = None,
    ) -> PerceptionStageResult:
        """
        Blocking perception path (unit tests, :meth:`~src.kernel.EthicalKernel.process_natural`).

        Uses ``LLMModule.perceive``. Import of ``PerceptionStageResult`` is deferred inside the
        method body to avoid circular imports when ``src.kernel`` loads.
        """
        from src.kernel import PerceptionStageResult

        k = self._kernel
        if precomputed is None:
            tier, premise_advisory, reality_assessment = k._preprocess_text_observability(text)
        else:
            tier, premise_advisory, reality_assessment = precomputed

        bootstrap_support = k._build_support_buffer_snapshot("everyday")
        support_line = k._support_buffer_context_line(bootstrap_support)
        merged_context = ((conversation_context or "").strip() + "\n" + support_line).strip()
        perception = k.llm.perceive(text, conversation_context=merged_context)
        k._postprocess_perception(perception, tier)

        vitality, mm, ed = k._chat_assess_sensor_stack(sensor_snapshot)
        signals = base_signals_from_llm_perception(perception)
        signals = merge_sensor_hints_into_signals(signals, sensor_snapshot, mm)
        signals = apply_somatic_nudges(signals, sensor_snapshot, k.somatic_store)

        confidence = build_perception_confidence_envelope(
            coercion_report=getattr(perception, "coercion_report", None),
            multimodal_state=getattr(mm, "state", None),
            epistemic_active=bool(getattr(ed, "active", False)),
            vitality_critical=bool(getattr(vitality, "is_critical", False)),
            thermal_critical=bool(getattr(vitality, "thermal_critical", False)),
            thermal_elevated=bool(getattr(vitality, "thermal_elevated", False)),
        )
        limbic = k._build_limbic_perception_profile(
            perception=perception,
            signals=signals,
            vitality=vitality,
            multimodal=mm,
            epistemic=ed,
            confidence_envelope=confidence,
        )
        contextual_support = k._build_support_buffer_snapshot(
            perception.suggested_context,
            signals=signals,
            limbic_profile=limbic,
        )
        temporal = build_temporal_context(
            turn_index=k.subjective_clock.turn_index,
            process_start_mono=k.subjective_clock.session_start_mono,
            turn_start_mono=turn_start_mono if turn_start_mono is not None else time.monotonic(),
            subjective_elapsed_s=k.subjective_clock.elapsed_session_s(),
            context=perception.suggested_context,
            text=text,
            vitality=vitality,
            sensor_snapshot=sensor_snapshot,
        )
        return PerceptionStageResult(
            tier=tier,
            premise_advisory=premise_advisory,
            reality_verification=reality_assessment,
            perception=perception,
            vitality=vitality,
            multimodal_trust=mm,
            epistemic_dissonance=ed,
            signals=signals,
            support_buffer=contextual_support,
            limbic_profile=limbic,
            temporal_context=temporal,
            perception_confidence=confidence,
        )

    async def run_async(
        self,
        text: str,
        *,
        conversation_context: str = "",
        sensor_snapshot: SensorSnapshot | None = None,
        turn_start_mono: float | None = None,
        precomputed: tuple[Any, PremiseAdvisory, RealityVerificationAssessment] | None = None,
    ) -> PerceptionStageResult:
        """
        Cooperative async path for chat/WebSocket (``LLMModule.aperceive``).

        Deferred import of ``PerceptionStageResult`` — same rationale as :meth:`run_sync`.
        """
        from src.kernel import PerceptionStageResult

        k = self._kernel
        if precomputed is None:
            tier, premise_advisory, reality_assessment = k._preprocess_text_observability(text)
        else:
            tier, premise_advisory, reality_assessment = precomputed

        bootstrap_support = k._build_support_buffer_snapshot("everyday")
        support_line = k._support_buffer_context_line(bootstrap_support)
        merged_context = ((conversation_context or "").strip() + "\n" + support_line).strip()
        perception = await k.llm.aperceive(text, conversation_context=merged_context)
        k._postprocess_perception(perception, tier)

        vitality, mm, ed = k._chat_assess_sensor_stack(sensor_snapshot)
        signals = base_signals_from_llm_perception(perception)
        signals = merge_sensor_hints_into_signals(signals, sensor_snapshot, mm)
        signals = apply_somatic_nudges(signals, sensor_snapshot, k.somatic_store)

        confidence = build_perception_confidence_envelope(
            coercion_report=getattr(perception, "coercion_report", None),
            multimodal_state=getattr(mm, "state", None),
            epistemic_active=bool(getattr(ed, "active", False)),
            vitality_critical=bool(getattr(vitality, "is_critical", False)),
            thermal_critical=bool(getattr(vitality, "thermal_critical", False)),
            thermal_elevated=bool(getattr(vitality, "thermal_elevated", False)),
        )
        limbic = k._build_limbic_perception_profile(
            perception=perception,
            signals=signals,
            vitality=vitality,
            multimodal=mm,
            epistemic=ed,
            confidence_envelope=confidence,
        )
        contextual_support = k._build_support_buffer_snapshot(
            perception.suggested_context,
            signals=signals,
            limbic_profile=limbic,
        )
        temporal = build_temporal_context(
            turn_index=k.subjective_clock.turn_index,
            process_start_mono=k.subjective_clock.session_start_mono,
            turn_start_mono=turn_start_mono if turn_start_mono is not None else time.monotonic(),
            subjective_elapsed_s=k.subjective_clock.elapsed_session_s(),
            context=perception.suggested_context,
            text=text,
            vitality=vitality,
            sensor_snapshot=sensor_snapshot,
        )
        return PerceptionStageResult(
            tier=tier,
            premise_advisory=premise_advisory,
            reality_verification=reality_assessment,
            perception=perception,
            vitality=vitality,
            multimodal_trust=mm,
            epistemic_dissonance=ed,
            signals=signals,
            support_buffer=contextual_support,
            limbic_profile=limbic,
            temporal_context=temporal,
            perception_confidence=confidence,
        )
