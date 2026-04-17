"""
Helpers and small utilities extracted from kernel.py for formatting and environment handling.
"""
import os
import math
from typing import Any

def kernel_env_truthy(name: str) -> bool:
    v = os.environ.get(name, "").strip().lower()
    return v in ("1", "true", "yes", "on")


def kernel_env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def perception_parallel_workers() -> int:
    """
    Worker count for optional perception-side parallel enrichment.
    Enabled only when ``KERNEL_PERCEPTION_PARALLEL`` is truthy. If enabled and
    ``KERNEL_PERCEPTION_PARALLEL_WORKERS`` is unset/invalid, use a conservative
    hardware-aware default.
    """
    if not kernel_env_truthy("KERNEL_PERCEPTION_PARALLEL"):
        return 0
    configured = kernel_env_int("KERNEL_PERCEPTION_PARALLEL_WORKERS", 0)
    if configured > 0:
        return configured
    cpu_n = os.cpu_count() or 2
    return max(2, min(cpu_n, 8))


def perception_coercion_u_value(raw: Any) -> float | None:
    """
    Normalize optional perception coercion uncertainty to [0, 1] or None.
    """
    if raw is None:
        return None
    try:
        u = float(raw)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(u):
        return None
    return max(0.0, min(1.0, u))
