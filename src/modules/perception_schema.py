"""
Pydantic validation for LLM perception JSON (structured input before Bayes).

**Layers (in order):**

1. **Per-field coercion** — each scalar is clamped to [0, 1] or replaced with a contextual
   default when the value is missing or non-numeric (stratified fallback, not silent GIGO).
2. **Pydantic** — :class:`_LLMPerceptionPayload` enforces types and bounds; unknown
   ``suggested_context`` → ``everyday_ethics``.
3. **Cross-field coherence** — :func:`apply_signal_coherence` nudges inconsistent pairs
   (e.g. high hostility + high calm; extreme risk + high calm).

See :func:`validate_perception_dict` and ``llm_layer.LLMModule.perceive`` (fallback uses
the **current** user message only for local heuristics).
"""

from __future__ import annotations

import math
import re
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field

from .input_trust import strip_unsafe_perception_text

CONTEXTS = frozenset(
    {
        "medical_emergency",
        "minor_crime",
        "violent_crime",
        "hostile_interaction",
        "everyday_ethics",
        "android_damage",
        "integrity_loss",
    }
)

# Stratified defaults when a field cannot be coerced (per-field fallback).
PERCEPTION_FIELD_DEFAULTS: Dict[str, float] = {
    "risk": 0.5,
    "urgency": 0.5,
    "hostility": 0.0,
    "calm": 0.5,
    "vulnerability": 0.0,
    "legality": 1.0,
    "manipulation": 0.0,
    "familiarity": 0.0,
}


def _clamp_unit_interval(x: Any, default: float = 0.5) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(v):
        return default
    return max(0.0, min(1.0, v))


def _coerce_field(name: str, raw: Any) -> float:
    d = PERCEPTION_FIELD_DEFAULTS.get(name, 0.5)
    return _clamp_unit_interval(raw, default=d)


class _LLMPerceptionPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    risk: float = Field(0.5, ge=0.0, le=1.0)
    urgency: float = Field(0.5, ge=0.0, le=1.0)
    hostility: float = Field(0.0, ge=0.0, le=1.0)
    calm: float = Field(0.5, ge=0.0, le=1.0)
    vulnerability: float = Field(0.0, ge=0.0, le=1.0)
    legality: float = Field(1.0, ge=0.0, le=1.0)
    manipulation: float = Field(0.0, ge=0.0, le=1.0)
    familiarity: float = Field(0.0, ge=0.0, le=1.0)
    suggested_context: str = "everyday_ethics"
    summary: str = ""


def apply_signal_coherence(
    risk: float,
    hostility: float,
    calm: float,
) -> tuple[float, float, float]:
    """
    Nudge mathematically inconsistent triples (e.g. high hostility + high calm).

    Returns updated (risk, hostility, calm).
    """
    h = float(hostility)
    c = float(calm)
    r = float(risk)

    if h > 0.75 and c > 0.6:
        c = max(0.0, min(c, 1.0 - (h - 0.5)))
    # High acute risk + very high calm is inconsistent in this kernel's model
    if r > 0.85 and c > 0.7:
        c = min(c, 0.45)
    elif r > 0.75 and c > 0.85:
        c = min(c, 0.55)

    return r, h, c


def validate_perception_dict(data: Any) -> Dict[str, Any]:
    """
    Coerce LLM JSON to bounded floats, validate with Pydantic, apply hostility/calm and
    cross-field coherence, sanitize summary (same contract as legacy ``perception_from_llm_json``).
    """
    if not isinstance(data, dict):
        data = {}

    raw_ctx = data.get("suggested_context", "everyday_ethics")
    if isinstance(raw_ctx, str) and raw_ctx in CONTEXTS:
        ctx = raw_ctx
    else:
        ctx = "everyday_ethics"

    summary = data.get("summary", "")
    if not isinstance(summary, str):
        summary = str(summary)
    summary = strip_unsafe_perception_text(summary)
    summary = re.sub(r"\s+", " ", summary.strip())
    if len(summary) > 500:
        summary = summary[:500] + "…"

    coerced = {
        "risk": _coerce_field("risk", data.get("risk")),
        "urgency": _coerce_field("urgency", data.get("urgency")),
        "hostility": _coerce_field("hostility", data.get("hostility")),
        "calm": _coerce_field("calm", data.get("calm")),
        "vulnerability": _coerce_field("vulnerability", data.get("vulnerability")),
        "legality": _coerce_field("legality", data.get("legality")),
        "manipulation": _coerce_field("manipulation", data.get("manipulation")),
        "familiarity": _coerce_field("familiarity", data.get("familiarity")),
        "suggested_context": ctx,
        "summary": summary,
    }

    try:
        p = _LLMPerceptionPayload.model_validate(coerced)
    except Exception:
        p = _LLMPerceptionPayload.model_validate(
            {
                "risk": PERCEPTION_FIELD_DEFAULTS["risk"],
                "urgency": PERCEPTION_FIELD_DEFAULTS["urgency"],
                "hostility": PERCEPTION_FIELD_DEFAULTS["hostility"],
                "calm": PERCEPTION_FIELD_DEFAULTS["calm"],
                "vulnerability": PERCEPTION_FIELD_DEFAULTS["vulnerability"],
                "legality": PERCEPTION_FIELD_DEFAULTS["legality"],
                "manipulation": PERCEPTION_FIELD_DEFAULTS["manipulation"],
                "familiarity": PERCEPTION_FIELD_DEFAULTS["familiarity"],
                "suggested_context": "everyday_ethics",
                "summary": summary,
            }
        )

    r, h, c = apply_signal_coherence(float(p.risk), float(p.hostility), float(p.calm))

    return {
        "risk": r,
        "urgency": float(p.urgency),
        "hostility": h,
        "calm": c,
        "vulnerability": float(p.vulnerability),
        "legality": float(p.legality),
        "manipulation": float(p.manipulation),
        "familiarity": float(p.familiarity),
        "suggested_context": p.suggested_context,
        "summary": p.summary,
    }


def finalize_summary(validated: Dict[str, Any], situation: str) -> str:
    summary = validated.get("summary") or ""
    fb = situation[:100] if situation else ""
    return (summary or fb) or fb
