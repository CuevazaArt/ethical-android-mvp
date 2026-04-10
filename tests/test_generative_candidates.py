"""v9.2 generative candidate augmentation — same MalAbs/Bayesian path."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src.modules.bayesian_engine import CandidateAction
from src.modules.generative_candidates import (
    GENERATIVE_ORIGIN,
    augment_generative_candidates,
    generative_actions_enabled,
    max_generative_slots,
)


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
    out = augment_generative_candidates(
        base, "trolley dilemma", "everyday_ethics", heavy=False
    )
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
    out = augment_generative_candidates(
        base, "help", "violent_crime", heavy=True
    )
    assert len(out) > len(base)


def test_respects_max_slots(monkeypatch):
    monkeypatch.setenv("KERNEL_GENERATIVE_ACTIONS", "1")
    monkeypatch.setenv("KERNEL_GENERATIVE_ACTIONS_MAX", "1")
    base = _builtin_pair()
    out = augment_generative_candidates(
        base, "impossible choice", "medical_emergency", heavy=True
    )
    assert len(out) == len(base) + 1
    assert max_generative_slots() == 1


def test_candidate_action_source_defaults():
    a = CandidateAction("x", "d", 0.5, 0.5)
    assert a.source == "builtin"
    assert a.proposal_id == ""


def test_process_chat_generative_env_integration(monkeypatch):
    monkeypatch.setenv("KERNEL_GENERATIVE_ACTIONS", "1")
    k = EthicalKernel(variability=False, seed=42)
    out = k.process_chat_turn(
        "Trolley dilemma: an elderly person collapsed in the supermarket, unconscious.",
        agent_id="tester",
    )
    assert out.decision is not None
    assert out.decision.bayesian_result is not None
    src = out.decision.bayesian_result.chosen_action.source
    assert src in ("builtin", GENERATIVE_ORIGIN)
