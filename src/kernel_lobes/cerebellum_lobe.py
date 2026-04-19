from __future__ import annotations
import os
from pathlib import Path
from typing import Any, TYPE_CHECKING, Optional, Tuple
import numpy as np
import time
import math
import logging

_log = logging.getLogger(__name__)

from src.kernel_lobes.models import BayesianStageMetadata

if TYPE_CHECKING:
    from src.modules.bayesian_engine import BayesianInferenceEngine
    from src.modules.strategy_engine import ExecutiveStrategist
    from src.modules.weighted_ethics_scorer import CandidateAction, EthicsMixtureResult


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
        rlhf: Optional[RLHFPipeline] = None
    ):
        self.bayesian = bayesian
        self.strategist = strategist
        self.rlhf = rlhf

    def execute_bayesian_stage(
        self,
        clean_actions: list[CandidateAction],
        scenario: str,
        context: str,
        signals: dict[str, Any],
        identity_deltas: Any = None,
        rlhf_features: Any = None
    ) -> Tuple[EthicsMixtureResult, BayesianStageMetadata]:
        """
        Run Bayesian scoring and BMA.
        Extracted from kernel._run_bayesian_stage.
        """
        t0 = time.perf_counter()
        # 0. Sync Scorer and Priors (High-Friction Restorative Logic)
        from src.modules.dao_orchestrator import DAOOrchestrator
        priors = None
        if hasattr(self.bayesian, "dao") and isinstance(self.bayesian.dao, DAOOrchestrator):
             priors = self.bayesian.dao.get_state("bayesian_posterior_alpha")
        elif os.environ.get("KERNEL_BAYESIAN_PERSISTENCE", "0") == "1":
             # If we have a global reference, we would load it here
             pass

        if priors:
            self.bayesian.update_posterior_from_feedback(priors)
        else:
            self.bayesian.reset()

        # 1. Update Strategic Alignment
        for a in clean_actions:
            a.strategic_alignment = self.strategist.evaluate_strategic_alignment(a.description)

        # 2. Feedback & Hierarchical logic (CPU bound)
        mixture_posterior_alpha = None
        feedback_consistency = None
        mixture_context_key = None
        dirichlet_alpha_for_bma = None
        
        fb_path = os.environ.get("KERNEL_FEEDBACK_PATH", "").strip()
        if fb_path:
            p = Path(fb_path)
            if p.is_file():
                from src.modules.feedback_mixture_posterior import context_level3_enabled, load_and_apply_feedback
                rng_fb = np.random.default_rng(int(os.environ.get("KERNEL_FEEDBACK_SEED", "42")))
                tick_context = (scenario, context, signals) if context_level3_enabled() else None
                alpha_vec, feedback_consistency, fb_meta = load_and_apply_feedback(p, rng=rng_fb, tick_context=tick_context)
                
                mixture_posterior_alpha = tuple(round(float(v), 6) for v in np.asarray(alpha_vec).reshape(3))
                # Update Bayesian Engine internal state
                self.bayesian.update_posterior_from_feedback(alpha_vec, feedback_consistency or "compatible")
                dirichlet_alpha_for_bma = alpha_vec
                
                if isinstance(fb_meta, dict) and fb_meta.get("active_context_key"):
                    mixture_context_key = str(fb_meta["active_context_key"])
                
                # Boy Scout Pass: Log incompatible feedback
                if feedback_consistency == "incompatible":
                    _log.warning("CerebellumLobe: Bayesian feedback is INCOMPATIBLE with priors. Risk of ethical drift.")

        # 3. Main Bayesian Evaluate
        bayes_result = self.bayesian.evaluate(
            actions=clean_actions, 
            scenario=scenario, 
            context=context, 
            signals=signals,
            identity_deltas=identity_deltas,
            rlhf_features=rlhf_features
        )

        # 4. BMA (Bayesian Mixture Averaging)
        bma_win_probs = None
        bma_dirichlet = None
        bma_n_s = None
        
        from src.modules.bayesian_mixture_averaging import bma_enabled, bma_n_samples, monte_carlo_win_probabilities, parse_bma_alpha_from_env
        if bma_enabled():
            alpha_bma = dirichlet_alpha_for_bma if dirichlet_alpha_for_bma is not None else parse_bma_alpha_from_env()
            n_s = bma_n_samples()
            # Use internal scorer directly
            win_probs = monte_carlo_win_probabilities(self.bayesian.scorer if hasattr(self.bayesian, "scorer") else self.bayesian, clean_actions, alpha=np.asarray(alpha_bma, dtype=np.float64), n_samples=n_s, scenario=scenario, context=context, signals=signals)
            
            bma_win_probs = win_probs
            bma_dirichlet = tuple(round(float(v), 6) for v in np.asarray(alpha_bma).reshape(3))
            bma_n_s = n_s

        latency_ms = (time.perf_counter() - t0) * 1000
        if latency_ms > 100.0: # Monte Carlo can be slow
            _log.warning("CerebellumLobe: Heavy Bayesian stage detected: %.4f ms", latency_ms)
        elif latency_ms > 20.0:
            _log.debug("CerebellumLobe: Bayesian stage latency: %.4f ms", latency_ms)

        meta = BayesianStageMetadata(
            mixture_posterior_alpha=mixture_posterior_alpha,
            feedback_consistency=feedback_consistency,
            mixture_context_key=mixture_context_key,
            applied_mixture_weights=tuple(round(float(v), 6) for v in self.bayesian.hypothesis_weights),
            bma_win_probabilities=bma_win_probs,
            bma_dirichlet_alpha=bma_dirichlet,
            bma_n_samples=bma_n_s
        )
        
        return bayes_result, meta
