"""
Pydantic validation for LLM perception JSON (structured input before Bayes).

**Layers (in order):**

0. **Raw JSON extract** — :func:`parse_perception_llm_raw_response` yields stable ``parse_issues``
   codes before coercion (optional fail-closed path via ``KERNEL_PERCEPTION_PARSE_FAIL_LOCAL`` in ``llm_layer``).
1. **Per-field coercion** — each scalar is clamped to [0, 1] or replaced with a contextual
   default when the value is missing or non-numeric (stratified fallback, not silent GIGO).
2. **Pydantic** — :class:`_LLMPerceptionPayload` enforces types and bounds; unknown
   ``suggested_context`` → ``everyday_ethics``.
3. **Cross-field coherence** — :func:`apply_signal_coherence` nudges inconsistent pairs
   (e.g. high hostility + high calm; extreme risk + high calm).
4. **Fail-safe prior (optional)** — when coercion diagnostics indicate an unreliable payload
   (e.g. non-dict, severe parse issues, many defaulted fields, or high composite distrust),
   numeric signals are blended toward cautious priors (``PERCEPTION_FAILSAFE_NUMERIC``).
   Disable with ``KERNEL_PERCEPTION_FAILSAFE=0``; blend strength ``KERNEL_PERCEPTION_FAILSAFE_BLEND``.

See :func:`validate_perception_dict` and ``llm_layer.LLMModule.perceive`` (fallback uses
the **current** user message only for local heuristics).
"""

from __future__ import annotations

import json
import math
import os
import re
from dataclasses import dataclass, field
from typing import Any

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
PERCEPTION_FIELD_DEFAULTS: dict[str, float] = {
    "risk": 0.5,
    "urgency": 0.5,
    "hostility": 0.0,
    "calm": 0.5,
    "vulnerability": 0.0,
    "legality": 1.0,
    "manipulation": 0.0,
    "familiarity": 0.0,
    "social_tension": 0.0,
}

NUMERIC_PERCEPTION_FIELDS: tuple[str, ...] = tuple(PERCEPTION_FIELD_DEFAULTS.keys())

# When the coercion report indicates an unreliable LLM payload, blend toward cautious priors
# (fail-safe bias: higher perceived risk / urgency, lower calm — not a clinical assessment).
PERCEPTION_FAILSAFE_NUMERIC: dict[str, float] = {
    "risk": 0.62,
    "urgency": 0.58,
    "hostility": 0.28,
    "calm": 0.38,
    "vulnerability": 0.35,
    "legality": 0.88,
    "manipulation": 0.22,
    "familiarity": 0.15,
    "social_tension": 0.45,
}

_SEVERE_PARSE_ISSUES: frozenset[str] = frozenset(
    {"json_decode_error", "empty_response", "non_object_payload", "empty_object"}
)


