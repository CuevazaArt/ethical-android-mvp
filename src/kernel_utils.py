"""
Pure string / numeric helpers factored out of :mod:`src.kernel` (MINOR_CONTRIBUTIONS_BACKLOG §5).

No network, no async, no DTOs from the ethical decision cycle—only testable coercions and labels.
Env reads are limited to :func:`os.environ` / :func:`os.cpu_count` (synchronous, deterministic for tests).

Narrowing helpers :func:`kernel_dao_as_mock` and :func:`kernel_mixture_scorer` exist so call sites
(:mod:`chat_server`, :mod:`kernel_pipeline`, tests) get :class:`~src.modules.mock_dao.MockDAO` or
:class:`~src.modules.weighted_ethics_scorer.WeightedEthicsScorer` when the kernel holds a
:class:`~src.modules.dao_orchestrator.DAOOrchestrator` or plain scorer facade.
"""

from __future__ import annotations

import math
import os
from typing import Any

from .modules.bayesian_engine import BayesianEngine
from .modules.dao_orchestrator import DAOOrchestrator
from .modules.mock_dao import MockDAO
from .modules.weighted_ethics_scorer import WeightedEthicsScorer

# Upper bound for operator-provided `KERNEL_PERCEPTION_PARALLEL_WORKERS` (defense in depth
# after `kernel_env_int`; parallel enrichment is best-effort and should not spawn unbounded
# local threads on typos or hostile env).
_MAX_PERCEPTION_PARALLEL_ENV_WORKERS = 64

__all__ = [
    "format_proactive_candidate_line",
    "kernel_dao_as_mock",
    "kernel_env_float",
    "kernel_env_int",
    "kernel_env_truthy",
    "kernel_mixture_scorer",
    "perception_coercion_u_value",
    "perception_parallel_workers",
]


def kernel_dao_as_mock(dao: MockDAO | DAOOrchestrator) -> MockDAO:
    """Return the in-process :class:`MockDAO` for APIs not wrapped by :class:`DAOOrchestrator`."""
    if isinstance(dao, DAOOrchestrator):
        return dao.local_dao
    return dao


def kernel_mixture_scorer(bayesian: BayesianEngine | WeightedEthicsScorer) -> WeightedEthicsScorer:
    """Return the :class:`WeightedEthicsScorer` used for mixture / BMA operations."""
    if isinstance(bayesian, BayesianEngine):
        return bayesian.scorer
    return bayesian


def format_proactive_candidate_line(action: object) -> str:
    """
    One-line label for the top proactive :class:`~src.modules.weighted_ethics_scorer.CandidateAction`
    on the idle ProactivePulse path (Tri-Lobe / ``CorpusCallosumOrchestrator``).

    **EXPERIMENTAL / operator visibility:** coerces non-finite ``estimated_impact`` and
    ``confidence`` so the async idle branch does not format ``nan``/``inf`` into operator
    strings (Pragmatismo V4.0). ``bool`` is not treated as a numeric impact/confidence pair.
    """
    name = getattr(action, "name", None)
    desc = getattr(action, "description", None)
    s_name = (str(name) if name is not None else "?").strip() or "?"
    s_desc = (str(desc) if desc is not None else "").strip() or "—"
    s_desc = " ".join(s_desc.split())
    if len(s_desc) > 200:
        s_desc = f"{s_desc[:197]}..."

    raw_imp = getattr(action, "estimated_impact", 0.0)
    raw_conf = getattr(action, "confidence", 0.5)
    if type(raw_imp) is bool or type(raw_conf) is bool:
        fi, fc = 0.0, 0.5
    else:
        try:
            fi = float(raw_imp)
            fc = float(raw_conf)
        except (TypeError, ValueError):
            fi, fc = 0.0, 0.5
    if not (math.isfinite(fi) and math.isfinite(fc)):
        fi, fc = 0.0, 0.5
    fi = max(-1.0, min(1.0, fi))
    fc = max(0.0, min(1.0, fc))
    return f"{s_name} — {s_desc} (impact={fi:.3f} conf={fc:.3f})"


def kernel_env_truthy(name: str) -> bool:
    v = os.environ.get(name, "").strip().lower()
    return v in ("1", "true", "yes", "on")


def kernel_env_int(name: str, default: int) -> int:
    """
    Read an int from ``os.environ``; return *default* if unset, non-numeric, or if the
    only numeric parse is a non-finite float (``NaN``/``±Inf`` — Harden-In-Place for
    operator env, aligned with :func:`kernel_env_float`).

    Integer strings parse via :func:`int` first. If that fails, a finite :func:`float`
    parse is accepted and truncated toward zero (e.g. ``\"1e2\"`` → ``100``, ``\"3.7\"`` → ``3``).
    """
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        pass
    try:
        f = float(raw)
    except ValueError:
        return default
    if not math.isfinite(f):
        return default
    return int(f)


def kernel_env_float(name: str, default: float) -> float:
    """
    Read a float from ``os.environ``; return *default* if unset, non-numeric, or not finite
    (``NaN``/``±Inf`` are treated as invalid — Harden-In-Place for operator env).
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
    return v


def perception_parallel_workers() -> int:
    """
    Worker count for optional perception-side parallel enrichment (EXPERIMENTAL / local compute).

    Enabled only when ``KERNEL_PERCEPTION_PARALLEL`` is truthy. If enabled and
    ``KERNEL_PERCEPTION_PARALLEL_WORKERS`` is unset/invalid, use a conservative
    hardware-aware default. If set, the value is capped at ``_MAX_PERCEPTION_PARALLEL_ENV_WORKERS`` (module
    constant) to avoid unbounded local threads (operator misconfig or hostile env).
    """
    if not kernel_env_truthy("KERNEL_PERCEPTION_PARALLEL"):
        return 0
    configured = kernel_env_int("KERNEL_PERCEPTION_PARALLEL_WORKERS", 0)
    if configured > 0:
        return min(configured, _MAX_PERCEPTION_PARALLEL_ENV_WORKERS)
    cpu_n = os.cpu_count() or 2
    return max(2, min(cpu_n, 8))


def perception_coercion_u_value(raw: Any) -> float | None:
    """
    Normalize optional perception coercion uncertainty to [0, 1] or None.

    ``bool`` is not accepted as numeric input (``float(True) == 1.0`` would mis-tag
    JSON/flag glitches as full uncertainty; Pragmatismo V4.0).
    """
    if raw is None:
        return None
    if type(raw) is bool:
        return None
    try:
        u = float(raw)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(u):
        return None
    return max(0.0, min(1.0, u))
