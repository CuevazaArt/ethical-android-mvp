"""
Biographic Pruning — Mundane Pruning and Flashbulb Management (Phase 5).

Implements PROPOSAL_005: manages database growth by consolidating or deleting
low-significance episodes while preserving identity-defining memories.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .llm_layer import LLMModule
    from .narrative import NarrativeMemory


class BiographicPruner:
    """
    Cognitive maintenance worker for long-term memory health.
    """

    def __init__(self, retention_days: int = 60, min_flashbulb_significance: float = 0.7):
        self.retention_days = retention_days
        self.min_flashbulb_significance = min_flashbulb_significance

    def run_maintenance_cycle(self, memory: NarrativeMemory, llm: LLMModule | None = None) -> dict:
        """
        Executes a pruning cycle on the persistent storage.
        If an LLM is provided, mundane episodes are summarized into an archetypal
        memory before being permanently deleted.
        """
        # 1. Fetch prunable episodes
        prunable = memory.persistence.get_prunable_episodes(
            max_age_days=self.retention_days, min_significance=self.min_flashbulb_significance
        )

        summary_episode_id = None
        if prunable and llm:
            # 2. Generate compression summary
            summary_text = self._generate_compression_summary(prunable, llm)

            # 3. Register the compression summary as a new high-significance episode

            from .narrative_types import BodyState

            sum_ep = memory.register(
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
                significance_override=0.75,  # Flashbulb memory
                is_sensitive_override=False,
            )
            summary_episode_id = sum_ep.id

        # 4. Prune mundane episodes from persistence
        deleted_count = memory.persistence.prune_mundane(
            max_age_days=self.retention_days, min_significance=self.min_flashbulb_significance
        )

        return {
            "deleted_episodes": deleted_count,
            "compressed_to_summary_id": summary_episode_id,
            "retention_policy_days": self.retention_days,
            "flashbulb_threshold": self.min_flashbulb_significance,
        }

    def _generate_compression_summary(self, episodes: list, llm: LLMModule) -> str:
        """
        Sends a batch of mundane episodes to the LLM for biographic distillation.
        """
        texts = [
            f"- {ep.timestamp}: {ep.event_description} ({ep.action_taken})" for ep in episodes[:10]
        ]
        prompt = (
            "Distill the following mundane experiences into a single archetypal insight for the android's narrative identity:\n\n"
            + "\n".join(texts)
        )
        if len(episodes) > 10:
            prompt += f"\n...and {len(episodes) - 10} more similar events."

        # Simplified call; in a real scenario we'd use a specific distillation prompt
        response = llm.perceive(prompt, conversation_context="Maintenance")
        return (
            response.summary
            if hasattr(response, "summary")
            else "Daily routines and minor interactions processed."
        )

    def simulate_memory_compression(self, memory: NarrativeMemory) -> str:
        """
        Simulates the consolidation of mundane details into the identity state.
        In Phase 5, this is advisory; later it might involve LLM-based summarization.
        """
        mundane = [
            ep for ep in memory.episodes if ep.significance < self.min_flashbulb_significance
        ]
        if len(mundane) > 20:
            return f"Consolidation recommended: {len(mundane)} mundane episodes eligible for biographic compression."
        return "Memory density healthy."