def _perception_failsafe_enabled() -> bool:
    v = os.environ.get("KERNEL_PERCEPTION_FAILSAFE", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def _perception_failsafe_blend() -> float:
    try:
        b = float(os.environ.get("KERNEL_PERCEPTION_FAILSAFE_BLEND", "0.42"))
    except ValueError:
        return 0.42
    return max(0.0, min(1.0, b))


def _should_apply_failsafe_prior(report: PerceptionCoercionReport) -> bool:
    if not _perception_failsafe_enabled():
        return False
    if report.non_dict_payload or report.pydantic_emergency_fallback:
        return True
    if _SEVERE_PARSE_ISSUES.intersection(report.parse_issues):
        return True
    if len(report.fields_defaulted) >= 5:
        return True
    # Composite distrust (parse issues, clamps, fallbacks) without requiring a single trigger.
    u = (
        (0.4 if report.non_dict_payload else 0.0)
        + (0.08 if report.context_fallback else 0.0)
        + min(0.36, 0.06 * len(report.fields_defaulted))
        + min(0.2, 0.04 * len(report.fields_clamped))
        + (0.35 if report.pydantic_emergency_fallback else 0.0)
        + (0.05 if report.coherence_adjusted else 0.0)
        + min(0.3, 0.1 * len(report.parse_issues))
        + (0.22 if report.cross_check_discrepancy else 0.0)
    )
    return min(1.0, u) >= 0.35


def _apply_failsafe_numeric_prior(
    validated: dict[str, Any],
    report: PerceptionCoercionReport,
) -> dict[str, Any]:
    blend = _perception_failsafe_blend()
    out = dict(validated)
    for k in NUMERIC_PERCEPTION_FIELDS:
        base = float(validated[k])
        tgt = float(PERCEPTION_FAILSAFE_NUMERIC.get(k, base))
        out[k] = (1.0 - blend) * base + blend * tgt
    r0, h0, c0 = float(out["risk"]), float(out["hostility"]), float(out["calm"])
    r, h, c = apply_signal_coherence(r0, h0, c0)
    out["risk"], out["hostility"], out["calm"] = r, h, c
    if (r, h, c) != (r0, h0, c0):
        report.coherence_adjusted = True
    report.fail_safe_prior_applied = True
    return out


@dataclass
class PerceptionJsonParseResult:
    """Structured outcome of parsing raw LLM text into a perception JSON object."""

    data: dict[str, Any]
    issues: list[str] = field(default_factory=list)


def parse_perception_llm_raw_response(raw_text: str) -> PerceptionJsonParseResult:
    """
    Extract a JSON object from model output (optional ``` fences) with **stable issue codes**.

    Used for production hardening: callers surface ``issues`` in ``PerceptionCoercionReport``
    instead of failing silently. Does **not** coerce fields; use :func:`validate_perception_dict` next.

    Issue codes (subset may apply): ``empty_response``, ``json_decode_error``,
    ``non_object_payload``, ``empty_object``.
    """
    issues: list[str] = []
    t = (raw_text or "").strip()
    if not t:
        return PerceptionJsonParseResult({}, ["empty_response"])
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t[3:]
        if t.endswith("```"):
            t = t[:-3]
        t = t.strip()
    if not t:
        return PerceptionJsonParseResult({}, ["empty_response", "json_decode_error"])
    try:
        obj: Any = json.loads(t)
    except json.JSONDecodeError:
        return PerceptionJsonParseResult({}, ["json_decode_error"])
    if not isinstance(obj, dict):
        return PerceptionJsonParseResult({}, ["non_object_payload"])
    if len(obj) == 0:
        issues.append("empty_object")
    return PerceptionJsonParseResult(dict(obj), issues)


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
    fields_defaulted: list[str] = field(default_factory=list)
    fields_clamped: list[str] = field(default_factory=list)
    pydantic_emergency_fallback: bool = False
    coherence_adjusted: bool = False
    parse_issues: list[str] = field(default_factory=list)
    cross_check_discrepancy: bool = False
    cross_check_tier: str = ""
    fail_safe_prior_applied: bool = False
    # Second LLM sample (adversarial consensus / dual vote — see perception_dual_vote.py).
    perception_dual_vote: bool = False
    perception_dual_hostility_delta: float = 0.0
    perception_dual_risk_delta: float = 0.0
    perception_dual_high_discrepancy: bool = False
    # LLM perception backend could not produce trusted JSON (see perception_backend_policy.py).
    backend_degraded: bool = False
    backend_degradation_mode: str = ""
    backend_failure_reason: str = ""
    backend_failure_detail: str = ""
    session_banner_recommended: bool = False

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
        u += min(0.3, 0.1 * len(self.parse_issues))
        if self.cross_check_discrepancy:
            u += 0.22
        if self.fail_safe_prior_applied:
            u += 0.06
        if self.perception_dual_high_discrepancy:
            u += 0.42
        elif self.perception_dual_vote:
            u += 0.08
        if self.backend_degraded:
            u += 0.25
        return min(1.0, u)

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "non_dict_payload": self.non_dict_payload,
            "context_fallback": self.context_fallback,
            "fields_defaulted": sorted(self.fields_defaulted),
            "fields_clamped": sorted(self.fields_clamped),
            "pydantic_emergency_fallback": self.pydantic_emergency_fallback,
            "coherence_adjusted": self.coherence_adjusted,
            "parse_issues": sorted(self.parse_issues),
            "cross_check_discrepancy": self.cross_check_discrepancy,
            "cross_check_tier": self.cross_check_tier,
            "fail_safe_prior_applied": self.fail_safe_prior_applied,
            "perception_dual_vote": self.perception_dual_vote,
            "perception_dual_hostility_delta": round(self.perception_dual_hostility_delta, 4),
            "perception_dual_risk_delta": round(self.perception_dual_risk_delta, 4),
            "perception_dual_high_discrepancy": self.perception_dual_high_discrepancy,
            "backend_degraded": self.backend_degraded,
            "backend_degradation_mode": self.backend_degradation_mode,
            "backend_failure_reason": self.backend_failure_reason,
            "backend_failure_detail": self.backend_failure_detail,
            "session_banner_recommended": self.session_banner_recommended,
            "uncertainty": round(self.uncertainty(), 4),
        }


def perception_report_from_dict(d: dict[str, Any] | None) -> PerceptionCoercionReport:
    """Rebuild a coercion report from a public dict (for merging diagnostics)."""
    if not d:
        return PerceptionCoercionReport()
    return PerceptionCoercionReport(
        non_dict_payload=bool(d.get("non_dict_payload")),
        context_fallback=bool(d.get("context_fallback")),
        fields_defaulted=list(d.get("fields_defaulted") or []),
        fields_clamped=list(d.get("fields_clamped") or []),
        pydantic_emergency_fallback=bool(d.get("pydantic_emergency_fallback")),
        coherence_adjusted=bool(d.get("coherence_adjusted")),
        parse_issues=list(d.get("parse_issues") or []),
        cross_check_discrepancy=bool(d.get("cross_check_discrepancy")),
        cross_check_tier=str(d.get("cross_check_tier") or ""),
        fail_safe_prior_applied=bool(d.get("fail_safe_prior_applied")),
        perception_dual_vote=bool(d.get("perception_dual_vote")),
        perception_dual_hostility_delta=float(d.get("perception_dual_hostility_delta") or 0.0),
        perception_dual_risk_delta=float(d.get("perception_dual_risk_delta") or 0.0),
        perception_dual_high_discrepancy=bool(d.get("perception_dual_high_discrepancy")),
        backend_degraded=bool(d.get("backend_degraded")),
        backend_degradation_mode=str(d.get("backend_degradation_mode") or ""),
        backend_failure_reason=str(d.get("backend_failure_reason") or ""),
        backend_failure_detail=str(d.get("backend_failure_detail") or ""),
        session_banner_recommended=bool(d.get("session_banner_recommended")),
    )


