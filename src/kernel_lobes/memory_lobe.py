from __future__ import annotations
import logging
from typing import Any, TYPE_CHECKING, Optional, Dict

if TYPE_CHECKING:
    from src.modules.narrative import NarrativeMemory
    from src.modules.dao_orchestrator import DAOOrchestrator
    from src.modules.migratory_identity import MigrationHub
    from src.modules.biographic_pruning import BiographicPruner
    from src.modules.weighted_ethics_scorer import EthicsMixtureResult
    from src.modules.sympathetic import InternalState
    from src.modules.uchi_soto import SocialEvaluation
    from src.modules.immortality import ImmortalityProtocol
    from src.modules.selective_amnesia import SelectiveAmnesia

_log = logging.getLogger(__name__)

class MemoryLobe:
    """
    Subsystem for Episodic Memory, DAO Auditing, and Biographic Identity.
    
    Acts as the 'Hippocampus' and 'Long-Term Storage' of the kernel.
    Vertical growth: Includes memory hygiene (Amnesia) and survival (Immortality).
    """
    def __init__(
        self,
        memory: NarrativeMemory,
        dao: DAOOrchestrator,
        migration: MigrationHub,
        biographic_pruner: Optional[BiographicPruner] = None,
        immortality: Optional[ImmortalityProtocol] = None,
        amnesia: Optional[SelectiveAmnesia] = None
    ):
        self.memory = memory
        self.dao = dao
        self.migration = migration
        self.biographic_pruner = biographic_pruner
        self.immortality = immortality
        self.amnesia = amnesia

    async def execute_episodic_stage_async(
        self,
        scenario: str,
        place: str,
        context: str,
        signals: dict,
        state: InternalState,
        social_eval: SocialEvaluation,
        bayes_result: EthicsMixtureResult,
        moral: Any,
        final_action: str,
        final_mode: str,
        affect: Any
    ) -> Optional[str]:
        """
        Async version of episode registration.
        """
        morals_dict = {ev.pole: ev.moral for ev in moral.evaluations}
        
        # 1. Register Episode (Async)
        ep = await self.memory.aregister(
            place=place,
            description=scenario,
            action=final_action,
            morals=morals_dict,
            verdict=moral.global_verdict.value,
            score=moral.total_score,
            mode=final_mode,
            sigma=state.sigma,
            context=context,
            body_state=self.migration.current_body,
            affect_pad=affect.pad if hasattr(affect, "pad") else None,
            affect_weights=affect.weights if hasattr(affect, "weights") else None,
            weights_snapshot=bayes_result.applied_mixture_weights
        )
        
        # 2. Register Audit in DAO (Async)
        await self.dao.aregister_audit("decision", f"{scenario} → {final_action}", episode_id=ep.id)
        
        return ep.id

    def execute_episodic_stage(
        self,
        scenario: str,
        place: str,
        context: str,
        signals: dict,
        state: InternalState,
        social_eval: SocialEvaluation,
        bayes_result: EthicsMixtureResult,
        moral: Any,
        final_action: str,
        final_mode: str,
        affect: Any
    ) -> Optional[str]:
        """
        Sync version of episode registration (legacy/sim compatibility).
        """
        morals_dict = {ev.pole: ev.moral for ev in moral.evaluations}
        
        # 1. Register Episode
        ep = self.memory.register(
            place=place,
            description=scenario,
            action=final_action,
            morals=morals_dict,
            verdict=moral.global_verdict.value,
            score=moral.total_score,
            mode=final_mode,
            sigma=state.sigma,
            context=context,
            body_state=self.migration.current_body,
            affect_pad=affect.pad if hasattr(affect, "pad") else None,
            affect_weights=affect.weights if hasattr(affect, "weights") else None,
            weights_snapshot=bayes_result.applied_mixture_weights
        )
        
        # 2. Register Audit in DAO
        self.dao.register_audit("decision", f"{scenario} → {final_action}", episode_id=ep.id)
        
        return ep.id

    def register_biographic_impact(self, impact: float) -> None:
        """Update biographic identity level."""
        if hasattr(self.memory, "identity") and hasattr(self.memory.identity, "register_episode"):
            self.memory.identity.register_episode(impact)

    def forget_episode(self, episode_id: str) -> bool:
        """Cascading deletion via SelectiveAmnesia."""
        if self.amnesia:
            return self.amnesia.forget_episode(episode_id)
        return False

    def trigger_backup(self, orchestrator: Any) -> Any:
        """Create a complete identity backup."""
        if self.immortality:
            # We pass the orchestrator (or kernel) because immortality needs 
            # to extract state from all modules.
            return self.immortality.backup(orchestrator)
        return None

    def prune_stale_memories(self) -> None:
        if self.biographic_pruner:
            self.biographic_pruner.prune(self.memory)
