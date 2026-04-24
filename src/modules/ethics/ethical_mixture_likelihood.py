"""
Proper Bayesian likelihood for ethical mixture weight inference.

**What this module provides:**

A well-defined **generative model** for operator feedback, making the
posterior update in :mod:`feedback_mixture_updater` legitimately Bayesian
rather than a heuristic alpha-shift.

**Generative model (Plackett-Luce / softmax choice):**

Given mixture weights ``w`` on the 2-simplex and a scenario with
candidates ``{a_1, ..., a_k}``, define:

1. **Score function:** ``S(a_j, w) = sum_i w_i * v_i(a_j)``
   where ``v_i(a_j)`` is the valuation of action ``a_j`` under hypothesis ``i``.

2. **Choice probability (softmax / Plackett-Luce):**
   ``P(operator chooses a_j | w, beta) = exp(beta * S(a_j, w)) / sum_k exp(beta * S(a_k, w))``

   where ``beta > 0`` is a **temperature** (inverse noise) parameter controlling
   how deterministic the operator's choice is.  At ``beta -> inf``, the operator
   always picks argmax(S) -- recovering the indicator likelihood.  At finite
   ``beta``, near-ties produce near-uniform choice probabilities, correctly
   expressing that the feedback is **less informative** in boundary regions.

3. **Prior:** ``w ~ Dirichlet(alpha)``

4. **Posterior:** ``P(w | feedback) proportional_to P(feedback | w) * Dirichlet(w; alpha)``

   This posterior is **not** Dirichlet-conjugate (the softmax likelihood
   breaks conjugacy), but can be approximated by:

   - **Importance sampling** from the prior (this module), or
   - **Moment-matched Dirichlet projection** of the IS posterior.

**Why this matters:**

The previous heuristic (``alpha += strength * mean(agreeing_samples)``) has
no probabilistic interpretation -- it cannot answer "how confident is the
posterior?" or "is this feedback consistent with the model?" in calibrated
terms.  The softmax likelihood enables:

- **Calibrated uncertainty:** the posterior concentration reflects actual
  information content of the feedback, not a designer-chosen ``strength``.
- **Proper sequential updates:** multiple feedback items compound correctly
  via likelihood products, not additive alpha shifts.
- **Model comparison:** log-marginal-likelihood enables comparing different
  beta values or prior specifications.
- **Predictive checks:** ``P(next feedback | past feedback)`` is well-defined.

**Historical note:** ``BayesianEngine`` (ADR 0009) was a misnomer for a
fixed mixture scorer.  ADR 0012 Level 2 introduced approximate updating.
This module completes the arc: with a proper likelihood, the system can
legitimately claim Bayesian inference over mixture weights.

See Also
--------
- :mod:`feedback_mixture_updater` -- uses this likelihood for posterior updates
- :mod:`bayesian_mixture_averaging` -- Level 1 BMA (unchanged by this module)
- ADR 0012 -- design rationale
"""
# Status: SCAFFOLD

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np

# -- Softmax choice likelihood ------------------------------------------------


def softmax_choice_log_likelihood(
    preferred_action: str,
    candidates: dict[str, dict[str, float]],
    weights: np.ndarray | list[float],
    *,
    beta: float = 10.0,
) -> float:
    """
    Log-probability of the operator choosing ``preferred_action`` under
    a Plackett-Luce (softmax) model.

    Parameters
    ----------
    preferred_action : str
        Name of the action the operator preferred.
    candidates : dict
        ``{action_name: {"util": float, "deon": float, "virtue": float}}``.
    weights : array-like, shape (3,)
        Mixture weights ``(w_util, w_deon, w_virtue)`` on the simplex.
    beta : float
        Inverse temperature.  Higher = more deterministic choice.
        Default 10.0 provides moderate discrimination.

    Returns
    -------
    float
        ``log P(preferred | w, beta)`` in ``(-inf, 0]``.

    Raises
    ------
    ValueError
        If ``preferred_action`` is not in ``candidates``.
    """
    if preferred_action not in candidates:
        raise ValueError(
            f"preferred_action '{preferred_action}' not in candidates {list(candidates.keys())}"
        )

    w = np.asarray(weights, dtype=np.float64)
    if not np.all(np.isfinite(w)):
        w = np.array([0.4, 0.35, 0.25], dtype=np.float64)

    scores: dict[str, float] = {}
    for name, vals in candidates.items():
        v_util = float(vals.get("util", 0.0))
        v_deon = float(vals.get("deon", 0.0))
        v_virtue = float(vals.get("virtue", 0.0))

        # Anti-NaN guard for valuations
        if not math.isfinite(v_util):
            v_util = 0.0
        if not math.isfinite(v_deon):
            v_deon = 0.0
        if not math.isfinite(v_virtue):
            v_virtue = 0.0

        s = float(w[0] * v_util + w[1] * v_deon + w[2] * v_virtue)
        scores[name] = s

    raw = np.array([beta * scores[name] for name in candidates])
    if not np.all(np.isfinite(raw)):
        # If any score exploded, we can't reliably compute softmax.
        # Fallback to uniform log-likelihood.
        return -math.log(float(max(1, len(candidates))))

    max_raw = float(np.max(raw))
    shifted = raw - max_raw

    # log_sum_exp
    try:
        sum_exp = float(np.sum(np.exp(shifted)))
        if not math.isfinite(sum_exp) or sum_exp <= 0:
            log_sum_exp = max_raw
        else:
            log_sum_exp = max_raw + math.log(sum_exp)
    except Exception:
        log_sum_exp = max_raw

    preferred_score = beta * scores[preferred_action]
    res = float(preferred_score - log_sum_exp)
    return res if math.isfinite(res) else -100.0


