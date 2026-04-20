from __future__ import annotations
import os
import math
from typing import Any, TYPE_CHECKING, Optional, Union
from collections.abc import Mapping

if TYPE_CHECKING:
    from .modules.mock_dao import MockDAO
    from .modules.dao_orchestrator import DAOOrchestrator
    from .modules.bayesian_engine import BayesianEngine
    from .modules.weighted_ethics_scorer import WeightedEthicsScorer


def kernel_env_truthy(name: str) -> bool:
    """
    Check if an environment variable is set to a truthy value (1, true, yes, on).
    Args:
        name: Environment variable name.
    """
    v = os.environ.get(name, "").strip().lower()
    return v in ("1", "true", "yes", "on")


def kernel_env_int(name: str, default: int) -> int:
    """
    Parse an environment variable as an integer with a fallback default.
    Args:
        name: Environment variable name.
        default: Fallback value if unset or invalid.
    """
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def kernel_env_float(
    name: str, default: float, *, min_v: float, max_v: float
) -> float:
    """
    Parse a float from the environment, clamped to ``[min_v, max_v]``; non-finite or
    missing/invalid values yield ``default``.
    """
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        v = float(raw)
    except ValueError:
        return default
    if not math.isfinite(v):
        return default
    return min(max_v, max(min_v, v))


def _safe_unit_float(x: Any, default: float = 0.0) -> float:
    """Coerce a mapping value to a finite float in ``[0.0, 1.0]`` for signal slots."""
    try:
        f = float(x)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(f):
        return default
    return max(0.0, min(1.0, f))


def perception_parallel_workers() -> int:
    """
    Worker count for optional perception-side parallel enrichment.
    Enabled only when ``KERNEL_PERCEPTION_PARALLEL`` is truthy.
    Returns:
        int: Number of workers (2-8) or 0 if disabled.
    """
    if not kernel_env_truthy("KERNEL_PERCEPTION_PARALLEL"):
        return 0
    configured: int = kernel_env_int("KERNEL_PERCEPTION_PARALLEL_WORKERS", 0)
    if configured > 0:
        return configured
    cpu_n: int = os.cpu_count() or 2
    return max(2, min(cpu_n, 8))


def perception_coercion_u_value(raw: Any) -> Optional[float]:
    """
    Normalize optional perception coercion uncertainty to [0, 1] or None.
    Args:
        raw: Input value (float, str, or None).
    """
    if raw is None:
        return None
    try:
        u: float = float(raw)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(u):
        return None
    return max(0.0, min(1.0, u))


def coercion_uncertainty_from_perception(perception: Any) -> float | None:
    """
    Read coercion uncertainty from a perception-like ``coercion_report`` (``dict`` with
    ``"uncertainty"`` or an object with an ``uncertainty`` callable) and normalize via
    :func:`perception_coercion_u_value`.
    """
    cr = getattr(perception, "coercion_report", None)
    raw: Any
    if isinstance(cr, dict):
        raw = cr.get("uncertainty")
    else:
        unc = getattr(cr, "uncertainty", None) if cr is not None else None
        if unc is not None and callable(unc):
            try:
                raw = unc()
            except Exception:
                raw = None
        else:
            raw = None
    return perception_coercion_u_value(raw)


def merge_perception_uncertainty_into_signals(
    signals: Mapping[str, Any] | dict[str, Any], pu: float | None
) -> dict[str, Any] | Mapping[str, Any]:
    """
    I3 — max-merge ``perception_uncertainty`` into ``signals`` for Bayesian stages.
    """
    if pu is None or pu <= 0.0:
        return signals
    out = dict(signals)
    cur = _safe_unit_float(out.get("perception_uncertainty", 0.0), 0.0)
    inc = _safe_unit_float(pu, 0.0)
    if inc <= 0.0:
        return signals
    out["perception_uncertainty"] = max(cur, inc)
    return out


