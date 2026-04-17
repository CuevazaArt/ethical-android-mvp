from __future__ import annotations

from src.kernel_lobes.models import EthicalSentence, SemanticState

if TYPE_CHECKING:
    from src.modules.uchi_soto import UchiSotoModule
    from src.modules.sympathetic import SympatheticModule
    from src.modules.locus import LocusModule
    from src.modules.sensor_contracts import SensorSnapshot
    from src.modules.multimodal_trust import MultimodalAssessment

def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


class LimbicEthicalLobe:
    """
    Subsystem for Social (Uchi-Soto), Internal State (Sympathetic), and Locus of Control.
    
    Acts as the 'Right Hemisphere' of the kernel, handling CPU-bound emotional 
    and relational context. No network I/O here (Phase-8 strict separation).
    """
    def __init__(
        self,
        uchi_soto: UchiSotoModule,
        sympathetic: SympatheticModule,
        locus: LocusModule,
        swarm: Any = None,
        oracle: Any = None
    ):
        self.uchi_soto = uchi_soto
        self.sympathetic = sympathetic
        self.locus = locus
        self.swarm = swarm
        self.oracle = oracle

    async def execute_stage(
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
        applied = 0.0
        tension = 0.0
        if state.timeout_trauma is not None:
            tt = state.timeout_trauma
            sev = _clamp01(tt.severity)
            conf = _clamp01(state.perception_confidence)
            # Cooperative I/O failure increases limbic load without veto (stub stack).
            applied = sev * 0.25
            tension = _clamp01(0.55 * sev + 0.45 * (1.0 - conf))
        return EthicalSentence(
            is_safe=True,
            social_tension_locus=tension,
            applied_trauma_weight=applied,
        )
