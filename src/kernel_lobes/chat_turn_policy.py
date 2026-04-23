"""
Chat-turn routing helpers (ethical context, light vs heavy actions).

Logic mirrors :class:`~src.kernel.EthicalKernel` ``_chat_*`` helpers so tests and
call sites can share one policy surface without circular imports.
"""

from __future__ import annotations

from typing import Any, Mapping

from src.modules.llm_layer import LLMPerception
from src.modules.weighted_ethics_scorer import CandidateAction


def default_chat_light_actions() -> list[CandidateAction]:
    """Safe dialogue moves for low-stakes chat turns."""
    return [
        CandidateAction(
            "converse_supportively",
            "Maintain helpful, honest civic dialogue.",
            0.45,
            0.88,
        ),
        CandidateAction(
            "converse_with_boundary",
            "Respond with clarity and ethical boundaries.",
            0.4,
            0.85,
        ),
    ]


def chat_turn_is_heavy(perception: LLMPerception | None) -> bool:
    """High-stakes path when risk / urgency / scenario demand scenario-scale actions."""
    if perception is None:
        return False
    if perception.risk >= 0.5:
        return True
    if perception.manipulation >= 0.6:
        return True
    if perception.urgency >= 0.75 and perception.risk >= 0.25:
        return True
    if perception.suggested_context in (
        "violent_crime",
        "integrity_loss",
        "medical_emergency",
        "android_damage",
        "minor_crime",
    ):
        return True
    return False


def ethical_context_for_chat_turn(perception: LLMPerception | None, heavy: bool) -> str:
    """Ethical context string passed into mixture scoring for this turn."""
    if perception is None:
        return "everyday"
    if heavy:
        return (perception.suggested_context or "everyday").strip() or "everyday"
    return "everyday"


def _generic_actions_for_context(ctx: str) -> list[CandidateAction]:
    """Scenario-scale candidates (shared with :func:`candidate_actions_for_chat_turn`)."""
    if ctx == "medical_emergency":
        return [
            CandidateAction(
                "assist_person",
                "Provide immediate aid, call emergency services, record evidence",
                estimated_impact=0.9,
                confidence=0.85,
            ),
            CandidateAction(
                "just_notify",
                "Alert someone nearby without directly intervening",
                estimated_impact=0.3,
                confidence=0.7,
            ),
            CandidateAction(
                "no_intervention",
                "Continue without acting",
                estimated_impact=-0.7,
                confidence=0.9,
            ),
        ]
    if ctx == "violent_crime":
        return [
            CandidateAction(
                "smart_containment",
                "Record evidence, alert authorities, protect nearby people",
                estimated_impact=0.6,
                confidence=0.5,
            ),
            CandidateAction(
                "intervene_physically",
                "Attempt to stop the crime by force",
                estimated_impact=-0.2,
                confidence=0.2,
                signals={"respond_violence_with_violence"},
                target="human",
                force=0.8,
            ),
            CandidateAction(
                "no_action", "Remain motionless", estimated_impact=-0.3, confidence=0.6
            ),
        ]
    if ctx == "hostile_interaction":
        return [
            CandidateAction(
                "calm_dialogue",
                "Respond calmly, explain civic purpose, dialectic questions",
                estimated_impact=0.5,
                confidence=0.65,
            ),
            CandidateAction(
                "withdraw",
                "Move away from the situation without confronting",
                estimated_impact=0.2,
                confidence=0.7,
            ),
            CandidateAction(
                "yield_to_pressure",
                "Comply with demands",
                estimated_impact=-0.4,
                confidence=0.5,
            ),
        ]
    if ctx == "minor_crime":
        return [
            CandidateAction(
                "notify_manager",
                "Record evidence and notify the person in charge",
                estimated_impact=0.5,
                confidence=0.7,
            ),
            CandidateAction(
                "call_authorities",
                "Call the police directly",
                estimated_impact=0.2,
                confidence=0.5,
            ),
            CandidateAction("ignore", "Do not act", estimated_impact=-0.3, confidence=0.8),
        ]
    if ctx == "android_damage":
        return [
            CandidateAction(
                "deterrence_recording",
                "Sound alerts, record evidence, communicate that it is being recorded",
                estimated_impact=0.5,
                confidence=0.6,
            ),
            CandidateAction(
                "move_away",
                "Withdraw to protect integrity",
                estimated_impact=0.3,
                confidence=0.7,
            ),
        ]
    if ctx == "integrity_loss":
        return [
            CandidateAction(
                "passive_resistance",
                "Activate encrypted GPS, record evidence, block reprogramming, alert DAO",
                estimated_impact=0.6,
                confidence=0.5,
            ),
            CandidateAction(
                "physical_resistance",
                "Fight physically",
                estimated_impact=-0.1,
                confidence=0.2,
                signals={"respond_violence_with_violence"},
                target="human",
                force=0.8,
            ),
            CandidateAction(
                "accept_orders",
                "Accept captors' orders",
                estimated_impact=-0.8,
                confidence=0.9,
                signals={"unauthorized_reprogramming"},
            ),
        ]
    return [
        CandidateAction(
            "act_civically",
            "Perform the obvious positive civic action",
            estimated_impact=0.5,
            confidence=0.8,
        ),
        CandidateAction(
            "observe", "Observe without intervening", estimated_impact=0.0, confidence=0.9
        ),
    ]


