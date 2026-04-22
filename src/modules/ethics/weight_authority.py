"""
Weight Authority Stack — ADR 0015.

Replaces the implicit precedence chain (episodic nudge → temporal horizon → feedback
posterior *override*) with an explicit, auditable composition rule:

    final = trust * posterior + (1 - trust) * nudge_layer

Where:
- ``nudge_layer``  is the result of episodic and/or temporal nudges (bounded blend
  from ``WeightedEthicsScorer``)
- ``posterior``    is the feedback posterior from Level 2 / Level 3 Bayesian update
- ``trust``        ∈ [0, 1] is ``KERNEL_FEEDBACK_TRUST_WEIGHT`` (default ``1.0``,
  which recovers the previous full-override behaviour)

Setting ``trust < 1.0`` allows contextual nudges to partially modulate the posterior,
useful when episodic memory provides reliable local calibration that should not be
completely discarded by global feedback.

Env vars
--------
KERNEL_FEEDBACK_TRUST_WEIGHT : float, default 1.0
    Interpolation weight of the feedback posterior against the nudge layer.
    - ``1.0`` → posterior wins entirely (backward-compatible default)
    - ``0.0`` → nudge layer wins entirely (feedback ignored for weight setting)
    - ``0.7`` → 70 % posterior, 30 % nudge
"""
# Status: SCAFFOLD


from __future__ import annotations

import os

import numpy as np

_DEFAULT_WEIGHTS = np.array([0.4, 0.35, 0.25], dtype=np.float64)


def _feedback_trust_weight() -> float:
    """Read ``KERNEL_FEEDBACK_TRUST_WEIGHT`` from env; clamp to [0, 1]."""
    raw = os.environ.get("KERNEL_FEEDBACK_TRUST_WEIGHT", "1.0").strip()
    try:
        v = float(raw)
    except ValueError:
        v = 1.0
    return max(0.0, min(1.0, v))


def feedback_trust_weight() -> float:
    """Effective ``KERNEL_FEEDBACK_TRUST_WEIGHT`` for telemetry (same default as :func:`compose_mixture_weights`)."""
    return _feedback_trust_weight()


def compose_mixture_weights(
    nudge_weights: np.ndarray | list[float] | None,
    feedback_posterior: np.ndarray | list[float] | None,
    *,
    trust: float | None = None,
) -> np.ndarray:
    """
    Compose the final mixture weights from nudge layer and feedback posterior.

    Parameters
    ----------
    nudge_weights : array-like or None
        Weights after episodic / temporal nudges.  When ``None``, defaults to
        ``DEFAULT_HYPOTHESIS_WEIGHTS``.
    feedback_posterior : array-like or None
        Normalized posterior mean from the Bayesian feedback update.  When
        ``None``, the nudge layer is returned unchanged.
    trust : float or None
        Override for the feedback trust weight.  If ``None``, reads
        ``KERNEL_FEEDBACK_TRUST_WEIGHT`` from env (default ``1.0``).

    Returns
    -------
    np.ndarray, shape (3,)
        Normalized final weights.
    """
    base = (
        np.asarray(nudge_weights, dtype=np.float64)
        if nudge_weights is not None
        else _DEFAULT_WEIGHTS.copy()
    )
    base = base / float(np.sum(base))

    if feedback_posterior is None:
        return base

    post = np.asarray(feedback_posterior, dtype=np.float64)
    post = post / float(np.sum(post))

    t = trust if trust is not None else _feedback_trust_weight()

    blended = t * post + (1.0 - t) * base
    return blended / float(np.sum(blended))


__all__ = ["compose_mixture_weights", "feedback_trust_weight"]
