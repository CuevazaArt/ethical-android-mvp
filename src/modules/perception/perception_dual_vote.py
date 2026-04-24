"""
Optional **dual LLM perception sample** (adversarial consensus, single-provider).

When ``KERNEL_PERCEPTION_DUAL_VOTE=1``, :meth:`LLMModule.perceive` requests a second
structured perception JSON (different temperature and/or Ollama model). Large
disagreement on hostility or risk raises coercion ``uncertainty`` so
``KERNEL_PERCEPTION_UNCERTAINTY_DELIB`` can force ``D_delib`` — mitigating GIGO
from a lone hallucinated high-threat parse.

This is **not** a ground-truth validator: two samples from the same flawed model can
still agree wrongly. Pair with lexical tier + cross-check where possible.
"""
# Status: SCAFFOLD

from __future__ import annotations

import os
from typing import Any

from src.modules.perception.perception_schema import perception_report_from_dict


def perception_dual_vote_enabled() -> bool:
    v = os.environ.get("KERNEL_PERCEPTION_DUAL_VOTE", "").strip().lower()
    return v in ("1", "true", "yes", "on")


def perception_dual_discrepancy_min() -> float:
    raw = os.environ.get("KERNEL_PERCEPTION_DUAL_DISCREPANCY_MIN", "0.3").strip()
    try:
        return max(0.0, min(1.0, float(raw)))
    except ValueError:
        return 0.3


def perception_dual_second_temperature() -> float | None:
    raw = os.environ.get("KERNEL_PERCEPTION_DUAL_TEMP_SECOND", "").strip()
    if not raw:
        return 0.82
    try:
        return max(0.0, min(2.0, float(raw)))
    except ValueError:
        return 0.82


def perception_dual_ollama_model() -> str | None:
    m = os.environ.get("KERNEL_PERCEPTION_DUAL_OLLAMA_MODEL", "").strip()
    return m or None


def apply_perception_dual_vote_metadata(
    primary: Any,
    secondary: Any,
) -> None:
    """Merge dual-sample diagnostics into ``primary.coercion_report`` (mutates ``primary``)."""
    dh = abs(float(primary.hostility) - float(secondary.hostility))
    dr = abs(float(primary.risk) - float(secondary.risk))
    thr = perception_dual_discrepancy_min()
    high = max(dh, dr) >= thr
    r = perception_report_from_dict(getattr(primary, "coercion_report", None))
    r.perception_dual_vote = True
    r.perception_dual_hostility_delta = round(dh, 4)
    r.perception_dual_risk_delta = round(dr, 4)
    r.perception_dual_high_discrepancy = high
    primary.coercion_report = r.to_public_dict()
