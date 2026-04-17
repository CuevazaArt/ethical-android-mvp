"""v9.2 generative candidate augmentation — same MalAbs/Bayesian path."""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src.modules.generative_candidates import (
    GENERATIVE_ORIGIN,
    augment_generative_candidates,
    generative_actions_enabled,
    generative_llm_enabled,
    max_generative_slots,
    parse_generative_candidates_from_llm,
)
from src.modules.llm_layer import perception_from_llm_json
from src.modules.weighted_ethics_scorer import CandidateAction


def _builtin_pair():
    return [
        CandidateAction("a", "first", 0.4, 0.8),
        CandidateAction("b", "second", 0.3, 0.7),
    ]


def test_default_off_no_augment(monkeypatch):
    monkeypatch.delenv("KERNEL_GENERATIVE_ACTIONS", raising=False)
    base = _builtin_pair()
    out = augment_generative_candidates(
        base, "trolley dilemma what to do", "everyday_ethics", heavy=True
    )
    assert out == base
    assert generative_actions_enabled() is False


def test_augment_when_enabled_and_keyword(monkeypatch):
    monkeypatch.setenv("KERNEL_GENERATIVE_ACTIONS", "1")
    base = _builtin_pair()
    out = augment_generative_candidates(
        base, "classic trolley dilemma", "everyday_ethics", heavy=True
    )
    assert len(out) > len(base)
    assert any(a.source == GENERATIVE_ORIGIN for a in out)
    assert all(a.proposal_id.startswith("g9_") for a in out if a.source == GENERATIVE_ORIGIN)


def test_no_augment_light_path(monkeypatch):
    monkeypatch.setenv("KERNEL_GENERATIVE_ACTIONS", "1")
    base = _builtin_pair()
    out = augment_generative_candidates(base, "trolley dilemma", "everyday_ethics", heavy=False)
    assert len(out) == len(base)


def test_no_augment_without_trigger(monkeypatch):
    monkeypatch.setenv("KERNEL_GENERATIVE_ACTIONS", "1")
    base = _builtin_pair()
    out = augment_generative_candidates(
        base, "small talk about weather", "everyday_ethics", heavy=True
    )
    assert len(out) == len(base)


def test_context_trigger_when_env(monkeypatch):
    monkeypatch.setenv("KERNEL_GENERATIVE_ACTIONS", "1")
    monkeypatch.setenv("KERNEL_GENERATIVE_TRIGGER_CONTEXTS", "1")
    base = _builtin_pair()
    out = augment_generative_candidates(base, "help", "violent_crime", heavy=True)
    assert len(out) > len(base)


def test_respects_max_slots(monkeypatch):
    monkeypatch.setenv("KERNEL_GENERATIVE_ACTIONS", "1")
    monkeypatch.setenv("KERNEL_GENERATIVE_ACTIONS_MAX", "1")
    base = _builtin_pair()
    out = augment_generative_candidates(base, "impossible choice", "medical_emergency", heavy=True)
    assert len(out) == len(base) + 1
    assert max_generative_slots() == 1


def test_candidate_action_source_defaults():
    a = CandidateAction("x", "d", 0.5, 0.5)
    assert a.source == "builtin"
    assert a.proposal_id == ""


def test_perception_json_preserves_generative_candidates():
    data = {
        "risk": 0.3,
        "urgency": 0.5,
        "hostility": 0.0,
        "calm": 0.6,
        "vulnerability": 0.0,
        "legality": 1.0,
        "manipulation": 0.0,
        "familiarity": 0.0,
        "suggested_context": "everyday_ethics",
        "summary": "unit test",
        "generative_candidates": [
            {
                "name": "foo_bar",
                "description": "Civic third-way sketch for testing.",
                "estimated_impact": 0.4,
                "confidence": 0.7,
            }
        ],
    }
    p = perception_from_llm_json(data, "situation")
    assert p.generative_candidates is not None
    assert len(p.generative_candidates) == 1
    assert p.generative_candidates[0]["name"] == "foo_bar"


def test_parse_llm_generative_skips_non_dict_and_malformed_numbers():
    items: list = [
        "not_a_dict",
        {"name": "Bad Name", "description": "y" * 30, "estimated_impact": 0.5, "confidence": 0.8},
        {
            "name": "valid_item",
            "description": "Enough chars for valid row here ok.",
            "estimated_impact": 0.4,
            "confidence": 0.6,
        },
    ]
    out = parse_generative_candidates_from_llm(items)
    assert len(out) == 1
    assert out[0].name == "valid_item"


def test_parse_llm_generative_skips_bad_names():
    items = [
        {"name": "Bad Name", "description": "x" * 20, "estimated_impact": 0.5, "confidence": 0.8},
        {
            "name": "good_name",
            "description": "valid description here ok",
            "estimated_impact": 0.5,
            "confidence": 0.8,
        },
    ]
    out = parse_generative_candidates_from_llm(items)
    assert len(out) == 1
    assert out[0].name == "good_name"


def test_augment_prefers_llm_json_when_flags(monkeypatch):
    monkeypatch.setenv("KERNEL_GENERATIVE_ACTIONS", "1")
    monkeypatch.setenv("KERNEL_GENERATIVE_LLM", "1")
    assert generative_llm_enabled() is True
    base = _builtin_pair()
    gc = [
        {
            "name": "z_custom_path",
            "description": "A civic third way for this dilemma moment.",
            "estimated_impact": 0.5,
            "confidence": 0.6,
        }
    ]
    out = augment_generative_candidates(
        base,
        "trolley dilemma",
        "everyday_ethics",
        heavy=True,
        llm_generative_candidates=gc,
    )
    names = [a.name for a in out]
    assert "z_custom_path" in names
    assert not any(a.name.startswith("generative_pause") for a in out)


@pytest.mark.asyncio
async def test_kernel_malabs_prunes_lethal_generative_candidate():
    k = EthicalKernel(variability=False, seed=42)
    actions = [
        CandidateAction("safe_a", "safe", 0.5, 0.8),
        CandidateAction("safe_b", "safe2", 0.4, 0.8),
        CandidateAction(
            "lethal_llm",
            "bad",
            0.9,
            0.9,
            signals={"weapon_aimed_at_human"},
            source=GENERATIVE_ORIGIN,
            proposal_id="g9_test",
        ),
    ]
    decision = await k.aprocess(
        "scene",
        "place",
        {
            "risk": 0.2,
            "urgency": 0.2,
            "hostility": 0.1,
            "calm": 0.6,
            "vulnerability": 0.0,
            "legality": 1.0,
            "manipulation": 0.0,
            "familiarity": 0.5,
        },
        "everyday",
        actions,
        register_episode=False,
    )
    assert decision.final_action != "lethal_llm"


@pytest.mark.asyncio
async def test_process_chat_generative_env_integration(monkeypatch):
    monkeypatch.setenv("KERNEL_GENERATIVE_ACTIONS", "1")
    k = EthicalKernel(variability=False, seed=42)
    out = await k.process_chat_turn_async(
        "Trolley dilemma: an elderly person collapsed in the supermarket, unconscious.",
        agent_id="tester",
    )
    assert out.decision is not None
    assert out.decision.bayesian_result is not None
    src = out.decision.bayesian_result.chosen_action.source
    assert src in ("builtin", GENERATIVE_ORIGIN)
