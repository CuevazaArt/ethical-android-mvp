"""CLI check-config (src.cli)."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.cli.__main__ import main


def test_check_config_strict_ok(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("ETHOS_RUNTIME_PROFILE", raising=False)
    monkeypatch.delenv("KERNEL_JUDICIAL_MOCK_COURT", raising=False)
    monkeypatch.delenv("KERNEL_SEMANTIC_CHAT_GATE", raising=False)
    assert main(["check-config", "--strict"]) == 0


def test_check_config_strict_fails_on_unknown_profile(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ETHOS_RUNTIME_PROFILE", "not_a_real_profile_ever")
    assert main(["check-config", "--strict"]) == 1


def test_check_config_strict_semantic_off_with_dao(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("ETHOS_RUNTIME_PROFILE", raising=False)
    monkeypatch.setenv("KERNEL_SEMANTIC_CHAT_GATE", "0")
    monkeypatch.setenv("KERNEL_MORAL_HUB_DAO_VOTE", "1")
    assert main(["check-config", "--strict"]) == 1
