"""Guardian Angel mode — opt-in tone layer (no policy change)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.guardian_mode import guardian_mode_llm_context, is_guardian_mode_active


def test_guardian_default_off(monkeypatch):
    monkeypatch.delenv("KERNEL_GUARDIAN_MODE", raising=False)
    assert is_guardian_mode_active() is False
    assert guardian_mode_llm_context() == ""


def test_guardian_on(monkeypatch):
    monkeypatch.setenv("KERNEL_GUARDIAN_MODE", "1")
    assert is_guardian_mode_active() is True
    ctx = guardian_mode_llm_context()
    assert "Guardian Angel" in ctx
    assert "ethical decision" in ctx.lower() or "fixed" in ctx.lower()


def test_guardian_on_synonyms(monkeypatch):
    monkeypatch.setenv("KERNEL_GUARDIAN_MODE", "true")
    assert is_guardian_mode_active() is True
