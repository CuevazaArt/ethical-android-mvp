"""
Selective Amnesia Service (Block 5.1: G4).
Implements the "Right to be Forgotten" for ethical kernels.
Allows permanent deletion of specific episodes and their associated audit evidence.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..kernel import EthicalKernel


class SelectiveAmnesia:
    """
    Coordinates the permanent removal of historical data across all layers:
    1. Episodic Narrative (Tier 2/3)
    2. Audit Ledger (OGA/DAO)
    3. Memory Index (Identity Reflection)
    """

    def __init__(self, kernel: EthicalKernel):
        self.kernel = kernel

    def forget_episode(self, episode_id: str) -> bool:
        """
        Triggers a cascading deletion of all data related to the episode.
        This is a destructive, irreversible operation.
        """
        print(f"[Amnesia] Triggering Right to be Forgotten for episode {episode_id}...")

        # 1. Delete from Narrative Persistence (Tier 2/3)
        narrative_deleted = self.kernel.memory.persistence.delete_episode(episode_id)

        # 2. Sync in-memory list
        self.kernel.memory.episodes = [
            ep for ep in self.kernel.memory.episodes if ep.id != episode_id
        ]

        # 3. Delete from Audit Ledger (DAO)
        audit_deleted_count = self.kernel.dao.local_dao.delete_records_by_episode(episode_id)

        # 4. Final verification and report
        success = narrative_deleted or (audit_deleted_count > 0)
        if success:
            print(f"[Amnesia] Cascase completed. Audit records purged: {audit_deleted_count}")
        else:
            print(f"[Amnesia] No data found for episode {episode_id}")

        # 5. Re-trigger Identity Reflection to ensure the amnesia is reflected in the self-model
        self.kernel.memory.consolidate()

        return success

    def forget_context(self, context_type: str) -> int:
        """Deletes all episodes belonging to a specific context (e.g., 'private')."""
        target_ids = [ep.id for ep in self.kernel.memory.episodes if ep.context == context_type]
        count = 0
        for eid in target_ids:
            if self.forget_episode(eid):
                count += 1
        return count