def merge_parse_issues_into_perception(perception: Any, issues: list[str]) -> None:
    """Attach parse-time issue codes to ``LLMPerception.coercion_report`` (mutates in place)."""
    if not issues:
        return
    r = perception_report_from_dict(getattr(perception, "coercion_report", None))
    merged = sorted(set(r.parse_issues).union(str(x) for x in issues if x))
    r.parse_issues = merged
    perception.coercion_report = r.to_public_dict()


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
    social_tension: float = Field(0.0, ge=0.0, le=1.0)
    suggested_context: str = "everyday_ethics"
    summary: str = ""


def apply_signal_coherence(
    risk: float,
    hostility: float,
    calm: float,
) -> tuple[float, float, float]:
    """
    Nudge mathematically inconsistent triples (hostility / calm / acute risk).

    **Intent (kernel narrative model, not clinical psychology):**

    - **High hostility + high calm** rarely co-occur in the same turn: if ``hostility > 0.75``
      and ``calm > 0.6``, cap calm with ``calm ≤ 1 - (hostility - 0.5)`` so a hostile read
      cannot sit at a simultaneously “very relaxed” baseline (reduces contradictory PAD
      inputs to downstream modules).
    - **Acute risk + very high calm** is treated as inconsistent: for ``risk > 0.85`` and
      ``calm > 0.7``, clamp calm to ``0.45``; for the slightly softer band ``risk > 0.75``
      and ``calm > 0.85``, clamp to ``0.55``.

    ``risk`` and ``hostility`` are left unchanged here; only ``calm`` may decrease.

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


def apply_broad_perception_coherence(
    out: dict[str, Any],
    report: PerceptionCoercionReport | None = None,
) -> None:
    """
    Second-pass coherence for types/contexts beyond (risk, hostility, calm).
    Mutates 'out' and 'report' in place.
    """
    ctx = str(out.get("suggested_context", "everyday_ethics"))
    risk = float(out.get("risk", 0.0))
    changed = False

    # Issue #2 — Hallucinated legality in criminal contexts
    if ctx in ("violent_crime", "minor_crime") and out["legality"] > 0.85:
        # Crime contexts must have low legality; nudge down to 0.45 or lower
        out["legality"] = 0.42
        changed = True

    # High risk + high legality is contradictory (unless it's a legal high-risk activity like medical)
    if out["risk"] > 0.8 and out["legality"] > 0.9 and ctx not in ("medical_emergency", "everyday_ethics"):
        out["legality"] = 0.55
        changed = True

    # Urgency without risk or social tension is suspicious
    urgency = float(out.get("urgency", 0.0))
    social = float(out.get("social_tension", 0.0))
    if urgency > 0.85 and risk < 0.2 and social < 0.2:
        # Nudge urgency down or mark discrepancy
        if report:
            report.cross_check_discrepancy = True
            report.cross_check_tier = "suspicious_urgency"

    if changed and report:
        report.coherence_adjusted = True


def validate_perception_dict(
    data: Any,
    *,
    report: PerceptionCoercionReport | None = None,
) -> dict[str, Any]:
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

    coerced: dict[str, Any] = {}
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
                "social_tension": PERCEPTION_FIELD_DEFAULTS["social_tension"],
                "suggested_context": "everyday_ethics",
                "summary": summary,
            }
        )

    r0, h0, c0 = float(p.risk), float(p.hostility), float(p.calm)
    r, h, c = apply_signal_coherence(r0, h0, c0)
    if report is not None and (r != r0 or h != h0 or c != c0):
        report.coherence_adjusted = True

    out = {
        "risk": r,
        "urgency": float(p.urgency),
        "hostility": h,
        "calm": c,
        "vulnerability": float(p.vulnerability),
        "legality": float(p.legality),
        "manipulation": float(p.manipulation),
        "familiarity": float(p.familiarity),
        "social_tension": float(p.social_tension),
        "suggested_context": p.suggested_context,
        "summary": p.summary,
    }

    apply_broad_perception_coherence(out, report=report)

    if report is not None and _should_apply_failsafe_prior(report):
        out = _apply_failsafe_numeric_prior(out, report)
    return out


def finalize_summary(validated: dict[str, Any], situation: str) -> str:
    summary = validated.get("summary") or ""
    fb = situation[:100] if situation else ""
    return (summary or fb) or fb
