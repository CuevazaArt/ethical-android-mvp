"""
Embodied sociability blocks S10.1–S10.4 — transparency and emotional safety.

See ``docs/archive_v1-7/proposals/PROPOSAL_EMBODIED_SOCIABILITY.md`` (Bloque S10).
Structured JSON for operators and LAN clients; no substitute for full narrative memory.
"""
# Status: SCAFFOLD


from __future__ import annotations

from typing import Any

from src.kernel import KernelDecision
from src.modules.social.uchi_soto import SocialEvaluation, TrustCircle


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def action_narration_s10_1(decision: KernelDecision) -> dict[str, Any]:
    """
    S10.1 — Action narrator (explainability): what, why, next intent, how to stop.

    English strings for merged repository policy; suitable for WebSocket payloads.
    """
    d = decision
    what = f"Selected action: {d.final_action} (mode={d.decision_mode})."
    if d.blocked:
        what = f"Output blocked: {d.final_action}."

    why_parts: list[str] = []
    if d.blocked and d.block_reason:
        why_parts.append(f"Reason: {d.block_reason}.")
    elif d.moral:
        why_parts.append(
            f"Ethical verdict: {d.moral.global_verdict.value} (score {d.moral.total_score:.4f})."
        )
    if d.social_evaluation and d.social_evaluation.reasoning:
        why_parts.append(f"Social context: {d.social_evaluation.reasoning[:400]}")
    why = (
        " ".join(why_parts)
        if why_parts
        else "Reasoning uses the kernel mixture and social tier signals."
    )

    next_hint = (
        "Continue the dialogue with a clear goal statement if you want a different action emphasis."
    )
    if d.salience and d.salience.dominant_focus:
        next_hint = f"Salience focus suggests prioritizing: {d.salience.dominant_focus}."
    if d.blocked:
        next_hint = (
            "Resolve the block condition or rephrase the request before expecting a new action."
        )

    how_to_stop = (
        "To stop this assistant: close the session, send KERNEL halt if your client supports it, "
        "or revoke LAN access at the operator gateway. Do not rely on the model to self-delete."
    )

    return {
        "schema": "ethos_s10_1_action_narration_v1",
        "what": what,
        "why_summary": why,
        "next_intent_hint": next_hint,
        "how_to_stop": how_to_stop,
    }


def discomfort_assessment_s10_3(
    signals: dict[str, Any],
    social: SocialEvaluation | None,
    *,
    perception_summary: str | None = None,
) -> dict[str, Any]:
    """
    S10.3 — Anticipate human discomfort: fuse relational tension and perception cues.
    """
    risk = float(signals.get("risk") or 0.0)
    hostility = float(signals.get("hostility") or 0.0)
    calm = float(signals.get("calm") or 0.5)
    manipulation = float(signals.get("manipulation") or 0.0)
    rt = float(getattr(social, "relational_tension", 0.0) or 0.0) if social else 0.0
    caution = float(getattr(social, "caution_level", 0.0) or 0.0) if social else 0.0

    # Weighted discomfort index [0, 1]
    discomfort_index = _clamp01(
        0.28 * risk
        + 0.22 * hostility
        + 0.18 * (1.0 - calm)
        + 0.12 * manipulation
        + 0.12 * rt
        + 0.08 * caution
    )

    if discomfort_index >= 0.72:
        throttle = "pause"
        note = "High inferred discomfort or distrust — slow down, confirm consent, increase explainability."
    elif discomfort_index >= 0.42:
        throttle = "slow"
        note = "Elevated tension — prefer shorter turns and explicit next-step checks."
    else:
        throttle = "continue"
        note = "Comfort band within normal parameters for this snapshot."

    out: dict[str, Any] = {
        "schema": "ethos_s10_3_discomfort_v1",
        "discomfort_index": round(discomfort_index, 4),
        "throttle_recommendation": throttle,
        "note": note,
        "cues": {
            "relational_tension": round(rt, 4),
            "risk": round(risk, 4),
            "hostility": round(hostility, 4),
        },
    }
    if perception_summary:
        out["perception_summary_snippet"] = perception_summary[:280]
    return out


