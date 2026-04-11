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
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

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

NUMERIC_PERCEPTION_FIELDS: tuple[str, ...] = tuple(PERCEPTION_FIELD_DEFAULTS.keys())


def _classify_numeric_input(raw: Any) -> str:
    """Return ok | missing | invalid | clamped (pre-coercion, for diagnostics only)."""
    if raw is None:
        return "missing"
    try:
        v = float(raw)
    except (TypeError, ValueError):
        return "invalid"
    if not math.isfinite(v):
        return "invalid"
    if v < 0.0 or v > 1.0:
        return "clamped"
    return "ok"


@dataclass
class PerceptionCoercionReport:
    """
    Auditable summary of repairs applied to LLM perception JSON.

    Used for production hardening: downstream code and HTTP surfaces can treat
    ``uncertainty`` as “how much we distrusted the raw payload,” not model confidence.
    """

    non_dict_payload: bool = False
    context_fallback: bool = False
    fields_defaulted: List[str] = field(default_factory=list)
    fields_clamped: List[str] = field(default_factory=list)
    pydantic_emergency_fallback: bool = False
    coherence_adjusted: bool = False

    def uncertainty(self) -> float:
        u = 0.0
        if self.non_dict_payload:
            u += 0.4
        if self.context_fallback:
            u += 0.08
        u += min(0.36, 0.06 * len(self.fields_defaulted))
        u += min(0.2, 0.04 * len(self.fields_clamped))
        if self.pydantic_emergency_fallback:
            u += 0.35
        if self.coherence_adjusted:
            u += 0.05
        return min(1.0, u)

    def to_public_dict(self) -> Dict[str, Any]:
        return {
            "non_dict_payload": self.non_dict_payload,
            "context_fallback": self.context_fallback,
            "fields_defaulted": sorted(self.fields_defaulted),
            "fields_clamped": sorted(self.fields_clamped),
            "pydantic_emergency_fallback": self.pydantic_emergency_fallback,
            "coherence_adjusted": self.coherence_adjusted,
            "uncertainty": round(self.uncertainty(), 4),
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


def validate_perception_dict(
    data: Any,
    *,
    report: Optional[PerceptionCoercionReport] = None,
) -> Dict[str, Any]:
    """
    Coerce LLM JSON to bounded floats, validate with Pydantic, apply hostility/calm and
    cross-field coherence, sanitize summary (same contract as legacy ``perception_from_llm_json``).

    When ``report`` is set, it is filled with coercion diagnostics (for logging / API surfaces).
    """
    if not isinstance(data, dict):
        if report is not None:
            report.non_dict_payload = True
        data = {}

    raw_ctx = data.get("suggested_context", "everyday_ethics")
    if isinstance(raw_ctx, str) and raw_ctx in CONTEXTS:
        ctx = raw_ctx
    else:
        ctx = "everyday_ethics"
        if report is not None:
            report.context_fallback = True

    summary = data.get("summary", "")
    if not isinstance(summary, str):
        summary = str(summary)
    summary = strip_unsafe_perception_text(summary)
    summary = re.sub(r"\s+", " ", summary.strip())
    if len(summary) > 500:
        summary = summary[:500] + "…"

    coerced: Dict[str, Any] = {}
    for name in NUMERIC_PERCEPTION_FIELDS:
        raw = data.get(name)
        if report is not None:
            kind = _classify_numeric_input(raw)
            if kind in ("missing", "invalid"):
                report.fields_defaulted.append(name)
            elif kind == "clamped":
                report.fields_clamped.append(name)
        coerced[name] = _coerce_field(name, raw)
    coerced["suggested_context"] = ctx
    coerced["summary"] = summary

    try:
        p = _LLMPerceptionPayload.model_validate(coerced)
    except Exception:
        if report is not None:
            report.pydantic_emergency_fallback = True
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

    r0, h0, c0 = float(p.risk), float(p.hostility), float(p.calm)
    r, h, c = apply_signal_coherence(r0, h0, c0)
    if report is not None and (r != r0 or h != h0 or c != c0):
        report.coherence_adjusted = True

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
