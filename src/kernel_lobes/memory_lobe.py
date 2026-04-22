from __future__ import annotations

import logging
import math
import time
from typing import TYPE_CHECKING, Any, Optional

from src.kernel_lobes.models import SemanticState, TimeoutTrauma, MotorCommandDispatch
from src.modules.memory.session_checkpoint import SessionCheckpointTracker

if TYPE_CHECKING:
    from src.nervous_system.corpus_callosum import CorpusCallosum
    from src.modules.governance.dao_orchestrator import DAOOrchestrator
    from src.modules.memory.immortality import ImmortalityProtocol
    from src.modules.cognition.llm_layer import LLMModule
    from src.modules.memory.memory_hygiene import MemoryHygieneService
    from src.modules.memory.migratory_identity import MigrationHub
    from src.modules.memory.narrative import NarrativeMemory
    from src.modules.somatic.sympathetic import InternalState
    from src.modules.social.uchi_soto import SocialEvaluation
    from src.modules.ethics.weighted_ethics_scorer import EthicsMixtureResult

_log = logging.getLogger(__name__)


class MemoryLobe:
    """
    Subsystem for Episodic Memory, DAO Auditing, and Biographic Identity.

    Acts as the 'Hippocampus' and 'Long-Term Storage' of the kernel.
    Vertical growth: Includes memory hygiene (Amnesia/Pruning) and survival (Immortality).
    """

    def __init__(
        self,
        memory: NarrativeMemory,
        dao: DAOOrchestrator,
        migration: MigrationHub,
        hygiene: MemoryHygieneService | None = None,
        immortality: ImmortalityProtocol | None = None,
        llm: LLMModule | None = None,
        bus: 'CorpusCallosum' | None = None,
    ):
        self.memory = memory
        self.dao = dao
        self.migration = migration
        self.hygiene = hygiene
        self.immortality = immortality
        self.llm = llm
        self.bus = bus
        self.tracker = SessionCheckpointTracker(self.memory)

        if self.bus:
            self.bus.subscribe(MotorCommandDispatch, self._on_motor_dispatch)
            _log.info("MemoryLobe: Subscribed to Nervous System Bus.")

    async def _on_motor_dispatch(self, dispatch: MotorCommandDispatch) -> None:
        """Monitor final decisions and promote them to biographic memory via tracker."""
        meta = dispatch.metadata or {}
        self.tracker.register_dispatch(dispatch, context_data=meta)
        
        # Trigger DAO Auditing asynchronously if needed (Task 26.1)
        action_desc = dispatch.action_id
        if getattr(dispatch, "is_vetoed", False):
            action_desc = "VETO"
        
        try:
            # Generate pseudo-episode ID for logging in DAO
            ep_id = f"ep_{dispatch.pulse_id}"
            await self.dao.aregister_audit("motor_dispatch", action_desc, episode_id=ep_id)
        except Exception as e:
            _log.error(f"MemoryLobe DAO audit failed for {dispatch.pulse_id}: {e}")

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
        affect: Any,
    ) -> str | None:
        """
        Async version of episode registration.
        """
        t0 = time.perf_counter()

        # 0. Safety Check
        if not moral or not hasattr(moral, "evaluations") or not bayes_result:
            _log.warning("MemoryLobe: Cannot register episode, missing moral or bayesian result.")
            return None

        try:
            morals_dict = {ev.pole: getattr(ev, "moral", 0.5) for ev in moral.evaluations}

            # 1. Register Episode (Async)
            sigma = float(getattr(state, "sigma", 0.5))
            if not math.isfinite(sigma):
                sigma = 0.5

            score = float(getattr(moral, "total_score", 0.5))
            if not math.isfinite(score):
                score = 0.5

            ep = await self.memory.aregister(
                place=place or "unknown",
                description=scenario or "unnamed_scenario",
                action=final_action or "idle",
                morals=morals_dict,
                verdict=getattr(moral.global_verdict, "value", "Gray Zone")
                if moral.global_verdict
                else "Gray Zone",
                score=score,
                mode=final_mode or "unknown",
                sigma=sigma,
                context=context or "neutral",
                body_state=getattr(self.migration, "current_body", "simulated"),
                affect_pad=affect.pad if hasattr(affect, "pad") else None,
                affect_weights=affect.weights if hasattr(affect, "weights") else None,
                weights_snapshot=getattr(
                    bayes_result, "applied_mixture_weights", (0.33, 0.33, 0.34)
                ),
            )

            # 2. Register Audit in DAO (Async)
            await self.dao.aregister_audit(
                "decision", f"{scenario} → {final_action}", episode_id=ep.id
            )

            latency = (time.perf_counter() - t0) * 1000
            _log.debug("MemoryLobe: Episodic stage (async) took %.2f ms", latency)

            return ep.id

        except Exception as e:
            _log.error("MemoryLobe: Critical error in episodic stage (async): %s", e)
            return None

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
    ) -> str | None:
        """
        Sync version of episode registration (legacy/sim compatibility).
        """
        t0 = time.perf_counter()

        # 0. Safety Check
        if not moral or not hasattr(moral, "evaluations") or not bayes_result:
            return None

        try:
            morals_dict = {ev.pole: getattr(ev, "moral", 0.5) for ev in moral.evaluations}

            # 1. Register Episode
            sigma = float(getattr(state, "sigma", 0.5))
            if not math.isfinite(sigma):
                sigma = 0.5

            score = float(getattr(moral, "total_score", 0.5))
            if not math.isfinite(score):
                score = 0.5

            ep = self.memory.register(
                place=place or "unknown",
                description=scenario or "unnamed_scenario",
                action=final_action or "idle",
                morals=morals_dict,
                verdict=getattr(moral.global_verdict, "value", "Gray Zone")
                if moral.global_verdict
                else "Gray Zone",
                score=score,
                mode=final_mode or "unknown",
                sigma=sigma,
                context=context or "neutral",
                body_state=getattr(self.migration, "current_body", "simulated"),
                affect_pad=affect.pad if hasattr(affect, "pad") else None,
                affect_weights=affect.weights if hasattr(affect, "weights") else None,
                weights_snapshot=getattr(
                    bayes_result, "applied_mixture_weights", (0.33, 0.33, 0.34)
                ),
            )

            # 2. Register Audit in DAO
            self.dao.register_audit("decision", f"{scenario} → {final_action}", episode_id=ep.id)

            latency = (time.perf_counter() - t0) * 1000
            _log.debug("MemoryLobe: Episodic stage (sync) took %.2f ms", latency)

            return ep.id

        except Exception as e:
            _log.error("MemoryLobe: Critical error in episodic stage (sync): %s", e)
            return None

    def register_biographic_impact(self, impact: float) -> None:
        """Update biographic identity level."""
        try:
            if not math.isfinite(impact):
                impact = 0.0
            if hasattr(self.memory, "identity") and hasattr(
                self.memory.identity, "register_episode"
            ):
                self.memory.identity.register_episode(impact)
        except Exception as e:
            _log.error("MemoryLobe: Error in biographic impact: %s", e)

    def forget_episode(self, episode_id: str) -> bool:
        """Cascading deletion via MemoryHygieneService."""
        try:
            if self.hygiene:
                return self.hygiene.forget_episode(episode_id)
        except Exception as e:
            _log.error("MemoryLobe: Error in forget_episode: %s", e)
        return False

    def trigger_backup(self, orchestrator: Any) -> Any:
        """Create a complete identity backup."""
        try:
            if self.immortality:
                return self.immortality.backup(orchestrator)
        except Exception as e:
            _log.error("MemoryLobe: Error in trigger_backup: %s", e)
        return None

    def prune_stale_memories(self) -> None:
        """Prune memories based on hygiene rules."""
        try:
            if self.hygiene:
                self.hygiene.run_pruning_cycle(self.llm)
        except Exception as e:
            _log.error("MemoryLobe: Error in prune_stale_memories: %s", e)
