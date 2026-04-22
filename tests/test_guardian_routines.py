"""Guardian care routines — JSON load + LLM suffix (no policy change)."""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.safety.guardian_routines import (
    guardian_routines_feature_enabled,
    guardian_routines_llm_suffix,
    invalidate_guardian_routines_cache,
    load_guardian_routines_from_path,
    public_routines_snapshot,
)

_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "guardian" / "routines.json"


def test_load_fixture():
    routines = load_guardian_routines_from_path(_FIXTURE)
    assert len(routines) >= 2
    ids = {r.id for r in routines}
    assert "hydration" in ids


def test_invalid_id_skipped(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text(
        '{"routines": [{"id": "123invalid", "title": "x", "hint": "y"}, '
        '{"id": "ok_id", "title": "Title", "hint": "Hint text here."}]}',
        encoding="utf-8",
    )
    routines = load_guardian_routines_from_path(p)
    assert len(routines) == 1
    assert routines[0].id == "ok_id"


def test_llm_suffix_requires_feature_and_path(monkeypatch):
    monkeypatch.delenv("KERNEL_GUARDIAN_ROUTINES", raising=False)
    monkeypatch.delenv("KERNEL_GUARDIAN_ROUTINES_PATH", raising=False)
    invalidate_guardian_routines_cache()
    assert guardian_routines_llm_suffix() == ""

    monkeypatch.setenv("KERNEL_GUARDIAN_ROUTINES", "1")
    monkeypatch.setenv("KERNEL_GUARDIAN_ROUTINES_PATH", str(_FIXTURE))
    invalidate_guardian_routines_cache()
    s = guardian_routines_llm_suffix()
    assert "hydration" in s
    assert "Care routines" in s


def test_public_snapshot(monkeypatch):
    monkeypatch.setenv("KERNEL_GUARDIAN_ROUTINES", "1")
    monkeypatch.setenv("KERNEL_GUARDIAN_ROUTINES_PATH", str(_FIXTURE))
    invalidate_guardian_routines_cache()
    pub = public_routines_snapshot()
    assert pub and all("id" in x and "title" in x and "hint" not in x for x in pub)


def test_feature_flag(monkeypatch):
    monkeypatch.delenv("KERNEL_GUARDIAN_ROUTINES", raising=False)
    assert guardian_routines_feature_enabled() is False
    monkeypatch.setenv("KERNEL_GUARDIAN_ROUTINES", "1")
    assert guardian_routines_feature_enabled() is True