def apply_temporal_eta_urgency_to_signals(
    signals: Mapping[str, Any] | dict[str, Any], perception: Any
) -> dict[str, Any] | Mapping[str, Any]:
    """
    I5 — when ``KERNEL_TEMPORAL_ETA_MODULATION`` is set, increase ``urgency`` from
    ``perception.temporal_context`` (ETA and battery horizon).
    """
    if not kernel_env_truthy("KERNEL_TEMPORAL_ETA_MODULATION"):
        return signals
    tc = getattr(perception, "temporal_context", None)
    if tc is None:
        return signals
    try:
        raw_eta = getattr(tc, "eta_seconds", 300)
        try:
            eta_s = float(raw_eta or 300)
        except (TypeError, ValueError):
            return signals
        if not math.isfinite(eta_s) or eta_s <= 0.0:
            return signals
        bhs = str(getattr(tc, "battery_horizon_state", "nominal") or "nominal")
        ref_eta = kernel_env_float(
            "KERNEL_TEMPORAL_REFERENCE_ETA_S",
            300.0,
            min_v=1.0,
            max_v=86400.0,
        )
        urgency_boost = min(max(ref_eta / max(eta_s, 1.0), 0.0), 1.0)
        if bhs == "critical":
            urgency_boost = min(urgency_boost + 0.3, 1.0)
        if urgency_boost > 0.0:
            out = dict(signals)
            cur_urgency = _safe_unit_float(out.get("urgency", 0.0), 0.0)
            out["urgency"] = min(
                max(cur_urgency + urgency_boost * 0.4, 0.0), 1.0
            )
            return out
    except Exception:
        return signals
    return signals


def enrich_chat_turn_signals_for_bayesian(
    signals: Mapping[str, Any] | dict[str, Any], perception: Any
) -> dict[str, Any] | Mapping[str, Any]:
    """
    Apply I3 (coercion / perception uncertainty) and I5 (temporal urgency) for chat ``aprocess`` paths.
    """
    pu = coercion_uncertainty_from_perception(perception)
    s = merge_perception_uncertainty_into_signals(signals, pu)
    return apply_temporal_eta_urgency_to_signals(s, perception)


def kernel_decision_event_payload(d: Any, *, context: str) -> dict[str, Any]:
    """
    JSON-serialisable dict for :data:`~src.modules.kernel_event_bus.EVENT_KERNEL_DECISION`.
    ``d`` is a :class:`~src.kernel.KernelDecision` (duck-typed to avoid import cycles).
    """
    m = getattr(d, "moral", None)
    return {
        "scenario": (getattr(d, "scenario", None) or "")[:500],
        "place": getattr(d, "place", ""),
        "final_action": getattr(d, "final_action", ""),
        "decision_mode": getattr(d, "decision_mode", ""),
        "blocked": bool(getattr(d, "blocked", False)),
        "block_reason": getattr(d, "block_reason", None) or "",
        "verdict": m.global_verdict.value if m is not None and getattr(m, "global_verdict", None) else None,
        "score": float(m.total_score) if m is not None and getattr(m, "total_score", None) is not None else None,
        "context": context,
    }


def kernel_dao_as_mock(dao: Union[MockDAO, DAOOrchestrator]) -> MockDAO:
    """
    Helper to extract the underlying MockDAO from the DAOOrchestrator.
    Useful for components that require direct local database access.
    """
    from .modules.dao_orchestrator import DAOOrchestrator
    if isinstance(dao, DAOOrchestrator):
        return dao.local_dao
    return dao # type: ignore


def kernel_mixture_scorer(
    bayesian: Union[BayesianEngine, WeightedEthicsScorer]
) -> WeightedEthicsScorer:
    """
    Helper to expose the current WeightedEthicsScorer regardless of the bridge's naming convention.
    """
    from .modules.bayesian_engine import BayesianInferenceEngine
    if isinstance(bayesian, BayesianInferenceEngine):
        return bayesian.scorer
    return bayesian # type: ignore
