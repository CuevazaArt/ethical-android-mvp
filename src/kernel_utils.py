from __future__ import annotations
import os
import math
from typing import Any, TYPE_CHECKING

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
