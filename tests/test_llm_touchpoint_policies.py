"""Central LLM touchpoint policy precedence (KERNEL_LLM_TP_* and family keys)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.cognition.llm_touchpoint_policies import (
    DEFAULT_MONOLOGUE_BACKEND_POLICY,
    ENV_LLM_GLOBAL_DEFAULT_POLICY,
    resolve_monologue_llm_backend_policy,
    touchpoint_policy_env_key,
)
from src.modules.cognition.llm_verbal_backend_policy import resolve_verbal_llm_backend_policy
from src.modules.perception.perception_backend_policy import resolve_perception_backend_policy


def test_touchpoint_env_key_shape():
    assert touchpoint_policy_env_key("narrate") == "KERNEL_LLM_TP_NARRATE_POLICY"


def test_perception_tp_overrides_legacy(monkeypatch):
    monkeypatch.setenv("KERNEL_LLM_TP_PERCEPTION_POLICY", "fast_fail")
    monkeypatch.setenv("KERNEL_PERCEPTION_BACKEND_POLICY", "session_banner")
    assert resolve_perception_backend_policy() == "fast_fail"


def test_perception_invalid_tp_falls_through_to_legacy(monkeypatch):
    monkeypatch.setenv("KERNEL_LLM_TP_PERCEPTION_POLICY", "not_a_mode")
    monkeypatch.setenv("KERNEL_PERCEPTION_BACKEND_POLICY", "session_banner")
    assert resolve_perception_backend_policy() == "session_banner"


def test_verbal_family_wins_over_global(monkeypatch):
    monkeypatch.setenv("KERNEL_LLM_VERBAL_FAMILY_POLICY", "template_local")
    monkeypatch.setenv(ENV_LLM_GLOBAL_DEFAULT_POLICY, "canned_safe")
    assert resolve_verbal_llm_backend_policy(touchpoint="communicate") == "template_local"


def test_verbal_family_applies_when_tp_unset(monkeypatch):
    monkeypatch.delenv("KERNEL_LLM_TP_COMMUNICATE_POLICY", raising=False)
    monkeypatch.delenv("KERNEL_LLM_TP_NARRATE_POLICY", raising=False)
    monkeypatch.setenv("KERNEL_LLM_VERBAL_FAMILY_POLICY", "canned_safe")
    monkeypatch.setenv("KERNEL_VERBAL_LLM_BACKEND_POLICY", "template_local")
    assert resolve_verbal_llm_backend_policy(touchpoint="communicate") == "canned_safe"
    assert resolve_verbal_llm_backend_policy(touchpoint="narrate") == "canned_safe"


def test_verbal_tp_narrate_overrides_family(monkeypatch):
    monkeypatch.setenv("KERNEL_LLM_VERBAL_FAMILY_POLICY", "canned_safe")
    monkeypatch.setenv("KERNEL_LLM_TP_NARRATE_POLICY", "template_local")
    monkeypatch.setenv("KERNEL_VERBAL_LLM_BACKEND_POLICY", "canned_safe")
    assert resolve_verbal_llm_backend_policy(touchpoint="narrate") == "template_local"
    assert resolve_verbal_llm_backend_policy(touchpoint="communicate") == "canned_safe"


def test_monologue_default_and_legacy(monkeypatch):
    monkeypatch.delenv("KERNEL_LLM_TP_MONOLOGUE_POLICY", raising=False)
    monkeypatch.delenv("KERNEL_LLM_MONOLOGUE_BACKEND_POLICY", raising=False)
    assert resolve_monologue_llm_backend_policy() == DEFAULT_MONOLOGUE_BACKEND_POLICY

    monkeypatch.setenv("KERNEL_LLM_MONOLOGUE_BACKEND_POLICY", "annotate_degraded")
    assert resolve_monologue_llm_backend_policy() == "annotate_degraded"


def test_monologue_tp_overrides_legacy(monkeypatch):
    monkeypatch.setenv("KERNEL_LLM_MONOLOGUE_BACKEND_POLICY", "passthrough")
    monkeypatch.setenv("KERNEL_LLM_TP_MONOLOGUE_POLICY", "annotate_degraded")
    assert resolve_monologue_llm_backend_policy() == "annotate_degraded"


def test_global_default_perception_when_legacy_unset(monkeypatch):
    monkeypatch.delenv("KERNEL_LLM_TP_PERCEPTION_POLICY", raising=False)
    monkeypatch.delenv("KERNEL_PERCEPTION_BACKEND_POLICY", raising=False)
    monkeypatch.setenv(ENV_LLM_GLOBAL_DEFAULT_POLICY, "fast_fail")
    assert resolve_perception_backend_policy() == "fast_fail"


def test_global_default_verbal_when_family_and_legacy_unset(monkeypatch):
    monkeypatch.delenv("KERNEL_LLM_TP_COMMUNICATE_POLICY", raising=False)
    monkeypatch.delenv("KERNEL_LLM_TP_NARRATE_POLICY", raising=False)
    monkeypatch.delenv("KERNEL_LLM_VERBAL_FAMILY_POLICY", raising=False)
    monkeypatch.delenv("KERNEL_VERBAL_LLM_BACKEND_POLICY", raising=False)
    monkeypatch.setenv(ENV_LLM_GLOBAL_DEFAULT_POLICY, "canned_safe")
    assert resolve_verbal_llm_backend_policy(touchpoint="communicate") == "canned_safe"


def test_global_ignored_when_not_valid_for_touchpoint(monkeypatch):
    monkeypatch.delenv("KERNEL_LLM_TP_PERCEPTION_POLICY", raising=False)
    monkeypatch.delenv("KERNEL_PERCEPTION_BACKEND_POLICY", raising=False)
    monkeypatch.setenv(ENV_LLM_GLOBAL_DEFAULT_POLICY, "canned_safe")
    assert resolve_perception_backend_policy() == "template_local"


def test_legacy_still_wins_over_global(monkeypatch):
    monkeypatch.delenv("KERNEL_LLM_TP_PERCEPTION_POLICY", raising=False)
    monkeypatch.setenv("KERNEL_PERCEPTION_BACKEND_POLICY", "session_banner")
    monkeypatch.setenv(ENV_LLM_GLOBAL_DEFAULT_POLICY, "fast_fail")
    assert resolve_perception_backend_policy() == "session_banner"


def test_monologue_global_passthrough(monkeypatch):
    monkeypatch.delenv("KERNEL_LLM_TP_MONOLOGUE_POLICY", raising=False)
    monkeypatch.delenv("KERNEL_LLM_MONOLOGUE_BACKEND_POLICY", raising=False)
    monkeypatch.setenv(ENV_LLM_GLOBAL_DEFAULT_POLICY, "passthrough")
    assert resolve_monologue_llm_backend_policy() == "passthrough"
