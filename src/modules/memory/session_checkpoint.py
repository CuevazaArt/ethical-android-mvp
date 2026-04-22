"""
Session Checkpoint Tracker (formerly Biographic Memory Tracker).
Converts chat turns and executive decisions into basic SQLite/JSON checkpoints.
"""
# Status: SCAFFOLD


from __future__ import annotations

import logging
import asyncio
import time
from typing import TYPE_CHECKING, Any, Optional

from src.settings import kernel_settings

if TYPE_CHECKING:
    from src.kernel_lobes.models import MotorCommandDispatch
    from src.modules.memory.narrative import NarrativeChronicle, NarrativeMemory

_log = logging.getLogger(__name__)


class SessionCheckpointTracker:
    """
    Subsystem that monitors the nervous system outcomes and promotes them
    to basic session checkpoints in the NarrativeMemory (no vector embeddings).
    """

    def __init__(self, memory: NarrativeMemory):
        self.memory = memory
        self._sleep_active: bool = False

    def register_dispatch(
        self, dispatch: MotorCommandDispatch, context_data: dict[str, Any] | None = None
    ):
        """
        Converts a MotorCommandDispatch into a NarrativeEpisode.
        """
        try:
            # Extract metadata from context if available
            ctx = context_data or {}
            user_input = ctx.get("text", "Unknown stimulus")

            # Determine ethical score and significance
            is_blocked = getattr(dispatch, "is_vetoed", False)
            score = -0.95 if is_blocked else 0.5
            mode = "D_veto" if is_blocked else "D_nomad"

            # Register in NarrativeMemory
            self.memory.register(
                place="Nervous Hub",
                description=f"Stimulus: {user_input[:100]}",
                action=dispatch.action_id,
                morals={"sovereignty": "active", "safety": "vetoed" if is_blocked else "pass"},
                verdict="Ethical Guard Active" if is_blocked else "Distributed Convergence",
                score=score,
                mode=mode,
                sigma=0.5,  # Baseline arousal for chat
                context="conversational_biography",
            )
            _log.info(
                "SessionCheckpointTracker: Event %s promoted to narrative episode.",
                dispatch.ref_pulse_id,
            )
            # Phase 23: Trigger limbic sleep if memory exceeds constraints
            self._check_limbic_sleep()
        except Exception as e:
            _log.error("BiographicMemoryTracker: Promotion failed: %s", e)

    def _check_limbic_sleep(self):
        """
        Checks if episodes exceed localized bounds (1.5B hardware constraint).
        Triggers async consolidation if true.
        """
        if self._sleep_active:
            return
            
        st = kernel_settings()
        max_episodes = 50 if st.kernel_nomad_mode else 500
        
        if len(self.memory.episodes) > max_episodes:
            self._sleep_active = True
            _log.info("BiographicMemoryTracker: Memory limit reached (%d/%d). Initiating Limbic Sleep.", len(self.memory.episodes), max_episodes)
            try:
                loop = asyncio.get_running_loop()
                limit_to_prune = max(10, max_episodes // 2)
                loop.create_task(self._limbic_sleep_async(limit=limit_to_prune))
            except RuntimeError:
                # No event loop available
                self._sleep_active = False

    async def _limbic_sleep_async(self, limit: int):
        """Asynchronously consolidates memories into a chronicle."""
        try:
            chronicle = await self.memory.consolidate_to_chronicle(limit=limit)
            if chronicle:
                _log.info("BiographicMemoryTracker: Limbic sleep completed. Pruned %d episodes.", limit)
                self._calibrate_identity(chronicle)
        except Exception as e:
            _log.error("BiographicMemoryTracker: Limbic sleep failed: %s", e)
        finally:
            self._sleep_active = False

    def _calibrate_identity(self, chronicle: 'NarrativeChronicle'):
        """
        Dynamic Identity Consolidation (Task 23.2).
        Calibrates the agent's narrative backstory based on recent chronicles.
        """
        try:
            from src.persistence.identity_manifest import IdentityManifestStore
            store = IdentityManifestStore()
            manifest = store.manifest
            
            summary_lower = str(chronicle.ethical_poles_summary).lower()
            update_text = ""
            
            if "safety" in summary_lower:
                update_text = " [Recently adopted a highly cautious posture.]"
            elif "sovereignty" in summary_lower:
                update_text = " [Recently exercised strong autonomy.]"
            elif "care" in summary_lower or "compassion" in summary_lower:
                update_text = " [Recently prioritized empathic responses.]"
                
            if update_text and update_text not in manifest.narrative_backstory:
                # Keep backstory concise to enforce nomadic brevity
                if len(manifest.narrative_backstory) < 300:
                    manifest.narrative_backstory += update_text
                    store.save()
                    _log.info("BiographicMemoryTracker: Identity dynamically calibrated post-sleep.")
        except Exception as e:
            _log.error("BiographicMemoryTracker: Failed to calibrate identity: %s", e)
