from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

_log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from src.modules.cognition.bayesian_engine import BayesianInferenceEngine
    from src.modules.cognition.rlhf_reward_model import RLHFPipeline
    from src.modules.cognition.strategy_engine import ExecutiveStrategist
    from src.modules.ethics.weighted_ethics_scorer import CandidateAction, EthicsMixtureResult
    from src.modules.memory.narrative import NarrativeMemory


from src.kernel_lobes.models import (
    BayesianEcograde,
    BayesianStageMetadata,
    MotorCommandDispatch,
    SensorySpike,
)

if TYPE_CHECKING:
    from src.nervous_system.corpus_callosum import CorpusCallosum


class CerebellumLobe:
    """
    Subsystem for Bayesian Inference, Strategic Alignment, and BMA.

    Acts as the 'Internal Oscillator' and error-correction unit.
    Handles the mathematical weight of decisions.
    """

    def __init__(
        self,
        bayesian: BayesianInferenceEngine,
        strategist: ExecutiveStrategist,
        memory: NarrativeMemory,
        rlhf: RLHFPipeline | None = None,
        bus: CorpusCallosum | None = None,
    ):
        self.bayesian = bayesian
        self.strategist = strategist
        self.memory = memory
        self.rlhf = rlhf
        self.bus = bus

        from src.modules.memory.session_checkpoint import SessionCheckpointTracker

        self.tracker = SessionCheckpointTracker(self.memory)
        # Mnemónica asíncrona: El Cerebelo escucha estímulos para pre-calcular confianza
        if self.bus:
            self.bus.subscribe(SensorySpike, self._on_sensory_event)
            self.bus.subscribe(MotorCommandDispatch, self._on_motor_dispatch)

    def execute_bayesian_stage(
        self,
        clean_actions: list[CandidateAction],
        scenario: str,
        context: str,
        signals: dict[str, Any],
        identity_deltas: Any = None,
        rlhf_features: Any = None,
    ) -> tuple[EthicsMixtureResult, BayesianStageMetadata]:
        """
        Run Bayesian scoring and BMA.
        Extracted from kernel._run_bayesian_stage.
        """
        t0 = time.perf_counter()
        # 0. Sync Scorer and Priors (High-Friction Restorative Logic)
        from src.modules.governance.dao_orchestrator import DAOOrchestrator

        priors = None
        if hasattr(self.bayesian, "dao") and isinstance(self.bayesian.dao, DAOOrchestrator):
            priors = self.bayesian.dao.get_state("bayesian_posterior_alpha")

        # 0.5 Sync Scorer defaults or empirical overrides (historical requirement)
        if priors:
            self.bayesian.update_posterior_from_feedback(priors)
        elif os.environ.get("KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS", "").strip().lower() not in (
            "1",
            "true",
            "yes",
            "on",
        ):
            self.bayesian.reset_mixture_weights()

        # 1. Update Strategic Alignment
        for a in clean_actions:
            a.strategic_alignment = self.strategist.evaluate_strategic_alignment(a.description)

        # 2. Feedback & Hierarchical logic (CPU bound)
        mixture_posterior_alpha = None
        feedback_consistency = None
        mixture_context_key = None
        hierarchical_context_key = None
        dirichlet_alpha_for_bma = None

        fb_path = os.environ.get("KERNEL_FEEDBACK_PATH", "").strip()
        _hier_on = os.environ.get("KERNEL_HIERARCHICAL_FEEDBACK", "").strip().lower() in (
            "1",
            "true",
            "yes",
            "on",
        )

        if fb_path:
            p = Path(fb_path)
            if p.is_file():
                from src.modules.cognition.feedback_mixture_posterior import (
                    context_level3_enabled,
                    load_and_apply_feedback,
                )

                rng_fb = np.random.default_rng(int(os.environ.get("KERNEL_FEEDBACK_SEED", "42")))
                tick_context = (scenario, context, signals) if context_level3_enabled() else None
                alpha_vec, feedback_consistency, fb_meta = load_and_apply_feedback(
                    p, rng=rng_fb, tick_context=tick_context
                )

                mixture_posterior_alpha = tuple(
                    round(float(v), 6) for v in np.asarray(alpha_vec).reshape(3)
                )
                # Update Bayesian Engine internal state
                self.bayesian.update_posterior_from_feedback(
                    alpha_vec, feedback_consistency or "compatible"
                )
                dirichlet_alpha_for_bma = alpha_vec

                if isinstance(fb_meta, dict) and fb_meta.get("active_context_key"):
                    mixture_context_key = str(fb_meta["active_context_key"])

                # Boy Scout Pass: Log incompatible feedback
                if feedback_consistency == "incompatible":
                    _log.warning(
                        "CerebellumLobe: Bayesian feedback is INCOMPATIBLE with priors. Risk of ethical drift."
                    )

        # 2.5 Apply Temporal Horizon Prior Nudge (ADR 0005 / Issue #1 B)
        # This closes the gap between 'weighted mixture' and 'experiential learning'
        from src.kernel_utils import kernel_env_truthy

        if kernel_env_truthy("KERNEL_TEMPORAL_HORIZON_PRIOR"):
            from src.modules.cognition.temporal_horizon_prior import apply_horizon_prior_to_engine

            # We use the 'genome' stored in the kernel if available, or the current state
            # Here we assume the mixture should not drift more than 15% from its core geometry.
            try:
                # We need the genome weights (the 'long-term constitutional' weights)
                # If not provided, we use the current weights as the baseline for this tick's drift.
                genome = getattr(self.bayesian, "prior_weights", (0.4, 0.35, 0.25))
                apply_horizon_prior_to_engine(
                    engine=self.bayesian.scorer
                    if hasattr(self.bayesian, "scorer")
                    else self.bayesian,
                    memory=self.memory,
                    context=context,
                    genome_weights=genome,
                    max_drift=0.15,
                )
                _log.debug(
                    "CerebellumLobe: Applied temporal horizon nudge based on NarrativeMemory."
                )
            except Exception as e:
                _log.error("CerebellumLobe: Failed to apply temporal horizon prior: %s", e)

                # ADR 0013 — Hierarchical updater: apply per-context Dirichlet blending
                if _hier_on:
                    from src.modules.cognition.hierarchical_updater import (
                        HierarchicalUpdater,
                        canonical_context_type,
                    )

                    ctype = canonical_context_type(context)
                    min_local = int(os.environ.get("KERNEL_HIERARCHICAL_MIN_LOCAL", "2"))
                    # Use a fresh hierarchical updater with the global alpha from feedback
                    hier = HierarchicalUpdater(
                        initial_alpha=list(np.asarray(alpha_vec).reshape(3)),
                        min_local_items=min_local,
                        seed=int(os.environ.get("KERNEL_FEEDBACK_SEED", "42")),
                    )
                    hier_alpha = hier.active_alpha_for_context(ctype)
                    mixture_posterior_alpha = tuple(
                        round(float(v), 6) for v in np.asarray(hier_alpha).reshape(3)
                    )
                    self.bayesian.update_posterior_from_feedback(
                        hier_alpha, feedback_consistency or "compatible"
                    )
                    dirichlet_alpha_for_bma = hier_alpha
                    hierarchical_context_key = ctype

        # 3. Main Bayesian Evaluate
        bayes_result = self.bayesian.evaluate(
            actions=clean_actions,
            scenario=scenario,
            context=context,
            signals=signals,
            identity_deltas=identity_deltas,
            rlhf_features=rlhf_features,
        )

        # 4. BMA (Bayesian Mixture Averaging)
        bma_win_probs = None
        bma_dirichlet = None
        bma_n_s = None

        from src.modules.cognition.bayesian_mixture_averaging import (
            bma_enabled,
            bma_n_samples,
            monte_carlo_win_probabilities,
            parse_bma_alpha_from_env,
        )

        if bma_enabled():
            alpha_bma = (
                dirichlet_alpha_for_bma
                if dirichlet_alpha_for_bma is not None
                else parse_bma_alpha_from_env()
            )
            n_s = bma_n_samples()
            # Use internal scorer directly; seed from variability flag for reproducibility
            _bma_rng = np.random.default_rng(42)
            win_probs = monte_carlo_win_probabilities(
                self.bayesian.scorer if hasattr(self.bayesian, "scorer") else self.bayesian,
                clean_actions,
                alpha=np.asarray(alpha_bma, dtype=np.float64),
                n_samples=n_s,
                scenario=scenario,
                context=context,
                signals=signals,
                rng=_bma_rng,
            )

            bma_win_probs = win_probs
            bma_dirichlet = tuple(round(float(v), 6) for v in np.asarray(alpha_bma).reshape(3))
            bma_n_s = n_s

        latency_ms = (time.perf_counter() - t0) * 1000
        if latency_ms > 100.0:  # Monte Carlo can be slow
            _log.warning("CerebellumLobe: Heavy Bayesian stage detected: %.4f ms", latency_ms)
        elif latency_ms > 20.0:
            _log.debug("CerebellumLobe: Bayesian stage latency: %.4f ms", latency_ms)

        meta = BayesianStageMetadata(
            mixture_posterior_alpha=mixture_posterior_alpha,
            feedback_consistency=feedback_consistency,
            mixture_context_key=mixture_context_key,
            hierarchical_context_key=hierarchical_context_key,
            applied_mixture_weights=tuple(
                round(float(v), 6) for v in self.bayesian.hypothesis_weights
            ),
            bma_win_probabilities=bma_win_probs,
            bma_dirichlet_alpha=bma_dirichlet,
            bma_n_samples=bma_n_s,
        )

        return bayes_result, meta

    async def _on_sensory_event(self, spike: SensorySpike):
        """Asynchronous Bayesian assistance loop."""
        _log.info(f"Cerebelo Auxiliar: Iniciando pre-cálculo asíncrono para Spike {spike.pulse_id}")
        # En una versión madura, aquí se ejecutaría el BMA en segundo plano
        # y se emitiría un BayesianEcograde con el delta de confianza.
        if self.bus:
            eco = BayesianEcograde(
                confidence_delta=0.05,  # Simulación de mejora de confianza por análisis bayesiano
                metadata={"ref_spike": spike.pulse_id},
            )
            await self.bus.publish(eco)

    async def _on_motor_dispatch(self, dispatch: MotorCommandDispatch):
        """Monitor final decisions (Moved to MemoryLobe in Block 26)."""
        pass
