from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

from ..modules.kernel_event_bus import KernelEventBus

if TYPE_CHECKING:
    from ..modules.narrative import NarrativeMemory
    from ..modules.dao_orchestrator import DAOOrchestrator
    from ..modules.migratory_identity import MigrationHub
    from ..modules.biographic_pruning import BiographicPruner
    from ..modules.weighted_ethics_scorer import EthicsMixtureResult
    from ..modules.sympathetic import InternalState
    from ..modules.uchi_soto import SocialEvaluation
    from ..modules.immortality import ImmortalityProtocol
    from ..modules.selective_amnesia import SelectiveAmnesia

_log = logging.getLogger(__name__)


class MemoryLobe:
    """
    Episodic memory, DAO audit trail, and biographic identity (hippocampus).

    With :class:`~src.modules.kernel_event_bus.KernelEventBus` (``KERNEL_EVENT_BUS=1``), call
    :meth:`subscribe_to_kernel_event_bus` once from :class:`~src.kernel.EthicalKernel` so OGA SQLite
    structured audits and ``SelectiveAmnesia`` RTBF dispatches stay wired (Tri-lobe Block 26.0).
    """

    __slots__ = (
        "memory",
        "dao",
        "migration",
        "biographic_pruner",
        "immortality",
        "amnesia",
        "_kernel_bus_handlers_registered",
    )

    def __init__(
        self,
        memory: NarrativeMemory,
        dao: DAOOrchestrator,
        migration: MigrationHub,
        biographic_pruner: Optional[BiographicPruner] = None,
        immortality: Optional[ImmortalityProtocol] = None,
        amnesia: Optional[SelectiveAmnesia] = None,
    ):
        self.memory = memory
        self.dao = dao
        self.migration = migration
        self.biographic_pruner = biographic_pruner
        self.immortality = immortality
        self.amnesia = amnesia
        self._kernel_bus_handlers_registered = False

    def subscribe_to_kernel_event_bus(self, bus: KernelEventBus) -> None:
        """Subscribe MemoryLobe handlers: episode OGA bridge, mixture weights, amnesia RTBF."""
        if self._kernel_bus_handlers_registered:
            return
        from ..modules.kernel_event_bus import (
            EVENT_KERNEL_AMNESIA_FORGET_EPISODE,
            EVENT_KERNEL_EPISODE_REGISTERED,
            EVENT_KERNEL_WEIGHTS_UPDATED,
        )

        bus.subscribe(EVENT_KERNEL_EPISODE_REGISTERED, self._bus_on_episode_registered)
        bus.subscribe(EVENT_KERNEL_WEIGHTS_UPDATED, self._bus_on_weights_updated)
        bus.subscribe(EVENT_KERNEL_AMNESIA_FORGET_EPISODE, self._bus_on_amnesia_forget)
        self._kernel_bus_handlers_registered = True
        _log.debug("MemoryLobe subscribed to KernelEventBus (tri-lobe Block 26.0).")

    def _bus_on_episode_registered(self, payload: dict[str, Any]) -> None:
        """Structured OGA SQLite audit after narrative episode commit (complements ``register_audit``)."""
        if not isinstance(payload, dict):
            return
        eid = payload.get("episode_id")
        ep = str(eid).strip() if eid is not None else ""
        if not ep:
            return
        rca = getattr(self.dao, "register_complex_audit", None)
        if not callable(rca):
            return
        try:
            rca(
                "tri_lobe_episode_registered",
                {
                    "scenario": payload.get("scenario"),
                    "place": payload.get("place"),
                    "final_action": payload.get("final_action"),
                    "context": payload.get("context"),
                    "decision_mode": payload.get("decision_mode"),
                    "score": payload.get("score"),
                    "component": "MemoryLobe",
                },
                episode_id=ep,
            )
        except Exception:
            _log.exception("MemoryLobe bus: tri_lobe_episode_registered audit failed")

    def _bus_on_weights_updated(self, payload: dict[str, Any]) -> None:
        """Telemetry when mixture weights move (I2); optional narrative consolidation."""
        if not isinstance(payload, dict):
            return
        rca = getattr(self.dao, "register_complex_audit", None)
        if not callable(rca):
            return
        try:
            rca(
                "tri_lobe_weights_updated",
                {
                    "source": payload.get("source"),
                    "trust": payload.get("trust"),
                    "prior_dim": len(payload.get("prior") or []),
                    "posterior_dim": len(payload.get("posterior") or []),
                    "component": "MemoryLobe",
                },
                episode_id=None,
            )
            self.memory.consolidate()
        except Exception:
            _log.exception("MemoryLobe bus: weights_updated handler failed")

    def _bus_on_amnesia_forget(self, payload: dict[str, Any]) -> None:
        """Bus-dispatched RTBF — single path through ``SelectiveAmnesia``."""
        if not isinstance(payload, dict) or self.amnesia is None:
            return
        eid = payload.get("episode_id")
        if not isinstance(eid, str) or not eid.strip():
            return
        try:
            self.amnesia.forget_episode(eid.strip())
        except Exception:
            _log.exception("MemoryLobe bus: forget_episode failed for %r", eid)

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
        affect: Any,
    ) -> Optional[str]:
        """Register interaction episode and audit trail."""
        morals_dict = {ev.pole: ev.moral for ev in moral.evaluations}

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
            weights_snapshot=bayes_result.applied_mixture_weights,
        )

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
            return self.immortality.backup(orchestrator)
        return None

    def prune_stale_memories(self) -> None:
        if self.biographic_pruner:
            self.biographic_pruner.prune(self.memory)
