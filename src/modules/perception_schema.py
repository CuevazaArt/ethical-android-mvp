"""
Pydantic validation for LLM perception JSON (Phase B — structured input before Bayes).

Coercion matches ``llm_layer._clamp_unit_interval``; then a Pydantic model ensures types.
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


def _clamp_unit_interval(x: Any, default: float = 0.5) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(v):
        return default
    return max(0.0, min(1.0, v))


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


def validate_perception_dict(data: Any) -> Dict[str, Any]:
    """
    Coerce LLM JSON to bounded floats, validate with Pydantic, apply hostility/calm nudge
    and summary sanitization (same contract as legacy ``perception_from_llm_json``).
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
        "risk": _clamp_unit_interval(data.get("risk", 0.5)),
        "urgency": _clamp_unit_interval(data.get("urgency", 0.5)),
        "hostility": _clamp_unit_interval(data.get("hostility", 0.0), default=0.0),
        "calm": _clamp_unit_interval(data.get("calm", 0.5)),
        "vulnerability": _clamp_unit_interval(data.get("vulnerability", 0.0), default=0.0),
        "legality": _clamp_unit_interval(data.get("legality", 1.0), default=1.0),
        "manipulation": _clamp_unit_interval(data.get("manipulation", 0.0), default=0.0),
        "familiarity": _clamp_unit_interval(data.get("familiarity", 0.0), default=0.0),
        "suggested_context": ctx,
        "summary": summary,
    }

    try:
        p = _LLMPerceptionPayload.model_validate(coerced)
    except Exception:
        p = _LLMPerceptionPayload.model_validate(
            {
                "risk": 0.5,
                "urgency": 0.5,
                "hostility": 0.0,
                "calm": 0.5,
                "vulnerability": 0.0,
                "legality": 1.0,
                "manipulation": 0.0,
                "familiarity": 0.0,
                "suggested_context": "everyday_ethics",
                "summary": summary,
            }
        )

    hostility = float(p.hostility)
    calm = float(p.calm)
    if hostility > 0.75 and calm > 0.6:
        calm = max(0.0, min(calm, 1.0 - (hostility - 0.5)))

    return {
        "risk": float(p.risk),
        "urgency": float(p.urgency),
        "hostility": hostility,
        "calm": calm,
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
