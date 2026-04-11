"""
Qualitative long-horizon consequence hints (teleología — MVP v7).

Three narrative branches without Monte Carlo. **Numeric** feedback into the Bayesian
mixture is a **separate** path: :mod:`temporal_horizon_prior` (ADR 0005) when
``KERNEL_TEMPORAL_HORIZON_PRIOR`` is enabled — see ``docs/TEMPORAL_PRIOR_HORIZONS.md``.

These strings remain advisory / UX and LLM tone only.
"""

from __future__ import annotations

from typing import Dict


def qualitative_temporal_branches(
    action: str,
    verdict: str,
    context_label: str,
) -> Dict[str, str]:
    a = action.replace("_", " ")
    ctx = context_label or "general"
    return {
        "horizon_immediate": (
            f"Immediate: action '{a}' with verdict {verdict} shapes the present moment "
            f"and visible civic stance in this {ctx} context."
        ),
        "horizon_weeks": (
            f"Weeks: repeated patterns around '{a}' may affect trust and expectations "
            f"of consistency in similar {ctx} situations."
        ),
        "horizon_long_term": (
            f"Long arc: habits reinforced by choices like '{a}' influence autonomy, "
            "reputation, and community norms—qualitative, not numerically predicted."
        ),
        "note": "qualitative_only_no_monte_carlo",
    }
