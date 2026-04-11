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


def test_guardian_includes_routines_when_configured(monkeypatch):
    from pathlib import Path

    from src.modules.guardian_routines import invalidate_guardian_routines_cache

    fixture = Path(__file__).resolve().parent / "fixtures" / "guardian" / "routines.json"
    monkeypatch.setenv("KERNEL_GUARDIAN_MODE", "1")
    monkeypatch.setenv("KERNEL_GUARDIAN_ROUTINES", "1")
    monkeypatch.setenv("KERNEL_GUARDIAN_ROUTINES_PATH", str(fixture))
    invalidate_guardian_routines_cache()
    ctx = guardian_mode_llm_context()
    assert "hydration" in ctx
    assert "Care routines" in ctx
