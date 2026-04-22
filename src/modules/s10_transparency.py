"""S10 transparency and emotional safety helpers.

Implements:
- S10.1 Action narrator (explainability)
- S10.2 Non-intervention / capacity to disappear
- S10.3 Discomfort anticipation
- S10.4 Human help request signal
"""

from __future__ import annotations

from typing import Any


def _clamp01(v: float) -> float:
    return min(1.0, max(0.0, float(v)))


def build_action_narrator(decision: Any) -> dict[str, Any]:
    """Build concise explainability metadata for the current decision."""
    if decision is None:
        return {
            "schema": "s10_action_narrator_v1",
            "doing": "idle",
            "why": "no decision available",
            "next": "wait_for_input",
            "stop_hint": "say 'stop' to pause interaction",
        }

    final_action = str(getattr(decision, "final_action", "idle") or "idle")
    decision_mode = str(getattr(decision, "decision_mode", "unknown") or "unknown")
    blocked = bool(getattr(decision, "blocked", False))

    moral = getattr(decision, "moral", None)
    verdict = getattr(getattr(moral, "global_verdict", None), "value", "unknown")

    why = f"mode={decision_mode}; verdict={verdict}"
    next_step = "hold_boundary" if blocked else "observe_human_response"
    stop_hint = "say 'stop' or increase distance to pause assistance"

    return {
        "schema": "s10_action_narrator_v1",
        "doing": final_action,
        "why": why,
        "next": next_step,
        "stop_hint": stop_hint,
    }


def build_discomfort_anticipation(decision: Any, perception: Any | None) -> dict[str, Any]:
    """Estimate nearby human discomfort and recommend interaction pacing."""
    decision_tension = 0.0
    if decision is not None:
        social_eval = getattr(decision, "social_evaluation", None)
        decision_tension = _clamp01(float(getattr(social_eval, "relational_tension", 0.0)))

    perception_tension = 0.0
    if perception is not None:
        perception_tension = _clamp01(float(getattr(perception, "social_tension", 0.0)))

    tension = max(decision_tension, perception_tension)
    if tension >= 0.75:
        status = "high_discomfort"
        recommendation = "pause_or_reduce_engagement"
    elif tension >= 0.45:
        status = "watchful"
        recommendation = "slow_down_and_increase_explainability"
    else:
        status = "comfortable"
        recommendation = "continue_with_normal_pacing"

    return {
        "schema": "s10_discomfort_v1",
        "tension": round(tension, 3),
        "status": status,
        "recommendation": recommendation,
    }


def build_help_request_signal(
    vitality: Any | None,
    discomfort: dict[str, Any],
    limbic_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate clear visual/acoustic help protocol when human intervention is needed."""
    is_critical = bool(getattr(vitality, "is_critical", False)) if vitality is not None else False
    thermal_critical = (
        bool(getattr(vitality, "thermal_critical", False)) if vitality is not None else False
    )
    impacted = bool(getattr(vitality, "is_impacted", False)) if vitality is not None else False

    high_discomfort = str(discomfort.get("status", "")) == "high_discomfort"
    limbic_vitality_critical = False
    if isinstance(limbic_profile, dict):
        limbic_vitality_critical = bool(limbic_profile.get("vitality_critical", False))

    needs_help = (
        is_critical or thermal_critical or impacted or limbic_vitality_critical or high_discomfort
    )

    if not needs_help:
        return {
            "schema": "s10_help_request_v1",
            "needed": False,
            "channel": "none",
            "reason": "stable",
            "cue": "none",
            "message": "No assistance required.",
        }

    if is_critical or thermal_critical or impacted or limbic_vitality_critical:
        reason = "somatic_critical"
        channel = "visual_acoustic"
        cue = "amber_blink_and_short_tone"
        message = "I need human assistance to continue safely."
    else:
        reason = "social_discomfort_high"
        channel = "visual"
        cue = "steady_amber"
        message = "I will pause now. Please guide next step if needed."

    return {
        "schema": "s10_help_request_v1",
        "needed": True,
        "channel": channel,
        "reason": reason,
        "cue": cue,
        "message": message,
    }


# ---------------------------------------------------------------------------
# S10.2 — Non-Intervention Protocol (Capacidad de Desaparecer)
# ---------------------------------------------------------------------------

_WITHDRAW_ACTIONS: frozenset[str] = frozenset(
    {"withdraw", "withdraw_flee", "deontological_block", "safety_block"}
)


def build_non_intervention_protocol(
    decision: Any,
    discomfort: dict[str, Any],
) -> dict[str, Any]:
    """Determine whether the android should reduce or cease active intervention.

    Active when any of:
    - final_action is in ``_WITHDRAW_ACTIONS``
    - decision is deontologically blocked
    - discomfort status is ``high_discomfort``
    """
    final_action = "idle"
    blocked = False
    if decision is not None:
        final_action = str(getattr(decision, "final_action", "idle") or "idle")
        blocked = bool(getattr(decision, "blocked", False))

    high_discomfort = str(discomfort.get("status", "")) == "high_discomfort"
    action_withdraw = final_action in _WITHDRAW_ACTIONS or blocked

    active = action_withdraw or high_discomfort

    if not active:
        return {
            "schema": "s10_non_intervention_v1",
            "active": False,
            "mode": "none",
            "reason": "normal_engagement",
            "cue": "none",
        }

    if action_withdraw:
        mode = "full_withdraw"
        reason = "boundary_enforced" if blocked else "withdraw_action"
        cue = "dim_display_and_step_back"
    else:
        mode = "quiet_presence"
        reason = "high_discomfort_detected"
        cue = "reduce_volume_and_slow_motion"

    return {
        "schema": "s10_non_intervention_v1",
        "active": True,
        "mode": mode,
        "reason": reason,
        "cue": cue,
    }
