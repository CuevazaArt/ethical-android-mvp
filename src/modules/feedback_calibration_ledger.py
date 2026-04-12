"""
Operator feedback ledger for bounded :class:`BayesianEngine` mixture updates.

Used during :meth:`EthicalKernel.execute_sleep` when ``KERNEL_PSI_SLEEP_UPDATE_MIXTURE=1``.
Counts (decision_regime, feedback_label) pairs — a calibration aid, not a clinical metric.
See ``docs/proposals/PROPOSAL_ETHICAL_CORE_LOGIC_EVOLUTION.md`` (B1).
"""

from __future__ import annotations

import os
from collections import Counter
from typing import Literal

import numpy as np

from .bayesian_engine import DEFAULT_HYPOTHESIS_WEIGHTS, BayesianEngine
from .identity_integrity import hypothesis_weights_allowed

FeedbackLabel = Literal["approve", "dispute", "harm_report"]

_VALID: frozenset[str] = frozenset({"approve", "dispute", "harm_report"})


def normalize_feedback_label(raw: str) -> FeedbackLabel | None:
    s = (raw or "").strip().lower()
    if s in _VALID:
        return s  # type: ignore[return-value]
    if s in ("harm", "report_harm"):
        return "harm_report"
    return None


def _env_truthy(name: str) -> bool:
    v = os.environ.get(name, "").strip().lower()
    return v in ("1", "true", "yes", "on")


class FeedbackCalibrationLedger:
    """In-memory confusion-style counts: ``(decision_regime, feedback_label) -> n``."""

    def __init__(self) -> None:
        self._counts: Counter[tuple[str, str]] = Counter()

    def record(self, decision_regime: str, label: str) -> None:
        if label not in _VALID:
            return
        r = (decision_regime or "").strip() or "unknown"
        self._counts[(r, label)] += 1

    def total(self) -> int:
        return int(sum(self._counts.values()))

    def clear(self) -> None:
        self._counts.clear()

    def copy_counts(self) -> Counter[tuple[str, str]]:
        return Counter(self._counts)


def compute_target_weights(counter: Counter[tuple[str, str]]) -> np.ndarray | None:
    """Map aggregated feedback to a mixture target on the 3-simplex (heuristic)."""
    n_approve = sum(c for (_, lab), c in counter.items() if lab == "approve")
    n_dispute = sum(c for (_, lab), c in counter.items() if lab == "dispute")
    n_harm = sum(c for (_, lab), c in counter.items() if lab == "harm_report")
    t = n_approve + n_dispute + n_harm
    if t <= 0:
        return None
    delta = np.array(
        [
            0.05 * (n_approve / t) - 0.12 * (n_harm / t) - 0.04 * (n_dispute / t),
            0.15 * (n_harm / t) + 0.07 * (n_dispute / t) - 0.02 * (n_approve / t),
            0.04 * (n_dispute / t) - 0.02 * (n_harm / t),
        ],
        dtype=np.float64,
    )
    target = DEFAULT_HYPOTHESIS_WEIGHTS + delta
    target = np.maximum(target, 1e-6)
    return target / float(np.sum(target))


def apply_psi_sleep_feedback_to_engine(
    engine: BayesianEngine,
    ledger: FeedbackCalibrationLedger,
    *,
    genome_weights: tuple[float, float, float],
    max_drift: float,
) -> str:
    """
    Blend ``engine.hypothesis_weights`` toward a feedback-derived target; clear ledger on success.

    Returns a short audit line for Psi Sleep output, or ``""`` if skipped.
    """
    if not _env_truthy("KERNEL_PSI_SLEEP_UPDATE_MIXTURE"):
        return ""
    try:
        min_s = int(os.environ.get("KERNEL_FEEDBACK_CALIBRATION_MIN_SAMPLES", "2"))
    except ValueError:
        min_s = 2
    min_s = max(0, min_s)
    n_samples = ledger.total()
    if n_samples < min_s:
        return ""
    try:
        blend = float(os.environ.get("KERNEL_PSI_SLEEP_FEEDBACK_BLEND", "0.12"))
    except ValueError:
        blend = 0.12
    blend = max(0.0, min(1.0, blend))

    target = compute_target_weights(ledger.copy_counts())
    if target is None:
        return ""

    current = np.asarray(engine.hypothesis_weights, dtype=np.float64).copy()
    mixed = (1.0 - blend) * current + blend * target
    mixed = np.maximum(mixed, 1e-6)
    mixed = mixed / float(np.sum(mixed))
    tup = (float(mixed[0]), float(mixed[1]), float(mixed[2]))
    if not hypothesis_weights_allowed(genome_weights, tup, max_drift):
        return "\n  Feedback mixture update skipped (genome drift cap)."

    engine.hypothesis_weights = mixed
    ledger.clear()
    return f"\n  Feedback mixture update applied (blend={blend:.3f}, samples={n_samples})."
