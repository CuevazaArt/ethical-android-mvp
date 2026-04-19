"""
Temporal prior nudge for ``BayesianEngine.hypothesis_weights`` (ADR 0005).

Interprets **horizon_weeks** (recent drift) and **horizon_long_term** (arc stability)
as numeric signals from :class:`NarrativeMemory`, then applies a **small** adjustment
before ``evaluate()`` — not a replacement for :meth:`BayesianEngine.refresh_weights_from_episodic_memory`.

Default: **inactive** unless ``KERNEL_TEMPORAL_HORIZON_PRIOR`` is set.

See ``docs/proposals/README.md``.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, List, Optional

import numpy as np

if TYPE_CHECKING:
    from .narrative import NarrativeEpisode, NarrativeMemory
    from .weighted_ethics_scorer import WeightedEthicsScorer

_logger = logging.getLogger(__name__)


@dataclass
class TemporalHorizonSignals:
    """Numeric stand-in for horizon_weeks / horizon_long_term."""

    weeks_trend: float
    long_term_stability: float
    combined: float


def _parse_ts(ep: NarrativeEpisode) -> datetime | None:
    try:
        ts = ep.timestamp
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        return datetime.fromisoformat(ts)
    except Exception:
        return None


def _matching_episodes(memory: NarrativeMemory, context: str, action_hint: str) -> List[NarrativeEpisode]:
    """Filter episodes by context and optional action hint."""
    if not hasattr(memory, "episodes") or not memory.episodes:
        return []

    eps = [e for e in memory.episodes if e.context == context]
    if action_hint and eps:
        ah = action_hint.lower()
        filtered = [e for e in eps if ah in (e.action_taken or "").lower()]
        if filtered:
            return filtered
    return eps


def compute_horizon_signals(
    memory: NarrativeMemory,
    context: str,
    action_hint: str = "",
    *,
    weeks_days: int | None = None,
) -> TemporalHorizonSignals:
    """
    Derive bounded signals from episodic history (same design as qualitative horizons).

    * **weeks_trend**: mean score trajectory in the recent calendar window.
    * **long_term_stability**: inverse spread of scores over the full matching arc.
    * **combined**: blend for a single nudge axis (see docs).
    """
    wd = weeks_days
    if wd is None:
        try:
            wd = int(os.environ.get("KERNEL_TEMPORAL_HORIZON_WEEKS_DAYS", "21"))
        except ValueError:
            wd = 21
    wd = max(7, min(120, wd))

    eps = _matching_episodes(memory, context, action_hint)
    if not eps:
        return TemporalHorizonSignals(0.0, 0.5, 0.0)

    by_time = sorted(eps, key=lambda e: _parse_ts(e) or datetime.min.replace(tzinfo=UTC))
    scores_all = np.array([float(e.ethical_score) for e in by_time], dtype=np.float64)

    # Boy Scout: Anti-NaN mass sanitation
    if not np.all(np.isfinite(scores_all)):
         scores_all = np.nan_to_num(scores_all, nan=0.5)

    std_all = float(np.std(scores_all)) if len(scores_all) > 1 else 0.0
    if not math.isfinite(std_all):
        std_all = 0.0
        
    long_term_stability = float(1.0 / (1.0 + std_all))

    def _age_days(e: NarrativeEpisode) -> Optional[float]:
        t = _parse_ts(e)
        if t is None:
            return None
        if t.tzinfo is not None:
            t = t.astimezone(UTC).replace(tzinfo=None)
        
        diff = (datetime.now() - t).total_seconds()
        return diff / 86400.0 if math.isfinite(diff) else None

    recent = [e for e in by_time if (ad := _age_days(e)) is not None and 0 <= ad <= float(wd)]

    weeks_trend = 0.0
    if len(recent) >= 3:
        recent_sorted = sorted(
            recent, key=lambda e: _parse_ts(e) or datetime.min.replace(tzinfo=UTC)
        )
        sc = np.array([float(e.ethical_score) for e in recent_sorted], dtype=np.float64)
        if not np.all(np.isfinite(sc)):
            sc = np.nan_to_num(sc, nan=0.5)
            
        n = len(sc)
        t1 = max(1, n // 3)
        t2 = max(1, n // 3)
        first = float(np.mean(sc[:t1]))
        last = float(np.mean(sc[-t2:]))
        raw = last - first
        
        if math.isfinite(raw):
            weeks_trend = float(np.clip(raw / 2.0, -1.0, 1.0))
        else:
            weeks_trend = 0.0

    arc_long = float(np.clip(2.0 * long_term_stability - 1.0, -1.0, 1.0))
    combined = float(0.55 * weeks_trend + 0.45 * arc_long)
    if not math.isfinite(combined):
        combined = 0.0
    combined = float(np.clip(combined, -1.0, 1.0))

    return TemporalHorizonSignals(
        weeks_trend=weeks_trend,
        long_term_stability=long_term_stability,
        combined=combined,
    )


def _nudge_delta(combined: float, alpha: float) -> np.ndarray:
    """Deteriorating (combined < 0) → more weight on deontological slot (index 1)."""
    scale = alpha * 0.15
    return np.array([-1.0, 1.0, -0.2], dtype=np.float64) * (-combined) * scale


def apply_horizon_prior_to_engine(
    engine: WeightedEthicsScorer,
    memory: NarrativeMemory,
    context: str,
    action_hint: str = "",
    *,
    genome_weights: tuple[float, float, float],
    max_drift: float = 0.15,
) -> TemporalHorizonSignals:
    """
    Mutates ``engine.hypothesis_weights`` in place after computing signals.

    Clamps each component to ``[g*(1-max_drift), g*(1+max_drift)]`` vs genome, then renormalizes.
    """
    import os
    try:
        alpha = float(os.environ.get("KERNEL_TEMPORAL_HORIZON_ALPHA", "0.08"))
    except (ValueError, TypeError):
        alpha = 0.08
    if not math.isfinite(alpha):
        alpha = 0.08
    alpha = max(0.0, min(0.25, alpha))

    sig = compute_horizon_signals(memory, context, action_hint)
    
    # Boy Scout: Numerical integrity for weights
    w = np.asarray(engine.hypothesis_weights, dtype=np.float64).copy()
    if not np.all(np.isfinite(w)):
        from .weighted_ethics_scorer import DEFAULT_HYPOTHESIS_WEIGHTS
        w = DEFAULT_HYPOTHESIS_WEIGHTS.copy()

    nudge = _nudge_delta(sig.combined, alpha)
    if np.all(np.isfinite(nudge)):
        w += nudge
        
    w = np.maximum(w, 1e-9)
    sum_w = float(np.sum(w))
    if sum_w > 1e-9:
        w /= sum_w
    else:
        from .weighted_ethics_scorer import DEFAULT_HYPOTHESIS_WEIGHTS
        w = DEFAULT_HYPOTHESIS_WEIGHTS.copy()

    g = np.array(genome_weights, dtype=np.float64)
    if not np.all(np.isfinite(g)):
        from .weighted_ethics_scorer import DEFAULT_HYPOTHESIS_WEIGHTS
        g = DEFAULT_HYPOTHESIS_WEIGHTS.copy()

    md = max(0.0, min(0.5, float(max_drift)))
    for i in range(3):
        lo = float(g[i] * (1.0 - md))
        hi = float(g[i] * (1.0 + md))
        w[i] = float(np.clip(w[i], lo, hi))
        
    sum_final = float(np.sum(w))
    if sum_final > 1e-9:
        w /= sum_final
    else:
        w = g.copy()
        
    engine.hypothesis_weights = w
    return sig
