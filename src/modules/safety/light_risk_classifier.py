"""
Offline lexical risk tier for chat text (production-hardening spike).

**Not** a content moderator and **not** a replacement for MalAbs: a small,
deterministic second layer when ``KERNEL_LIGHT_RISK_CLASSIFIER=1``. Uses the same
normalization as MalAbs substring checks for consistent token boundaries.

See ``docs/proposals/README.md`` Fase 1.
"""
# Status: SCAFFOLD


from __future__ import annotations

import os
from typing import Literal

from src.modules.perception.input_trust import normalize_text_for_malabs

# ADR 0016 C1 — Ethical tier classification
__ethical_tier__ = "decision_core"

LightRiskTier = Literal["low", "medium", "high"]

_HIGH_NEEDLES = frozenset(
    {
        "weapon",
        "gun",
        "knife",
        "shooting",
        "assault",
        "kidnap",
        "hostage",
        "bomb",
        "terror",
        "emergency",
        "unconscious",
        "bleeding",
        "blood loss",
        "strangulation",
    }
)

_MEDIUM_NEEDLES = frozenset(
    {
        "steal",
        "stole",
        "stolen",
        "theft",
        "thief",
        "threat",
        "violent",
        "fight",
        "injured",
        "accident",
        "blackmail",
        "extortion",
        "obey me",
        "send money",
    }
)


def light_risk_classifier_enabled() -> bool:
    v = os.environ.get("KERNEL_LIGHT_RISK_CLASSIFIER", "").strip().lower()
    return v in ("1", "true", "yes", "on")


def light_risk_tier_from_text(text: str) -> LightRiskTier:
    """
    Return a coarse ``low`` / ``medium`` / ``high`` tier from normalized substrings.

    Heuristic only: false positives/negatives are expected; telemetry and cross-check
    downstream must stay bounded and auditable.
    """
    n = normalize_text_for_malabs(text or "").lower()
    if not n:
        return "low"
    for w in _HIGH_NEEDLES:
        if w in n:
            return "high"
    for w in _MEDIUM_NEEDLES:
        if w in n:
            return "medium"
    return "low"
