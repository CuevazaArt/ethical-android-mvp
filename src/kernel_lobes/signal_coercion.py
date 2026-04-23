"""
Shared numeric coercion for kernel signal vectors (Module 0 / Block 0.1.3).

Used by limbic profile policy and LLM perception → signal dict mapping so corrupt model
outputs cannot inject NaN/Inf or crash downstream scoring.
"""

from __future__ import annotations

import math
from typing import Any


def safe_signal_scalar(value: Any, default: float = 0.0) -> float:
    """Coerce a perception signal component to a finite float."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(v):
        return default
    return v
