"""
Memory Hygiene — Services for pruning, amnesia, and biographic maintenance.

Consolidates Selective Amnesia (Right to be Forgotten) and Biographic Pruning.
"""
# Status: SCAFFOLD

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.modules.cognition.llm_layer import LLMModule
    from src.modules.governance.dao_orchestrator import DAOOrchestrator
    from src.modules.memory.narrative import NarrativeMemory

_log = logging.getLogger(__name__)


class MemoryHygieneService:
    """
    Coordinates the permanent removal and consolidation of historical data.
    """

    def __init__(
        self,
        memory: NarrativeMemory,
        dao: DAOOrchestrator,
        retention_days: int = 60,
        min_flashbulb_significance: float = 0.7,
    ):
        self.memory = memory
        self.dao = dao
        self.retention_days = retention_days
        self.min_flashbulb_significance = min_flashbulb_significance

    def forget_episode(self, episode_id: str) -> bool:
        """
        Triggers a cascading deletion of all data related to the episode.
        """
        _log.info("MemoryHygiene: Triggering Right to be Forgotten for episode %s", episode_id)

        # 1. Delete from Narrative Persistence
        narrative_deleted = self.memory.persistence.delete_episode(episode_id)

        # 2. Sync in-memory list
        self.memory.episodes = [ep for ep in self.memory.episodes if ep.id != episode_id]

        # 3. Delete from Audit Ledger (DAO)
        audit_deleted_count = self.dao.delete_records_by_episode(episode_id)

        # 4. Success verification
        success = narrative_deleted or (audit_deleted_count > 0)

        # 5. Re-trigger Identity Reflection
        self.memory.consolidate()

        return success

    def forget_context(self, context_type: str) -> int:
        """Forget all episodes matching a specific context."""
        target_ids = [ep.id for ep in self.memory.episodes if ep.context == context_type]
        count = 0
        for eid in target_ids:
            if self.forget_episode(eid):
                count += 1
        return count

    def run_maintenance_cycle(self, memory: Any | None = None) -> dict[str, Any]:
        """
        Back-compat API for removed ``BiographicPruner`` (legacy kernel / tests).

        ``memory`` is ignored: this service is already bound to the live ``NarrativeMemory``.
        """
        _ = memory
        return self.run_pruning_cycle(None)

    def run_pruning_cycle(self, llm: LLMModule | None = None) -> dict[str, Any]:
        """
        Manages database growth by deleting low-significance episodes.
        """
        _log.info("MemoryHygiene: Starting pruning cycle.")

        # 1. Fetch prunable episodes
        prunable = self.memory.persistence.get_prunable_episodes(
            max_age_days=self.retention_days, min_significance=self.min_flashbulb_significance
        )

        summary_episode_id = None
        if prunable and llm:
            # 2. Generate compression summary (archetypal distillation)
            summary_text = self._generate_compression_summary(prunable, llm)

            from src.modules.memory.narrative_types import BodyState

            sum_ep = self.memory.register(
                place="System Maintenance",
                description=f"Biographic Compression: {summary_text}",
                action="compress_memory",
                morals={},
                verdict="neutral",
                score=0.0,
                mode="D_fast",
                sigma=0.5,
                context="maintenance",
                body_state=BodyState(energy=1.0, active_nodes=8, sensors_ok=True),
                significance_override=0.75,
                is_sensitive_override=False,
            )
            summary_episode_id = sum_ep.id

        # 3. Prune mundane episodes from persistence
        deleted_count = self.memory.persistence.prune_mundane(
            max_age_days=self.retention_days, min_significance=self.min_flashbulb_significance
        )

        return {
            "deleted_episodes": deleted_count,
            "compressed_to_summary_id": summary_episode_id,
            "retention_policy_days": self.retention_days,
            "flashbulb_threshold": self.min_flashbulb_significance,
        }

    def _generate_compression_summary(self, episodes: list[Any], llm: LLMModule) -> str:
        """Distill mundane experiences into a single archetypal insight."""
        texts = [
            f"- {ep.timestamp}: {ep.event_description} ({ep.action_taken})" for ep in episodes[:10]
        ]
        prompt = (
            "Distill the following mundane experiences into a single archetypal insight for the android's narrative identity:\n\n"
            + "\n".join(texts)
        )
        if len(episodes) > 10:
            prompt += f"\n...and {len(episodes) - 10} more similar events."

        response = llm.perceive(prompt, conversation_context="Maintenance")
        return (
            response.summary
            if hasattr(response, "summary")
            else "Daily routines and minor interactions processed."
        )
