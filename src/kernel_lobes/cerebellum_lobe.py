from __future__ import annotations
import os
from pathlib import Path
from typing import Any, TYPE_CHECKING, Optional, Tuple
import numpy as np

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
        strategist: ExecutiveStrategist
    ):
        self.bayesian = bayesian
        self.strategist = strategist

    def execute_bayesian_stage(
        self,
        clean_actions: list[CandidateAction],
        scenario: str,
        context: str,
        signals: dict[str, Any],
    ) -> Tuple[EthicsMixtureResult, BayesianStageMetadata]:
        """
        Run Bayesian scoring and BMA.
        Extracted from kernel._run_bayesian_stage.
        """
        # Mixture weights are set in ``EthicalKernel._run_bayesian_stage`` (reset vs episodic refresh).

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

        # RLHF → Bayesian prior nudge runs in :meth:`~src.kernel.EthicalKernel.aprocess` (async) before this stage.

        # 3. Main Bayesian Evaluate
        bayes_result = self.bayesian.evaluate(
            actions=clean_actions, 
            scenario=scenario, 
            context=context, 
            signals=signals
        )

        # 4. BMA (Bayesian Mixture Averaging)
        bma_win_probs = None
        bma_dirichlet = None
        bma_n_s = None
        
        from src.modules.bayesian_mixture_averaging import bma_enabled, bma_n_samples, monte_carlo_win_probabilities, parse_bma_alpha_from_env
        if bma_enabled():
            alpha_bma = dirichlet_alpha_for_bma if dirichlet_alpha_for_bma is not None else parse_bma_alpha_from_env()
            n_s = bma_n_samples()
            rng_bma = np.random.default_rng(int(os.environ.get("KERNEL_BMA_SEED", "42")))
            scorer = self.bayesian.scorer if hasattr(self.bayesian, "scorer") else self.bayesian
            win_probs = monte_carlo_win_probabilities(
                scorer,
                clean_actions,
                alpha=np.asarray(alpha_bma, dtype=np.float64),
                n_samples=n_s,
                scenario=scenario,
                context=context,
                signals=signals,
                rng=rng_bma,
            )
            
            bma_win_probs = win_probs
            bma_dirichlet = tuple(round(float(v), 6) for v in np.asarray(alpha_bma).reshape(3))
            bma_n_s = n_s

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