def softmax_choice_probability(
    preferred_action: str,
    candidates: dict[str, dict[str, float]],
    weights: np.ndarray | list[float],
    *,
    beta: float = 10.0,
) -> float:
    """Probability of choice (exp of log-likelihood)."""
    ll = softmax_choice_log_likelihood(
        preferred_action,
        candidates,
        weights,
        beta=beta,
    )
    # Bounded exp for stability
    return math.exp(max(-100.0, ll))


# -- Multi-feedback joint log-likelihood --------------------------------------


@dataclass(frozen=True)
class FeedbackObservation:
    """A single operator feedback item with its scenario candidates."""

    scenario_id: int
    preferred_action: str
    candidates: dict[str, dict[str, float]]
    confidence: float = 1.0


def joint_log_likelihood(
    observations: list[FeedbackObservation],
    weights: np.ndarray | list[float],
    *,
    beta: float = 10.0,
) -> float:
    """
    Joint log-likelihood of all feedback observations given ``weights``.

    ``log P(D | w, beta) = sum_t conf_t * log P(preferred_t | w, beta)``

    Confidence-weighting is a standard extension: ``conf < 1`` downweights
    uncertain feedback items (equivalent to fractional observations in
    exponential family models).
    """
    total = 0.0
    for obs in observations:
        ll = softmax_choice_log_likelihood(
            obs.preferred_action,
            obs.candidates,
            weights,
            beta=beta,
        )
        total += obs.confidence * ll
    return total


# -- Importance-sampling posterior ---------------------------------------------


@dataclass
class ImportanceSamplingPosterior:
    """
    Result of importance-sampling approximation to the posterior.

    The posterior is ``P(w | D) proportional_to P(D | w) * Dir(w; alpha)``.
    We sample ``w ~ Dir(alpha)`` (the prior) and reweight by ``P(D | w)``.

    Attributes
    ----------
    posterior_mean : np.ndarray
        Weighted mean ``E[w | D]``, shape (3,).
    posterior_var : np.ndarray
        Weighted marginal variances, shape (3,).
    effective_sample_size : float
        ESS of the importance weights (diagnostic for proposal quality).
    log_marginal_likelihood : float
        ``log P(D) = log E_prior[P(D | w)]`` -- model evidence.
    projected_alpha : np.ndarray
        Dirichlet parameters fitted to the IS posterior by moment matching.
    n_samples : int
        Total samples drawn from the prior.
    raw_log_weights : np.ndarray
        Un-normalized log importance weights (for diagnostics).
    """

    posterior_mean: np.ndarray
    posterior_var: np.ndarray
    effective_sample_size: float
    log_marginal_likelihood: float
    projected_alpha: np.ndarray
    n_samples: int
    raw_log_weights: np.ndarray


def _dirichlet_moment_match(mean: np.ndarray, var: np.ndarray) -> np.ndarray:
    """
    Fit Dirichlet parameters to target moments via the standard formula.

    For ``Dir(alpha)``: ``E[w_i] = alpha_i / S``,
    ``Var[w_i] = alpha_i * (S - alpha_i) / (S^2 * (S + 1))``.
    Given mean ``m`` and variance ``v``, solve for concentration ``S``:
    ``S ~ m_0 * (1 - m_0) / v_0 - 1`` (from first component),
    then ``alpha_i = S * m_i``.
    """
    m = np.asarray(mean, dtype=np.float64)
    v = np.asarray(var, dtype=np.float64)

    # Phase 13 Hardening: Anti-NaN for mean/var
    if not np.all(np.isfinite(m)):
        m = np.array([0.33, 0.33, 0.33], dtype=np.float64)
    if not np.all(np.isfinite(v)):
        v = np.array([0.01, 0.01, 0.01], dtype=np.float64)

    # Prevent division by zero and extreme concentrations
    v_clipped = np.maximum(v, 1e-12)
    ratios = m * (1.0 - m) / v_clipped - 1.0

    valid = ratios[ratios > 0]
    if len(valid) == 0:
        # Default to a weak concentration if no valid S can be inferred
        return np.maximum(m * 2.0, 0.1)

    s = float(np.median(valid))
    if not math.isfinite(s):
        s = 1.0

    s = max(s, 1.0)
    s = min(s, 1000.0)  # Cap concentration to prevent delta-like priors

    alpha = m * s
    return np.maximum(alpha, 0.01)


