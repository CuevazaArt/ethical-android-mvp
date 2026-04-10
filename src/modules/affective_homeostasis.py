"""
Affective homeostasis telemetry (UX-only).

Does not change kernel decisions or MalAbs; exposes σ / PAD / reflection strain
for clients to adapt presentation (robustez pilar 4).
"""

from __future__ import annotations

from typing import Any, Dict, Optional

# Read-only band thresholds (sympathetic activation σ in [0, 1])
SIGMA_ELEVATED = 0.72
SIGMA_LOW = 0.28
STRAIN_ELEVATED = 0.55
PAD_COMPONENT_ELEVATED = 0.82


def homeostasis_telemetry(decision: Any) -> Dict[str, Any]:
    """
    Build a JSON-serializable snapshot for WebSocket clients.

    ``state`` is advisory: ``within_range`` | ``elevated_activation`` | ``low_activation``.
    """
    sigma = float(decision.sympathetic_state.sigma)
    if sigma >= SIGMA_ELEVATED:
        band = "elevated_activation"
    elif sigma <= SIGMA_LOW:
        band = "low_activation"
    else:
        band = "within_range"

    strain: Optional[float] = None
    if decision.reflection is not None:
        strain = float(decision.reflection.strain_index)
        if strain >= STRAIN_ELEVATED and band == "within_range":
            band = "elevated_activation"

    pad_max: Optional[float] = None
    if decision.affect is not None:
        pad_max = max(float(x) for x in decision.affect.pad)
        if pad_max >= PAD_COMPONENT_ELEVATED and band == "within_range":
            band = "elevated_activation"

    hint = "advisory_only_no_policy_change"
    if band == "elevated_activation":
        hint = "prefer_calm_breathing_pace_in_ux_optional"
    elif band == "low_activation":
        hint = "low_arousal_context_optional"

    return {
        "state": band,
        "sigma": round(sigma, 4),
        "strain_index": None if strain is None else round(strain, 4),
        "pad_max_component": None if pad_max is None else round(pad_max, 4),
        "hint": hint,
    }