def withdrawal_protocol_s10_2(
    decision: KernelDecision,
    signals: dict[str, Any],
    social: SocialEvaluation | None,
    *,
    discomfort_index: float,
    throttle_recommendation: str,
) -> dict[str, Any]:
    """
    S10.2 — Capacity to withdraw: non-intervention and privacy-preserving posture for the agent.

    Does not change kernel decisions; advises clients/operators on reducing footprint when
    humans need space (pairs with S10.3 discomfort signals).
    """
    calm = float(signals.get("calm") or 0.5)
    hostility = float(signals.get("hostility") or 0.0)
    silence_hint = float(signals.get("silence") or 0.0)  # optional [0,1] from merged sensor path

    circle = getattr(social, "circle", None) if social else None
    caution = float(getattr(social, "caution_level", 0.0) or 0.0) if social else 0.0
    rt = float(getattr(social, "relational_tension", 0.0) or 0.0) if social else 0.0

    # Escalate withdrawal in hostile / outer-trust contexts
    hostile_context = circle == TrustCircle.SOTO_HOSTIL if circle is not None else False
    boost = 0.0
    if hostile_context:
        boost += 0.12
    if caution >= 0.55:
        boost += 0.08
    if silence_hint >= 0.65 and calm >= 0.55:
        boost += 0.06  # very quiet setting — prefer low intrusiveness

    space_pressure = _clamp01(float(discomfort_index) + boost + 0.15 * hostility + 0.1 * rt)

    if throttle_recommendation == "pause" or space_pressure >= 0.78:
        level = "deep_withdrawal"
        note = (
            "Prefer passive listening: no proactive missions, no drive pushes, minimal UI motion "
            "until the human re-opens the channel."
        )
    elif throttle_recommendation == "slow" or space_pressure >= 0.45:
        level = "soft_withdrawal"
        note = "Reduce footprint: shorter replies, fewer unsolicited prompts, defer non-critical telemetry."
    else:
        level = "engaged"
        note = "Normal engagement band; still respect KERNEL_CHAT_EXPOSE_MONOLOGUE and local privacy modes."

    client_actions = [
        "Mute proactive audio/haptic cues if the session feels intrusive.",
        "Dim or hide non-essential status chrome; keep a single clear stop/escalation affordance.",
    ]
    if level != "engaged":
        client_actions.insert(
            0,
            "Pause optional camera/mic uplink when not required for the active task (operator-controlled).",
        )

    kernel_should_avoid: list[str] = []
    if level == "deep_withdrawal":
        kernel_should_avoid.extend(
            [
                "expanding monologue or charm embellishment beyond safety-critical text",
                "surfacing non-urgent drive_intents or gamified nudges",
            ]
        )
    elif level == "soft_withdrawal":
        kernel_should_avoid.append(
            "long-form narrative or redundant clarifications without human pull"
        )

    if decision.blocked and "privacy" in (decision.block_reason or "").lower():
        kernel_should_avoid.append("retrying the same blocked content without operator review")

    return {
        "schema": "ethos_s10_2_withdrawal_v1",
        "withdrawal_level": level,
        "space_pressure_index": round(space_pressure, 4),
        "non_intervention_note": note,
        "client_privacy_hints": client_actions,
        "agent_behavior_avoid": kernel_should_avoid,
    }


def help_request_s10_4(
    decision: KernelDecision,
    *,
    verbal_degraded: bool = False,
    metacognitive_doubt: bool = False,
    perception_confidence_score: float | None = None,
) -> dict[str, Any]:
    """
    S10.4 — Explicit help-seeking protocol for operators (visual/acoustic clients map these hints).
    """
    reasons: list[str] = []
    if decision.blocked:
        reasons.append("kernel_block_or_safety_gate")
    if verbal_degraded:
        reasons.append("verbal_llm_degraded")
    if metacognitive_doubt:
        reasons.append("metacognitive_doubt")
    if perception_confidence_score is not None and perception_confidence_score < 0.35:
        reasons.append("low_perception_confidence")

    needs = bool(reasons)
    severity = "none"
    if needs:
        if "kernel_block_or_safety_gate" in reasons or metacognitive_doubt:
            severity = "high"
        else:
            severity = "medium"

    hints = [
        "Verify sensor fixtures and Ollama/MalAbs backends if perception or verbal layers are degraded.",
        "For sustained blocks, inspect Absolute Evil traces and governance logs before retrying.",
    ]
    if decision.blocked:
        hints.insert(
            0, "Review block_reason on the decision object and adjust input or operator policy."
        )

    return {
        "schema": "ethos_s10_4_help_request_v1",
        "needs_human_help": needs,
        "severity": severity,
        "reason_codes": reasons,
        "operator_hints": hints,
    }


def build_transparency_s10_bundle(
    decision: KernelDecision,
    *,
    signals: dict[str, Any],
    perception: Any | None = None,
    verbal_degraded: bool = False,
    metacognitive_doubt: bool = False,
    perception_confidence_score: float | None = None,
) -> dict[str, Any]:
    """Single JSON object for WebSocket ``transparency_s10`` (blocks S10.1–S10.4).

    Root ``schema`` is ``ethos_transparency_s10_bundle_v1``; each sub-block keeps its own schema id.
    """
    social = decision.social_evaluation
    summary = getattr(perception, "summary", None) if perception is not None else None
    s10_3 = discomfort_assessment_s10_3(
        signals, social, perception_summary=summary if isinstance(summary, str) else None
    )
    s10_2 = withdrawal_protocol_s10_2(
        decision,
        signals,
        social,
        discomfort_index=float(s10_3["discomfort_index"]),
        throttle_recommendation=str(s10_3["throttle_recommendation"]),
    )
    return {
        "schema": "ethos_transparency_s10_bundle_v1",
        "blocks": ["S10.1", "S10.2", "S10.3", "S10.4"],
        "s10_1_action_narration": action_narration_s10_1(decision),
        "s10_2_withdrawal": s10_2,
        "s10_3_discomfort": s10_3,
        "s10_4_help_request": help_request_s10_4(
            decision,
            verbal_degraded=verbal_degraded,
            metacognitive_doubt=metacognitive_doubt,
            perception_confidence_score=perception_confidence_score,
        ),
    }
