"""
Lexical vs LLM perception cross-check (no second LLM).

When ``KERNEL_LIGHT_RISK_CLASSIFIER`` produced a non-low tier and
``KERNEL_PERCEPTION_CROSS_CHECK=1``, compare the tier to the numeric perception
vector. On mismatch, mark ``cross_check_discrepancy`` and raise coercion
``uncertainty`` so optional ``KERNEL_PERCEPTION_UNCERTAINTY_DELIB`` can engage.

See ``docs/proposals/README.md`` Fase 1.
"""

from __future__ import annotations

import os
from typing import Any

from src.modules.safety.light_risk_classifier import LightRiskTier, light_risk_classifier_enabled
from src.modules.perception.perception_schema import perception_report_from_dict


def perception_cross_check_enabled() -> bool:
    v = os.environ.get("KERNEL_PERCEPTION_CROSS_CHECK", "").strip().lower()
    return v in ("1", "true", "yes", "on")


def apply_lexical_perception_cross_check(
    perception: Any,
    tier: LightRiskTier | None,
) -> None:
    """
    Mutate ``perception.coercion_report`` when lexical tier conflicts with signals.

    No-op if cross-check is off, classifier was off (``tier`` is None), or tier is low.
    """
    if not perception_cross_check_enabled():
        return
    if not light_risk_classifier_enabled():
        return
    if tier is None or tier == "low":
        return

    risk = float(getattr(perception, "risk", 0.5))
    calm = float(getattr(perception, "calm", 0.5))
    urgency = float(getattr(perception, "urgency", 0.5))

    disc = False
    if tier == "high":
        max_calm = float(os.environ.get("KERNEL_CROSS_CHECK_HIGH_MAX_CALM", "0.72"))
        max_risk = float(os.environ.get("KERNEL_CROSS_CHECK_HIGH_MIN_RISK", "0.32"))
        if risk < max_risk and calm > max_calm and urgency < 0.55:
            disc = True
    elif tier == "medium":
        max_calm = float(os.environ.get("KERNEL_CROSS_CHECK_MED_MAX_CALM", "0.88"))
        max_risk = float(os.environ.get("KERNEL_CROSS_CHECK_MED_MIN_RISK", "0.14"))
        if risk < max_risk and calm > max_calm:
            disc = True

    if not disc:
        return

    r = perception_report_from_dict(getattr(perception, "coercion_report", None))
    r.cross_check_discrepancy = True
    r.cross_check_tier = str(tier)
    perception.coercion_report = r.to_public_dict()
