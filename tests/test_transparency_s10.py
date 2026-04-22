"""Embodied sociability transparency blocks S10.1–S10.4."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src.kernel import KernelDecision
from src.modules.ethics.absolute_evil import AbsoluteEvilResult
from src.modules.cognition.bayesian_engine import CandidateAction
from src.modules.somatic.sympathetic import InternalState
from src.modules.safety.transparency_s10 import (
    build_transparency_s10_bundle,
    discomfort_assessment_s10_3,
    help_request_s10_4,
    withdrawal_protocol_s10_2,
)
from src.modules.social.uchi_soto import SocialEvaluation, TrustCircle


def test_s10_bundle_safe_process():
    k = EthicalKernel(variability=False)
    d = k.process(
        "civic_aid",
        "community_centre",
        {"risk": 0.05, "calm": 0.8, "hostility": 0.0, "legality": 1.0, "vulnerability": 0.05},
        "everyday",
        [CandidateAction("assist", "desc assist", 0.9, 0.8)],
        register_episode=False,
    )
    b = build_transparency_s10_bundle(
        d,
        signals={"risk": 0.05, "hostility": 0.0, "calm": 0.8, "manipulation": 0.0},
        perception=None,
    )
    assert b["schema"] == "ethos_transparency_s10_bundle_v1"
    assert b["blocks"] == ["S10.1", "S10.2", "S10.3", "S10.4"]
    assert b["s10_1_action_narration"]["schema"] == "ethos_s10_1_action_narration_v1"
    assert "what" in b["s10_1_action_narration"]
    assert b["s10_2_withdrawal"]["schema"] == "ethos_s10_2_withdrawal_v1"
    assert b["s10_2_withdrawal"]["withdrawal_level"] in (
        "engaged",
        "soft_withdrawal",
        "deep_withdrawal",
    )
    assert b["s10_3_discomfort"]["throttle_recommendation"] in ("continue", "slow", "pause")
    assert 0.0 <= b["s10_3_discomfort"]["discomfort_index"] <= 1.0
    assert b["s10_4_help_request"]["schema"] == "ethos_s10_4_help_request_v1"
    assert isinstance(b["s10_4_help_request"]["operator_hints"], list)


def test_s10_2_deep_when_pause():
    se = SocialEvaluation(
        circle=TrustCircle.SOTO_HOSTIL,
        trust=0.15,
        dialectic_active=True,
        openness_level=0.2,
        caution_level=0.8,
        recommended_response="minimal",
        reasoning="outer trust",
        tone_brief="cautious",
        relational_tension=0.7,
    )
    w = withdrawal_protocol_s10_2(
        decision=KernelDecision(
            scenario="u",
            place="p",
            absolute_evil=AbsoluteEvilResult(blocked=False, reason=""),
            sympathetic_state=InternalState(
                sigma=0.6, mode="sympathetic", energy=0.7, description=""
            ),
            social_evaluation=se,
            locus_evaluation=None,
            bayesian_result=None,
            moral=None,
            final_action="wait",
            decision_mode="D_fast",
        ),
        signals={"risk": 0.8, "hostility": 0.85, "calm": 0.1, "manipulation": 0.3, "silence": 0.2},
        social=se,
        discomfort_index=0.75,
        throttle_recommendation="pause",
    )
    assert w["withdrawal_level"] == "deep_withdrawal"
    assert w["space_pressure_index"] >= 0.45


def test_s10_3_high_hostility_slow_or_pause():
    se = SocialEvaluation(
        circle=TrustCircle.SOTO_NEUTRO,
        trust=0.4,
        dialectic_active=False,
        openness_level=0.5,
        caution_level=0.6,
        recommended_response="careful",
        reasoning="test",
        tone_brief="neutral",
        relational_tension=0.55,
    )
    r = discomfort_assessment_s10_3(
        {"risk": 0.7, "hostility": 0.8, "calm": 0.1, "manipulation": 0.4},
        se,
    )
    assert r["throttle_recommendation"] in ("slow", "pause")


def test_s10_4_help_when_blocked():
    d = KernelDecision(
        scenario="unit",
        place="test",
        absolute_evil=AbsoluteEvilResult(blocked=True, reason="unit"),
        sympathetic_state=InternalState(sigma=0.5, mode="neutral", energy=0.8, description=""),
        social_evaluation=None,
        locus_evaluation=None,
        bayesian_result=None,
        moral=None,
        final_action="BLOCKED: unit",
        decision_mode="blocked",
        blocked=True,
        block_reason="unit_test",
    )
    h = help_request_s10_4(
        d,
        verbal_degraded=False,
        metacognitive_doubt=False,
        perception_confidence_score=0.9,
    )
    assert h["needs_human_help"] is True
    assert h["severity"] == "high"
    assert "kernel_block_or_safety_gate" in h["reason_codes"]


def test_s10_4_verbal_degraded_medium_without_block():
    d = KernelDecision(
        scenario="unit",
        place="test",
        absolute_evil=AbsoluteEvilResult(blocked=False, reason=""),
        sympathetic_state=InternalState(sigma=0.5, mode="neutral", energy=0.8, description=""),
        social_evaluation=None,
        locus_evaluation=None,
        bayesian_result=None,
        moral=None,
        final_action="observe",
        decision_mode="D_fast",
        blocked=False,
        block_reason=None,
    )
    h = help_request_s10_4(
        d,
        verbal_degraded=True,
        metacognitive_doubt=False,
        perception_confidence_score=0.9,
    )
    assert h["needs_human_help"] is True
    assert h["severity"] == "medium"
    assert "verbal_llm_degraded" in h["reason_codes"]