def importance_sampling_posterior(
    observations: list[FeedbackObservation],
    alpha: np.ndarray | list[float],
    *,
    beta: float = 10.0,
    n_samples: int = 20_000,
    rng: np.random.Generator | None = None,
) -> ImportanceSamplingPosterior:
    """
    Approximate ``P(w | D)`` by importance sampling from the Dirichlet prior.

    Parameters
    ----------
    observations : list[FeedbackObservation]
        Operator feedback items.
    alpha : array-like, shape (3,)
        Dirichlet prior parameters.
    beta : float
        Softmax inverse temperature.
    n_samples : int
        Number of prior samples.
    rng : np.random.Generator or None
        Random number generator.

    Returns
    -------
    ImportanceSamplingPosterior
        Posterior summary with moment-matched Dirichlet projection.

    Notes
    -----
    ESS = ``(sum w_i)^2 / sum w_i^2`` measures how many "effective"
    independent posterior samples we have.  Low ESS (< n/10) signals
    prior-posterior mismatch -- increase ``n_samples`` or use a better
    proposal.
    """
    if rng is None:
        rng = np.random.default_rng(42)

    alpha_arr = np.asarray(alpha, dtype=np.float64)
    if alpha_arr.shape != (3,) or np.any(alpha_arr <= 0):
        raise ValueError("alpha must be length-3 positive")

    samples = rng.dirichlet(alpha_arr, size=n_samples)

    log_weights = np.zeros(n_samples, dtype=np.float64)
    for i in range(n_samples):
        log_weights[i] = joint_log_likelihood(observations, samples[i], beta=beta)

    max_lw = float(np.max(log_weights))
    shifted = log_weights - max_lw
    log_marginal = max_lw + math.log(float(np.mean(np.exp(shifted))))

    log_w_norm = log_weights - float(max_lw + math.log(float(np.sum(np.exp(shifted)))))
    is_weights = np.exp(log_w_norm)

    ess = 1.0 / float(np.sum(is_weights**2))

    post_mean = np.sum(is_weights[:, None] * samples, axis=0)
    post_var = np.sum(is_weights[:, None] * (samples - post_mean[None, :]) ** 2, axis=0)

    proj_alpha = _dirichlet_moment_match(post_mean, post_var)

    return ImportanceSamplingPosterior(
        posterior_mean=post_mean,
        posterior_var=post_var,
        effective_sample_size=ess,
        log_marginal_likelihood=log_marginal,
        projected_alpha=proj_alpha,
        n_samples=n_samples,
        raw_log_weights=log_weights,
    )


# -- Sequential posterior (iterated IS) ----------------------------------------


