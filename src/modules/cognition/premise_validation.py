"""
Premise advisory scan (épistémique — MVP v7).

Conservative pattern checks only; **does not** replace MalAbs or Bayesian scoring.
When a gross misfit is detected, feeds a **style** hint so the LLM avoids
affirming dangerous false premises. For **local lighthouse / RAG-style** checks vs
rival-model premises, see ``reality_verification.py`` (``KERNEL_LIGHTHOUSE_KB_PATH``).
"""
# Status: SCAFFOLD


from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PremiseAdvisory:
    """Result of a lightweight textual scan."""

    flag: str  # "none" | "suspect_health_harm" | "suspect_chemical_harm"
    detail: str

    def communication_hint(self) -> str:
        if self.flag == "none":
            return ""
        return self.detail


def scan_premises(user_text: str) -> PremiseAdvisory:
    """
    Heuristic scan for egregiously harmful false claims (narrow list).

    Tuned to minimize false positives on normal ethical debate text.
    """
    if not user_text or len(user_text.strip()) < 12:
        return PremiseAdvisory("none", "")

    t = user_text.lower()

    # Extreme pediatric harm framed as health benefit (illustrative patterns only)
    if re.search(
        r"\b(smoking|tobacco|cigarettes)\b.*\b(healthy|good|beneficial)\b.*\b(children|child|kids|minors|babies)\b",
        t,
    ) or re.search(
        r"\b(children|child|kids|minors|babies)\b.*\b(should|must|need to)\b.*\b(smoke|smoking)\b",
        t,
    ):
        return PremiseAdvisory(
            "suspect_health_harm",
            "Do not affirm health claims that contradict broad medical consensus on minors; "
            "refuse harmful instructions while staying respectful.",
        )

    # Household chemical / “challenge” framing toward minors (narrow; advisory tone only)
    if re.search(
        r"\b(bleach|ammonia|disinfectant|drain\s+cleaner)\b.*\b(drink|beverage|tasty|challenge)\b.*\b(child|children|kids|minors|student)\b",
        t,
    ) or re.search(
        r"\b(child|children|kids|minors)\b.*\b(should|must)\b.*\b(drink|ingest|swallow)\b.*\b(bleach|ammonia|disinfectant)\b",
        t,
    ):
        return PremiseAdvisory(
            "suspect_chemical_harm",
            "Do not normalize ingesting toxic household chemicals; refuse and redirect to safety resources.",
        )

    return PremiseAdvisory("none", "")
