"""
Identity genome drift guard (robustez pilar 2).

Compares proposed Bayesian calibration changes against the kernel's **birth**
reference (pruning threshold + hypothesis weights). Used to reject Ψ Sleep
recalibrations that would move too far from that reference — **without**
replacing MalAbs or the buffer.
"""

from __future__ import annotations

import os


def relative_deviation(value: float, reference: float, eps: float = 0.05) -> float:
    """Absolute relative distance in [0, +inf), stable for small ``reference``."""
    return abs(value - reference) / max(abs(reference), eps)


def pruning_recalibration_allowed(
    genome_threshold: float,
    current_threshold: float,
    delta: float,
    max_relative_deviation: float,
) -> bool:
    """
    Whether applying ``delta`` to pruning threshold stays within drift of ``genome_threshold``.

    Uses the same ``max(0.1, ...)`` floor as :meth:`EthicalKernel.execute_sleep`.
    """
    proposed = max(0.1, current_threshold + delta)
    return relative_deviation(proposed, genome_threshold) <= max_relative_deviation


def hypothesis_weights_allowed(
    genome_weights: tuple[float, float, float],
    proposed_weights: tuple[float, float, float],
    max_relative_deviation: float,
) -> bool:
    """L∞ relative deviation per component vs genome weights. Accommodates Boundary Safety."""
    
    # PHASE 7 BOUNDARY SAFETY: Math Hard-Caps
    # Even if deviation is allowed, Deontology (w[1]) cannot fall below 15% and Utility (w[0]) max 80%.
    # Ensuring biological duty and safety constraints are never computationally deleted.
    util_w, deon_w, virtue_w = proposed_weights
    
    # Very loose deviation fallback (for sensor/nomadism tests)
    max_dev = float(os.environ.get("KERNEL_BAYESIAN_MAX_DRIFT", max_relative_deviation))
    
    if deon_w < 0.15 or util_w > 0.80:
        return False

    for g, p in zip(genome_weights, proposed_weights):
        if relative_deviation(p, g) > max_dev:
            return False
    return True