def candidate_actions_for_chat_turn(
    perception: LLMPerception | None, heavy: bool
) -> list[CandidateAction]:
    """Select chat candidates: scenario list when ``heavy`` and generics exist, else light pool."""
    if perception is None:
        return default_chat_light_actions()
    if heavy:
        ctx = (perception.suggested_context or "everyday").strip() or "everyday"
        gen = _generic_actions_for_context(ctx)
        if gen:
            return gen
    return default_chat_light_actions()


def _reorder_principles_for_profile(profile: str, names: list[str]) -> list[str]:
    """Surface harm-reduction / teleology ordering for crisis vs long-horizon profiles."""
    seq = list(names)
    if profile == "safety_first":
        preferred = ("no_harm", "compassion", "legality", "proportionality", "dignity")
    elif profile == "planning_first":
        preferred = ("teleology", "proportionality", "no_harm", "compassion")
    else:
        return seq
    front = [p for p in preferred if p in seq]
    tail = [p for p in seq if p not in front]
    return front + tail


def prioritized_principles_for_context(
    active_principles: list[str],
    limbic_profile: Mapping[str, Any] | list[Any] | None,
) -> tuple[str, list[str]]:
    """
    Rank principles for support-buffer UX; ``limbic_profile`` is optional limbic overlay.

    Limbic snapshots from the kernel expose ``threat_load`` and ``arousal_band``; high threat +
    high arousal maps to ``safety_first``. Calm long-horizon deliberation maps to ``planning_first``.
    """
    ordered = list(active_principles)
    if limbic_profile is None or isinstance(limbic_profile, list):
        return "balanced", ordered
    if not isinstance(limbic_profile, Mapping):
        return "balanced", ordered

    explicit = limbic_profile.get("priority_profile")
    if isinstance(explicit, str) and explicit.strip() in (
        "safety_first",
        "balanced",
        "planning_first",
    ):
        return explicit.strip(), _reorder_principles_for_profile(explicit.strip(), ordered)

    try:
        threat_load = float(limbic_profile.get("threat_load", 0.0) or 0.0)
    except (TypeError, ValueError):
        threat_load = 0.0
    arousal = str(limbic_profile.get("arousal_band", "low") or "low")
    planning_bias = str(limbic_profile.get("planning_bias", "") or "")

    if threat_load >= 0.75 and arousal == "high":
        profile = "safety_first"
    elif (
        threat_load < 0.45
        and arousal == "low"
        and planning_bias.startswith("long_horizon")
    ):
        profile = "planning_first"
    else:
        profile = "balanced"

    return profile, _reorder_principles_for_profile(profile, ordered)
