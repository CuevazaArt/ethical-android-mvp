"""
Selective Amnesia Service (Block 5.1: G4).
Implements the "Right to be Forgotten" for ethical kernels.
"""

from __future__ import annotations
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .narrative import NarrativeMemory
    from .dao_orchestrator import DAOOrchestrator

_log = logging.getLogger(__name__)


class SelectiveAmnesia:
    """
    Coordinates the permanent removal of historical data across all layers.
    """

    def __init__(self, memory: NarrativeMemory, dao: DAOOrchestrator):
        self.memory = memory
        self.dao = dao

    def forget_episode(self, episode_id: str) -> bool:
        """
        Triggers a cascading deletion of all data related to the episode.
        """
        _log.info("Triggering Right to be Forgotten for episode %s", episode_id)

        # 1. Delete from Narrative Persistence
        narrative_deleted = self.memory.persistence.delete_episode(episode_id)

        # 2. Sync in-memory list
        self.memory.episodes = [
            ep for ep in self.memory.episodes if ep.id != episode_id
        ]

        # 3. Delete from Audit Ledger (DAO)
        from .dao_orchestrator import DAOOrchestrator
        mock_face = self.dao.local_dao if isinstance(self.dao, DAOOrchestrator) else self.dao
        audit_deleted_count = mock_face.delete_records_by_episode(episode_id)

        # 4. Success verification
        success = narrative_deleted or (audit_deleted_count > 0)
        
        # 5. Re-trigger Identity Reflection
        self.memory.consolidate()

        return success

    def forget_context(self, context_type: str) -> int:
        target_ids = [ep.id for ep in self.memory.episodes if ep.context == context_type]
        count = 0
        for eid in target_ids:
            if self.forget_episode(eid):
                count += 1
        return count