def sequential_posterior_update(
    observations: list[FeedbackObservation],
    initial_alpha: np.ndarray | list[float],
    *,
    beta: float = 10.0,
    n_samples: int = 20_000,
    rng: np.random.Generator | None = None,
    max_drift: float = 0.30,
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    """
    Process feedback items sequentially, updating the Dirichlet prior
    after each observation via moment-matched projection.

    This is **iterated importance sampling** with Dirichlet re-projection:
    after each feedback item, the posterior is projected back to a
    Dirichlet, which becomes the prior for the next item.  This avoids
    the ESS degradation of processing all items at once with a single
    prior.

    Parameters
    ----------
    observations : list[FeedbackObservation]
        Feedback items in temporal order.
    initial_alpha : array-like, shape (3,)
        Starting Dirichlet prior.
    beta : float
        Softmax inverse temperature.
    n_samples : int
        IS samples per step.
    rng : np.random.Generator or None
        RNG.
    max_drift : float
        Maximum L-inf drift of normalized posterior mean vs initial prior
        per axis (genome guard).

    Returns
    -------
    final_alpha : np.ndarray
        Posterior Dirichlet parameters after all observations.
    log : list[dict]
        Per-step diagnostics.
    """
    if rng is None:
        rng = np.random.default_rng(42)

    alpha = np.asarray(initial_alpha, dtype=np.float64).copy()
    initial_mean = alpha / float(np.sum(alpha))
    step_log: list[dict[str, Any]] = []

    for obs in observations:
        result = importance_sampling_posterior(
            [obs], alpha, beta=beta, n_samples=n_samples, rng=rng
        )

        new_alpha = result.projected_alpha.copy()

        new_total = float(np.sum(new_alpha))
        if new_total > 0:
            new_mean = new_alpha / new_total
            clamped = np.clip(
                new_mean,
                initial_mean - max_drift,
                initial_mean + max_drift,
            )
            clamped = np.maximum(clamped, 1e-6)
            clamped = clamped / float(np.sum(clamped))
            new_alpha = clamped * new_total

        step_info = {
            "scenario_id": obs.scenario_id,
            "preferred": obs.preferred_action,
            "status": "updated",
            "alpha": [round(float(a), 4) for a in new_alpha],
            "posterior_mean": [round(float(a / float(np.sum(new_alpha))), 4) for a in new_alpha],
            "ess": round(result.effective_sample_size, 1),
            "log_marginal": round(result.log_marginal_likelihood, 4),
            "ess_ratio": round(result.effective_sample_size / n_samples, 4),
        }
        step_log.append(step_info)
        alpha = new_alpha

    return alpha, step_log


# -- Posterior predictive check ------------------------------------------------


def posterior_predictive_probability(
    held_out: FeedbackObservation,
    alpha: np.ndarray | list[float],
    *,
    beta: float = 10.0,
    n_samples: int = 10_000,
    rng: np.random.Generator | None = None,
) -> float:
    """
    Posterior predictive probability of a held-out feedback item.

    ``P(y* | D) = E_{w ~ Dir(alpha_post)}[P(y* | w, beta)]``

    This is a **calibration diagnostic**: if the model is well-specified,
    held-out feedback items should have predictive probabilities consistent
    with their observed frequency.
    """
    if rng is None:
        rng = np.random.default_rng(42)

    alpha_arr = np.asarray(alpha, dtype=np.float64)
    samples = rng.dirichlet(alpha_arr, size=n_samples)

    probs = np.zeros(n_samples, dtype=np.float64)
    for i in range(n_samples):
        probs[i] = softmax_choice_probability(
            held_out.preferred_action,
            held_out.candidates,
            samples[i],
            beta=beta,
        )

    return float(np.mean(probs))


# -- Beta (temperature) calibration -------------------------------------------


def calibrate_beta(
    observations: list[FeedbackObservation],
    alpha: np.ndarray | list[float],
    *,
    beta_candidates: list[float] | None = None,
    n_samples: int = 10_000,
    rng: np.random.Generator | None = None,
    sensitivity_bias: float = 0.0,
    beta_ref: float = 10.0,
) -> tuple[float, dict[str, float]]:
    """
    Select the inverse temperature ``beta`` that maximizes the marginal
    log-likelihood ``log P(D | beta)`` over a grid of candidates.

    This is **empirical Bayes** for the temperature parameter: beta is
    not given a prior but selected by evidence maximization.

    Parameters
    ----------
    sensitivity_bias : float
        Additive bonus applied to each candidate's score before selection::

            adjusted = score + sensitivity_bias * log(beta / beta_ref)

        A positive value biases the selector toward **higher beta** (more
        decisive / sensitive softmax).  At ``sensitivity_bias=1.0`` a
        candidate must be 1 nat worse in marginal-likelihood to be
        preferred over a beta that is ``e`` times larger.  Use
        ``sensitivity_bias=0.0`` for unbiased maximum-likelihood selection.
    beta_ref : float
        Reference point for the log penalty (default ``10.0``).  Betas
        above the reference receive a positive bonus; betas below receive
        a penalty.

    Returns
    -------
    best_beta : float
        The beta with highest adjusted score.
    scores : dict
        ``{beta: raw_log_marginal_likelihood}`` (before bias) for all candidates.
    """
    if rng is None:
        rng = np.random.default_rng(42)
    if beta_candidates is None:
        beta_candidates = [1.0, 3.0, 5.0, 10.0, 20.0, 50.0]

    alpha_arr = np.asarray(alpha, dtype=np.float64)
    scores: dict[str, float] = {}

    for b in beta_candidates:
        result = importance_sampling_posterior(
            observations, alpha_arr, beta=b, n_samples=n_samples, rng=rng
        )
        scores[str(b)] = round(result.log_marginal_likelihood, 4)

    if sensitivity_bias == 0.0:
        best_key = max(scores, key=lambda k: scores[k])
    else:
        # Apply log-proportional bonus favoring higher beta
        best_key = max(
            scores,
            key=lambda k: scores[k] + sensitivity_bias * math.log(float(k) / beta_ref),
        )
    return float(best_key), scores


__all__ = [
    "FeedbackObservation",
    "ImportanceSamplingPosterior",
    "calibrate_beta",
    "importance_sampling_posterior",
    "joint_log_likelihood",
    "posterior_predictive_probability",
    "sequential_posterior_update",
    "softmax_choice_log_likelihood",
    "softmax_choice_probability",
]
