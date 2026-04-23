"""
Post-perception signal shaping for chat turns (Block 0.1.3).

Keeps :class:`~src.kernel.EthicalKernel` slimmer: coercion uncertainty (I3) and
temporal ETA urgency modulation (I5) live next to other chat-turn policy helpers.
"""

from __future__ import annotations

import math
import os
from collections.abc import Mapping
from typing import Any

from .signal_coercion import safe_signal_scalar


def _env_truthy(name: str) -> bool:
    v = os.environ.get(name, "").strip().lower()
    return v in ("1", "true", "yes", "on")


def coercion_uncertainty_raw(perception: Any) -> float | None:
    """
    Legacy-compatible extraction; returns a finite float or ``None`` if unusable.

    ``bool`` is not treated as numeric (``float(True)==1.0``) — Pragmatismo V4.0, aligned
    with ``src.kernel_utils.perception_coercion_u_value`` (Plan 8.1.37).
    """
    cr = getattr(perception, "coercion_report", None)
    if isinstance(cr, dict):
        raw = cr.get("uncertainty")
        if raw is None:
            return None
        if type(raw) is bool:
            return None
        try:
            v = float(raw)
        except (TypeError, ValueError):
            return None
        if not math.isfinite(v) or v < 0.0:
            return None
        return v
    if cr is not None and callable(getattr(cr, "uncertainty", None)):
        try:
            u = cr.uncertainty()
        except (TypeError, ValueError):
            return None
        if type(u) is bool:
            return None
        try:
            v = float(u)
        except (TypeError, ValueError):
            return None
        if not math.isfinite(v) or v < 0.0:
            return None
        return v
    return None


def merge_chat_turn_signals_for_ethical_core(
    signals: Mapping[str, Any],
    perception: Any,
) -> dict[str, Any]:
    """
    Copy-on-write merge: coercion uncertainty into ``perception_uncertainty`` (I3)
    and optional temporal ETA boost into ``urgency`` (I5).

    ``perception`` is typically :class:`~src.modules.llm_layer.LLMPerception`; typed as ``Any``
    because tests and call sites attach optional ``temporal_context`` dynamically.

    Scalar components are coerced to finite floats. ``rlhf_features`` (mapping) is preserved
    shallow-copy when present so :func:`~src.modules.rlhf_reward_model.apply_rlhf_modulation_to_bayesian_async`
    can consume MalAbs / semantic gate telemetry on chat turns.
    """
    out: dict[str, Any] = {}
    for k, v in dict(signals).items():
        if k == "rlhf_features" and isinstance(v, Mapping):
            out[k] = dict(v)
        else:
            out[k] = safe_signal_scalar(v)
    pu = coercion_uncertainty_raw(perception)
    if pu is not None and pu > 0.0 and math.isfinite(pu):
        prev = safe_signal_scalar(out.get("perception_uncertainty", 0.0))
        out["perception_uncertainty"] = max(prev, pu)

    if not _env_truthy("KERNEL_TEMPORAL_ETA_MODULATION"):
        return out

    tc = getattr(perception, "temporal_context", None)
    if tc is None:
        return out
    try:
        eta_raw = getattr(tc, "eta_seconds", 300)
        eta_s = safe_signal_scalar(eta_raw, default=300.0)
        eta_s = max(eta_s, 1.0)
        bhs = str(getattr(tc, "battery_horizon_state", "nominal") or "nominal")
        ref_eta = safe_signal_scalar(os.environ.get("KERNEL_TEMPORAL_REFERENCE_ETA_S", "300"), 300.0)
        ref_eta = max(ref_eta, 1.0)
        urgency_boost = min(max(ref_eta / eta_s, 0.0), 1.0)
        if bhs == "critical":
            urgency_boost = min(urgency_boost + 0.3, 1.0)
        if urgency_boost > 0.0 and math.isfinite(urgency_boost):
            cur_urgency = safe_signal_scalar(out.get("urgency", 0.0))
            merged = cur_urgency + urgency_boost * 0.4
            out["urgency"] = safe_signal_scalar(merged, 0.0)
            if out["urgency"] > 1.0:
                out["urgency"] = 1.0
    except (TypeError, ValueError, AttributeError):
        pass
    return out
