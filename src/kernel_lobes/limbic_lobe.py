from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from src.kernel_lobes.models import EthicalSentence, LimbicStageResult, SemanticState
from src.kernel_lobes.signal_coercion import safe_signal_scalar

if TYPE_CHECKING:
    from src.modules.locus import LocusModule
    from src.modules.multimodal_trust import MultimodalAssessment
    from src.modules.sensor_contracts import SensorSnapshot
    from src.modules.sympathetic import SympatheticModule
    from src.modules.uchi_soto import UchiSotoModule


class LimbicEthicalLobe:
    """
    Subsystem for Social (Uchi-Soto), Internal State (Sympathetic), and Locus of Control.
    
    Acts as the 'Right Hemisphere' of the kernel, handling CPU-bound emotional 
    and relational context. No network I/O here (Phase-8 strict separation).
    """
    def __init__(
        self,
        uchi_soto: Optional["UchiSotoModule"] = None,
        sympathetic: Optional["SympatheticModule"] = None,
        locus: Optional["LocusModule"] = None,
        swarm: Any = None,
    ) -> None:
        if uchi_soto is None:
            from src.modules.uchi_soto import UchiSotoModule

            uchi_soto = UchiSotoModule()
        if sympathetic is None:
            from src.modules.sympathetic import SympatheticModule

            sympathetic = SympatheticModule()
        if locus is None:
            from src.modules.locus import LocusModule

            locus = LocusModule()
        self.uchi_soto = uchi_soto
        self.sympathetic = sympathetic
        self.locus = locus
        self.swarm = swarm

    def judge(self, state: SemanticState) -> EthicalSentence:
        """V1.5 lab path: map timeout trauma into limbic tension (see ``tests/test_kernel_lobes_stack``)."""
        if state.timeout_trauma is None:
            return EthicalSentence(
                is_safe=True,
                social_tension_locus=0.0,
                applied_trauma_weight=0.0,
            )
        t = state.timeout_trauma
        sev = max(0.0, min(1.0, float(t.severity)))
        tension = min(1.0, 0.5 + sev * 0.4)
        trauma_w = min(1.0, 0.3 + sev * 0.5)
        return EthicalSentence(
            is_safe=True,
            social_tension_locus=tension,
            applied_trauma_weight=trauma_w,
        )

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
        
        # 3. Swarm Nudge (non-finite / non-numeric nudges are ignored; see signal_coercion)
        if self.swarm:
            try:
                raw = self.swarm.get_swarm_trust_nudge()
            except (TypeError, ValueError, AttributeError):
                nudge = 0.0
            else:
                nudge = safe_signal_scalar(raw, 0.0)
            if nudge > 0.0:
                signals["trust"] = max(0.0, min(1.0, signals.get("trust", 0.5) + nudge))
                
        # 4. Evaluations
        social_eval = self.uchi_soto.evaluate_interaction(signals, agent_id, message_content)
        
        # Inject somatic tension into social evaluation
        if hasattr(social_eval, "relational_tension"):
            social_eval.relational_tension = max(0.0, min(1.0, social_eval.relational_tension + somatic_tension))

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
            locus_evaluation=locus_eval
        )

    async def execute_swarm_consensus_stage(self, **kwargs: object) -> None:
        """Stub until LAN swarm consensus is wired to the limbic stack."""
        return None
