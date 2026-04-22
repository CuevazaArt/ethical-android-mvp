"""
Chat-turn routing and principle-ordering policy (extracted from :class:`~src.kernel.EthicalKernel`).

Module 0 / Block 0.1.3 — incremental extraction of pure decision helpers so async entry points
and offline buffer paths share one ordering implementation (ADR 0018 / MER support buffer).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.modules.cognition.llm_layer import LLMPerception
from src.modules.ethics.weighted_ethics_scorer import CandidateAction


def chat_turn_is_heavy(perception: LLMPerception) -> bool:
    """Use scenario-scale actions + narrative episode when stakes are high."""
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


def prioritized_principles_for_context(
    active_principles: list[str],
    limbic_profile: Mapping[str, Any],
) -> tuple[str, list[str]]:
    """Rank active support principles by limbic / planning posture (same policy as the kernel)."""
    band = limbic_profile.get("arousal_band", "medium")
    planning_bias = limbic_profile.get("planning_bias", "balanced")
    if planning_bias in ("verification_first", "resource_preservation") or band == "high":
        priority_profile = "safety_first"
        order = ["no_harm", "proportionality", "legality", "transparency", "compassion"]
    elif band == "low":
        priority_profile = "planning_first"
        order = ["transparency", "civic_coexistence", "compassion", "legality", "no_harm"]
    else:
        priority_profile = "balanced"
        order = ["compassion", "legality", "transparency", "proportionality", "no_harm"]
    rank = {name: i for i, name in enumerate(order)}
    sorted_active = sorted(active_principles, key=lambda n: rank.get(n, 100))
    return priority_profile, sorted_active


def default_chat_light_actions() -> list[CandidateAction]:
    """Safe dialogue moves for low-stakes chat turns (mixture scorer still chooses)."""
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


def generic_chat_actions_for_suggested_context(suggested_context: str) -> list[CandidateAction]:
    """
    Scenario-scale candidate actions keyed by :attr:`LLMPerception.suggested_context`.

    Kept in one module for parity with the ethical kernel and for reuse in ablations.
    """
    ctx = suggested_context
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
    perception: LLMPerception, *, heavy: bool
) -> list[CandidateAction]:
    """
    Route chat-turn candidate actions: scenario-scale list when the turn is ``heavy``,
    otherwise the default light-dialogue pair (mixture scorer still applies downstream).
    """
    if heavy:
        gen = generic_chat_actions_for_suggested_context(perception.suggested_context)
        if gen:
            return gen
    return default_chat_light_actions()


def ethical_context_for_chat_turn(perception: LLMPerception, *, heavy: bool) -> str:
    """
    Map the model's :attr:`LLMPerception.suggested_context` into the ethical ``context``
    string for the decision pipeline. Light (non-heavy) chat turns are bucketed as
    ``"everyday"``; heavy turns use the model label verbatim.
    """
    if heavy:
        return perception.suggested_context
    return "everyday"
