"""Operator cockpit: KERNEL_* grouping and experimental-risk heuristics."""

from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.validators.kernel_env_operator import (
    build_operator_config_report,
    classify_env_key,
    experimental_risk_level,
    profile_alignment_scores,
)


def test_classify_known_prefixes():
    assert classify_env_key("KERNEL_CHAT_INCLUDE_HOMEOSTASIS") == "Chat JSON / UX"
    assert classify_env_key("KERNEL_SEMANTIC_CHAT_GATE") == "MalAbs semantic / embed"
    assert classify_env_key("KERNEL_ENV_VALIDATION") == "Validation & policy"
    assert classify_env_key("CHAT_HOST") == "Chat server bind"
    assert classify_env_key("KERNEL_LLM_MONOLOGUE") == "LLM / variability / generative"
    assert classify_env_key("KERNEL_LLM_MONOLOGUE_BACKEND_POLICY") == "LLM / variability / generative"
    assert classify_env_key("KERNEL_UNKNOWN_FOO") == "Other KERNEL_*"


def test_experimental_risk_high_without_profile(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("ETHOS_RUNTIME_PROFILE", raising=False)
    for i in range(12):
        monkeypatch.setenv(f"KERNEL_TOUCH_{i}", "1")
    r = experimental_risk_level()
    assert r["level"] == "high"
    assert r["ethos_runtime_profile"] is None


def test_experimental_risk_low_with_profile(monkeypatch: pytest.MonkeyPatch):
    for i in range(12):
        monkeypatch.setenv(f"KERNEL_TOUCH_{i}", "1")
    monkeypatch.setenv("ETHOS_RUNTIME_PROFILE", "lan_operational")
    r = experimental_risk_level()
    assert r["level"] == "low"


def test_profile_alignment_prefers_matching_bundle(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("ETHOS_RUNTIME_PROFILE", raising=False)
    monkeypatch.setenv("KERNEL_SEMANTIC_CHAT_GATE", "0")
    monkeypatch.setenv("KERNEL_JUDICIAL_ESCALATION", "1")
    monkeypatch.setenv("KERNEL_JUDICIAL_MOCK_COURT", "1")
    monkeypatch.setenv("KERNEL_CHAT_INCLUDE_JUDICIAL", "1")
    rows = profile_alignment_scores()
    top = rows[0]
    assert top["profile"] == "judicial_demo"
    assert top["score"] == 1.0


def test_build_operator_config_report_shape(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("KERNEL_ENV_VALIDATION", "warn")
    r = build_operator_config_report()
    assert "by_family" in r
    assert "experimental_risk" in r
    assert "profile_alignment" in r
    assert "policy_violations" in r
    assert isinstance(r["profile_descriptions"], dict)
