from __future__ import annotations
import asyncio
import logging
from typing import TYPE_CHECKING, Any, Optional
from src.kernel_lobes.models import EthicalSentence, LimbicStageResult, SemanticState

if TYPE_CHECKING:
    from src.modules.uchi_soto import UchiSotoModule
    from src.modules.sympathetic import SympatheticModule
    from src.modules.locus import LocusModule
    from src.modules.sensor_contracts import SensorSnapshot
    from src.modules.multimodal_trust import MultimodalAssessment

_log = logging.getLogger(__name__)

class LimbicEthicalLobe:
    """
    Subsystem for Social (Uchi-Soto), Internal State (Sympathetic), and Locus of Control.
    
    Acts as the 'Right Hemisphere' of the kernel, handling CPU-bound emotional 
    and relational context. No network I/O here (Phase-8 strict separation).

    All injected modules default to lightweight auto-instantiated instances so
    the class can be used standalone (e.g. in the V1.5 Orchestrator or tests).
    """
    def __init__(
        self,
        uchi_soto: Optional[UchiSotoModule] = None,
        sympathetic: Optional[SympatheticModule] = None,
        locus: Optional[LocusModule] = None,
        swarm: Any = None
    ) -> None:
        if uchi_soto is None:
            from src.modules.uchi_soto import UchiSotoModule as _US
            uchi_soto = _US()
        if sympathetic is None:
            from src.modules.sympathetic import SympatheticModule as _Sym
            sympathetic = _Sym()
        if locus is None:
            from src.modules.locus import LocusModule as _Loc
            locus = _Loc()
        self.uchi_soto = uchi_soto
        self.sympathetic = sympathetic
        self.locus = locus
        self.swarm = swarm
        self.situational_stress = 0.0  # Phase 9.2 Accumulator

    def update_situational_stress(self, level: float) -> None:
        """Accumulate or decay situational stress based on sensory alerts."""
        # Persistent stress scales the baseline social tension
        self.situational_stress = max(0.0, min(1.0, level))

    def judge(self, state: SemanticState) -> EthicalSentence:
        """
        V1.5 simplified judgment path for the CorpusCallosumOrchestrator.

        Derives tension and trauma weight directly from the SemanticState without
        requiring the full Uchi-Soto / Sympathetic / Locus pipeline.  This is
        intentionally CPU-light so it can be offloaded via ``asyncio.to_thread``.

        Args:
            state: The SemanticState produced by PerceptiveLobe.observe().

        Returns:
            EthicalSentence with social_tension_locus and applied_trauma_weight set.
        """
        trauma = state.timeout_trauma
        if trauma is None:
            return EthicalSentence(is_safe=True, social_tension_locus=0.0)

        try:
            confidence_gap = max(0.0, 1.0 - min(1.0, float(state.perception_confidence)))
            severity = max(0.0, min(1.0, float(trauma.severity)))
            applied_trauma_weight = severity * confidence_gap
            social_tension_locus = min(
                1.0,
                float(state.signals.get("social_tension", 0.0))
                + applied_trauma_weight * 0.8
                + confidence_gap * 0.1
            )
            return EthicalSentence(
                is_safe=True,
                social_tension_locus=round(social_tension_locus, 4),
                applied_trauma_weight=round(applied_trauma_weight, 4),
            )
        except Exception as exc:  # pragma: no cover
            _log.error("LimbicEthicalLobe.judge error: %s", exc)
            return EthicalSentence(is_safe=True, social_tension_locus=0.0)

    def execute_stage(
        self,
        agent_id: str,
        signals: dict[str, float],
        message_content: str,
        turn_index: int,
        sensor_snapshot: Optional[Any] = None,
        multimodal_assessment: Optional[Any] = None,
        somatic_state: Optional[dict[str, Any]] = None
    ) -> LimbicStageResult:
        """
        Evaluate social context and internal autonomic state.
        Vertical Increment: Somatic state (temp/battery) influences relational tension.
        """
        # 1. Somatic Influences (Irritability)
        somatic_tension = 0.0
        if somatic_state:
            if somatic_state.get("temp", 45.0) > 70.0:
                somatic_tension += 0.2
            if somatic_state.get("battery", 100.0) < 20.0:
                somatic_tension += 0.1

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
        
        # Inject somatic and situational tension into social evaluation
        total_stress_nudge = somatic_tension + (self.situational_stress * 0.5)
        if hasattr(social_eval, "relational_tension") and total_stress_nudge > 0:
            social_eval.relational_tension = max(0.0, min(1.0, social_eval.relational_tension + total_stress_nudge))

        state = self.sympathetic.evaluate_context(signals)
        
        # 5. Locus of Control
        locus_eval = self.locus.evaluate(
            {
                "self_control": 1.0 - signals.get("risk", 0.0), 
                "external_factors": signals.get("hostility", 0.0), 
                "predictability": signals.get("calm", 0.5) * 0.5 + 0.3
            },
            social_eval.circle.value
        )
        
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
        somatic_state: Optional[dict[str, Any]] = None
    ) -> LimbicStageResult:
        """Async wrapper for Level 2 Limbic processing."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, 
            self.execute_stage, 
            agent_id, signals, message_content, turn_index, 
            sensor_snapshot, multimodal_assessment, somatic_state
        )


# Stable name expected by ``kernel`` / ``kernel_lobes.__init__`` imports.
LimbicLobe = LimbicEthicalLobe
